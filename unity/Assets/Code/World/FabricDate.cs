using UnityEngine;

namespace Overstory.World
{
    /// <summary>
    /// The fabric's date (docs/building-blocks.md: history is read from maps against the date; Shaders/History.hlsl):
    /// the one shader global every place and history layer is evaluated at, so a jump in time costs one uniform and no
    /// rebake. _OS_Date: x the year with the month as a fraction (January 1989 is 1989.0, July 1989.5), y the day of the
    /// year, z the hour, w reserved. Float32 throughout: a half holds 1989.5 as 1990, and no shader may read it so.
    /// The date is the world's, not the light's: a light rig keeps its own clock (_OS_Time).
    /// </summary>
    [ExecuteAlways]
    public class FabricDate : MonoBehaviour
    {
        public static readonly int Id = Shader.PropertyToID("_OS_Date");

        public int year = 1989;
        [Range(1, 12)] public int month = 1;
        [Tooltip("The day of the month.")]
        [Range(1, 31)] public int day = 1;
        [Range(0f, 24f)] public float hour = 12f;

        /// <summary>The global's value for a date (the day of the month clamped to the month's length).</summary>
        public static Vector4 Encode(int year, int month, int day, float hour)
        {
            month = Mathf.Clamp(month, 1, 12);
            day = Mathf.Clamp(day, 1, System.DateTime.DaysInMonth(year, month));
            return new Vector4(year + (month - 1) / 12f, new System.DateTime(year, month, day).DayOfYear, hour, 0f);
        }

        /// <summary>Sets the date and applies it.</summary>
        public void Set(int year, int month = 1, int day = 1, float hour = 12f)
        {
            this.year = year;
            this.month = month;
            this.day = day;
            this.hour = hour;
            Apply();
        }

        public void Apply() => Shader.SetGlobalVector(Id, Encode(year, month, day, hour));

        void OnEnable() => Apply();

        void OnValidate() => Apply();
    }
}
