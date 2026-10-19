using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Assembly;
using Overstory.Scenes;
using Overstory.World;

namespace Overstory.EditorTools
{
    /// <summary>
    /// Sets up the project and LT1's scene from the command line, so the setup is code, not clicks:
    ///
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Setup.Project
    ///     Unity -batchmode -quit -projectPath unity -executeMethod Overstory.EditorTools.LT1Setup.Scene
    ///
    /// Project comes first: it sets the scripting define that compiles URP's screen-space reflections,
    /// which Scene then adds to the renderer.
    /// </summary>
    public static class LT1Setup
    {
        const string RP = "Assets/Settings/PC_RPAsset.asset";
        const string Renderer = "Assets/Settings/PC_Renderer.asset";
        const string Street = "Assets/Art/Buildings/harbour-row/street.json";
        const string Palette = "Assets/Art/Palette";
        const string Materials = "Assets/Art/Materials";
        const string LT1 = "Assets/Experiments/LT1";
        const string ScenePath = LT1 + "/LT1.unity";
        const string SSRDefine = "URP_SCREEN_SPACE_REFLECTION";

        // -- step 1: the project ---------------------------------------------------------------------------------

        public static void Project()
        {
            PlayerSettings.productName = "Overstory";
            PlayerSettings.companyName = "Overstory";
            PlayerSettings.colorSpace = ColorSpace.Linear;
            var target = NamedBuildTarget.Standalone;
            var defines = new List<string>(PlayerSettings.GetScriptingDefineSymbols(target).Split(';'));
            if (!defines.Contains(SSRDefine))
            {
                defines.Add(SSRDefine);
                PlayerSettings.SetScriptingDefineSymbols(target, string.Join(";", defines.FindAll(d => d.Length > 0)));
            }

            // the pipeline: sharp, well-shadowed stills of a street seen from up to ~200 m
            var rp = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(RP);
            var so = new SerializedObject(rp);
            Set(so, "m_MSAA", 4);
            Set(so, "m_SupportsHDR", true);
            Set(so, "m_ColorGradingMode", 1); // HDR grading
            Set(so, "m_ShadowDistance", 200f);
            Set(so, "m_ShadowCascadeCount", 4);
            SetVector3(so, "m_Cascade4Split", new Vector3(0.05f, 0.15f, 0.4f));
            Set(so, "m_MainLightShadowmapResolution", 4096);
            Set(so, "m_AdditionalLightsShadowmapResolution", 4096);
            Set(so, "m_SoftShadowsSupported", true);
            Set(so, "m_SoftShadowQuality", 3);
            Set(so, "m_RequireDepthTexture", true);
            Set(so, "m_RequireOpaqueTexture", true);
            so.ApplyModifiedPropertiesWithoutUndo();
            EditorUtility.SetDirty(rp);

            // work at the PC quality level, whose pipeline this is
            QualitySettings.SetQualityLevel(System.Array.IndexOf(QualitySettings.names, "PC"), true);
            AssetDatabase.SaveAssets();
            Debug.Log("[LT1Setup] project set up");
        }

        // -- step 2: renderer, materials, light, cameras, scene ----------------------------------------------------

        public static void Scene()
        {
            SetRenderer();
            Directory.CreateDirectory(Materials);
            Directory.CreateDirectory(LT1 + "/Light");
            Directory.CreateDirectory(LT1 + "/Views");
            AssetDatabase.Refresh();

            var street = MaterialAt(Materials + "/M_Street.mat", "Overstory/Street", m => m.DisableKeyword("_OS_WATER"));
            var water = MaterialAt(Materials + "/M_Water.mat", "Overstory/Street", m =>
            {
                m.SetFloat("_Water", 1f);
                m.SetFloat("_WaveScale", 0.35f);
                m.SetFloat("_WaveStrength", 0.16f);
                m.EnableKeyword("_OS_WATER");
            });
            var sky = MaterialAt(Materials + "/M_Sky.mat", "Overstory/Sky", m => { });

            var drizzle = Asset<LightRig>(LT1 + "/Light/LT1_Drizzle.asset", Drizzle);
            var streetShot = Asset<CameraShot>(LT1 + "/Views/LT1_StreetLevel.asset", s =>
            {
                // standing on the quay at the west end, eye height, looking along the row towards the warehouses
                s.position = new Vector3(-7f, -8.6f, 1.65f);
                s.target = new Vector3(40f, 0.5f, 3.4f);
                s.verticalFov = 42f;
            });
            var neighbourhood = Asset<CameraShot>(LT1 + "/Views/LT1_Neighbourhood.asset", s =>
            {
                // raised over the harbour, three-quarters on: the whole row, its roofs and the quay
                s.position = new Vector3(50f, -68f, 60f);
                s.target = new Vector3(58f, 5f, 2f);
                s.verticalFov = 40f;
            });

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var camGo = new GameObject("Camera") { tag = "MainCamera" };
            var cam = camGo.AddComponent<Camera>();
            cam.allowHDR = true;
            cam.allowMSAA = true;
            cam.clearFlags = CameraClearFlags.Skybox;
            var camData = camGo.AddComponent<UniversalAdditionalCameraData>();
            camData.renderPostProcessing = true;
            camData.antialiasing = AntialiasingMode.None; // MSAA from the pipeline, and stills are supersampled
            camData.renderShadows = true;
            camData.dithering = true; // no banding in the soft gradients of grey skies and haze

            var sunGo = new GameObject("Sun");
            var sun = sunGo.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.shadows = LightShadows.Soft;

            var volGo = new GameObject("Grade");
            var volume = volGo.AddComponent<Volume>();
            volume.isGlobal = true;

            var streetGo = new GameObject("Harbour Row");
            var builder = streetGo.AddComponent<StreetBuilder>();
            builder.enabled = false; // filled in before it first builds
            builder.layout = AssetDatabase.LoadAssetAtPath<TextAsset>(Street);
            builder.streetMaterial = street;
            builder.waterMaterial = water;
            var layout = StreetLayout.Parse(builder.layout.text);
            var files = new List<string>();
            foreach (var b in layout.buildings) files.Add(b.file);
            foreach (var k in layout.kit) files.Add(k.file);
            foreach (var f in files)
            {
                var model = AssetDatabase.LoadAssetAtPath<GameObject>(f);
                if (model == null)
                    throw new FileNotFoundException($"the street needs {f}; run blender/tools/export_street.py first");
                builder.models.Add(new StreetBuilder.ModelRef { file = f, model = model });
            }

            var stageGo = new GameObject("Stage");
            var stage = stageGo.AddComponent<StreetStage>();
            stage.enabled = false;
            stage.street = builder;
            stage.sun = sun;
            stage.view = cam;
            stage.volume = volume;
            stage.sky = sky;
            stage.paletteAlbedo = AssetDatabase.LoadAssetAtPath<Texture2D>(Palette + "/palette_albedo.png");
            stage.paletteEmit = AssetDatabase.LoadAssetAtPath<Texture2D>(Palette + "/palette_emit.png");
            stage.paletteGlow = AssetDatabase.LoadAssetAtPath<Texture2D>(Palette + "/palette_glow.png");
            stage.paletteSurface = AssetDatabase.LoadAssetAtPath<Texture2D>(Palette + "/palette_surface.png");
            stage.rig = drizzle;
            stage.shot = streetShot;
            builder.enabled = true;
            stage.enabled = true;

            EditorSceneManager.SaveScene(scene, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            AssetDatabase.SaveAssets();
            Debug.Log($"[LT1Setup] scene saved: {ScenePath} ({layout.buildings.Length} buildings, {layout.lamps.Length} lamps)");
        }

        /// <summary>Grey drizzle with wet ground: the default light and the hardest test.</summary>
        static void Drizzle(LightRig r)
        {
            // an October afternoon under low cloud: the sky is the key light, the sun only a direction
            r.sunBearing = 110f;
            r.sunElevation = 22f;
            r.sunColour = new Color(0.87f, 0.9f, 0.97f);
            r.sunIntensity = 0.35f;
            r.shadowStrength = 0.45f;

            r.zenith = C(150, 158, 167);
            r.horizon = C(188, 192, 196);
            r.belowHorizon = C(96, 100, 100);
            r.skyCurve = 0.5f;
            r.sunGlow = Color.black;

            // overcast: the dome overhead is the light; a wall sees half of it, and the wet street little back
            r.ambientSky = C(194, 201, 210);
            r.ambientEquator = C(134, 139, 145);
            r.ambientGround = C(72, 74, 72);
            r.ambientIntensity = 1f;

            // the air is a shade darker than the sky behind it, so distance lays things in soft grey
            // layers against a lighter sky instead of washing them out; drizzle haze hugs the ground
            r.fogColour = C(152, 157, 162);
            r.fogDensity = 0.0036f;
            r.fogHeightFalloff = 0.065f;
            r.fogBaseHeight = 0f;
            r.fogMaxOpacity = 0.85f;
            r.fogSunColour = Color.black;

            r.wetness = 1f;
            r.windowGlow = 0f;
            r.lampsOn = false;
            r.lampGlow = 0f;
            r.lampIntensity = 0f;

            // exposed for the white walls: white stays white, the sky brighter still, the wet street well below
            r.postExposure = 1.5f;
            r.contrast = 22f;
            r.saturation = -12f;
            r.temperature = -4f;
            r.tint = 0f;
            r.colourFilter = Color.white;
            r.bloomIntensity = 0f;
            r.bloomThreshold = 1.1f;
            r.reflectionStrength = 1f;
            r.clock = 0f;
        }

        static Color C(int r, int g, int b) => new Color(r / 255f, g / 255f, b / 255f);

        // -- the renderer: stronger ambient occlusion for overcast light, and screen-space reflections -------------

        static void SetRenderer()
        {
            var data = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(Renderer);
            foreach (var f in data.rendererFeatures)
            {
                if (f == null || f.GetType().Name != "ScreenSpaceAmbientOcclusion")
                    continue;
                var so = new SerializedObject(f);
                Set(so, "m_Settings.Intensity", 1.0f);
                Set(so, "m_Settings.Radius", 0.45f);
                Set(so, "m_Settings.DirectLightingStrength", 0.25f);
                Set(so, "m_Settings.Falloff", 120f);
                so.ApplyModifiedPropertiesWithoutUndo();
            }
#if URP_SCREEN_SPACE_REFLECTION
            if (!data.rendererFeatures.Exists(f => f is ScreenSpaceReflectionRendererFeature))
            {
                var ssr = ScriptableObject.CreateInstance<ScreenSpaceReflectionRendererFeature>();
                ssr.name = "ScreenSpaceReflection";
                AssetDatabase.AddObjectToAsset(ssr, data);
                AssetDatabase.TryGetGUIDAndLocalFileIdentifier(ssr, out string _, out long id);
                var so = new SerializedObject(data);
                var list = so.FindProperty("m_RendererFeatures");
                list.arraySize++;
                list.GetArrayElementAtIndex(list.arraySize - 1).objectReferenceValue = ssr;
                var map = so.FindProperty("m_RendererFeatureMap");
                map.arraySize++;
                map.GetArrayElementAtIndex(map.arraySize - 1).longValue = id;
                so.ApplyModifiedPropertiesWithoutUndo();
                Debug.Log("[LT1Setup] screen-space reflections added to the renderer");
            }
#else
            Debug.LogWarning("[LT1Setup] URP_SCREEN_SPACE_REFLECTION is not defined yet: run LT1Setup.Project first");
#endif
            EditorUtility.SetDirty(data);
            AssetDatabase.SaveAssets();
        }

        // -- helpers ------------------------------------------------------------------------------------------------

        static Material MaterialAt(string path, string shader, System.Action<Material> set)
        {
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                m = new Material(Shader.Find(shader) ?? throw new System.Exception($"shader {shader} did not compile"));
                AssetDatabase.CreateAsset(m, path);
            }
            m.shader = Shader.Find(shader);
            m.enableInstancing = true;
            set(m);
            EditorUtility.SetDirty(m);
            return m;
        }

        static T Asset<T>(string path, System.Action<T> set) where T : ScriptableObject
        {
            var a = AssetDatabase.LoadAssetAtPath<T>(path);
            if (a == null)
            {
                a = ScriptableObject.CreateInstance<T>();
                AssetDatabase.CreateAsset(a, path);
            }
            set(a);
            EditorUtility.SetDirty(a);
            return a;
        }

        static void Set(SerializedObject so, string name, object value)
        {
            var p = so.FindProperty(name) ?? throw new System.Exception($"no property {name} on {so.targetObject.name}");
            switch (value)
            {
                case int i: p.intValue = i; break; // for enums too: the enum's value, not its index
                case float f: p.floatValue = f; break;
                case bool b: p.boolValue = b; break;
                default: throw new System.ArgumentException($"cannot set {name} to {value}");
            }
        }

        static void SetVector3(SerializedObject so, string name, Vector3 v)
        {
            var p = so.FindProperty(name) ?? throw new System.Exception($"no property {name}");
            p.vector3Value = v;
        }
    }
}
