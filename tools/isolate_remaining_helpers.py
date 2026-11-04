#!/usr/bin/env python3
"""CI-only isolation of remaining duplicate non-card helper symbols.

Explicit owner map; fail closed if definitions are absent. All competing
function bodies remain in the repository. Runtime behavior is unverified.
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

owners = {
    "dark_confidant_effect": "cards/black_creatures.c",
    "effect_mana_drain": "cards/blue_oneshot.c",
    "initialize_ability_tooltip_names": "functions/ability_icons.c",
    "karoo": "cards/lands.c",
    "maze_of_ith_effect": "cards/recoded_cards.c",
    "monolith": "cards/artifacts.c",
    "pattern_of_rebirth_tutor": "cards/green_enchantments.c",
    "play_land_sound_effect": "cards/lands.c",
    "play_land_sound_effect_force_color": "cards/lands.c",
    "popup": "functions/functions.c",
    "sac_land": "functions/produce_mana.c",
    "spirit_link_effect": "cards/white_enchantments.c",
}
pattern = re.compile(r"(?m)^\s*(?:int|void|char\s*\*|const\s+char\s*\*)\s+([A-Za-z_][A-Za-z_0-9]*)\s*\([^;{}]*\)\s*\{")
sources = {}
for root in (Path("src/cards"), Path("src/functions")):
    for path in sorted(root.glob("*.c")):
        sources[path] = path.read_text(encoding="utf-8", errors="replace")
definitions = defaultdict(list)
for path, content in sources.items():
    for name in set(pattern.findall(content)):
        if name in owners:
            definitions[name].append(path)

changes = defaultdict(list)
for name, owner_name in owners.items():
    preferred = Path("src") / owner_name
    found = definitions[name]
    if preferred not in found or len(found) != 2:
        raise SystemExit(f"Unexpected owners for {name}: {found}; expected {preferred} and one alternative")
    loser = next(path for path in found if path != preferred)
    new_name = f"{name}_legacy_ci_{loser.stem}"
    if new_name in sources[loser]:
        raise SystemExit(f"Legacy name collision: {new_name}")
    changes[loser].append((name, new_name, preferred))

for path, changes_here in changes.items():
    content = sources[path]
    include = re.search(r'(?m)^#include\s+"manalink\.h"[^\n]*\n', content)
    if not include:
        raise SystemExit(f"Cannot safely inject helper isolation in {path}: no manalink.h")
    macros = "\n".join(f"#define {name} {legacy}" for name, legacy, _ in changes_here)
    content = content[:include.end()] + "/* CI-only provisional helper ownership; verify callers at runtime. */\n" + macros + "\n" + content[include.end():]
    path.write_text(content, encoding="utf-8")

with Path("experimental-helper-ownership.csv").open("w", newline="", encoding="utf-8") as output:
    writer = csv.writer(output)
    writer.writerow(["symbol", "preferred_owner", "isolated_source", "legacy_symbol", "validation"])
    for path, changes_here in sorted(changes.items()):
        for name, legacy, preferred in changes_here:
            writer.writerow([name, str(preferred), str(path), legacy, "PENDING_RUNTIME_VALIDATION"])
print(f"CI-only helper isolations: {sum(map(len, changes.values()))}")
