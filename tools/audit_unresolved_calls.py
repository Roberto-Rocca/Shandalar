#!/usr/bin/env python3
"""Collect unresolved references and their C/ASM call sites; no gameplay edits."""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

log = Path(sys.argv[1] if len(sys.argv) > 1 else "build.log")
output = Path(sys.argv[2] if len(sys.argv) > 2 else "unresolved-call-sites.csv")
pattern = re.compile(r"(?P<path>[^\s:]+\.(?:c|asm)):(?P<line>\d+):[^\n]*?undefined reference to [`'](?P<symbol>[A-Za-z_][\w]*)'")
entries = defaultdict(set)
for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
    match = pattern.search(line)
    if match:
        d = match.groupdict()
        path = d["path"].replace("\\", "/")
        # GitHub runner absolute paths end in /src/...
        path = "src/" + path.split("/src/")[-1] if "/src/" in path else path
        entries[d["symbol"]].add((path, int(d["line"])))
with output.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(("symbol", "source", "line", "source_excerpt"))
    for symbol, locations in sorted(entries.items()):
        for path, lineno in sorted(locations):
            local_path = Path(path)
            lines = local_path.read_text(encoding="utf-8", errors="replace").splitlines() if local_path.is_file() else []
            excerpt = lines[lineno - 1].strip() if 0 < lineno <= len(lines) else ""
            writer.writerow((symbol, path, lineno, excerpt))
print(f"Unresolved reference names with source locations: {len(entries)}")
print(f"Written {output}")
