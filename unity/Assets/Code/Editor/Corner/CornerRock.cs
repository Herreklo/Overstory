using System;
using System.IO;
using UnityEngine;

namespace Overstory.EditorTools.Corner
{
    /// <summary>
    /// The corner's knuckle as its jointing breaks it, and the ground where its clay is cut away: the meshes
    /// tools/corner_ground.py builds (cache/ground/, R2B2 in the gully port's vertex layout: the sky each corner sees
    /// with the contact shade in UV3.x, lichen in UV4.y, moss in UV5.x), drawn with the painted surface's own values
    /// (Elements/rock/rock.json). The clay it replaces is hidden in the fixture's boxes (fixtures/lt1-corner-ground.json,
    /// patch), which the patch fills to the clay's own edge.
    /// </summary>
    static class CornerRock
    {
        [Serializable]
        class Look
        {
            public CornerSurface rock = new(), patch = new();
            public string level = "l0";
        }

        [Serializable]
        class Box
        {
            public string name;
            public float[] min, max;
        }

        [Serializable]
        class Patch
        {
            public Box[] boxes;
        }

        [Serializable]
        class Fixture
        {
            public Patch patch;
        }

        [CornerElement("rock")]
        static void Rock(CornerContext corner)
        {
            var look = corner.Data<Look>("rock.json");
            string repo = Path.GetFullPath(Path.Combine(Application.dataPath, "..", ".."));
            string knuckle = Path.Combine(repo, "cache", "ground", $"knuckle-{look.level}.bin");
            string ground = Path.Combine(repo, "cache", "ground", "patch-l0.bin");
            foreach (var f in new[] { knuckle, ground })
                if (!File.Exists(f))
                    throw new FileNotFoundException("the rock's meshes are built by tools/corner_ground.py (Blender's python)", f);

            var fix = JsonUtility.FromJson<Fixture>(File.ReadAllText(Path.Combine(repo, "fixtures", "lt1-corner-ground.json")));
            foreach (var b in fix.patch.boxes)
                corner.HideBox(new Vector3(b.min[0], b.min[1], -5f), new Vector3(b.max[0], b.max[1], 30f), 1);

            var km = LT1R2b.Load(knuckle);
            km.name = "knuckle";
            km.hideFlags = HideFlags.None;
            corner.Add("knuckle", km, corner.Surface(look.rock, "rock"));
            var gm = LT1R2b.Load(ground);
            gm.name = "knuckle ground";
            gm.hideFlags = HideFlags.None;
            corner.Add("knuckle ground", gm, corner.Surface(look.patch, "ground"));
        }
    }
}
