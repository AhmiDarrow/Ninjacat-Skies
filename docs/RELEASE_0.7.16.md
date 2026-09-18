# Ninjacat Skies 0.7.16

Hotfix for Clowder Hall. The ceremony pad sits on a chunk corner, so the stall keepers load at different moments; `dock_stalls.js` treated one missed lookup as a missing keeper and spawned another on each visit. It now needs repeated misses with a player at the pad before respawning, and keeps only the keeper nearest each post, which also removes duplicates already in a world.

Pins are unchanged from 0.7.15: Chocobos Reborn 1.0.3 (project **1699008**, file **8908978**), Tribal Power 3.4.2 (project 1684851, file **8908289**), Ninjacat Skies Core 0.4.9 (project 1689718, file **8908462**), FTB XMod Compat 21.1.11 (project 889915, file **8653466**). Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21. CurseForge file type is **release**. Existing quest ids are unchanged.
