# FancyMenu — authoring notes (INTERNAL)

Jars in `pack/mods` (NeoForge 1.21.1):

- `fancymenu_neoforge_3.9.12_MC_1.21.1.jar` (slug `fancymenu`, project 367706)
- `konkrete_neoforge_1.9.9_MC_1.21.jar` (required library)
- `melody_neoforge_1.0.10_MC_1.21.jar` (required library)

Download targets are listed in `tools/download-mods.ps1` (Konkrete, Melody, FancyMenu).

## Shipped overrides

Under `pack/overrides/config/fancymenu/`:

- `options.txt` — window title **Ninjacat Skies**; custom 16/32 window icons; modpack mode on; overlay hidden; **global nine-slice button skins** (normal / hover / inactive) + cream/gold label colors
- `customizablemenus.txt` — Title Screen + Pause Screen opted in
- `customization/title_screen_layout.txt` — `title_sky.png` image backdrop with soft parallax; pack logo; Codex tagline; vanilla MC logo / Realms / Realms icons hidden
- `customization/pause_screen_layout.txt` — translucent void-indigo `#2A2F4FCC` tint; Codex footer; Feedback / Report Bugs / Server Links hidden (buttons inherit global skins)
- `assets/` — regenerate via scripts below

Also mirrored to UI pack:

- `pack/overrides/resourcepacks/ninjacat-skies-ui/assets/ninjacat_skies_ui/textures/gui/ninjacat_logo.png`

UI resource pack splash lines: `pack/overrides/resourcepacks/ninjacat-skies-ui/assets/minecraft/texts/splashes.txt` (aligned with title tagline / STORY voice).

### Asset generators

| Script | Output |
|--------|--------|
| `INTERNAL/_gen_fancymenu_logo.py` | `assets/ninjacat_logo.png` (+ UI pack copy) |
| `INTERNAL/_gen_fancymenu_skins.py` | `button_{normal,hover,inactive}.png`, `title_sky.png`, `window_icon_{16,32}.png` |

### Layout / options details

| Piece | Status |
|-------|--------|
| Window title `Ninjacat Skies` | done (`options.txt` + `custom_menu_title`) |
| Window icons 16/32 | done (`window_icon_*.png`; macOS icns not set) |
| Title sky still + soft parallax | done (`title_sky.png`, `parallax_intensity = 0.035`) |
| Logo image element → `assets/ninjacat_logo.png` | done (`ncs-title-logo-001`) |
| Tagline text | done — `Ninjacat Skies` / `The Loom was cut. Reweave it—one Strand at a time.` |
| Footer hush line (title) | done — Whisker Codex / void-teal |
| Vanilla `minecraft_logo_widget` | hidden |
| Vanilla `minecraft_splash_widget` | hidden (was hanging over buttons) |
| Vanilla `minecraft_branding_widget` | hidden (mod-list branding clutter) |
| Autoscale / setscale | done — `setscale 2` + `autoscale 1920×1080` |
| Buddy popup + FancyMenu example welcome | disabled (`enable_buddy=false`, `show_welcome_screen=false`) |
| Pack welcome popup `ninjacat_skies_welcome` | done — Custom GUI popup + title ticker (first run) + **How to Start** title button |
| Realms button + notification icons | hidden |
| Pause screen opted in | done (`PauseScreen` in `customizablemenus.txt`) |
| Pause void-indigo tint `#2A2F4FCC` | done (translucent; blur kept) |
| Pause Codex footer | done — `Whisker Codex · hush between Strands` |
| Pause Feedback / Report Bugs / Server Links | hidden |
| Global nine-slice button skins | done — indigo/teal normal; brighter hover + gold sheen; muted inactive; borders 5px |
| Global button label colors | done — cream base `#E8E0D5`, gold hover `#D4A84B` |
| Drippy loading | **later** (optional polish) |

### Global button option keys (FM 3.9.12)

Under `##[global_customizations]` in `options.txt`:

- `S:global_button_background_{normal,hover,inactive}` → `/config/fancymenu/assets/button_*.png`
- `B:global_button_background_nine_slice = 'true'`
- `I:global_button_background_nine_slice_border_{top,right,bottom,left} = '5'`

Applies to vanilla/mod widgets on all screens (title, pause, options, etc.) without per-layout templates.

### Pause / title risks (hand-authored)

- Universal id `pause_screen` and widget ids come from FancyMenu 3.9.12 (`PauseScreen` mixin / identifier registry). Confirm with CTRL+ALT+D in-game if a FM update renames widgets.
- Translucent pause color backdrop + `apply_vanilla_background_blur = true` is best-effort; opaque title sky covers the panorama fully.
- Hiding Feedback / Bugs / Server Links is safe for core Resume / Options / Advancements / Stats / Disconnect. Do **not** hide those.
- Title logo wiring (`ncs-title-logo-001` → `assets/ninjacat_logo.png`) is untouched by the pause layout.
- If global button paths fail to resolve after a FM update, fall back to `[source:local]/config/fancymenu/assets/...` or re-set via Global Customizations in-game.

## In-game verify (playtest)

1. Launch client; confirm title sky, paw logo, window title **Ninjacat Skies**, teal-framed buttons, Realms gone, vanilla MC logo gone; window icon is the paw.
2. Enter a world → pause; confirm indigo tint, Codex footer, skinned Resume/Options; Feedback/Bugs/Server Links gone.
3. Optional polish pass (modpack mode off): nudge logo/tagline anchors at GUI scale 1 and 2; retune parallax intensity; adjust pause tint alpha.
4. Re-enable modpack mode before export so players do not see editor chrome.

## Docs

- Layout system: https://docs.fancymenu.net/en/technical-docs-layout-system
- Global customizations: https://docs.fancymenu.net/docs/en-US/global-customizations
- Nine-slicing: https://docs.fancymenu.net/docs/en-US/nine-slicing-and-tiling

Do not copy menu assets or copy from other packs. Keep voice aligned with `docs/STORY.md` / `docs/STYLEGUIDE.md`.
