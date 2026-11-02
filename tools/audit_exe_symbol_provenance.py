#!/usr/bin/env python3
"""Audit EXE-dependent unresolved symbols without inventing addresses or stubs."""
import csv
import re
from pathlib import Path

names = (
    "damage_dealt_to_me",
    "hack_animate_dead_player",
    "hack_animate_dead_card",
    "card_goblin_shrine_exe",
    "card_fork_orig",
)
files = sorted(p for p in Path("src").rglob("*")
               if p.suffix.lower() in (".c", ".h", ".asm", ".lds"))
             )
linker = Path("src/manalink.lds").read_text(errors="replace")
with Path("exe-symbol-provenance.csv").open("w", newline="", encoding="utf-8") as out:
    writer = csv.writer(out)
    writer.writerow(("symbol", "file", "line", "kind", "context"))
    for name in names:
        found = 0
        for path in files:
            for line_no, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
                if re.search(r"\b" + re.escape(name) + r"\b", line):
                    kind = ("linker_address" if path.name == "manalink.lds" else
                            "extern_declaration" if re.search(r"\bextern\b", line) else
                            "source_reference")
                    writer.writerow((name, path.as_posix(), line_no, kind, line.strip()[:250]))
                    found += 1
        if not found:
            writer.writerow((name, "", "", "absent", "No source reference found"))
        print(f"{name}: {found} textual source references")
print("A reference is NOT proof of an implementation or ABI-compatible EXE address.")
