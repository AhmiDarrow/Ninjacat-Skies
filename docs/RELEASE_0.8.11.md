# Ninjacat Skies 0.8.11 — Piled stones

Pack CurseForge client file **TBD**, server additional **TBD**.

Tribal Power 5.3.2. Existing saves load as they are; no quest ids change, and the mod list is
unchanged at 104.

- **Tribal Power 5.3.2 - Bound stones** (project 1684851, file **8973651**; it carries 5.3.1, file 8973496,
  and 5.3.0, file 8972954, both of which fail to load registries under AgriCraft 4.0.17 because their
  `agricraft/plants` seeds lack the drop-chance fields; the FullPackServer gate caught it): touching Pulse Cairns join into one rune-carved stone that glows and lights
  up with its charge, every Tribal block model's see-through gaps closed (Ley Collector bowl, Stone Font,
  Ancestral Cache underside and 19 more), Pulse Cairn piles (64 stones, 256,000 Pulse), one-use cell fills, and the March crops under both AgriCraft folder spellings
  (AgriCraft 4.0.3 reads agricraft/plant|soil|mutation; the 4.0.17 release this pack ships reads
  plants|soils|mutations, so 5.0-5.2 crops never registered here). Also brings **5.2.1 - Sharper keys**
  (8972319): the Gear screen readable, shorter key names.
- **AgriCraft datapack** in `pack/overrides/kubejs/data/minecraft/agricraft/plants/` (19 files overriding
  AgriCraft's own vanilla definitions):
  - The 14 flowers get their own item as a seed (they had `"seeds": []`, so a vanilla flower could not
    go on crop sticks; the only source was grass drops a void pad lacks), `override_planting: false`,
    and soil humidity `equal_or_higher: damp` / nutrients `equal_or_higher: high`, so farmland suits
    them as well as podzol. At the tolerance factor 0.2 AgriCraft uses, a seed below Strength 5 needs
    an exact soil match, and only podzol was damp.
  - Brown and red mushroom, crimson fungus, nether wart and sweet berries: `override_planting: false`.
    AgriCraft hijacks an override seed planted on any registered soil whether or not the crop can
    grow there (e.g. a mushroom on podzol), leaving a crop that never grows.
  - The six farmland crops (wheat, beetroot, carrot, potato, melon, pumpkin) keep AgriCraft's
    conversion, as chapter 42 describes.

Pins: Ninjacat Skies Core 0.5.13 (project 1689718, file **8968452**), Tribal Power 5.3.2 (project
1684851, file **8973651**), Chocobos Reborn 1.0.13 (project 1699008, file **8960886**). Client zip
carries all 104 mods; the server zip installs 100. Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21.
