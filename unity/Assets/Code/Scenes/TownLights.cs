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

        [Serializable] class Lamp { public float x, y, z; public string kind; }
        [Serializable] class Lamps { public Lamp[] lamps; }

        // what each kind gives (sRGB colour, intensity relative to the rig's lamp intensity, reach in metres)
        static readonly Dictionary<string, (Color colour, float strength, float range)> Kinds = new()
        {
            ["warm"] = (new Color(1.0f, 0.70f, 0.42f), 0.55f, 14f),     // a 100 W bulb in a lantern
            ["mercury"] = (new Color(0.74f, 0.90f, 0.92f), 1.0f, 22f),  // mercury vapour, blue-green white
            ["sodium"] = (new Color(1.0f, 0.60f, 0.26f), 1.5f, 28f),    // high-pressure sodium, on a 7 m pole
            ["red"] = (new Color(1.0f, 0.16f, 0.10f), 2.0f, 30f),       // the breakwater's head
            ["white"] = (new Color(0.92f, 0.95f, 1.0f), 2.0f, 30f),     // the beacon on the Pip
        };

        readonly List<(Light light, string kind)> lights = new();
        GraphicsBuffer positions, colours;

        public int Count => lights.Count;

        void OnEnable() => Build();

        void OnDisable()
        {
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
                light.shadows = LightShadows.None;
                light.enabled = false;
                lights.Add((light, Kinds.ContainsKey(l.kind) ? l.kind : "warm"));
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
                var (colour, strength, range) = Kinds[kind];
                bool on = r.lampsOn && light != null;
                if (light == null)
                    continue;
                light.enabled = on;
                light.color = colour;
                light.intensity = r.lampIntensity * strength;
                light.range = range;
                var p = light.transform.position;
                pos[i] = new Vector4(p.x, p.y, p.z, range * 2.5f); // past this a halo is too faint to see
                col[i] = on ? (Vector4)(colour.linear * (r.lampIntensity * strength)) : Vector4.zero;
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
        }
    }
}
