# Duplicate ownership: initial gameplay review

Source: GitHub Actions run 41411487376 (linker-symbol-audit).
This is a review document, NOT a request to merge or suppress definitions.

## Build status
- 303 distinct duplicate symbols (292 card/effect symbols and 11 other symbols).
- 9 unresolved symbol names.
- Largest conflict pair: `cards/recoded_cards.c` vs `cards/unlimited.c` (43 symbols).

## Examples requiring behavioral review

| Symbol | Source A | Source B | Observed semantic difference | Decision |
| --- | --- | --- | --- | --- |
| `card_time_walk` | `cards/recoded_cards.c` | `cards/unlimited.c` | Recoded version blocks extra-turn resolution when opponent controls Stranglehold, then calls an original EXE entry point; Unlimited implementation calls `time_walk_effect` directly. | Do not suppress either definition until turn-extra and Stranglehold behavior is validated. |
| `card_rock_hydra` | `cards/recoded_cards.c` | `cards/unlimited.c` | Recoded version sets counters on resolution and delegates other events to the EXE; Unlimited version handles counters and activation logic locally. | Compare X, damage prevention, activation restrictions and AI before selecting an owner. |

## Safe workflow

1. For each duplicate, compare both function bodies and caller expectations.
2. Determine whether either implementation is a wrapper around `Magic.exe` or a standalone replacement.
3. Check executable addresses against the exact patched `Magic.exe`; a passing link does not validate addresses.
4. Verify rule behavior and exported dispatch mappings before disabling any competing implementation.
5. Change only one reviewed symbol at a time and run diagnostics and gameplay checks.

No source implementation has been removed or changed by this review.
