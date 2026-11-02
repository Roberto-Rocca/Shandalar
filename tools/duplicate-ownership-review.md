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

## Precedence policy confirmed by historical developer discussions

Default owner for duplicate card symbols: **`cards/recoded_cards.c` takes precedence** over expansion files, pending compatibility checks. Preserve the other implementation in source until its dependencies and callers are understood; do not delete it reflexively.

Historical supporting sources:
- Gargaroz, 12 Dec 2011: several basic cards were recoded to work with added rules (especially subtype boosts and +1/+1 counters), and explicitly identifies `recoded_cards.c`. https://slightlymagic.net/forum/viewtopic.php?f=56&start=195&t=5815
- Gargaroz, 15 May 2013: if a card is not in `recoded_cards.c`, look in its expansion source, since it was not recoded. https://slightlymagic.net/forum/viewtopic.php?p=118187
- Gargaroz, 10 Oct 2011: recoded cards are located in `recoded_cards.c`. https://slightlymagic.net/forum/viewtopic.php?p=72807

Caveat: historical discussions also note some recoded implementations were not enabled in dispatch. This is a *default preference*, not proof that every function is runtime-correct. Verify the executable and dispatch mapping prior to adopting a replacement.

## Safe workflow

1. For each duplicate, compare both function bodies and caller expectations.
2. Determine whether either implementation is a wrapper around `Magic.exe` or a standalone replacement.
3. Check executable addresses against the exact patched `Magic.exe`; a passing link does not validate addresses.
4. Verify rule behavior and exported dispatch mappings before disabling any competing implementation.
5. Change only one reviewed symbol at a time and run diagnostics and gameplay checks.

No source implementation has been removed or changed by this review.
