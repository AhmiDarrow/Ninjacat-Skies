# Changelog

## 0.1.0-alpha (in progress)

### Scope
- Target playtime: **40–60 hours** Normal first clear
- FTB Quests: **1324** quests across **34** chapters (item-ID audit clean; titles + short descs in `en_us.snbt`)
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

### Known gaps
- Client playtest still unchecked after dependency fix (re-import required)
- Some side chapters remain thinner than the Strand spine
- Optional: Drippy loading screen / macOS window icon
