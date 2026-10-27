using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
using Object = UnityEngine.Object;
using Path = System.IO.Path;

namespace Overstory.EditorTools
{
    /// <summary>
    /// The walked corner's trees (fixtures/lt1-corner.json, trees): the meshes blender/parts/trees/corner.py writes
    /// (cache/trees/corner), placed on their ground at the level their distance from the eye asks for, drawn with
    /// Shaders/CornerTree.shader from the element's data (Experiments/LT1/Corner/Elements/trees/trees.json). Used by the
    /// painted corner's element (Corner/CornerTrees.cs) and by the trees' own stage stills in the heart (Still).
    ///
    ///     -executeMethod Overstory.EditorTools.LT1CornerTrees.Still [-moments 1750-sea-fog,...] [-views street,...]
    ///         [-looks grey,material] [-out reviews/lt1/trees/corner/stage] [-trees birch-yard,...] [-level near]
    /// </summary>
    public static class LT1CornerTrees
    {
        const string DataAsset = "Assets/Experiments/LT1/Corner/Elements/trees/trees.json";
        const string Lights = "Assets/Experiments/LT1/Heart/Light";

        [Serializable] public class Level { public string name; public float to; }
        [Serializable]
        public class PartLook
        {
            public string habit, part, albedo, albedo2, foot_colour, twig_colour;
            public float cutoff = 0.45f, mark_reach, veil = 1f;
            public float[] bands, values, lost, lamp, foot, marks, bark_tile, twig_r;
        }
        [Serializable] public class Look { public string cache, atlas; public Level[] levels; public PartLook[] parts; }
        [Serializable] public class TreeLevel { public string level, file; public int drawn; }
        [Serializable] public class TreeRow { public string id, habit; public float[] at; public float height; public TreeLevel[] levels; }
        [Serializable] public class Index { public TreeRow[] trees; }

        static string Repo => Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));

        public static Look ReadLook() => JsonUtility.FromJson<Look>(File.ReadAllText(Path.Combine(Repo, "unity", DataAsset)));
        public static Index ReadIndex() => JsonUtility.FromJson<Index>(File.ReadAllText(Path.Combine(Repo, ReadLook().cache)));

        static readonly string[] Parts = { "bark", "crown", "solid", "shadow" };

        /// <summary>A TRE1 mesh (corner.py): one Mesh per submesh, by name, each holding only its own vertices.</summary>
        public static List<(string name, Mesh mesh)> Load(string path)
        {
            using var br = new BinaryReader(File.OpenRead(path));
            if (Encoding.ASCII.GetString(br.ReadBytes(4)) != "TRE1")
                throw new IOException($"{path}: not a TRE1 mesh");
            int n = br.ReadInt32(), s = br.ReadInt32();
            var P = new Vector3[n];
            var N = new Vector3[n];
            var C = new Color[n];
            var U = new Vector2[3, n];
            for (int i = 0; i < n; i++)
            {
                P[i] = new Vector3(br.ReadSingle(), br.ReadSingle(), br.ReadSingle());
                N[i] = new Vector3(br.ReadSingle(), br.ReadSingle(), br.ReadSingle());
                C[i] = new Color(br.ReadSingle(), br.ReadSingle(), br.ReadSingle(), br.ReadSingle());
                for (int k = 0; k < 3; k++)
                    U[k, i] = new Vector2(br.ReadSingle(), br.ReadSingle());
            }
            var outList = new List<(string, Mesh)>();
            for (int sm = 0; sm < s; sm++)
            {
                string name = Encoding.ASCII.GetString(br.ReadBytes(16)).TrimEnd('\0');
                int c = br.ReadInt32();
                var idx = new int[c];
                for (int i = 0; i < c; i++)
                    idx[i] = br.ReadInt32();
                var remap = new Dictionary<int, int>();
                var vp = new List<Vector3>();
                var vn = new List<Vector3>();
                var vc = new List<Color>();
                var vu = new[] { new List<Vector2>(), new List<Vector2>(), new List<Vector2>() };
                var tri = new int[c];
                float reach = 0f;
                for (int i = 0; i < c; i++)
                {
                    int v = idx[i];
                    if (!remap.TryGetValue(v, out int w))
                    {
                        w = vp.Count;
                        remap[v] = w;
                        vp.Add(P[v]);
                        vn.Add(N[v]);
                        vc.Add(C[v]);
                        for (int k = 0; k < 3; k++)
                            vu[k].Add(U[k, v]);
                        reach = Mathf.Max(reach, U[2, v].magnitude);
                    }
                    tri[i] = w;
                }
                var mesh = new Mesh { name = $"{Path.GetFileNameWithoutExtension(path)} {name}", indexFormat = IndexFormat.UInt32 };
                mesh.SetVertices(vp);
                mesh.SetNormals(vn);
                mesh.SetColors(vc);
                for (int k = 0; k < 3; k++)
                    mesh.SetUVs(k, vu[k]);
                mesh.SetTriangles(tri, 0);
                mesh.RecalculateBounds();
                // a card reaches out from its pivot by its offset, turned to any eye
                var b = mesh.bounds;
                b.Expand(2f * reach);
                mesh.bounds = b;
                outList.Add((name, mesh));
            }
            return outList;
        }

        static Color Srgb(string hex)
        {
            if (string.IsNullOrEmpty(hex) || !ColorUtility.TryParseHtmlString(hex.StartsWith("#") ? hex : "#" + hex, out var c))
                throw new FormatException($"trees.json: not a colour: {hex}");
            return c;
        }

        static Vector4 V(float[] a, Vector4 fallback)
        {
            if (a == null || a.Length == 0)
                return fallback;
            var v = fallback;
            for (int i = 0; i < Mathf.Min(4, a.Length); i++)
                v[i] = a[i];
            return v;
        }

        /// <summary>The atlas, imported by ArtImport as a tree's spray (its name ends _clusters): data, not colour, its
        /// coverage kept in every mip so an alpha-tested crown never thins with distance.</summary>
        static Texture2D Atlas(string assetPath)
        {
            var t = AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath);
            if (t == null)
                throw new FileNotFoundException($"no atlas at {assetPath} (blender/parts/trees/mass_card.py unity/{assetPath})");
            return t;
        }

        /// <summary>One part's material from the data.</summary>
        public static Material Make(PartLook l, string part, bool painted, bool grey, Texture atlas, Vector3 lampHead, Color lampSrgb)
        {
            int p = Array.IndexOf(Parts, part);
            var m = new Material(Shader.Find("Overstory/CornerTree")) { name = $"tree {l.habit} {part}" };
            m.SetFloat("_Part", p);
            if (painted)
                m.EnableKeyword("CT_PAINTED");
            m.SetFloat("_Grey", grey ? 1f : 0f);
            m.SetTexture("_Cards", atlas);
            m.SetFloat("_Cutoff", l.cutoff);
            m.SetFloat("_AlphaToMask", p == 1 ? 1f : 0f);
            m.SetColor("_Albedo", Srgb(l.albedo));
            m.SetColor("_Albedo2", Srgb(l.albedo2 ?? l.albedo));
            m.SetColor("_FootColour", Srgb(l.foot_colour ?? l.albedo));
            m.SetVector("_Bands", V(l.bands, new Vector4(0.45f, -0.2f, 0.08f, 0.25f)));
            m.SetVector("_Values", V(l.values, new Vector4(1f, 0.62f, 0.32f, 0f)));
            m.SetVector("_Lost", V(l.lost, new Vector4(0.7f, 0.6f, 0f, 0f)));
            m.SetVector("_Foot", V(l.foot, new Vector4(0.9f, 0.55f, 0.35f, 0.6f)));
            m.SetVector("_Marks", V(l.marks, new Vector4(3f, 0.32f, 0f, 0f)));
            m.SetFloat("_MarkReach", l.mark_reach);
            m.SetVector("_BarkTile", V(l.bark_tile, new Vector4(0.3f, 0.6f, 0f, 0f)));
            m.SetColor("_TwigColour", Srgb(l.twig_colour ?? l.albedo));
            m.SetVector("_TwigR", V(l.twig_r, new Vector4(0f, 0.001f, 0f, 0f)));
            m.SetVector("_Lamp", V(l.lamp, new Vector4(14f, 0.5f, 0.25f, 0.2f)));
            m.SetVector("_LampPos", lampHead);
            m.SetColor("_LampColour", lampSrgb);
            m.SetFloat("_Veil", l.veil);
            m.renderQueue = (int)RenderQueue.AlphaTest;
            return m;
        }

        /// <summary>The ground's height (Unity y) under a street point: the highest surface there that is not a house,
        /// a lamp or a tree (temporary colliders on what stands over the point).</summary>
        public static float Ground(float x, float y, Transform skip, float fallback)
        {
            var made = new List<Component>();
            try
            {
                foreach (var mr in Object.FindObjectsByType<MeshRenderer>())
                {
                    if (!mr.enabled || (skip != null && mr.transform.IsChildOf(skip)))
                        continue;
                    string nm = mr.name.ToLowerInvariant();
                    if (nm.Contains("house") || nm.Contains("lamp") || nm.Contains("tree") || nm.Contains("lantern")
                        || nm.Contains("water") || nm.Contains("sea"))
                        continue;
                    var b = mr.bounds;
                    if (x < b.min.x || x > b.max.x || y < b.min.z || y > b.max.z)
                        continue;
                    var mf = mr.GetComponent<MeshFilter>();
                    if (mf == null || mf.sharedMesh == null || mr.GetComponent<Collider>() != null)
                        continue;
                    var col = mr.gameObject.AddComponent<MeshCollider>();
                    col.sharedMesh = mf.sharedMesh;
                    made.Add(col);
                }
                Physics.SyncTransforms();
                float best = float.MinValue;
                foreach (var h in Physics.RaycastAll(new Vector3(x, 2000f, y), Vector3.down, 4000f))
                    best = Mathf.Max(best, h.point.y);
                return best > float.MinValue ? best : fallback;
            }
            finally
            {
                foreach (var c in made)
                    Object.DestroyImmediate(c);
            }
        }

        /// <summary>The corner's trees under parent, each on its ground at the level its distance from the camera asks
        /// for (or every level under a LODGroup when lods). Returns the renderers and what made them.</summary>
        public static List<(MeshRenderer mr, string habit, string part)> Place(Transform parent, Camera cam, bool painted, bool grey,
            Vector3 lampHead, Color lampSrgb, List<Object> made, bool lods = false, string onlyLevel = null)
        {
            var look = ReadLook();
            var idx = ReadIndex();
            var atlas = Atlas(look.atlas);
            var mats = new Dictionary<string, Material>();
            Material Mat(string habit, string part)
            {
                string key = $"{habit} {part}";
                if (mats.TryGetValue(key, out var m))
                    return m;
                var l = Array.Find(look.parts, q => q.habit == habit && q.part == (part == "shadow" ? "crown" : part))
                        ?? Array.Find(look.parts, q => q.habit == habit);
                if (l == null)
                    throw new ArgumentException($"trees.json has no look for {habit} {part}");
                m = Make(l, part, painted, grey, atlas, lampHead, lampSrgb);
                made?.Add(m);
                mats[key] = m;
                return m;
            }
            var placed = new List<(MeshRenderer, string, string)>();
            foreach (var t in idx.trees)
            {
                if (!Cli.Wanted("-trees", t.id))
                    continue;
                float g = Ground(t.at[0], t.at[1], parent, 0f);
                var root = new GameObject($"tree {t.id}");
                root.transform.SetParent(parent, false);
                root.transform.position = new Vector3(t.at[0], g, t.at[1]);
                float d = cam != null ? Vector3.Distance(cam.transform.position, root.transform.position + Vector3.up * 0.5f * t.height) : 0f;
                // the level its distance asks for, or the next coarser it has, or its finest
                string want = onlyLevel;
                if (want == null)
                    foreach (var lv in look.levels)
                        if (d <= lv.to) { want = lv.name; break; }
                var levels = new List<TreeLevel>();
                if (lods)
                    levels.AddRange(t.levels);
                else
                {
                    int wi = Array.FindIndex(look.levels, lv => lv.name == want);
                    TreeLevel pick = null;
                    for (int k = Mathf.Max(wi, 0); k < look.levels.Length && pick == null; k++)
                        pick = Array.Find(t.levels, tl => tl.level == look.levels[k].name);
                    levels.Add(pick ?? t.levels[0]);
                }
                var lodList = new List<LOD>();
                foreach (var lv in levels)
                {
                    var holder = new GameObject(lv.level);
                    holder.transform.SetParent(root.transform, false);
                    var rs = new List<Renderer>();
                    foreach (var (name, mesh) in Load(Path.Combine(Repo, lv.file)))
                    {
                        made?.Add(mesh);
                        var go = new GameObject(name);
                        go.transform.SetParent(holder.transform, false);
                        go.AddComponent<MeshFilter>().sharedMesh = mesh;
                        var mr = go.AddComponent<MeshRenderer>();
                        mr.sharedMaterial = Mat(t.habit, name);
                        mr.shadowCastingMode = name == "crown" ? ShadowCastingMode.Off
                            : name == "shadow" ? ShadowCastingMode.ShadowsOnly : ShadowCastingMode.On;
                        mr.lightProbeUsage = LightProbeUsage.Off;
                        mr.reflectionProbeUsage = ReflectionProbeUsage.Off;
                        rs.Add(mr);
                        placed.Add((mr, t.habit, name));
                    }
                    if (lods && cam != null)
                    {
                        var to = Array.Find(look.levels, q => q.name == lv.level)?.to ?? 1e5f;
                        float h = t.height / (2f * Mathf.Max(to, 1f) * Mathf.Tan(0.5f * cam.fieldOfView * Mathf.Deg2Rad));
                        lodList.Add(new LOD(Mathf.Clamp(h, 0.002f, 0.99f), rs.ToArray()));
                    }
                }
                if (lods && lodList.Count > 1)
                {
                    lodList.Sort((a, b) => b.screenRelativeTransitionHeight.CompareTo(a.screenRelativeTransitionHeight));
                    root.AddComponent<LODGroup>().SetLODs(lodList.ToArray());
                }
                Debug.Log($"[LT1CornerTrees] {t.id}: ground {g:F2} m, {d:F1} m from the eye, level {string.Join(",", levels.ConvertAll(q => q.level))} ({string.Join(",", levels.ConvertAll(q => q.drawn.ToString()))} triangles)");
            }
            return placed;
        }

        /// <summary>The trees' own views (besides LT1Stone.Views): at eye level under the yard birch, from the lane.</summary>
        static (string name, Vector3 pos, Vector3 target, float fov) OwnView(string name, Transform skip)
        {
            if (name == "eye-birch")
            {
                float g = Ground(49.4f, 16.0f, skip, 4.2f);
                var pos = new Vector3(49.4f, 16.0f, g + 1.65f);
                return (name, pos, new Vector3(44.6f, 22.6f, g + 1.65f + 6.0f), 46.4f);
            }
            if (name == "birch-across")
            {
                float g = Ground(52.0f, 14.0f, skip, 4.2f);
                var pos = new Vector3(52.0f, 14.0f, g + 1.65f);
                return (name, pos, new Vector3(44.2f, 22.4f, g + 1.65f + 4.5f), 46.4f);
            }
            return default;
        }

        /// <summary>The trees in the heart's own light (the corner staged as LT1Stone.Stage does), from the corner's
        /// views and the trees' own, in grey and in their material.</summary>
        public static void Still()
        {
            string outBase = Path.Combine(Repo, Cli.Arg("-out", "reviews/lt1/trees/corner/stage/still"));
            Directory.CreateDirectory(Path.GetDirectoryName(outBase));
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            var (stage, go) = LT1Stone.Stage(false);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            var made = new List<Object>();
            var root = new GameObject("Trees (the corner's)");
            try
            {
                var viewNames = Cli.Arg("-views", "street").Split(',');
                var moments = Cli.Arg("-moments", "1750-sea-fog").Split(',');
                var looks = Cli.Arg("-looks", "grey,material").Split(',');
                string level = Cli.Arg("-level", null);
                foreach (var moment in moments)
                {
                    var rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");
                    if (rig == null)
                        throw new FileNotFoundException($"no rig {moment}");
                    stage.rig = rig;
                    stage.Apply();
                    foreach (var viewName in viewNames)
                    {
                        var view = Array.Find(LT1Stone.Views, v => v.name == viewName);
                        if (view.name == null)
                            view = OwnView(viewName, root.transform);
                        if (view.name == null)
                            throw new ArgumentException($"no view {viewName}");
                        LT1Stone.Aim(stage, shot, view);
                        foreach (var look in looks)
                        {
                            for (int i = root.transform.childCount - 1; i >= 0; i--)
                                Object.DestroyImmediate(root.transform.GetChild(i).gameObject);
                            Place(root.transform, stage.view, false, look == "grey", Vector3.down * 1000f, Color.black, made, false, level);
                            string file = $"{outBase}-{moment}-{viewName}-{look}.png";
                            LT1Render.Still(stage.view, file, grey: true, eighth: false, msaa: 4);
                            Debug.Log($"[LT1CornerTrees] {file}");
                        }
                    }
                }
            }
            finally
            {
                Object.DestroyImmediate(root);
                foreach (var o in made)
                    if (o != null)
                        Object.DestroyImmediate(o);
                ShaderUtil.allowAsyncCompilation = async;
                urp.shadowDistance = reach;
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
            }
        }
    }
}
