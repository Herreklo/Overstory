using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEditor.Rendering;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using Overstory.Corner;
using Overstory.Play;
using Debug = UnityEngine.Debug;
using Object = UnityEngine.Object;

namespace Overstory.EditorTools.Corner
{
    /// <summary>
    /// The painted corner as a scene Øystein can open, and a small Mac app of it with the walk's free camera
    /// (tools/painted_corner.py runs these under the Unity lock):
    ///
    ///     Scene   LT1ArtPasses.Compose (the greybox, the houses, the lamps, the elements), saved as
    ///             Experiments/LT1/Corner/LT1_PaintedCorner.unity: its renderers with their own materials, the page's
    ///             values on PaintedCornerLook (set again at runtime, the air enqueued per camera), the free camera
    ///             (Walker, CornerFly, FrameTimeOverlay); its generated meshes and materials in Corner/Generated/, with
    ///             greybox.txt (what an element can hide). Then Check and Still.
    ///     Check   the saved scene opened: every renderer has its mesh and materials, the look its values and air.
    ///     Still   the saved scene's camera drawn as the app draws it (1x, MSAA 4x, the runtime air) to
    ///             reviews/lt1/art-direction/engine/corner-scene.png (and -grey), to set beside the frame.
    ///     Build   Scene, then unity/Builds/PaintedCorner/PaintedCorner.app from it (LT1Perf.BuildPlayer: full screen
    ///             at 2560 by 1440), with the BatchRendererGroup's shader variants kept for the build only.
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.Corner.LT1PaintedCorner.Build
    ///         [-elements none|name,...] [-noscene]
    /// </summary>
    public static class LT1PaintedCorner
    {
        public const string Folder = CornerBuild.Folder;
        public const string Generated = Folder + "/Generated";
        public const string ScenePath = Folder + "/LT1_PaintedCorner.unity";
        public const string App = "Builds/PaintedCorner/PaintedCorner.app";
        const string StillOut = "reviews/lt1/art-direction/engine/corner-scene";

        public static void Scene()
        {
            var clock = Stopwatch.StartNew();
            if (AssetDatabase.IsValidFolder(Generated))
                AssetDatabase.DeleteAsset(Generated);
            AssetDatabase.DeleteAsset(ScenePath);
            AssetDatabase.CreateFolder(Folder, "Generated");
            var C = LT1ArtPasses.Compose(Cli.Arg("-data", LT1ArtPasses.PaintJson), true);
            try
            {
                // the heart and the shared settings as they were before anything is saved
                C.RestoreSettings();
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Additive);
                var was = SceneManager.GetActiveScene();
                SceneManager.SetActiveScene(scene);
                RenderSettings.skybox = null;
                RenderSettings.fog = false;
                RenderSettings.ambientMode = AmbientMode.Flat;
                RenderSettings.ambientLight = Color.black;
                SceneManager.SetActiveScene(was);
                SceneManager.MoveGameObjectToScene(C.Root, scene);
                var root = C.Root;

                // the look: the page's values, set again at runtime, and the air
                var G = C.Build.Globals;
                var look = root.AddComponent<PaintedCornerLook>();
                look.floats = G.Floats.Select(kv => new PaintedCornerLook.FloatGlobal { name = kv.Key, value = kv.Value }).ToList();
                look.vectors = G.Vectors.Select(kv => new PaintedCornerLook.VectorGlobal { name = kv.Key, value = kv.Value }).ToList();
                look.arrays = G.Arrays.Select(kv => new PaintedCornerLook.ArrayGlobal { name = kv.Key, values = kv.Value }).ToList();
                look.textures = G.Textures.Select(kv => new PaintedCornerLook.TextureGlobal { name = kv.Key, value = kv.Value }).ToList();
                look.air = new Material(Shader.Find("Hidden/Overstory/PaintAir")) { name = "PaintAir" };
                C.Build.Made.Add(look.air);
                look.rendererData = C.RendererData;
                look.shadowDistance = C.ShadowM;
                C.Camera.gameObject.AddComponent<AudioListener>();

                // the walk's free camera, from the street stop
                var fly = new GameObject("Free camera");
                SceneManager.MoveGameObjectToScene(fly, scene);
                var walker = fly.AddComponent<Walker>();
                walker.view = C.Camera;
                walker.lens = C.Camera.fieldOfView;
                var cf = fly.AddComponent<CornerFly>();
                cf.walker = walker;
                cf.view = C.Camera;
                fly.AddComponent<FrameTimeOverlay>();

                int saved = Persist(scene, C.Build, look);
                WriteGreybox(C.Build);
                if (!EditorSceneManager.SaveScene(scene, ScenePath))
                    throw new System.Exception($"[LT1PaintedCorner] could not save {ScenePath}");
                int renderers = root.GetComponentsInChildren<Renderer>(true).Length;
                EditorSceneManager.CloseScene(scene, true);
                Debug.Log($"[LT1PaintedCorner] saved {ScenePath}: {renderers} renderers, {saved} generated assets in {Generated}, " +
                          $"elements {(C.Build.Ran.Count > 0 ? string.Join(", ", C.Build.Ran) : "none")}, {clock.Elapsed.TotalSeconds:F0} s");
            }
            finally
            {
                C.Cleanup();
            }
            Check();
            Still();
        }

        /// <summary>Everything the scene draws that was made in memory saved as an asset in Generated/, so the scene
        /// holds it by reference: meshes, materials (and their textures), what the elements kept, the globals' textures.</summary>
        static int Persist(Scene scene, CornerBuild build, PaintedCornerLook look)
        {
            var saved = new HashSet<Object>();
            int n = 0;
            void Save(Object o)
            {
                if (o == null || EditorUtility.IsPersistent(o) || !saved.Add(o))
                    return;
                if (o is RenderTexture)
                {
                    Debug.LogWarning($"[LT1PaintedCorner] {o.name} is a RenderTexture: not saved");
                    return;
                }
                if (o is Material mat)
                    foreach (int id in mat.GetTexturePropertyNameIDs())
                        Save(mat.GetTexture(id));
                o.hideFlags = HideFlags.None;
                var safe = new StringBuilder();
                foreach (char ch in string.IsNullOrEmpty(o.name) ? o.GetType().Name : o.name)
                    safe.Append(char.IsLetterOrDigit(ch) || ch == ' ' || ch == '-' || ch == '_' || ch == '.' ? ch : '-');
                AssetDatabase.CreateAsset(o, $"{Generated}/{n++:D4} {safe}{(o is Material ? ".mat" : ".asset")}");
            }
            foreach (var go in scene.GetRootGameObjects())
            {
                foreach (var mf in go.GetComponentsInChildren<MeshFilter>(true))
                    Save(mf.sharedMesh);
                foreach (var mc in go.GetComponentsInChildren<MeshCollider>(true))
                    Save(mc.sharedMesh);
                foreach (var r in go.GetComponentsInChildren<Renderer>(true))
                    foreach (var m in r.sharedMaterials)
                        Save(m);
            }
            foreach (var o in build.Kept)
                Save(o);
            foreach (var t in look.textures)
                Save(t.value);
            Save(look.air);
            return n;
        }

        /// <summary>Generated/greybox.txt: each renderer the corner draws before its elements, what an element may hide.</summary>
        static void WriteGreybox(CornerBuild build)
        {
            var sb = new StringBuilder();
            sb.AppendLine("# What the painted corner draws before its elements (LT1PaintedCorner, rebuilt each time). An element hides");
            sb.AppendLine("# them by name or path prefix (corner.Hide), by class (corner.HideClass) or a street box of a class (corner.HideBox).");
            sb.AppendLine("# class: 1 clay, 2 a house, 3 laid stone, 4 a tree, 6 anything else, 7 a lantern's glass, 8 its metal");
            sb.AppendLine("# class\tname\tpath\tstreet min (x y z)\tstreet max\thidden by");
            foreach (var p in build.Greybox.OrderBy(p => p.Class).ThenBy(p => p.Path, System.StringComparer.Ordinal))
            {
                var b = p.Hidden ? default : p.Street;
                sb.AppendLine($"{p.Class}\t{p.Name}\t{p.Path}\t{(p.Hidden ? "-" : $"{b.min.x:F1} {b.min.y:F1} {b.min.z:F1}")}\t" +
                              $"{(p.Hidden ? "-" : $"{b.max.x:F1} {b.max.y:F1} {b.max.z:F1}")}\t{(p.Hidden ? "an element" : "")}");
            }
            File.WriteAllText(Path.Combine(Application.dataPath, "..", Generated, "greybox.txt"), sb.ToString());
        }

        /// <summary>The saved scene opened and checked; throws on any miss, so a batch run exits with an error.</summary>
        public static void Check()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var problems = new List<string>();
            var look = Object.FindAnyObjectByType<PaintedCornerLook>();
            if (look == null)
                problems.Add("no PaintedCornerLook");
            else
            {
                if (look.air == null || look.air.shader == null || look.air.shader.name != "Hidden/Overstory/PaintAir")
                    problems.Add("the look has no air material");
                if (look.rendererData == null)
                    problems.Add("the look has no renderer data");
                if (look.arrays.Count == 0 || look.vectors.Count == 0)
                    problems.Add("the look has no values");
            }
            var cams = Object.FindObjectsByType<Camera>(FindObjectsSortMode.None);
            if (cams.Length != 1)
                problems.Add($"{cams.Length} cameras");
            int renderers = 0, own = 0;
            foreach (var r in Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None))
            {
                renderers++;
                var mf = r.GetComponent<MeshFilter>();
                if (r is MeshRenderer && (mf == null || mf.sharedMesh == null))
                    problems.Add($"{r.name}: no mesh");
                foreach (var m in r.sharedMaterials)
                    if (m == null || m.shader == null)
                        problems.Add($"{r.name}: a missing material");
                    else if (m.shader.name != "Hidden/Overstory/PaintSurface")
                        own++;
            }
            int lights = Object.FindObjectsByType<Light>(FindObjectsSortMode.None).Length;
            if (Object.FindAnyObjectByType<Walker>() == null || Object.FindAnyObjectByType<CornerFly>() == null)
                problems.Add("no free camera");
            Debug.Log($"[LT1PaintedCorner] check {ScenePath}: {renderers} renderers ({own} materials with their own shader), " +
                      $"{lights} lights, {look?.floats.Count} floats, {look?.vectors.Count} vectors, {look?.arrays.Count} arrays, " +
                      $"{look?.textures.Count} textures; {(problems.Count == 0 ? "ok" : string.Join("; ", problems.Take(20)))}");
            if (problems.Count > 0)
                throw new System.Exception($"[LT1PaintedCorner] the scene failed its check: {problems.Count} problems");
        }

        /// <summary>The saved scene's camera drawn as the app draws it (1x, MSAA 4x, the air at runtime).</summary>
        public static void Still()
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            var cam = Object.FindAnyObjectByType<Camera>() ?? throw new System.Exception("[LT1PaintedCorner] no camera");
            int W = int.Parse(Cli.Arg("-width", "2560")), H = int.Parse(Cli.Arg("-height", "1440"));
            string outBase = Path.Combine(Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..")), Cli.Arg("-still", StillOut));
            bool async = ShaderUtil.allowAsyncCompilation;
            ShaderUtil.allowAsyncCompilation = false;
            var rt = new RenderTexture(W, H, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB) { antiAliasing = 4 };
            rt.Create();
            Texture2D tex = null, grey = null;
            try
            {
                for (int i = 0; i < 2; i++)
                    LT1Render.Render(cam, rt);
                cam.targetTexture = null;
                var prev = RenderTexture.active;
                RenderTexture.active = rt;
                tex = new Texture2D(W, H, TextureFormat.RGB24, false, false);
                tex.ReadPixels(new Rect(0, 0, W, H), 0, 0);
                tex.Apply();
                RenderTexture.active = prev;
                Directory.CreateDirectory(Path.GetDirectoryName(outBase));
                File.WriteAllBytes(outBase + ".png", tex.EncodeToPNG());
                grey = LT1ArtPasses.GreyOf(tex, 1);
                File.WriteAllBytes(outBase + "-grey.png", grey.EncodeToPNG());
                Debug.Log($"[LT1PaintedCorner] still {outBase}.png ({W}x{H}, the saved scene's camera at {cam.transform.position})");
            }
            finally
            {
                ShaderUtil.allowAsyncCompilation = async;
                cam.targetTexture = null;
                rt.Release();
                Object.DestroyImmediate(rt);
                if (tex != null)
                    Object.DestroyImmediate(tex);
                if (grey != null)
                    Object.DestroyImmediate(grey);
            }
        }

        /// <summary>Scene (unless -noscene), then the app from it.</summary>
        public static void Build()
        {
            var clock = Stopwatch.StartNew();
            if (!Cli.Flag("-noscene"))
                Scene();
            double sceneT = clock.Elapsed.TotalSeconds;
            string app = Path.GetFullPath(Path.Combine(Application.dataPath, "..", App));
            // growth draws through a BatchRendererGroup: its shader variants kept for this build only (the setting put
            // back after, in memory: tools/painted_corner.py puts the file back too if Unity wrote it)
            var settings = new SerializedObject(GraphicsSettings.GetGraphicsSettings());
            var brg = settings.FindProperty("m_BrgStripping") ?? throw new System.Exception("[LT1PaintedCorner] no m_BrgStripping");
            int was = brg.intValue;
            try
            {
                brg.intValue = (int)BatchRendererGroupStrippingMode.KeepAll;
                settings.ApplyModifiedPropertiesWithoutUndo();
                Debug.Log($"[LT1PaintedCorner] BatchRendererGroup variants for the build: {EditorGraphicsSettings.batchRendererGroupShaderStrippingMode} (was {(BatchRendererGroupStrippingMode)was})");
                if (!LT1Perf.BuildPlayer(app, ScenePath))
                    throw new System.Exception("[LT1PaintedCorner] the app did not build");
            }
            finally
            {
                settings.Update();
                brg.intValue = was;
                settings.ApplyModifiedPropertiesWithoutUndo();
            }
            Debug.Log($"[LT1PaintedCorner] built {app}: scene {sceneT:F0} s, build {clock.Elapsed.TotalSeconds - sceneT:F0} s");
        }
    }
}
