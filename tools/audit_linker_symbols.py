#!/usr/bin/env python3
"""Read-only linker diagnostic for legacy Shandalar builds.

Parse GNU ld messages from build.log. Never select a winning implementation:
duplicate definitions require review of gameplay behavior and calling conventions.
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

LOG = Path(sys.argv[1] if len(sys.argv) > 1 else "build.log")
REPORT = Path(sys.argv[2] if len(sys.argv) > 2 else "linker-symbol-audit.json")
CSV_REPORT = REPORT.with_suffix(".csv")
PAIR_REPORT = REPORT.with_name("linker-duplicate-file-pairs.csv")
line_pattern = re.compile(
    r"(?P<file>[^\s:]+\.(?:c|cpp|asm)):(?P<line>\d+): "
    r"multiple definition of [`'](?P<symbol>[^`']+)[`']; "
    r"(?P<first_object>[^:]+):(?P<first_file>[^\s:]+\.(?:c|cpp|asm)):"
    r"(?P<first_line>\d+): first defined here"
)
undefined_pattern = re.compile(r"undefined reference to [`']([^`']+)[`']")
entries = {}
unresolved = Counter()
for line in LOG.read_text(encoding="utf-8", errors="replace").splitlines():
    # GitHub Actions log lines have timestamps before linker output.
    match = line_pattern.search(line)
    if match:
        d = match.groupdict()
        entries.setdefault(d["symbol"], []).append({
            "conflict": {"file": d["file"], "line": int(d["line"])},
            "first": {"file": d["first_file"], "line": int(d["first_line"])}
        })
    for symbol in undefined_pattern.findall(line):
        unresolved[symbol] += 1

def category(name):
    if name.startswith("card_") or name.startswith("effect_"):
        return "card_or_card_effect"
    return "shared_function"

duplicates = [
    {"symbol": symbol, "category": category(symbol), "locations": locations}
    for symbol, locations in sorted(entries.items())
]
report = {
    "source_log": str(LOG),
    "duplicate_symbol_count": len(duplicates),
    "duplicate_symbols": duplicates,
    "unresolved_symbol_count": len(unresolved),
    "unresolved_symbols": [
        {"symbol": name, "occurrences": count}
        for name, count in sorted(unresolved.items())
    ],
    "notice": "Diagnostic only: symbol addresses and preferred implementations are not validated."
}
REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
with CSV_REPORT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["symbol", "category", "conflicting_file", "conflicting_line", "first_file", "first_line"])
    for item in duplicates:
        for pair in item["locations"]:
            writer.writerow([
                item["symbol"], item["category"],
                pair["conflict"]["file"], pair["conflict"]["line"],
                pair["first"]["file"], pair["first"]["line"]
            ])
# Rank file pairs to choose small, reviewable fixes, without selecting an implementation.
file_pairs = {}
for item in duplicates:
    for location in item["locations"]:
        source_pair = tuple(sorted([
            location["first"]["file"].replace("\\\\", "/").split("/src/")[-1],
            location["conflict"]["file"].replace("\\\\", "/").split("/src/")[-1],
        ]))
        file_pairs.setdefault(source_pair, set()).add(item["symbol"])
with PAIR_REPORT.open("w", encoding="utf-8", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["file_a", "file_b", "duplicate_count", "symbols"])
    for pair, symbols in sorted(file_pairs.items(), key=lambda row: (-len(row[1]), row[0])):
        writer.writerow([pair[0], pair[1], len(symbols), ";".join(sorted(symbols))])
print("Largest duplicate file pairs:")
for pair, symbols in sorted(file_pairs.items(), key=lambda row: (-len(row[1]), row[0]))[:12]:
    print(f"  {len(symbols):3} {pair[0]} / {pair[1]}")
print(f"Pair report: {PAIR_REPORT}")
print(f"Duplicate symbols: {len(duplicates)}")
print(f"Unresolved symbols: {len(unresolved)}")
print("Duplicate symbol categories:", dict(Counter(item["category"] for item in duplicates)))
for item in duplicates:
    pair = item["locations"][0]
    print(f"  {item['symbol']}: {pair['first']['file']}:{pair['first']['line']} / {pair['conflict']['file']}:{pair['conflict']['line']}")
print(f"Reports: {REPORT}, {CSV_REPORT}")
