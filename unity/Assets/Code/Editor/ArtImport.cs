using UnityEditor;

namespace Overstory.EditorTools
{
    /// <summary>
    /// How exported art is imported: models from Blender in metres with their own flat normals and no
    /// materials of their own (the street's one material is assigned when placed), and the palette's
    /// maps point-sampled and uncompressed so every swatch keeps its exact colour.
    /// </summary>
    public class ArtImport : AssetPostprocessor
    {
        // raise when the rules change, so Unity re-imports the art under them
        public override uint GetVersion() => 3;

        void OnPreprocessModel()
        {
            if (!assetPath.StartsWith("Assets/Art/"))
                return;
            var m = (ModelImporter)assetImporter;
            m.globalScale = 1f;
            m.useFileScale = true;
            m.bakeAxisConversion = false;
            m.importNormals = ModelImporterNormals.Import;
            m.importTangents = ModelImporterTangents.None;
            m.materialImportMode = ModelImporterMaterialImportMode.None;
            m.importAnimation = false;
            m.animationType = ModelImporterAnimationType.None;
            m.importCameras = false;
            m.importLights = false;
            m.importBlendShapes = false;
            m.isReadable = false;
            m.meshCompression = ModelImporterMeshCompression.Off;
            m.generateSecondaryUV = false;
            m.weldVertices = true;
            m.indexFormat = ModelImporterIndexFormat.Auto;
        }

        /// <summary>
        /// The export writes vertices already in Unity's axes (export_street.py: Unity x, y, z is street
        /// x, z, y). Unity still turns the root 180 degrees to make up for the FBX file's own axis
        /// settings; that turn is undone here so every model stands as the street placed it.
        /// </summary>
        void OnPostprocessModel(UnityEngine.GameObject root)
        {
            if (!assetPath.StartsWith("Assets/Art/"))
                return;
            root.transform.localRotation = UnityEngine.Quaternion.identity;
        }

        void OnPreprocessTexture()
        {
            if (assetPath.StartsWith("Assets/Art/Trees/"))
            {
                // a tree's painted parts are masks the tree shader colours, not colours; the leaf sprays keep their
                // coverage in every mip (Castano's coverage-preserving mips), so a crown does not thin with distance
                var tt = (TextureImporter)assetImporter;
                bool spray = assetPath.EndsWith("_leaves.png");
                tt.textureType = TextureImporterType.Default;
                tt.sRGBTexture = false;
                tt.mipmapEnabled = true;
                tt.mipMapsPreserveCoverage = spray;
                tt.alphaTestReferenceValue = 0.5f;
                tt.alphaSource = spray ? TextureImporterAlphaSource.FromInput : TextureImporterAlphaSource.None;
                tt.alphaIsTransparency = false;
                tt.filterMode = UnityEngine.FilterMode.Trilinear;
                tt.anisoLevel = 4;
                tt.wrapMode = spray ? UnityEngine.TextureWrapMode.Clamp : UnityEngine.TextureWrapMode.Repeat;
                // the leaf ids must not bleed between leaves under block compression
                tt.textureCompression = spray ? TextureImporterCompression.Uncompressed : TextureImporterCompression.CompressedHQ;
                tt.isReadable = false;
                return;
            }
            if (!assetPath.StartsWith("Assets/Art/Palette/"))
                return;
            var t = (TextureImporter)assetImporter;
            t.textureType = TextureImporterType.Default;
            // colours are sRGB; the glow groups and surface properties are data
            t.sRGBTexture = assetPath.EndsWith("_albedo.png") || assetPath.EndsWith("_emit.png");
            t.filterMode = UnityEngine.FilterMode.Point;
            t.wrapMode = UnityEngine.TextureWrapMode.Clamp;
            t.mipmapEnabled = false;
            t.npotScale = TextureImporterNPOTScale.None;
            t.alphaSource = TextureImporterAlphaSource.None;
            t.textureCompression = TextureImporterCompression.Uncompressed;
            t.isReadable = false;
        }
    }
}
