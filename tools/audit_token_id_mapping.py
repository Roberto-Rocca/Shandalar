#!/usr/bin/env python3
"""Read-only cross-check of card identifiers against available game databases."""
import csv
import re
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[1]
header = (root / "Program/src/card_id.h").read_text(encoding="utf-8")
ids = {key: int(value) for key, value in re.findall(r"\b(CARD_ID_[A-Z0-9_]+)\s*=\s*(\d+)\b", header)}
for key in ("CARD_ID_GOBLIN", "CARD_ID_GOBLIN_ASSAULT", "CARD_ID_IMMOBILIZER_ELDRAZI", "CARD_ID_RULES_ENGINE", "CARD_ID_DEADBOX"):
    print("HEADER", key, ids.get(key, "NOT_DEFINED"))

for relative in ("Cards.dat", "Program/Cards.dat", "DBInfo.dat", "Program/DBInfo.dat"):
    path = root / relative
    if not path.is_file():
        continue
    data = path.read_bytes()
    count = struct.unpack_from("<I", data)[0] if len(data) >= 4 else None
    print("BINARY", relative, "bytes", len(data), "count_prefix", count)
    if "DBInfo" in relative and count is not None:
        print("DBINFO_16_BYTE_RECORD_LAYOUT", len(data) == 4 + count * 16)
    if "Cards" in relative:
        for needle in (b"Immobilizer Eldrazi", b"Goblin Assault"):
            print("BINARY_NAME_OFFSET", relative, needle.decode(), data.find(needle))

for relative in ("CSV/Magic.exe.Cards.csv", "magic_updater/Manalink.csv", "Program/magic_updater/Manalink.csv", "Manalink.csv"):
    path = root / relative
    if not path.is_file():
        continue
    with path.open(encoding="latin1", newline="") as handle:
        sample = handle.read(16384)
        handle.seek(0)
        delimiter = ";" if sample.count(";") >= sample.count(",") else ","
        rows = csv.reader(handle, delimiter=delimiter)
        columns = next(rows, [])
        print("CSV", relative, "columns", len(columns), "first_headers", columns[:12])
        matches = []
        count = 0
        for row in rows:
            if not row:
                continue
            count += 1
            line = " ".join(row[:8]).lower()
            if any(term in line for term in ("immobilizer eldrazi", "goblin assault")) or any(v.strip() == "15615" for v in row[:5]):
                matches.append((count, row[:12]))
        print("CSV_ROWS", relative, count)
        for index, row in matches[:25]:
            print("CSV_MATCH", relative, index, repr(row))
print("Read-only audit complete. No database or ID modifications.")
