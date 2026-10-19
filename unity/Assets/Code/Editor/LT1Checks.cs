using UnityEditor;
using UnityEngine;

namespace Overstory.EditorTools
{
    /// <summary>Checks that the export and import agree on axes: Unity (x, y, z) must be street (x, z, y).</summary>
    public static class LT1Checks
    {
        public static void Axes()
        {
            // the 1983 lamp reaches its arm 2.5 m out over the street, towards the harbour (street -y)
            var lamp = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Art/Kit/lamp/kit_lamp_pole-1983_lod0.fbx");
            var mf = lamp.GetComponentInChildren<MeshFilter>();
            var b = mf.sharedMesh.bounds;
            var t = mf.transform;
            Debug.Log($"[LT1Checks] lamp root rotation {lamp.transform.localEulerAngles}, mesh transform {t.localEulerAngles} scale {t.localScale}, bounds min {b.min} max {b.max}");
            var house = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Art/Buildings/harbour-row/bld_101_1989.fbx");
            var hb = house.GetComponentInChildren<MeshFilter>().sharedMesh.bounds;
            Debug.Log($"[LT1Checks] building 101 root rotation {house.transform.localEulerAngles}, mesh bounds min {hb.min} max {hb.max} (Blender x -5.70..7.35, y -5.55..5.25)");
            bool ok = Quaternion.Angle(t.rotation, Quaternion.identity) < 0.01f && b.min.z < -2.3f && b.max.z < 0.3f && b.max.y > 7.5f && Mathf.Abs(b.min.y) < 0.01f
                      && Quaternion.Angle(house.transform.rotation, Quaternion.identity) < 0.01f && Mathf.Abs(hb.min.x + 5.70f) < 0.02f && Mathf.Abs(hb.max.x - 7.35f) < 0.02f;
            Debug.Log(ok ? "[LT1Checks] axes OK: Unity (x, y, z) = street (x, z, y)" : "[LT1Checks] AXES WRONG");
            if (!ok)
                EditorApplication.Exit(1);
        }
    }
}
