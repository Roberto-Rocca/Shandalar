#!/usr/bin/env python3
"""Read-only audit of the legacy Manalink card table and source references."""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID_HEADER = ROOT / "Program/src/card_id.h"
CURRENT_CSV = ROOT / "CSV/Magic.exe.Cards.csv"
SRC = ROOT / "src"
CARD_ID_PATTERN = re.compile(r"\b(CARD_ID_[A-Z0-9_]+)\b")
DEFINITION_PATTERN = re.compile(r"\b(CARD_ID_[A-Z0-9_]+)\s*=\s*(\d+)\b")


def inspect_csv(path):
    print(f"\nCSV: {path.relative_to(ROOT)}")
    if not path.exists():
        print("  MISSING")
        return
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        sample = handle.read(32768)
        handle.seek(0)
        delimiter = ";" if sample.count(";") > sample.count(",") else ","
        rows = csv.reader(handle, delimiter=delimiter)
        header = next(rows, [])
        print(f"  delimiter: {delimiter!r}; columns: {len(header)}")
        print(f"  first columns: {header[:10]}")
        count, bad_width, min_id, max_id = 0, 0, None, None
        for row in rows:
            if not row or not any(cell.strip() for cell in row):
                continue
            count += 1
            bad_width += len(row) != len(header)
            if row[0].strip().isdigit():
                value = int(row[0].strip())
                min_id = value if min_id is None else min(min_id, value)
                max_id = value if max_id is None else max(max_id, value)
        print(f"  data rows: {count}; inconsistent widths: {bad_width}")
        print(f"  first-column numeric ID range: {min_id} .. {max_id}")
        if not (len(header) == 221 and delimiter == ";" and header[0].strip().upper() == "ID"):
            print("  NOTE: not verified as the original 221-column Manalink.csv input")
        else:
            print("  Layout matches the header structure of historical Manalink.csv (not a conversion validation)")


def main():
    text = ID_HEADER.read_text(encoding="utf-8", errors="replace")
    definitions = {name: int(number) for name, number in DEFINITION_PATTERN.findall(text)}
    print(f"card_id.h enumerators: {len(definitions)}")
    values = {}
    for name, number in definitions.items():
        values.setdefault(number, []).append(name)
    duplicates = {k: v for k, v in values.items() if len(v) > 1}
    print(f"duplicate numeric IDs: {len(duplicates)}")
    for number, names in sorted(duplicates.items())[:20]:
        print(f"  {number}: {', '.join(names)}")

    references = {}
    for path in sorted(SRC.rglob("*")):
        if path.suffix not in {".c", ".cpp", ".h"}:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        for name in set(CARD_ID_PATTERN.findall(source)):
            if name not in definitions:
                references.setdefault(name, []).append(str(path.relative_to(ROOT)))
    print(f"\nSource card ID symbols not defined by Program/src/card_id.h: {len(references)}")
    for name, paths in sorted(references.items()):
        print(f"  {name}: {', '.join(paths[:5])}" + (" ..." if len(paths) > 5 else ""))
    inspect_csv(CURRENT_CSV)
    print("\nThis is an inventory only. It does not renumber cards or write .dat files.")


if __name__ == "__main__":
    main()
