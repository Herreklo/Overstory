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
            // the parts at about 3 m, raking, so a casing's depth, a sill's drip and a reveal read: C's east window,
            // D's front window (raised, over the gully), E's front window at eye level
            ("c-win", new Vector3(44.0f, 33.4f, 9.8f), new Vector3(41.4f, 34.6f, 9.5f), Lens35),
            ("d-win", new Vector3(50.9f, 45.2f, 14.7f), new Vector3(53.6f, 46.95f, 14.1f), Lens35),
            ("e-win", new Vector3(52.9f, 88.9f, 18.25f), new Vector3(50.0f, 87.35f, 17.95f), Lens35),
            // the roofs from about 12 m up, across the gully: C's slate and its gutter, D's and E's pantiles against the
            // sky; and the eaves' corners at about 3 m, where a verge meets an eave
            ("c-roof", new Vector3(49.0f, 29.5f, 19.5f), new Vector3(40.0f, 34.6f, 14.5f), Lens35),
            ("c-eave", new Vector3(44.6f, 28.6f, 12.0f), new Vector3(41.8f, 31.4f, 12.6f), Lens35),
            ("d-roof", new Vector3(47.0f, 50.0f, 22.5f), new Vector3(55.5f, 44.3f, 18.5f), Lens35),
            ("d-eave", new Vector3(50.8f, 51.0f, 16.0f), new Vector3(53.7f, 47.9f, 16.7f), Lens35),
            ("c-wide", new Vector3(50.0f, 27.0f, 12.0f), new Vector3(40.0f, 34.6f, 11.0f), Lens35),
            ("e-roof", new Vector3(55.5f, 82.5f, 25.5f), new Vector3(47.0f, 89.5f, 22.5f), Lens35),
        };

        [System.Serializable] class Coat { public string colour, srgb, paint, under, underSrgb; public float year; public int count; }
        [System.Serializable] class Coats { public Coat body, back, trim, window, door; }
        [System.Serializable] class Roof { public string material; public float year; }
        [System.Serializable] class Row { public string name; public int index; public int id; public float[] fp; public Coats coats; public Roof roof; }

        // the pack's records the house shader reads (paint.json, materials/*.json): one shape for every simple material
        [System.Serializable] class Chalk { public float perDecade, towardValue, keepChroma; }
        [System.Serializable] class Gloss { public float @new, old, halfYears; }
        [System.Serializable] class Peel { public float onsetYears, spanYears, flakeMm, alongGrain, toWood; }
        [System.Serializable] class Weather { public float southFactor, footM, footFactor, lapFactor, boardSpread, patchSpread, patchM, gatherFactor, gatherM, dripFactor, endFactor, rainFactor, rainFromDeg; }
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
            public Source source;
            public Sawings sawings;
            public Stocks stocks;
            public Weathering weathering;
            public NailRust nailRust;
            public Room room;
            public Daylight daylight;
            public Wave wave;
        }
        [System.Serializable] class Soil { public string srgb; public float perDecade, most, openShare; }
        // the softwood's record (pine.json): its source, sawings, stocks, weathering and nails' rust
        [System.Serializable] class Source { public string srgbHeart, srgbKnot; public float[] heartShare, ringsPerM, knotMm; public float latewood, knotsPerM, knotGrey; }
        [System.Serializable] class Sawing { public float fibre, edgeMm; }
        [System.Serializable] class Sawings { public Sawing rough, planed; }
        [System.Serializable] class Stock { public float[] priorYears; public float valueSpread, filmShare, filmCover; public string srgbFilm; }
        [System.Serializable] class Stocks { public Stock formwork, @new; }
        [System.Serializable] class Weathering
        {
            public string srgbBrowned, srgbSilver, srgbDamp;
            public float brownHalfYears, dampMost, dampReachM, dampYears, shelterReachM, grainOld, grainYears, checksPerBoard, checkYears, cupping;
            public float[] greySpread, silverYears, streaks;
        }
        [System.Serializable] class NailRust { public string srgb, srgbIron; public float most, mPerYear, mostM, haloMm; public float[] widthMm; }
        // what the boarding is made of and how it is nailed (timber.json, boarding)
        [System.Serializable] class Nails { public float[] fromEndMm; public float acrossMm; }
        [System.Serializable] class Boarding { public string stock, sawing; public Nails nails; }
        [System.Serializable] class Timber { public Boarding boarding; }
        [System.Serializable] class Daylight { public float window, backWall, ceiling, curtains; }
        [System.Serializable] class Wave { public float tiltDeg; public float[] perM; }

        // the houses buffer's rows a house (House.shader, OS_HOUSE_ROWS) and its painted parts in order
        const int HouseRows = 16;
        static readonly string[] Parts = { "body", "back", "trim", "window", "door" };
        static readonly int HousesId = Shader.PropertyToID("_OS_Houses");

        /// <summary>
        /// The houses of a folder of their own in the painted corner (LT1ArtPasses.Paint), from the houses' views or the
        /// gully's. For the run that folder's houses stand in cache/houses and are put back after; each view is drawn
        /// from a copy of Paint.json (at -data) with its view, moment, tier, size and out changed, nothing else. A
        /// houses' view is drawn in the place of the gully's "high" for the run (in memory).
        ///
        ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Houses.Painted
        ///         -mesh cache/houses-hero -into reviews/lt1/houses/hero/windows/p01 -views c-win,eye-foot
        ///         [-moment 1750-sea-fog] [-tier near] [-size 1920x1080] -data /scratch/paint.json
        /// </summary>
        public static void Painted()
        {
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string unity = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string src = Path.Combine(repo, Cli.Arg("-mesh", "cache/houses-hero"));
            string live = Path.Combine(repo, "cache/houses");
            string data = Cli.Arg("-data", null) ?? throw new System.ArgumentException("-data: a scratch path for Paint.json's copy");
            string into = Cli.Arg("-into", "reviews/lt1/houses/hero/painted");
            string moment = Cli.Arg("-moment", "1750-sea-fog"), tier = Cli.Arg("-tier", "near");
            var size = Cli.Arg("-size", "1920x1080").Split('x');
            string paint = File.ReadAllText(Path.Combine(unity, "Assets/Experiments/LT1/ArtDirection/Paint.json"));
            string Set(string json, string key, string value) =>
                new System.Text.RegularExpressions.Regex($"\"{key}\"\\s*:\\s*(\"[^\"]*\"|[0-9.]+)").Replace(json, $"\"{key}\": {value}", 1);
            string keep = Path.Combine(Path.GetTempPath(), $"lt1-houses-live-{System.Diagnostics.Process.GetCurrentProcess().Id}");
            Directory.CreateDirectory(keep);
            var swapped = new List<string>();
            int hi = System.Array.FindIndex(LT1Stone.Views, v => v.name == "high");
            var high = LT1Stone.Views[hi];
            try
            {
                foreach (var file in Directory.GetFiles(src))
                {
                    string name = Path.GetFileName(file), at = Path.Combine(live, name);
                    if (File.Exists(at))
                        File.Copy(at, Path.Combine(keep, name), true);
                    swapped.Add(name);
                    File.Copy(file, at, true);
                }
                foreach (var viewName in Cli.Arg("-views", "eye-foot").Split(','))
                {
                    string drawn = viewName;
                    var own = System.Array.Find(Views, v => v.name == viewName);
                    if (own.name != null)
                    {
                        LT1Stone.Views[hi] = ("high", own.pos, own.target, own.fov);
                        drawn = "high";
                    }
                    string json = Set(paint, "view", $"\"{drawn}\"");
                    json = Set(json, "moment", $"\"{moment}\"");
                    json = Set(json, "tier", $"\"{tier}\"");
                    json = Set(json, "out", $"\"{into}-{moment}-{viewName}\"");
                    json = Set(json, "width", size[0]);
                    json = Set(json, "height", size[1]);
                    File.WriteAllText(data, json);
                    LT1ArtPasses.Paint();
                    LT1Stone.Views[hi] = high;
                }
            }
            finally
            {
                LT1Stone.Views[hi] = high;
                foreach (var name in swapped)
                {
                    string kept = Path.Combine(keep, name), at = Path.Combine(live, name);
                    if (File.Exists(kept))
                        File.Copy(kept, at, true);
                    else
                        File.Delete(at);
                }
                Directory.Delete(keep, true);
            }
        }

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

        /// <summary>The houses built where the town has them (tools/houses.py --street) for the town's render (LT1Town,
        /// -heroes): their material, its grey twin and the date they were built at, from dir's houses.json. Release
        /// frees the houses buffer.</summary>
        internal static (Material mat, Material grey, float date) Town(string dir, string repo)
        {
            var all = JsonUtility.FromJson<Rows>(File.ReadAllText(Path.Combine(dir, "houses.json")));
            Release();
            var (mat, grey) = Fill(new List<Row>(all.houses), Path.Combine(repo, all.pack), all.paint);
            return (mat, grey, all.date);
        }

        internal static void Release()
        {
            buffer?.Release();
            buffer = null;
        }

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
            var src = pine.source;
            var wt = pine.weathering;
            var boarding = JsonUtility.FromJson<Timber>(File.ReadAllText(Path.Combine(pack, "timber.json"))).boarding;
            var stock = (Stock)typeof(Stocks).GetField(boarding.stock).GetValue(pine.stocks);
            var sawing = (Sawing)typeof(Sawings).GetField(boarding.sawing).GetValue(pine.sawings);
            mat.SetVector("_WoodHeart", With(Linear(src.srgbHeart), src.heartShare[1]));
            mat.SetVector("_WoodBrown", With(Linear(wt.srgbBrowned), wt.brownHalfYears));
            mat.SetVector("_WoodSilver", With(Linear(wt.srgbSilver), wt.silverYears[0]));
            mat.SetVector("_WoodDamp", With(Linear(wt.srgbDamp), wt.dampMost));
            mat.SetVector("_WoodKnot", With(Linear(src.srgbKnot), src.knotsPerM));
            mat.SetVector("_WoodA", new Vector4(src.heartShare[0], wt.silverYears[1], wt.dampReachM, wt.dampYears));
            mat.SetVector("_WoodB", new Vector4(src.ringsPerM[0], src.ringsPerM[1], src.latewood, wt.grainOld));
            mat.SetVector("_WoodC", new Vector4(wt.grainYears, wt.streaks[0], wt.streaks[1], wt.checksPerBoard));
            mat.SetVector("_WoodD", new Vector4(wt.checkYears, wt.cupping, src.knotMm[0] * 0.001f, src.knotMm[1] * 0.001f));
            mat.SetVector("_WoodE", new Vector4(wt.greySpread[0], wt.greySpread[1], wt.shelterReachM, src.knotGrey));
            mat.SetVector("_WoodStock", new Vector4(stock.priorYears[0], stock.priorYears[1], stock.valueSpread, stock.filmShare));
            mat.SetVector("_WoodFilm", With(Linear(stock.srgbFilm), stock.filmCover));
            mat.SetVector("_WoodSaw", new Vector4(sawing.fibre, sawing.edgeMm * 0.001f, pine.sawings.planed.fibre, pine.sawings.planed.edgeMm * 0.001f));
            var rust = pine.nailRust;
            mat.SetVector("_Rust", With(Linear(rust.srgb), rust.most));
            mat.SetVector("_RustIron", With(Linear(rust.srgbIron), rust.haloMm * 0.001f));
            mat.SetVector("_RustB", new Vector4(rust.mPerYear, rust.mostM, rust.widthMm[0] * 0.001f, rust.widthMm[1] * 0.001f));
            mat.SetVector("_NailsAt", new Vector4(boarding.nails.fromEndMm[0] * 0.001f, boarding.nails.fromEndMm[1] * 0.001f, boarding.nails.acrossMm * 0.001f, 0f));
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
            mat.SetVector("_WeatherB", new Vector4(w.boardSpread, w.patchSpread, w.patchM, 0f));
            mat.SetVector("_WeatherD", new Vector4(w.gatherFactor, w.gatherM, 0f, 0f));
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
