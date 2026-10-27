using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

namespace Overstory.EditorTools.Corner
{
    /// <summary>
    /// One element of the painted corner (the houses, the trees, the growth, the rock and ground...): a static method
    /// that adds its own renderers to the corner. LT1ArtPasses.Paint (the frame's still) and LT1PaintedCorner (the scene
    /// and the app) call every method marked with it, after the greybox, the houses and the lamps are composed and
    /// before anything is drawn, in Order, then by name:
    ///
    ///     [CornerElement("trees")]
    ///     static void Trees(CornerContext corner) { ... }
    ///
    /// An element's code is its own file in Code/Editor/Corner/, its data its own folder,
    /// Experiments/LT1/Corner/Elements/{name}/ (corner.Data, corner.DataPath). It parents what it makes under
    /// corner.Root, draws it with corner.Surface (the painted surface with its own values from its own data, class 10),
    /// corner.ClassMaterial (the page's own class, e.g. 3 laid stone) or a shader of its own that answers _P_Mode as
    /// PaintSurface does (1: distance from the eye, 1, the veil share, 1), and hides the greybox it replaces with
    /// Hide, HideClass or HideBox. It never edits Paint.json, LT1ArtPasses.cs or the art-direction shaders. A throw in
    /// one element is logged as an error and drops that element (its root and its hides); the others still run.
    /// -elements a,b (prefixes) runs only those; -elements none runs none.
    /// </summary>
    [AttributeUsage(AttributeTargets.Method, AllowMultiple = false)]
    public sealed class CornerElementAttribute : Attribute
    {
        /// <summary>The element's name: its root's name, its data folder's (Elements/{Name}) and the -elements filter's.</summary>
        public string Name { get; }
        /// <summary>Lower runs first (default 0): an element that reads another's renderers runs after it.</summary>
        public int Order { get; set; }

        public CornerElementAttribute(string name) => Name = name;
    }

    /// <summary>An element's own painted surface (PaintSurface.shader, class 10), from its own data file, in the page's
    /// terms (reviews/lt1/art-direction/README.md): its value, how wet, calm and glossy it is, what light and fog it
    /// takes.</summary>
    [Serializable]
    public class CornerSurface
    {
        /// <summary>Its value (sRGB hex), as the page's swatches.</summary>
        public string srgb = "#808080";
        /// <summary>The share of the wet film it carries (the film itself lies only on faces near level).</summary>
        public float wet;
        /// <summary>0 the sky's light by the face's normal; 1 one value over the whole mass (its facets lost).</summary>
        public float calm;
        /// <summary>How much it mirrors the sky (glass 1).</summary>
        public float gloss;
        /// <summary>How much of the lamps' light it takes (1 whole).</summary>
        public float lamp = 1f;
        /// <summary>The share of the fog's veil it takes past the near layer (1 by its distance; 0 stays in the near layer).</summary>
        public float veil = 1f;
        /// <summary>True when the mesh carries its sky bake in UV3.x (as the stone does); else it takes the open sky.</summary>
        public bool skyBake;
    }

    /// <summary>One of the corner's lamps (Paint.json, lamps): its place (Unity world), its light and its Light.</summary>
    public sealed class CornerLamp
    {
        public string Id { get; internal set; }
        public Vector3 Head { get; internal set; }
        public Vector3 Foot { get; internal set; }
        /// <summary>Its light's colour (linear).</summary>
        public Color Colour { get; internal set; }
        public float Power { get; internal set; }
        public Light Light { get; internal set; }
    }

    /// <summary>One renderer of what the corner draws before its elements (the greybox): the stage's meshes, the
    /// houses and the lamps, each under the corner's root.</summary>
    public sealed class CornerPiece
    {
        /// <summary>The name of the stage's object it was copied from (e.g. "buildings_3"), or "house C", "lamp landing glass".</summary>
        public string Name { get; internal set; }
        /// <summary>Its path in the heart's scene (or in the corner, for the houses and lamps).</summary>
        public string Path { get; internal set; }
        /// <summary>What it is: 1 clay, 2 a house, 3 laid stone, 4 a tree, 6 anything else, 7 a lantern's glass, 8 its metal.</summary>
        public int Class { get; internal set; }
        public MeshRenderer Renderer { get; internal set; }
        /// <summary>Its bounds in street metres (x east, y north, z up).</summary>
        public Bounds Street => Renderer != null ? CornerContext.StreetBounds(Renderer.bounds) : default;
        public bool Hidden { get; internal set; }
    }

    /// <summary>What an element gets from the corner, and its one way to change it.</summary>
    public sealed class CornerContext
    {
        readonly CornerBuild build;
        internal readonly List<string> hideNames = new();
        internal readonly List<int> hideClasses = new();
        internal readonly List<(Vector3 min, Vector3 max, int cls)> hideBoxes = new();
        readonly Dictionary<string, Material> surfaces = new();

        internal CornerContext(CornerBuild build, string element, GameObject root)
        {
            this.build = build;
            Element = element;
            Root = root;
        }

        /// <summary>The element's name.</summary>
        public string Element { get; }
        /// <summary>The element's own root (under the corner's "Elements"): everything under it is drawn, and saved in the scene.</summary>
        public GameObject Root { get; }
        /// <summary>True while building the saved scene and the app; false for the frame's still.</summary>
        public bool ForScene => build.ForScene;
        /// <summary>The hour (Paint.json, moment), e.g. "1750-sea-fog".</summary>
        public string Moment => build.Moment;
        /// <summary>The view (Paint.json, view), e.g. "street".</summary>
        public string View => build.View;
        /// <summary>The town's date (cache/houses/houses.json), e.g. 1989.</summary>
        public float Date => build.Date;
        /// <summary>The street stop's camera. Read it; never move it.</summary>
        public Camera Camera => build.Camera;
        public IReadOnlyList<CornerLamp> Lamps => build.Lamps;
        /// <summary>What the corner draws before the elements (names and classes: Experiments/LT1/Corner/Generated/greybox.txt).</summary>
        public IReadOnlyList<CornerPiece> Greybox => build.Greybox;

        /// <summary>The element's data folder (an asset path): Assets/Experiments/LT1/Corner/Elements/{name}.</summary>
        public string DataFolder => CornerBuild.ElementsFolder + "/" + Element;
        /// <summary>A file in the element's data folder (a full path).</summary>
        public string DataPath(string file) => Path.GetFullPath(Path.Combine(Application.dataPath, "..", DataFolder, file));
        /// <summary>A JSON file in the element's data folder, read with JsonUtility.</summary>
        public T Data<T>(string file) => JsonUtility.FromJson<T>(File.ReadAllText(DataPath(file)));

        /// <summary>A value the page set (Paint.json, globals, e.g. "_P_Focus"), or zero.</summary>
        public Vector4 Global(string name) => build.Globals.Vectors.TryGetValue(name, out var v) ? v
            : build.Globals.Floats.TryGetValue(name, out var f) ? new Vector4(f, 0f, 0f, 0f) : Vector4.zero;

        /// <summary>Street metres (x east, y north, z up) to Unity's world (x, z, y).</summary>
        public static Vector3 World(Vector3 street) => new Vector3(street.x, street.z, street.y);
        public static Vector3 World(float x, float y, float z) => new Vector3(x, z, y);
        /// <summary>Unity's world to street metres.</summary>
        public static Vector3 Street(Vector3 world) => new Vector3(world.x, world.z, world.y);
        public static Bounds StreetBounds(Bounds world) => new Bounds(Street(world.center), Street(world.size));

        /// <summary>The painted surface with the element's own values (class 10), one material per distinct surface.</summary>
        public Material Surface(CornerSurface s, string name = null)
        {
            string key = JsonUtility.ToJson(s);
            if (surfaces.TryGetValue(key, out var m))
                return m;
            if (!ColorUtility.TryParseHtmlString(s.srgb.StartsWith("#") ? s.srgb : "#" + s.srgb, out var c))
                throw new FormatException($"[{Element}] not a colour: {s.srgb}");
            var lin = c.linear;
            m = new Material(Shader.Find("Hidden/Overstory/PaintSurface")) { name = $"{Element} {name ?? "surface " + surfaces.Count}" };
            m.SetFloat("_Class", 10f);
            m.SetVector("_OwnAlbedo", new Vector4(lin.r, lin.g, lin.b, s.wet));
            m.SetVector("_OwnB", new Vector4(s.calm, s.gloss, 0f, s.lamp));
            m.SetVector("_OwnC", new Vector4(s.veil, s.skyBake ? 1f : 0f, 0f, 0f));
            build.Made.Add(m);
            surfaces[key] = m;
            return m;
        }

        /// <summary>The page's own surface for a class (1 clay, 2 a house, 3 laid stone, 4 a tree, 6 anything else): what
        /// the greybox of that class is drawn with, its values from Paint.json.</summary>
        public Material ClassMaterial(int cls) => build.ClassMaterial(cls, 0f, 0f);

        /// <summary>Hides every greybox renderer whose name, or path, starts with this (e.g. "house " the cached houses).</summary>
        public void Hide(string name) => hideNames.Add(name);
        /// <summary>Hides every greybox renderer of a class (e.g. 4 the trees).</summary>
        public void HideClass(int cls) => hideClasses.Add(cls);
        /// <summary>Hides what a class draws inside a street box (min and max, street metres), cut in the shader: the
        /// part of a greybox mesh an element replaces (at most 16 boxes in all, the page's own among them).</summary>
        public void HideBox(Vector3 streetMin, Vector3 streetMax, int cls) => hideBoxes.Add((streetMin, streetMax, cls));

        /// <summary>A generated asset (a mesh, material or texture made in memory): saved with the scene, destroyed after
        /// the still. Meshes and materials on renderers under Root are kept without it.</summary>
        public T Keep<T>(T asset) where T : Object
        {
            build.Made.Add(asset);
            build.Kept.Add(asset);
            return asset;
        }

        /// <summary>A global the element's shaders read: set now, and again by the scene's look at runtime.</summary>
        public void SetGlobal(string name, float value) => build.Globals.Float(name, value);
        public void SetGlobal(string name, Vector4 value) => build.Globals.Vector(name, value);
        public void SetGlobal(string name, Vector4[] values) => build.Globals.Array(name, values);
        public void SetGlobal(string name, Texture value) => build.Globals.Texture(name, value);

        /// <summary>A renderer under Root (or under parent): a mesh with one material, casting shadows unless asked not to.</summary>
        public MeshRenderer Add(string name, Mesh mesh, Material material, Transform parent = null, ShadowCastingMode shadows = ShadowCastingMode.On)
        {
            var g = new GameObject(name);
            g.transform.SetParent(parent != null ? parent : Root.transform, false);
            g.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = g.AddComponent<MeshRenderer>();
            var mats = new Material[Mathf.Max(1, mesh != null ? mesh.subMeshCount : 1)];
            for (int i = 0; i < mats.Length; i++)
                mats[i] = material;
            mr.sharedMaterials = mats;
            mr.shadowCastingMode = shadows;
            mr.lightProbeUsage = LightProbeUsage.Off;
            mr.reflectionProbeUsage = ReflectionProbeUsage.Off;
            return mr;
        }
    }

    /// <summary>The globals the corner sets, kept so the scene's look sets them again at runtime (PaintedCornerLook).</summary>
    internal sealed class CornerGlobals
    {
        public readonly Dictionary<string, float> Floats = new();
        public readonly Dictionary<string, Vector4> Vectors = new();
        public readonly Dictionary<string, Vector4[]> Arrays = new();
        public readonly Dictionary<string, Texture> Textures = new();

        public void Float(string name, float v) { Floats[name] = v; Shader.SetGlobalFloat(name, v); }
        public void Vector(string name, Vector4 v) { Vectors[name] = v; Shader.SetGlobalVector(name, v); }
        public void Array(string name, Vector4[] v) { Arrays[name] = (Vector4[])v.Clone(); Shader.SetGlobalVectorArray(name, v); }
        public void Texture(string name, Texture t) { Textures[name] = t; Shader.SetGlobalTexture(name, t); }
    }

    /// <summary>What the corner shares with its elements while it is composed (LT1ArtPasses.Compose).</summary>
    internal sealed class CornerBuild
    {
        public const string Folder = "Assets/Experiments/LT1/Corner";
        public const string ElementsFolder = Folder + "/Elements";

        public bool ForScene;
        public string Moment, View;
        public float Date;
        public Camera Camera;
        public GameObject Elements;
        public readonly List<CornerLamp> Lamps = new();
        public readonly List<CornerPiece> Greybox = new();
        public readonly CornerGlobals Globals = new();
        /// <summary>Everything made in memory: destroyed after the still; saved with the scene when referenced or kept.</summary>
        public readonly List<Object> Made = new();
        public readonly List<Object> Kept = new();
        public readonly List<(Vector3 min, Vector3 max, int cls)> HideBoxes = new();
        public readonly List<string> Ran = new();
        /// <summary>The page's material for a class, a lantern's head's whiteness and a designed shape's slot.</summary>
        public Func<float, float, float, Material> ClassMaterial;
    }

    /// <summary>Runs the corner's elements ([CornerElement]) and applies what they hide.</summary>
    internal static class CornerElements
    {
        public static void Run(CornerBuild build)
        {
            var found = TypeCache.GetMethodsWithAttribute<CornerElementAttribute>()
                .Select(m => (method: m, a: m.GetCustomAttribute<CornerElementAttribute>()))
                .OrderBy(x => x.a.Order).ThenBy(x => x.a.Name, StringComparer.Ordinal).ToList();
            var contexts = new List<CornerContext>();
            foreach (var (method, a) in found)
            {
                string where = $"{method.DeclaringType?.FullName}.{method.Name}";
                if (!Cli.Wanted("-elements", a.Name))
                {
                    Debug.Log($"[Corner] element {a.Name} ({where}) not run (-elements)");
                    continue;
                }
                var ps = method.GetParameters();
                if (!method.IsStatic || ps.Length != 1 || ps[0].ParameterType != typeof(CornerContext))
                {
                    Debug.LogError($"[Corner] element {a.Name} ({where}) must be static void (CornerContext corner)");
                    continue;
                }
                if (build.Ran.Contains(a.Name))
                {
                    Debug.LogError($"[Corner] element {a.Name} ({where}): the name is taken");
                    continue;
                }
                var root = new GameObject(a.Name);
                root.transform.SetParent(build.Elements.transform, false);
                var ctx = new CornerContext(build, a.Name, root);
                var clock = System.Diagnostics.Stopwatch.StartNew();
                try
                {
                    method.Invoke(null, new object[] { ctx });
                    contexts.Add(ctx);
                    build.Ran.Add(a.Name);
                    Debug.Log($"[Corner] element {a.Name} ({where}): {root.GetComponentsInChildren<Renderer>(true).Length} renderers, " +
                              $"hides {ctx.hideNames.Count} names, {ctx.hideClasses.Count} classes, {ctx.hideBoxes.Count} boxes, {clock.Elapsed.TotalSeconds:F1} s");
                }
                catch (Exception e)
                {
                    var inner = e is TargetInvocationException t && t.InnerException != null ? t.InnerException : e;
                    Debug.LogError($"[Corner] element {a.Name} ({where}) failed and is left out: {inner}");
                    Object.DestroyImmediate(root);
                }
            }

            // what they replace: whole greybox renderers by name or class, parts of them by box (in the shader)
            foreach (var ctx in contexts)
            {
                foreach (var piece in build.Greybox)
                {
                    if (piece.Hidden)
                        continue;
                    bool hide = ctx.hideClasses.Contains(piece.Class)
                                || ctx.hideNames.Any(n => piece.Name.StartsWith(n, StringComparison.Ordinal) || piece.Path.StartsWith(n, StringComparison.Ordinal));
                    if (!hide)
                        continue;
                    piece.Hidden = true;
                    if (piece.Renderer != null)
                        Object.DestroyImmediate(piece.Renderer.gameObject);
                }
                build.HideBoxes.AddRange(ctx.hideBoxes);
            }
            int hidden = build.Greybox.Count(p => p.Hidden);
            Debug.Log($"[Corner] elements run: {(build.Ran.Count > 0 ? string.Join(", ", build.Ran) : "none")}; greybox hidden {hidden} of {build.Greybox.Count}, boxes {build.HideBoxes.Count}");
        }
    }
}
