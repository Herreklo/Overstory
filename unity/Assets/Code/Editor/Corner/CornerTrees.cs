using UnityEngine;

namespace Overstory.EditorTools.Corner
{
    /// <summary>
    /// The corner's trees (fixtures/lt1-corner.json): the yard birch, the spruce behind the house and the heath birches,
    /// each from blender/parts/trees/corner.py at the level its distance asks for (every level under a LODGroup in the
    /// scene), drawn by Shaders/CornerTree.shader, which answers _P_Mode itself. Data: Elements/trees/trees.json. The
    /// greybox has no trees, so nothing is hidden.
    /// </summary>
    static class CornerTrees
    {
        [CornerElement("trees")]
        static void Trees(CornerContext corner)
        {
            // the lamp that lights the near tree's side: the one nearest the tree drawn at the near level
            var near = System.Array.Find(LT1CornerTrees.ReadIndex().trees, t => System.Array.Exists(t.levels, l => l.level == "near"));
            var at = near != null ? new Vector2(near.at[0], near.at[1]) : Vector2.zero;
            var lampHead = Vector3.down * 1000f;
            var lampColour = Color.black;
            float best = float.MaxValue;
            foreach (var lamp in corner.Lamps)
            {
                float d = Vector2.Distance(new Vector2(lamp.Head.x, lamp.Head.z), at);
                if (d < best)
                {
                    best = d;
                    lampHead = lamp.Head;
                    lampColour = lamp.Colour.gamma;
                }
            }
            LT1CornerTrees.Place(corner.Root.transform, corner.Camera, true, false, lampHead, lampColour, null, corner.ForScene);
        }
    }
}
