using System;

namespace Overstory.Scenes
{
    /// <summary>
    /// Where the sun stands at a place, a date and a local hour (NOAA's solar position, with refraction near the
    /// horizon): a fact of the world, never typed into a rig by hand. Good to a fraction of a degree, 1900 to 2100.
    /// </summary>
    public static class Daylight
    {
        /// <summary>The sun's compass bearing (degrees from north, clockwise) and its elevation over the horizon.</summary>
        public static (double azimuth, double elevation) Sun(int year, int month, int day, double hour, double utcOffset,
                                                             double latitude, double longitude)
        {
            var midnight = new DateTime(year, month, day, 0, 0, 0, DateTimeKind.Utc);
            double utcHours = hour - utcOffset;
            double jd = (midnight - new DateTime(2000, 1, 1, 12, 0, 0, DateTimeKind.Utc)).TotalDays + utcHours / 24.0 + 2451545.0;
            double t = (jd - 2451545.0) / 36525.0;
            double l0 = Mod(280.46646 + t * (36000.76983 + t * 0.0003032), 360.0);
            double m = 357.52911 + t * (35999.05029 - 0.0001537 * t);
            double e = 0.016708634 - t * (0.000042037 + 0.0000001267 * t);
            double mr = Rad(m);
            double c = Math.Sin(mr) * (1.914602 - t * (0.004817 + 0.000014 * t)) + Math.Sin(2 * mr) * (0.019993 - 0.000101 * t)
                       + Math.Sin(3 * mr) * 0.000289;
            double omega = 125.04 - 1934.136 * t;
            double lambda = l0 + c - 0.00569 - 0.00478 * Math.Sin(Rad(omega));
            double eps0 = 23.0 + (26.0 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60.0) / 60.0;
            double eps = eps0 + 0.00256 * Math.Cos(Rad(omega));
            double dec = Deg(Math.Asin(Math.Sin(Rad(eps)) * Math.Sin(Rad(lambda))));
            double y = Math.Pow(Math.Tan(Rad(eps / 2.0)), 2);
            double l0r = Rad(l0);
            double eot = 4.0 * Deg(y * Math.Sin(2 * l0r) - 2 * e * Math.Sin(mr) + 4 * e * y * Math.Sin(mr) * Math.Cos(2 * l0r)
                                   - 0.5 * y * y * Math.Sin(4 * l0r) - 1.25 * e * e * Math.Sin(2 * mr));
            double trueSolar = Mod(utcHours * 60.0 + eot + 4.0 * longitude, 1440.0);
            double ha = Rad(trueSolar / 4.0 - 180.0);
            double la = Rad(latitude), de = Rad(dec);
            double cosZen = Math.Sin(la) * Math.Sin(de) + Math.Cos(la) * Math.Cos(de) * Math.Cos(ha);
            double elevation = 90.0 - Deg(Math.Acos(Math.Max(-1.0, Math.Min(1.0, cosZen))));
            double azimuth = Mod(Deg(Math.Atan2(Math.Sin(ha), Math.Cos(ha) * Math.Sin(la) - Math.Tan(de) * Math.Cos(la))) + 180.0, 360.0);
            if (elevation > -0.575) // the air lifts the sun a little near the horizon
                elevation += 1.02 / Math.Tan(Rad(elevation + 10.3 / (elevation + 5.11))) / 60.0;
            return (azimuth, elevation);
        }

        static double Rad(double d) => d * Math.PI / 180.0;
        static double Deg(double r) => r * 180.0 / Math.PI;
        static double Mod(double a, double b) => a - b * Math.Floor(a / b);
    }
}
