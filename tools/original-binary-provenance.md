# Binary provenance investigation — 2026-11-02

## Evidence from user-provided archive (static inspection only)

Archive: `chatgpt.zip`. No executable was run or uploaded to this repository.

- `bin/Magic.exe`: 3,186,688 bytes; PE32 i386; `.text` starts at virtual address `0x401000`; `.cards` starts at `0x7e7000` (consistent with existing `_cards_data = 0x7E7010` linker mapping).
- `bin/ManalinkEh.dll`: 6,587,465 bytes; PE32 i386; reported PE linker timestamp 2016-08-26. The archive's filesystem date is 2025 and is **not** proof of when the DLL was built.
- DLL COFF symbol table (as printed by GNU `objdump -t`) contains `_card_fork`, `_card_goblin_shrine`, `_card_animate_dead`, and `_damage_dealt_to_me_arbitrary`. These are internal COFF symbols; **they are not DLL exports**. Its PE export table only names `CodeSectionEx` and `DllEntry`.
- Symbols `card_fork_orig`, `card_goblin_shrine_exe`, `hack_animate_dead_player`, `hack_animate_dead_card`, `damage_dealt_to_me` are not provided by `src/manalink.lds` on `diagnostics/32bit-build`.
- `MAGIC*.map` in the archive are binary game data, not readable linker symbol maps.

## Conclusions and constraints

1. The COFF table provides a useful disassembly starting point for the DLL's compiled card functions, but **their addresses in the DLL cannot be copied into `manalink.lds` as `Magic.exe` function addresses**.
2. Do **not** bind `card_fork_orig` or `card_goblin_shrine_exe` to the entry points of `_card_fork` and `_card_goblin_shrine` in the DLL: that risks calling the replacement recursively and ignores distinct image base addresses.
3. Confirm intended reanimation state-sharing before introducing standalone definitions for `hack_animate_dead_player` and `hack_animate_dead_card`.
4. For Illusionary Mask, review precise event/trigger semantics before substituting `damage_dealt_to_me_arbitrary`.
5. First verify the build and patch variant associated with the binary pair. Do not assume the archived 2016 DLL exactly matches current source.
6. Runtime regression tests of all touched card handlers remain necessary even after a successful link.

## Suggested reproducible inspection (Linux, read-only)

```sh
objdump -h Magic.exe
objdump -h ManalinkEh.dll
objdump -t ManalinkEh.dll | grep -E '_card_(fork|goblin_shrine|animate_dead)$|_damage_dealt_to_me_arbitrary$'
objdump -p ManalinkEh.dll
```

These checks are informational only. No gameplay modifications or arbitrary EXE addresses were introduced.
