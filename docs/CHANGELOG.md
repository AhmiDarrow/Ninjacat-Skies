# Changelog

## 0.3.0-alpha — Wider Sky

_Uploaded to CurseForge 2026-09-07 (file 8827030)._

Twenty-eight mods added (content + libraries), each wired into the questline, plus fixes to the FancyMenu onboarding and a KubeJS crash.

**New mods, woven into new chapters**
- **Stonemason** (Chipped): every workbench — mason, carpenter, glassblower, loom, botanist, alchemy, tinkering — for thousands of block variants from vanilla stock.
- **Furnishings** (Handcrafted, Macaw's Bridges & Roofs, FramedBlocks, Amendments): chairs, tables, beds, shelves, bridges to span the void, roofs, and camouflage frames.
- **Small Stewardries** (Supplementaries, Comforts): sconces, hourglass, faucet, crank, sack, safe, notice board, pedestal, sleeping bag, hammock, rope.
- **The Current** (Create: Crafts & Additions, Create: Enchantment Industry, Mekanism Generators, AE2 Wireless Terminals, Applied Mekanistics): wires and motors bridging Create rotation to Forge Energy, liquid-XP enchanting, Mekanism power generators, a pocket AE2 terminal, and Mek chemicals in the AE2 network — tied to Spark, Clock and Spindle.
- **Woven into existing chapters**: Sophisticated Storage into Storage & Packs; Modular Routers into Pipeworks.
- **Quality of life / maps** (no quests needed): Xaero's Minimap & World Map, Clumps, Controlling, Mouse Tweaks, TrashSlot, Just Enough Resources, Just Enough Professions, plus libraries (Moonlight, Resourceful Lib, Searchables, Athena, Create Dragons Lib).

All new mods sourced for NeoForge 1.21.1 and boot-verified together on a dedicated server (28 added, 0 load errors, 0 failed recipes). Quest count 1354 → 1444; item-id, dead-end and reachability audits all clean against the live 15,000-item registry.

**Fixes**
- **FancyMenu**: removed the pack's custom welcome popup auto-open (the "How to Start" title button still opens it on demand). All FancyMenu self-suppressors remain set: modpack_mode, welcome screen off, buddy off, customization overlay off.
- **KubeJS**: `jei_hides.js` no longer crashes on load — the old `JEIEvents` reference is guarded (KubeJS 2101 renamed the JEI event binding).

Note for a public (non-alpha) release: the new mods are bundled in `overrides/mods/` for now because the CurseForge project API is unreachable from here. Run `tools/download-mods.ps1` on a machine with CurseForge access to convert them to manifest (CF-hosted) entries for proper author attribution before promoting past alpha.

## 0.2.2-alpha — Reachable Roots

Void-pad reachability review after the bees fix turned up the same class of bug in two more mods, both now fixed, plus a permanent backstop so it can't recur.

- **Mystical Agriculture** was blocked: Inferium and Prosperity essences smelt from `c:ores/inferium` / `c:ores/prosperity`, worldgen ores that never spawn in the void, and Prosperity has no mob drop — so every essence seed (and the deep-crops half of Colony) was unreachable. Both ores now fall from the sieve (`mystical.js`): Inferium common from dirt (string mesh and up), Prosperity rarer from gravel/sand; Voidloom meshes catch them too, so the Loomframe automates the essence floor.
- **Farmer's Delight** cabbage, tomato and rice only came from wild plants that generate in the world (tomato seeds even craft from a tomato you can't get yet); onion was fine (zombies drop it). Their seeds and cabbage leaf now come from the sieve (`farmers.js`).
- **`tools/check_reachability.py`** — new backstop that scans every mod's recipes, the Ex Deorum sieve/hammer/barrel, all loot tables, the KubeJS additions and quest rewards, and flags any non-optional main-line quest item with no producer (the worldgen/mob/structure-only signature). Runs clean; wired into the notes for pre-export checks.
- Reviewed and cleared as reachable: AE2 (certus from sand), Ars Nouveau (archwood/sourceberry from moss), Mekanism/Powah (ore chunks from the sieve; uranium→uraninite), Occultism (Spirit Fire converts vanilla), Tribal Power (Bone Chime from vanilla; March via Gate Drum), Nature's Aura, Solar Flux (code-generated recipes).

## 0.2.1-alpha — Colony

- **Bees on a void pad.** Productive Bees nests are craftable: a ring of the material around any small flower (oak/birch/spruce/dark oak/acacia/jungle/cherry logs, hay, coarse dirt, gravel, sand, stone, sugar cane, slime, snow, glowstone, quartz, nether brick, soul sand, gilded blackstone, end stone, obsidian). Placed nests spawn their bees; the oak and hay nests also spawn plain honey bees, so hives, honeycomb and every breeding line start from the pad. Vanilla Bee Nest is craftable from planks and flowers.
- **Strand: Swarm rebuilt** around that route: Ring of Oak → First Wings (look at a bee) → flowers → Bee Nest → comb → hive → Honey Treat → Rings of Grit / Coarse Dirt / Stone → Advanced Beehive → Bottler → Centrifuge → Catcher / Cage → Incubator → Breeding Chamber → Gene Indexer → deep crops; "Something New Hums" when a new bee species appears. Apiary side chapter opens with the Nest Locator and the foothold nests (glowstone, quartz, nether brick, soul sand, end stone, obsidian).
- **Steward Caches are loot crates**: FTB Quests reward tables (backed by the mod's loot tables) — Knot quests hand you a glowing crate to open.
- **Secret quests**: one hidden per Strand chapter (a zombie on your pad, a wrong potato, a witch at night, killing a bee…), revealed on completion.
- **Chapter subtitles** for the nine Strands, Clowder Hall, the Desk and the Apiary.
- Verified on the dedicated server: 73 KubeJS recipes, 0 failures; 34 chapters / 1354 quests / 10 reward tables.

## 0.2.0-alpha — Loom Tension

First CurseForge alpha. Everything below the "Scope" block was landed 2026-09-05/06; see the dated sections for the Loom Tension layer, Voidloom rework, quest regeneration, and headless verification.


### Scope
- Target playtime: **40–60 hours** Normal first clear
- FTB Quests: **1354** quests across **34** chapters (item-ID + dead-end audit clean; Strand chapters authored in `en_us.snbt`)
- Island starters: Frayed Thread, Ninjacat Pad, Dojo Cottage (Skyblock Builder templates)

### Custom mods
- `ninjacatlib` — shared text helpers
- `ninjacatskies` — Whisker Codex, Frayed Thread, Strand tokens, **Braid Cord**, **Spindle Loom Fragment** end trophy, Skybound first-join kits
- `voidloom` — Void Yarn, thread meshes, Spindle Hammer/Crook, Loomframe (mesh slot + grit bonus scrap), Tension Barrel (water+dirt→clay; string+ender→yarn)
- `clowderhall` — Island Charter (rules book + spawn seal), Hub Key (right-click → Hall), `/clowder hub` → **`clowderhall:clowder_hall`** hub dimension, `/clowder return` restores saved pad pos

### Hub ceremony
- Dedicated **Clowder Dock** hub NBT (`clowder_dock.nbt`, 15×6×15) for `mainSpawnIsland` — beacon frame, lectern, banners, plaques; Easy/Normal/Hard templates unchanged
- **Clowder Hall hub dimension** `clowderhall:clowder_hall` — void flat datapack dim; Java `ensureHubHall` builds ~15×15 deepslate/cyan terracotta ceremony pad at ~0,64,0 (beacon, lectern, banners, glow plaques, starter chest). Enter stores return pos in player persistentData; `/clowder return` or missing save → overworld spawn. Does not touch skyblock overworld islands.

### Tribal / The March
- **March noise terrain** shipped — Gate Drum → `tribalpower:the_march` with hills/valleys across **steppe**, **highlands**, and **crystal fields** (no longer flat-slab-only)

### Progression gates (KubeJS)
- Distinct Strand token recipes (frayed thread + strand-flavored mats)
- Soft Create `precision_mechanism` and AE2 controller crafts require Voidloom binders
- Loom Braid: any two of Clock/Swarm/Spark tokens → braid_cord; soft-gates AE2 molecular assembler
- Voidloom meshes tagged for Ex Deorum sieves and share string/flint/iron drop tables
- Spindle Loom Fragment craft requires all nine Strand tokens **plus `tribalpower:march_stone`**
- **Tribal Power jar present** — Hum recipes live in the jar (no KubeJS dupes); Spark soft-gates toward Hum; Sigil requires braid_cord on Bind path; Tribal chapter order Chime → Shard → Codex
- **Loom Tension** (`loom_tension.js`) — per-player `ncs_tension`; +1 per Strand token; +3 / +5 once for braid / Spindle fragment; soft unlocks at 5 / 9 / 14 (Thread, Codex pages, spare braid)

### Third-party (1.21.1 NeoForge)
- Skyblock: Ex Deorum, Skyblock Builder, LibX, Sky GUIs, FTB Quests/Teams/Chunks/Library, Forgiving Void
- Agri: Mystical Agriculture, Farmer's Delight, Productive Bees, Botany Pots
- Tech: Create, AE2, KubeJS, Almost Unified, Powah, Mekanism (as available)
- Tools/Magic: Silent Gear (TiC substitute), Nature's Aura + Occultism + Iron's Spells (Botania substitute stack)
- UI: **FancyMenu** 3.9.12 (+ Konkrete, Melody) — title sky still + soft parallax, paw logo/window icons, Codex tagline, Realms hidden, global indigo/teal nine-slice button skins

### Pack QA
- `tools/gates/Invoke-AllGates.ps1` structure, quest consistency, item-ID, public-surface, and export dry-run gates

### Quest fantasy
- **Recover (Stone)** — yarn → hammer/mesh → Tension Barrel clay → porcelain clay/bucket → sieve grit → binding knot → loomframe (early: unravel Thread→string→yarn; slime = pad compost)
- **Spark (Hum)** — brief redstone foothold, then Drumheart / Pulse / Ley / Resonator before Powah FE bridges (Mek stays side)
- **Frayed Thread Desk** — consumes Thread for QoL / alternate mats (saplings, meshes, slime, pearls, storage…); no Thread-for-Thread tithes

### Polish (2026-09-06)
- Recover softlock closed: unravel Thread→string; 4 string→2 yarn; pad-compost slime; Stone sieve-before-knot; Normal kit 6 Thread
- Spindle Hammer craft is cobble (stone-tier) — no iron-before-sieve softlock
- Pad claim wipe: Normal/Easy/Hard chests restore Codex + Charter + Hub Key + How to Start; Hard Thread×6 for Recover; Dock plaque → Charter / Create Team
- Dock spawn protection no longer blocks chest/lectern/Charter use; yarn→string sink is lossy (no infinite loop)
- Charter: Create Team **only** on overworld Dock; Hall no longer false-Dock; pad seals spawn only
- FancyMenu welcome marks seen on open (ESC safe); ticker ~2s
- Soft hardcore lives wired (default off); ops `/skybound revive` restores lives + Survival + respawn/Dock seat
- `/clowder return` requires being in Clowder Hall; Hall dimension lang keys added
- Removed KubeJS Tribal Hum recipe duplicates; Tribal chapter reordered to jar deps
- download-mods drops unavailable Botania/Tinkers/Mantle targets
- Strand tokens stack to 16; braid tooltips warn they are consumed before Spindle trophy
- Spindle fragment recipe guarded with `Item.exists('tribalpower:march_stone')`
- Frayed Thread Desk consumes Thread for real QoL rewards
- Loom Tension milestones 5 / 9 / 14; Voidloom BE client sync packets
- JEI hides Occultism ritual dummy icons; Strand Banner Pattern craft
- `pack.toml` no longer claims a missing packwiz `index.toml`
- Tribal Power jar pin **2.0.1**
- First-join kit includes Island Charter + Hub Key (registry soft-dep)
- Hard pad chest: ice×2 + lava + empty bucket for Soil cobble/water before Recover
- `/clowder revive` self (spectator) or `/clowder revive <player>` for Clowder mates; ops `/skybound revive`
- Clowder Hall ceremony chest aligns with Dock kit (Codex, Charter, Hub Key, How to Start, Thread)
- Spark Hum ladder matches Tribal jar (Chime→Shard→Resonator→Drumheart…); Tribal Codex after Copper
- Sigil braid early (not behind golden bowl); Spindle Reweave after controller (not vibration chamber)
- Charter seals only overworld pads; Hub Key toggles Hall enter/leave; Desk sells leather for Drumheart
- Strand Banner Pattern is a real loom pattern (`clowderhall:strand`); Spindle Crook has leaf speed + `#exdeorum:crooks`
- Tension Barrel returns empty bucket to player (iron or porcelain water); Recover clay → porcelain clay → porcelain bucket order
- Normal/Hard chests include empty bucket; Desk sells bucket; pearl/chorus yarn is truly 2 string → 2 yarn
- Charter off-Dock/Hall cues Dock-only Create Team; How to Start / store / Codex Recover copy aligned
- Recover copy: unravel is 3 string; yarn craft is 4→2; Tension Barrel returns bucket (quest/book/checklist)
- Easy vs Normal/Hard water kit wording fixed; Hard bone meal ×4; starter book v4 synced to island howto
- Desk: Feather + Lapis packs; shop rewards `team_reward: false` under team-default rewards
- Spindle token quest before Loom Fragment (fragment needs all nine tokens)
- Tribal water totem/seal accept porcelain water via KubeJS; Charter refuses mid-air spawn seals
- Hall How to Start + Charter Rules Recover copy synced; Tension Barrel tooltip notes porcelain + return
- Desk: empty bucket early; shop purchases repeatable; orphan repo-root `data/tribalpower` removed

### Planned / in progress
- Client playtest sign-off
- Optional: Drippy loading / macOS window icon / hub Tension plaque

### Onboarding / menu polish (2026-09-06)
- FancyMenu: hide splash + branding clutter; autoscale; disable Buddy + stock FancyMenu welcome; tighten title text so it no longer hangs over buttons
- Pack-owned **Welcome to Ninjacat Skies** popup (Custom GUI) auto-opens once on title; **How to Start** title button reopens it
- Guided pad claim: Island Charter right-click opens Sky GUIs **Create Team** (name + pad template picker); books/signs no longer push bare `/skyblock create`
- Docs/books corrected: real chat shortcut is `/skyblock create <name>` (skips pad pick); guided path is Charter / key **C**

### Client load fix (2026-09-06)
- Added missing NeoForge libraries that blocked first boot: Patchouli, Bookshelf, HammerLib, Prickle, Iron's Lib, SmartBrainLib, GeckoLib, GuideME, Titanium, Player Animator, Modonomicon
- CurseForge export ships `icon.png`, `modlist.html`, `overrides/INSTALL.txt`, store description helpers, and manifest `recommendedRam: 8192` (author-recommended 8 GB)


### Loom Tension is real (2026-09-06)
Strand tokens are no longer crafted. Each Strand chapter ends in a **Knot** quest (checkmark on hand-picked beats) that
rewards the token, a Steward Cache, and levels; a **Seat** quest clears when the token is seated at a **Tension Post**.
- **Tension Post** (`ninjacatskies:tension_post`): logs + Binding Knot + Thread. Seat tokens; nine notches light per tribe;
  chime pitched per Strand; thread helix; steward whisper to the whole Clowder; Codex Page every third seat; the Post hums.
- **Loom Tension is team-scoped** (FTB Teams extra data; solo fallback) and computed from seated Strands — no craft exploit.
  Aura near the Post: Regeneration (any Strand), a little food (Sprout), no fall damage within 48 blocks (Claw),
  Haste (5 Strands), Luck (Sigil), Slow Falling (rewoven). Horizon tint warms per Strand (client, `skyTint` config).
- **Braid Cord** is spun at the Post: Strand Filament + two of Clock/Swarm/Spark seated. **Spindle Loom Fragment**: March
  stone at the Post with all nine seated. Seating the Fragment is the **Reweave**: server broadcast, nine chimes in
  sequence, expanding ring, fireworks, advancement, Slow Falling aura. Tokens stack to 16 as souvenirs; never consumed.
- **The Fray**: a slow dark particle column over the Dock (config `frayX/Y/Z`), thinning with server-wide seated Strands;
  turns to lit thread at full Reweave.
- **Whisker Codex is a Modonomicon book** (right-click; sneak-click for the next-step nudge). Three categories: The Cut,
  The Loom Braid, Nine Tribes (tribe entries unlock on seat via `ninjacatskies:strand/<name>` advancements).
  **Codex Pages** are readable: right-click for a tribe margin note (27 notes; pages keep their tribe when seated).
- Nine distinct token textures; Post block + notch textures; synthesised original sounds (chime, seat, hum, reweave,
  page; Loomframe sift; Barrel settle) via `tools/generate_sounds_loom.py`.
- Voice pass: steward lines, Codex nudges, and ~40 quest descriptions rewritten in-voice; no design-doc language
  ("FE bridges", "bait", "not the title") in player text.

### Voidloom identity (2026-09-06)
- **Loomframe** now sifts on its own: mesh + up to 64 grit, one piece per 2.5 s with a shuttle clack and particles,
  4 output slots, hopper/pipe capability (insert top slot, extract outputs). Thread meshes add **Loom Lint** (4 → yarn),
  **Frayed Thread** (flint+), **Strand Filament** (iron+) to the scrap table.
- **Tension Barrel** batches: 8 water measures (4 per bucket, bucket returned immediately), 8 dirt / string / pearls,
  3 output slots, ring particles while working; string + pearl → **2** yarn. Item handler for hoppers.
- KubeJS `voidloom_sieve.js`: additive Ex Deorum sieve lines for voidloom meshes only (Lint / Thread / Filament).
- Removed: `loom_tension.js`, `steward_lines.js` (now Java), token/braid/fragment crafting recipes.

### Quest regeneration (2026-09-06)
- Generator: cluster lattice (5-beat clusters) instead of 35-deep chains; tiered Thread rewards + a level on heads;
  Knot/Seat quests; `checkmark`, `observation`, `dimension`, `advancement` tasks; command-driven Steward Cache rewards;
  side grids hidden until the chapter's second beat; unique titles (chapter suffix on repeats); Desk purchases have no
  dependencies; Desk repriced (star 200, diamonds 30, shulker 90).
- Reweave chapter opens Loom-native (Spin the Filament → Splice a Braid) and names the digital loom (Cold Weft,
  Charged Warp, Press the Pattern, Digital Loom); ends Knot → Loom Fragment → **Reweave**.
- Clowder chapter opens with Raise the Post (observation), Enter the Hall (dimension), Look at the Fray.
- Unobtainables: heart of the sea / rabbit hide / turtle helmet / wolf armor removed; recovery compass, elytra, totem,
  trident, echo shard, disc, sponge, saddle forced optional. `tools/audit_quest_items.py` now fails on dead ends.
- In-voice descriptions for the Strand chapters (`LORE` table); "Watering Can" duplicate → Bone Block; pad "spare" filler
  quests retired.

### Verification + side chapters (2026-09-06, later)
- **Headless dedicated-server run** (NeoForge 21.1.249, all 64 mods, pack overrides): reaches Done; 8/8 KubeJS scripts, 0 failed recipes (48 added); FTB Quests loads 34 chapters / 1323 quests; Modonomicon loads the Whisker Codex with no entry errors (spotlight pages fixed to ItemStack form). Client rendering/sound still unverified.
- Known item-id list is now the live item registry dump (6,315 ids) instead of a model-file scrape; five stale quest ids fixed (Powah crystals, Ex Deorum pebbles) and five nonexistent ones removed (PackagedAuto AE variants, Pipez clear upgrade). Quest count 1328 → 1323.
- **Every quest description is authored**: `tools/quest_side_lore.py` carries 937 in-voice lines for chapters 10–34 and the remaining Strand-chapter side beats; zero two-word descriptions remain.
- **Clowder Hall Reweave Ring**: twelve deepslate pillars around the ceremony pad; each rewoven Clowder lights a sea lantern and a glowing name plaque. Refreshed on every Hall entry.

### Known gaps
- Client playtest still unchecked after dependency fix (re-import required)
- Optional: Drippy loading screen / macOS window icon
