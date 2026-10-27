using System;
using System.Collections.Generic;
using System.IO;
using Overstory.Growth;
using UnityEngine;
using UnityEngine.Rendering;

#pragma warning disable 0649   // the data's fields, filled by JsonUtility

namespace Overstory.EditorTools.Corner
{
    /// <summary>
    /// The growth in the painted corner (the art-direction page, The growth): lichen and moss drawn in the stones' and
    /// the rock's own surfaces (CornerGrowth.hlsl calls Shaders/GrowthPaint.hlsl; this sets its values), and the heath
    /// above E and the weeds in D's yard as tufts through the growth's own BatchRendererGroup (GrowthTufts, Shaders/
    /// GrowthTuft.shader). Until the rock and ground's rock lands, the clay knuckle takes its lichen from an overlay
    /// (Shaders/GrowthOverlay.shader) by the rock's rules.
    ///
    /// What grows where, the meshes and the values are the generator's (blender/parts/growth/corner.py, from the record,
    /// the pack and fixtures/lt1-corner-growth.json, into cache/growth/corner/growth.json); its own data
    /// (Elements/growth/growth.json) holds only the page's shapes. It runs after the other elements (Order), so it can
    /// see whether a rock is drawn.
    /// </summary>
    static class LT1CornerGrowth
    {
        [Serializable] class Data { public string cache; public StandInData standIn; }
        [Serializable] class StandInData { public bool on; public float[] box, open; public float floor, floorUp, top, foot; }

        [Serializable] class Made { public string pack; public float date; public Global[] globals; public StandIn standIn; public TuftSet tufts; }
        [Serializable] class Global { public string name; public float[] v; }
        [Serializable] class StandIn { public float years; public float[] rule, foot; public float mossMax, mossOverLichen; }
        [Serializable] class TuftSet { public float[] to; public float fade, thinFrom, keepAt120, widen; public Look look; public string[] habitats; public TuftKind[] kinds; }
        [Serializable] class Look { public float calm, lamp, veil, root, tipLift, hueDetail, wet, shrinkBand, sink, minPx; }
        [Serializable] class TuftKind { public string species; public int variant; public string[] levels; public int[] tris; public float height, radius; public float[] @base, tip, seed; public float hue; public float[] instances; }

        const int Stride = 10;   // x y z, turn, scale, lean x y, rank, hue, habitat

        [CornerElement("growth", Order = 100)]
        static void Growth(CornerContext corner)
        {
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            var data = corner.Data<Data>("growth.json");
            string cache = Path.Combine(repo, data.cache);
            if (!File.Exists(cache))
                throw new FileNotFoundException($"the growth is not made: run blender/parts/growth/corner.py ({data.cache})");
            var made = JsonUtility.FromJson<Made>(File.ReadAllText(cache));

            foreach (var g in made.globals)
                corner.SetGlobal(g.name, new Vector4(g.v[0], g.v[1], g.v[2], g.v[3]));
            var T = made.tufts;
            corner.SetGlobal("_GT_Look", new Vector4(T.look.calm, T.look.lamp, T.look.veil, T.look.root));
            corner.SetGlobal("_GT_Thin", new Vector4(T.thinFrom, T.keepAt120, T.widen, T.look.shrinkBand));
            corner.SetGlobal("_GT_LookB", new Vector4(T.look.tipLift, T.look.hueDetail, T.look.wet, T.look.minPx));

            bool rock = RockDrawn(corner);
            int stand = data.standIn != null && data.standIn.on && !rock ? StandInOverlay(corner, data.standIn, made.standIn) : 0;
            int tufts = Tufts(corner, repo, T);
            Debug.Log($"[Growth] {made.pack} {made.date}: lichen and moss in the surfaces; the knuckle's stand-in on {stand} clay pieces" +
                      (rock ? " (off: a rock is drawn)" : "") + $"; {tufts} tufts in {T.kinds.Length} kinds");
        }

        // whether another element draws the rock (its root named rock...)
        static bool RockDrawn(CornerContext corner)
        {
            var parent = corner.Root.transform.parent;
            if (parent == null)
                return false;
            foreach (Transform t in parent)
                if (t.gameObject != corner.Root && t.name.StartsWith("rock", StringComparison.OrdinalIgnoreCase)
                    && t.GetComponentsInChildren<Renderer>(true).Length > 0)
                    return true;
            return false;
        }

        static int StandInOverlay(CornerContext corner, StandInData d, StandIn r)
        {
            var b = d.box;
            Vector3 a = CornerContext.World(b[0], b[1], b[2]), c = CornerContext.World(b[3], b[4], b[5]);
            var box = new Bounds();
            box.SetMinMax(Vector3.Min(a, c), Vector3.Max(a, c));
            var mat = corner.Keep(new Material(Shader.Find("Hidden/Overstory/GrowthOverlay")) { name = "growth: the knuckle's stand-in" });
            mat.SetFloat("_Source", 1f);
            mat.SetVector("_StandMin", box.min);
            mat.SetVector("_StandMax", box.max);
            mat.SetVector("_StandFloor", new Vector4(d.floor, d.floorUp, d.top, 0f));
            mat.SetVector("_StandRule", new Vector4(r.rule[0], r.rule[1], r.rule[2], r.years));
            mat.SetVector("_StandFoot", new Vector4(d.foot, r.foot[0], r.foot[1], r.foot[2]));
            mat.SetFloat("_StandMoss", r.mossMax);
            if (d.open != null && d.open.Length == 3)
                mat.SetVector("_StandOpen", new Vector4(d.open[0], d.open[1], d.open[2], 0f));
            var parent = new GameObject("knuckle stand-in").transform;
            parent.SetParent(corner.Root.transform, false);
            int n = 0;
            foreach (var piece in corner.Greybox)
            {
                if (piece.Class != 1 || piece.Hidden || piece.Renderer == null || !piece.Renderer.bounds.Intersects(box))
                    continue;
                var mf = piece.Renderer.GetComponent<MeshFilter>();
                if (mf == null || mf.sharedMesh == null)
                    continue;
                var t = piece.Renderer.transform;
                var mr = corner.Add($"lichen over {piece.Name}", mf.sharedMesh, mat, parent, ShadowCastingMode.Off);
                mr.transform.SetPositionAndRotation(t.position, t.rotation);
                mr.transform.localScale = t.lossyScale;
                mr.receiveShadows = false;
                n++;
            }
            return n;
        }

        static int Tufts(CornerContext corner, string repo, TuftSet T)
        {
            var go = new GameObject("tufts");
            go.transform.SetParent(corner.Root.transform, false);
            var shader = Shader.Find("Hidden/Overstory/GrowthTuft");
            if (shader == null)
                throw new InvalidOperationException("Hidden/Overstory/GrowthTuft is missing");
            var mats = new Dictionary<string, Material>();
            var kinds = new List<GrowthTufts.Kind>();
            int n = 0;
            foreach (var k in T.kinds)
            {
                if (!mats.TryGetValue(k.species, out var m))
                {
                    m = corner.Keep(new Material(shader) { name = $"growth: {k.species}" });
                    m.SetColor("_Base", new Color(k.@base[0], k.@base[1], k.@base[2], 1f));
                    m.SetColor("_Tip", new Color(k.tip[0], k.tip[1], k.tip[2], 1f));
                    m.SetColor("_Seed", new Color(k.seed[0], k.seed[1], k.seed[2], 1f));
                    m.SetFloat("_Hue", k.hue);
                    mats[k.species] = m;
                }
                var levels = new Mesh[k.levels.Length];
                for (int l = 0; l < levels.Length; l++)
                    levels[l] = corner.Keep(LoadTuft(Path.Combine(repo, k.levels[l]), $"growth: {k.species} {k.variant} L{l}"));
                int count = k.instances.Length / Stride;
                var mtx = new Matrix4x4[count];
                var users = new uint[count];
                for (int i = 0; i < count; i++)
                {
                    int o = i * Stride;
                    var I = k.instances;
                    var pos = CornerContext.World(I[o], I[o + 1], I[o + 2] - T.look.sink);
                    // the street's turn (anticlockwise seen from above) is Unity's turn about up the other way; the lean
                    // tips its top toward street x and y
                    var rot = Quaternion.Euler(I[o + 6] * Mathf.Rad2Deg, 0f, -I[o + 5] * Mathf.Rad2Deg)
                              * Quaternion.Euler(0f, -I[o + 3] * Mathf.Rad2Deg, 0f);
                    mtx[i] = Matrix4x4.TRS(pos, rot, Vector3.one * I[o + 4]);
                    uint rank = (uint)Mathf.Clamp(Mathf.RoundToInt(I[o + 7] * 255f), 0, 255);
                    uint hue = (uint)Mathf.Clamp(Mathf.RoundToInt(I[o + 8] * 255f), 0, 255);
                    users[i] = rank | (hue << 8) | ((uint)Mathf.RoundToInt(I[o + 9]) << 16);
                }
                kinds.Add(new GrowthTufts.Kind
                {
                    name = $"{k.species} {k.variant}", levels = levels, material = m, to = T.to, fade = T.fade,
                    thinFrom = T.thinFrom, keepMin = T.keepAt120, radius = k.radius, matrices = mtx, users = users,
                });
                n += count;
            }
            var tufts = go.AddComponent<GrowthTufts>();
            tufts.kinds = kinds.ToArray();
            tufts.Rebuild();
            return n;
        }

        /// <summary>A tuft's R2B2 soup (blender/parts/growth/tufts.py): each triangle its own corners, in Unity's frame, its
        /// winding turned for Unity's; its first five UV sets kept (the rest are empty).</summary>
        static Mesh LoadTuft(string path, string name)
        {
            using var br = new BinaryReader(File.OpenRead(path));
            if (new string(br.ReadChars(4)) != "R2B2")
                throw new IOException($"{path}: not an R2B2 mesh");
            int count = br.ReadInt32();
            var v = new Vector3[count];
            for (int i = 0; i < count; i++)
                v[i] = new Vector3(br.ReadSingle(), br.ReadSingle(), br.ReadSingle());
            var nn = new Vector3[count];
            for (int i = 0; i < count; i++)
                nn[i] = new Vector3(br.ReadSingle(), br.ReadSingle(), br.ReadSingle());
            var mesh = new Mesh { name = name };
            mesh.vertices = v;
            mesh.normals = nn;
            for (int k = 0; k < 8; k++)
            {
                var uv = new List<Vector2>(count);
                for (int i = 0; i < count; i++)
                    uv.Add(new Vector2(br.ReadSingle(), br.ReadSingle()));
                if (k < 5)
                    mesh.SetUVs(k, uv);
            }
            var tri = new int[count];
            for (int i = 0; i < count; i += 3)
            {
                tri[i] = i;
                tri[i + 1] = i + 2;
                tri[i + 2] = i + 1;
            }
            mesh.triangles = tri;
            mesh.RecalculateBounds();
            mesh.UploadMeshData(false);
            return mesh;
        }
    }
}
