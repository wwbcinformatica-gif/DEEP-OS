"""
File Tools — glob + grep aprimorados (GlobTool do OpenClaude).
"""
import fnmatch
import os


async def tool_glob(pattern: str, path: str = "") -> dict:
    base = path or os.getcwd()
    matched = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ('node_modules', '__pycache__')]
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), base)
            if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(f, pattern):
                matched.append(rel)
    matched.sort()
    return {"pattern": pattern, "path": base, "files": matched, "total": len(matched)}
