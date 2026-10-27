using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Overstory.Corner
{
    /// <summary>
    /// The painted corner's look in a saved scene (LT1PaintedCorner, Code/Editor/Corner/), in the editor and in the app:
    /// the page's values set again as globals (as LT1ArtPasses.Compose set them from Paint.json and the elements), and
    /// for each game or scene camera while it draws: the shadows' reach, the pipeline renderer's own features off (they
    /// are put back after, so no shared asset changes), and the air (PaintAirPass) enqueued.
    /// </summary>
    [ExecuteAlways]
    public class PaintedCornerLook : MonoBehaviour
    {
        [Serializable] public struct FloatGlobal { public string name; public float value; }
        [Serializable] public struct VectorGlobal { public string name; public Vector4 value; }
        [Serializable] public class ArrayGlobal { public string name; public Vector4[] values; }
        [Serializable] public struct TextureGlobal { public string name; public Texture value; }

        public List<FloatGlobal> floats = new List<FloatGlobal>();
        public List<VectorGlobal> vectors = new List<VectorGlobal>();
        public List<ArrayGlobal> arrays = new List<ArrayGlobal>();
        public List<TextureGlobal> textures = new List<TextureGlobal>();
        [Tooltip("PaintAir.shader's material: its pass \"Scene\" draws the air.")]
        public Material air;
        [Tooltip("The pipeline's renderer: its features are off while a camera draws the corner, and on again after.")]
        public UniversalRendererData rendererData;
        [Tooltip("The shadows' reach (m) while a camera draws the corner (Paint.json, shadowM).")]
        public float shadowDistance = 80f;
        [Tooltip("The contact shade's turns averaged in each pixel.")]
        public float contactTurns = 4f;

        PaintAirPass pass;
        readonly List<(ScriptableRendererFeature feature, bool on)> held = new List<(ScriptableRendererFeature, bool)>();
        float heldShadow = -1f;

        void OnEnable()
        {
            pass = new PaintAirPass();
            Apply();
            RenderPipelineManager.beginCameraRendering += Begin;
            RenderPipelineManager.endCameraRendering += End;
        }

        void OnDisable()
        {
            RenderPipelineManager.beginCameraRendering -= Begin;
            RenderPipelineManager.endCameraRendering -= End;
            PutBack();
        }

        /// <summary>The page's values as globals.</summary>
        public void Apply()
        {
            foreach (var a in arrays)
                if (a.values != null && a.values.Length > 0)
                    Shader.SetGlobalVectorArray(a.name, a.values);
            foreach (var v in vectors)
                Shader.SetGlobalVector(v.name, v.value);
            foreach (var f in floats)
                Shader.SetGlobalFloat(f.name, f.value);
            foreach (var t in textures)
                if (t.value != null)
                    Shader.SetGlobalTexture(t.name, t.value);
            Shader.SetGlobalFloat("_P_Mode", 0f);
        }

        static bool Draws(Camera cam) => cam.cameraType == CameraType.Game || cam.cameraType == CameraType.SceneView;

        void Begin(ScriptableRenderContext context, Camera cam)
        {
            if (!Draws(cam) || !isActiveAndEnabled)
                return;
            Apply();
            PutBack();
            if (GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp)
            {
                heldShadow = urp.shadowDistance;
                urp.shadowDistance = shadowDistance;
            }
            if (rendererData != null)
                foreach (var f in rendererData.rendererFeatures)
                    if (f != null)
                    {
                        held.Add((f, f.isActive));
                        f.SetActive(false);
                    }
            var data = cam.GetUniversalAdditionalCameraData();
            if (data != null && data.scriptableRenderer != null && air != null)
            {
                pass.air = air;
                pass.contactTurns = contactTurns;
                data.scriptableRenderer.EnqueuePass(pass);
            }
        }

        void End(ScriptableRenderContext context, Camera cam)
        {
            if (Draws(cam))
                PutBack();
        }

        void PutBack()
        {
            foreach (var (f, on) in held)
                if (f != null)
                    f.SetActive(on);
            held.Clear();
            if (heldShadow >= 0f && GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp)
                urp.shadowDistance = heldShadow;
            heldShadow = -1f;
        }
    }
}
