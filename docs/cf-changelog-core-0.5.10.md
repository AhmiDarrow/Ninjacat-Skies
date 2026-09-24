# Ninjacat Skies Core 0.5.10

**Your things wait in a basket, Thread comes in skeins and bolts, and Steward Caches are worth opening.** Existing saves load as they are; no ids change. This replaces 0.5.8 and 0.5.9, which never shipped in a pack.

**The Yarn Basket**

- **When you die, everything you drop goes into a Yarn Basket** where you fell: a wicker basket of yarn balls, not a scatter of items. That includes your Curios slots. If you fell into the void, it waits where you last stood. You get a chat line saying where it is.
- **Right-click it to take everything back** into your inventory, or break it to spill it on the ground. Right-click works even where breaking is protected, like the Dock and the Hall.
- **It is yours and your Clowder's.** Anyone else gets a polite no, and can neither open it nor break it. It shrugs off explosions and pistons, and never despawns.
- Deaths on a Guardians stage or in a rift are handled as before: those drops still come home with you.
- Server owners can switch it off with `hardcore.yarnBasket` in `ninjacatskies-common.toml`.

**Thread Skeins and Thread Bolts**

- A **Thread Skein** is nine Frayed Thread wound together, and a **Thread Bolt** is nine skeins (81 Thread). Both craft in a full grid and unwind back into nine of the smaller piece at any time.
- They exist because a trade slot holds one stack. A stall price above 64 used to be cut to 64 without saying so, so the big Spark stall prices are now paid in skeins and bolts.

**Steward Caches**

- **Twice the parcels, and more of them worth having.** A small cache is now 4 parcels, a medium 8 and a large 17. Supplies lean better: copper, iron and Thread in smalls; ingots, gold, redstone, lapis and experience in mediums; diamonds, emeralds, ender pearls, obsidian or a Thread Skein in larges.
- **The garden.** Every cache rolls saplings of every vanilla tree, seeds, crops, plants and flowers, and sometimes a **spawn egg** — chicken, cow, pig and sheep most often, since a pad has no other way to get them. Medium and large caches add rabbits, bees, goats, turtles, frogs, cats, wolves, horses, donkeys, llamas, mooshrooms, parrots, foxes, pandas, axolotls and armadillos.
- **Decor.** Candles, lanterns, frames, paintings, carpets, banners, glass, terracotta, sea lanterns, dyes and more.
- **A piece of a life.** Every cache also makes one rare draw: a **Thread Shard** at 1.5% / 4% / 12% (small / medium / large), or a whole **Thread of Return** at 0.2% / 0.5% / 1.5%. Bigger caches always have better odds.
- Still no machines, progression tokens, caches or hostile eggs inside a cache.

1.21.1 / NeoForge 21.1.249.
