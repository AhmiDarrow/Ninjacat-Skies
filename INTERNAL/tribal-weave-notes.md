# Tribal Weave Notes (private)

Tribal Power is steward technomancy born from the Loom — nine tribes once hummed the lattice; Skybound stewards relearn the beat.

## Weave plan: Hum / Bind / Reweave

Three weave phases map onto Tribal systems and Echo stages.

### 1. Hum

Pulse generation and lattice setup. No refinement yet — only rhythm.

- **Drumheart** / **Ley Collector** store Spirit Pulse (not FE).
- **Bone Chime**, **Copper Resonator**, **Ritual Chalk** are the first tools of tempo and line.
- Plant **Resonance Totems** (Earth / Fire / Water / Air / Spirit) near a **Song Bench**.
- **Lattice Conductor** routes harmonics between totems.
- Goal: a living song that answers when the bench starts.

### 2. Bind

Echo mid-stages knot spirit into matter.

- **Echo Shatter** → **Shattered Ore** (break the songless lump).
- **Echo Attune** → **Attuned Ore** (find a key).
- **Echo Bind** → **Bound Ore** (knot that will not slip).
- Seals (**Blank** → elemental → **Spirit**) prepare rites on the **Rite Pedestal**.
- **Ancestral Cache** holds local tribute; Pulse Cells carry beats between stations.

### 3. Reweave

Manifest and travel — Loom-facing end of the tribal side path.

- **Echo Manifest** → **Manifest Ingot** (call metal the tribes would recognize).
- **Spiritgear** tools spend Pulse while working.
- **Deep Cache** links storage toward **The March**.
- **Gate Drum** / **Spirit Door** open the otherworld; March blocks and **Spirit Reed** are proof of travel.
- Closing beat: steward technomancy as a peer route beside Voidloom — same Loom, different tribe song.

## Pack integration

- Jar: `pack/mods/tribalpower-2.0.1.jar` (present — weave started).
- Quests: chapter `34_tribal` via `tools/generate_quests.py` → `build_tribal_side()` (do not shrink).
- Spark soft-gates Hum (Drumheart / Pulse Cell / Bone Chime); Sigil requires braid_cord; Spindle trophy needs `march_stone`.
- Tribal 2.0.1+ ships Hum recipes in-jar. Pack KubeJS must **not** duplicate them. Quest chapter `34_tribal` order matches jar deps (Chime → Shard → Codex).
- Item IDs: refresh with `python tools/extract_item_ids.py` after jar copy; audit with `python tools/audit_quest_items.py`.

## Voice

Codex voice, short. Concrete verbs: hum, bind, reweave, strike, offer, route. No chosen-one prophecy; tribes as forgotten craft lines, not pantheons.
