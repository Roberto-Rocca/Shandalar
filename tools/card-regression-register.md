# Shandalar — regression test register

This file is the durable project record for changes reviewed in the recent diagnostic sessions. Test with the exact patched Magic.exe used by the project. A successful linker result is not gameplay validation.

## Classic card source ownership (public handler from recoded_cards.c)

| Card | Intervention | Status / specific checks |
| --- | --- | --- |
| Time Walk | Renamed conflicting Unlimited implementation; original executable address binding added | Test extra turn and Stranglehold |
| Rock Hydra | Renamed conflicting Unlimited implementation; original executable address binding added | Test X counters, damage prevention, upkeep activation and AI |
| Volcanic Eruption | Renamed conflicting Unlimited implementation | Test land targets, subtype-changing effects, spell copying and Gaddock Teeg |
| Raise Dead | Renamed conflicting Unlimited implementation | Test selecting creatures from graveyard, shroud and resolution |

## Original-executable address / wrapper experiments

| Card | Intervention | Status / specific checks |
| --- | --- | --- |
| Demonic Tutor | Original EXE entry point added to linker script | Test tutor selection and Stranglehold |
| Giant Spider | Original EXE entry point added | Test blocking and special ability handling |
| Battering Ram | Original EXE entry point added | Test combat-phase banding |
| Tawnos's Weaponry | Original EXE function/symbol binding added | Test activated effects and calling convention |
| Ashnod's Transmogrant | Original EXE entry point added | Test activation and counters |
| Pentavite | Earlier diagnostic substituted an unavailable `is_aura` helper with an explicit aura subtype check | Test the relevant Pentavite interaction; review historical commit to identify complete behavior context |

## Batch generated changes

The CI artifact `recoded-batch-renames.csv` from the bulk diagnostic build lists every *additional* card symbol with an isolated alternative implementation. Merge that list into regression coverage after confirming that the build's source ownership and dispatch are correct.

## Important distinctions

- Items above are confirmed from the available project conversation and examined commits; this is not asserted to be an exhaustive record of every earlier experiment.
- `src/cards/recoded_cards.c` is the preferred handler when a duplicate is present there.
- Legacy handlers are preserved in repository sources; batch names are altered in the CI checkout only.
- Check `CSV/Magic.exe.Cards.csv`, Manalink dispatch IDs and the patched Magic.exe addresses before declaring a card fixed.
- Runtime validation remains pending for every card listed here.

## Unresolved-symbol regression targets (run 41420176092)

The automated source-candidate scan completed on 214 source/header files. Its candidate list is **not** evidence that similarly named functions are ABI-compatible.

| Card / subsystem | Missing symbol | What to check before patching |
| --- | --- | --- |
| Wall of Roots | `add_0_minus1_counters` | Uses 0/-1 counters rather than -1/-1 counters; validate exact counter type and once-per-turn mana activation |
| Dryad Arbor | `colored_artifact` | Suspicious call: Dryad Arbor is a green land creature, **not an artifact**; review intent rather than inventing an alias |
| Animate Dead | `hack_animate_dead_player`, `hack_animate_dead_card` | Locate original storage and lifetime before replacing globals |
| Goblin Shrine | `card_goblin_shrine_exe` | Confirm EXE entry point and correct patched binary before any linker mapping |
| Fork | `card_fork_orig` | Confirm original dispatch and copied spell behavior before mapping |
| Other card damage interactions | `damage_dealt_to_me` | Compare existing `damage_dealt_to_me_arbitrary` signature and trigger semantics |
| Artifact/card play effect | `can_legally_play` | Determine whether stored identifier is internal card ID, CSV ID, or something else before using `can_legally_play_iid` |
| Black sorcery effect | `effect_coercion` | Compare effect semantics with `new_effect_coercion` and its parameter structs |

All items remain **untested in gameplay**. The batch owner selection is temporary in CI and requires dispatch/EXE validation.

## 2026-11-02 — targeted Dryad Arbor source correction

- Removed the call to undefined `colored_artifact()` from `card_dryad_arbor()` in `src/cards/lands.c`. Dryad Arbor is a green land creature, not an artifact.
- Preserved `mana_producer_fixed(..., COLOR_GREEN)`; no other event handling changed.
- **Validate in-game**: green color, land + creature types, summoning sickness, green mana production, interactions with artifact-only effects. Card data must be checked separately.
- Upstream cross-check: `ShandalarMagic/Shandalar` retains this unresolved call, so this is a reasoned corrective divergence, **not** a verbatim upstream reconstruction.

## 2026-11-02 — Wall of Roots counter correction

- Replaced unavailable `add_0_minus1_counters(player, card, 1)` with `add_counters(player, card, COUNTER_M0_M1, 1)`, using the existing exact `COUNTER_M0_M1` enum in `src/defs.h`.
- Verify -0/-1 counter accumulation, toughness updates, mana timing and once-per-turn activation, especially across turn boundaries. Compilation is not gameplay validation.
