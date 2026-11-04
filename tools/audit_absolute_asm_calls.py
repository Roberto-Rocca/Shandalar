#!/usr/bin/env python3
"""Fail CI when NASM/YASM sources contain numeric direct calls or jumps.

In x86, 'call 0x4352D0' in NASM is relative, not an absolute call
to Magic.exe; use a memory-indirect call through an address cell.
"""
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parents[1] / "src"
bad = []
pattern = re.compile(r"^\s*(?:call|jmp)\s+(?:0x[0-9a-f]+|[0-9]+)\b", re.I)
for path in root.rglob("*.asm"):
    for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        code = line.split(";", 1)[0]
        if pattern.match(code):
            bad.append(f"{path.relative_to(root)}:{number}: {line.strip()}")
if bad:
    print("Unsupported direct numeric CALL/JMP (relative target):")
    print("\n".join(bad))
    sys.exit(1)
print("PASS: no direct numeric CALL/JMP in src/**/*.asm")
