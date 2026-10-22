using System.Collections.Generic;
using System.Linq;
using UnityEditor.Build;
using UnityEditor.Rendering;
using UnityEngine;

namespace Overstory.EditorTools
{
    /// <summary>
    /// L5's term arms (1c; reviews/lt1/light/l5-report.md) as few variants as they need. The street and stone shaders
    /// declare one set of OS_L5_&lt;TERM&gt; keywords, each skipping one term for the harness (PerfRunner: 'bare-&lt;term&gt;',
    /// 'all-shadow'). Compiled for every combination they would multiply the shaders' variants by ten, about two seconds
    /// of the M4 each, so a build keeps a term's variants only when its own -perf-passes names that term, and then only
    /// in look P with the history and the air on, the only ones the harness draws them in. No game or walk build carries
    /// them; the variants with no OS_L5 keyword are never touched.
    /// </summary>
    class L5Strip : IPreprocessShaders
    {
        public int callbackOrder => 0;

        static HashSet<string> wanted;

        /// <summary>The OS_L5 keywords this build's -perf-passes names ('bare-near' keeps OS_L5_NEAR).</summary>
        static HashSet<string> Wanted()
        {
            if (wanted != null)
                return wanted;
            wanted = new HashSet<string>();
            var args = System.Environment.GetCommandLineArgs();
            int i = System.Array.IndexOf(args, "-perf-passes");
            if (i >= 0 && i + 1 < args.Length)
                foreach (var c in args[i + 1].Split(','))
                    foreach (var prefix in new[] { "bare-", "all-" })
                        if (c.StartsWith(prefix) && c != "bare-haze")
                            wanted.Add("OS_L5_" + c.Substring(prefix.Length).ToUpperInvariant());
            if (wanted.Count > 0)
                Debug.Log($"[L5Strip] keeping {string.Join(", ", wanted)} in look P");
            return wanted;
        }

        public void OnProcessShader(Shader shader, ShaderSnippetData snippet, IList<ShaderCompilerData> data)
        {
            if (shader.name != "Overstory/Street" && shader.name != "Overstory/Stone")
                return;
            var keep = Wanted();
            for (int i = data.Count - 1; i >= 0; i--)
            {
                var names = data[i].shaderKeywordSet.GetShaderKeywords().Select(k => k.name).ToList();
                var l5 = names.Where(n => n.StartsWith("OS_L5_")).ToList();
                if (l5.Count == 0)
                    continue;
                bool used = l5.All(keep.Contains) && names.Contains("_OS_LOOK_P")
                            && !names.Contains("OS_HAZE_OFF") && !names.Contains("OS_HISTORY_OFF");
                if (!used)
                    data.RemoveAt(i);
            }
        }
    }
}
