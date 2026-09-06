# Ninjacat Skies — Style Guide

## Pixel art

- Native sizes: **16×16** items/blocks, **32×32** only for GUI icons that need it
- Light from top-left; 1 px outline where MC vanilla uses it
- Palette: void indigo `#2A2F4F`, teal `#3D7A7A`, lantern gold `#D4A84B`, ash `#8A8580`, cream `#E8E0D5`
- Paw motif: **rare** (Codex, Strand icons, one menu accent)—never on every ore
- Reject: noisy AI textures, photo-resampling, plastic sheen, random pastel clutter, purple-black missing placeholders in releases

## Pipeline

1. Author in Aseprite (or edit `art/` sources)
2. Export to mod `textures/`; keep `.aseprite` / Blockbench `.bbmodel` in `art/`
3. In-game check at GUI scale 1 and 2 before merge
4. Generative tools = moodboard in `art/reference/` only—never a ship path

## Code

- Clear registry names (`void_yarn`, not `item2`)
- Datagen for lang, tags, models, recipes
- No commented-out dead features in main
- Mixins documented with why
- English `en_us` hand-written

## Prose

See `STORY.md`. Short pages. Codex voice. No filler lore.  
All writing must be original to this project.
