# Ninjacat Skies Core 0.5.3

Bug fixes, an art pass, and a way into the End. Existing saves load as they are; no ids change.

**A way to the End**

- **The End Apple.** Twelve portal frames are not a pad craft, so the End had no route. The apple costs five ender pearls, two bones and two blaze powder. The first bite puts you on the End's obsidian pad and leaves a bitten half; eating that brings you back to the spot you ate from. The way back is stored on you, so dying in the End does not lose it, and the whole apple will not be eaten in the End. A new quest in the End chapter; every existing quest keeps its id.

**Art**

Everything below is drawn at 32x32 to one style: one tinted outline, light from the top left, four to five tone ramps, hard edges.

- **Driftwrecks**: all 127 item and block textures redrawn. Each of the 54 Keepsakes is its own object, and no two are alike.
- **One glyph per tribe** everywhere: Tribe Banners, Keepsakes, Strand Tokens and Tension Post notches all use the same nine marks as Tribal Power.
- **Voidloom**: Binding Knot, Loom Lint and Strand Filament were pixel-identical, and the flint and iron Thread Meshes were the same picture. Each is its own drawing now; the meshes are a wooden hoop, a lashed flint frame and a riveted iron frame.
- **Snapped Guardians**: 13 relics and 13 Frayed Totems redrawn, each totem carrying its boss's mark.
- **Guardians and Remnants** wear pixel-quantised textures, so the bosses sit with the rest of the art instead of looking like smooth 3D.
- Clearer Tension Post, Tension Barrel and Loomframe faces, a readable window icon, and a Steward Echo that is a cat instead of a checker.

**Fixes**

- **Order cues play in order.** The idol's pillar order and the Clock and Sigil Remnant cues all fired at once, so the puzzles could not be read.
- **Boss fights survive a restart.** Phases no longer re-fire, Sealbreaker's wards re-arm, and Edgewalker's bridges and Thornmother's stations come back.
- **Blocks you place on a stage drop again** when broken. 0.5.2 stopped them dropping.
- **Thornseed hedges** left in the last seconds before a server stop are cleaned up, and Overweaver shades take their cobwebs and bushes with them.
- **Offline winners** get the defeat record and the advancement, not just the relic.
- **The Thread Lock** counted air toward its cap, so a large curtain only half opened.
- **The Remnant boss bar** keeps its Strand's name and colour after a reload.
- **Reweave ring signs** are waxed, so a visitor cannot rewrite a Clowder's name.
- With `sunderedSky = false` the sunrise and sunset glow come back.
- A malformed block plan is reported instead of crashing later, and a party login no longer logs a line for every member.

1.21.1 / NeoForge 21.1.249.
