using UnityEngine;

namespace Overstory.World
{
    /// <summary>
    /// The history pages bound for every shader (docs/research/history-pages.md, 1; Shaders/History.hlsl): the RGBA page
    /// array (P0, P1 and H1 of every page group, a slice each) as a global texture, and the piece table as a global
    /// StructuredBuffer that a draw reads by UV3's piece index. No material property: a draw finds its pages through its
    /// pieces, so binding costs no draw, SRP batch or material copy.
    /// </summary>
    [ExecuteAlways]
    public class HistoryPages : MonoBehaviour
    {
        public static readonly int PagesId = Shader.PropertyToID("_OS_PagesRGBA");
        public static readonly int PiecesId = Shader.PropertyToID("_OS_Pieces");

        /// <summary>Bytes a piece: History.hlsl's OSPiece.</summary>
        public const int Stride = 16;

        [Tooltip("The RGBA pages: P0, P1 and H1 of every page group, a slice each (RGBA8, or BC7).")]
        public Texture2DArray rgba;
        [Tooltip("The piece table, four uints a piece (OSPiece: the group's first slice, two pairs of resets, the age and flags).")]
        public uint[] pieces;
        [Tooltip("Bind when enabled. Off where a runner binds one of several sets.")]
        public bool bindOnEnable = true;

        GraphicsBuffer table;

        void OnEnable()
        {
            if (bindOnEnable)
                Bind();
        }

        /// <summary>Makes these the pages and piece table every shader reads.</summary>
        public void Bind()
        {
            if (rgba == null || pieces == null || pieces.Length < 4)
                return;
            if (table == null || !table.IsValid())
            {
                table = new GraphicsBuffer(GraphicsBuffer.Target.Structured, Mathf.Max(1, pieces.Length / 4), Stride);
                table.SetData(pieces);
            }
            Shader.SetGlobalTexture(PagesId, rgba);
            Shader.SetGlobalBuffer(PiecesId, table);
        }

        void OnDisable()
        {
            table?.Release();
            table = null;
        }
    }
}
