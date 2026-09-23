# Ninjacat Skies Core 0.5.7

**A quarter of a dimension sleeping passes the night.** Existing saves load as they are; no ids change.

- The night passes when **25% of the players online in that dimension** are asleep, rounded up, so one sleeper is enough for up to four players. Players in the Nether, the End or anywhere else are not counted against the Overworld's beds.
- Core writes this to the vanilla `playersSleepingPercentage` gamerule every time the server starts. The share is `sleep.playersSleepingPercentage` in `ninjacatskies-common.toml`; set it to `-1` and Core leaves the gamerule alone, so `/gamerule` works again.

1.21.1 / NeoForge 21.1.249.
