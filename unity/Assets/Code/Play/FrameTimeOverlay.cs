using System.Globalization;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Overstory.Play
{
    /// <summary>
    /// The frame time on screen (LT1g, the walk, W2; docs/measuring.md, The frame-time harness): from FrameTimingManager,
    /// the presented frame's period (its CPU frame time, which includes waiting for the GPU and the screen), the main
    /// thread's own time and the GPU's time, each as the mean and the worst 1% (the 99th percentile, as the harness's
    /// p99) over the last two seconds, with the light, view and mood shown. F1 hides and shows it. As in the harness's
    /// summary, the GPU row is the GPU's own time per presented frame, which on Apple's tile GPUs overlaps frames and
    /// can exceed the frame's period (first build, 22 October: frame 29.8 ms, GPU 45.8 ms at eye-foot in drizzle).
    ///
    /// A guide while walking, not a measurement: the harness (tools/perf.sh) measures. Frame timing stats must be on in
    /// the player (LT1Perf.BuildPlayer turns them on for its build); without them the overlay says so.
    ///
    /// Hooks: LightName, ViewName and MoodName are set by whatever drives the light, the camera and the mood
    /// (PlayCorner today; W4's PlayKeys and walker later, e.g. ViewName = "walk"); null shows a dash, and an empty mood
    /// is not shown. Visible says whether it is drawn.
    ///
    /// Drawn with IMGUI (no package, no asset): its text is rebuilt four times a second and drawn as one label, without
    /// the layout pass, so it costs next to nothing.
    /// </summary>
    public class FrameTimeOverlay : MonoBehaviour
    {
        public static string LightName { get; set; }
        public static string ViewName { get; set; }
        public static string MoodName { get; set; }

        [Tooltip("Seconds of frames each figure is taken over.")]
        public float window = 2f;
        [Tooltip("How often the text is rebuilt, a second.")]
        public float refresh = 4f;
        public bool visible = true;

        public bool Visible { get => visible; set => visible = value; }

        const int Capacity = 4096;     // two seconds at up to 2,000 frames a second
        readonly double[] when = new double[Capacity];
        readonly float[] frame = new float[Capacity], cpu = new float[Capacity], gpu = new float[Capacity];
        readonly float[] scratch = new float[Capacity];
        readonly FrameTiming[] timing = new FrameTiming[1];
        int head, count;
        ulong lastStart;
        double nextText;
        string text = "";
        GUIStyle style;
        Texture2D back;
        readonly GUIContent content = new GUIContent();
        Vector2 contentSize;

        void Awake() => useGUILayout = false;

        void Update()
        {
            if (Keyboard.current != null && Keyboard.current.f1Key.wasPressedThisFrame)
                visible = !visible;

            FrameTimingManager.CaptureFrameTimings();
            if (FrameTimingManager.GetLatestTimings(1, timing) >= 1 && timing[0].frameStartTimestamp != lastStart)
            {
                lastStart = timing[0].frameStartTimestamp;
                when[head] = Time.realtimeSinceStartupAsDouble;
                frame[head] = (float)timing[0].cpuFrameTime;
                cpu[head] = (float)timing[0].cpuMainThreadFrameTime;
                gpu[head] = (float)timing[0].gpuFrameTime;
                head = (head + 1) % Capacity;
                count = Mathf.Min(count + 1, Capacity);
            }

            double now = Time.realtimeSinceStartupAsDouble;
            if (visible && now >= nextText)
            {
                nextText = now + 1.0 / Mathf.Max(refresh, 0.5f);
                text = Compose(now);
            }
        }

        /// <summary>The mean and the 99th percentile of one series over the window (NaN when empty).</summary>
        (float mean, float p99, int n) Stats(float[] series, double now)
        {
            int n = 0;
            double sum = 0;
            for (int k = 0; k < count; k++)
            {
                int i = (head - 1 - k + Capacity) % Capacity;
                if (now - when[i] > window)
                    break;
                scratch[n++] = series[i];
                sum += series[i];
            }
            if (n == 0)
                return (float.NaN, float.NaN, 0);
            System.Array.Sort(scratch, 0, n);
            // the nearest rank: the frame that 1% of the window's frames are slower than
            int rank = Mathf.Clamp(Mathf.CeilToInt(0.99f * n) - 1, 0, n - 1);
            return ((float)(sum / n), scratch[rank], n);
        }

        string Compose(double now)
        {
            var ci = CultureInfo.InvariantCulture;
            if (!FrameTimingManager.IsFeatureEnabled())
                return "frame timing stats are off in this build (PlayerSettings.enableFrameTimingStats)\n" + Names();
            var (fm, f99, n) = Stats(frame, now);
            var (cm, c99, _) = Stats(cpu, now);
            var (gm, g99, _) = Stats(gpu, now);
            // no composite formatting: the player's Mono threw a FormatException on these rows' format strings at the
            // first frames (trial build, 22 October), so the columns are padded by hand
            string Ms(float v, int width) => v.ToString("F1", ci).PadLeft(width);
            string Row(string label, float mean, float p99) => float.IsNaN(mean) || mean <= 0f
                ? label.PadRight(6) + "   n/a"
                : label.PadRight(6) + Ms(mean, 6) + " ms   worst 1% " + Ms(p99, 5);
            var urp = GraphicsSettings.currentRenderPipeline as UniversalRenderPipelineAsset;
            string fps = float.IsNaN(fm) || fm <= 0f ? "" : "  (" + (1000f / fm).ToString("F0", ci) + " fps)";
            return Row("frame", fm, f99) + fps + "\n"
                 + Row("CPU", cm, c99) + "\n"
                 + Row("GPU", gm, g99) + "\n"
                 + n.ToString(ci) + " frames in " + window.ToString("F0", ci) + " s · " + Screen.width.ToString(ci) + "×"
                 + Screen.height.ToString(ci) + " · MSAA " + (urp != null ? urp.msaaSampleCount : 1).ToString(ci) + "x\n"
                 + Names();
        }

        static string Names()
        {
            string s = (LightName ?? "–") + " · " + (ViewName ?? "–");
            if (!string.IsNullOrEmpty(MoodName))
                s += " · " + MoodName;
            return s + "\nF1 hides";
        }

        void OnGUI()
        {
            if (!visible || Event.current.type != EventType.Repaint || text.Length == 0)
                return;
            int size = Mathf.Max(12, Mathf.RoundToInt(Screen.height / 52f));
            if (style == null || style.fontSize != size)
            {
                if (back == null)
                {
                    back = new Texture2D(1, 1, TextureFormat.RGBA32, false) { hideFlags = HideFlags.HideAndDontSave };
                    back.SetPixel(0, 0, new Color(0f, 0f, 0f, 0.55f));
                    back.Apply();
                }
                style = new GUIStyle(GUI.skin.label)
                {
                    fontSize = size,
                    richText = false,
                    wordWrap = false,
                    alignment = TextAnchor.UpperLeft,
                    padding = new RectOffset(size / 2, size / 2, size / 3, size / 3),
                };
                style.normal.textColor = new Color(0.95f, 0.95f, 0.92f);
                style.normal.background = back;
                style.font = Font.CreateDynamicFontFromOSFont(new[] { "Menlo", "Monaco", "Courier New" }, size);
                content.text = null;
            }
            if (!ReferenceEquals(content.text, text))
            {
                content.text = text;
                contentSize = style.CalcSize(content);
            }
            GUI.Label(new Rect(size * 0.6f, size * 0.6f, contentSize.x, contentSize.y), content, style);
        }

        void OnDestroy()
        {
            if (back != null)
                Destroy(back);
        }
    }
}
