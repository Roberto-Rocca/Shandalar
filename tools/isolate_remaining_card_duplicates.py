#!/usr/bin/env python3
"""Experimentally isolate remaining duplicate card handlers, preserving all source.

Run AFTER isolate_recoded_duplicates.py. No original source changes in Git.
Selection is provisional and MUST be reviewed against gameplay behavior.
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

folder = Path("src/cards")
definition = re.compile(r"(?m)^\s*int\s+(card_[A-Za-z0-9_]+)\s*\([^;{}]*\)\s*\{")
preferred = {"lands.c", "artifacts.c", "artifact_creatures.c",
             "black_creatures.c", "blue_creatures.c", "green_creatures.c",
             "red_creatures.c", "white_creatures.c",
             "black_oneshot.c", "blue_oneshot.c", "green_oneshot.c",
             "red_oneshot.c", "white_oneshot.c",
             "black_enchantments.c", "blue_enchantments.c",
             "green_enchantments.c", "red_enchantments.c",
             "white_enchantments.c"}
sources = {path: path.read_text(encoding="utf-8", errors="replace")
           for path in sorted(folder.glob("*.c"))}
owners = defaultdict(list)
for path, content in sources.items():
    for name in set(definition.findall(content)):
        owners[name].append(path)

def priority(path):
    if path.name == "recoded_cards.c":
        return (0, path.name)
    if path.name in preferred:
        return (1, path.name)
    if path.name == "jatill.c":
        return (3, path.name)
    return (2, path.name)

renames = defaultdict(list)
for symbol, paths in sorted(owners.items()):
    if len(paths) < 2:
        continue
    # ManalinkEh.asm calls these public Unlimited handlers directly.
    required_unlimited = {"card_ancestral_recall", "card_swords_to_plowshares"}
    unlimited_path = folder / "unlimited.c"
    winner = unlimited_path if symbol in required_unlimited and unlimited_path in paths else min(paths, key=priority)
    for loser in paths:
        if loser == winner:
            continue
        old_content = sources[loser]
        legacy = f"{symbol}_legacy_batch_{loser.stem}"
        if legacy in old_content:
            raise SystemExit(f"Collision: {legacy}")
        # Macro injection after the shared header, consistently with phase one.
        renames[loser].append((symbol, legacy, winner))

for path, symbols in sorted(renames.items()):
    content = sources[path]
    include = re.search(r'(?m)^#include\s+"manalink\.h"[^\n]*\n', content)
    if not include:
        raise SystemExit(f"Missing manalink.h: {path}")
    macro_lines = [f"#define {original} {legacy}" for original, legacy, _ in symbols]
    prefix = "/* CI-only experimental ownership; regression tests required. */\n"
    content = content[:include.end()] + prefix + "\n".join(macro_lines) + "\n" + content[include.end():]
    path.write_text(content, encoding="utf-8")

with Path("experimental-card-ownership.csv").open("w", newline="", encoding="utf-8") as f:
    out = csv.writer(f)
    out.writerow(("symbol", "preferred_owner", "isolated_source", "legacy_symbol", "validation"))
    for path, items in sorted(renames.items()):
        for name, legacy, owner in items:
            out.writerow((name, str(owner), str(path), legacy, "PENDING_GAMEPLAY_VALIDATION"))
print("Experimental non-recoded card symbol isolations:", sum(map(len, renames.values())))
print("Experimental source files:", len(renames))
