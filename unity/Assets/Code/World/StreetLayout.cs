using System;
using UnityEngine;

namespace Overstory.World
{
    /// <summary>
    /// A street as Blender's export resolved it (blender/tools/export_street.py): where each building,
    /// lamp and bollard stands, and the bands of ground. Unity places and draws it; it decides nothing.
    /// Positions are street coordinates in metres: x along the street, y from the building line towards
    /// the back of the plots (negative towards the harbour), z up.
    /// </summary>
    [Serializable]
    public class StreetLayout
    {
        public string street;
        public int year;
        public string style;
        public int worldSeed;
        public string fixture;
        public float x0, x1;
        public Band[] bands;
        public Quay quay;
        public Water water;
        public Backland backland;
        public BuildingRef[] buildings;
        public LampRef[] lamps;
        public Bollards bollards;
        public KitPiece[] kit;
        public Emissive[] emissive;
        public PaletteInfo palette;
        public Slope slope;

        /// <summary>Whether the town climbs above the street (levels, stairs, hillside, ridges).</summary>
        public bool HasSlope => slope != null && slope.levels != null && slope.levels.Length > 0;

        public static StreetLayout Parse(string json) => JsonUtility.FromJson<StreetLayout>(json);

        public KitPiece Kit(string name)
        {
            foreach (var k in kit)
                if (k.name == name)
                    return k;
            throw new ArgumentException($"no kit piece '{name}' in the street layout");
        }

        public Band BandNamed(string name)
        {
            foreach (var b in bands)
                if (b.name == name)
                    return b;
            throw new ArgumentException($"no band '{name}' in the street layout");
        }
    }

    [Serializable] public struct P3 { public float x, y, z; }

    [Serializable] public class Band { public string name; public float y0, y1; public string surface; }

    [Serializable] public class Quay { public float edge, height; public string coping; }

    [Serializable] public class Water { public float level; }

    [Serializable] public class Backland { public float depth; public string surface; public YZ[] profile; }

    /// <summary>A point of a ground profile: height z at distance y from the building line.</summary>
    [Serializable] public struct YZ { public float y, z; }

    /// <summary>The town above the street: levels held by retaining walls, stairs, the hillside, distant ridges.</summary>
    [Serializable]
    public class Slope
    {
        public Level[] levels;
        public Stair[] stairs;
        public YZ[] hillside;
        public Ridge[] ridges;
        public string walls;
    }

    /// <summary>A level of the town: ground at height z from y0 to y1, a retaining wall at y0, a lane along it.</summary>
    [Serializable] public class Level { public string name; public float y0, y1, z; public string surface; public Lane lane; }

    [Serializable] public class Lane { public float y0, y1; public string surface; }

    /// <summary>A stepped lane at x: flat where its path is level, steps where it climbs.</summary>
    [Serializable] public class Stair { public string name; public float x, width; public YZ[] path; }

    /// <summary>A ridge of hills or mountains from a to b on the ground plane, its crest at height.</summary>
    [Serializable] public class Ridge { public string name; public float ax, ay, bx, by, height, width; }

    [Serializable]
    public class BuildingRef
    {
        public int id;
        public string type;
        public string file;
        public P3 position;
        public string[] lit;
        public int tris;
    }

    [Serializable]
    public class LampRef
    {
        public string id;
        public string variant;
        public P3 position;
        public string light; // warm, mercury or sodium: the kind of light the lamp gives
    }

    [Serializable] public class Bollards { public string variant; public P3[] positions; }

    [Serializable]
    public class KitPiece
    {
        public string name;
        public string file;
        public P3 light; // where its light comes from, relative to its pivot, for lamps
        public string glow;
    }

    [Serializable] public class Emissive { public string swatch, off, group; }

    [Serializable] public class PaletteInfo { public int grid; public string[] names; }

    /// <summary>Street coordinates (x along, y back, z up) to Unity's (x right, y up, z forward).</summary>
    public static class StreetSpace
    {
        public static Vector3 ToUnity(float x, float y, float z) => new Vector3(x, z, y);
        public static Vector3 ToUnity(P3 p) => new Vector3(p.x, p.z, p.y);
        public static Vector3 ToUnity(Vector3 street) => new Vector3(street.x, street.z, street.y);
    }

    /// <summary>The shared palette's swatches: UV coordinates by name, as palette.py lays them out.</summary>
    public class Palette
    {
        readonly PaletteInfo info;

        public Palette(PaletteInfo info) { this.info = info; }

        public Vector2 UV(string swatch)
        {
            int i = Array.IndexOf(info.names, swatch);
            if (i < 0)
                throw new ArgumentException($"no swatch '{swatch}' in the palette");
            int col = i % info.grid, row = i / info.grid;
            return new Vector2((col + 0.5f) / info.grid, 1f - (row + 0.5f) / info.grid);
        }
    }
}
