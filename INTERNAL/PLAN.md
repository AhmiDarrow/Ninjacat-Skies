# Ninjacat Skies — Living Implementation Plan

**Canonical project copy** of the approved implementation plan.

This file is what implementation follows going forward. Public docs (`docs/STORY.md`, README) stay free of agent/INTERNAL language.

---

## Goal

Build **Ninjacat Skies**: a multiplayer void-island quest modpack with an original story, distinctive flair, and custom mods that make the pack feel authored—not assembled.

**Originality rule:** Everything shipped is original or properly licensed. Never copy other packs’ quests, maps, configs, scripts, assets, or branding. Genre (void islands + sieves + farms + quests) is fine; unique story, systems, and prose must be ours.

**Quality bar (non-negotiable):** readable NeoForge code + datagen; hand-consistent pixel art (no AI-slop textures); short specific lore; intentional UI.

**Ship target:** Full **40–60 hour** Normal first clear. All **Nine Strands** authored (**1322** quests / **34** chapters), parallel mid-game routes, Spindle end trophy.

---

## Design mandate — evolve past the classic flow

### What classic was

The familiar void → sieve → farm → forge → power → magic → digital ladder was **inspiration only** — a shared genre grammar so players know how to start standing on a pad. It is **not** the product we are shipping, and it must not remain the identity of the campaign.

### What we are shipping instead

Ninjacat Skies evolves **past** that ladder into a Loom-native campaign shaped as the **Loom Braid**:

1. **Strands are systems, not chapter skins.** Completing a Strand changes how the world/pack behaves (Voidloom tables, Clowder cosmetics, soft recipe unlocks, hub state)—not just the next item checklist in the same old order.
2. **Parallel Clowder specialization beats railroad.** Mid-game is a **braid** (Pattern / Colony / Hum)—farm / bees / Create / pulse-tech / magic routes that can clear content without every player cloning the same furnace→power→AE2 script.
3. **Pack-native loops first.** Voidloom yarn/knots/meshes, Frayed Thread sinks, Loom Tension, Codex journal, and **Tribal Power** (core Hum / Bind / Reweave muscle) sit *beside* Ex Deorum / Create / Mek / AE2 as equal citizens—not decorative stickers on a classic pack.
4. **Late game is reweave, not “AE2 homework.”** Spindle / Loom Fragment / hub rites / March foothold / Clowder monuments should feel like repairing the sky, not only maxing digital storage.
5. **No spiritual-successor cosplay.** Do not chase another pack’s pacing beat-for-beat. If a quest line only exists because “classic packs do this next,” rewrite or cut it.

### Anti-patterns (reject)

- Quest chapters that are only renamed classic milestones with no Loom consequence
- “Magic furnace” or copy-paste RF lines as the only Spark fantasy
- Single mandatory mid-game spine that punishes alternate Clowder roles
- Shipping filler pad-decor as if it were campaign depth without Strand systems behind it
- Shrinking Tribal Power’s standalone feature set “because the pack already has Mekanism”

### Evolution backlog (implement deliberately)

| Pillar | Intent |
|--------|--------|
| Loom Tension | Real milestones with small passives / hub flair / unlock hooks |
| Voidloom depth | Meshes and stations that actually change early–mid resource identity |
| Strand soft/hard gates | Distinct token crafts + a few meaningful recipe gates (not no-ops) |
| Clowder hub ceremony | Working hub teleport, charter fantasy, shared Strand plaques |
| Loom Braid gates | Braid Cord (any 2 of Clock/Swarm/Spark tokens) → Bind → Reweave |
| Tribal core weave | Pulse / Lattice / Rites / March as Hum–Bind–Reweave muscle (see dual mandate) |
| Dimension / portal play | Nether/End footholds plus March as a Reweave site, not afterthoughts |
| Quest authorship | Mix generated density with hand-tuned story beats, journal pages, Steward lines |

---

## Progression — The Loom Braid (approved)

Think of progression as **braiding cut threads back into the Loom**, not climbing a tech tree.

```text
WAKE ──► RECOVER ──► ROOT ──► EDGE
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                 PATTERN   COLONY     HUM
                 (Clock)   (Swarm)   (Spark)
                    │         │         │
                    └─────────┼─────────┘
                              ▼
                            BIND
                           (Sigil)
                              ▼
                          REWEAVE
                          (Spindle)
```

| Phase | Strand(s) | Player fantasy | Familiar hook | What’s new |
|-------|-----------|----------------|---------------|------------|
| **Wake** | Soil | Survive; Codex wakes; claim a pad | Void island start | First Loom Tension scrap; kit/ceremony |
| **Recover** | Stone (+ Voidloom) | Pull fallen world-dust back into matter | Sieves/hammers | Voidloom is the identity; sieve is a tool inside Recover |
| **Root** | Sprout | Grow anchors so the pad stops fraying | Farms / Mystical | Living weave; food as Tension infrastructure |
| **Edge** | Claw | Cut paths; leave the pad safely | Tools / nether | Footholds as cuts in the Loom |
| **Pattern** | Clock | Factory as loom pattern | Create | One of three peer braid paths |
| **Colony** | Swarm | Living industry | Bees / deep crops | Peer braid path—not “after power” |
| **Hum** | Spark | Rhythm / pulse / heat | FE gens | Tribal Pulse is primary Hum fantasy; Mek/Powah are bridges |
| **Bind** | Sigil | Contracts with leftover steward tricks | Magic mods | Tribal rites/seals are core Bind tools; Aura/Ars/Occultism remain peers |
| **Reweave** | Spindle | Stitch the cut | AE2 + trophy | Digital loom + March foothold for full clear |

**Keep:** Nine Strand names, void islands, sieving as a tool, farming, automation, magic, late digital storage, 40–60h density.

**Change:** Order rigidity, phase fantasy, when branches open, what clearing a phase does, late-game meaning.

### Loom Tension glue

- Phase clears grant Tension (scoreboard / Codex / hub plaque)—cosmetic + soft unlocks.
- Spindle expects Tension from Wake+Recover+Root+Edge plus **any two braid paths** plus Bind (tunable; all three braid if longer clear is desired).
- Farm-focused and Create-focused Clowders both remain valid.

### Strand → braid job map

| Strand | Classic inspiration | Braid job |
|--------|---------------------|-----------|
| Soil | void tutorial | **Wake** |
| Stone | sieve age | **Recover** (Voidloom-led) |
| Sprout | farm age | **Root** |
| Claw | forge/tools | **Edge** |
| Spark | power ladder | **Hum** (braid) |
| Clock | Create ladder | **Pattern** (braid) |
| Swarm | bees after power | **Colony** (braid) |
| Sigil | magic after tech | **Bind** |
| Spindle | digital end | **Reweave** |

### Implementation shape (quests / KubeJS)

1. Flexible FTB deps + “Braid Gate”: Bind after any two of Pattern/Colony/Hum (or synthetic **Braid Cord** from any two of those Strand tokens).
2. Recover leads with Voidloom yarn/meshes; Ex Deorum stays the engine underneath.
3. Spark presents Hum options (Drumheart/Pulse and/or Powah/Mek)—not a single RF religion.
4. Spindle trophy stays; full clear expects March foothold / March-attuned component when Tribal ships.
5. Reorder fantasy and gates—do not yank familiar mods out of the pack wholesale.

---

## Storyline — “The Loom Unraveled”

The skies were held by the **Loom of Worlds**. Something cut it. Pads remain. Nine **Strands** still answer.

Players are **Skybound**. Teams are **Clowders**. The **Whisker Codex** assigns work. Completing Strands restores **Loom Tension**.

Tone: wry, tactile, lightly melancholy—repair work in the clouds.

### Nine tribes story bridge (approved)

1. **Nine Ninjacat tribes** tended the Loom; each tribe kept one Strand.
2. From their shared power—drawn through the Loom—**Tribal Power** was born: shamanic technomancy (pulse, lattices, seals, the path into The March).
3. When the Loom was cut, the tribes scattered. Tribal engines left in the world are **orphan technomancy**—usable, dangerous, sacred.
4. Skybound Clowders reweave Strands; learning Tribal systems is learning how the tribes once hummed the Loom.

| Strand | Tribe role (flavor) | Tribal system echo |
|--------|---------------------|--------------------|
| Soil | Pad-keepers | Cache / hearth |
| Stone | Grit-singers | Echo shatter / lattice attunement |
| Sprout | Rootbinders | Living March flora links |
| Claw | Edge-walkers | Spiritgear |
| Spark | Drumhearts | Spirit Pulse / Drumheart |
| Clock | Pattern-weavers | Song Bench / timed lattice songs |
| Swarm | Colony-keepers | Swarming March life |
| Sigil | Seal-carvers | Rites & seals |
| Spindle | Loom-stitchers | Gate Drum → March / reweave tools |

Writing: no anime/games inspiration pitch. Public Tribal voice may speak of steward tribes and a severed lattice without hard-depending on Ninjacat items.

Side boards (Clowder, shop, decor, dimensions, Tribal deep dives) must carry unique fantasy, not only checklist bulk.

---

## Tribal Power — dual mandate (approved)

Tribal Power is **two deliverables**, not one diluted compromise.

### 1) Standalone mod (own GitHub — full original scope)

- Repo: `https://github.com/AhmiDarrow/Tribal-Power`
- Branch: `rewrite/shamanic-technomancy` (sibling checkout `tribal-power`)
- Must ship as a **complete NeoForge 1.21.1 mod** playable without Ninjacat Skies.
- Pillars: Spirit Pulse, Totem Lattice + Echo stages, Ancestral/Deep Cache, seals & rites, spiritgear, Gate Drum, **The March**, in-book wiki, replaced assets.
- Success bar: ores → lattice → pulse → storage → rites → March → endgame gear with **no** soft-require on Ninjacat items, Codex, Strands, or Voidloom.
- Ninjacat hooks stay optional / pack-scripted—never hard deps in Tribal’s `mods.toml`.

### 2) Weave into Ninjacat Skies as a core pack pillar

| Braid phase | Tribal’s job in the pack |
|-------------|--------------------------|
| Wake / Recover / Root | Light touch only; no Tribal softlock early |
| Edge | Optional seals/gear previews; Silent Gear led |
| **Hum (Spark)** | **Primary power fantasy** (Drumheart + Spirit Pulse); Mek/Powah are bridges |
| Pattern / Colony | Create / bees lead; Lattice may assist, not replace |
| **Bind (Sigil)** | **Core binding path** (rites + seals) beside Aura/Ars/Occultism |
| **Reweave (Spindle)** | AE2 digital loom **and** March foothold / Gate Drum for full clear |

**Weave rule:** Pack integration adds quests, gates, and story—it does **not** shrink Tribal’s standalone feature set.

### Ownership split

| Layer | Owner |
|-------|--------|
| Pulse, Lattice, Echo, Caches, Seals, Spiritgear, March, guidebook, VFX | **Tribal Power repo** |
| Codex, Strands, Loom Tension, Voidloom, Clowder, FTB quest spine, pack gates | **Ninjacat Skies repo** |
| When the player meets Drumheart / March | **Pack weave** (quests / KubeJS) |

### Pack integration rules

1. Ship Tribal jar in `pack/mods` like other cores—pinned rewrite builds.
2. Quests: side chapter **and** woven Hum / Bind / Reweave beats.
3. Never gate Soil–Root on Tribal.
4. Codex frames Tribal as steward technomancy left in the cut—not a second protagonist dump.
5. Tribal guidebook owns block docs; FTB quests teach timing, not every recipe wall.
6. Playtest twice: Tribal alone, then Ninjacat pack.

---

## Platform

| Choice | Value |
|--------|--------|
| Minecraft | **1.21.1** |
| Loader | **NeoForge 21.1.x** (~21.1.249) |
| Java | **21** |

---

## Custom mods

1. **ninjacatskies** — Codex, kits, tokens, Spindle Loom Fragment, Braid Cord, story glue
2. **voidloom** — Pack-native void crafting (enhance Ex Deorum, don’t clone it)
3. **clowderhall** — Hub ceremony, charter, `/clowder` commands
4. **ninjacat-lib** — Thin shared helpers

**Tribal Power** is peer-repo core content (dual mandate above)—not a fifth kitchen-sink jar owned inside this tree.

Ninjacat still owns: Whisker Codex, Clowders, Nine Strands, Loom Tension, Voidloom, Spindle trophy, pack voice.

---

## Verification (evolved)

1. Client boots; island → **Voidloom-feeling** early game (Recover identity, not only vanilla sieve cosplay)
2. Mid-game offers at least two viable braid paths (Pattern / Colony / Hum) for a Clowder
3. Strand clears have a visible/pack consequence beyond a checkmark
4. Spindle trophy craftable from all nine tokens; full clear path expects March when Tribal is woven
5. Gates + originality + export stay green
6. No public text claims we are a named legacy pack’s sequel
7. Tribal alone remains playable without Ninjacat softlocks

---

## Amendment log

| Date | Change |
|------|--------|
| 2026-09-05 | Promoted durable `INTERNAL/PLAN.md` from session plan; added **evolve past classic flow** mandate (classic ladder = inspiration only). |
| 2026-09-05 | Synced approved **Loom Braid** progression, **Tribal dual mandate** (standalone GitHub + core pack weave), and **nine tribes** story bridge. |
