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
