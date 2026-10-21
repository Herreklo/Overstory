using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using Unity.Collections;
using UnityEngine;
using UnityEngine.Rendering;
using Path = System.IO.Path;

namespace Overstory.Perf
{
    /// <summary>
    /// The scale test's district (docs/research/scale-test.md): loads the chunk cache blender/tools/scale_district.py
    /// writes (one file per 64 m chunk: the core's houses merged at full detail, every house's shell, the ground) into
    /// meshes through Mesh.MeshData, timing each chunk's read and its upload to the GPU, and draws it in one of three
    /// arms: 'l0', every core house at full detail and shells round the core; 'near', full detail only within
    /// nearRadius of the camera and shells beyond (what a streamed town would draw); 'shells', the shells alone.
    /// The ground is drawn in every arm. PerfRunner loads it when the player is given -district &lt;dir&gt;.
    /// </summary>
    public class DistrictLoader : MonoBehaviour
    {
        public Material material;
        [Tooltip("Metres from the camera within which the 'near' arm draws a chunk's houses at full detail.")]
        public float nearRadius = 200f;

        public class Chunk
        {
            public string name;
            public Vector3 centre;
            public MeshRenderer l0, shell, ground;
        }

        public readonly List<Chunk> chunks = new List<Chunk>();

        /// <summary>The chunk file's vertex (24 bytes), in Unity's attribute order.</summary>
        static readonly VertexAttributeDescriptor[] Layout =
        {
            new VertexAttributeDescriptor(VertexAttribute.Position, VertexAttributeFormat.Float32, 3),
            new VertexAttributeDescriptor(VertexAttribute.Normal, VertexAttributeFormat.SNorm8, 4),
            new VertexAttributeDescriptor(VertexAttribute.Color, VertexAttributeFormat.UNorm8, 4),
            new VertexAttributeDescriptor(VertexAttribute.TexCoord0, VertexAttributeFormat.Float16, 2),
        };
        const int Stride = 24;
        static readonly string[] Parts = { "l0", "shell", "ground" };

        [System.Serializable]
        public class View
        {
            public string name;
            public float[] pos, target;
            public float fov;
        }

        [System.Serializable]
        class Plan
        {
            public float size, core, chunk;
            public int plots;
            public View[] views;
        }

        /// <summary>What loading the district cost, written into the run's summary.</summary>
        [System.Serializable]
        public class Report
        {
            public string dir;
            public float size, core, chunk;
            public int plots, chunks, meshes;
            public long fileBytes, vertexBytes, indexBytes;
            public long l0Triangles, shellTriangles, groundTriangles;
            public double loadSeconds;
            public PerfRunner.Stat readMs, uploadMs, chunkMs, coreChunkMs;
            public double mbPerSecond;
            public long rssBefore, rssAfter, monoBefore, monoAfter;
            public double[] msEach;
            public long[] bytesEach;
            public bool[] coreEach;
        }

        public Report report;
        public View[] views;

        /// <summary>Every chunk in dir/chunks read and uploaded, one after another, each timed.</summary>
        public Report Load(string dir)
        {
            var plan = JsonUtility.FromJson<Plan>(File.ReadAllText(Path.Combine(dir, "district.json")));
            views = plan.views;
            var files = Directory.GetFiles(Path.Combine(dir, "chunks"), "c_*.bin").OrderBy(f => f, System.StringComparer.Ordinal).ToArray();
            var r = new Report { dir = dir, size = plan.size, core = plan.core, chunk = plan.chunk, plots = plan.plots, chunks = files.Length };
            System.GC.Collect();
            r.rssBefore = Rss();
            r.monoBefore = System.GC.GetTotalMemory(true);
            var read = new List<double>();
            var upload = new List<double>();
            var whole = new List<double>();
            var core = new List<double>();
            var sizes = new List<long>();
            var cores = new List<bool>();
            var all = System.Diagnostics.Stopwatch.StartNew();
            foreach (var file in files)
            {
                var clock = System.Diagnostics.Stopwatch.StartNew();
                byte[] data = File.ReadAllBytes(file);
                double tRead = clock.Elapsed.TotalMilliseconds;
                var chunk = Build(Path.GetFileNameWithoutExtension(file), data, r);
                double tAll = clock.Elapsed.TotalMilliseconds;
                read.Add(tRead);
                upload.Add(tAll - tRead);
                whole.Add(tAll);
                if (chunk.l0 != null)
                    core.Add(tAll);
                r.fileBytes += data.Length;
                sizes.Add(data.Length);
                cores.Add(chunk.l0 != null);
                chunks.Add(chunk);
            }
            r.loadSeconds = all.Elapsed.TotalSeconds;
            r.readMs = Stats(read);
            r.uploadMs = Stats(upload);
            r.chunkMs = Stats(whole);
            r.coreChunkMs = Stats(core);
            r.mbPerSecond = r.fileBytes / 1048576.0 / r.loadSeconds;
            r.msEach = whole.ToArray();
            r.bytesEach = sizes.ToArray();
            r.coreEach = cores.ToArray();
            System.GC.Collect();
            r.rssAfter = Rss();
            r.monoAfter = System.GC.GetTotalMemory(true);
            report = r;
            Debug.Log($"[DistrictLoader] {r.chunks} chunks, {r.fileBytes / 1048576.0:F0} MB in {r.loadSeconds:F1} s; a chunk {r.chunkMs.median:F2} ms " +
                      $"(95th {r.chunkMs.p95:F2}), a core chunk {r.coreChunkMs.median:F2} ms; L0 {r.l0Triangles:N0}, shells {r.shellTriangles:N0}, " +
                      $"ground {r.groundTriangles:N0} triangles; resident {r.rssBefore / 1048576} -> {r.rssAfter / 1048576} MB");
            return r;
        }

        /// <summary>One chunk's meshes made from its file's bytes (MeshData, no copy through managed arrays of vertices).</summary>
        Chunk Build(string name, byte[] data, Report r)
        {
            if (data[0] != 'O' || data[1] != 'S' || data[2] != 'C' || data[3] != 'K')
                throw new System.Exception($"[DistrictLoader] {name} is not a chunk");
            int at = 4;
            uint version = U32(data, ref at);
            if (version != 1)
                throw new System.Exception($"[DistrictLoader] {name}: version {version}");
            var origin = new Vector3(F32(data, ref at), F32(data, ref at), F32(data, ref at));
            int count = (int)U32(data, ref at);
            var go = new GameObject(name);
            go.transform.SetParent(transform, false);
            go.transform.localPosition = origin;
            var chunk = new Chunk { name = name };
            var meshes = new List<(int part, Mesh mesh)>();
            var array = Mesh.AllocateWritableMeshData(count);
            var used = new List<int>();
            var bounds = new List<Bounds>();
            for (int m = 0; m < count; m++)
            {
                int nv = (int)U32(data, ref at), ni = (int)U32(data, ref at), isz = (int)U32(data, ref at);
                var lo = new Vector3(F32(data, ref at), F32(data, ref at), F32(data, ref at));
                var hi = new Vector3(F32(data, ref at), F32(data, ref at), F32(data, ref at));
                var md = array[m];
                if (nv == 0)
                {
                    md.SetVertexBufferParams(0, Layout);
                    md.SetIndexBufferParams(0, IndexFormat.UInt16);
                    md.subMeshCount = 0;
                    bounds.Add(default);
                    continue;
                }
                md.SetVertexBufferParams(nv, Layout);
                NativeArray<byte>.Copy(data, at, md.GetVertexData<byte>(), 0, nv * Stride);
                at += nv * Stride;
                md.SetIndexBufferParams(ni, isz == 2 ? IndexFormat.UInt16 : IndexFormat.UInt32);
                NativeArray<byte>.Copy(data, at, md.GetIndexData<byte>(), 0, ni * isz);
                at += ni * isz;
                var b = new Bounds((lo + hi) * 0.5f, hi - lo);
                md.subMeshCount = 1;
                md.SetSubMesh(0, new SubMeshDescriptor(0, ni) { bounds = b, vertexCount = nv }, MeshUpdateFlags.DontRecalculateBounds | MeshUpdateFlags.DontValidateIndices);
                used.Add(m);
                bounds.Add(b);
                r.vertexBytes += nv * Stride;
                r.indexBytes += (long)ni * isz;
                if (m == 0) r.l0Triangles += ni / 3;
                else if (m == 1) r.shellTriangles += ni / 3;
                else r.groundTriangles += ni / 3;
            }
            var made = Enumerable.Range(0, count).Select(m => new Mesh { name = $"{name}_{Parts[Mathf.Min(m, 2)]}" }).ToArray();
            Mesh.ApplyAndDisposeWritableMeshData(array, made, MeshUpdateFlags.DontRecalculateBounds | MeshUpdateFlags.DontValidateIndices);
            var whole = new Bounds();
            bool any = false;
            foreach (int m in used)
            {
                var mesh = made[m];
                mesh.bounds = bounds[m];
                mesh.UploadMeshData(true);      // to the GPU now, and no copy kept in memory (a streamed chunk keeps none)
                var part = new GameObject(Parts[Mathf.Min(m, 2)]);
                part.transform.SetParent(go.transform, false);
                part.AddComponent<MeshFilter>().sharedMesh = mesh;
                var mr = part.AddComponent<MeshRenderer>();
                mr.sharedMaterial = material;
                mr.shadowCastingMode = m == 2 ? ShadowCastingMode.Off : ShadowCastingMode.On;
                mr.enabled = false;
                if (m == 0) chunk.l0 = mr;
                else if (m == 1) chunk.shell = mr;
                else chunk.ground = mr;
                if (!any) { whole = bounds[m]; any = true; } else whole.Encapsulate(bounds[m]);
                r.meshes++;
            }
            foreach (int m in Enumerable.Range(0, count).Except(used))
                Destroy(made[m]);
            chunk.centre = origin + whole.center;
            return chunk;
        }

        /// <summary>The district drawn in an arm ('' hides it), seen from eye (Unity metres) for the 'near' arm.</summary>
        public void Show(string arm, Vector3 eye)
        {
            bool on = arm != "";
            foreach (var c in chunks)
            {
                bool full = c.l0 != null && (arm == "l0" || (arm == "near" && Flat(c.centre - eye) < nearRadius));
                if (c.l0 != null) c.l0.enabled = on && full;
                if (c.shell != null) c.shell.enabled = on && !full;
                if (c.ground != null) c.ground.enabled = on;
            }
        }

        /// <summary>Every renderer the district has, so the corner's own can be told from them.</summary>
        public HashSet<Renderer> Renderers() => new HashSet<Renderer>(GetComponentsInChildren<Renderer>(true));

        static float Flat(Vector3 d) => Mathf.Sqrt(d.x * d.x + d.z * d.z);

        static uint U32(byte[] d, ref int at)
        {
            uint v = System.BitConverter.ToUInt32(d, at);
            at += 4;
            return v;
        }

        static float F32(byte[] d, ref int at)
        {
            float v = System.BitConverter.ToSingle(d, at);
            at += 4;
            return v;
        }

        /// <summary>The process's resident memory (bytes), from ps: the player's whole footprint, GPU buffers included
        /// on Apple's unified memory as far as the system counts them to the process.</summary>
        internal static long Rss()
        {
            try
            {
                var psi = new System.Diagnostics.ProcessStartInfo("/bin/ps", $"-o rss= -p {System.Diagnostics.Process.GetCurrentProcess().Id}")
                    { UseShellExecute = false, RedirectStandardOutput = true };
                using (var p = System.Diagnostics.Process.Start(psi))
                {
                    string s = p.StandardOutput.ReadToEnd().Trim();
                    p.WaitForExit();
                    return long.Parse(s, CultureInfo.InvariantCulture) * 1024;
                }
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"[DistrictLoader] no resident memory: {e.Message}");
                return -1;
            }
        }

        internal static PerfRunner.Stat Stats(List<double> v)
        {
            if (v.Count == 0)
                return new PerfRunner.Stat();
            var s = v.OrderBy(x => x).ToArray();
            double Q(double q) => s[Mathf.Clamp((int)System.Math.Ceiling(q * s.Length) - 1, 0, s.Length - 1)];
            return new PerfRunner.Stat { median = Q(0.5), p95 = Q(0.95), p99 = Q(0.99), max = s[s.Length - 1], mean = s.Average() };
        }

        /// <summary>A view from district.json as the runner's (street metres).</summary>
        public static PerfRunner.View ToRunner(View v) => new PerfRunner.View
        {
            name = v.name, position = new Vector3(v.pos[0], v.pos[1], v.pos[2]), target = new Vector3(v.target[0], v.target[1], v.target[2]), fov = v.fov,
        };
    }
}
