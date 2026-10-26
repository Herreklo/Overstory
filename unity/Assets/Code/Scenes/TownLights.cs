using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using Overstory.World;

namespace Overstory.Scenes
{
    /// <summary>
    /// The town's lamps as lights: each one where the layout put it (lights.json, written with the heart's meshes), the
    /// kind its street was lit with (warm lanterns of 1955, mercury of the 1960s, sodium of the 1970s, the harbour's
    /// red and white lights). The stage turns them on and off with the light rig, and hands them to the fog so each
    /// lamp lights the air round it (FogLights.shader).
    /// </summary>
    [ExecuteAlways]
    public class TownLights : MonoBehaviour
    {
        [Tooltip("lights.json: { lamps: [ { x, y, z, kind } ] } in street metres.")]
        public TextAsset source;

        [Serializable] class Lamp { public float x, y, z, dx, dy; public string kind; }
        [Serializable] class Lamps { public Lamp[] lamps; }

        [Tooltip("The square the town's glow is mapped over: its middle (Unity x, z) and side, as the sky map's.")]
        public Vector2 glowCentre = new Vector2(75f, -75f);
        public float glowSize = 1024f;

        readonly List<(Light light, string kind)> lights = new();
        GraphicsBuffer positions, colours;
        Texture2D glowMap;

        public int Count => lights.Count;

        void OnEnable() => Build();

        void OnDisable()
        {
            if (glowMap != null)
                DestroyImmediate(glowMap);
            glowMap = null;
            positions?.Release();
            colours?.Release();
            positions = colours = null;
            Shader.SetGlobalInt("_OS_FogLampCount", 0);
        }

        /// <summary>Makes a light for every lamp in the source, replacing any made before.</summary>
        public void Build()
        {
            lights.Clear();
            for (int i = transform.childCount - 1; i >= 0; i--)
                DestroyImmediate(transform.GetChild(i).gameObject);
            if (source == null)
                return;
            var data = JsonUtility.FromJson<Lamps>(source.text);
            if (data?.lamps == null)
                return;
            foreach (var l in data.lamps)
            {
                var go = new GameObject($"lamp ({l.kind})") { hideFlags = HideFlags.DontSave };
                go.transform.SetParent(transform, false);
                go.transform.position = StreetSpace.ToUnity(l.x, l.y, l.z);
                var light = go.AddComponent<Light>();
                light.type = LightType.Point;
                if (l.kind == "shop")
                {
                    // out of the window and down onto the pavement, a trapezoid of light as Hopper paints it
                    light.type = LightType.Spot;
                    light.spotAngle = 120f;
                    light.innerSpotAngle = 60f;
                    var out_ = StreetSpace.ToUnity(l.dx, l.dy, 0f).normalized;
                    go.transform.rotation = Quaternion.LookRotation((out_ - Vector3.up * 0.9f).normalized, Vector3.up);
                }
                light.shadows = LightShadows.None;
                light.enabled = false;
                lights.Add((light, l.kind)); // what a kind gives is the rig's (LightRig.lampKinds)
            }
        }

        /// <summary>Lights the lamps as the rig says (on or off, how bright), and hands them to the fog.</summary>
        public void Apply(LightRig r)
        {
            if (lights.Count == 0)
                Build();
            var pos = new Vector4[Mathf.Max(1, lights.Count)];
            var col = new Vector4[Mathf.Max(1, lights.Count)];
            for (int i = 0; i < lights.Count; i++)
            {
                var (light, kind) = lights[i];
                if (light == null)
                    continue;
                bool known = r.Lamp(kind, out var lamp);
                bool on = r.lampsOn && known;
                light.enabled = on;
                if (!on)
                    continue;
                light.color = lamp.colour;
                light.intensity = r.lampIntensity * lamp.intensity;
                light.range = lamp.range;
                var p = light.transform.position;
                pos[i] = new Vector4(p.x, p.y, p.z, lamp.range * 2.5f); // past this a halo is too faint to see
                // a shop's light is a window's, not a bare lamp's: little of it reaches the fog (the kind's share)
                col[i] = (Vector4)(lamp.colour.linear * (r.lampIntensity * lamp.intensity * lamp.fogShare));
            }
            if (positions == null || positions.count != pos.Length)
            {
                positions?.Release();
                colours?.Release();
                positions = new GraphicsBuffer(GraphicsBuffer.Target.Structured, pos.Length, 16);
                colours = new GraphicsBuffer(GraphicsBuffer.Target.Structured, col.Length, 16);
            }
            positions.SetData(pos);
            colours.SetData(col);
            Shader.SetGlobalBuffer("_OS_FogLampPos", positions);
            Shader.SetGlobalBuffer("_OS_FogLampColour", colours);
            Shader.SetGlobalInt("_OS_FogLampCount", r.lampsOn ? lights.Count : 0);
            Shader.SetGlobalFloat("_OS_FogLampStrength", r.lampsOn ? r.lampHalo : 0f);
            SetGlow(r);
        }

        /// <summary>
        /// The town's glow: every lit lamp and shop summed on a map from above and spread about twenty metres, as the
        /// fog spreads their light; the air samples it so fog over lit streets glows from below.
        /// </summary>
        void SetGlow(LightRig r)
        {
            const int n = 256;
            if (glowMap == null)
                glowMap = new Texture2D(n, n, TextureFormat.RGBAHalf, false, true)
                {
                    name = "town glow", wrapMode = TextureWrapMode.Clamp, filterMode = FilterMode.Bilinear, hideFlags = HideFlags.DontSave,
                };
            var px = new Color[n * n];
            float cell = glowSize / n, sigma = 20f;
            int reach = Mathf.CeilToInt(sigma * 3f / cell);
            float x0 = glowCentre.x - glowSize / 2f, z0 = glowCentre.y - glowSize / 2f;
            if (r.lampsOn)
                foreach (var (light, kind) in lights)
                {
                    if (light == null || !r.Lamp(kind, out var lamp))
                        continue;
                    var p = light.transform.position;
                    var c = lamp.colour.linear * (r.lampIntensity * lamp.intensity * lamp.fogShare);
                    int ci = Mathf.FloorToInt((p.x - x0) / cell), cj = Mathf.FloorToInt((p.z - z0) / cell);
                    for (int j = Mathf.Max(0, cj - reach); j <= Mathf.Min(n - 1, cj + reach); j++)
                        for (int i = Mathf.Max(0, ci - reach); i <= Mathf.Min(n - 1, ci + reach); i++)
                        {
                            float dx = (i + 0.5f) * cell + x0 - p.x, dz = (j + 0.5f) * cell + z0 - p.z;
                            px[j * n + i] += c * Mathf.Exp(-(dx * dx + dz * dz) / (2f * sigma * sigma));
                        }
                }
            glowMap.SetPixels(px);
            glowMap.Apply();
            Shader.SetGlobalTexture("_OS_GlowMap", glowMap);
            Shader.SetGlobalVector("_OS_GlowRect", new Vector4(x0, z0, 1f / glowSize, 0f));
        }
    }
}
