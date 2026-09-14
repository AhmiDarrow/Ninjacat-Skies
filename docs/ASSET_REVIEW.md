# Asset review — 2026-09-13

Preserve the existing pixel-art direction. Core's frayed_thread and braid_cord were pixel-identical; codex_page was pixel-identical to whisker_codex. Three hand-authored 16×16 sprites now distinguish loose frayed fiber, braided cord and a folded paper page. The codex book and strand tokens remain intact.

Sources: `art/reviewed-pixel-items.json`. Export: `python tools/export_reviewed_pixel_art.py --write`; check: `python tools/export_reviewed_pixel_art.py`. The older item generator skips these reviewed names. Tribal Power's local overhaul tool also respects the reviewed source manifest when pointed at this repository. Run the reviewed exporter explicitly after changing these maps.

Pack menu backgrounds, branding, buttons, quest headers, Core materials and supporting-module assets were retained. The primary review included visual contact sheets for Core and the menu; the supporting modules were structurally audited. Menu legibility and quest-header text still need an in-game GUI-scale check.

Source asset validation reports no local missing references or invalid images/JSON/animation frame indices. Minecraft and other external namespaces require a loaded game/mod set for final resolution. Gradle resource processing is blocked by a local Java loopback connection error, so this is not release certification.
