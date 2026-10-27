using System.Collections.Generic;
using System.Globalization;
using System.IO;
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
    /// The walked corner's timber houses (tools/houses.py: each built from its facts, its era's working and the date)
    /// drawn in place of their clay, from the target frame's street stop or a house front at eye level, in grey and in
    /// their material, and a sheet beside the target frame.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Houses.Still
    ///         -mesh cache/houses -out reviews/lt1/houses/first-pass/round01 [-houses C,D,E]
    ///         [-moment 1750-sea-fog,1300-drizzle] [-view street,c-east] [-looks grey,material] [-debug 0]
    ///         [-tier near] (street or city: each house's NAME.TIER.bin, from tools/houses.py --tiers)
    ///         [-ref reviews/lt1/heart/target/3-street-gully-steps-target.png]
    ///
    /// The clay of each house drawn is cut out of the corner's clay in memory (its triangles over the house's
    /// footprint, from cache/houses/houses.json), never removed. Frames are OUT-moment-view-look.png; the sheet puts the
    /// target first, then every frame, two to a row.
    /// </summary>
    public static class LT1Houses
    {
        const string Lights = "Assets/Experiments/LT1/Heart/Light";
        const float Lens28 = 46.4f, Lens35 = 37.8f;

        /// <summary>The houses' own views (street metres), beside the gully's (LT1Stone.Views).</summary>
        static readonly (string name, Vector3 pos, Vector3 target, float fov)[] Views =
        {
            // a person on Gully Steps beside C, looking across at its east wall (its eave side, lit in the target)
            ("c-east", new Vector3(47.5f, 33.0f, 9.05f), new Vector3(41.4f, 35.5f, 10.2f), Lens35),
            // C's back gable from below, the one the target frame shows
            ("c-back", new Vector3(44.5f, 24.0f, 7.0f), new Vector3(38.0f, 30.9f, 11.0f), Lens35),
            // a person on Gully Steps across from D, looking up at its west wall over the retaining wall: the empty house
            // beside C's kept one
            ("d-west", new Vector3(48.6f, 47.0f, 9.6f), new Vector3(53.6f, 43.6f, 14.2f), Lens35),
        };

        [System.Serializable] class Coat { public string colour, srgb, paint, under, underSrgb; public float year; public int count; }
        [System.Serializable] class Coats { public Coat body, back, trim, window, door; }
        [System.Serializable] class Roof { public string material; public float year; }
        [System.Serializable] class Row { public string name; public int index; public int id; public float[] fp; public Coats coats; public Roof roof; }

        // the pack's records the house shader reads (paint.json, materials/*.json): one shape for every simple material
        [System.Serializable] class Chalk { public float perDecade, towardValue, keepChroma; }
        [System.Serializable] class Gloss { public float @new, old, halfYears; }
        [System.Serializable] class Peel { public float onsetYears, spanYears, flakeMm, alongGrain, toWood; }
        [System.Serializable] class Weather { public float southFactor, footM, footFactor, lapFactor, boardSpread, dripFactor, endFactor, rainFactor, rainFromDeg; }
        [System.Serializable] class Curtains { public string srgb; public float share, opacity, depthM, valanceShare, foldsPerM; }
        [System.Serializable] class Room
        {
            public string srgbLamp, srgbWalls, srgbCeiling, srgbFloor;
            public string srgbFurniture, srgbShade;
            public float lampPower, lampSoftM2, depthM, halfWidthM, sillM, heightM, ambient, lampDropM, lampSwingM;
            public float furnitureHeightM, furnitureHalfLengthM, cornerReachM, cornerLight, shadeRadiusM, shadeGlow;
            public Curtains curtains;
        }
        [System.Serializable] class Record
        {
            public string srgb, srgbNew, srgbOld, srgbWeathered, srgbDark;
            public float weatherHalfYears, oldYears, valueSpread, warmSpread;
            public float gloss = -1f;
            public float[] water;
            public float jointView = 1f, jointFar = 1f;
            public Chalk chalk;
            public Gloss glossCurve;
            public Peel peel;
            public Weather weather;
            public Soil soil;
            public float[] greySpread;
            public NailStain nailStain;
            public float boardingValueSpread;
            public Room room;
            public Daylight daylight;
            public Wave wave;
        }
        [System.Serializable] class Soil { public string srgb; public float perDecade, most, openShare; }
        [System.Serializable] class NailStain { public string srgb; public float most, downM, fromTopM, acrossM; public float[] widthMm; }
        [System.Serializable] class Daylight { public float window, backWall, ceiling, curtains; }
        [System.Serializable] class Wave { public float tiltDeg; public float[] perM; }

        // the houses buffer's rows a house (House.shader, OS_HOUSE_ROWS) and its painted parts in order
        const int HouseRows = 16;
        static readonly string[] Parts = { "body", "back", "trim", "window", "door" };
        static readonly int HousesId = Shader.PropertyToID("_OS_Houses");

        public static void Still()
        {
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string outBase = Path.Combine(repo, Cli.Arg("-out", "reviews/lt1/houses/first-pass/still"));
            Directory.CreateDirectory(Path.GetDirectoryName(outBase));
            var urp = (UniversalRenderPipelineAsset)GraphicsSettings.currentRenderPipeline;
            float reach = urp.shadowDistance;
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            var (stage, go) = LT1Stone.Stage(false);
            var shot = ScriptableObject.CreateInstance<CameraShot>();
            var made = new List<Object>();
            var root = new GameObject("houses") { hideFlags = HideFlags.DontSave };
            var restore = new List<(MeshFilter mf, Mesh mesh)>();
            buffer = null;
            try
            {
                string dir = Path.Combine(repo, Cli.Arg("-mesh", "cache/houses"));
                var all = JsonUtility.FromJson<Rows>(File.ReadAllText(Path.Combine(dir, "houses.json")));
                var rows = new List<Row>(all.houses);
                string pack = Path.Combine(repo, all.pack);
                var date = stage.GetComponent<Overstory.World.FabricDate>();
                int dy = Mathf.FloorToInt(all.date);
                date.Set(dy, 1 + Mathf.Clamp(Mathf.RoundToInt((all.date - dy) * 12f), 0, 11));
                var houses = Fill(rows, pack, all.paint);
                made.Add(houses.mat);
                made.Add(houses.grey);
                var names = Cli.Arg("-houses", "C").Split(',');
                var drawn = new List<(MeshRenderer mr, Material mat, Material grey)>();
                var cut = new List<Vector2[]>();
                foreach (var name in names)
                {
                    var row = rows.Find(r => r.name == name);
                    if (row == null)
                        throw new System.ArgumentException($"house {name} is not in {dir}/houses.json");
                    var fp = new Vector2[4];
                    for (int i = 0; i < 4; i++)
                        fp[i] = new Vector2(row.fp[2 * i], row.fp[2 * i + 1]);
                    cut.Add(fp);
                    string tier = Cli.Arg("-tier", "near");
                    var m = LT1R2b.Load(Path.Combine(dir, tier == "near" ? $"{name}.bin" : $"{name}.{tier}.bin"));
                    m.name = $"house {name}";
                    made.Add(m);
                    var g = new GameObject(name);
                    g.transform.SetParent(root.transform, false);
                    g.AddComponent<MeshFilter>().sharedMesh = m;
                    var mr = g.AddComponent<MeshRenderer>();
                    mr.shadowCastingMode = ShadowCastingMode.On;
                    var mat = houses.mat;
                    var grey = houses.grey;
                    drawn.Add((mr, mat, grey));
                    Debug.Log($"[LT1Houses] {name} ({row.id}): {m.vertexCount / 3} triangles");
                }
                // the clay of the houses drawn, cut out of the corner's mesh in memory
                foreach (var mf in Object.FindObjectsByType<MeshFilter>(FindObjectsSortMode.None))
                {
                    if (mf.transform.root == root.transform || mf.sharedMesh == null || !mf.name.StartsWith("buildings_"))
                        continue;
                    var kept = CutClay(mf, cut);
                    if (kept == null)
                        continue;
                    made.Add(kept);
                    restore.Add((mf, mf.sharedMesh));
                    mf.sharedMesh = kept;
                }
                var viewNames = Cli.Arg("-view", "street").Split(',');
                var moments = Cli.Arg("-moment", "1750-sea-fog").Split(',');
                var looks = Cli.Arg("-looks", "grey,material").Split(',');
                var files = new List<string>();
                foreach (var moment in moments)
                {
                    var rig = AssetDatabase.LoadAssetAtPath<LightRig>($"{Lights}/Heart_{moment}.asset");
                    if (rig == null)
                        throw new FileNotFoundException($"no rig {moment}");
                    stage.rig = rig;
                    stage.Apply();
                    foreach (var viewName in viewNames)
                    {
                        var view = System.Array.Find(Views, v => v.name == viewName);
                        if (view.name == null)
                            view = System.Array.Find(LT1Stone.Views, v => v.name == viewName);
                        if (view.name == null)
                            throw new System.ArgumentException($"no view {viewName}");
                        LT1Stone.Aim(stage, shot, view);
                        foreach (var look in looks)
                        {
                            foreach (var (mr, mat, grey) in drawn)
                                mr.sharedMaterial = look == "grey" ? grey : mat;
                            string file = $"{outBase}-{moment}-{viewName}-{look}.png";
                            LT1Render.Still(stage.view, file, grey: true, eighth: false, msaa: 4);
                            files.Add(file);
                        }
                    }
                }
                string refFile = Cli.Arg("-ref", "reviews/lt1/heart/target/3-street-gully-steps-target.png");
                var sheet = new List<string>();
                if (refFile != "")
                    sheet.Add(Path.Combine(repo, refFile));
                sheet.AddRange(files);
                Sheet(sheet, $"{outBase}-sheet.png");
            }
            finally
            {
                buffer?.Release();
                foreach (var (mf, mesh) in restore)
                    mf.sharedMesh = mesh;
                Object.DestroyImmediate(root);
                foreach (var o in made)
                    Object.DestroyImmediate(o);
                ShaderUtil.allowAsyncCompilation = async;
                urp.shadowDistance = reach;
                Object.DestroyImmediate(go);
                Object.DestroyImmediate(shot);
            }
        }

        [System.Serializable] class Rows { public float date; public string pack; public string paint; public Row[] houses; }

        static ComputeBuffer buffer;

        /// <summary>The houses' material (and its grey twin) and the houses buffer, all from the pack's records: each
        /// house's coats and roof (houses.json), each paint's chalk, gloss and peel (materials/paint-*.json), the
        /// roof coverings, the wood, stone, mortar, render and glass (materials/*.json) and the paint's weather
        /// (paint.json). Nothing here holds a look value of its own.</summary>
        static (Material mat, Material grey) Fill(List<Row> rows, string pack, string paintRule)
        {
            Record Read(string name) =>
                JsonUtility.FromJson<Record>(File.ReadAllText(Path.Combine(pack, name)).Replace("\"gloss\": {", "\"glossCurve\": {"));
            var paints = new List<string>();
            var covers = new List<string>();
            int Index(List<string> list, string name)
            {
                if (!list.Contains(name))
                    list.Add(name);
                return list.IndexOf(name);
            }
            int n = 0;
            foreach (var r in rows)
                n = Mathf.Max(n, r.index + 1);
            var data = new Vector4[n * HouseRows];
            foreach (var r in rows)
            {
                int o = r.index * HouseRows;
                for (int p = 0; p < Parts.Length; p++)
                {
                    var c = (Coat)typeof(Coats).GetField(Parts[p]).GetValue(r.coats);
                    var top = Linear(c.srgb);
                    data[o + 3 * p] = new Vector4(top.r, top.g, top.b, c.year);
                    var under = c.underSrgb != "" ? Linear(c.underSrgb) : Color.black;
                    data[o + 3 * p + 1] = new Vector4(under.r, under.g, under.b, c.underSrgb != "" ? 1f : 0f);
                    data[o + 3 * p + 2] = new Vector4(Index(paints, c.paint), c.count, 0f, 0f);
                }
                data[o + 15] = new Vector4(Index(covers, r.roof.material), r.roof.year, 0f, 0f);
            }
            buffer = new ComputeBuffer(data.Length, 16);
            buffer.SetData(data);
            Shader.SetGlobalBuffer(HousesId, buffer);
            if (paints.Count > 4 || covers.Count > 4)
                throw new System.InvalidOperationException("the house shader holds four paints and four coverings");
            var chalk = new Vector4[4];
            var gloss = new Vector4[4];
            var peel = new Vector4[4];
            var paintWater = new Vector4[4];
            for (int i = 0; i < paints.Count; i++)
            {
                var m = Read($"materials/{paints[i]}.json");
                chalk[i] = new Vector4(m.chalk.perDecade, m.chalk.towardValue, m.chalk.keepChroma, 0f);
                // w: the share of the lost paint that goes to the wood, not to the coat under it
                gloss[i] = new Vector4(m.glossCurve.@new, m.glossCurve.old, m.glossCurve.halfYears, m.peel.toWood);
                peel[i] = new Vector4(m.peel.onsetYears, m.peel.spanYears, m.peel.flakeMm * 0.001f, m.peel.alongGrain);
                paintWater[i] = Water(m);
            }
            Shader.SetGlobalVectorArray("_OS_PaintChalk", chalk);
            Shader.SetGlobalVectorArray("_OS_PaintGloss", gloss);
            Shader.SetGlobalVectorArray("_OS_PaintPeel", peel);
            Shader.SetGlobalVectorArray("_OS_PaintWater", paintWater);
            var coverNew = new Vector4[4];
            var coverOld = new Vector4[4];
            var coverWater = new Vector4[4];
            for (int i = 0; i < covers.Count; i++)
            {
                var m = Read($"materials/{covers[i]}.json");
                coverNew[i] = With(Linear(m.srgbNew), m.gloss);
                coverOld[i] = With(Linear(m.srgbOld), m.oldYears);
                coverWater[i] = Water(m);
            }
            Shader.SetGlobalVectorArray("_OS_CoverNew", coverNew);
            Shader.SetGlobalVectorArray("_OS_CoverOld", coverOld);
            Shader.SetGlobalVectorArray("_OS_CoverWater", coverWater);
            var mat = new Material(Shader.Find("Overstory/House")) { hideFlags = HideFlags.DontSave };
            var pine = Read("materials/pine.json");
            mat.SetVector("_PineNew", With(Linear(pine.srgbNew), pine.weatherHalfYears));
            mat.SetVector("_PineOld", With(Linear(pine.srgbWeathered), pine.gloss));
            mat.SetVector("_WaterPine", Water(pine));
            mat.SetVector("_Boarding", new Vector4(pine.greySpread[0], pine.greySpread[1], pine.nailStain.downM, pine.nailStain.most));
            mat.SetVector("_Nails", With(Linear(pine.nailStain.srgb), pine.nailStain.fromTopM));
            mat.SetVector("_BoardingB", new Vector4(pine.nailStain.acrossM, pine.nailStain.widthMm[0] * 0.001f, pine.nailStain.widthMm[1] * 0.001f, pine.boardingValueSpread));
            var stone = Read("materials/fieldstone.json");
            mat.SetVector("_Stone", With(Linear(stone.srgb), stone.valueSpread));
            mat.SetVector("_StoneB", new Vector4(stone.warmSpread, stone.gloss, 0f, 0f));
            mat.SetVector("_WaterStone", Water(stone));
            var mortar = Read("materials/lime-mortar.json");
            mat.SetVector("_Mortar", With(Linear(mortar.srgb), mortar.gloss));
            mat.SetVector("_WaterMortar", Water(mortar));
            mat.SetFloat("_Joint", mortar.jointView);
            mat.SetFloat("_JointFar", mortar.jointFar);
            var render = Read("materials/render.json");
            mat.SetVector("_Render", With(Linear(render.srgb), render.gloss));
            mat.SetVector("_WaterRender", Water(render));
            var glass = Read("materials/glass.json");
            mat.SetVector("_Glass", new Vector4(0f, 0f, 0f, glass.gloss));
            var day = glass.daylight;
            mat.SetVector("_GlassDay", new Vector4(day.window, day.backWall, day.ceiling, day.curtains));
            mat.SetVector("_GlassWave", new Vector4(glass.wave.tiltDeg * Mathf.Deg2Rad, glass.wave.perM[0], glass.wave.perM[1], 0f));
            var room = glass.room;
            mat.SetVector("_Room", With(Linear(room.srgbLamp), room.lampPower));
            mat.SetVector("_RoomWall", With(Linear(room.srgbWalls), room.depthM));
            mat.SetVector("_RoomCeiling", With(Linear(room.srgbCeiling), room.halfWidthM));
            mat.SetVector("_RoomFloor", With(Linear(room.srgbFloor), room.sillM));
            mat.SetVector("_RoomShape", new Vector4(room.heightM, room.ambient, room.lampDropM, room.lampSwingM));
            mat.SetVector("_RoomFurniture", With(Linear(room.srgbFurniture), room.furnitureHeightM));
            mat.SetVector("_RoomFurniture2", new Vector4(room.furnitureHalfLengthM, room.cornerReachM, room.cornerLight, room.lampSoftM2));
            var shade = Linear(room.srgbShade) * room.shadeGlow;
            mat.SetVector("_RoomShade", new Vector4(room.shadeRadiusM, shade.r, shade.g, shade.b));
            var cu = room.curtains;
            mat.SetVector("_Curtain", With(Linear(cu.srgb), cu.share));
            mat.SetVector("_CurtainB", new Vector4(cu.opacity, cu.depthM, cu.valanceShare, cu.foldsPerM));
            var rule = Read(paintRule);
            var w = rule.weather;
            mat.SetVector("_Soil", new Vector4(rule.soil.perDecade, rule.soil.most, rule.soil.openShare, 0f));
            mat.SetColor("_SoilColour", Linear(rule.soil.srgb));
            mat.SetVector("_Weather", new Vector4(w.southFactor, w.footM, w.footFactor, w.lapFactor));
            mat.SetVector("_WeatherB", new Vector4(w.boardSpread, 0f, 0f, 0f));
            mat.SetVector("_WeatherC", new Vector4(w.dripFactor, w.endFactor, w.rainFactor, w.rainFromDeg * Mathf.Deg2Rad));
            mat.SetFloat("_Grey", 0f);
            mat.SetFloat("_Debug", float.Parse(Cli.Arg("-debug", "0"), CultureInfo.InvariantCulture));
            var grey = new Material(mat) { hideFlags = HideFlags.DontSave };
            grey.SetFloat("_Grey", 1f);
            return (mat, grey);
        }

        static Color Linear(string hex) =>
            ColorUtility.TryParseHtmlString("#" + hex, out var c) ? c.linear
                : throw new System.FormatException($"not a colour: {hex}");

        static Vector4 With(Color c, float a) => new Vector4(c.r, c.g, c.b, a);

        /// <summary>A material record's water profile (Water.hlsl: darkens, film gloss, holds, stains).</summary>
        static Vector4 Water(Record m) => new Vector4(m.water[0], m.water[1], m.water[2], m.water[3]);

        /// <summary>The mesh less its triangles standing over any of the footprints (grown by a metre for the eaves),
        /// or null when it has none there.</summary>
        static Mesh CutClay(MeshFilter mf, List<Vector2[]> footprints)
        {
            var src = mf.sharedMesh;
            var v = src.vertices;
            var toWorld = mf.transform.localToWorldMatrix;
            var w = new Vector2[v.Length];
            for (int i = 0; i < v.Length; i++)
            {
                var p = toWorld.MultiplyPoint3x4(v[i]);
                w[i] = new Vector2(p.x, p.z);
            }
            var dst = Object.Instantiate(src);
            dst.hideFlags = HideFlags.DontSave;
            bool any = false;
            for (int sm = 0; sm < src.subMeshCount; sm++)
            {
                var t = src.GetTriangles(sm);
                var keep = new List<int>(t.Length);
                for (int i = 0; i < t.Length; i += 3)
                {
                    var c = (w[t[i]] + w[t[i + 1]] + w[t[i + 2]]) / 3f;
                    bool inside = false;
                    foreach (var fp in footprints)
                        inside |= Inside(fp, c, 1.0f);
                    if (inside)
                    {
                        any = true;
                        continue;
                    }
                    keep.Add(t[i]);
                    keep.Add(t[i + 1]);
                    keep.Add(t[i + 2]);
                }
                dst.SetTriangles(keep, sm);
            }
            if (any)
                return dst;
            Object.DestroyImmediate(dst);
            return null;
        }

        /// <summary>Whether a point lies within a convex footprint grown by `grow` metres.</summary>
        static bool Inside(Vector2[] fp, Vector2 p, float grow)
        {
            float area = 0f;
            for (int i = 0; i < fp.Length; i++)
                area += fp[i].x * fp[(i + 1) % fp.Length].y - fp[(i + 1) % fp.Length].x * fp[i].y;
            float sign = Mathf.Sign(area);
            for (int i = 0; i < fp.Length; i++)
            {
                var a = fp[i];
                var b = fp[(i + 1) % fp.Length];
                // (how far inside this edge, in metres)
                float d = sign * ((b.x - a.x) * (p.y - a.y) - (b.y - a.y) * (p.x - a.x)) / (b - a).magnitude;
                if (d < -grow)
                    return false;
            }
            return true;
        }

        /// <summary>The sheet: each image fitted into 960 by 540, two to a row, in order.</summary>
        static void Sheet(List<string> images, string file)
        {
            const int W = 960, H = 540;
            int rows = (images.Count + 1) / 2;
            var sheet = new Texture2D(2 * W, rows * H, TextureFormat.RGB24, false);
            var fill = new Color32[2 * W * rows * H];
            for (int i = 0; i < fill.Length; i++)
                fill[i] = new Color32(24, 24, 24, 255);
            sheet.SetPixels32(fill);
            for (int k = 0; k < images.Count; k++)
            {
                var t = new Texture2D(2, 2);
                t.LoadImage(File.ReadAllBytes(images[k]));
                int x = (k % 2) * W, y = (rows - 1 - k / 2) * H;
                float s = Mathf.Min((float)W / t.width, (float)H / t.height);
                int dw = Mathf.RoundToInt(t.width * s), dh = Mathf.RoundToInt(t.height * s);
                var px = new Color[dw * dh];
                for (int j = 0; j < dh; j++)
                    for (int i = 0; i < dw; i++)
                        px[j * dw + i] = t.GetPixelBilinear((i + 0.5f) / dw, (j + 0.5f) / dh);
                sheet.SetPixels(x + (W - dw) / 2, y + (H - dh) / 2, dw, dh, px);
                Object.DestroyImmediate(t);
            }
            sheet.Apply();
            File.WriteAllBytes(file, sheet.EncodeToPNG());
            Object.DestroyImmediate(sheet);
        }
    }
}
