using UnityEngine;
using UnityEngine.InputSystem;
using Overstory.Play;

namespace Overstory.Corner
{
    /// <summary>
    /// The painted corner's free camera (the app and Play in the editor): the walk's own (Walker, its free camera)
    /// taken from the street stop at the start. Its keys are the walk's: click to hold the mouse and look, Esc lets it
    /// go; W A S D or the arrows fly where it looks, Shift faster, Ctrl slower; PgUp and PgDn or the wheel rise and fall;
    /// Q and E turn, R and F tilt. 1 or Home puts it back on the street stop. F1 hides the frame time. Cmd+Q quits.
    /// </summary>
    public class CornerFly : MonoBehaviour
    {
        public Walker walker;
        public Camera view;

        Vector3 homePosition;
        Quaternion homeRotation;

        void Start()
        {
            if (walker == null || view == null)
                return;
            homePosition = view.transform.position;
            homeRotation = view.transform.rotation;
            walker.lens = view.fieldOfView;
            walker.TakeOver(preferFree: true);
        }

        void Update()
        {
            var k = Keyboard.current;
            if (k == null || walker == null || view == null)
                return;
            if (k.digit1Key.wasPressedThisFrame || k.numpad1Key.wasPressedThisFrame || k.homeKey.wasPressedThisFrame)
            {
                view.transform.SetPositionAndRotation(homePosition, homeRotation);
                walker.TakeOver(preferFree: true);
            }
        }
    }
}
