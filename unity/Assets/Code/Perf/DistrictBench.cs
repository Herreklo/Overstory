using System.Collections.Generic;
using System.IO;
using Unity.Burst;
using Unity.Collections;
using Unity.Collections.LowLevel.Unsafe;
using Unity.Jobs;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;

namespace Overstory.Perf
{
    /// <summary>
    /// The scale test's micro-benchmarks (docs/research/scale-test.md, Rebuilding a chunk), in the built player: what
    /// rebuilding a chunk costs on the device when its history changes. The generator places approved parts and does
    /// not invent their geometry (docs/building-blocks.md), so a chunk's rebuild is mostly copying its parts' vertices
    /// through each one's transform into the chunk's mesh: timed here on the district's largest chunk, its houses cut
    /// into parts of a few hundred vertices, once in plain C# (Mono) and once as a Burst job, then uploaded through
    /// MeshData. And a history page (1024 by 512) drawn on the GPU, read back and compressed to a block format, as a
    /// chunk's maps would be.
    /// </summary>
    public static class DistrictBench
    {
        [System.Serializable]
        public class Report
        {
            public string chunk;
            public int triangles, vertices, parts, repeats;
            public bool burst;
            public PerfRunner.Stat placeManagedMs, placeBurstMs, uploadMs;
            public int pageWidth, pageHeight;
            public string pageFormat;
            public PerfRunner.Stat pageDrawMs, pageReadbackMs, pageCompressMs, pageCompressFastMs;
        }

        /// <summary>The chunk file's vertex: position, normal (snorm8 x4), colour (unorm8 x4), UV0 (half x2).</summary>
        struct Vertex
        {
            public float x, y, z;
            public uint n, c, uv;
        }

        const int PartSize = 400;   // vertices a part: a window, a door, a run of boards

        [BurstCompile]
        struct PlaceJob : IJob
        {
            [ReadOnly] public NativeArray<Vertex> src;
            [ReadOnly] public NativeArray<float> mats;
            public NativeArray<Vertex> dst;

            public void Execute() => Place(src, mats, dst);
        }

        /// <summary>Each part's vertices through its transform (12 floats a part, a 3 by 4 matrix): positions and normals.</summary>
        static void Place(NativeArray<Vertex> src, NativeArray<float> mats, NativeArray<Vertex> dst)
        {
            for (int i = 0; i < src.Length; i++)
            {
                int k = i / PartSize * 12;
                var v = src[i];
                float x = v.x, y = v.y, z = v.z;
                v.x = mats[k] * x + mats[k + 1] * y + mats[k + 2] * z + mats[k + 3];
                v.y = mats[k + 4] * x + mats[k + 5] * y + mats[k + 6] * z + mats[k + 7];
                v.z = mats[k + 8] * x + mats[k + 9] * y + mats[k + 10] * z + mats[k + 11];
                float nx = (sbyte)(v.n & 0xff), ny = (sbyte)((v.n >> 8) & 0xff), nz = (sbyte)((v.n >> 16) & 0xff);
                float rx = mats[k] * nx + mats[k + 1] * ny + mats[k + 2] * nz;
                float ry = mats[k + 4] * nx + mats[k + 5] * ny + mats[k + 6] * nz;
                float rz = mats[k + 8] * nx + mats[k + 9] * ny + mats[k + 10] * nz;
                v.n = Pack(rx) | Pack(ry) << 8 | Pack(rz) << 16;
                dst[i] = v;
            }
        }

        static uint Pack(float f)
        {
            int i = (int)(f + (f >= 0f ? 0.5f : -0.5f));
            i = i < -127 ? -127 : i > 127 ? 127 : i;
            return (uint)(byte)(sbyte)i;
        }

        public static Report Run(string chunkFile, int repeats = 20)
        {
            var r = new Report { chunk = Path.GetFileName(chunkFile), repeats = repeats, burst = BurstCompiler.IsEnabled };
            byte[] data = File.ReadAllBytes(chunkFile);
            int at = 4 + 4 + 12 + 4;       // magic, version, origin, count; then the first mesh (L0)
            int nv = System.BitConverter.ToInt32(data, at), ni = System.BitConverter.ToInt32(data, at + 4), isz = System.BitConverter.ToInt32(data, at + 8);
            at += 12 + 24;
            r.vertices = nv;
            r.triangles = ni / 3;
            r.parts = (nv + PartSize - 1) / PartSize;
            var src = new NativeArray<byte>(nv * 24, Allocator.Persistent);
            NativeArray<byte>.Copy(data, at, src, 0, nv * 24);
            var verts = src.Reinterpret<Vertex>(1);
            at += nv * 24;
            var idx = new NativeArray<uint>(ni, Allocator.Persistent);
            for (int i = 0; i < ni; i++)
                idx[i] = isz == 2 ? System.BitConverter.ToUInt16(data, at + 2 * i) : System.BitConverter.ToUInt32(data, at + 4 * i);
            var mats = new NativeArray<float>(r.parts * 12, Allocator.Persistent);
            for (int p = 0; p < r.parts; p++)
            {
                float a = p * 0.37f, c = Mathf.Cos(a), s = Mathf.Sin(a);
                float[] m = { c, 0, s, p % 7, 0, 1, 0, 0.01f * p, -s, 0, c, p % 5 };
                for (int j = 0; j < 12; j++)
                    mats[p * 12 + j] = m[j];
            }
            var dst = new NativeArray<Vertex>(nv, Allocator.Persistent);
            var managed = new List<double>();
            var burst = new List<double>();
            var upload = new List<double>();
            var layout = new[]
            {
                new VertexAttributeDescriptor(VertexAttribute.Position, VertexAttributeFormat.Float32, 3),
                new VertexAttributeDescriptor(VertexAttribute.Normal, VertexAttributeFormat.SNorm8, 4),
                new VertexAttributeDescriptor(VertexAttribute.Color, VertexAttributeFormat.UNorm8, 4),
                new VertexAttributeDescriptor(VertexAttribute.TexCoord0, VertexAttributeFormat.Float16, 2),
            };
            for (int rep = 0; rep <= repeats; rep++)
            {
                var clock = System.Diagnostics.Stopwatch.StartNew();
                Place(verts, mats, dst);
                double tm = clock.Elapsed.TotalMilliseconds;
                clock.Restart();
                new PlaceJob { src = verts, mats = mats, dst = dst }.Run();
                double tb = clock.Elapsed.TotalMilliseconds;
                clock.Restart();
                var array = Mesh.AllocateWritableMeshData(1);
                var md = array[0];
                md.SetVertexBufferParams(nv, layout);
                md.GetVertexData<Vertex>().CopyFrom(dst);
                md.SetIndexBufferParams(ni, IndexFormat.UInt32);
                md.GetIndexData<uint>().CopyFrom(idx);
                md.subMeshCount = 1;
                md.SetSubMesh(0, new SubMeshDescriptor(0, ni), MeshUpdateFlags.DontValidateIndices);
                var mesh = new Mesh();
                Mesh.ApplyAndDisposeWritableMeshData(array, mesh, MeshUpdateFlags.DontValidateIndices);
                mesh.UploadMeshData(true);
                double tu = clock.Elapsed.TotalMilliseconds;
                Object.Destroy(mesh);
                if (rep == 0)
                    continue;      // (the first only primes: Burst's compiled code loaded, the JIT warm)
                managed.Add(tm);
                burst.Add(tb);
                upload.Add(tu);
            }
            r.placeManagedMs = DistrictLoader.Stats(managed);
            r.placeBurstMs = DistrictLoader.Stats(burst);
            r.uploadMs = DistrictLoader.Stats(upload);
            src.Dispose();
            idx.Dispose();
            mats.Dispose();
            dst.Dispose();

            // a history page: drawn on the GPU (a blit of a source page stands in for the bake's own shader), read
            // back and compressed to a block format (DXT5 on this platform: Texture2D.Compress has no BC7)
            const int W = 1024, H = 512;
            r.pageWidth = W;
            r.pageHeight = H;
            var page = new Texture2D(W, H, TextureFormat.RGBA32, false);
            var px = new Color32[W * H];
            for (int i = 0; i < px.Length; i++)
                px[i] = new Color32((byte)(i * 37), (byte)(i >> 3), (byte)((i * 11) ^ (i >> 10)), 255);
            page.SetPixels32(px);
            page.Apply(false);
            var rt = new RenderTexture(W, H, 0, GraphicsFormat.R8G8B8A8_UNorm);
            rt.Create();
            var draw = new List<double>();
            var back = new List<double>();
            var high = new List<double>();
            var fast = new List<double>();
            for (int rep = 0; rep <= repeats; rep++)
            {
                var clock = System.Diagnostics.Stopwatch.StartNew();
                Graphics.Blit(page, rt);
                var req = AsyncGPUReadback.Request(rt, 0, 0, 1, 0, 1, 0, 1, TextureFormat.RGBA32);
                req.WaitForCompletion();
                double td = clock.Elapsed.TotalMilliseconds;
                clock.Restart();
                var whole = AsyncGPUReadback.Request(rt, 0, TextureFormat.RGBA32);
                whole.WaitForCompletion();
                var got = whole.GetData<byte>();
                double tr = clock.Elapsed.TotalMilliseconds;
                var tex = new Texture2D(W, H, TextureFormat.RGBA32, false);
                tex.SetPixelData(got, 0);
                var tex2 = new Texture2D(W, H, TextureFormat.RGBA32, false);
                tex2.SetPixelData(got, 0);
                clock.Restart();
                tex.Compress(true);
                double th = clock.Elapsed.TotalMilliseconds;
                clock.Restart();
                tex2.Compress(false);
                double tf = clock.Elapsed.TotalMilliseconds;
                r.pageFormat = tex.format.ToString();
                Object.Destroy(tex);
                Object.Destroy(tex2);
                if (rep == 0)
                    continue;
                draw.Add(td);
                back.Add(tr);
                high.Add(th);
                fast.Add(tf);
            }
            rt.Release();
            Object.Destroy(page);
            r.pageDrawMs = DistrictLoader.Stats(draw);
            r.pageReadbackMs = DistrictLoader.Stats(back);
            r.pageCompressMs = DistrictLoader.Stats(high);
            r.pageCompressFastMs = DistrictLoader.Stats(fast);
            Debug.Log($"[DistrictBench] {r.chunk}: {r.triangles:N0} triangles, {r.vertices:N0} vertices in {r.parts} parts: placed in C# " +
                      $"{r.placeManagedMs.median:F2} ms, Burst ({(r.burst ? "on" : "OFF")}) {r.placeBurstMs.median:F2} ms, uploaded {r.uploadMs.median:F2} ms; " +
                      $"a {W}x{H} page drawn {r.pageDrawMs.median:F2} ms, read back {r.pageReadbackMs.median:F2} ms, compressed to {r.pageFormat} " +
                      $"{r.pageCompressMs.median:F1} ms (fast {r.pageCompressFastMs.median:F1} ms)");
            return r;
        }
    }
}
