# Ninjacat Skies 0.9.0 — The Spirit Herd and a Full Grid

Pack CurseForge client file **(pending)**, server additional **(pending)**.

Shamanic Mounts joins the pack, Chocobos Reborn moves to 1.1.0, and 25 other mods take their latest 1.21.1
NeoForge release. Ninjacat Skies Core stays 0.5.17 and Tribal Power stays 5.3.10. Existing saves load as they
are; no quest ids change. The mod list grows from 104 to 105 (101 on the server).

- **Shamanic Mounts 0.1.3 - Condor Wings** (project 1711650, file **8978477**), new: breedable spirit mounts
  with a real gene system. Ten founder lines (steed, hart, hound, cat, bird, bear, serpent and more), pelts,
  sizes and gifts that pass down, tack with saddle bags and vanilla horse armour, a Herd Book, and spawns that
  include the Tribal Power March biomes. Server and every player need it.
- **Chocobos Reborn 1.1.0 - Full Grid** (project 1699008, file **8999472**): forty-eight courses, twelve a
  class. Sprints are one long lap, grands prix short three-to-five-lap circuits. Racers bump instead of passing
  through each other. Win points and purses scale with the length of the heat (a sprint win is 4, 36 promote;
  old points convert once). Rebuilt AI, cleaner courses, and Flame and Purple birds no longer race. Existing
  course islands rebuild the next time each is raced.
- **Mod updates** (latest 1.21.1 NeoForge release of each; every jar checked against CurseForge's SHA-1, and
  every required dependency of the new set checked statically):
  - Applied Energistics 2: `appliedenergistics2-19.2.17.jar` -> `appliedenergistics2-19.2.18.jar` (file 8992605)
  - Ars Nouveau: `ars_nouveau-1.21.1-5.13.1.jar` -> `ars_nouveau-1.21.1-5.13.2.jar` (file 8993194)
  - Balm: `balm-neoforge-1.21.1-21.0.65.jar` -> `balm-neoforge-1.21.1-21.0.66.jar` (file 8969738)
  - Create Crafts & Additions: `createaddition-1.7.0.jar` -> `createaddition-1.7.1.jar` (file 8887653)
  - Create: Dragons Plus: `CreateDragonsPlus-1.11.8b.jar` -> `CreateDragonsPlus-1.11.9.jar` (file 8900055)
  - Create: Enchantment Industry: `create-enchantment-industry-2.5.3b.jar` -> `create-enchantment-industry-2.5.4.jar` (file 8900719)
  - Entity Culling Fabric/Forge: `entityculling-neoforge-1.10.5-mc1.21.1.jar` -> `entityculling-neoforge-1.11.2-mc1.21.1.jar` (file 8942303)
  - FramedBlocks: `FramedBlocks-10.6.1.jar` -> `FramedBlocks-10.6.2.jar` (file 8780141)
  - FTB Library (NeoForge): `ftb-library-neoforge-2101.1.35.jar` -> `ftb-library-neoforge-2101.1.36.jar` (file 8858846)
  - FTB Quests (NeoForge): `ftb-quests-neoforge-2101.1.34.jar` -> `ftb-quests-neoforge-2101.1.36.jar` (file 8885017)
  - GeckoLib: `geckolib-neoforge-1.21.1-4.9.2.jar` -> `geckolib-neoforge-1.21.1-4.9.3.jar` (file 8893490)
  - GuideME: `guideme-21.1.17.jar` -> `guideme-21.1.19.jar` (file 8897145)
  - HammerLib: `HammerLib-1.21-21.0.14.jar` -> `HammerLib-1.21-21.0.16.jar` (file 8888364)
  - ImmediatelyFast: `ImmediatelyFast-NeoForge-1.6.13+1.21.1.jar` -> `ImmediatelyFast-NeoForge-1.6.14+1.21.1.jar` (file 8875640)
  - Iron's Lib: `irons_lib-1.21.1-2.1.0.jar` -> `irons_lib-1.21.1-2.2.0.jar` (file 8973642)
  - KubeJS: `kubejs-neoforge-2101.7.2-build.374.jar` -> `kubejs-neoforge-2101.7.2-build.377.jar` (file 8843626)
  - Modonomicon: `modonomicon-1.21.1-neoforge-1.120.4.jar` -> `modonomicon-1.21.1-neoforge-1.120.7.jar` (file 8970913)
  - Moonlight Lib: `moonlight-1.21.1-3.6.3-neoforge.jar` -> `moonlight-1.21.1-3.7.0-neoforge.jar` (file 8981395)
  - Productive Bees: `productivebees-1.21.1-13.13.5.jar` -> `productivebees-1.21.1-13.14.0.jar` (file 8987967)
  - Sophisticated Backpacks: `sophisticatedbackpacks-1.21.1-3.26.1.2124.jar` -> `sophisticatedbackpacks-1.21.1-3.26.5.2171.jar` (file 8992926)
  - Sophisticated Core: `sophisticatedcore-1.21.1-1.5.0.2322.jar` -> `sophisticatedcore-1.21.1-1.5.2.2343.jar` (file 8985869)
  - Sophisticated Storage: `sophisticatedstorage-1.21.1-1.5.91.2127.jar` -> `sophisticatedstorage-1.21.1-1.6.0.2136.jar` (file 8985962)
  - Supplementaries: `supplementaries-1.21.1-3.9.8-neoforge.jar` -> `supplementaries-1.21.1-3.9.9-neoforge.jar` (file 8852720)
  - Xaero's Minimap: `xaerominimap-neoforge-1.21.1-26.4.2.jar` -> `xaerominimap-neoforge-1.21.1-26.5.0.jar` (file 8849842)
  - Xaero's World Map: `xaeroworldmap-neoforge-1.21.1-1.45.0.jar` -> `xaeroworldmap-neoforge-1.21.1-1.46.0.jar` (file 8849973)

FTB XMod Compat stays at 21.1.11: 21.1.12 requires JEI 19.53 or newer, and every JEI after 19.51.0.418 is a
beta, so the full-pack server refused to start with it (caught by the FullPackServer gate).
