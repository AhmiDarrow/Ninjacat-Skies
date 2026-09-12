# Ninjacat Skies Core 0.4.4

- Hovering Just Enough Resources mob-loot slots in JEI no longer hard-crashes the client. JER 1.6.0.17 names every grid cell and runs `drops.get(slotIndex)` on empty cells (`IndexOutOfBoundsException` at `MobTooltip.onTooltip`). Core now skips those empty cells.

CurseForge project 1689718, file **8866486**.
