using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using Overstory.Scenes;
using Overstory.World;

namespace Overstory.Play
{
    /// <summary>
    /// The walk's corner in the player (LT1g, the walk; reviews/lt1/playable/outline.md §2): what LT1Play.Compose put
    /// in the scene to switch between (the judging views, the judging lights, the moods), and the town's shared globals
    /// set once at the start, as the editor's frames set them (LT1Stone.Stage). It decides nothing about the world: the
    /// views, rigs and moods are the measuring tools' and the heart's own (LT1Stone.Views, LT1Stone.Moments,
    /// LT1Heart.Moods), in their order.
    ///
    /// Hooks for the play code (W4's PlayKeys and walker):
    /// - SetView(i), SetLight(i), SetMood(i) switch, and NextLight() / NextMood() cycle; mood -1 is none (neutral).
    /// - Release() hands the camera to a walker: the views stop placing it until SetView is called again.
    /// - ViewName, LightName, MoodName say what is shown; each change is pushed to FrameTimeOverlay and raises Changed.
    /// - Current is the scene's corner.
    /// The camera's place is applied through StreetStage.Apply (a CameraShot), which also re-aims the light's shafts
    /// (_OS_SunScreen); a walker that moves the camera itself must call stage.Apply() or its own shaft update.
    /// </summary>
    [DefaultExecutionOrder(-100)]
    public class PlayCorner : MonoBehaviour
    {
        [System.Serializable]
        public class View
        {
            public string name;
            [Tooltip("Street metres: x along, y back from the building line, z up.")]
            public Vector3 position;
            public Vector3 target;
            public float fov;
        }

        [System.Serializable]
        public class Moment
        {
            public string name;
            public LightRig rig;
        }

        [System.Serializable]
        public class Mood
        {
            public string name;
            public Grade grade;
        }

        public StreetStage stage;
        public View[] views;
        public Moment[] moments;
        public Mood[] moods;
        [Tooltip("The view, light and mood shown first (mood -1: none).")]
        public int view, moment, mood = -1;
        [Tooltip("The sun's shadow reach, as the judging frames set it (LT1Stone.Aim).")]
        public float shadowDistance = 120f;
        [Tooltip("Renderers whose bounds the editor set by hand (a leaf card is drawn out from its pivot in the shader), " +
                 "with those bounds: a scene keeps no renderer's own bounds, so they are set again here.")]
        public Renderer[] boundsOf;
        public Bounds[] bounds;
        [Tooltip("Shaders the player finds by name (SkyMap), kept in the build by this reference.")]
        public Shader[] keep;

        public static PlayCorner Current { get; private set; }
        public static event System.Action<PlayCorner> Changed;

        public bool HoldsCamera { get; private set; } = true;
        public string ViewName => HoldsCamera && views != null && view >= 0 && view < views.Length ? views[view].name : null;
        public string LightName => moments != null && moment >= 0 && moment < moments.Length ? moments[moment].name : null;
        public string MoodName => moods != null && mood >= 0 && mood < moods.Length ? moods[mood].name : null;

        CameraShot shot;

        void Awake()
        {
            Current = this;
            // as the harness runs (PerfRunner): no cap, so the overlay's numbers are the harness's numbers (macOS still
            // presents on the display's refresh, so nothing tears)
            QualitySettings.vSyncCount = 0;
            Application.targetFrameRate = -1;
        }

        void Start() => Begin();

        void OnDestroy()
        {
            if (Current == this)
                Current = null;
            if (shot != null)
            {
                if (Application.isPlaying)
                    Destroy(shot);
                else
                    DestroyImmediate(shot);
            }
        }

        /// <summary>The town's globals, the birch's bounds and the first view, light and mood (also from the editor's stills).</summary>
        public void Begin()
        {
            for (int i = 0; boundsOf != null && i < boundsOf.Length; i++)
                if (boundsOf[i] != null)
                    boundsOf[i].localBounds = bounds[i];
            GrowthPack.Apply();
            WaterPack.Apply();
            Shader.SetGlobalFloat("_OS_NearForce", 0f);
            if (GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset urp)
                urp.shadowDistance = shadowDistance;
            HoldsCamera = true;
            Show();
        }

        public void SetView(int i)
        {
            if (views == null || views.Length == 0)
                return;
            view = Mathf.Clamp(i, 0, views.Length - 1);
            HoldsCamera = true;
            Show();
        }

        public void SetLight(int i)
        {
            if (moments == null || moments.Length == 0)
                return;
            moment = ((i % moments.Length) + moments.Length) % moments.Length;
            Show();
        }

        /// <summary>A mood by index, or none (neutral) for -1.</summary>
        public void SetMood(int i)
        {
            mood = moods == null || i < 0 || i >= moods.Length ? -1 : i;
            Show();
        }

        public void NextLight() => SetLight(moment + 1);

        /// <summary>The next mood, none after the last.</summary>
        public void NextMood() => SetMood(moods == null || mood + 1 >= moods.Length ? -1 : mood + 1);

        /// <summary>The camera is the walker's from now on: the views no longer place it until SetView.</summary>
        public void Release()
        {
            HoldsCamera = false;
            Show();
        }

        void Show()
        {
            if (stage == null)
                return;
            if (moments != null && moment >= 0 && moment < moments.Length)
                stage.rig = moments[moment].rig;
            stage.mood = moods != null && mood >= 0 && mood < moods.Length ? moods[mood].grade : null;
            if (HoldsCamera && views != null && view >= 0 && view < views.Length)
            {
                if (shot == null)
                    shot = ScriptableObject.CreateInstance<CameraShot>();
                var v = views[view];
                shot.position = v.position;
                shot.target = v.target;
                shot.verticalFov = v.fov;
                shot.near = 0.1f;
                shot.far = 9000f;
                stage.shot = shot;
            }
            else
            {
                stage.shot = null;
            }
            stage.Apply();
            FrameTimeOverlay.LightName = LightName;
            if (HoldsCamera)
                FrameTimeOverlay.ViewName = ViewName;
            FrameTimeOverlay.MoodName = MoodName;
            Changed?.Invoke(this);
        }
    }
}
