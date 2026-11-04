#!/usr/bin/env python3
"""Find similarly named source symbols for unresolved linker references.

Read-only source inventory; deliberately does not guess ABI or EXE addresses.
"""
import csv
import difflib
import json
import re
from pathlib import Path

report = json.loads(Path("linker-symbol-audit.json").read_text(encoding="utf-8"))
symbols = [item["symbol"] for item in report["unresolved_symbols"]]
roots = [Path("src")]
source_files = sorted(path for root in roots for path in root.rglob("*")
                      if path.suffix.lower() in {".c", ".h", ".cpp", ".asm", ".lds"})
definitions = {}
identifiers = set()
for path in source_files:
    content = path.read_text(encoding="utf-8", errors="replace")
    for match in re.finditer(r"\b[A-Za-z_]\w*\b", content):
        identifiers.add(match.group())
    for match in re.finditer(r"(?m)^\s*(?:extern\s+)?(?:static\s+)?(?:int|void|char|unsigned|long|short|card_instance_t\s*\*)\s+([A-Za-z_]\w*)\s*\(", content):
        definitions.setdefault(match.group(1), set()).add(str(path))
output = Path("unresolved-symbol-candidates.csv")
with output.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["missing_symbol", "candidate", "similarity", "definition_locations", "warning"])
    for missing in symbols:
        candidates = difflib.get_close_matches(missing, sorted(definitions), n=8, cutoff=0.5)
        for candidate in candidates:
            writer.writerow([missing, candidate,
                             round(difflib.SequenceMatcher(None, missing, candidate).ratio(), 3),
                             ";".join(sorted(definitions[candidate])),
                             "NAME SIMILARITY ONLY; validate semantics and ABI"])
        if not candidates:
            writer.writerow([missing, "", "", "", "No similar source declaration; check original EXE and headers"])
print(f"Scanned {len(source_files)} source/header files for {len(symbols)} unresolved names")
print(f"Candidate report: {output}")
