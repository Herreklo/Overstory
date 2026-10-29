using UnityEditor;
using UnityEngine;

namespace Overstory.EditorTools
{
    /// <summary>
    /// A batch capture renders every texture at its full mips: the PC quality level streams mips (a far house holds only
    /// what its distance needs), and a still taken before the streamer settles would be judged on blurred textures.
    /// </summary>
    [InitializeOnLoad]
    static class BatchFullMips
    {
        static BatchFullMips()
        {
            if (Application.isBatchMode)
                Texture.streamingTextureForceLoadAll = true;
        }
    }
}
