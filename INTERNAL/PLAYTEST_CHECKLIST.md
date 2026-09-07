# Client playtest checklist (INTERNAL)

**Status:** unchecked — awaiting human client smoke.  
**Date prepared:** 2026-09-05  
**Scope:** Wake → Recover → Root → Edge → Hum / Pattern / Colony → Bind → Reweave

Do not mark items done from agent disk audits. Check only after a live client run.

---

## Boot / branding

- [ ] Client boots with pack; no fatal mod errors on title
- [ ] FancyMenu **title** visible: void-indigo **sky still** (soft parallax), Ninjacat paw logo, pack tagline, window title **Ninjacat Skies**
- [ ] Title text sits **above** the button column (no splash/branding hanging over Singleplayer)
- [ ] No FancyMenu Buddy / stock “Welcome to FancyMenu!” popup
- [ ] Pack **Welcome to Ninjacat Skies** popup appears on first title load; **How to Start** title button reopens it
- [ ] Title / Options buttons use **indigo+teal nine-slice** skins (cream label, gold on hover); window icon is the paw
- [ ] Vanilla MC logo + Realms + splash + branding hidden on title
- [ ] FancyMenu **pause**: void-indigo tint, Codex footer, skinned Resume/Options; Feedback / Report Bugs / Server Links hidden

## Skyblock world + islands

- [ ] Create world with world type **Skyblock** (`skyblockbuilder:skyblock`)
- [ ] First join lands on **Clowder Dock** (15×15 overworld spawn, beacon/lectern)
- [ ] Standing plaque text faces the spawn apron (readable looking north); lectern **How to Start** book is OOC and clear
- [ ] First join grants **How to Start** + **Island Charter** + **Hub Key** (+ Codex); Dock chest also has copies
- [ ] Three island templates selectable when creating a team:
  - [ ] **Ninjacat Pad** (Normal)
  - [ ] **Dojo Cottage** (Easy)
  - [ ] **Frayed Thread** (Hard) — chest includes ice×2 + lava for cobble gen
- [ ] Claim / visit island works; true void between pads
- [ ] Charter on Dock opens Create Team; on pad seals spawn (no Create Team popup)

## Clowder Hall hub dimension

- [ ] `/clowder hub` teleports to **`clowderhall:clowder_hall`** (ceremony pad ~0,64,0 — not overworld Dock)
- [ ] **Hub Key** right-click also enters Clowder Hall
- [ ] Ceremony pad present (beacon, lectern, banners, plaques, starter chest with Codex/Charter/Hub Key)
- [ ] `/clowder return` only works **while in Hall**; restores saved pad / Dock fallback
- [ ] Shared lives: deaths debit the FTB team; zero exhausts all members; six one-time milestone rewards add one life each; revive commands require operator permission

## Wake → Recover (Voidloom-led)

- [ ] Early survival kit / pad usable without softlock
- [ ] Craft / place **Voidloom Loomframe** (`voidloom:loomframe`); mesh station behaves
- [ ] Void yarn / binding knot / thread meshes progress Recover quests
- [ ] Tension Barrel: water+dirt → clay; **empty bucket returns to player** (iron or porcelain water)
- [ ] Spindle Crook breaks leaves quickly; Ex Deorum crook string/silkworm drops apply
- [ ] Strand Banner Pattern applies a **Strand** layer on the loom (not a dummy item)

## Loom Tension (2026-09-06 layer)

- [ ] Soil Knot quest appears after its five beats; claiming gives Strand Token: Soil + Steward Cache (command reward) + 3 levels
- [ ] Craft Tension Post (logs + Binding Knot + Thread); place on pad; right-click with token → chime, helix, whisper (teal + gold), notch lit, `Seat Soil` quest clears
- [ ] Second player on the same team hears the chime / whisper and sees the Seat quest cleared
- [ ] Post hums quietly (client), light level rises with notches; particles drift from lit notches
- [ ] Aura: Regeneration near Post; after Claw seated, falling off the pad within 48 blocks does no damage (actionbar "Edge-walker footing")
- [ ] Horizon/fog warms slightly after seating (compare screenshot before/after; `skyTint=false` disables)
- [ ] The Fray column visible over the Dock (0,66,0 by default) from within 96 blocks; thins as Strands seat
- [ ] Whisker Codex right-click opens the Modonomicon book; Nine Tribes entries unlock per seat; sneak-click nudges
- [ ] Codex Page right-click prints a tribe margin note with page sound
- [ ] Strand Filament from iron thread mesh (sieve or Loomframe); right-click Post with it after 2 braid Strands → Braid Cord
- [ ] March stone right-click with 9 seated → Fragment; Fragment right-click → Reweave finale (broadcast, chimes, ring, fireworks), `Reweave` quest clears
- [ ] Loomframe: load 64 dirt, walk away, come back to scraps; hopper on top feeds, hopper on side pulls
- [ ] Tension Barrel: water bucket returns immediately; 8 dirt → 8 clay unattended

- [ ] Clowder Hall: after a Reweave, re-enter the Hall — one ring pillar lit with the Clowder's name plaque

## Root → Edge

- [ ] Living pad / farm foothold (Soil–Root feel) without Tribal softlock
- [ ] Edge kit / tools / footholds open braid routes (Pattern ‖ Colony ‖ Hum)

## Hum (Tribal Pulse)

- [ ] **Drumheart** places, stores Pulse, charges Pulse Cell
- [ ] **Ley Collector** gathers ambient Pulse
- [ ] **Pulse Resonator** (`tribalpower:pulse_resonator`) accepts coal/charcoal, lights, generates denser Pulse
- [ ] **Song Bench** Echo loop: Shatter → Attune → Bind → Manifest grit path readable
- [ ] Lattice Conductor routes Pulse from Drumheart / Ley / Resonator into totems
- [ ] Spark chapter shows Hum: Drumheart / Pulse Cell / Ley / Pulse Resonator before FE bridges

## Pattern ‖ Colony (peer braid)

- [ ] Pattern (Create) progression reachable as peer path
- [ ] Colony (Productive Bees) progression reachable as peer path
- [ ] Any **two** of Clock / Swarm / Spark strand tokens craftable

## Bind → Reweave

- [ ] Craft **`ninjacatskies:braid_cord`** from any Clock/Swarm/Spark token pair
- [ ] Bind / Sigil chapter accepts braid_cord (not optional)
- [ ] **Gate Drum** opens / enters **The March**
- [ ] March **noise biomes** visible (not flat-slab only): **steppe** / **highlands** / **crystal fields**
- [ ] Obtain **`tribalpower:march_stone`**
- [ ] Craft / claim **`ninjacatskies:spindle_loom_fragment`** (Spindle trophy needs March stone + strand proof)

## Smoke regressions (quick)

- [ ] FTB Quests open; Spark + Tribal chapters list Pulse Resonator
- [ ] Whisker Codex / Spirit Codex open without crash
- [ ] Steward / Tension whispers fire at least once on expected triggers
- [ ] No obvious missing textures on Loomframe, Drumheart, Song Bench, Pulse Resonator, Gate Drum

---

## Sign-off

| Field | Value |
|-------|--------|
| Tester | |
| Client / launcher | |
| Pack build / zip | |
| Result | PASS / FAIL |
| Notes | |
