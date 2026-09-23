# 0.8.8 — A quarter of the beds

Ninjacat Skies Core 0.5.7, Tribal Power 4.0.1 and Chocobos Reborn 1.0.12. Existing saves load
as they are, no quest ids change, and the mod list is unchanged at 104.

- **A quarter of a dimension sleeping passes the night.** The night now passes when **25% of the
  players online in that dimension** are asleep, rounded up: one sleeper is enough for up to four
  players, two for five to eight. Players in the Nether, the End or any other dimension are not counted
  against the Overworld's beds. Server owners can change the share with
  `sleep.playersSleepingPercentage` in `ninjacatskies-common.toml`, or set it to `-1` to manage
  the `playersSleepingPercentage` gamerule yourself.
- **The End chapter is back.** Since the End Apple was added, a half-written quest had broken the
  End chapter's quest file, and FTB Quests skipped the whole chapter. The **End Apple** quest is
  finished (bring one End Apple) and every End quest shows again. Progress on those quests was
  never lost; their ids did not change.
- **Tribal Power 4.0.0 and 4.0.1 — The camp answers, One hearth.** Fifty-four new creatures and the Weeping Colossus;
  the Song Bench, songbooks, the Reagent Pouch and the Pulse Bow; Pulse rebalanced against Powah,
  Mekanism, Solar Flux and Create Crafts & Additions, with the Pulse Adapter now the Harmonic
  Energizer (300 FE a tick) and a Lattice Converter to turn FE back into Pulse at a loss; one-colour
  ley lines that totems bend; a five-sight Ley Lens; Lattice Conductors; the Tribal Bench; and the
  hearth workshops and totems carved in wood, stone and copper. Twelve creatures that had been
  dropping nothing drop again. Existing Pulse Adapters keep their block id. 4.0.1 gives the rest of the
  workshop row and every placeable the same hearth stone, wood and copper, and makes a standing camp
  cheaper to run: ley lines skip veins that cannot reach you, and full generators and idle Lattice
  Conductors stop rewriting their chunk every second. Pulse numbers are unchanged.
- **Chocobos Reborn 1.0.9 to 1.0.12.** A new tame follows you, across dimensions too. Races run
  smoother, with distant birds drawn lighter and each rider's ping credited at the finish line, so
  host and guests race on equal terms. Tame birds shed feathers and can be brushed. Greens heal a
  full bird that is hurt. Whiskerwind's beds are furniture now and no longer explode.

**Server owners:** the server zip still leaves out the four client-only mods (Sodium, Reese's,
BadOptimizations, Dynamic FPS); clients get all 104, servers 100. Unzip the new server pack over
the old folder and run `install` again. The sleep rule is set when the server starts, so an
existing world picks it up on its first boot on 0.8.8.

Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21.
