# Ninjacat Skies Core

**CurseForge summary (one line):** The companion mods of the Ninjacat Skies skyblock pack in one jar: the Codex, shared Clowder lives, Voidloom, Clowder Hall, the Snapped Guardians and Driftwrecks.

The companion mods of the [Ninjacat Skies](https://www.curseforge.com/minecraft/modpacks/ninjacat-skies) skyblock modpack, packaged as one download so the pack can install them straight from CurseForge.

## What's inside

Six mods, loaded through NeoForge's Jar-in-Jar system. Each keeps its own mod id, so existing worlds are unaffected.

- **Ninjacat Lib** – shared utilities for the others: text, block plans and a build queue that raises large structures a slice at a time.
- **Ninjacat Skies** – the Whisker Codex guide book, Skybound starter kits, the Tension Post the Strand story is seated on, shared Clowder lives, the Yarn Basket, Steward Caches, and the small rules a skyblock server wants (see below).
- **Voidloom** – void yarn, spindle tools and Loomframe sieving.
- **Clowder Hall** – the hub ceremony, island charters and the Clowder multiplayer layer, which keeps skyblock island teams and FTB parties in sync.
- **Snapped Guardians** – thirteen bosses summoned with Frayed Totems and fought in their own arenas. Each one drops a unique Woven Relic.
- **Driftwrecks** – pieces of the old world that drift up to your Clowder's pad, hold for a while and unravel. Every wreck is assembled when it arrives, from a deck shape, a core place, a scatter of ruins and sometimes islets, so no two drift in alike. Cross on a Tether Spool bridge, finish its objective, and bring home Salvaged Weft, lore pages for the Wreck Atlas and Keepsakes. Hold wrecks hide sealed rifts with nine Remnants.

## Life on the pad

- **Shared lives.** A Clowder shares one pool of lives; every survival death spends one, and at zero the team spectates until an operator revives it. Six milestones across the campaign each add a life. Past those, the only repeatable life is a **Thread of Return**: four Thread Shards around a Braid Cord, spun at a Tension Post from sixteen Strand Filaments.
- **The Yarn Basket.** When you die, everything you drop, Curios included, goes into a wicker basket of yarn balls where you fell, or where you last stood if you fell into the void. Right-click it to take it all back, or break it to spill it. Only you and your Clowder can; it shrugs off explosions and pistons and never despawns.
- **A Dismount key.** Sneak no longer throws you out of the saddle, so it is free to steer what you ride (a chocobo descends on sneak). Press **Caps Lock** (rebindable) to get off anything you ride.
- **Steward Caches.** Sealed provisions the Nine Tribes left, in three sizes. Each rolls supplies, a garden parcel (saplings, seeds, crops, flowers and passive spawn eggs, since a pad has no other way to get a chicken or a cow), a decoration, and one rare draw for a Thread Shard or a whole Thread of Return. Four small caches craft into a medium, three mediums into a large; bigger seals always have the better odds.
- **Thread.** Frayed Thread is the pack's currency at the Clowder Hall stalls. A **Thread Skein** is nine Thread and a **Thread Bolt** nine skeins, so big prices fit in one trade slot; both unwind again in a crafting grid.
- **The End Apple.** Five ender pearls, two bones and two blaze powder. The first bite drops you on the End's obsidian pad; eating the bitten half brings you home to the spot you ate from.
- **A quarter of the beds.** The night passes when 25% of the players online in a dimension are asleep, rounded up: one sleeper for up to four players.

## Driftwrecks at a glance

- **Arrivals.** Once a Clowder tensions Soil, Drift pressure fills with its online time and a wreck arrives 160–320 blocks from the Tension Post. A Driftlure calls one early.
- **Five objectives.** Open the heart chest, break the frayed spawners, re-thread the pillars in the idol's order, walk a Steward echo home, or hold the seam through three waves.
- **Fair loot.** Every chest rolls separately for each player. When a wreck unravels nobody falls, anything left behind comes home in a Salvage Bundle, and blocks you placed stay.
- **The Wreck Atlas.** Nine Strands by six places, with a Codex page for each and small permanent perks for full rows and columns. Fill it and the Heartwreck arrives, once.

## For server owners

- `ninjacatskies-common.toml`: `hardcore.livesEnabled` and `startingLives`; `hardcore.yarnBasket`; `controls.sneakDismounts` (vanilla sneak-to-dismount back); `sleep.playersSleepingPercentage` (-1 leaves the gamerule alone); `loom.frayEnabled` and `sunderedSky` for the sky.
- `driftwrecks-server.toml` sets pacing, distances and lifetime, and can turn the feature off. `/driftwreck` has admin commands; `/skybound` manages lives.
- **Translatable.** Every line a player reads, from chat and tooltips to the whole Whisker Codex, lives in lang files. Translations are welcome on GitHub.

## Requirements

- Minecraft 1.21.1 with NeoForge 21.1.249 or newer, Java 21.
- No other required mods. Optional integrations: FTB Quests, FTB Teams, Skyblock Builder, Ex Deorum, Productive Bees, Curios, Modonomicon, Jade and Just Enough Resources.

## Made for the pack

These mods are built around the Ninjacat Skies quests, recipes and configs. They load on their own, but the intended way to play them is the modpack.

Source and issue tracker: [github.com/AhmiDarrow/Ninjacat-Skies](https://github.com/AhmiDarrow/Ninjacat-Skies)
