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
# Already resolved symbols legitimately disappear from the linker duplicate list.
# Verify the remaining public definition in source instead of expecting an error.
source_root = Path("src/cards")
recoded_text = (source_root / "recoded_cards.c").read_text(encoding="utf-8", errors="replace")
unlimited_text = (source_root / "unlimited.c").read_text(encoding="utf-8", errors="replace")
for name in ("card_rock_hydra", "card_volcanic_eruption", "card_time_walk"):
    pattern = re.compile(r"\\bint\\s+" + re.escape(name) + r"\\s*\\(")
    if len(pattern.findall(recoded_text)) != 1:
        raise SystemExit(f"Expected exactly one recoded definition: {name}")
    matches = [row for row in rows if row[0] == name]
    if pattern.search(unlimited_text):
        if not matches or matches[0][1] != "prefer_recoded_pending_runtime_validation":
            raise SystemExit(f"Still duplicated but missing priority audit: {name}")
        print(f"Pending duplicate, recoded preferred: {name}")
    else:
        if matches:
            raise SystemExit(f"Unexpected duplicate after legacy rename: {name}")
        legacy_pattern = re.compile(r"\\bint\\s+" + re.escape(name + "_legacy_unlimited") + r"\\s*\\(")
        if not legacy_pattern.search(unlimited_text):
            raise SystemExit(f"Legacy implementation not retained: {name}")
        print(f"Resolved, recoded owns public symbol: {name}")
print(f"Report: {destination}")
