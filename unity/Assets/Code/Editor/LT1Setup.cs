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

            Asset<LightRig>(LT1 + "/Light/LT1_Clay.asset", Clay);
            Asset<LightRig>(LT1 + "/Light/LT1_BlueHour.asset", BlueHour);
            Asset<LightRig>(LT1 + "/Light/LT1_SummerEvening.asset", SummerEvening);
            Asset<LightRig>(LT1 + "/Light/LT1_ClearDay.asset", ClearDay);
            foreach (var (name, pos, target) in CityShots)
                Asset<CameraShot>($"{LT1}/Views/LT1_City_{name}.asset", s =>
                {
                    s.position = pos;
                    s.target = target;
                    s.verticalFov = 42f;
                    s.near = 0.5f;
                    s.far = 25000f;
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

        /// <summary>
        /// The city view's middle stop and its variants: from the harbour, the town climbing behind the
        /// quay, the ridges and the sky in frame. Street coordinates in metres.
        /// </summary>
        public static readonly (string name, Vector3 pos, Vector3 target)[] CityShots =
        {
            ("Mid", new Vector3(55f, -115f, 46f), new Vector3(58f, 45f, 15f)),
            ("MidLow", new Vector3(52f, -115f, 22f), new Vector3(55f, 40f, 10f)),
            ("MidHigh", new Vector3(52f, -150f, 75f), new Vector3(55f, 30f, 4f)),
            ("OrbitWest", new Vector3(-75f, -115f, 42f), new Vector3(50f, 35f, 8f)),
            ("OrbitEast", new Vector3(135f, -150f, 40f), new Vector3(52f, 60f, 32f)),
            // inside the town: over the quay by the warehouses, looking west along Harbour Row to the harbour mouth
            ("Quay", new Vector3(104f, -34f, 14f), new Vector3(46f, 22f, 10f)),
            // over the roofs of the upper town towards the light (west, over the harbour): roofs and chimneys against the glow
            ("Roofs", new Vector3(96f, 60f, 30f), new Vector3(12f, -28f, 8f)),
        };

        /// <summary>
        /// Clay: one soft, neutral light to judge shape alone. A sky dome and a key from the front left,
        /// high enough to model every roof, and thin air that lays the ridges back in layers.
        /// </summary>
        static void Clay(LightRig r)
        {
            r.sunBearing = 235f;
            r.sunElevation = 34f;
            r.sunColour = Color.white;
            r.sunIntensity = 2.4f;
            r.shadowStrength = 1f;
            r.zenith = C(168, 172, 176);
            r.horizon = C(208, 210, 212);
            r.belowHorizon = C(120, 122, 122);
            r.skyCurve = 0.6f;
            r.sunGlow = Color.black;
            // a weak fill, so the key models every form: lit faces near white, shade a mid grey
            r.ambientSky = C(128, 130, 134);
            r.ambientEquator = C(96, 98, 100);
            r.ambientGround = C(62, 62, 62);
            r.ambientIntensity = 1f;
            r.fogColour = C(196, 198, 200);
            r.fogDensity = 0.00025f;
            r.fogHeightFalloff = 0.002f;
            r.fogBaseHeight = 0f;
            r.fogMaxOpacity = 0.92f;
            r.fogSunColour = Color.black;
            r.wetness = 0f;
            r.windowGlow = 0f;
            r.lampsOn = false;
            r.lampGlow = 0f;
            r.lampIntensity = 0f;
            r.postExposure = 0f;
            r.contrast = 0f;
            r.saturation = -100f;
            r.temperature = 0f;
            r.tint = 0f;
            r.colourFilter = Color.white;
            r.bloomIntensity = 0f;
            r.bloomThreshold = 1.1f;
            r.reflectionStrength = 0f;
            r.clock = 0f;
        }

        /// <summary>
        /// Blue hour in October, after rain: the sun just down behind the harbour mouth to the west, the
        /// sky one cold hue at low value (Sohlberg's blue night), a last warm glow low in the west, the
        /// air turning lighter and bluer with distance, and the warm light of the rooms where people are
        /// home and of the lamps, each in its era's colour, doubled in the wet stone and the water.
        /// </summary>
        static void BlueHour(LightRig r)
        {
            r.sunBearing = 196f;
            r.sunElevation = 7f;
            r.sunColour = C(150, 140, 200);
            r.sunIntensity = 0.35f;
            r.shadowStrength = 0.5f;

            r.zenith = C(24, 36, 74);
            r.horizon = C(86, 98, 146);
            r.belowHorizon = C(18, 22, 34);
            r.skyCurve = 0.55f;
            r.sunGlow = C(120, 74, 70);
            r.sunGlowPower = 5f;

            r.ambientSky = C(78, 96, 150);
            r.ambientEquator = C(52, 62, 102);
            r.ambientGround = C(30, 32, 46);
            r.ambientIntensity = 0.5f; // darker: the town's own lights carry the frame

            r.fogColour = C(44, 52, 92);
            r.fogMidColour = C(76, 80, 136);
            r.fogMidDistance = 400f;
            r.fogFarColour = C(150, 132, 178);
            r.fogFarDistance = 3000f;
            r.fogDensity = 0.0034f;
            r.fogHeightFalloff = 0.014f;
            r.fogBaseHeight = 0f;
            r.fogMaxOpacity = 0.88f;
            r.fogSunColour = C(70, 40, 44);
            r.fogSunPower = 6f;

            r.wetness = 0.7f;
            r.cloudCover = 0.32f;
            r.cloudSize = 600f;
            r.cloudSoftness = 0.1f;
            r.cloudHeight = 1800f;
            r.windowGlow = 3.2f; // warm, not bleached: the tonemapper keeps a lamp-lit room's colour
            r.lampsOn = true;
            r.lampGlow = 14f;
            r.lampIntensity = 18f;
            r.windowSpill = 2.2f;

            r.postExposure = 1.1f;
            r.contrast = 12f;
            r.saturation = 0f;
            r.temperature = 0f;
            r.tint = 0f;
            r.colourFilter = Color.white;
            r.bloomIntensity = 0.45f;
            r.bloomThreshold = 0.95f;
            r.reflectionStrength = 1f;
            r.clock = 0f;
        }

        /// <summary>
        /// A hot summer evening: 28 degrees, the sun low in the west over the harbour mouth, gold on every
        /// west wall, long warm shadows filled with blue from the sky, a dry street, windows dark.
        /// </summary>
        static void SummerEvening(LightRig r)
        {
            r.sunBearing = 232f; // low over the harbour, full on the fronts that face it
            r.sunElevation = 10f;
            r.sunColour = C(255, 190, 118);
            r.sunIntensity = 3.4f;
            r.shafts = 1.3f;
            r.shaftReach = 0.65f;
            r.shaftDecay = 0.968f;
            r.shaftThreshold = 0.55f;
            r.shadowStrength = 1f;

            r.zenith = C(92, 136, 196);
            r.horizon = C(250, 206, 150);
            r.belowHorizon = C(70, 62, 60);
            r.skyCurve = 0.45f;
            r.sunGlow = C(255, 150, 70);
            r.sunGlowPower = 6f;

            r.ambientSky = C(112, 146, 200);
            r.ambientEquator = C(168, 148, 126);
            r.ambientGround = C(96, 82, 68);
            r.ambientIntensity = 0.58f; // little fill: shadow is deep, and coloured by the sky

            r.fogColour = C(150, 112, 92);
            r.fogMidColour = C(204, 156, 128);
            r.fogMidDistance = 350f;
            r.fogFarColour = C(240, 206, 174);
            r.fogFarDistance = 3000f;
            r.fogDensity = 0.0018f;
            r.fogHeightFalloff = 0.014f; // haze lies low: a hill grades from a hazy foot to a clearer crest
            r.fogBaseHeight = 0f;
            r.fogMaxOpacity = 0.85f;
            r.fogSunColour = C(210, 120, 46);
            r.fogSunPower = 4f;

            r.wetness = 0f;
            r.cloudCover = 0.4f;       // broken cloud: the low sun falls on the town in pools
            r.cloudSize = 900f;
            r.cloudSoftness = 0.05f;
            r.cloudHeight = 1200f;
            r.windowGlow = 0f;
            r.lampsOn = false;
            r.lampGlow = 0f;
            r.lampIntensity = 0f;

            r.postExposure = 0.2f;
            r.contrast = 14f;
            r.saturation = 4f;
            r.temperature = 0f;
            r.tint = 0f;
            r.colourFilter = Color.white;
            r.bloomIntensity = 0.25f;
            r.bloomThreshold = 1.1f;
            r.reflectionStrength = 1f;
            r.clock = 0f;
        }

        /// <summary>
        /// A clear afternoon after rain: deep blue sky, big cumulus with lit tops, sun high in the south-west,
        /// colour at full strength, the air clean and only blue far off.
        /// </summary>
        static void ClearDay(LightRig r)
        {
            r.sunBearing = 228f;
            r.sunElevation = 36f;
            r.sunColour = C(255, 242, 218);
            r.sunIntensity = 3.0f;
            r.shadowStrength = 1f;

            r.zenith = C(34, 104, 206);
            r.horizon = C(168, 204, 236);
            r.belowHorizon = C(80, 90, 96);
            r.skyCurve = 0.5f;
            r.sunGlow = C(60, 50, 30);
            r.sunGlowPower = 10f;

            r.ambientSky = C(118, 158, 222);
            r.ambientEquator = C(168, 170, 160);
            r.ambientGround = C(112, 100, 78);
            r.ambientIntensity = 1f;

            r.fogColour = C(176, 196, 214);
            r.fogMidColour = C(170, 198, 228);
            r.fogMidDistance = 500f;
            r.fogFarColour = C(198, 220, 242);
            r.fogFarDistance = 4000f;
            r.fogDensity = 0.0008f;
            r.fogHeightFalloff = 0.01f;
            r.fogBaseHeight = 0f;
            r.fogMaxOpacity = 0.8f;
            r.fogSunColour = Color.black;

            r.wetness = 0f;
            r.cloudCover = 0.38f;
            r.cloudSize = 520f;
            r.cloudSoftness = 0.06f;
            r.cloudHeight = 1300f;
            r.windowGlow = 0f;
            r.lampsOn = false;
            r.lampGlow = 0f;
            r.lampIntensity = 0f;

            r.postExposure = -0.2f;
            r.contrast = 10f;
            r.saturation = 14f;
            r.temperature = 0f;
            r.tint = 0f;
            r.colourFilter = Color.white;
            r.bloomIntensity = 0.15f;
            r.bloomThreshold = 1.2f;
            r.reflectionStrength = 1f;
            r.clock = 0f;
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
            r.fogDensity = 0.0028f;
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
            Directory.CreateDirectory(Materials);
            AssetDatabase.Refresh();
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
            // light rays: a full-screen pass over the sky, before post-processing
            if (!data.rendererFeatures.Exists(f => f != null && f.name == "LightShafts"))
            {
                var mat = MaterialAt(Materials + "/M_LightShafts.mat", "Overstory/LightShafts", m => { });
                var ls = ScriptableObject.CreateInstance<FullScreenPassRendererFeature>();
                ls.name = "LightShafts";
                ls.passMaterial = mat;
                ls.injectionPoint = FullScreenPassRendererFeature.InjectionPoint.BeforeRenderingPostProcessing;
                ls.requirements = ScriptableRenderPassInput.Depth;
                ls.fetchColorBuffer = true;
                AssetDatabase.AddObjectToAsset(ls, data);
                AssetDatabase.TryGetGUIDAndLocalFileIdentifier(ls, out string _, out long lid);
                var so3 = new SerializedObject(data);
                var list3 = so3.FindProperty("m_RendererFeatures");
                list3.arraySize++;
                list3.GetArrayElementAtIndex(list3.arraySize - 1).objectReferenceValue = ls;
                var map3 = so3.FindProperty("m_RendererFeatureMap");
                map3.arraySize++;
                map3.GetArrayElementAtIndex(map3.arraySize - 1).longValue = lid;
                so3.ApplyModifiedPropertiesWithoutUndo();
                Debug.Log("[LT1Setup] light rays added to the renderer");
            }
            // the key block of look D: a full-screen pass over depth and normals, before post-processing
            if (!data.rendererFeatures.Exists(f => f != null && f.name == "KeyBlock"))
            {
                var mat = MaterialAt(Materials + "/M_KeyBlock.mat", "Overstory/KeyBlock", m => { });
                var kb = ScriptableObject.CreateInstance<FullScreenPassRendererFeature>();
                kb.name = "KeyBlock";
                kb.passMaterial = mat;
                kb.injectionPoint = FullScreenPassRendererFeature.InjectionPoint.BeforeRenderingPostProcessing;
                kb.requirements = ScriptableRenderPassInput.Depth | ScriptableRenderPassInput.Normal;
                kb.fetchColorBuffer = true;
                AssetDatabase.AddObjectToAsset(kb, data);
                AssetDatabase.TryGetGUIDAndLocalFileIdentifier(kb, out string _, out long kid);
                var so2 = new SerializedObject(data);
                var list2 = so2.FindProperty("m_RendererFeatures");
                list2.arraySize++;
                list2.GetArrayElementAtIndex(list2.arraySize - 1).objectReferenceValue = kb;
                var map2 = so2.FindProperty("m_RendererFeatureMap");
                map2.arraySize++;
                map2.GetArrayElementAtIndex(map2.arraySize - 1).longValue = kid;
                so2.ApplyModifiedPropertiesWithoutUndo();
                Debug.Log("[LT1Setup] the key block added to the renderer");
            }
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
