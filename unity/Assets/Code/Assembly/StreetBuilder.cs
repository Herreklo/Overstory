using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using Overstory.World;
using Object = UnityEngine.Object;

namespace Overstory.Assembly
{
    /// <summary>
    /// Builds a street from its resolved layout (street.json): every building where its plot puts it,
    /// the lamps and bollards, and the generated ground. Everything it makes is rebuilt on enable and
    /// never saved, so the scene holds only the references and the same layout always gives the same
    /// street.
    /// </summary>
    [ExecuteAlways]
    public class StreetBuilder : MonoBehaviour
    {
        [Serializable]
        public class ModelRef
        {
            public string file;
            public GameObject model;
        }

        public TextAsset layout;
        public Material streetMaterial;
        public Material waterMaterial;
        [Tooltip("The exported models by their path in street.json. Filled by the experiment's setup.")]
        public List<ModelRef> models = new List<ModelRef>();

        public StreetLayout Layout { get; private set; }

        /// <summary>Each lamp's light, with the kind of light it gives (warm, mercury, sodium).</summary>
        public readonly List<(Light light, string kind)> LampLights = new List<(Light, string)>();

        /// <summary>Whether the street stands: its generated objects are under this one.</summary>
        public bool Built => Layout != null && transform.childCount > 0;

        void OnEnable()
        {
            if (!Built)
                Build();
        }

        void OnDisable() => Clear();

        public void Build()
        {
            Clear();
            if (layout == null || streetMaterial == null)
                return;
            Layout = StreetLayout.Parse(layout.text);
            var root = Make(new GameObject($"{Layout.street}, {Layout.year} (built from street.json)"), transform);

            var buildings = Make(new GameObject("buildings"), root.transform);
            foreach (var b in Layout.buildings)
            {
                var go = Place(b.file, buildings.transform, StreetSpace.ToUnity(b.position));
                go.name = $"building {b.id}";
            }

            var lamps = Make(new GameObject("lamps"), root.transform);
            foreach (var l in Layout.lamps)
            {
                var kit = Layout.Kit(l.variant);
                var p = l.position;
                p.z = StreetGround.SurfaceZ(Layout, p.y);
                var go = Place(kit.file, lamps.transform, StreetSpace.ToUnity(p));
                go.name = $"{l.id} ({l.variant})";
                var lightGo = Make(new GameObject("light"), go.transform);
                lightGo.transform.localPosition = StreetSpace.ToUnity(kit.light);
                var light = lightGo.AddComponent<Light>();
                bool lantern = l.variant.StartsWith("post");
                light.type = lantern ? LightType.Point : LightType.Spot;
                if (!lantern)
                {
                    lightGo.transform.localRotation = Quaternion.LookRotation(Vector3.down, Vector3.forward);
                    light.spotAngle = 130f;
                    light.innerSpotAngle = 60f;
                }
                light.range = lantern ? 14f : 22f;
                light.shadows = LightShadows.Soft;
                light.enabled = false; // the scene's light turns lamps on
                LampLights.Add((light, l.light));
            }

            var bollards = Make(new GameObject("bollards"), root.transform);
            var bollard = Layout.Kit(Layout.bollards.variant);
            for (int i = 0; i < Layout.bollards.positions.Length; i++)
            {
                var p = Layout.bollards.positions[i];
                p.z = StreetGround.SurfaceZ(Layout, p.y);
                Place(bollard.file, bollards.transform, StreetSpace.ToUnity(p)).name = $"bollard {i + 1}";
            }

            var trees = Make(new GameObject("trees"), root.transform);
            foreach (var t in Layout.trees ?? new TreeRef[0])
            {
                var p = t.position;
                p.z -= 0.25f; // the trunk stands in the ground, never on it
                var go = Place(Layout.Kit(t.variant).file, trees.transform, StreetSpace.ToUnity(p));
                go.name = $"{t.id} ({t.variant})";
                go.transform.localRotation = Quaternion.Euler(0f, t.turn, 0f);
                go.transform.localScale = Vector3.one * t.scale;
            }

            var ground = Make(new GameObject("ground"), root.transform);
            foreach (var part in StreetGround.Build(Layout))
            {
                var go = Make(new GameObject(part.name), ground.transform);
                go.AddComponent<MeshFilter>().sharedMesh = part.mesh;
                var r = go.AddComponent<MeshRenderer>();
                r.sharedMaterial = part.water ? waterMaterial : streetMaterial;
                r.shadowCastingMode = part.water ? ShadowCastingMode.Off : ShadowCastingMode.On;
            }
        }

        GameObject Place(string file, Transform parent, Vector3 position)
        {
            var model = models.Find(m => m.file == file)?.model;
            if (model == null)
                throw new InvalidOperationException($"the street needs {file}, which the setup has not linked");
            var go = Make(Instantiate(model), parent);
            go.transform.localPosition = position;
            foreach (var r in go.GetComponentsInChildren<MeshRenderer>())
            {
                var mats = new Material[r.sharedMaterials.Length];
                for (int i = 0; i < mats.Length; i++)
                    mats[i] = streetMaterial;
                r.sharedMaterials = mats;
                r.shadowCastingMode = ShadowCastingMode.On;
            }
            return go;
        }

        static GameObject Make(GameObject go, Transform parent)
        {
            go.transform.SetParent(parent, false);
            foreach (var t in go.GetComponentsInChildren<Transform>(true))
                t.gameObject.hideFlags = HideFlags.DontSave;
            return go;
        }

        /// <summary>
        /// Removes everything this builder made: every unsaved child and the meshes generated for it.
        /// Found by looking, not from a list, so a script reload in the editor never leaves a second street.
        /// </summary>
        void Clear()
        {
            LampLights.Clear();
            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                var child = transform.GetChild(i).gameObject;
                if ((child.hideFlags & HideFlags.DontSave) == 0)
                    continue;
                foreach (var mf in child.GetComponentsInChildren<MeshFilter>(true))
                    if (mf.sharedMesh != null && (mf.sharedMesh.hideFlags & HideFlags.DontSave) != 0)
                        Remove(mf.sharedMesh);
                Remove(child);
            }
        }

        static void Remove(Object o)
        {
            if (Application.isPlaying)
                Object.Destroy(o);
            else
                DestroyImmediate(o);
        }
    }
}
