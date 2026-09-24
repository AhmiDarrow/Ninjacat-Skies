# Steward caches

The Nine Tribes set aside provisions for the Clowders who would follow. These sealed parcels reward steady progress without handing out machinery or bypassing the Loom.

- **Small:** two weighted supply rolls: bread, torches, bone meal, string, clay, saplings, seeds and leather, and about one roll in four copper, iron or Frayed Thread.
- **Medium:** five rolls; roughly half are the better pool: iron and copper ingots, gold, redstone, lapis, bottled experience and Frayed Thread.
- **Large:** twelve rolls; roughly three in five are better: ingots, redstone, lapis, experience, and a chance of diamonds, emeralds, ender pearls, obsidian or a Thread Skein.
- **The garden:** one roll in a small cache, two in a medium, three in a large: saplings of every vanilla tree, seeds, crops (potato, carrot, cane, cactus, bamboo, berries, cocoa, kelp, mushrooms, nether wart), plants and flowers, and **passive vanilla spawn eggs**. A pad has no other way to get a chicken, cow, pig or sheep, so those four carry most of the egg share, which is about 9% / 12% / 15% of a garden roll. Medium and large seals add rabbits, bees, goats, turtles, frogs, cats, wolves, horses, donkeys, llamas, mooshrooms, parrots, foxes, pandas, axolotls and armadillos.
- **Decor:** one roll in a small or medium cache, two in a large: candles, lanterns, frames, paintings, carpets and wool, banners, glass, terracotta, a decorated pot, sea lanterns, dyes and the like.
- **The rare draw:** every seal also makes one draw on its own: a **Thread Shard** at 1.5% / 4% / 12% (small / medium / large), or a whole **Thread of Return** at 0.2% / 0.5% / 1.5%. Across a campaign's ~530 caches that is about eleven Shards and one and a half whole Threads on average.

![The three Steward cache sizes in Minecraft](images/steward-cache-models.png)

Use a cache to unwrap it. Rolls can repeat; a particular item is never guaranteed. Four unopened small caches craft into one medium; three unopened mediums craft into one large. Combining trades some total basic-supply rolls for a broader pool and denser parcels. There is no downgrade recipe and opened supplies cannot be repacked.

The pools contain no machines, equipment, progression tokens, caches or hostile spawn eggs. They do not drop from mobs. The rare draw is the only way a cache touches a life; the six milestone rewards still grant the campaign's guaranteed shared lives. The ten older, tribe-specific milestone caches keep their separate themed loot pools.

The 0.6.1 audit found 1,441 of 1,495 quests awarding Threads, with 1,211 awarding only Threads. Version 0.6.2 adds 381 small, 104 medium and six large caches across 491 quests. Existing Thread rewards and the repeatable Desk shop are unchanged. Every third eligible quest within a chapter receives a cache; occasional larger parcels replace that small-cache allocation. The first cache in each chapter explains the system.

## Existing worlds

All existing quest, task and reward identifiers are retained. New cache rewards have new identifiers, so completed quests may offer their newly added cache without resetting progress or reopening previously claimed rewards. The three item registrations are additive. World, team, life and island data formats are unchanged. Update the server and all clients together.

## Implementation and validation

`StewardCacheItem` rolls the datapack loot table on the server before consuming one sealed cache. A missing or empty table preserves it. A short use cooldown guards rapid repeated opening. Inventory overflow drops at the player's feet. Survival consumes one cache; creative follows Minecraft's normal item-consumption rules.

Loot pools are written by `tools/generate_provisions.py` into `data/ninjacatskies/loot_table/provisions`, combining recipes in `data/ninjacatskies/recipe`, and recipe-book unlocks in `data/ninjacatskies/advancement/recipes/misc`. Models use native Minecraft cuboids, woven wood, colored bands and the existing animated Loom seal.

`tools/gates/test_steward_caches.py` checks bounded allowlisted supplies, combining inputs, reward distribution, preserved Thread awards and the complete pre-update quest-object identifier digest. Server GameTests open all three tiers and exercise cooldown and full-inventory behavior.
