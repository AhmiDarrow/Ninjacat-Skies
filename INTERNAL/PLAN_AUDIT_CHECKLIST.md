# Plan Audit Checklist (INTERNAL)

Durable reminder for agents. Source of truth: `INTERNAL/PLAN.md`.  
Latest disk audit 2026-09-05 (post FancyMenu skins + Clowder Hall hub dim + March noise / Conductor / Tension / Steward / Voidloom BE): **~98% PASS / 0 MISSING** — P0 empty; remaining = client playtest only. FancyMenu button skins + title sky shipped.  
Keep this file INTERNAL-only. No secrets.

---

## Loom Braid phases

```
WAKE → RECOVER → ROOT → EDGE → (PATTERN ‖ COLONY ‖ HUM) → BIND → REWEAVE
```

- [x] **Wake** (Soil) — pads / Codex / starter kits on disk; Soil has no Tribal softlock
- [x] **Recover** (Stone + Voidloom) — `02_stone` leads Voidloom yarn→hammer→mesh→knot→loomframe; Ex Deorum follows as engine — `docs/CHANGELOG.md`, Stone quests
- [x] **Root** (Sprout) — farms / Mystical spine present (`03_sprout` + side agri)
- [x] **Edge** (Claw) — Silent Gear / foothold spine (`04_claw` + nether side)
- [x] **Pattern** (Clock) — Create peer braid path (`06_clock` + factory side)
- [x] **Colony** (Swarm) — bees / deep crops peer path (`07_swarm` + bees/crops sides)
- [x] **Hum** (Spark) — Drumheart / Pulse / Ley Collector *before* Powah on main chain; Mek stays side — Spark quests + `braid_gates.js`
- [x] **Bind** (Sigil) — `braid_cord` on main chain (required); Tribal rites chapter beside Aura/Ars/Occultism
- [x] **Reweave** (Spindle) — AE2 + Gate Drum → `march_stone` → Spindle fragment trophy

Glue: any two of Clock/Swarm/Spark tokens → `ninjacatskies:braid_cord` → Bind → Reweave. **Live** in `braid_gates.js` + quests.

Phase systems now shipped: Loom Tension (`loom_tension.js`), steward lines (`steward_lines.js`), March **terrain noise** (steppe / highlands / crystal fields).

---

## Tribal dual mandate

### Standalone (`tribal-power` / `rewrite/shamanic-technomancy`)

- [x] Playable without Ninjacat (no hard deps) — pack weave uses `Item.exists` guards only
- [x] Spirit Pulse + Drumheart — items + Hum quests / KubeJS lead-ins
- [x] Totem Lattice + Song Bench Echo loop (Shatter→Attune→Bind→Manifest) — `34_tribal` stages live
- [x] Caches / seals & rites / spiritgear — chapter + item IDs present
- [x] Gate Drum → The March — Spindle + tribal closing beats
- [x] March noise terrain — `worldgen/noise_settings/the_march.json` + biomes `march_steppe` / `march_highlands` / `march_crystal_fields`; Codex notes noise hills/valleys
- [x] Guidebook (Spirit Codex) matches live systems — Echo loop + Lattice Conductor + March noise biomes documented in `tribal-power/.../guide/GuidePages.java` + `data/tribalpower/guide/spirit_codex.json`
- [x] No anime/games tagline; Loom-born steward-tribes origin OK (`docs/STORY.md`)

### Pack weave (Ninjacat Skies)

- [x] Jar in `pack/mods` (pinned rewrite build) — `tribalpower-2.0.1.jar`
- [x] Hum recipes in Tribal jar (no KubeJS dupes); chapter order Chime→Shard→Codex
- [x] Spark has Drumheart on main chain
- [x] Sigil requires `braid_cord` (not optional)
- [x] Spindle full clear: Gate Drum → `march_stone` → Spindle fragment
- [x] Trophy recipe = nine Strand tokens **+** `tribalpower:march_stone`
- [x] Never gate Soil–Root on Tribal; don’t shrink Tribal pillars for Mek
- [x] Lattice Conductor real routing — `LatticeConductorBlockEntity` + `LatticeNetwork` (Pulse push, Song Bench assist, Echo grit route); jar copied to `pack/mods/tribalpower-2.0.1.jar`

---

## Nine tribes story

- [x] Nine Ninjacat tribes tended nine Strands
- [x] Tribal Power born from shared Loom power (orphan technomancy after the cut)
- [x] Strand↔tribe flavor table in `docs/STORY.md` / `INTERNAL/PLAN.md`
- [x] Public voice: steward tribes / severed lattice — no anime pitch, no agent/INTERNAL leaks

| Strand | Tribe flavor |
|--------|--------------|
| Soil | Pad-keepers |
| Stone | Grit-singers |
| Sprout | Rootbinders |
| Claw | Edge-walkers |
| Spark | Drumhearts |
| Clock | Pattern-weavers |
| Swarm | Colony-keepers |
| Sigil | Seal-carvers |
| Spindle | Loom-stitchers |

---

## P0 — CLOSED (do not reopen unless regressed)

| Item | Closed as |
|------|-----------|
| Echo processing loop | Song Bench Echo stages live |
| Hum / Drumheart in Spark | Main-chain quest + KubeJS Hum recipes |
| March trophy / Reweave gate | `march_stone` on trophy + Spindle chain |
| FancyMenu jars | FancyMenu + Konkrete + Melody in `pack/mods` (title+pause+skins) |
| Clowder Dock | `clowder_dock.nbt` as `mainSpawnIsland` |
| Recover Voidloom lead | Stone main chain opens on Voidloom, sieve as Recover tool |
| Hum-first Spark | Drumheart/Pulse/Ley before Powah FE bridges |
| Braid gates | `braid_cord` recipes + Sigil/Spindle quest use |
| Lattice Conductor routing | Tribal BE + jar in `pack/mods` |
| Loom Tension system | `pack/overrides/kubejs/server_scripts/loom_tension.js` |
| Steward lines | `steward_lines.js` + expanded `WhiskerCodexItem.java` |
| Voidloom stations | Loomframe mesh BE + Tension Barrel transforms (`mods/voidloom/...`) |
| FancyMenu logo + title + skins | `pack/overrides/config/fancymenu/` logo, title sky+parallax, global nine-slice buttons, window icons (`INTERNAL/fancymenu-notes.md`) |
| Spirit Codex parity | Echo + Conductor pages in GuidePages / spirit_codex.json |

Remaining P0: **empty**.

---

## P1 — remaining (truly open)

1. **Client playtest** — boot client; verify FancyMenu skins + island → Recover Voidloom feel, braid paths, Tension/steward whispers, Tribal lattice. **Not done.** Use `INTERNAL/PLAYTEST_CHECKLIST.md`. (PLAN also asks Tribal-alone playtest.)

## P2 — shipped / optional polish (do not block ship criteria)

1. **FancyMenu button skins / sky art** — **DONE**: global nine-slice indigo/teal buttons + `title_sky.png` soft parallax + window icons (`INTERNAL/fancymenu-notes.md`; regenerate via `INTERNAL/_gen_fancymenu_skins.py`). In-game nudge of anchors/alpha still optional.
2. **Hub dimension** — **DONE**: `clowderhall:clowder_hall` void datapack dim + Java ceremony pad (`mods/clowderhall/.../ModDimensions.java` `ensureHubHall`); `/clowder hub` / Hub Key / `/clowder return` (`INTERNAL/islands-notes.md`). Overworld Clowder Dock remains skyblock first-join spawn.
3. **March terrain noise** — **DONE**: Gate Drum → `tribalpower:the_march` with noise hills/valleys across steppe / highlands / crystal fields (`tribal-power/.../worldgen/biome/march_*.json`, `noise_settings/the_march.json`; GuidePages). Further flora density polish optional.
4. **FE ↔ Pulse bridge** — **Pulse Resonator** (coal→Pulse) shipped as pragmatic Hum generator; full FE capability bridge still optional.
5. **Drippy loading / macOS window icon** — optional later.

---

## Re-verify commands

From the Ninjacat Skies repo root:

```powershell
# Full gate suite (omit -SkipBuild to rebuild custom jars)
pwsh -NoProfile -File .\tools\gates\Invoke-AllGates.ps1 -SkipBuild -WithExportDryRun

# Quest item-ID audit
python .\tools\audit_quest_items.py

# After copying a new Tribal jar
python .\tools\extract_item_ids.py
```

```powershell
# Presence greps (expect hits)
rg -n "drumheart" pack\overrides\kubejs pack\overrides\config\ftbquests
rg -n "braid_cord" pack\overrides\kubejs mods\ninjacatskies pack\overrides\config\ftbquests
rg -n "march_stone" pack\overrides\kubejs pack\overrides\config\ftbquests
rg -n "clowder_dock" pack\overrides\config\skyblockbuilder
rg -n -i "fancymenu" pack\mods pack\overrides\config tools\download-mods.ps1
rg -n "ncs_tension" pack\overrides\kubejs\server_scripts\loom_tension.js
rg -n "STEWARD" pack\overrides\kubejs\server_scripts\steward_lines.js
```

Also confirm jars exist: `tribalpower-*.jar`, `fancymenu_*.jar`, `konkrete_*.jar`, `melody_*.jar`, `clowderhall-*.jar` under `pack/mods`.

---

## Quick pointers

| Topic | File |
|-------|------|
| Living plan | `INTERNAL/PLAN.md` |
| Tribal weave | `INTERNAL/tribal-weave-notes.md` |
| KubeJS braid | `INTERNAL/kubejs-notes.md` |
| Hub / Dock | `INTERNAL/islands-notes.md` |
| FancyMenu | `INTERNAL/fancymenu-notes.md` |
| Gates | `INTERNAL/GATES.md` |
| Public canon | `docs/STORY.md` |
| Third-party credits | `docs/ATTRIBUTION.md` |
| Plan complete | `INTERNAL/PLAN_COMPLETE.md` (when authored) |
