#!/usr/bin/env python3
"""Audit every duplicate against the preferred recoded_cards.c ownership policy.

Read-only: this does not change C code, linker behavior, or gameplay dispatch.
"""
import csv
import json
import re
import sys
from pathlib import Path

source = Path(sys.argv[1] if len(sys.argv) > 1 else "linker-symbol-audit.json")
destination = Path(sys.argv[2] if len(sys.argv) > 2 else "recoded-ownership-audit.csv")
data = json.loads(source.read_text(encoding="utf-8"))
rows = []
for entry in data["duplicate_symbols"]:
    symbol = entry["symbol"]
    source_paths = set()
    for pair in entry["locations"]:
        for key in ("first", "conflict"):
            source_paths.add(pair[key]["file"].replace("\\", "/").split("/src/")[-1])
    recoded = "cards/recoded_cards.c" in source_paths
    if recoded and symbol.startswith("card_"):
        decision = "prefer_recoded_pending_runtime_validation"
    elif recoded:
        decision = "review_shared_effect_or_helper"
    else:
        decision = "manual_review_no_recoded_definition"
    rows.append((symbol, decision, ";".join(sorted(source_paths))))
with destination.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(("symbol", "ownership_policy", "source_files"))
    writer.writerows(sorted(rows))
recoded_count = sum("prefer_recoded" in row[1] for row in rows)
print(f"Audited duplicate symbols: {len(rows)}")
print(f"Card symbols with recoded priority: {recoded_count}")
print(f"Other symbols for review: {len(rows) - recoded_count}")
for name in ("card_rock_hydra", "card_volcanic_eruption", "card_time_walk"):
    matches = [row for row in rows if row[0] == name]
    if not matches or matches[0][1] != "prefer_recoded_pending_runtime_validation":
        raise SystemExit(f"Expected recoded precedence not found for {name}")
    print(f"Verified recoded priority: {name}")
print(f"Report: {destination}")
