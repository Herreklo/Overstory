using System.Collections;
using System.Globalization;
using System.IO;
using UnityEngine;

namespace Overstory.Play
{
    /// <summary>
    /// The player photographs its own screen and quits, when asked on the command line (LT1g, the walk, W2): the check
    /// that the built app opens and its overlay reads.
    ///
    ///     OverstoryPlayable.app/Contents/MacOS/Overstory -shot /abs/path.png [-shot-after 20]
    ///
    /// It waits that many seconds of real time (20 by default: the overlay's two-second window full), captures the
    /// screen as presented, the overlay included (ScreenCapture), and quits. A capture from outside (macOS screencapture)
    /// shows only the desktop unless the shell holds the Screen Recording permission, so the player takes its own.
    /// Without -shot it does nothing, and never in the editor.
    /// </summary>
    public class PlayerShot : MonoBehaviour
    {
        string path;
        float after;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void FromCommandLine()
        {
            if (Application.isEditor)
                return;
            string path = null;
            float after = 20f;
            var args = System.Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length - 1; i++)
            {
                if (args[i] == "-shot")
                    path = args[i + 1];
                else if (args[i] == "-shot-after")
                    float.TryParse(args[i + 1], NumberStyles.Float, CultureInfo.InvariantCulture, out after);
            }
            if (string.IsNullOrEmpty(path))
                return;
            var go = new GameObject("The player's own shot");
            DontDestroyOnLoad(go);
            var shot = go.AddComponent<PlayerShot>();
            shot.path = path;
            shot.after = after;
        }

        IEnumerator Start()
        {
            yield return new WaitForSecondsRealtime(after);
            if (File.Exists(path))
                File.Delete(path);
            ScreenCapture.CaptureScreenshot(path);
            // the file is written at the end of a later frame
            double give = Time.realtimeSinceStartupAsDouble + 10.0;
            while (!File.Exists(path) && Time.realtimeSinceStartupAsDouble < give)
                yield return null;
            yield return null;
            Debug.Log(File.Exists(path)
                ? $"[PlayerShot] {path} ({Screen.width}x{Screen.height}) after {after:F0} s"
                : $"[PlayerShot] no file at {path} after {after:F0} s");
            Application.Quit(File.Exists(path) ? 0 : 1);
        }
    }
}
