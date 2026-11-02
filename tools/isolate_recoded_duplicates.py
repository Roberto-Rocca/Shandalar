#!/usr/bin/env python3
"""Batch-resolve recoded card duplicate definitions in a CI checkout.

Preserves legacy function bodies and source files in Git. The injected macros
rename only competing symbols during preprocessing. Intended for link
diagnostics, NOT proof of runtime correctness or dispatch mapping.
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

cards_dir = Path("src/cards")
recoded = cards_dir / "recoded_cards.c"
pattern = re.compile(r"(?m)^\s*int\s+(card_[a-zA-Z0-9_]+)\s*\([^;{}]*\)\s*\{")
recoded_names = set(pattern.findall(recoded.read_text(encoding="utf-8", errors="replace")))
if not recoded_names:
    raise SystemExit("Cannot detect recoded cards; refusing batch changes")

changes = defaultdict(list)
for path in sorted(cards_dir.glob("*.c")):
    if path == recoded:
        continue
    content = path.read_text(encoding="utf-8", errors="replace")
    defined = set(pattern.findall(content))
    duplicates = sorted(recoded_names & defined)
    if not duplicates:
        continue
    include = re.search(r'(?m)^#include\s+"manalink\.h"[^\n]*\n', content)
    if not include:
        raise SystemExit(f"Missing manalink.h include in {path}; refusing unsafe rewrite")
    defines = []
    for name in duplicates:
        new_name = f"{name}_legacy_{path.stem}"
        if new_name in content or new_name in recoded_names:
            raise SystemExit(f"Naming collision for {name} in {path}")
        defines.append(f"#define {name} {new_name}")
        changes[str(path)].append((name, new_name))
    banner = "/* CI-only legacy symbol isolation; original source remains unchanged in Git. */\n"
    updated = content[:include.end()] + banner + "\n".join(defines) + "\n" + content[include.end():]
    path.write_text(updated, encoding="utf-8")

report = Path("recoded-batch-renames.csv")
with report.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["source_file", "original_symbol", "temporary_legacy_symbol", "preferred_owner"])
    for path, pairs in sorted(changes.items()):
        for old, new in pairs:
            writer.writerow([path, old, new, str(recoded)])
total = sum(len(items) for items in changes.values())
print(f"Batch renames: {total} across {len(changes)} files")
print(f"Report: {report}")
if total < 20:
    raise SystemExit("Unexpectedly few recoded conflicts; refusing diagnostic build")
