using System;
using System.Collections.Generic;
using UnityEngine;
using Overstory.Core;
using Overstory.World;

namespace Overstory.Scenes
{
    // The light record (schemas/light-record.schema.json; reviews/lt1/light/la-report.md, What L1 must hold) as
    // JsonUtility reads it: the inputs the derivation needs, and the derived block it writes. tools/light_record.py
    // writes the sources and the id; LightDerive writes derived.

    [Serializable] public class LightRecord
    {
        public int schemaVersion;
        public string id;
        public LightWorld world;
        public LightSources sources;
        public LightDerived derived;
    }

    [Serializable] public class LightWorld
    {
        public string pack;
        public YearMonth fabric;
        public int dayOfYear, timeOfDayS, instantMs;
        public LightWeather weather;
        public int latitudeMicrodeg, longitudeMicrodeg, utcOffsetMinutes;
    }

    [Serializable] public class YearMonth { public int year, month; }

    [Serializable] public class LightWeather
    {
        public int cover;
        public string precipitation;
        public int intensity, surfacesWet, haze;
        public string cloudKind;   // absent: stratocumulus
        public int cloudBaseMm;    // absent (0): the kind's own
        public int highCover;
        public LightFog fog;       // absent: visibilityMm 0, no fog
    }

    [Serializable] public class LightFog { public int visibilityMm, bankTopMm, overLand = -1, wisps = -1; }

    [Serializable] public class LightSources { public string fabric, people, pack, keys, function; }

    [Serializable] public class LightDerived
    {
        public LightSun sun;
        public LightSky sky;
        public LightAir air;
        public LightKeys keys;
        public string[] circuitsOn;
        public float exposureEv100;
        public LightMap[] maps;
    }

    [Serializable] public class LightSun { public int azimuthMillidegrees, elevationMillidegrees; public float illuminanceLux; public float[] rgb; }

    [Serializable] public class LightSky
    {
        public string model;
        public LightSkyParams @params;
        public float[] sh;          // 9 coefficients x rgb, Unity's world axes, candela per square metre
        public float illuminanceLux;
        public LightDome dome;
    }

    [Serializable] public class LightSkyParams { public float turbidity, overcast; public float[] groundAlbedo; }
    [Serializable] public class LightDome { public float[] zenith, horizon, towardSun, awayFromSun, deck; }
    [Serializable] public class LightAir { public float phaseG; public LightAirLayer[] layers; }
    [Serializable] public class LightAirLayer { public int toMm; public float density; public float[] rgb; }

    [Serializable] public class LightKeys
    {
        public int elevationMillidegrees;
        public float evening;
        public LightWeatherWeights weather;
        public LightPush[] pushes;
    }

    [Serializable] public class LightWeatherWeights { public float clear, overcast, fog; }
    [Serializable] public class LightPush { public string target; public float dL, dC, dh, dLog2, add; }
    [Serializable] public class LightMap { public string id, inputs; }

    // -- the pack's light tables (packs/<pack>/light/) ------------------------------------------------------------

    [Serializable] public class LightPack
    {
        public Atmosphere atmosphere;
        public Overcast overcast;
        public CloudKind[] cloudKinds;
        public Surfaces surfaces;
        public AirPack air;
        public Photocell photocell;
        public Rooms rooms;
        public ExposurePack exposure;
        public DomePack dome;
        public LensPack lens;
        [NonSerialized] public LampKind[] lampKinds;
        [NonSerialized] public KeyRow[] keys;
        [NonSerialized] public HashSet<string> terms;

        [Serializable] public class Atmosphere
        {
            public float planetRadiusM, topM, eyeM, rayleighScaleM, ozoneCentreM, ozoneHalfWidthM, aerosolScaleM;
            public float rayleighAt1um, ozoneColumnDu, spectrumFromNm, spectrumStepNm;
            public int spectralStepNm;
            public float[] solarIrradiance, ozoneCrossSectionM2;
            public float aerosolDepthClear, aerosolDepthPerHaze, aerosolAngstrom, aerosolAlbedo, aerosolG;
        }
        [Serializable] public class Overcast { public float loss, lossPower, neutralise; }
        [Serializable] public class CloudKind { public string kind; public int baseMm, topMm; public float sizeM, softness, sunThrough, sunLobe; }
        [Serializable] public class Surface { public float[] xy; public float albedo; }
        [Serializable] public class Surfaces { public Surface ground, town; public float wetDarkening, groundLitShare; }
        [Serializable] public class AirPack
        {
            public float koschmieder, heightFalloff, maxOpacity, middleM, farM, bankWispSizeM, townGlowHeightM;
            public float motesInFog, moteSize, shaftsPerHaze, beamHazePerHaze, beamReachM, beamFalloff;
            public int bankOverLand, bankWisps;
        }
        [Serializable] public class Photocell { public string[] circuits; public float onLux, offLux; }
        [Serializable] public class Rooms { public float windowCdPerM2, shopCdPerM2, spillCd; }
        [Serializable] public class ExposurePack { public float calibration, saturation; }
        [Serializable] public class DomePack { public float curve, glowPower; }
        [Serializable] public class LensPack { public float bloomIntensity, bloomThreshold; }
        [Serializable] public class LampKind { public string kind; public float[] xy; public float lumens, upward, glassCdPerM2, warmUpS, rangeM, fogShare; public float[] rendition; }
        [Serializable] public class KeyRow { public string weather, side; public int elevationMillidegrees; public LightPush[] pushes; }
        [Serializable] class LampKinds { public LampKind[] kinds; }
        [Serializable] class Keys { public KeyRow[] keys; }
        [Serializable] class Term { public string id; }
        [Serializable] class Terms { public Term[] terms; }

        /// <summary>The pack's light tables from their files' text, and the registry of terms.</summary>
        public static LightPack Read(string sky, string lampKinds, string keys, string terms)
        {
            var p = JsonUtility.FromJson<LightPack>(sky);
            p.lampKinds = JsonUtility.FromJson<LampKinds>(lampKinds).kinds;
            p.keys = JsonUtility.FromJson<Keys>(keys).keys;
            p.terms = new HashSet<string>();
            foreach (var t in JsonUtility.FromJson<Terms>(terms).terms)
                p.terms.Add(t.id);
            return p;
        }

        public CloudKind Cloud(string kind)
        {
            foreach (var c in cloudKinds)
                if (c.kind == (string.IsNullOrEmpty(kind) ? "stratocumulus" : kind))
                    return c;
            throw new ArgumentException($"no cloud kind {kind}");
        }
    }

    /// <summary>
    /// light-derive-1: the light at one instant from the world state and the pack (LA's thirteen points). The sun's
    /// place from the clock; its colour and illuminance through a spherical atmosphere (Rayleigh, a maritime aerosol,
    /// ozone); the clear sky by single scattering with Earth's shadow, blended with an overcast sky by the cloud; the
    /// sky's radiance as an L2 SH, from which the ambient, the dome and the air are views; the exposure from the light
    /// on open ground; the key set's pushes resolved by the sun's elevation, the evening and the weather. Every
    /// number that depends on the place, the era or the look is the pack's.
    /// </summary>
    public static class LightDerive
    {
        public const string Function = "light-derive-1";
        static readonly float[] Lambda = { 680f, 550f, 440f };

        public static LightDerived Derive(LightRecord r, LightPack p, float streetAxisCompass)
        {
            var w = r.world;
            var wx = w.weather;
            var date = new DateTime(w.fabric.year, 1, 1).AddDays(w.dayOfYear - 1);
            double hour = (w.timeOfDayS + w.instantMs / 1000.0) / 3600.0;
            double lat = w.latitudeMicrodeg / 1e6, lon = w.longitudeMicrodeg / 1e6, utc = w.utcOffsetMinutes / 60.0;
            var (az, el) = Daylight.Sun(date.Year, date.Month, date.Day, hour, utc, lat, lon);
            float elevation = (float)el;
            Vector3 toSun = SunVector(az, el, streetAxisCompass);

            // the weather's weights: fog by its visibility (1 at 500 m, none past 20 km), overcast by the cover
            float cover = wx.cover / 1000f, haze = wx.haze / 1000f;
            bool fog = wx.fog != null && wx.fog.visibilityMm > 0;
            float fogW = fog ? Mathf.Clamp01(Mathf.Log10(20000f / (wx.fog.visibilityMm / 1000f)) / Mathf.Log10(20000f / 500f)) : 0f;
            float overW = Mathf.SmoothStep(0f, 1f, Mathf.InverseLerp(0.4f, 0.95f, cover)) * (1f - fogW);
            var weights = new LightWeatherWeights { clear = 1f - overW - fogW, overcast = overW, fog = fogW };

            // the evening: 0 in the morning, 1 in the evening, a half at the day's highest and lowest points
            double b = 2.0 * Math.PI * (w.dayOfYear - 81) / 365.0;
            double eot = 9.87 * Math.Sin(2 * b) - 7.53 * Math.Cos(b) - 1.5 * Math.Sin(b);
            double solar = hour - utc + lon / 15.0 + eot / 60.0;
            float evening = (float)(0.5 + 0.5 * Math.Sin((solar - 12.0) * Math.PI / 12.0));
            int keyEl = Mathf.Max(-18000, Mathf.RoundToInt(elevation * 1000f));
            var pushes = Resolve(p, keyEl, evening, weights);

            // the atmosphere, and the sun through it
            var atm = Atmosphere.From(p.atmosphere, haze, p.surfaces.ground.albedo);
            Vector3 sunGround = atm.Rgb(atm.SunAt(atm.Eye, toSun));
            sunGround = Push(sunGround, pushes, "sun");
            float sunLux = Lum(sunGround);
            var kind = p.Cloud(wx.cloudKind);

            // the sky: single scattering (clear), the cloud deck (overcast), sampled on the upper hemisphere into an SH
            var sky = new SkyModel(atm, toSun, p, kind, cover, sunGround, elevation);
            var sh = new Vector3[9];
            Vector3 eUp = Vector3.zero;
            const int ne = 12, na = 32;
            for (int i = 0; i < ne; i++)
            {
                float e0 = (float)i / ne * Mathf.PI / 2, e1 = (float)(i + 1) / ne * Mathf.PI / 2;
                float e = (e0 + e1) / 2;
                float dOmega = (Mathf.Sin(e1) - Mathf.Sin(e0)) * (2f * Mathf.PI / na);
                for (int j = 0; j < na; j++)
                {
                    float a = (j + 0.5f) / na * 2f * Mathf.PI;
                    var d = new Vector3(Mathf.Cos(e) * Mathf.Cos(a), Mathf.Sin(e), Mathf.Cos(e) * Mathf.Sin(a));
                    Vector3 L = PushSky(sky.Radiance(d), pushes, e);
                    var y = Basis(d);
                    for (int k = 0; k < 9; k++)
                        sh[k] += L * (y[k] * dOmega);
                    eUp += L * (Mathf.Sin(e) * dOmega);
                }
            }
            float skyLux = Lum(eUp);

            // the light on open level ground, and the exposure an incident meter would give it, the keys' bias on top
            float sunH = Mathf.Max(0f, Mathf.Sin(elevation * Mathf.Deg2Rad)) * sunLux * ((1f - cover) + cover * kind.sunThrough);
            float groundLux = skyLux + sunH;
            Vector3 toSunGround = sunLux > 0f ? sunGround / sunLux * sunH : Vector3.zero;
            // an exposure push of -1 gives the picture one stop less light: one EV more
            float ev = Mathf.Log(Mathf.Max(groundLux, 1e-4f) * 100f / p.exposure.calibration, 2f) - Level(pushes, "exposure");

            // the air: the haze's extinction from the aerosol at the ground, fog's by Koschmieder; what it in-scatters
            // at full depth is the sky's horizon, the fog's the light all round it. The horizon is taken at right angles
            // to the sun, out of its lobe and the band opposite: the dome and the air add those as glows (sunGlow,
            // antiGlow, fogSun), so the side away from a low sun is not lit by the sun's aureole
            var across = Vector3.Cross(Vector3.up, toSun);
            if (across.sqrMagnitude < 1e-6f)
                across = Vector3.right;
            Vector3 horizon = (sky.Radiance(Flat(across, 0.0523f)) + sky.Radiance(Flat(-across, 0.0523f))) / 2f;
            horizon = PushSky(horizon, pushes, 3f * Mathf.Deg2Rad);
            float hazeDensity = atm.AerosolAtGround550 + atm.RayleighAtGround550;
            var nearAir = Push(horizon, pushes, "air");
            var farAir = Push(nearAir, pushes, "air.far");
            var layers = new List<LightAirLayer>
            {
                new LightAirLayer { toMm = Mathf.RoundToInt(p.air.middleM * 1000f), density = hazeDensity * Scale(pushes, "air"), rgb = Arr(nearAir) },
                new LightAirLayer { toMm = Mathf.RoundToInt(p.air.farM * 1000f), density = hazeDensity * Scale(pushes, "air"), rgb = Arr(Vector3.Lerp(nearAir, farAir, 0.5f)) },
                new LightAirLayer { toMm = Mathf.RoundToInt(p.air.farM * 1000f), density = hazeDensity * Scale(pushes, "air.far"), rgb = Arr(farAir) },
            };
            if (fog)
            {
                // a droplet scatters the mean radiance round it: the sky's E / pi over the upper half, the lit
                // ground's over the lower, so (E_up + E_down) / 2 pi
                Vector3 eDown = Mul(sky.GroundAlbedo, eUp + toSunGround);
                Vector3 inFog = (eUp + eDown) / (2f * Mathf.PI);
                layers.Add(new LightAirLayer { toMm = wx.fog.bankTopMm, density = p.air.koschmieder / (wx.fog.visibilityMm / 1000f) * Scale(pushes, "fog"), rgb = Arr(Push(inFog, pushes, "air")) });
            }

            // the street circuits: on below the photocells' threshold
            var circuits = groundLux < p.photocell.onLux ? p.photocell.circuits : new string[0];

            float azM = Mathf.Repeat((float)az, 360f);
            return new LightDerived
            {
                sun = new LightSun
                {
                    azimuthMillidegrees = Mathf.RoundToInt(azM * 1000f) % 360000,
                    elevationMillidegrees = Mathf.RoundToInt(elevation * 1000f),
                    illuminanceLux = elevation > -0.27f ? sunLux : 0f,
                    rgb = Arr(sunLux > 0f ? sunGround / sunLux : Vector3.one),
                },
                sky = new LightSky
                {
                    model = "single-scatter-1",
                    @params = new LightSkyParams { turbidity = atm.Turbidity, overcast = cover, groundAlbedo = Arr(sky.GroundAlbedo) },
                    sh = Flat(sh),
                    illuminanceLux = skyLux,
                    dome = new LightDome
                    {
                        zenith = Arr(PushSky(sky.Clear(Vector3.up), pushes, Mathf.PI / 2)),
                        horizon = Arr(horizon),
                        towardSun = Arr(PushSky(sky.Radiance(Flat(toSun, 0.0523f)), pushes, 3f * Mathf.Deg2Rad)),
                        awayFromSun = Arr(PushSky(sky.Radiance(Flat(-toSun, 0.0873f)), pushes, 5f * Mathf.Deg2Rad)),
                        deck = Arr(PushSky(sky.Deck(Vector3.up), pushes, Mathf.PI / 2)),
                    },
                },
                air = new LightAir { phaseG = p.atmosphere.aerosolG, layers = layers.ToArray() },
                keys = new LightKeys { elevationMillidegrees = keyEl, evening = evening, weather = weights, pushes = pushes.ToArray() },
                circuitsOn = circuits,
                exposureEv100 = ev,
                maps = new[]
                {
                    new LightMap { id = "height-sky", inputs = Hex(Hash.Of("height-sky", r.sources.fabric)) },
                    new LightMap { id = "cloud", inputs = Hex(Hash.Of(Hash.Of("cloud", (ulong)wx.cover), Hash.Of(wx.cloudKind ?? "", (ulong)(w.timeOfDayS * 1000L + w.instantMs)))) },
                },
            };
        }

        // -- the rig: the record as the stage and the shaders read it -----------------------------------------------

        /// <summary>
        /// Fills a rig from a record's derived block: every quantity in display units, the record's exposure applied
        /// (a lux becomes u = 1 / (pi * saturation * 2^EV100), a candela per square metre pi * u), so a white face
        /// at the saturation luminance reads 1. Colours the rig holds in gamma are converted; nothing is clamped.
        /// glassKind is the lamp kind whose glass the town's lamps show (one emission for all).
        /// </summary>
        public static void ToRig(LightRecord rec, LightPack p, LightRig r, string glassKind)
        {
            var d = rec.derived;
            var w = rec.world;
            var wx = w.weather;
            var pushes = d.keys.pushes;
            float u = 1f / (Mathf.PI * p.exposure.saturation * Mathf.Pow(2f, d.exposureEv100)), k = Mathf.PI * u;

            // the clock and the sun, from the record, never again from the rig's own clock
            var date = new DateTime(w.fabric.year, 1, 1).AddDays(w.dayOfYear - 1);
            r.year = date.Year; r.month = date.Month; r.day = date.Day;
            r.hour = (w.timeOfDayS + w.instantMs / 1000f) / 3600f;
            r.utcOffset = w.utcOffsetMinutes / 60f;
            r.latitude = w.latitudeMicrodeg / 1e6f; r.longitude = w.longitudeMicrodeg / 1e6f;
            r.sunFromClock = false;
            float az = d.sun.azimuthMillidegrees / 1000f, el = d.sun.elevationMillidegrees / 1000f;
            r.sunBearing = Mathf.Repeat(r.streetAxisCompass - az, 360f);
            r.sunElevation = el;
            Vector3 sunRgb = Vec(d.sun.rgb);
            r.sunColour = G(sunRgb);
            r.sunIntensity = d.sun.illuminanceLux * u;
            r.shadowStrength = 1f;

            // the cloud: the sun's light under it is the kind's
            var kind = p.Cloud(wx.cloudKind);
            float cover = wx.cover / 1000f;
            r.cloudCover = cover;
            r.cloudSize = kind.sizeM;
            r.cloudSoftness = kind.softness;
            r.cloudHeight = (wx.cloudBaseMm > 0 ? wx.cloudBaseMm : kind.baseMm) / 1000f;
            r.cloudSunThrough = kind.sunThrough;
            r.highCloud = wx.highCover / 1000f;
            float through = (1f - cover) + cover * kind.sunThrough;

            // the dome: views of the sky's model
            var dome = d.sky.dome;
            Vector3 hz = Vec(dome.horizon);
            r.zenith = G(Vec(dome.zenith) * k);
            r.horizon = G(hz * k);
            r.deck = G(Vec(dome.deck) * k);
            r.sunGlow = G(Max0(Vec(dome.towardSun) - hz) * k);
            r.antiGlow = G(Max0(Vec(dome.awayFromSun) - hz) * k);
            r.skyCurve = p.dome.curve;
            r.sunGlowPower = p.dome.glowPower;

            // the ambient: the sky's SH on faces up and round the horizon; the ground and the town give back theirs
            Vector3 toSun = SunVector(az, el, r.streetAxisCompass);
            var toward = new Vector3(toSun.x, 0f, toSun.z).normalized;
            var across = Vector3.Cross(Vector3.up, toward);
            Vector3 eUp = Irradiance(d.sky.sh, Vector3.up), eAcross = Irradiance(d.sky.sh, across), eToward = Irradiance(d.sky.sh, toward);
            Vector3 sun = sunRgb * d.sun.illuminanceLux;
            float sinEl = Mathf.Max(0f, Mathf.Sin(el * Mathf.Deg2Rad)), cosEl = Mathf.Cos(el * Mathf.Deg2Rad);
            float wet = wx.surfacesWet / 1000f;
            Vector3 groundAlbedo = XyToRgb(p.surfaces.ground.xy) * (p.surfaces.ground.albedo * (1f - p.surfaces.wetDarkening * wet));
            Vector3 townAlbedo = XyToRgb(p.surfaces.town.xy) * p.surfaces.town.albedo;
            float lit = p.surfaces.groundLitShare;
            r.belowHorizon = G(Mul(groundAlbedo, eUp + sun * (sinEl * through)) * u);
            r.ambientSky = G(eUp * u);
            r.ambientEquator = G(eAcross * u);
            var side = G(eToward * u);
            side.a = 1f;
            r.ambientSunSide = side;
            r.ambientGround = G(Mul(groundAlbedo, eUp) * u);
            r.sunBounce = Lum(groundAlbedo) * lit * through;
            // a facade across the street: the sky on a wall, and the sun on the walls that face it (cos el / pi on average)
            r.townBounce = G(Mul(townAlbedo, eAcross + sun * (cosEl / Mathf.PI * through * lit)) * u);
            r.ambientIntensity = 1f;

            // the air, near to far, then the fog bank
            var L = d.air.layers;
            r.fogDensity = L[0].density;
            r.fogColour = G(Vec(L[0].rgb) * k);
            r.fogMidColour = G(Vec(L[1].rgb) * k);
            r.fogMidDistance = L[0].toMm / 1000f;
            r.fogFarColour = G(Vec(L[2].rgb) * k);
            r.fogFarDistance = L[1].toMm / 1000f;
            r.fogHeightFalloff = p.air.heightFalloff;
            r.fogBaseHeight = 0f;
            r.fogMaxOpacity = p.air.maxOpacity;
            r.fogSunColour = r.sunGlow;
            r.fogSunPower = 2f / Mathf.Max(1f - d.air.phaseG, 0.05f); // the forward lobe's width, from the aerosol's g
            bool fog = L.Length > 3;
            r.fogBank = fog;
            r.hazeDensity = fog ? L[3].density : 0f;
            r.hazeHeight = fog ? L[3].toMm / 1000f : 20f;
            r.hazeColour = fog ? G(Vec(L[3].rgb) * k) : r.fogColour;
            r.bankOverLand = (fog && wx.fog.overLand >= 0 ? wx.fog.overLand : p.air.bankOverLand) / 1000f;
            r.bankWisps = (fog && wx.fog.wisps >= 0 ? wx.fog.wisps : p.air.bankWisps) / 1000f;
            r.bankWispSize = p.air.bankWispSizeM;
            // the town's light in the air: a lamp's intensity I lights the air about H above it with I / H^2, which
            // scatters a quarter of it (in display units) towards the eye per unit of optical depth
            r.townGlowHeight = p.air.townGlowHeightM;
            r.townGlow = Scale(pushes, "town") / (4f * r.townGlowHeight * r.townGlowHeight);
            float haze = wx.haze / 1000f;
            r.shafts = el > 0f ? p.air.shaftsPerHaze * haze * (1f - cover) * Scale(pushes, "shafts") : 0f;
            r.beamHaze = p.air.beamHazePerHaze * haze;
            r.beamReach = p.air.beamReachM;
            r.beamFalloff = p.air.beamFalloff;
            r.motes = p.air.motesInFog * d.keys.weather.fog * Scale(pushes, "motes");
            r.moteSize = p.air.moteSize;
            r.wetness = wet;

            // the lamps by kind, the rooms, the halo
            r.lampsOn = d.circuitsOn != null && d.circuitsOn.Length > 0;
            r.lampIntensity = 1f;
            float lamps = Scale(pushes, "lamps");
            var kinds = new List<LightRig.LampLight>();
            LightPack.LampKind glass = null;
            foreach (var lk in p.lampKinds)
            {
                // the light below the lamp: the share that is not thrown up, spread over the lower hemisphere
                float cd = lk.lumens * (1f - lk.upward) / (2f * Mathf.PI);
                kinds.Add(new LightRig.LampLight { kind = lk.kind, colour = G(XyToRgb(lk.xy)), intensity = cd * u * lamps, range = lk.rangeM, fogShare = lk.fogShare });
                if (lk.kind == glassKind)
                    glass = lk;
            }
            r.lampKinds = kinds.ToArray();
            r.lampGlow = glass != null ? glass.glassCdPerM2 * k * lamps : 0f;
            r.windowGlow = p.rooms.windowCdPerM2 * k * Scale(pushes, "windows");
            r.windowSpill = p.rooms.spillCd * u;
            r.lampHalo = Mathf.PI * Scale(pushes, "halo"); // the halo's integral gives radiance; pi * u is its display

            // the grade: the hour's balance only; the exposure is already in every value
            r.postExposure = 0f;
            r.contrast = Setting(pushes, "grade.contrast");
            r.saturation = Setting(pushes, "grade.saturation");
            r.temperature = Setting(pushes, "grade.temperature");
            r.tint = 0f;
            r.colourFilter = Color.white;
            r.bloomIntensity = p.lens.bloomIntensity * Scale(pushes, "bloom");
            r.bloomThreshold = p.lens.bloomThreshold;
        }

        static Color G(Vector3 linear) => new Color(linear.x, linear.y, linear.z, 1f).gamma;

        /// <summary>Two derived blocks as JSON agree when their text matches and every number is within a relative
        /// tolerance: the record is checked on load, never trusted or rewritten for a rounding.</summary>
        public static bool Close(string a, string b, float tolerance = 1e-4f)
        {
            var num = new System.Text.RegularExpressions.Regex(@"-?\d+(\.\d+)?([eE][-+]?\d+)?");
            var ma = num.Matches(a);
            var mb = num.Matches(b);
            if (ma.Count != mb.Count || num.Replace(a, "#") != num.Replace(b, "#"))
                return false;
            for (int i = 0; i < ma.Count; i++)
            {
                double x = double.Parse(ma[i].Value, System.Globalization.CultureInfo.InvariantCulture);
                double y = double.Parse(mb[i].Value, System.Globalization.CultureInfo.InvariantCulture);
                if (Math.Abs(x - y) > tolerance * Math.Max(1.0, Math.Max(Math.Abs(x), Math.Abs(y))))
                    return false;
            }
            return true;
        }

        // -- the key set ---------------------------------------------------------------------------------------------

        /// <summary>The pushes at this elevation, evening and weather: each regime's rows interpolated by elevation,
        /// morning and evening blended, the regimes weighted. A push on a term the registry lacks is refused.</summary>
        static List<LightPush> Resolve(LightPack p, int el, float evening, LightWeatherWeights w)
        {
            var sum = new Dictionary<string, LightPush>();
            void Add(string weather, float weight)
            {
                if (weight <= 0f)
                    return;
                foreach (var (side, sw) in new[] { ("morning", 1f - evening), ("evening", evening) })
                {
                    var rows = new List<LightPack.KeyRow>();
                    foreach (var k in p.keys)
                        if (k.weather == weather && (k.side == side || k.side == "both"))
                            rows.Add(k);
                    rows.Sort((a, b) => a.elevationMillidegrees.CompareTo(b.elevationMillidegrees));
                    if (rows.Count == 0)
                        continue;
                    int hi = rows.FindIndex(k => k.elevationMillidegrees >= el);
                    LightPack.KeyRow r0, r1;
                    if (hi < 0) r0 = r1 = rows[rows.Count - 1];
                    else if (hi == 0) r0 = r1 = rows[0];
                    else { r0 = rows[hi - 1]; r1 = rows[hi]; }
                    float t = r0 == r1 ? 0f : Mathf.InverseLerp(r0.elevationMillidegrees, r1.elevationMillidegrees, el);
                    foreach (var (row, rw) in new[] { (r0, 1f - t), (r1, t) })
                        foreach (var push in row.pushes)
                        {
                            if (!p.terms.Contains(push.target))
                                throw new ArgumentException($"key push on {push.target}, not in schemas/light-terms.json");
                            float f = weight * sw * rw;
                            if (!sum.TryGetValue(push.target, out var s))
                                sum[push.target] = s = new LightPush { target = push.target };
                            s.dL += push.dL * f; s.dC += push.dC * f; s.dh += push.dh * f; s.dLog2 += push.dLog2 * f; s.add += push.add * f;
                        }
                }
            }
            Add("clear", w.clear);
            Add("overcast", w.overcast);
            Add("fog", w.fog);
            var list = new List<LightPush>(sum.Values);
            list.Sort((a, b) => string.CompareOrdinal(a.target, b.target));
            return list;
        }

        public static LightPush Find(IEnumerable<LightPush> pushes, string target)
        {
            foreach (var p in pushes)
                if (p.target == target)
                    return p;
            return null;
        }

        public static float Level(IEnumerable<LightPush> pushes, string target) => Find(pushes, target)?.dLog2 ?? 0f;
        public static float Scale(IEnumerable<LightPush> pushes, string target) => Mathf.Pow(2f, Level(pushes, target));
        public static float Setting(IEnumerable<LightPush> pushes, string target) => Find(pushes, target)?.add ?? 0f;

        /// <summary>A colour pushed in OKLCH (its lightness, chroma and hue) and scaled by 2^dLog2.</summary>
        public static Vector3 Push(Vector3 rgb, IEnumerable<LightPush> pushes, string target)
        {
            var p = Find(pushes, target);
            if (p == null)
                return rgb;
            float y = Lum(rgb);
            if (y > 0f && (p.dL != 0f || p.dC != 0f || p.dh != 0f))
            {
                // the push acts on the colour at unit luminance, so a level and a hue never trade
                var c = ToOklch(rgb / y);
                c.x = Mathf.Max(0f, c.x + p.dL);
                c.y = Mathf.Max(0f, c.y + p.dC);
                c.z += p.dh;
                var o = FromOklch(c);
                rgb = Max0(o) * y;
            }
            return rgb * Mathf.Pow(2f, p.dLog2);
        }

        static Vector3 PushSky(Vector3 L, List<LightPush> pushes, float elevation)
        {
            L = Push(L, pushes, "sky");
            float up = Mathf.Clamp01(Mathf.Sin(elevation));
            var z = Push(L, pushes, "sky.zenith");
            var h = Push(L, pushes, "sky.horizon");
            return L + (z - L) * up + (h - L) * (1f - up);
        }

        // -- the atmosphere --------------------------------------------------------------------------------------

        /// <summary>
        /// A spherical atmosphere, rendered spectrally (Bruneton 2017, whose tables the pack holds): Rayleigh by
        /// lambda^-4, a maritime aerosol by its Angstrom exponent, ozone by its cross-section in a tent at 25 km; the
        /// solar spectrum at the top. Light is carried on wavelengths from 380 to 780 nm and only turned into colour
        /// at the end (CIE 1931), since twilight's blue is ozone's Chappuis band, which three wavelengths miss.
        /// </summary>
        internal class Atmosphere
        {
            public float R, Top, HR, HA, OzC, OzW, G, Turbidity, AerosolAtGround550, RayleighAtGround550, GroundAlbedo;
            public Vector3 Eye;
            public int W;
            public double[] Lambda, Ray, Oz, AerExt, AerSca, Sun;
            double[,] cmf;
            // the multiple-scattering transfer (Hillaire 2020) by height and the sun's cosine there
            static readonly float[] MsHeights = { 0f, 1000f, 3000f, 6000f, 10000f, 16000f, 25000f, 40000f, 60000f };
            static readonly float[] MsSunDeg = { -20f, -12f, -8f, -5f, -3f, -1f, 0f, 2f, 5f, 10f, 20f, 40f, 90f };
            double[,][] ms;

            public static Atmosphere From(LightPack.Atmosphere a, float haze, float groundAlbedo)
            {
                var m = new Atmosphere { R = a.planetRadiusM, Top = a.planetRadiusM + a.topM, HR = a.rayleighScaleM, HA = a.aerosolScaleM,
                                         OzC = a.ozoneCentreM, OzW = a.ozoneHalfWidthM, G = a.aerosolG, GroundAlbedo = groundAlbedo };
                m.Eye = new Vector3(0f, a.planetRadiusM + a.eyeM, 0f);
                m.Turbidity = a.aerosolDepthClear + haze * a.aerosolDepthPerHaze;
                var lambdas = new List<double>();
                for (int l = 380; l <= 780; l += a.spectralStepNm)
                    lambdas.Add(l);
                m.W = lambdas.Count;
                m.Lambda = lambdas.ToArray();
                m.Ray = new double[m.W]; m.Oz = new double[m.W]; m.AerExt = new double[m.W]; m.AerSca = new double[m.W]; m.Sun = new double[m.W];
                m.cmf = new double[m.W, 3];
                // the ozone layer's peak number density: the column (Dobson units) spread over the tent
                double ozPeak = a.ozoneColumnDu * 2.687e20 / a.ozoneHalfWidthM;
                for (int c = 0; c < m.W; c++)
                {
                    double l = m.Lambda[c];
                    m.Ray[c] = a.rayleighAt1um / Math.Pow(l / 1000.0, 4.0);
                    m.Oz[c] = Table(a.ozoneCrossSectionM2, a.spectrumFromNm, a.spectrumStepNm, l) * ozPeak;
                    m.AerExt[c] = m.Turbidity / a.aerosolScaleM * Math.Pow(l / 550.0, -a.aerosolAngstrom);
                    m.AerSca[c] = m.AerExt[c] * a.aerosolAlbedo;
                    m.Sun[c] = Table(a.solarIrradiance, a.spectrumFromNm, a.spectrumStepNm, l);
                    for (int k = 0; k < 3; k++)
                        m.cmf[c, k] = Cie1931(l, k);
                }
                m.AerosolAtGround550 = m.Turbidity / a.aerosolScaleM;
                m.RayleighAtGround550 = (float)(a.rayleighAt1um / Math.Pow(0.55, 4.0));
                m.BuildMultipleScattering();
                return m;
            }

            static double Table(float[] t, float from, float step, double l)
            {
                double x = (l - from) / step;
                int i = Mathf.Clamp((int)Math.Floor(x), 0, t.Length - 2);
                double f = Math.Min(1.0, Math.Max(0.0, x - i));
                return t[i] * (1.0 - f) + t[i + 1] * f;
            }

            /// <summary>Spectral radiance or irradiance (W per square metre per nm, per sr) as linear Rec.709 in
            /// candela per square metre or lux: 683 lm/W times the CIE 1931 matching functions.</summary>
            public Vector3 Rgb(double[] s)
            {
                double X = 0, Y = 0, Z = 0, dl = Lambda.Length > 1 ? Lambda[1] - Lambda[0] : 10.0;
                for (int c = 0; c < W; c++)
                {
                    X += s[c] * cmf[c, 0]; Y += s[c] * cmf[c, 1]; Z += s[c] * cmf[c, 2];
                }
                X *= 683.0 * dl; Y *= 683.0 * dl; Z *= 683.0 * dl;
                return Max0(new Vector3((float)(3.2406 * X - 1.5372 * Y - 0.4986 * Z), (float)(-0.9689 * X + 1.8758 * Y + 0.0415 * Z),
                                        (float)(0.0557 * X - 0.2040 * Y + 1.0570 * Z)));
            }

            public (double r, double a, double o) Density(double h) =>
                (Math.Exp(-h / HR), Math.Exp(-h / HA), Math.Max(0.0, 1.0 - Math.Abs(h - OzC) / OzW));

            void Extinction(double h, double[] e)
            {
                var (r, a, o) = Density(h);
                for (int c = 0; c < W; c++)
                    e[c] = Ray[c] * r + AerExt[c] * a + Oz[c] * o;
            }

            /// <summary>Light's transmittance from p along d to the top, 0 where the planet is in the way. A grazing
            /// path is densest where it passes closest to the ground, so the steps crowd there.</summary>
            public double[] Transmittance(Vector3 p, Vector3 d, int n = 16)
            {
                var T = new double[W];
                if (Hits(p, d, R))
                    return T;
                float t = Exit(p, d, Top), near = Mathf.Clamp(-Vector3.Dot(p, d), 0f, t);
                var tau = new double[W];
                var e = new double[W];
                void Segment(float a, float b, bool crowdAtEnd, int m)
                {
                    float L = b - a;
                    for (int i = 0; i < m; i++)
                    {
                        float f0 = (float)i / m * i / m, f1 = (float)(i + 1) / m * (i + 1) / m;
                        float s0 = crowdAtEnd ? b - L * f1 : a + L * f0, s1 = crowdAtEnd ? b - L * f0 : a + L * f1;
                        var q = p + d * ((s0 + s1) / 2f);
                        Extinction(q.magnitude - R, e);
                        for (int c = 0; c < W; c++)
                            tau[c] += e[c] * (s1 - s0);
                    }
                }
                if (near > 0f)
                {
                    Segment(0f, near, true, n / 2);
                    Segment(near, t, false, n / 2);
                }
                else
                    Segment(0f, t, false, n);
                for (int c = 0; c < W; c++)
                    T[c] = Math.Exp(-tau[c]);
                return T;
            }

            /// <summary>The sun's irradiance (spectral) arriving at p, through the air.</summary>
            public double[] SunAt(Vector3 p, Vector3 toSun)
            {
                var T = Transmittance(p, toSun, 24);
                for (int c = 0; c < W; c++)
                    T[c] *= Sun[c];
                return T;
            }

            /// <summary>The sky's spectral radiance along d from the eye: single scattering of the sun (Rayleigh and
            /// aerosol phases) plus the multiple-scattering transfer, each through the air between.</summary>
            public double[] Radiance(Vector3 d, Vector3 toSun, int n = 32) => Radiance(Eye, d, toSun, n);

            /// <summary>The same from a point p (from the planet's centre).</summary>
            public double[] Radiance(Vector3 p, Vector3 d, Vector3 toSun, int n = 32)
            {
                float t = Exit(p, d, Top);
                double mu = Vector3.Dot(d, toSun);
                double phaseR = 3.0 / (16.0 * Math.PI) * (1.0 + mu * mu);
                double phaseA = (1.0 - G * G) / (4.0 * Math.PI * Math.Pow(Math.Max(1e-4, 1.0 + G * G - 2.0 * G * mu), 1.5));
                var tau = new double[W];
                var sum = new double[W];
                var e = new double[W];
                for (int i = 0; i < n; i++)
                {
                    float s0 = t * i / n * i / n, s1 = t * (i + 1) / n * (i + 1) / n, ds = s1 - s0;
                    var q = p + d * ((s0 + s1) / 2f);
                    float rq = q.magnitude;
                    double h = rq - R;
                    Extinction(h, e);
                    var T = Transmittance(q, toSun);
                    var psi = MultipleAt((float)h, Vector3.Dot(q / rq, toSun));
                    var (rd, ad, _) = Density(h);
                    for (int c = 0; c < W; c++)
                    {
                        double sca = Ray[c] * rd + AerSca[c] * ad;
                        double view = Math.Exp(-(tau[c] + e[c] * ds / 2.0));
                        sum[c] += ((Ray[c] * rd * phaseR + AerSca[c] * ad * phaseA) * T[c] + sca * psi[c]) * view * ds;
                        tau[c] += e[c] * ds;
                    }
                }
                for (int c = 0; c < W; c++)
                    sum[c] *= Sun[c];
                return sum;
            }

            /// <summary>Hillaire's (2020) multiple-scattering LUT: at each height and sun angle, the second order of
            /// light from every direction (isotropic, the ground lit by the sun included), summed to infinite order
            /// as a geometric series 1 / (1 - f).</summary>
            void BuildMultipleScattering()
            {
                const int dirs = 32, steps = 8;
                var w = new Vector3[dirs];
                for (int i = 0; i < dirs; i++)
                {
                    float z = 1f - 2f * (i + 0.5f) / dirs, r = Mathf.Sqrt(1f - z * z), ph = i * Mathf.PI * (3f - Mathf.Sqrt(5f));
                    w[i] = new Vector3(r * Mathf.Cos(ph), z, r * Mathf.Sin(ph));
                }
                ms = new double[MsHeights.Length, MsSunDeg.Length][];
                var e = new double[W];
                for (int hi = 0; hi < MsHeights.Length; hi++)
                    for (int si = 0; si < MsSunDeg.Length; si++)
                    {
                        var x = new Vector3(0f, R + MsHeights[hi], 0f);
                        float sd = MsSunDeg[si] * Mathf.Deg2Rad;
                        var sun = new Vector3(Mathf.Cos(sd), Mathf.Sin(sd), 0f);
                        var L = new double[W];
                        var F = new double[W];
                        foreach (var dir in w)
                        {
                            bool ground = Hits(x, dir, R);
                            float t;
                            if (ground)
                            {
                                float b = Vector3.Dot(x, dir), c2 = x.sqrMagnitude - R * R;
                                t = -b - Mathf.Sqrt(Mathf.Max(0f, b * b - c2));
                            }
                            else
                                t = Exit(x, dir, Top);
                            var tau = new double[W];
                            for (int i = 0; i < steps; i++)
                            {
                                float s0 = t * i / steps * i / steps, s1 = t * (i + 1) / steps * (i + 1) / steps, ds = s1 - s0;
                                var q = x + dir * ((s0 + s1) / 2f);
                                double h = q.magnitude - R;
                                Extinction(h, e);
                                var Ts = Transmittance(q, sun, 12);
                                var (rd, ad, _) = Density(h);
                                for (int c = 0; c < W; c++)
                                {
                                    double sca = Ray[c] * rd + AerSca[c] * ad;
                                    double view = Math.Exp(-(tau[c] + e[c] * ds / 2.0));
                                    L[c] += view * sca * Ts[c] * ds / (4.0 * Math.PI);
                                    F[c] += view * sca * ds;
                                    tau[c] += e[c] * ds;
                                }
                            }
                            if (ground)
                            {
                                var g = x + dir * t;
                                float mug = Vector3.Dot(g.normalized, sun);
                                if (mug > 0f)
                                {
                                    var Ts = Transmittance(g, sun, 12);
                                    for (int c = 0; c < W; c++)
                                        L[c] += Math.Exp(-tau[c]) * Ts[c] * mug * GroundAlbedo / Math.PI;
                                }
                            }
                        }
                        var psi = new double[W];
                        for (int c = 0; c < W; c++)
                            psi[c] = L[c] / dirs / Math.Max(1e-6, 1.0 - F[c] / dirs);
                        ms[hi, si] = psi;
                    }
            }

            double[] MultipleAt(float h, float muSun)
            {
                float deg = Mathf.Asin(Mathf.Clamp(muSun, -1f, 1f)) * Mathf.Rad2Deg;
                var (i, a) = Bracket(MsHeights, h);
                var (j, b) = Bracket(MsSunDeg, deg);
                var o = new double[W];
                for (int c = 0; c < W; c++)
                    o[c] = (1 - a) * (1 - b) * ms[i, j][c] + a * (1 - b) * ms[i + 1, j][c] + (1 - a) * b * ms[i, j + 1][c] + a * b * ms[i + 1, j + 1][c];
                return o;
            }

            static (int, float) Bracket(float[] xs, float x)
            {
                if (x <= xs[0]) return (0, 0f);
                if (x >= xs[xs.Length - 1]) return (xs.Length - 2, 1f);
                int i = 0;
                while (x > xs[i + 1]) i++;
                return (i, (x - xs[i]) / (xs[i + 1] - xs[i]));
            }

            public static bool Hits(Vector3 p, Vector3 d, float radius)
            {
                float b = Vector3.Dot(p, d), c = p.sqrMagnitude - radius * radius;
                return b < 0f && b * b - c > 0f;
            }

            public static float Exit(Vector3 p, Vector3 d, float radius)
            {
                float b = Vector3.Dot(p, d), c = p.sqrMagnitude - radius * radius;
                return -b + Mathf.Sqrt(Mathf.Max(0f, b * b - c));
            }

            // CIE 1931 2-degree colour matching functions, 380 to 780 nm by 10 (x, y, z)
            static readonly float[] Cmf =
            {
                0.0014f, 0.0000f, 0.0065f, 0.0042f, 0.0001f, 0.0201f, 0.0143f, 0.0004f, 0.0679f, 0.0435f, 0.0012f, 0.2074f,
                0.1344f, 0.0040f, 0.6456f, 0.2839f, 0.0116f, 1.3856f, 0.3483f, 0.0230f, 1.7471f, 0.3362f, 0.0380f, 1.7721f,
                0.2908f, 0.0600f, 1.6692f, 0.1954f, 0.0910f, 1.2876f, 0.0956f, 0.1390f, 0.8130f, 0.0320f, 0.2080f, 0.4652f,
                0.0049f, 0.3230f, 0.2720f, 0.0093f, 0.5030f, 0.1582f, 0.0633f, 0.7100f, 0.0782f, 0.1655f, 0.8620f, 0.0422f,
                0.2904f, 0.9540f, 0.0203f, 0.4334f, 0.9950f, 0.0087f, 0.5945f, 0.9950f, 0.0039f, 0.7621f, 0.9520f, 0.0021f,
                0.9163f, 0.8700f, 0.0017f, 1.0263f, 0.7570f, 0.0011f, 1.0622f, 0.6310f, 0.0008f, 1.0026f, 0.5030f, 0.0003f,
                0.8544f, 0.3810f, 0.0002f, 0.6424f, 0.2650f, 0.0000f, 0.4479f, 0.1750f, 0.0000f, 0.2835f, 0.1070f, 0.0000f,
                0.1649f, 0.0610f, 0.0000f, 0.0874f, 0.0320f, 0.0000f, 0.0468f, 0.0170f, 0.0000f, 0.0227f, 0.0082f, 0.0000f,
                0.0114f, 0.0041f, 0.0000f, 0.0058f, 0.0021f, 0.0000f, 0.0029f, 0.0010f, 0.0000f, 0.0014f, 0.0005f, 0.0000f,
                0.0007f, 0.0002f, 0.0000f, 0.0003f, 0.0001f, 0.0000f, 0.0002f, 0.0001f, 0.0000f, 0.0001f, 0.0000f, 0.0000f,
                0.0000f, 0.0000f, 0.0000f,
            };

            static double Cie1931(double l, int k)
            {
                double x = (l - 380.0) / 10.0;
                int i = Mathf.Clamp((int)Math.Floor(x), 0, 39);
                double f = Math.Min(1.0, Math.Max(0.0, x - i));
                return Cmf[3 * i + k] * (1.0 - f) + Cmf[3 * (i + 1) + k] * f;
            }
        }

        /// <summary>The sky's radiance by direction (candela per square metre, linear Rec.709): the clear sky from the
        /// atmosphere, and the cloud deck by the CIE overcast gradient, lit by the clear sky above it and dimmed by
        /// the cover as Kasten and Czeplak found (1 - loss N^power of the clear light reaches the ground).</summary>
        internal class SkyModel
        {
            readonly Atmosphere atm;
            readonly Vector3 toSun;
            readonly float cover, lobe, deckZenith;
            readonly Vector3 deckColour;
            public readonly Vector3 GroundAlbedo;

            public SkyModel(Atmosphere atm, Vector3 toSun, LightPack p, LightPack.CloudKind kind, float cover, Vector3 sunGround, float elevation)
            {
                this.atm = atm;
                this.toSun = toSun;
                this.cover = cover;
                lobe = kind.sunLobe;
                GroundAlbedo = XyToRgb(p.surfaces.ground.xy) * p.surfaces.ground.albedo;
                // the deck is lit at its top by the sun and the clear sky above it, over most of the haze: its colour;
                // its level is Kasten and Czeplak's, measured against the clear light on the ground
                float y = Lum(Global(atm.Eye, sunGround));
                var top = kind.topMm > 0 ? new Vector3(0f, atm.R + kind.topMm / 1000f, 0f) : atm.Eye;
                var eTop = Global(top, atm.Rgb(atm.SunAt(top, toSun)));
                float yTop = Lum(eTop);
                var hue = yTop > 0f ? eTop / yTop : Vector3.one;
                deckColour = Vector3.Lerp(hue, Vector3.one, p.overcast.neutralise);
                // the deck's share of the clear light, so that blended by the cover the ground gets Kasten and
                // Czeplak's 1 - loss N^power; CIE overcast: E = 7 pi / 9 Lz, the lobe's extra light folded in
                float share = 1f - p.overcast.loss * Mathf.Pow(Mathf.Max(cover, 1e-3f), p.overcast.lossPower - 1f);
                deckZenith = y * share / (7f * Mathf.PI / 9f * (1f + lobe * 0.12f));
            }

            public Vector3 Radiance(Vector3 d) => Vector3.Lerp(Clear(d.normalized), Deck(d), cover);

            /// <summary>The clear sky alone: what shows between the clouds.</summary>
            public Vector3 Clear(Vector3 d) => atm.Rgb(atm.Radiance(d, toSun));

            /// <summary>The cloud deck's underside alone: CIE overcast's gradient, its glow towards the sun.</summary>
            public Vector3 Deck(Vector3 d)
            {
                d = d.normalized;
                float e = Mathf.Max(0f, d.y);
                float toward = Mathf.Max(0f, Vector3.Dot(d, toSun));
                float sunUp = Mathf.Clamp01(toSun.y * 10f + 0.5f);
                return deckColour * (deckZenith * (1f + 2f * e) / 3f * (1f + lobe * sunUp * Mathf.Pow(toward, 8f)));
            }

            // global light on a level plane at p: the clear sky over it and the sun
            Vector3 Global(Vector3 p, Vector3 sun)
            {
                Vector3 e = Vector3.zero;
                const int n = 6;
                for (int i = 0; i < n; i++)
                    for (int j = 0; j < 2 * n; j++)
                    {
                        float el = (i + 0.5f) / n * Mathf.PI / 2, a = (j + 0.5f) / (2 * n) * 2 * Mathf.PI;
                        float dO = Mathf.Cos(el) * (Mathf.PI / 2 / n) * (2 * Mathf.PI / (2 * n));
                        e += atm.Rgb(atm.Radiance(p, new Vector3(Mathf.Cos(el) * Mathf.Cos(a), Mathf.Sin(el), Mathf.Cos(el) * Mathf.Sin(a)), toSun)) * (Mathf.Sin(el) * dO);
                    }
                return e + sun * Mathf.Max(0f, toSun.y);
            }
        }

        // -- helpers ---------------------------------------------------------------------------------------------

        /// <summary>Towards the sun, in Unity's world axes, from its compass bearing and elevation and the street's frame.</summary>
        public static Vector3 SunVector(double azimuth, double elevation, float streetAxisCompass)
        {
            float b = Mathf.Repeat(streetAxisCompass - (float)azimuth, 360f) * Mathf.Deg2Rad, e = (float)elevation * Mathf.Deg2Rad;
            return StreetSpace.ToUnity(new Vector3(Mathf.Cos(e) * Mathf.Cos(b), Mathf.Cos(e) * Mathf.Sin(b), Mathf.Sin(e))).normalized;
        }

        static Vector3 Flat(Vector3 d, float up)
        {
            var h = new Vector3(d.x, 0f, d.z).normalized * Mathf.Sqrt(1f - up * up);
            return new Vector3(h.x, up, h.z);
        }

        /// <summary>The real L2 SH basis at a unit direction.</summary>
        public static float[] Basis(Vector3 d) => new[]
        {
            0.282095f,
            0.488603f * d.y, 0.488603f * d.z, 0.488603f * d.x,
            1.092548f * d.x * d.y, 1.092548f * d.y * d.z, 0.315392f * (3f * d.z * d.z - 1f), 1.092548f * d.x * d.z, 0.546274f * (d.x * d.x - d.y * d.y),
        };

        /// <summary>Irradiance on a face with normal n from radiance in SH (Ramamoorthi and Hanrahan's cosine lobe).</summary>
        public static Vector3 Irradiance(float[] sh, Vector3 n)
        {
            var y = Basis(n.normalized);
            float[] band = { Mathf.PI, 2f * Mathf.PI / 3f, 2f * Mathf.PI / 3f, 2f * Mathf.PI / 3f, Mathf.PI / 4f, Mathf.PI / 4f, Mathf.PI / 4f, Mathf.PI / 4f, Mathf.PI / 4f };
            Vector3 e = Vector3.zero;
            for (int k = 0; k < 9; k++)
                e += new Vector3(sh[3 * k], sh[3 * k + 1], sh[3 * k + 2]) * (band[k] * y[k]);
            return Max0(e);
        }

        public static Vector3 XyToRgb(float[] xy)
        {
            float x = xy[0], y = xy[1];
            float X = x / y, Z = (1f - x - y) / y;
            var rgb = new Vector3(3.2406f * X - 1.5372f - 0.4986f * Z, -0.9689f * X + 1.8758f + 0.0415f * Z, 0.0557f * X - 0.2040f + 1.0570f * Z);
            rgb = Max0(rgb);
            return rgb / Lum(rgb);
        }

        public static float Lum(Vector3 c) => 0.2126f * c.x + 0.7152f * c.y + 0.0722f * c.z;
        public static Vector3 Mul(Vector3 a, Vector3 b) => new Vector3(a.x * b.x, a.y * b.y, a.z * b.z);
        static Vector3 Max0(Vector3 v) => new Vector3(Mathf.Max(0f, v.x), Mathf.Max(0f, v.y), Mathf.Max(0f, v.z));
        public static float[] Arr(Vector3 v) => new[] { v.x, v.y, v.z };
        public static Vector3 Vec(float[] a) => new Vector3(a[0], a[1], a[2]);
        static string Hex(ulong h) => h.ToString("x16");

        static float[] Flat(Vector3[] sh)
        {
            var f = new float[27];
            for (int k = 0; k < 9; k++)
            {
                f[3 * k] = sh[k].x; f[3 * k + 1] = sh[k].y; f[3 * k + 2] = sh[k].z;
            }
            return f;
        }

        // OKLab (Björn Ottosson, 2020) on linear Rec.709, as lightness, chroma and hue in degrees
        static Vector3 ToOklch(Vector3 c)
        {
            float l = Mathf.Pow(0.4122214708f * c.x + 0.5363325363f * c.y + 0.0514459929f * c.z, 1f / 3f);
            float m = Mathf.Pow(0.2119034982f * c.x + 0.6806995451f * c.y + 0.1073969566f * c.z, 1f / 3f);
            float s = Mathf.Pow(0.0883024619f * c.x + 0.2817188376f * c.y + 0.6299787005f * c.z, 1f / 3f);
            float L = 0.2104542553f * l + 0.7936177850f * m - 0.0040720468f * s;
            float a = 1.9779984951f * l - 2.4285922050f * m + 0.4505937099f * s;
            float b = 0.0259040371f * l + 0.7827717662f * m - 0.8086757660f * s;
            return new Vector3(L, Mathf.Sqrt(a * a + b * b), Mathf.Atan2(b, a) * Mathf.Rad2Deg);
        }

        static Vector3 FromOklch(Vector3 lch)
        {
            float a = lch.y * Mathf.Cos(lch.z * Mathf.Deg2Rad), b = lch.y * Mathf.Sin(lch.z * Mathf.Deg2Rad);
            float l = lch.x + 0.3963377774f * a + 0.2158037573f * b;
            float m = lch.x - 0.1055613458f * a - 0.0638541728f * b;
            float s = lch.x - 0.0894841775f * a - 1.2914855480f * b;
            l = l * l * l; m = m * m * m; s = s * s * s;
            return new Vector3(4.0767416621f * l - 3.3077115913f * m + 0.2309699292f * s,
                               -1.2684380046f * l + 2.6097574011f * m - 0.3413193965f * s,
                               -0.0041960863f * l - 0.7034186147f * m + 1.7076147010f * s);
        }
    }
}
