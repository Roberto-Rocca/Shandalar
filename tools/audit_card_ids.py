#!/usr/bin/env python3
"""Read-only audit of the legacy Manalink card table and source references."""
import csv
import json
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


def normalize_card_name(value):
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def crosscheck_card_names(symbols):
    """Look for exact normalized card-name matches, without inferring an ID."""
    result = {}
    with CURRENT_CSV.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        if not {"Card Name", "Card ID", "Card#"}.issubset(reader.fieldnames or []):
            return result
        by_name = {}
        for row in reader:
            key = normalize_card_name(row.get("Card Name", ""))
            if key:
                by_name.setdefault(key, []).append({
                    "card_name": row.get("Card Name", ""),
                    "card_id_field": row.get("Card ID", ""),
                    "card_number": row.get("Card#", ""),
                })
    for symbol in sorted(symbols):
        key = normalize_card_name(symbol.removeprefix("CARD_ID_"))
        result[symbol] = by_name.get(key, [])
    return result


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
    # Keep source locations for a reviewable, machine-readable inventory.
    detail = {}
    for path in sorted(SRC.rglob("*")):
        if path.suffix not in {".c", ".cpp", ".h"}:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for symbol in set(CARD_ID_PATTERN.findall(line)):
                if symbol not in definitions and symbol != "CARD_ID_H":
                    detail.setdefault(symbol, []).append({
                        "path": str(path.relative_to(ROOT)),
                        "line": lineno,
                        "source": line.strip()[:240],
                    })
    csv_matches = crosscheck_card_names(detail)
    matched_symbols = [name for name, rows in csv_matches.items() if rows]
    print(f"Exact normalized card-name matches in current CSV: {len(matched_symbols)} / {len(detail)}")
    for name in matched_symbols:
        print(f"  {name}: " + ", ".join(f"{row['card_name']} (CSV Card ID {row['card_id_field']})" for row in csv_matches[name][:4]))
    report = {
        "csv_card_name_matches": csv_matches,
        "defined_ids": len(definitions),
        "duplicate_numeric_ids": duplicates,
        "unresolved_symbols": detail,
        "limitations": [
            "Lexical scan: comments, disabled preprocessor branches and macro tokens may be listed.",
            "A missing ID is not evidence that a new numeric ID may safely be assigned.",
            "CSV column shape differs from historical Manalink.csv: no conversion is attempted.",
        ],
    }
    out = ROOT / "card-id-audit.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nWrote detailed audit: {out.name}, {len(detail)} unresolved symbols (excluding header guard)")
    print("References in rules_engine.c requiring manual review:")
    for symbol, locations in sorted(detail.items()):
        matches = [p for p in locations if p["path"] == "src/functions/rules_engine.c"]
        if matches:
            print(f"  {symbol}: " + ", ".join(str(p["line"]) for p in matches))
    inspect_csv(CURRENT_CSV)
    print("\nThis is an inventory only. It does not renumber cards or write .dat files.")


if __name__ == "__main__":
    main()
