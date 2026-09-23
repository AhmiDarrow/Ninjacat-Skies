# Ninjacat Skies 0.8.8 — A quarter of the beds

Pack CurseForge client file **8958894**, server additional **8958897**.

Ninjacat Skies Core 0.5.7, Tribal Power 4.0.1 and Chocobos Reborn 1.0.12. Existing saves load as
they are; no quest ids change, and the mod list is unchanged at 104.

- **Ninjacat Skies Core 0.5.7 - Sleep a quarter** (project 1689718, file **8958302**): the night
  passes when 25% of the players online in a dimension are asleep, rounded up. Vanilla already
  keeps a sleep count per dimension, so Core only sets the share: a new common config key,
  `sleep.playersSleepingPercentage` (default 25, `-1` leaves it alone), is written to the
  `playersSleepingPercentage` gamerule on every server start. `SleepGameTests` covers it.
  Changelog: `cf-changelog-core-0.5.7.md`.
- **End chapter fixed.** `23_end.snbt` had not parsed since 7154d2d (End Apple): the new quest
  `4200000000178001` was spliced in as a header with no task or reward, leaving two brackets open,
  so FTB Quests dropped the chapter ("Unexpected end of file"; 41 of 42 chapters loaded). The quest
  is completed as the generator defines it (one `ninjacatskies:end_apple`, one Frayed Thread, no
  cache), and `Test-QuestConsistency` now fails any chapter whose brackets do not balance.
- **Tribal Power 4.0.1 - One hearth** (project 1684851, file **8958670**), which also brings
  **4.0.0 - The camp answers** (file 8958138): the bestiary
  (54 creatures and the Weeping Colossus), songs, Pulse rebalanced against the pack's power mods,
  one-colour ley, and the carved hearth workshops and totems. The Pulse Adapter is now the
  Harmonic Energizer under the same block id. 4.0.1 finishes the hearth look across every
  placeable and cuts idle chunk writes from generators, conductors and ley bending.
- **Chocobos Reborn 1.0.12 - Sound sleepers** (project 1699008, file **8957838**), which also
  brings 1.0.9 Follow me, 1.0.10 Level field and 1.0.11 Fine feathers to the pack. Whiskerwind's
  beds no longer explode, and nobody sleeps there, so that dimension never holds up the night.

Pins: Ninjacat Skies Core 0.5.7 (project 1689718, file **8958302**), Tribal Power 4.0.1
(project 1684851, file **8958670**), Chocobos Reborn 1.0.12 (project 1699008, file **8957838**).
Client zip carries all 104 mods; the server zip installs 100. Minecraft 1.21.1 / NeoForge
21.1.249 / Java 21.
