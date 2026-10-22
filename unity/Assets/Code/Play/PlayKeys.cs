using UnityEngine;
using UnityEngine.InputSystem;

namespace Overstory.Play
{
    /// <summary>
    /// The walk's keys (LT1g, the walk, W4): 1 to 5 the judging views (eye-foot, eye-on, street, into12, high), 6 to 9
    /// LT1g's four views (A's window, the steps, the Row, the Anchor's door), as PlayCorner's views list them; L the next
    /// light, M the next mood (none after the last); V the free camera and back (Walker). F1 is the overlay's own.
    /// A view key hands the camera back to the views; any movement key takes it again (Walker).
    /// </summary>
    public class PlayKeys : MonoBehaviour
    {
        public PlayCorner corner;
        public Walker walker;

        static readonly Key[] Digits = { Key.Digit1, Key.Digit2, Key.Digit3, Key.Digit4, Key.Digit5, Key.Digit6, Key.Digit7, Key.Digit8, Key.Digit9 };
        static readonly Key[] Pad = { Key.Numpad1, Key.Numpad2, Key.Numpad3, Key.Numpad4, Key.Numpad5, Key.Numpad6, Key.Numpad7, Key.Numpad8, Key.Numpad9 };

        void Update()
        {
            var k = Keyboard.current;
            if (k == null || corner == null || (walker != null && walker.Scripted))
                return;
            for (int i = 0; i < Digits.Length; i++)
                if (k[Digits[i]].wasPressedThisFrame || k[Pad[i]].wasPressedThisFrame)
                {
                    if (corner.views != null && i < corner.views.Length)
                        corner.SetView(i);
                    return;
                }
            if (k.lKey.wasPressedThisFrame)
                corner.NextLight();
            if (k.mKey.wasPressedThisFrame)
                corner.NextMood();
            if (k.vKey.wasPressedThisFrame && walker != null)
                walker.ToggleFree();
        }
    }
}
