using System.Collections.Generic;
using System.Diagnostics;
using Unity.Collections;
using Unity.Jobs;
using UnityEngine;
using Overstory.World;
using Debug = UnityEngine.Debug;

namespace Overstory.Play
{
    /// <summary>
    /// What the walk collides with (LT1g, the walk, W4; docs/research/collision-and-navigation.md, item 4), built when
    /// the scene starts from the proxies tools/playable/proxies.py wrote (proxies.json: houses and walls as boxes, the
    /// gully's flights as ramps over their nosings, landings, cheek walls, stoops, blockers; doors and ways) and from
    /// the drawn clay ground, cut into one mesh collider per 64 m land chunk and cooked in jobs. Nothing here is drawn,
    /// and nothing is invented: every proxy is a box or a ramp the layout or the stair's sidecar gives, under the id of
    /// its record.
    ///
    /// Layers (by number; TagManager names them): 8 Walk, everything a walker's body meets; 9 Camera, what only the free
    /// camera meets (the roofs); 10 the walker's body; 11 the free camera. Each controller excludes the layers it does
    /// not meet (Collider.excludeLayers), so nothing global changes.
    ///
    /// Proxies are created sorted by id, so the same data always gives the same colliders in the same order.
    /// </summary>
    [DefaultExecutionOrder(-90)]
    public class WalkWorld : MonoBehaviour
    {
        public const int WalkLayer = 8, CameraLayer = 9, BodyLayer = 10, FlyLayer = 11;
        public const int WalkMask = 1 << WalkLayer, CameraMask = 1 << CameraLayer;

        [System.Serializable]
        public class Source { public string clay, heart_layout, centre_land, stair, cheeks; public int seed; }

        [System.Serializable]
        public class Proxy
        {
            public string id, kind, layer, flight, tag, name;
            public float x, y, a, l, w, z0, z1;   // a box: centre, angle (degrees, street), length along, width across, base, top
            public float[] p0, p1;                // a ramp: its top line, foot to top (street)
            public float t, rise;
            public int steps;
        }

        [System.Serializable]
        public class Door { public string id, name; public float x, y, z, a; public bool corner; }

        [System.Serializable]
        public class Way { public string name, kind; public float width; public bool door; public float[] pts; }

        [System.Serializable]
        public class Walking { public string flight; public float[] pts; }

        [System.Serializable]
        public class Data
        {
            public Source source;
            public float[] heart, corner;
            public float sea;
            public Proxy[] proxies;
            public Door[] doors;
            public Way[] ways;
            public Walking[] walking;
        }

        [Tooltip("tools/playable/proxies.py's output.")]
        public TextAsset proxies;
        [Tooltip("The drawn clay ground (the heart's, as the stair's staging sank it), cut into chunks for collision.")]
        public MeshFilter[] ground;
        [Tooltip("The land chunk, metres (D8.3).")]
        public float chunk = 64f;
        [Tooltip("Records that collide as their drawn houses (mesh colliders LT1Play.AddWalk puts under them), not as boxes.")]
        public string[] drawn = new string[0];

        public static WalkWorld Current { get; private set; }
        public Data data { get; private set; }
        public Transform Root { get; private set; }

        /// <summary>What the last Build made and what it cost (ms), for the report and CheckProxies.</summary>
        public int Boxes, Ramps, Chunks, ChunkTriangles, DrawnColliders;
        public double ParseMs, BoxesMs, SplitMs, BakeMs;

        /// <summary>The heart's box in Unity space (x, z): the walk stays inside it.</summary>
        public Rect Heart { get; private set; }
        public float Sea => data != null ? data.sea : -0.2f;

        void Awake()
        {
            Current = this;
            Build();
        }

        void OnDestroy()
        {
            if (Current == this)
                Current = null;
        }

        /// <summary>Builds every proxy under a root of its own (once; Clear undoes it). Also from the editor's check.</summary>
        public void Build()
        {
            if (Root != null)
                return;
            Current = this;
            var watch = Stopwatch.StartNew();
            data = JsonUtility.FromJson<Data>(proxies.text);
            Heart = Rect.MinMaxRect(data.heart[0], data.heart[1], data.heart[2], data.heart[3]);
            ParseMs = watch.Elapsed.TotalMilliseconds;

            Root = new GameObject("Proxies (the walk)").transform;
            Root.SetParent(transform, false);
            Root.gameObject.hideFlags = HideFlags.DontSave;

            watch.Restart();
            Boxes = Ramps = 0;
            var asDrawn = new HashSet<string>(drawn ?? new string[0]);
            foreach (var p in data.proxies)
            {
                if (asDrawn.Contains(p.id) || p.id.EndsWith("/roof", System.StringComparison.Ordinal) && asDrawn.Contains(p.id.Substring(0, p.id.Length - 5)))
                    continue;
                if (p.kind == "ramp")
                {
                    MakeRamp(p);
                    Ramps++;
                }
                else
                {
                    MakeBox(p);
                    Boxes++;
                }
            }
            BoxesMs = watch.Elapsed.TotalMilliseconds;
            // the drawn houses' colliders (in the scene, cooked when the player was built): each must have a shape
            if (drawn != null && drawn.Length > 0)
            {
                int shaped = 0, all = 0;
                foreach (var mc in FindObjectsByType<MeshCollider>(FindObjectsSortMode.None))
                {
                    var wp = mc.GetComponent<WalkProxy>();
                    if (wp == null || !wp.id.Contains("/1989/"))
                        continue;
                    all++;
                    if (mc.sharedMesh != null && mc.bounds.size.sqrMagnitude > 1f)
                        shaped++;
                }
                DrawnColliders = shaped;
                if (shaped < drawn.Length || shaped < all)
                    Debug.LogError($"[WalkWorld] {all - shaped} of {all} drawn houses' colliders have no shape ({string.Join(", ", drawn)})");
            }
            BuildGround();
            Physics.SyncTransforms();
            if (Application.isPlaying)
                Debug.Log($"[WalkWorld] {Boxes} boxes, {Ramps} ramps, {Chunks} ground chunks ({ChunkTriangles} triangles), {DrawnColliders} drawn houses: " +
                          $"built in {ParseMs + BoxesMs + SplitMs + BakeMs:F0} ms (read {ParseMs:F0}, boxes {BoxesMs:F0}, ground cut {SplitMs:F0}, cooked {BakeMs:F0})");
        }

        public void Clear()
        {
            if (Root == null)
                return;
            foreach (var mc in Root.GetComponentsInChildren<MeshCollider>())
                if (mc.sharedMesh != null)
                {
                    if (Application.isPlaying) Destroy(mc.sharedMesh); else DestroyImmediate(mc.sharedMesh);
                }
            if (Application.isPlaying) Destroy(Root.gameObject); else DestroyImmediate(Root.gameObject);
            Root = null;
        }

        GameObject Make(string id, string kind, int layer, string flight = null)
        {
            var go = new GameObject(id) { layer = layer };
            go.transform.SetParent(Root, false);
            var wp = go.AddComponent<WalkProxy>();
            wp.id = id;
            wp.kind = kind;
            wp.flight = string.IsNullOrEmpty(flight) ? null : flight;
            return go;
        }

        void MakeBox(Proxy p)
        {
            var go = Make(p.id, p.kind, p.layer == "camera" ? CameraLayer : WalkLayer, p.flight);
            // street (x, y) turned by a counter-clockwise is Unity's turn by -a about up (StreetSpace: x, z, y)
            go.transform.SetPositionAndRotation(StreetSpace.ToUnity(p.x, p.y, (p.z0 + p.z1) * 0.5f), Quaternion.Euler(0f, -p.a, 0f));
            var bc = go.AddComponent<BoxCollider>();
            bc.size = new Vector3(p.l, p.z1 - p.z0, p.w);
        }

        void MakeRamp(Proxy p)
        {
            var go = Make(p.id, p.kind, WalkLayer, p.flight);
            Vector3 a = StreetSpace.ToUnity(p.p0[0], p.p0[1], p.p0[2]);
            Vector3 b = StreetSpace.ToUnity(p.p1[0], p.p1[1], p.p1[2]);
            Vector3 fwd = (b - a).normalized;
            var rot = Quaternion.LookRotation(fwd, Vector3.up);
            go.transform.SetPositionAndRotation((a + b) * 0.5f - rot * Vector3.up * (p.t * 0.5f), rot);
            var bc = go.AddComponent<BoxCollider>();
            bc.size = new Vector3(p.w, p.t, Vector3.Distance(a, b));
            var wp = go.GetComponent<WalkProxy>();
            var level = new Vector3(b.x - a.x, 0f, b.z - a.z);
            wp.start = a;
            wp.length = level.magnitude;
            wp.up = level / wp.length;
            wp.rise = p.rise;
        }

        /// <summary>The ground's cooking: the MeshCollider's own defaults, so the collider reuses the bake.</summary>
        const MeshColliderCookingOptions Cooking = MeshColliderCookingOptions.CookForFasterSimulation | MeshColliderCookingOptions.EnableMeshCleaning
                                                 | MeshColliderCookingOptions.WeldColocatedVertices | MeshColliderCookingOptions.UseFastMidphase;

        struct Bake : IJobParallelFor
        {
            [ReadOnly] public NativeArray<EntityId> ids;
            public void Execute(int i) => Physics.BakeMesh(ids[i], false, Cooking);
        }

        /// <summary>The drawn ground, cut by each triangle's middle into land chunks, each one static mesh collider.</summary>
        void BuildGround()
        {
            var watch = Stopwatch.StartNew();
            var buckets = new SortedDictionary<long, List<int>>();   // chunk key -> (filter, triangle) pairs, flattened
            var verts = new List<Vector3[]>();
            var tris = new List<int[]>();
            for (int f = 0; f < ground.Length; f++)
            {
                var mf = ground[f];
                if (mf == null || mf.sharedMesh == null)
                    continue;
                var mesh = mf.sharedMesh;
                if (!mesh.isReadable && Application.isPlaying)
                {
                    Debug.LogError($"[WalkWorld] {mf.name}'s mesh is not readable: no ground collision");
                    continue;
                }
                var v = mesh.vertices;
                var l2w = mf.transform.localToWorldMatrix;
                for (int i = 0; i < v.Length; i++)
                    v[i] = l2w.MultiplyPoint3x4(v[i]);
                var t = mesh.triangles;
                verts.Add(v);
                tris.Add(t);
                int fi = verts.Count - 1;
                for (int k = 0; k < t.Length; k += 3)
                {
                    Vector3 c = (v[t[k]] + v[t[k + 1]] + v[t[k + 2]]) / 3f;
                    long key = Key(Mathf.FloorToInt(c.x / chunk), Mathf.FloorToInt(c.z / chunk));
                    if (!buckets.TryGetValue(key, out var list))
                        buckets[key] = list = new List<int>();
                    list.Add(fi);
                    list.Add(k);
                }
            }

            var meshes = new List<Mesh>();
            var names = new List<string>();
            ChunkTriangles = 0;
            foreach (var kv in buckets)
            {
                var list = kv.Value;
                var cv = new List<Vector3>();
                var ct = new List<int>(list.Count / 2 * 3);
                var map = new Dictionary<long, int>();
                for (int n = 0; n < list.Count; n += 2)
                {
                    int fi = list[n], k = list[n + 1];
                    var v = verts[fi];
                    var t = tris[fi];
                    for (int c = 0; c < 3; c++)
                    {
                        long vk = ((long)fi << 32) | (uint)t[k + c];
                        if (!map.TryGetValue(vk, out int idx))
                        {
                            idx = cv.Count;
                            cv.Add(v[t[k + c]]);
                            map[vk] = idx;
                        }
                        ct.Add(idx);
                    }
                }
                var m = new Mesh { name = ChunkName(kv.Key), indexFormat = UnityEngine.Rendering.IndexFormat.UInt32, hideFlags = HideFlags.DontSave };
                m.SetVertices(cv);
                m.SetTriangles(ct, 0, true);
                meshes.Add(m);
                names.Add(m.name);
                ChunkTriangles += ct.Count / 3;
            }
            SplitMs = watch.Elapsed.TotalMilliseconds;

            watch.Restart();
            var ids = new NativeArray<EntityId>(meshes.Count, Allocator.TempJob);
            for (int i = 0; i < meshes.Count; i++)
                ids[i] = meshes[i].GetEntityId();
            new Bake { ids = ids }.Schedule(meshes.Count, 1).Complete();
            ids.Dispose();
            for (int i = 0; i < meshes.Count; i++)
            {
                var go = Make(names[i], "ground", WalkLayer);
                var mc = go.AddComponent<MeshCollider>();
                mc.cookingOptions = Cooking;
                mc.sharedMesh = meshes[i];   // reuses the job's bake (same mesh, same options)
            }
            BakeMs = watch.Elapsed.TotalMilliseconds;
            Chunks = meshes.Count;
        }

        static long Key(int i, int j) => ((long)(i + 100000) << 20) | (uint)(j + 100000);

        static string ChunkName(long key)
        {
            int i = (int)(key >> 20) - 100000, j = (int)(key & 0xFFFFF) - 100000;
            return "heart/ground/" + i.ToString(System.Globalization.CultureInfo.InvariantCulture) + "_" + j.ToString(System.Globalization.CultureInfo.InvariantCulture);
        }

        /// <summary>The proxy a collider stands for, or null.</summary>
        public static WalkProxy Of(Collider c) => c != null ? c.GetComponent<WalkProxy>() : null;

        /// <summary>Whether a point (Unity space) lies inside the heart, at least margin metres from its edge.</summary>
        public bool InHeart(Vector3 p, float margin) =>
            p.x >= Heart.xMin + margin && p.x <= Heart.xMax - margin && p.z >= Heart.yMin + margin && p.z <= Heart.yMax - margin;
    }
}
