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
        public TreeRef[] trees;
        public Town town;
        public P3[] spill; // where lit rooms spill light: in front of each lit floor's windows

        /// <summary>Whether the street has a grown town above it, with its own ground.</summary>
        public bool HasTown => town != null && town.fine != null && town.fine.nx > 1;

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
        public string hillsideSurface;
        public Ridge[] ridges;
        public string walls;
        public Site site;

        public bool HasSite => site != null && site.bayX1 > site.bayX0;
    }

    /// <summary>The ground the town stands on: the bay it fills, the hills beside it, how rough the land is.</summary>
    [Serializable]
    public class Site
    {
        public float bayX0, bayX1, sideHeight, sideReach, roughHeight, roughScale;
        public string surface;
    }

    /// <summary>A level of the town: ground at height z from y0 to y1, a retaining wall at y0, a lane along it.</summary>
    [Serializable] public class Level { public string name; public float y0, y1, z; public string surface; public Lane lane; }

    [Serializable] public class Lane { public float y0, y1; public string surface; }

    /// <summary>A stepped lane at x: flat where its path is level, steps where it climbs.</summary>
    [Serializable] public class Stair { public string name; public float x, width; public YZ[] path; }

    /// <summary>A ridge of hills or mountains from a to b on the ground plane, its crest at height.</summary>
    [Serializable] public class Ridge { public string name; public float ax, ay, bx, by, height, width; public string surface; }

    [Serializable]
    public class BuildingRef
    {
        public int id;
        public string type;
        public string file;
        public P3 position;
        public float yaw; // degrees, turning the building in the street's plane (counter-clockwise seen from above)
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

    /// <summary>The town grown above the street (blender/tools/grow_town.py), resolved: its ground and stonework.</summary>
    [Serializable]
    public class Town
    {
        public HeightGrid fine, coarse;
        public Path[] lanes, stairs, steps, squares;
        public Wall[] walls;
        public Foundation[] foundations;
        [Tooltip("Above this height (street metres) open ground is heath, below it grass.")]
        public float heathAbove = 55f;
    }

    /// <summary>A height grid in street metres: z[j * nx + i] at (x0 + i * step, y0 + j * step).</summary>
    [Serializable]
    public class HeightGrid
    {
        public float x0, y0, step;
        public int nx, ny;
        public float[] z;

        public float At(int i, int j) => z[Mathf.Clamp(j, 0, ny - 1) * nx + Mathf.Clamp(i, 0, nx - 1)];

        public bool Contains(float x, float y) => x >= x0 && y >= y0 && x <= x0 + (nx - 1) * step && y <= y0 + (ny - 1) * step;

        public float Sample(float x, float y)
        {
            float u = (x - x0) / step, v = (y - y0) / step;
            int i = Mathf.Clamp(Mathf.FloorToInt(u), 0, nx - 2), j = Mathf.Clamp(Mathf.FloorToInt(v), 0, ny - 2);
            float fu = u - i, fv = v - j;
            float a = Mathf.Lerp(At(i, j), At(i + 1, j), fu), b = Mathf.Lerp(At(i, j + 1), At(i + 1, j + 1), fu);
            return Mathf.Lerp(a, b, fv);
        }
    }

    /// <summary>A lane, stepped lane, steps or square: points in street metres, a width, a surface.</summary>
    [Serializable] public class Path { public string name; public float width; public string surface; public float z; public P3[] points; public P3[] corners; }

    [Serializable] public class WallPoint { public float x, y, zb, zt; }

    /// <summary>A wall along a line: dry stone holding a cut, or a garden wall along a lane.</summary>
    [Serializable] public class Wall { public string kind; public WallPoint[] points; }

    /// <summary>A house's stone basement: its footprint, from the floor down into the ground.</summary>
    [Serializable] public class Foundation { public int id; public float top, bottom; public P3[] corners; }

    /// <summary>A tree: its species' kit piece, where it stands, its size from its age, a seeded turn.</summary>
    [Serializable] public class TreeRef { public string id; public string variant; public P3 position; public float scale; public float turn; }

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
