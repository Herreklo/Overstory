using UnityEngine;
using Overstory.World;

namespace Overstory.Scenes
{
    /// <summary>A fixed camera on a street: where it stands and what it looks at, in street coordinates.</summary>
    [CreateAssetMenu(menuName = "Overstory/Camera shot")]
    public class CameraShot : ScriptableObject
    {
        [Tooltip("Where the camera stands: x along the street, y from the building line (negative towards the harbour), z up, in metres.")]
        public Vector3 position;
        [Tooltip("The point it looks at, in the same coordinates.")]
        public Vector3 target;
        [Tooltip("Vertical field of view in degrees.")]
        public float verticalFov = 40f;
        public float near = 0.2f;
        public float far = 1500f;

        public void Apply(Camera cam)
        {
            Vector3 p = StreetSpace.ToUnity(position), t = StreetSpace.ToUnity(target);
            cam.transform.SetPositionAndRotation(p, Quaternion.LookRotation(t - p, Vector3.up));
            cam.fieldOfView = verticalFov;
            cam.nearClipPlane = near;
            cam.farClipPlane = far;
        }
    }
}
