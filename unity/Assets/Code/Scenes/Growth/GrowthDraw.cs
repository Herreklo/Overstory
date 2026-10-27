using System;
using System.Collections.Generic;
using Unity.Collections;
using Unity.Collections.LowLevel.Unsafe;
using Unity.Jobs;
using UnityEngine;
using UnityEngine.Rendering;

namespace Overstory.Growth
{
    /// <summary>
    /// The growth's own BatchRendererGroup (unity-conventions: swarms such as tufts draw through our own BRG): many
    /// instances of a few meshes, each kind its levels by the distance from the eye, crossfaded between them
    /// (LOD_FADE_CROSSFADE, the dither's value packed in each visible index), culled to the view, no shadows cast.
    /// What to draw comes from the generator's placements (blender/generators/growth.py), already seeded and placed: this
    /// only draws them, so the same placements draw the same every time.
    ///
    /// Per instance the shader gets unity_ObjectToWorld, unity_WorldToObject and unity_RendererUserValue: the generator's
    /// 32 bits (tufts: its seed's rank in the low byte, its hue in the next, its habitat above).
    /// </summary>
    public sealed unsafe class GrowthDraw : IDisposable
    {
        /// <summary>One kind of thing drawn: its meshes by level (nearest first), its material and its instances.</summary>
        public sealed class Kind
        {
            public string name;
            public Mesh[] levels;
            public Material material;
            /// <summary>Each level's reach from the eye (m); past the last, the kind is not drawn.</summary>
            public float[] to;
            /// <summary>The share of a level's reach over which it crossfades into the next (0: it pops).</summary>
            public float fade;
            /// <summary>Thinning far off: past thinFrom (m) only the instances whose rank is under thinFrom / d stay, down
            /// to keepMin of them (the shader widens the ones kept, and shrinks each as its rank is passed).</summary>
            public float thinFrom = float.PositiveInfinity, keepMin = 1f;
            public readonly List<Matrix4x4> matrices = new List<Matrix4x4>();
            public readonly List<uint> users = new List<uint>();
            /// <summary>Each instance's bounding radius about its pivot (m), for the frustum.</summary>
            public float radius = 1f;

            internal int first;
            internal BatchMaterialID material_;
            internal BatchMeshID[] meshes_;
        }

        readonly List<Kind> kinds = new List<Kind>();
        BatchRendererGroup brg;
        GraphicsBuffer buffer;
        BatchID batch;
        int count;
        static readonly int ObjectToWorld = Shader.PropertyToID("unity_ObjectToWorld");
        static readonly int WorldToObject = Shader.PropertyToID("unity_WorldToObject");
        static readonly int UserValue = Shader.PropertyToID("unity_RendererUserValuesPropertyEntry");

        /// <summary>Counts from the last camera cull, for checking: instances drawn and triangles drawn.</summary>
        public int lastDrawn, lastTriangles;

        public IReadOnlyList<Kind> Kinds => kinds;

        public void Add(Kind k)
        {
            if (brg != null)
                throw new InvalidOperationException("GrowthDraw: add every kind before Build");
            kinds.Add(k);
        }

        /// <summary>Uploads every instance and starts drawing.</summary>
        public void Build()
        {
            brg = new BatchRendererGroup(OnPerformCulling, IntPtr.Zero);
            brg.SetEnabledViewTypes(new[] { BatchCullingViewType.Camera });
            count = 0;
            foreach (var k in kinds)
            {
                k.first = count;
                count += k.matrices.Count;
                k.material_ = brg.RegisterMaterial(k.material);
                k.meshes_ = new BatchMeshID[k.levels.Length];
                for (int l = 0; l < k.levels.Length; l++)
                    k.meshes_[l] = brg.RegisterMesh(k.levels[l]);
            }
            // the raw buffer: 64 zero bytes (the defaults), then each instance's object-to-world (3x4), its world-to-object
            // (3x4), and its user value
            const int zero = 16, mat = 12;
            int words = zero + count * (mat * 2 + 1);
            words = (words + 3) & ~3;
            var data = new uint[words];
            int o2w = zero, w2o = zero + count * mat, user = zero + count * mat * 2;
            int i = 0;
            foreach (var k in kinds)
                for (int j = 0; j < k.matrices.Count; j++, i++)
                {
                    Pack(data, o2w + i * mat, k.matrices[j]);
                    Pack(data, w2o + i * mat, k.matrices[j].inverse);
                    data[user + i] = k.users[j];
                }
            buffer = new GraphicsBuffer(GraphicsBuffer.Target.Raw, words, 4);
            buffer.SetData(data);
            var meta = new NativeArray<MetadataValue>(3, Allocator.Temp);
            meta[0] = new MetadataValue { NameID = ObjectToWorld, Value = 0x80000000u | (uint)(o2w * 4) };
            meta[1] = new MetadataValue { NameID = WorldToObject, Value = 0x80000000u | (uint)(w2o * 4) };
            meta[2] = new MetadataValue { NameID = UserValue, Value = 0x80000000u | (uint)(user * 4) };
            batch = brg.AddBatch(meta, buffer.bufferHandle);
            meta.Dispose();
            var b = new Bounds(Vector3.zero, Vector3.one * 1e5f);
            brg.SetGlobalBounds(b);
        }

        static void Pack(uint[] d, int at, Matrix4x4 m)
        {
            // column by column, three rows each (float3x4)
            for (int c = 0; c < 4; c++)
                for (int r = 0; r < 3; r++)
                    d[at + c * 3 + r] = (uint)BitConverter.SingleToInt32Bits(m[r, c]);
        }

        // one draw's instances: a kind's level, whole or fading (its dither's value per instance)
        struct Bucket
        {
            public int kind, level;
            public bool fading;
            public List<uint> visible;
        }

        readonly Dictionary<int, Bucket> buckets = new Dictionary<int, Bucket>();

        void Put(int kind, int level, uint index, float fadeValue)
        {
            bool fading = fadeValue < 0.999f;
            int key = (kind * 16 + level) * 2 + (fading ? 1 : 0);
            if (!buckets.TryGetValue(key, out var b))
            {
                b = new Bucket { kind = kind, level = level, fading = fading, visible = new List<uint>() };
                buckets[key] = b;
            }
            if (fading)
            {
                int s = Mathf.Clamp(Mathf.RoundToInt(fadeValue * 127f), -127, 127);
                index = (index & 0x00ffffffu) | ((uint)(sbyte)s << 24);
            }
            b.visible.Add(index);
        }

        JobHandle OnPerformCulling(BatchRendererGroup group, BatchCullingContext ctx, BatchCullingOutput output, IntPtr userContext)
        {
            if (ctx.viewType != BatchCullingViewType.Camera || count == 0)
                return default;
            foreach (var b in buckets.Values)
                b.visible.Clear();
            Vector3 eye = ctx.lodParameters.cameraPosition;
            var planes = ctx.cullingPlanes;
            int nPlanes = Mathf.Min(planes.Length, 6);
            int drawn = 0;
            long triangles = 0;
            for (int ki = 0; ki < kinds.Count; ki++)
            {
                var k = kinds[ki];
                int levels = k.levels.Length;
                for (int j = 0; j < k.matrices.Count; j++)
                {
                    var m = k.matrices[j];
                    Vector3 pos = new Vector3(m.m03, m.m13, m.m23);
                    float scale = new Vector3(m.m00, m.m10, m.m20).magnitude;
                    float rad = k.radius * Mathf.Max(scale, new Vector3(m.m01, m.m11, m.m21).magnitude);
                    bool inside = true;
                    for (int p = 0; p < nPlanes && inside; p++)
                        inside = planes[p].GetDistanceToPoint(pos) > -rad;
                    if (!inside)
                        continue;
                    float d = Vector3.Distance(eye, pos);
                    if (d > k.thinFrom)
                    {
                        float keep = Mathf.Max(k.keepMin, k.thinFrom / d);
                        if ((k.users[j] & 0xff) / 255f >= keep)
                            continue;
                    }
                    int level = 0;
                    while (level < levels && d > k.to[level])
                        level++;
                    if (level >= levels)
                        continue;
                    uint index = (uint)(k.first + j);
                    float start = k.to[level] * (1f - k.fade);
                    if (k.fade > 0f && d > start)
                    {
                        // fading out of this level, into the next (or into nothing past the last)
                        float t = Mathf.Clamp01((d - start) / Mathf.Max(k.to[level] - start, 1e-4f));
                        Put(ki, level, index, 1f - t);
                        if (level + 1 < levels)
                            Put(ki, level + 1, index, -(1f - t));
                    }
                    else
                        Put(ki, level, index, 1f);
                    drawn++;
                    triangles += Triangles(k.levels[level]);
                }
            }
            lastDrawn = drawn;
            lastTriangles = (int)triangles;

            // the draws: one per kind, level, whole or fading, and submesh
            int nCmd = 0, nVis = 0;
            foreach (var b in buckets.Values)
                if (b.visible.Count > 0)
                {
                    nCmd += kinds[b.kind].levels[b.level].subMeshCount;
                    nVis += b.visible.Count;
                }
            if (nCmd == 0)
                return default;
            var dc = new BatchCullingOutputDrawCommands();
            dc.drawCommands = (BatchDrawCommand*)UnsafeUtility.Malloc(UnsafeUtility.SizeOf<BatchDrawCommand>() * nCmd, UnsafeUtility.AlignOf<BatchDrawCommand>(), Allocator.TempJob);
            dc.drawRanges = (BatchDrawRange*)UnsafeUtility.Malloc(UnsafeUtility.SizeOf<BatchDrawRange>(), UnsafeUtility.AlignOf<BatchDrawRange>(), Allocator.TempJob);
            dc.visibleInstances = (int*)UnsafeUtility.Malloc(4 * nVis, 4, Allocator.TempJob);
            dc.drawCommandPickingEntityIds = null;
            dc.instanceSortingPositions = null;
            dc.instanceSortingPositionFloatCount = 0;
            dc.drawCommandCount = nCmd;
            dc.drawRangeCount = 1;
            dc.visibleInstanceCount = nVis;
            int c = 0, v = 0;
            var keys = new List<int>(buckets.Keys);
            keys.Sort();
            foreach (int key in keys)
            {
                var b = buckets[key];
                if (b.visible.Count == 0)
                    continue;
                var k = kinds[b.kind];
                int start = v;
                foreach (uint idx in b.visible)
                    dc.visibleInstances[v++] = (int)idx;
                for (int s = 0; s < k.levels[b.level].subMeshCount; s++)
                    dc.drawCommands[c++] = new BatchDrawCommand
                    {
                        visibleOffset = (uint)start,
                        visibleCount = (uint)b.visible.Count,
                        batchID = batch,
                        materialID = k.material_,
                        meshID = k.meshes_[b.level],
                        submeshIndex = (ushort)s,
                        splitVisibilityMask = 0xff,
                        flags = b.fading ? BatchDrawCommandFlags.LODCrossFade : BatchDrawCommandFlags.None,
                        sortingPosition = 0,
                    };
            }
            dc.drawRanges[0] = new BatchDrawRange
            {
                drawCommandsBegin = 0,
                drawCommandsCount = (uint)nCmd,
                filterSettings = new BatchFilterSettings
                {
                    renderingLayerMask = 0xffffffff,
                    layer = 0,
                    shadowCastingMode = ShadowCastingMode.Off,
                    receiveShadows = false,
                    staticShadowCaster = false,
                    allDepthSorted = false,
                },
            };
            output.drawCommands[0] = dc;
            return default;
        }

        readonly Dictionary<Mesh, long> trisOf = new Dictionary<Mesh, long>();

        long Triangles(Mesh m)
        {
            if (!trisOf.TryGetValue(m, out long n))
            {
                n = 0;
                for (int s = 0; s < m.subMeshCount; s++)
                    n += m.GetIndexCount(s) / 3;
                trisOf[m] = n;
            }
            return n;
        }

        public void Dispose()
        {
            if (brg != null)
            {
                brg.Dispose();
                brg = null;
            }
            buffer?.Dispose();
            buffer = null;
        }
    }
}
