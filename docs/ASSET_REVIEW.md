# Asset review — 2026-09-13

Preserve the existing pixel-art direction. Core's frayed_thread and braid_cord were pixel-identical; codex_page was pixel-identical to whisker_codex. Three hand-authored 16×16 sprites now distinguish loose frayed fiber, braided cord and a folded paper page. The codex book and strand tokens remain intact.

Sources (superseded 2026-09-19, see below): the 16px reviewed maps and the old 16px generators were retired when Core moved to native 32px art.

Pack menu backgrounds, branding, buttons, quest headers, Core materials and supporting-module assets were retained. The primary review included visual contact sheets for Core and the menu; the supporting modules were structurally audited. Menu legibility and quest-header text still need an in-game GUI-scale check.

Source asset validation reports no local missing references or invalid images/JSON/animation frame indices. Minecraft and other external namespaces require a loaded game/mod set for final resolution. Gradle resource processing is blocked by a local Java loopback connection error, so this is not release certification.

# Visual cohesion pass � 2026-09-19

Core follows the family style target: 32x32 native items/blocks, 1 px tinted outline, top-left light, hue-shifted ramps, no AA/noise.

- `tools/generate_core_art.py` is the single source of truth for ninjacatskies, voidloom and clowderhall item/block textures (`--check` verifies shipped PNGs). Sprites that were already on style are frozen in `art/core-kept-sprites.json`; the rest are drawn natively at 32px with `tools/core_pixel.py`. It replaces `generate_item_textures.py`, `generate_textures_loom.py`, `export_reviewed_pixel_art.py` and `art/reviewed-pixel-items.json` (16px). Tribal Power's `overhaul_art.py` now paints only its own namespace; if Core art is ever clobbered, re-run the Core generator.
- Strand tokens and Tension Post notches use the canonical tribe glyphs from `tools/art_tribe_glyphs.py` (soil/stone and sigil/rewoven no longer share a shape).
- `tools/generate_guardians_items.py` draws the Guardians relics and Frayed Totems at 32px.
- `tools/pixel_quantise_boss.py` pixel-quantises the baked Guardian and Remnant textures (called by the Blender exporters after every bake).
