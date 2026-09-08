# Ninjacat Skies 0.6.2-alpha — Steward provisions

- Added small, medium and large Steward caches with distinct woven-parcel models and animated Loom seals.
- Added 491 cache rewards across the existing questline: 381 small, 104 medium and six large. Thread currency and existing special rewards remain intact.
- Use a cache for randomized, modest supplies: food, growing and building materials, with broader pools in larger caches. No machines, progression tokens or extra lives in these new caches.
- Craft four small caches into a medium and three mediums into a large. Small/medium/large caches provide 2/5/12 supply rolls; combining trades some basic quantity for broader loot. Recipes unlock in the recipe book when the source cache is collected.
- Server-controlled opening consumes one cache, handles full inventories by dropping overflow, and preserves caches if a datapack removes their loot.

Save compatibility: all existing quest, task and reward IDs are preserved, as are world, island, team and life data. Completed quests can offer their newly added cache rewards. No reset is required. Update clients and servers together.

Validation: companion-mod builds and all seven server GameTests pass, including all three cache tiers and inventory overflow. Reward balance, existing quest IDs, life rewards, item references and pack/export gates pass. A full-pack client connected to the verification server and rendered all three new cache models successfully.

Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21. Companion mods 0.3.2; Tribal Power remains 2.3.0.
