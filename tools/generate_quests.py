#!/usr/bin/env python3
"""Generate original FTB Quests for Ninjacat Skies (40–60h density target)."""
from __future__ import annotations

import json
import math
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from quest_side_lore import SIDE_LORE  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
QUESTS = ROOT / "pack/overrides/config/ftbquests/quests"
CHAPTERS = QUESTS / "chapters"
LANG = QUESTS / "lang"
KNOWN = set((ROOT / "INTERNAL/known_item_ids.txt").read_text(encoding="utf-8").split()) if (
    ROOT / "INTERNAL/known_item_ids.txt"
).exists() else set()

WARNED: set[str] = set()


def hid(n: int) -> str:
    return f"{n:016X}"


GROUP_SURVIVAL = hid(0xA100000000000001)
GROUP_CRAFT = hid(0xA100000000000002)
GROUP_LATE = hid(0xA100000000000003)
GROUP_SIDE = hid(0xA100000000000004)

CH = {
    "soil": hid(0xB100000000000001),
    "stone": hid(0xB100000000000002),
    "sprout": hid(0xB100000000000003),
    "claw": hid(0xB100000000000004),
    "spark": hid(0xB100000000000005),
    "clock": hid(0xB100000000000006),
    "swarm": hid(0xB100000000000007),
    "sigil": hid(0xB100000000000008),
    "spindle": hid(0xB100000000000009),
    "exdeorum": hid(0xB10000000000000A),
    "storage": hid(0xB10000000000000B),
    "mekanism": hid(0xB10000000000000C),
    "powah": hid(0xB10000000000000D),
    "ars": hid(0xB10000000000000E),
    "clowder": hid(0xB10000000000000F),
    "shop": hid(0xB100000000000010),
    "aura": hid(0xB100000000000011),
    "food": hid(0xB100000000000012),
    "spells": hid(0xB100000000000013),
    "solar": hid(0xB100000000000014),
    "decor": hid(0xB100000000000015),
    "nether": hid(0xB100000000000016),
    "end": hid(0xB100000000000017),
    "crops": hid(0xB100000000000018),
    "bees": hid(0xB100000000000019),
    "pipes": hid(0xB10000000000001A),
    "occult": hid(0xB10000000000001B),
    "factory": hid(0xB10000000000001C),
    "network": hid(0xB10000000000001D),
    "voidcraft": hid(0xB10000000000001E),
    "packaged": hid(0xB10000000000001F),
    "qio": hid(0xB100000000000020),
    "mobfarm": hid(0xB100000000000021),
    "tribal": hid(0xB100000000000022),
}

lang: dict[str, object] = {
    f"chapter_group.{GROUP_SURVIVAL}.title": "Skybound",
    f"chapter_group.{GROUP_CRAFT}.title": "Craft & Tension",
    f"chapter_group.{GROUP_LATE}.title": "Reweave",
    f"chapter_group.{GROUP_SIDE}.title": "Side Paths",
    "file.0000000000000001.title": "Ninjacat Skies",
}

_seq = {"q": 0}


def next_ids(strand_i: int):
    _seq["q"] += 1
    i = _seq["q"]
    return (
        hid(0xC200000000000000 + strand_i * 0x10000 + i),
        hid(0xD200000000000000 + strand_i * 0x10000 + i),
        hid(0xE200000000000000 + strand_i * 0x10000 + i),
    )


def valid_item(item: str) -> bool:
    if item.startswith("minecraft:"):
        return True
    if not KNOWN:
        return True
    ok = item in KNOWN
    if not ok and item not in WARNED:
        WARNED.add(item)
        print("SKIP invalid item", item)
    return ok


def to_snbt(obj, indent=0) -> str:
    sp = "\t" * indent
    if isinstance(obj, dict):
        lines = ["{"]
        items = list(obj.items())
        for i, (k, v) in enumerate(items):
            lines.append(f"{sp}\t{k}: {to_snbt(v, indent + 1)}")
        lines.append(sp + "}")
        return "\n".join(lines)
    if isinstance(obj, list):
        if not obj:
            return "[ ]"
        if all(isinstance(x, str) for x in obj):
            return "[" + ", ".join(json.dumps(x) for x in obj) + "]"
        lines = ["["]
        for v in obj:
            lines.append(f"{sp}\t{to_snbt(v, indent + 1)}")
        lines.append(sp + "]")
        return "\n".join(lines)
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, int):
        return str(obj)
    if isinstance(obj, float):
        return f"{obj}d"
    if isinstance(obj, str):
        if obj.endswith("d") and obj[:-1].replace(".", "", 1).replace("-", "", 1).isdigit():
            return obj
        return json.dumps(obj)
    raise TypeError(type(obj))


def write_chapter(filename: str, chapter_id: str, group: str, order: int, icon: str, quests: list[dict], title: str) -> None:
    lang[f"chapter.{chapter_id}.title"] = title
    if order + 1 in CHAPTER_SUBTITLES:
        lang[f"chapter.{chapter_id}.subtitle"] = CHAPTER_SUBTITLES[order + 1]
    quests = list(quests) + secret_quest(order + 1, -3.0, -2.0)
    quests = finalize_chapter(order + 1, quests)
    body = {
        "default_hide_dependency_lines": False,
        "default_quest_shape": "",
        "filename": filename,
        "group": group,
        "icon": {"id": icon},
        "id": chapter_id,
        "images": [],
        "order_index": order,
        "quest_links": [],
        "quests": quests,
    }
    CHAPTERS.mkdir(parents=True, exist_ok=True)
    (CHAPTERS / f"{filename}.snbt").write_text(to_snbt(body) + "\n", encoding="utf-8")


def item_quest(
    strand_i: int,
    *,
    title: str,
    desc: list[str],
    item: str,
    count: int = 1,
    reward_item: str | None = None,
    reward_count: int = 1,
    deps: list[str] | None = None,
    x: float = 0.0,
    y: float = 0.0,
    optional: bool = False,
    consume: bool = False,
) -> dict | None:
    if not valid_item(item) or item in REMOVE_ITEMS:
        return None
    if item in FORCE_OPTIONAL:
        optional = True
        desc = list(desc) + ["Optional — the void may never offer one."]
    if strand_i in SIDE_LORE and title in SIDE_LORE[strand_i]:
        desc = [SIDE_LORE[strand_i][title]]
    if strand_i in STRAND_CHAPTERS and title in LORE and len(LORE[title][0].split()) > 2:
        desc = list(LORE[title])
    reward = reward_item or "ninjacatskies:frayed_thread"
    if not valid_item(reward):
        reward = "minecraft:experience_bottle"
    q, t, r = next_ids(strand_i)
    lang[f"quest.{q}.title"] = title
    lang[f"quest.{q}.quest_desc"] = desc
    task: dict = {"id": t, "type": "item", "item": {"id": item, "count": count}}
    if consume:
        task["consume_items"] = True
    entry: dict = {
        "id": q,
        "x": f"{round(x, 1)}d",
        "y": f"{round(y, 1)}d",
        "tasks": [task],
        "rewards": [{"id": r, "type": "item", "item": {"id": reward, "count": reward_count}}],
    }
    if deps:
        entry["dependencies"] = deps
    if optional:
        entry["optional"] = True
    return entry



# ---------------------------------------------------------------- authored layer (2026-09-06)

# Short names for unique-title suffixes.
CHAPTER_SHORT = {
    1: "Soil", 2: "Stone", 3: "Sprout", 4: "Claw", 5: "Spark", 6: "Clock", 7: "Swarm", 8: "Sigil", 9: "Spindle",
    10: "Sieve", 11: "Storage", 12: "Mek", 13: "Powah", 14: "Ars", 15: "Clowder", 16: "Desk", 17: "Aura",
    18: "Kitchen", 19: "Spells", 20: "Solar", 21: "Decor", 22: "Nether", 23: "End", 24: "Fields", 25: "Apiary",
    26: "Pipes", 27: "Otherworld", 28: "Clockworks", 29: "Network", 30: "Voidcraft", 31: "Packaged", 32: "QIO",
    33: "Hunt", 34: "Tribal",
}
STRAND_CHAPTERS = {1: "soil", 2: "stone", 3: "sprout", 4: "claw", 5: "spark", 6: "clock", 7: "swarm", 8: "sigil", 9: "spindle"}
CURRENT = {"strand_i": 0, "title_counts": {}}

# Items the void world cannot produce on the main line. REMOVE drops the quest; OPTIONAL keeps it as a side note.
REMOVE_ITEMS = {"minecraft:heart_of_the_sea", "minecraft:rabbit_hide", "minecraft:turtle_helmet", "minecraft:wolf_armor"}
FORCE_OPTIONAL = {"minecraft:recovery_compass", "minecraft:elytra", "minecraft:totem_of_undying", "minecraft:trident",
                  "minecraft:echo_shard", "minecraft:music_disc_cat", "minecraft:sponge", "minecraft:saddle"}

# Phrases that were design-doc voice. Exact-string swaps applied to every description line.
VOICE_FIX = {
    "Sieve is a tool, not the title.": "Grit-singers named every shard by its echo. Sieve until you can hear the iron.",
    "FE bridge buffer — not the Hum religion.": "A buffer for Forge Energy — the bridge from Pulse to wire, if you want one.",
    "Burn for FE.": "Burn fuel for Forge Energy.",
    "Pocket FE.": "A pocketful of stored power.",
    "Pocket FE+.": "A bigger pocket of stored power.",
    "Simple FE pipes.": "Plain energy pipes between machines.",
    "FE centrifuge.": "A powered centrifuge for combs.",
    "Feed FE into machines.": "Feed power into the digital loom.",
    "FE smelt.": "A powered smelter.",
    "FE cable.": "Energy cable.",
    "Store a pulse of FE.": "Store a measure of power.",
    "If found — optional.": "If the void ever offers one. Optional.",
    "If you somehow find water seas.": "For the day someone builds a sea. Optional.",
    "If present — late.": "Late. Only if the Aura wants it.",
    "If available.": "Only if one turns up.",
    "Summon focus — Bind braid is already on the main path.": "A focus for summoning. The rites are patient.",
    "Spark tensioned. Hum ladder Chime→Shard→Resonator→Drumheart; Powah/Mek are FE bridges.": "Spark tensioned. The drum keeps time now.",
    "Sigil tensioned. Braid held for Bind; Spindle assemblers and March trophy wait ahead.": "Sigil tensioned. The seals hold.",
    "Another Strand tensioned.": "Another Strand answers.",
    "Amethyst block for Sigil bait.": "Amethyst in a block. Sigil will want shards later.",
    "Spark Strand bait.": "Spark will want this. Keep it dry.",
    "Trade bait.": "Villagers like these. So does the Desk.",
    "Sigil bait.": "Sigil will want these.",
    "Swarm bait.": "Swarm will want this.",
    "Boss bait.": "For a fight you choose on purpose.",
    "Boss bait trio.": "Three fights, chosen on purpose.",
    "End pollen bait.": "End flora for the bees that want it.",
    "Tough bee bait.": "The bees that live in hard places.",
    "Purple bait.": "Chorus for the End-minded.",
    "Teleport bait.": "For skipping the drop.",
    "Brew bait.": "Brew stock.",
    "Watering Can": "Bone Block",
    "Braid any two of Clock, Swarm, or Spark tokens into a cord. Soft-gates the molecular assembler.":
        "Spun at the Tension Post: a Strand Filament, with two of Clock, Swarm, or Spark seated. The assembler wants one at its heart.",
    "Loom braid required for Bind — any two of Clock, Swarm, or Spark tokens.":
        "Right-click the Tension Post with a Strand Filament once two of Clock, Swarm, or Spark are seated. Bind begins here.",
    "Nine Strand tokens plus March stone — Spindle end trophy.":
        "Right-click the Tension Post with a March stone once all nine Strands are seated. Then seat the Fragment itself.",
    "Fluix + Binding Knot + Thread — ninth token before the trophy.": "The ninth Strand. Its Knot is at the end of this chapter.",
    "March-attuned footing — Gate Drum into The March; trophy needs one.": "Footing from beyond the gate. The Spindle wants one.",
    "Build from patterns — needs braid_cord in the craft.": "Builds from patterns. Wants a Braid Cord at its heart.",
    "Unravel Thread → 3 string; craft 4 string → 2 yarn. Later: 2 string + pearl/chorus → 2 yarn.":
        "Unravel Thread to string; four string spin two yarn. Later the Tension Barrel does it better with a pearl.",
    "Hub shop seed money.": "Every quest returns a little. The Desk chapter spends it.",
}

# In-voice descriptions for the Strand chapters, keyed by quest title. Two lines: what, and why.
LORE = {
    # Soil
    "Wake on a Pad": ["You are Skybound. This is what did not fall.", "Eight logs. Start with the tree; it started with you."],
    "Something to Stand On": ["Dirt is a promise the pad makes to your boots.", "Sixteen blocks. Widen the promise."],
    "Craft a Bench": ["Hands need a surface. Everything after this is a surface."],
    "Wooden Pick": ["Claw comes later. For now, wood that bites."],
    "First Sapling": ["Green against the drop.", "Plant it before you are hungry."],
    "Plank Stock": ["Sixty-four planks is a pad that stops feeling like a ledge."],
    "Stick Bundle": ["Handles, frames, the bones of tools."],
    "Chest for the Clowder": ["Put things where they stay. A Clowder shares a chest before it shares anything else."],
    "Torch Line": ["See the edge before the edge sees you."],
    "Cobble Cache": ["Ice and lava make stone where there was none.", "Normal and Hard pads ship both. The Desk sells a bucket."],
    "Furnace Heat": ["Warmth that is not yet Spark.", "The Pad-keepers would have called this a hearth."],
    "Cook a Meal": ["Hunger is a soft void. Eight loaves closes it for a while."],
    "Catch the Rain": ["Place lava, melt ice into a source, fill the bucket.", "Easy ships water; Normal and Hard ship the pieces."],
    "Frayed Currency": ["Scraps of the Loom that still hold. Every quest returns some.", "Unravel one for string, or spend them at the Desk."],
    "Codex in Hand": ["Damaged, but it still assigns work.", "Right-click to open. Sneak-click when you are lost."],
    # Stone
    "Pull Void Yarn": ["Thread that remembers where it came from.", "Unravel Thread to string; four string spin two yarn."],
    "Spindle Hammer": ["Cobble and sticks. Break fallen grit into gravel, sand, dust."],
    "Thread the Mesh": ["String around yarn. It catches what the Loom dropped — and combs Loom Lint out of dirt."],
    "Tension Barrel": ["Pour water; the bucket comes straight back. Add dirt. Wait for clay.", "String and a pearl in the same barrel make yarn."],
    "Clay Pocket": ["Sixteen clay from the barrel. Load eight dirt at a time."],
    "Porcelain Clay": ["Clay and bone meal. Shape the unfired bucket."],
    "Porcelain Tool": ["Smelt it. Porcelain carries lava where iron is still a rumour."],
    "Sift Fallen Grit": ["Grit-singers named every shard by its echo.", "Sieve until you can hear the iron."],
    "Wooden Hammer": ["A spare set of hits."],
    "Pebbles": ["Matter from grit. Sixty-four stones that were dust an hour ago."],
    "Gravel Path": ["Loom dust waits in gravel. So does flint."],
    "Sand Cache": ["Fine grit. Glass later, and the iron mesh's best catch."],
    "Dust Pile": ["Ash of the fallen world. Redstone and gunpowder hide in it."],
    "Tie Binding Knot": ["Yarn around slime. Pad compost makes the slime.", "The Knot is the Loom's soft gate; keep two."],
    "Raise Loomframe": ["Planks around a Knot. Stretch a mesh, load grit, let it work.", "Hoppers feed it. This is the pad's first machine."],
    "Iron Ore Chunk": ["Iron is low and patient. Eight chunks from the mesh."],
    "Copper Ore Chunk": ["Conductive thoughts."],
    "Gold Ore Chunk": ["Gold barely bothers to answer. Four is enough."],
    "Coal": ["Fuel the line."],
    "Raw Iron": ["Chunks to raw. Smelt onward."],
    "Iron Ingot": ["Recover pays out. Sixteen bars the void did not want you to have."],
    "Copper Ingot": ["Wire and bulbs, and Tribal resonators later."],
    "Gold Ingot": ["Gilded tools, and gold plates for the pattern-weavers."],
    "Flint Mesh": ["Sharper catch. Flint meshes shake Frayed Thread out of grit."],
    "Iron Mesh": ["Metal thread for heavier dust. Iron meshes are where Strand Filament falls."],
    "Crucible": ["Melt and drip. Cobble to lava, given time."],
    "Barrel": ["Ex Deorum's barrel: compost, and water into clay the slow way."],
    "Stone Hammer": ["Harder hits, longer life."],
    "Iron Hammer": ["Serious grit."],
    "Compressed Sieve": ["Wider mesh, nine at a time."],
    "Glass": ["See through. Sand to glass."],
    "Bucket": ["Carry the rain in iron now."],
    "Lava Bucket": ["Heat from the void, in hand."],
    "Obsidian": ["Portal thoughts. Water on lava source."],
    "Diamond": ["Rare grit luck. Two is a start."],
    # Sprout
    "Iron Hoe": ["Scratch rows into the pad."],
    "Wheat Field": ["Bread is infrastructure. Thirty-two wheat is a field, not a patch."],
    "Seed Pouch": ["Plant what you eat."],
    "Bone Meal Engine": ["Speed is kindness. Compost and bones."],
    "Farmers Knife": ["Prep the harvest."],
    "Cutting Board": ["A kitchen starts here."],
    "Cooking Pot": ["Warm meals feed more than hunger."],
    "Inferium": ["Essence farming begins. Sixteen from the first row."],
    "Prosperity": ["The seed backbone. Sieve or grow it."],
    "Infusion Altar": ["Raise seeds from essence."],
    "Infusion Pedestal": ["Four around the altar."],
    "Dirt Seeds": ["Grow more pad."],
    "Wood Seeds": ["Grow canopy without the axe."],
    "Stone Seeds": ["Grow grit."],
    "Iron Seeds": ["Metal from leaves. Recover's second engine."],
    "Water Seeds": ["Bottled rain from a crop."],
    "Botany Pot": ["Compact growth for a small pad."],
    "Hopper Pot": ["The pot that harvests itself."],
    "Prudentium": ["Tier up. The seeds get greedier and better."],
    "Tertium": ["Deeper green."],
    "Bone Block": ["Nine meal to a block. Storage for the engine."],
    "Hay Silo": ["Sprout surplus, stacked."],
    "Rich Soil": ["Better farmland. Rootbinders would approve."],
    "Organic Compost": ["Feed the soil that feeds you."],
    # Claw
    "Blueprint Paper": ["Cut the void on your terms. Eight sheets of plans."],
    "Blueprint Package": ["Plans in a box."],
    "Rod Blueprint": ["Tool bones."],
    "Pick Blueprint": ["Shape a pick that outlives its metal."],
    "Sword Blueprint": ["Shape a blade."],
    "Upgrade Base": ["Room to grow."],
    "Iron Mass": ["Thirty-two bars of material for parts."],
    "Diamond Tip": ["Claw sharpens."],
    "Shears": ["Leaves and wool, and combs later."],
    "Shield": ["Pads have edges. So do mobs."],
    "Iron Chestplate": ["Survive the night on purpose."],
    "Bow": ["Keep the void's mobs at a distance."],
    "Arrow Bundle": ["Sixty-four reasons to keep distance."],
    "Flint and Steel": ["Light the way through."],
    "Obsidian Frame": ["Ten blocks. A door the Edge-walkers would recognise."],
    "Ender Eye": ["Foothold prep. Somewhere else exists."],
    "Enchanting Table": ["Soft power for hard tools."],
    "Anvil": ["Repair and name what you carry."],
    "Name Tag": ["Call it yours."],
    # Spark
    "Redstone Dust": ["A brief signal before the Hum. Sixty-four dust."],
    "Furnace Array": ["Parallel heat. Eight is a line, not a furnace."],
    "Hopper Line": ["Move the grit without hands."],
    "Comparator": ["Measure the beat."],
    "Hum: Bone Chime": ["Bone, string, amethyst. The first beat.", "It yields two — keep one for the Spirit Codex."],
    "Hum: Spirit Shard": ["A shard of old tribe song. Needs a Chime."],
    "Hum: Copper Resonator": ["Copper around a Chime: metal tuned to spirit."],
    "Hum: Drumheart": ["Strike it. Hold a Pulse. Listen before you wire anything.", "Chime, Shard, leather — the Desk sells leather."],
    "Hum: Pulse Cell": ["Carry Pulse between drum and lattice."],
    "Hum: Ley Collector": ["Draw ambient ley into beats near a Drumheart."],
    "Hum: Pulse Resonator": ["Burn coal for denser beats beside Drumheart and Ley."],
    "Powah Starter Cell": ["A buffer for Forge Energy — the bridge from Pulse to wire, if you want one."],
    "Powah Furnator": ["Burn fuel for Forge Energy."],
    "Powah Cable": ["Move energy along."],
    "Solar Panel Starter": ["Sky power, on a pad that is all sky."],
    "Energizing Orb": ["Charge items in a ring of rods."],
    "Battery": ["A pocketful of stored power."],
    # Clock
    "Andesite Alloy": ["Hands that work while you sleep. Thirty-two."],
    "Shaft": ["The rotation spine."],
    "Cogwheel": ["One cog. Then the same cog again."],
    "Large Cog": ["More teeth, slower turn."],
    "Water Wheel": ["A river in the sky, turning."],
    "Millstone": ["Mill grit into dust without a hammer."],
    "Mechanical Press": ["Plates and paths."],
    "Mechanical Mixer": ["Bulk recipes, fast."],
    "Encased Fan": ["Washing, drying, and gravel into sand."],
    "Deployer": ["A hand on a shaft."],
    "Precision Mechanism": ["Clockwork heart. Wants a Binding Knot at its centre.", "The Loom, asking to be included."],
    "Sequenced Gearshift": ["Programmed spin. The pattern-weavers' song, written down."],
    # Swarm
    "Honeycomb": ["Colonies in the wind. The Desk sells comb if none drift by."],
    "Beehive": ["A home for workers."],
    "Advanced Beehive": ["A productive home."],
    "Centrifuge": ["Spin combs into everything they hide."],
    "Incubator": ["Hatch the genes you want."],
    "Gene Indexer": ["Sort traits like seed."],
    "Imperium": ["High essence. The fields are industry now."],
    "Supremium": ["Peak green."],
    "Honey Block": ["Swarm surplus, stacked."],
    # Sigil
    "Amethyst": ["The stewards left tricks in crystal. Thirty-two shards."],
    "Braid Cord": ["Right-click the Tension Post with a Strand Filament once two of Clock, Swarm, or Spark are seated.", "Bind begins here."],
    "Book and Quill": ["Write the rite before you carve it."],
    "Brewing Stand": ["Bottled tricks."],
    "Dragon Breath": ["Breath of the thing that guards the End."],
    "Source Gem": ["Ars fuel."],
    "Novice Spell Book": ["First spells. Peer magic, if you want it beside the rites."],
    "Occultism Dictionary": ["Call spirits by their names."],
    "Spirit Fire": ["Otherworld light."],
    # Spindle
    "Spin the Filament": ["An iron mesh, gravel or sand, patience.", "Strand Filament is the Loom's own thread. The braid is spun from it."],
    "Splice a Braid": ["Two braid paths seated, one Filament, one right-click on the Post.", "Bind has begun; Reweave starts here."],
    "Cold Weft": ["Certus quartz — the cold thread of a digital loom."],
    "Charged Warp": ["Fluix — certus, quartz, and redstone charged in water."],
    "Press the Pattern": ["The inscriber presses circuits the way a loom presses cloth."],
    "Digital Loom": ["The controller. Wants a Binding Knot at its centre.", "Spindle core."],
    "Gate Drum": ["Strike it open. The March is on the other side."],
    "March Stone": ["Footing from beyond the gate. Bring one home."],
    "Loom Fragment": ["Nine seated, one March stone, one right-click on the Post: the Fragment.", "Seat it. The cut closes above your pad."],
    "Molecular Assembler": ["Builds from patterns. Wants a Braid Cord at its heart."],
}

# Knot beats: hand-picked mainline titles whose completion tensions the Strand.
KNOT_BEATS = {
    "soil": ["Craft a Bench", "First Sapling", "Furnace Heat", "Catch the Rain", "Codex in Hand"],
    "stone": ["Pull Void Yarn", "Porcelain Tool", "Raise Loomframe", "Iron Ingot", "Iron Mesh"],
    "sprout": ["Wheat Field", "Cooking Pot", "Infusion Altar", "Iron Seeds", "Prudentium"],
    "claw": ["Blueprint Package", "Pick Blueprint", "Iron Chestplate", "Obsidian Frame", "Enchanting Table"],
    "spark": ["Hum: Bone Chime", "Hum: Drumheart", "Hum: Pulse Cell", "Hum: Pulse Resonator"],
    "clock": ["Water Wheel", "Mechanical Press", "Mechanical Mixer", "Encased Fan", "Precision Mechanism"],
    "swarm": ["Ring of Oak", "Beehive", "Advanced Beehive", "Centrifuge", "Incubator", "Imperium"],
    "sigil": ["Braid Cord", "Brewing Stand", "Novice Spell Book", "Occultism Dictionary"],
    "spindle": ["Splice a Braid", "Digital Loom", "Gate Drum", "March Stone"],
}
KNOT_TEXT = {
    "soil": ("Soil Knot", "Wake", ["Bench, sapling, hearth, water, Codex. The pad holds.", "Tension the Strand: the Pad-keepers answer, and the token is yours to seat."]),
    "stone": ("Stone Knot", "Recover", ["Yarn, porcelain, a Loomframe working, iron in the chest.", "Tension the Strand: the Grit-singers answer."]),
    "sprout": ("Sprout Knot", "Root", ["A field, a kitchen, essence rising.", "Tension the Strand: the Rootbinders answer."]),
    "claw": ("Claw Knot", "Edge", ["Plans, iron on your back, a door out.", "Tension the Strand: the Edge-walkers answer. The braid opens."]),
    "spark": ("Spark Knot", "Hum", ["A drum struck, a Pulse held, a resonator burning.", "Tension the Strand: the Drumhearts answer."]),
    "clock": ("Clock Knot", "Pattern", ["A wheel, a press, a mixer, a fan, a clockwork heart.", "Tension the Strand: the Pattern-weavers answer."]),
    "swarm": ("Swarm Knot", "Colony", ["A nest you built, a hive you moved, a centrifuge, an incubator, essence fields.", "Tension the Strand: the Colony-keepers answer."]),
    "sigil": ("Sigil Knot", "Bind", ["A braid spun, potions bottled, spells and spirits called.", "Tension the Strand: the Seal-carvers answer."]),
    "spindle": ("Spindle Knot", "Reweave", ["A braid, a digital loom, a gate, a stone from the March.", "Tension the ninth Strand. Then the Fragment, then the Post."]),
}


def task_quest(strand_i, *, title, desc, task, rewards, deps=None, x=0.0, y=0.0, optional=False, hide=False, shape="", subtitle=None):
    q, t, r = next_ids(strand_i)
    lang[f"quest.{q}.title"] = title
    lang[f"quest.{q}.quest_desc"] = desc
    if subtitle:
        lang[f"quest.{q}.subtitle"] = subtitle
    task = dict(task)
    task["id"] = t
    rw = []
    for i, reward in enumerate(rewards):
        reward = dict(reward)
        reward["id"] = hid(int(r, 16) + i * 0x1000000)
        rw.append(reward)
    entry = {"id": q, "x": f"{round(x, 1)}d", "y": f"{round(y, 1)}d", "tasks": [task], "rewards": rw}
    if deps:
        entry["dependencies"] = deps
    if optional:
        entry["optional"] = True
    if hide:
        entry["hide_until_deps_complete"] = True
    if shape:
        entry["shape"] = shape
    return entry


def reward_item(item, count=1):
    return {"type": "item", "item": {"id": item, "count": count}}


def reward_xp_levels(n):
    return {"type": "xp_levels", "xp_levels": n}


REWARD_TABLE_IDS = {name: hid(0xF100000000000000 + i + 1) for i, name in enumerate(
    ["soil", "stone", "sprout", "claw", "spark", "clock", "swarm", "sigil", "spindle", "reweave"])}


def reward_crate(name):
    """A Steward Cache loot crate — FTB Quests reward table backed by the mod's vanilla loot table."""
    return {"type": "loot", "table_id": REWARD_TABLE_IDS[name]}


def write_reward_tables():
    folder = QUESTS / "reward_tables"
    folder.mkdir(parents=True, exist_ok=True)
    tribes = {"soil": "Pad-keepers", "stone": "Grit-singers", "sprout": "Rootbinders", "claw": "Edge-walkers", "spark": "Drumhearts",
              "clock": "Pattern-weavers", "swarm": "Colony-keepers", "sigil": "Seal-carvers", "spindle": "Loom-stitchers", "reweave": "Nine Tribes"}
    icons = {"soil": "minecraft:oak_sapling", "stone": "voidloom:void_yarn", "sprout": "mysticalagriculture:inferium_essence",
             "claw": "minecraft:iron_ingot", "spark": "minecraft:redstone", "clock": "create:cogwheel", "swarm": "minecraft:honeycomb",
             "sigil": "minecraft:amethyst_shard", "spindle": "ae2:fluix_crystal", "reweave": "ninjacatskies:spindle_loom_fragment"}
    colors = {"soil": 0x6B8E3A, "stone": 0x8A8580, "sprout": 0x5AAF5A, "claw": 0x8C8C96, "spark": 0xD4A84B, "clock": 0xC87A3A,
              "swarm": 0xE6C478, "sigil": 0x8A5FB8, "spindle": 0x3D7A7A, "reweave": 0xE8E0D5}
    for name, tid in REWARD_TABLE_IDS.items():
        body = {
            "id": tid,
            "title": f"Steward Cache: {tribes[name]}",
            "icon": {"id": icons[name]},
            "loot_size": 1,
            "hide_tooltip": False,
            "use_title": True,
            "loot_table_id": f"ninjacatskies:steward_cache/{name}",
            "loot_crate": {
                "string_id": f"steward_{name}",
                "item_name": f"Steward Cache ({tribes[name]})",
                "color": colors[name],
                "glow": True,
                "drops": {"passive": 0, "monster": 0, "boss": 0},
            },
            "rewards": [],
        }
        (folder / f"steward_cache_{name}.snbt").write_text(to_snbt(body) + "\n", encoding="utf-8")


def reward_loot(table):
    """Steward Cache: a vanilla loot table handed over by command (FTB's own 'loot' type wants a RewardTable)."""
    return {"type": "command", "command": f"loot give @p loot {table}", "silent": True, "elevate_perms": True}


def knot_finale(strand_i, token, main, x, y):
    """Checkmark Knot quest (token + cache + levels) and a Seat quest that clears when the Post takes it."""
    title, phase, desc = KNOT_TEXT[token]
    by_title = {lang.get(f"quest.{q['id']}.title"): q["id"] for q in main}
    deps = [by_title[t] for t in KNOT_BEATS[token] if t in by_title]
    if not deps and main:
        deps = [main[-1]["id"]]
    knot = task_quest(
        strand_i,
        title=title,
        subtitle=phase,
        desc=desc,
        task={"type": "checkmark"},
        rewards=[
            reward_item(f"ninjacatskies:strand_token_{token}", 1),
            reward_crate(token),
            reward_xp_levels(3),
        ],
        deps=deps,
        x=x,
        y=y,
        shape="hexagon",
    )
    knot["size"] = "1.5d"
    seat = task_quest(
        strand_i,
        title=f"Seat {token.title()}",
        desc=["Right-click your Clowder's Tension Post with the token.", "The notch lights, the tribe chimes, the pad changes."],
        task={"type": "advancement", "advancement": f"ninjacatskies:strand/{token}", "criterion": ""},
        rewards=[reward_item("ninjacatskies:frayed_thread", 6), reward_item("ninjacatskies:codex_page", 1)],
        deps=[knot["id"]],
        x=x + 1.6,
        y=y,
        shape="diamond",
    )
    return [knot, seat]


SECRETS = {
    1: ("Something Came Up", ["A zombie on a pad with no caves. The void sends its regards.", "Light the edges."], {"type": "kill", "entity": "minecraft:zombie", "value": 1}, [reward_item("minecraft:torch", 16), reward_item("ninjacatskies:codex_page", 1)]),
    2: ("Boom, Later", ["A creeper, dealt with. Gunpowder is worth more than the fright."], {"type": "kill", "entity": "minecraft:creeper", "value": 3}, [reward_item("minecraft:gunpowder", 8), reward_xp_levels(1)]),
    3: ("Wrong Potato", ["Every Rootbinder pulls one eventually.", "Do not eat it. Do not throw it away either."], {"type": "item", "item": {"id": "minecraft:poisonous_potato", "count": 1}}, [reward_item("minecraft:golden_carrot", 4)]),
    4: ("Edge of the Edge", ["Something tall looked back. Edge-walkers called them door-wardens."], {"type": "kill", "entity": "minecraft:enderman", "value": 1}, [reward_item("minecraft:ender_pearl", 2), reward_xp_levels(2)]),
    5: ("Bottled Trouble", ["A witch, on your pad, at night. The drums did not warn you."], {"type": "kill", "entity": "minecraft:witch", "value": 1}, [reward_item("minecraft:glowstone_dust", 8), reward_item("minecraft:redstone", 16)]),
    6: ("Rattle in the Gears", ["Twenty skeletons. The pattern holds if you keep the lights on."], {"type": "kill", "entity": "minecraft:skeleton", "value": 20}, [reward_item("minecraft:bone_block", 8), reward_xp_levels(2)]),
    7: ("Regret", ["You killed a bee.", "The Colony-keepers would like a word. Here is a bottle; think about it."], {"type": "kill", "entity": "minecraft:bee", "value": 1}, [reward_item("minecraft:honey_bottle", 1)]),
    8: ("Old Gold", ["An apple the stewards never ate. Neither should you, probably."], {"type": "item", "item": {"id": "minecraft:enchanted_golden_apple", "count": 1}}, [reward_xp_levels(5), reward_item("ninjacatskies:codex_page", 1)]),
    9: ("A Star, Somehow", ["A wither, on a pad, in the sky. The Loom-stitchers would have been impressed and then furious."], {"type": "item", "item": {"id": "minecraft:nether_star", "count": 1}}, [reward_xp_levels(10), reward_item("ninjacatskies:frayed_thread", 24)]),
}

CHAPTER_SUBTITLES = {
    1: ["Wake — survive, claim the pad, let the Codex wake."],
    2: ["Recover — pull the fallen world back into matter."],
    3: ["Root — grow anchors so the pad stops fraying."],
    4: ["Edge — kit up and leave the pad on purpose."],
    5: ["Hum — rhythm and pulse before wires."],
    6: ["Pattern — a factory as a song that carries itself."],
    7: ["Colony — keep something alive that keeps something else alive."],
    8: ["Bind — seals, rites, and two braid paths in a cord."],
    9: ["Reweave — the digital loom, the March, the Fragment."],
    15: ["Teams, the Hall, the Post, and the Fray."],
    16: ["Spend Thread. No dependencies, no order."],
    25: ["Every nest is a ring of something around a flower."],
}


def secret_quest(strand_i, x, y):
    if strand_i not in SECRETS:
        return []
    title, desc, task, rewards = SECRETS[strand_i]
    q = task_quest(strand_i, title=title, desc=desc, task=task, rewards=rewards, x=x, y=y, shape="octagon")
    q["invisible"] = True
    q["invisible_until_tasks"] = 1
    return [q]


def apply_voice(desc):
    out = []
    for line in desc:
        line = VOICE_FIX.get(line, line)
        out.append(line)
    return out


def finalize_chapter(strand_i, quests):
    """Hide side grids until the second mainline beat; strip Desk dependencies; unique titles."""
    CURRENT["strand_i"] = strand_i
    mainline = [q for q in quests if not q.get("optional")]
    gate = mainline[1]["id"] if len(mainline) > 1 else None
    for q in quests:
        if q.get("optional") and not q.get("dependencies") and gate and strand_i != 16:
            q["dependencies"] = [gate]
            q["hide_until_deps_complete"] = True
        if strand_i == 16:
            q.pop("dependencies", None)
        title_key = f"quest.{q['id']}.title"
        title = lang.get(title_key)
        if title:
            n = CURRENT["title_counts"].get(title, 0)
            CURRENT["title_counts"][title] = n + 1
            if n > 0:
                lang[title_key] = f"{title} ({CHAPTER_SHORT.get(strand_i, strand_i)})"
        dk = f"quest.{q['id']}.quest_desc"
        if dk in lang:
            lang[dk] = apply_voice(lang[dk])
    return quests

def chain(strand_i: int, steps: list[tuple], start_x: float = 0.0, y: float = 0.0, gap: float = 1.4) -> list[dict]:
    """steps: (title, item, count, desc[, reward_item, reward_count, optional, consume])

    Laid out as clusters of five: a head beat, then four beats under it that depend on the head.
    Each head depends on the previous head, so a chapter reads as a lattice, not a 35-deep railroad.
    Thread rewards scale with the chapter band; heads also give a level.
    """
    out: list[dict] = []
    prev_head: str | None = None
    head: str | None = None
    cluster = 0
    member = 0
    band = 0 if strand_i <= 3 else 1 if strand_i <= 6 else 2 if strand_i <= 9 else 1
    for step in steps:
        title, item, count, desc = step[0], step[1], step[2], step[3]
        reward_item_ = step[4] if len(step) > 4 else None
        reward_count = step[5] if len(step) > 5 else (1 + band if member else 2 + band)
        optional = step[6] if len(step) > 6 else False
        consume = step[7] if len(step) > 7 else False
        x = start_x + cluster * 1.8
        yy = y + member * 1.3
        deps = None
        if member == 0:
            deps = [prev_head] if prev_head else None
        else:
            deps = [head] if head else None
        q = item_quest(
            strand_i,
            title=title,
            desc=[desc] if isinstance(desc, str) else desc,
            item=item,
            count=count,
            reward_item=reward_item_,
            reward_count=reward_count,
            deps=deps,
            x=x,
            y=yy,
            optional=optional,
            consume=consume,
        )
        if not q:
            continue
        out.append(q)
        if q.get("optional"):
            # Optional beats never carry the lattice.
            if member == 0:
                q["dependencies"] = [prev_head] if prev_head else []
                if not q["dependencies"]:
                    q.pop("dependencies")
                continue
        if member == 0 and not q.get("optional"):
            head = q["id"]
            if not q.get("optional"):
                q.setdefault("rewards", []).append({"id": hid(int(q["id"], 16) + 0x0F00000000000000), "type": "xp_levels", "xp_levels": 1})
        member += 1
        if member >= 5:
            prev_head = head
            member = 0
            cluster += 1
    return out


def grid_optional(strand_i: int, steps: list[tuple], origin=(0.0, 7.5), cols=6) -> list[dict]:
    """steps: (title, item, count, desc[, reward_item, reward_count, consume])"""
    out = []
    for i, step in enumerate(steps):
        title, item, count, desc = step[0], step[1], step[2], step[3]
        reward_item = step[4] if len(step) > 4 else None
        reward_count = step[5] if len(step) > 5 else 1
        consume = step[6] if len(step) > 6 else False
        ox, oy = origin
        x = ox + (i % cols) * 1.5
        y = oy + (i // cols) * 1.5
        q = item_quest(
            strand_i,
            title=title,
            desc=[desc],
            item=item,
            count=count,
            reward_item=reward_item,
            reward_count=reward_count,
            x=x,
            y=y,
            optional=True,
            consume=consume,
        )
        if q:
            out.append(q)
    return out


def token_finale(strand_i: int, token: str, prev: str | None, x: float, y: float) -> list[dict]:
    item = f"ninjacatskies:strand_token_{token}"
    q = item_quest(
        strand_i,
        title=f"Strand Token: {token.title()}",
        desc=["Another Strand tensioned."],
        item=item,
        reward_item=item,
        deps=[prev] if prev else None,
        x=x,
        y=y,
    )
    return [q] if q else []


def last_id(quests: list[dict]) -> str | None:
    return quests[-1]["id"] if quests else None


def build_soil() -> list[dict]:
    s = 1
    main = chain(s, [
        ("Wake on a Pad", "minecraft:oak_log", 8, "Skybound. Gather wood."),
        ("Something to Stand On", "minecraft:dirt", 16, "Dirt is a promise."),
        ("Craft a Bench", "minecraft:crafting_table", 1, "Hands need a surface."),
        ("Wooden Pick", "minecraft:wooden_pickaxe", 1, "Claw comes later."),
        ("First Sapling", "minecraft:oak_sapling", 1, "Green against the drop."),
        ("Plank Stock", "minecraft:oak_planks", 64, "Expand the pad."),
        ("Stick Bundle", "minecraft:stick", 32, "Handles and frames."),
        ("Chest for the Clowder", "minecraft:chest", 1, "Put things where they stay."),
        ("Torch Line", "minecraft:torch", 16, "See the edge."),
        ("Cobble Cache", "minecraft:cobblestone", 32, "Ice+lava gen, or sieve grit in Stone. Hard pad chest has ice+lava."),
        ("Furnace Heat", "minecraft:furnace", 1, "Warmth that is not yet Spark."),
        ("Cook a Meal", "minecraft:bread", 8, "Hunger is a soft void."),
        ("Catch the Rain", "minecraft:water_bucket", 1, "Place lava, melt ice into a source, fill empty bucket. Easy ships water; Normal/Hard ship ice+lava+empty bucket."),
        ("Frayed Currency", "ninjacatskies:frayed_thread", 8, "Hub shop seed money."),
        ("Codex in Hand", "ninjacatskies:whisker_codex", 1, "It still assigns work."),
    ])
    side = grid_optional(s, [
        ("Bed Claim", "minecraft:white_bed", 1, "Set a spawn."),
        ("Ladder Down", "minecraft:ladder", 16, "Build below."),
        ("String Cache", "minecraft:string", 16, "Meshes wait."),
        ("Bone Meal Stock", "minecraft:bone_meal", 16, "Speed the green."),
        ("Dirt Platform", "minecraft:dirt", 64, "Widen the pad."),
        ("Oak Leaves", "minecraft:oak_leaves", 32, "Compost later."),
        ("Flower Pot", "minecraft:flower_pot", 1, "A quiet corner."),
        ("Barrel", "minecraft:barrel", 1, "More storage."),
        ("Composter", "minecraft:composter", 1, "Waste to meal."),
        ("Wooden Hoe", "minecraft:wooden_hoe", 1, "Scratch a row."),
        ("Wooden Axe", "minecraft:wooden_axe", 1, "Faster logs."),
        ("Wooden Shovel", "minecraft:wooden_shovel", 1, "Move dirt."),
        ("Wooden Sword", "minecraft:wooden_sword", 1, "Soft defense."),
        ("Bowl", "minecraft:bowl", 4, "Soup later."),
        ("Item Frame", "minecraft:item_frame", 4, "Label the pad."),
        ("Painting", "minecraft:painting", 1, "Make it home."),
        ("Oak Door", "minecraft:oak_door", 1, "A threshold."),
        ("Oak Fence", "minecraft:oak_fence", 16, "Edge rails."),
        ("Oak Stairs", "minecraft:oak_stairs", 16, "Steps up."),
        ("Oak Slab", "minecraft:oak_slab", 32, "Half measures."),
        ("Oak Trapdoor", "minecraft:oak_trapdoor", 4, "Trapdoor access hatches."),
        ("Oak Pressure Plate", "minecraft:oak_pressure_plate", 2, "Step click."),
        ("Oak Button", "minecraft:oak_button", 4, "Button for redstone taps."),
        ("Stick Fence Gate", "minecraft:oak_fence_gate", 2, "Fence the pad edge."),
        ("Campfire", "minecraft:campfire", 1, "Smoke signal."),
        ("Lantern", "minecraft:lantern", 4, "Hanging light."),
        ("Soul Lantern", "minecraft:soul_lantern", 2, "Blue light."),
        ("Scaffolding", "minecraft:scaffolding", 32, "Build high."),
        ("Chain", "minecraft:chain", 8, "Chain for hanging flair."),
        ("Iron Bars", "minecraft:iron_bars", 16, "Cage the edge."),
        ("Glass Pane", "minecraft:glass_pane", 16, "Glass for pad windows."),
        ("White Wool", "minecraft:white_wool", 8, "Soft block."),
        ("White Carpet", "minecraft:white_carpet", 8, "Soft floor."),
        ("Flowering Azalea", "minecraft:flowering_azalea", 2, "Pretty green."),
        ("Moss Block", "minecraft:moss_block", 8, "Soft stone."),
        ("Hanging Roots", "minecraft:hanging_roots", 4, "Hanging roots under the pad."),
        ("Glow Lichen", "minecraft:glow_lichen", 8, "Wall light."),
        ("Pointed Dripstone", "minecraft:pointed_dripstone", 4, "Dripstone for pointed flair."),
        ("Amethyst Block", "minecraft:amethyst_block", 4, "Amethyst block for Sigil bait."),
        ("Copper Block", "minecraft:copper_block", 2, "Heavy copper."),
        ("Raw Iron Block", "minecraft:raw_iron_block", 1, "Ore pile."),
        ("Coal Block", "minecraft:coal_block", 4, "Fuel brick."),
        ("Hay Block", "minecraft:hay_block", 4, "Feed stock."),
        ("Dried Kelp Block", "minecraft:dried_kelp_block", 4, "Sea brick."),
        ("Book", "minecraft:book", 4, "Write later."),
        ("Paper", "minecraft:paper", 16, "Paper for books and maps."),
        ("Ink Sac", "minecraft:ink_sac", 8, "Dye and books need ink."),
        ("Feather", "minecraft:feather", 8, "Feathers for arrows and books."),
        ("Leather", "minecraft:leather", 8, "Leather for books and kits."),
    ], origin=(-3.0, 7.5), cols=6)
    finale = knot_finale(s, "soil", main, 11.5, -2.0)
    return main + side + finale


def build_stone() -> list[dict]:
    s = 2
    # Recover: Voidloom identity first; sieve tools mid-chain before knot/loomframe softlock.
    # Early yarn = unravel Thread → string, then 4 string → 2 yarn; slime = dirt + seeds + bone meal.
    main = chain(s, [
        ("Pull Void Yarn", "voidloom:void_yarn", 4, "Unravel Thread → 3 string; craft 4 string → 2 yarn. Later: 2 string + pearl/chorus → 2 yarn."),
        ("Spindle Hammer", "voidloom:spindle_hammer", 1, "Stone-tier — cobble + sticks. Break fallen grit."),
        ("Thread the Mesh", "voidloom:thread_mesh_string", 1, "Catch grit in thread."),
        ("Tension Barrel", "voidloom:tension_barrel", 1, "Water+dirt → clay (empty bucket returns to you). String+pearl → yarn."),
        ("Clay Pocket", "minecraft:clay_ball", 16, "From the Tension Barrel — needed before porcelain."),
        ("Porcelain Clay", "exdeorum:porcelain_clay_ball", 8, "Clay + bone meal — shape the unfired bucket."),
        ("Porcelain Tool", "exdeorum:porcelain_bucket", 1, "Smelt the unfired porcelain bucket — hold the melt."),
        ("Sift Fallen Grit", "exdeorum:oak_sieve", 1, "Sieve is a tool, not the title."),
        ("Wooden Hammer", "exdeorum:wooden_hammer", 1, "Spare hits on grit."),
        ("Pebbles", "minecraft:cobblestone", 64, "Matter from grit."),
        ("Gravel Path", "minecraft:gravel", 32, "Loom dust waiting in gravel."),
        ("Sand Cache", "minecraft:sand", 32, "Fine grit; glass later."),
        ("Dust Pile", "exdeorum:dust", 16, "Ash of the fallen world."),
        ("Tie Binding Knot", "voidloom:binding_knot", 2, "Yarn + slime — pad compost works early."),
        ("Raise Loomframe", "voidloom:loomframe", 1, "Mark Recover on the pad."),
        ("Iron Ore Chunk", "exdeorum:iron_ore_chunk", 8, "Metal bits from grit."),
        ("Copper Ore Chunk", "exdeorum:copper_ore_chunk", 8, "Conductive thoughts."),
        ("Gold Ore Chunk", "exdeorum:gold_ore_chunk", 4, "Soft gleam."),
        ("Coal", "minecraft:coal", 32, "Fuel the line."),
        ("Raw Iron", "minecraft:raw_iron", 16, "Smelt onward."),
        ("Iron Ingot", "minecraft:iron_ingot", 16, "Recover pays out."),
        ("Copper Ingot", "minecraft:copper_ingot", 16, "Wire and bulbs."),
        ("Gold Ingot", "minecraft:gold_ingot", 8, "Gilded tools."),
        ("Flint Mesh", "voidloom:thread_mesh_flint", 1, "Sharper catch for grit."),
        ("Iron Mesh", "voidloom:thread_mesh_iron", 1, "Metal thread for heavier dust."),
        ("Crucible", "exdeorum:oak_crucible", 1, "Melt and drip."),
        ("Barrel", "exdeorum:oak_barrel", 1, "Transform fluids."),
        ("Stone Hammer", "exdeorum:stone_hammer", 1, "Harder hits."),
        ("Iron Hammer", "exdeorum:iron_hammer", 1, "Serious grit."),
        ("Compressed Sieve", "exdeorum:oak_compressed_sieve", 1, "Wider Recover mesh."),
        ("Glass", "minecraft:glass", 16, "See through."),
        ("Bucket", "minecraft:bucket", 1, "Carry the rain."),
        ("Lava Bucket", "minecraft:lava_bucket", 1, "Heat from the void."),
        ("Obsidian", "minecraft:obsidian", 4, "Portal thoughts."),
        ("Diamond", "minecraft:diamond", 2, "Rare grit luck."),
    ])
    side = grid_optional(s, [
        ("Flint", "minecraft:flint", 16, "Mesh upgrade fuel."),
        ("Gunpowder", "minecraft:gunpowder", 8, "Boom later."),
        ("Redstone", "minecraft:redstone", 16, "Spark Strand bait."),
        ("Lapis", "minecraft:lapis_lazuli", 16, "Enchant fuel."),
        ("Andesite", "minecraft:andesite", 32, "Create later."),
        ("Diorite", "minecraft:diorite", 16, "Stone variety."),
        ("Granite", "minecraft:granite", 16, "Stone variety."),
        ("Netherrack", "minecraft:netherrack", 16, "Hell grit."),
        ("Soul Sand", "minecraft:soul_sand", 8, "Slow feet."),
        ("Glowstone Dust", "minecraft:glowstone_dust", 8, "Soft light."),
        ("Crook", "voidloom:spindle_crook", 1, "Leaf work."),
        ("String", "minecraft:string", 32, "More meshes."),
        ("Slimeball", "minecraft:slime_ball", 4, "Knot binder — or pad compost recipe."),
        ("Bone", "minecraft:bone", 16, "Meal stock."),
        ("Spider Eye", "minecraft:spider_eye", 4, "Brew later."),
    ], origin=(-4.0, 7.5), cols=6)
    finale = knot_finale(s, "stone", main, 12.0, -2.0)
    return main + side + finale


def build_sprout() -> list[dict]:
    s = 3
    main = chain(s, [
        ("Iron Hoe", "minecraft:iron_hoe", 1, "Green against the drop."),
        ("Wheat Field", "minecraft:wheat", 32, "Bread is infrastructure."),
        ("Seed Pouch", "minecraft:wheat_seeds", 32, "Plant what you eat."),
        ("Bone Meal Engine", "minecraft:bone_meal", 32, "Speed is kindness."),
        ("Farmers Knife", "farmersdelight:flint_knife", 1, "Prep the harvest."),
        ("Cutting Board", "farmersdelight:cutting_board", 1, "Kitchen start."),
        ("Cooking Pot", "farmersdelight:cooking_pot", 1, "Warm meals."),
        ("Cabbage", "farmersdelight:cabbage", 8, "Crisp leaves."),
        ("Tomato", "farmersdelight:tomato", 8, "Red fruit."),
        ("Onion", "farmersdelight:onion", 8, "Tears of joy."),
        ("Inferium", "mysticalagriculture:inferium_essence", 16, "Essence farming begins."),
        ("Prosperity", "mysticalagriculture:prosperity_shard", 8, "Seed backbone."),
        ("Infusion Altar", "mysticalagriculture:infusion_altar", 1, "Raise seeds."),
        ("Infusion Pedestal", "mysticalagriculture:infusion_pedestal", 4, "Circle the altar."),
        ("Dirt Seeds", "mysticalagriculture:dirt_seeds", 1, "Grow more pad."),
        ("Wood Seeds", "mysticalagriculture:wood_seeds", 1, "Grow canopy."),
        ("Stone Seeds", "mysticalagriculture:stone_seeds", 1, "Grow grit."),
        ("Iron Seeds", "mysticalagriculture:iron_seeds", 1, "Metal from leaves."),
        ("Copper Seeds", "mysticalagriculture:copper_seeds", 1, "Copper leaves."),
        ("Gold Seeds", "mysticalagriculture:gold_seeds", 1, "Gilded leaves."),
        ("Coal Seeds", "mysticalagriculture:coal_seeds", 1, "Fuel farm."),
        ("Water Seeds", "mysticalagriculture:water_seeds", 1, "Bottled rain."),
        ("Botany Pot", "botanypots:terracotta_botany_pot", 1, "Compact growth."),
        ("Hopper Pot", "botanypots:terracotta_hopper_botany_pot", 1, "Auto harvest pot."),
        ("Prudentium", "mysticalagriculture:prudentium_essence", 16, "Tier up a machine line."),
        ("Tertium", "mysticalagriculture:tertium_essence", 8, "Deeper green."),
        ("Bone Block", "minecraft:bone_block", 4, "Nine meal to a block."),
        ("Hay Silo", "minecraft:hay_block", 8, "Sprout surplus."),
        ("Rich Soil", "farmersdelight:rich_soil", 8, "Better farmland."),
        ("Organic Compost", "farmersdelight:organic_compost", 8, "Feed the soil."),
    ])
    side = grid_optional(s, [
        ("Carrot", "minecraft:carrot", 16, "Orange rows."),
        ("Potato", "minecraft:potato", 16, "Potato staple crop."),
        ("Beetroot", "minecraft:beetroot", 16, "Red roots."),
        ("Melon", "minecraft:melon_slice", 16, "Melon for food and trades."),
        ("Pumpkin", "minecraft:pumpkin", 8, "Pumpkin for food and decor."),
        ("Sugar Cane", "minecraft:sugar_cane", 16, "Paper and sugar."),
        ("Cactus", "minecraft:cactus", 8, "Green spikes."),
        ("Bamboo", "minecraft:bamboo", 16, "Fast poles."),
        ("Sweet Berries", "minecraft:sweet_berries", 16, "Berries while you build."),
        ("Cocoa", "minecraft:cocoa_beans", 8, "Brown gold."),
        ("Apple", "minecraft:apple", 8, "From leaves."),
        ("Mushroom Stew", "minecraft:mushroom_stew", 4, "Cave comfort."),
        ("Honey Bottle", "minecraft:honey_bottle", 4, "Swarm preview."),
        ("Glow Berries", "minecraft:glow_berries", 8, "Lit snacks."),
        ("Nether Wart", "minecraft:nether_wart", 8, "Brew base."),
    ], origin=(-4.0, 7.5), cols=6)
    finale = knot_finale(s, "sprout", main, 12.0, -2.0)
    return main + side + finale


def build_claw() -> list[dict]:
    s = 4
    main = chain(s, [
        ("Blueprint Paper", "silentgear:blueprint_paper", 8, "Cut the void on your terms."),
        ("Blueprint Package", "silentgear:blueprint_package", 1, "Plans in a box."),
        ("Rod Blueprint", "silentgear:rod_blueprint", 1, "Tool bones."),
        ("Pick Blueprint", "silentgear:pickaxe_blueprint", 1, "Shape a pick."),
        ("Axe Blueprint", "silentgear:axe_blueprint", 1, "Shape an axe."),
        ("Shovel Blueprint", "silentgear:shovel_blueprint", 1, "Shape a shovel."),
        ("Sword Blueprint", "silentgear:sword_blueprint", 1, "Shape a blade."),
        ("Upgrade Base", "silentgear:upgrade_base", 4, "Room to grow."),
        ("Iron Mass", "minecraft:iron_ingot", 32, "Material for parts."),
        ("Diamond Tip", "minecraft:diamond", 6, "Claw sharpens."),
        ("Shears", "minecraft:shears", 1, "Leaves and wool."),
        ("Shield", "minecraft:shield", 1, "Pads have edges."),
        ("Iron Chestplate", "minecraft:iron_chestplate", 1, "Survive the night."),
        ("Iron Helmet", "minecraft:iron_helmet", 1, "Mind the drop."),
        ("Iron Leggings", "minecraft:iron_leggings", 1, "Steady legs."),
        ("Iron Boots", "minecraft:iron_boots", 1, "Sure footing."),
        ("Bow", "minecraft:bow", 1, "Bow keeps void mobs away."),
        ("Arrow Bundle", "minecraft:arrow", 64, "Keep distance."),
        ("Flint and Steel", "minecraft:flint_and_steel", 1, "Light the way."),
        ("Obsidian Frame", "minecraft:obsidian", 10, "Portal frame."),
        ("Ender Eye", "minecraft:ender_eye", 1, "Foothold prep."),
        ("Enchanting Table", "minecraft:enchanting_table", 1, "Soft power."),
        ("Anvil", "minecraft:anvil", 1, "Repair and name."),
        ("Name Tag", "minecraft:name_tag", 1, "Call it yours."),
    ])
    side = grid_optional(s, [
        ("Hoe Blueprint", "silentgear:hoe_blueprint", 1, "Farm claw."),
        ("Sickle Blueprint", "silentgear:sickle_blueprint", 1, "Wide harvest."),
        ("Paxel Blueprint", "silentgear:paxel_blueprint", 1, "All tools."),
        ("Hammer Blueprint", "silentgear:hammer_blueprint", 1, "3x3 thoughts."),
        ("Excavator Blueprint", "silentgear:excavator_blueprint", 1, "Dig wide."),
        ("Knife Blueprint", "silentgear:knife_blueprint", 1, "Fine cuts."),
        ("Gold Armor Bits", "minecraft:golden_chestplate", 1, "Soft plate."),
        ("Turtle Helm", "minecraft:turtle_helmet", 1, "Water breath."),
        ("Wolf Armor", "minecraft:wolf_armor", 1, "If found — optional."),
        ("Trident", "minecraft:trident", 1, "Sea claw."),
        ("Crossbow", "minecraft:crossbow", 1, "Heavy shot."),
        ("Spyglass", "minecraft:spyglass", 1, "Scan the void."),
    ], origin=(-4.0, 7.5), cols=6)
    # drop invalid optional if any
    finale = knot_finale(s, "claw", main, 12.0, -2.0)
    return main + side + finale


def build_spark() -> list[dict]:
    s = 5
    # Hum: brief redstone, then Tribal jar recipe order (Chime→Shard→Resonator→Drumheart→…),
    # then Powah/FE as bridges (Mek stays its own side chapter).
    main = chain(s, [
        ("Redstone Dust", "minecraft:redstone", 64, "Warmth that is not a campfire — brief signal before the Hum."),
        ("Furnace Array", "minecraft:furnace", 8, "Parallel heat."),
        ("Hopper Line", "minecraft:hopper", 16, "Move the grit."),
        ("Comparator", "minecraft:comparator", 4, "Measure the beat."),
        ("Hum: Bone Chime", "tribalpower:bone_chime", 1, "First beat — bone, string, amethyst. Opens the Hum."),
        ("Hum: Spirit Shard", "tribalpower:spirit_shard", 2, "Shard needs a Chime — keep rattling."),
        ("Hum: Copper Resonator", "tribalpower:copper_resonator", 1, "Copper around a Chime — tunes metal to spirit."),
        ("Hum: Drumheart", "tribalpower:drumheart", 1, "Strike the heart. Store Spirit Pulse — needs Chime + Shard."),
        ("Hum: Pulse Cell", "tribalpower:pulse_cell", 1, "Carry Pulse — needs Resonator + Shard."),
        ("Hum: Ley Collector", "tribalpower:ley_collector", 1, "Draw ley into beats — Resonator + Shard + copper."),
        ("Hum: Pulse Resonator", "tribalpower:pulse_resonator", 1, "Burn coal for denser beats beside Drumheart and Ley."),
        # FE bridges — secondary to Tribal Pulse identity
        ("Powah Starter Cell", "powah:energy_cell_starter", 1, "FE bridge buffer — not the Hum religion."),
        ("Powah Furnator", "powah:furnator_starter", 1, "Burn for FE."),
        ("Powah Cable", "powah:energy_cable_starter", 8, "Move Forge Energy along."),
        ("Solar Panel Starter", "powah:solar_panel_starter", 2, "Sky power bridge."),
        ("Thermo Generator", "powah:thermo_generator_starter", 1, "Heat differential."),
        ("Energizing Orb", "powah:energizing_orb", 1, "Charge items."),
        ("Energizing Rod", "powah:energizing_rod_starter", 1, "Feed the orb."),
        ("Battery", "powah:battery_starter", 1, "Pocket FE."),
        ("Wrench", "powah:wrench", 1, "Rotate machines."),
    ])
    side = grid_optional(s, [
        ("Blast Furnace", "minecraft:blast_furnace", 2, "Faster metals."),
        ("Smoker", "minecraft:smoker", 2, "Faster food."),
        ("Coal Block", "minecraft:coal_block", 16, "Dense fuel."),
        ("Dropper", "minecraft:dropper", 4, "Push items."),
        ("Dispenser", "minecraft:dispenser", 4, "Push with purpose."),
        ("Piston", "minecraft:piston", 8, "Push blocks."),
        ("Sticky Piston", "minecraft:sticky_piston", 4, "Pull back."),
        ("Observer", "minecraft:observer", 4, "Observer reads the beat."),
        ("Repeater", "minecraft:repeater", 8, "Repeater times the circuit."),
        ("Target", "minecraft:target", 2, "Signal catch."),
        ("Lightning Rod", "minecraft:lightning_rod", 1, "Sky notice."),
        ("Clock", "minecraft:clock", 1, "Time for power."),
        ("Copper Bulb", "minecraft:copper_bulb", 8, "Light without torches."),
        ("Redstone Lamp", "minecraft:redstone_lamp", 8, "Soft glow."),
        ("Daylight Detector", "minecraft:daylight_detector", 2, "Sun switch."),
        ("Lever", "minecraft:lever", 8, "Manual bit."),
        ("Button", "minecraft:stone_button", 8, "Button taps a redstone pulse."),
        ("Pressure Plate", "minecraft:stone_pressure_plate", 4, "Step signal."),
        ("Tripwire Hook", "minecraft:tripwire_hook", 4, "Wire trap."),
        ("Note Block", "minecraft:note_block", 1, "Audible bit."),
        ("Jukebox", "minecraft:jukebox", 1, "Jukebox for pad morale."),
        ("Minecart", "minecraft:minecart", 1, "Rail thoughts."),
        ("Rail", "minecraft:rail", 32, "Rails across the void span."),
        ("Powered Rail", "minecraft:powered_rail", 8, "Powered rail for carts."),
        ("Detector Rail", "minecraft:detector_rail", 4, "Sense cart."),
        ("Solar Flux Cell", "solarflux:photovoltaic_cell_1", 1, "Alt solar craft."),
        ("Pipez Item", "pipez:item_pipe", 16, "Simple item pipes."),
        ("Pipez Fluid", "pipez:fluid_pipe", 8, "Simple fluid pipes."),
        ("Pipez Energy", "pipez:energy_pipe", 8, "Simple FE pipes."),
        ("Pipez Wrench", "pipez:wrench", 1, "Configure pipes."),
        ("Ritual Chalk", "tribalpower:ritual_chalk", 4, "Mark lattice lines — needs a Spirit Shard."),
    ], origin=(-4.0, 7.5), cols=6)
    finale = knot_finale(s, "spark", main, 12.0, -2.0)
    return main + side + finale


def build_clock() -> list[dict]:
    s = 6
    main = chain(s, [
        ("Andesite Alloy", "create:andesite_alloy", 32, "Hands that work while you sleep."),
        ("Shaft", "create:shaft", 16, "Create shaft — rotation spine."),
        ("Cogwheel", "create:cogwheel", 16, "Cogwheel bites the shaft."),
        ("Large Cog", "create:large_cogwheel", 8, "More teeth."),
        ("Andesite Casing", "create:andesite_casing", 16, "Andesite casing frames Create."),
        ("Water Wheel", "create:water_wheel", 1, "River in the sky."),
        ("Hand Crank", "create:hand_crank", 1, "Manual spin."),
        ("Millstone", "create:millstone", 1, "Mill or crush bulk materials."),
        ("Basin", "create:basin", 1, "Basin holds Create mixing."),
        ("Mechanical Press", "create:mechanical_press", 1, "Press plates and paths."),
        ("Mechanical Mixer", "create:mechanical_mixer", 1, "Mix bulk recipes fast."),
        ("Depot", "create:depot", 4, "Park items."),
        ("Belt Connector", "create:belt_connector", 8, "Belts move items along shafts."),
        ("Chute", "create:chute", 8, "Drop down."),
        ("Encased Fan", "create:encased_fan", 2, "Fan for washing and drying."),
        ("Deployer", "create:deployer", 1, "Place and use items by shaft."),
        ("Mechanical Saw", "create:mechanical_saw", 1, "Cut logs."),
        ("Mechanical Drill", "create:mechanical_drill", 1, "Drill through grit blocks."),
        ("Mechanical Harvester", "create:mechanical_harvester", 1, "Cut crops in a spinning arc."),
        ("Portable Storage Interface", "create:portable_storage_interface", 1, "Train thoughts."),
        ("Item Vault", "create:item_vault", 1, "Bulk store."),
        ("Fluid Tank", "create:fluid_tank", 2, "Hold liquids."),
        ("Spout", "create:spout", 1, "Spout fluids into basins."),
        ("Hose Pulley", "create:hose_pulley", 1, "Pump fluids from a source."),
        ("Copper Casing", "create:copper_casing", 8, "Fluid age."),
        ("Brass Casing", "create:brass_casing", 8, "Precision age."),
        ("Precision Mechanism", "create:precision_mechanism", 2, "Clockwork heart."),
        ("Rotation Speed Controller", "create:rotation_speed_controller", 1, "Control rotation speed."),
        ("Gearbox", "create:gearbox", 2, "Turn the corner."),
        ("Clutch", "create:clutch", 1, "Clutch stops a shaft line."),
        ("Gearshift", "create:gearshift", 1, "Gearshift flips rotation."),
        ("Sequenced Gearshift", "create:sequenced_gearshift", 1, "Programmed spin."),
    ])
    side = grid_optional(s, [
        ("Whisk", "create:whisk", 1, "Mixer tool."),
        ("Propeller", "create:propeller", 1, "Fan blade."),
        ("White Sail", "create:white_sail", 4, "Wind mill."),
        ("Windmill Bearing", "create:windmill_bearing", 1, "Catch sky."),
        ("Mechanical Bearing", "create:mechanical_bearing", 1, "Rotate structures."),
        ("Gantry Carriage", "create:gantry_carriage", 1, "Gantry slides along a rail."),
        ("Cart Assembler", "create:cart_assembler", 1, "Contraption cart."),
        ("Minecart Coupling", "create:minecart_coupling", 1, "Link carts."),
        ("Track", "create:track", 32, "Train path."),
        ("Train Door", "create:train_door", 1, "Train door for carriages."),
        ("Schedule", "create:schedule", 1, "Schedule train routes."),
        ("Display Link", "create:display_link", 1, "Show data."),
        ("Display Board", "create:display_board", 1, "Display board shows data."),
        ("Potato Cannon", "create:potato_cannon", 1, "Optional fun."),
        ("Extendo Grip", "create:extendo_grip", 1, "Long arm."),
    ], origin=(-4.0, 7.5), cols=6)
    finale = knot_finale(s, "clock", main, 12.0, -2.0)
    return main + side + finale


def build_swarm() -> list[dict]:
    s = 7
    # Colony: you cannot find a bee in the void, so you make somewhere a bee wants to be.
    wings = task_quest(
        s, title="First Wings", subtitle="Colony",
        desc=["Place the oak nest on the pad and wait. Something with wings will come out of the wood.", "Look at it. That counts."],
        task={"type": "observation", "observe_type": 5, "timer": 0, "to_observe": "minecraft:bee"},
        rewards=[reward_item("minecraft:shears", 1), reward_item("ninjacatskies:frayed_thread", 4), reward_xp_levels(1)],
        x=1.8, y=-1.4, shape="diamond",
    )
    main = chain(s, [
        ("Ring of Oak", "productivebees:oak_wood_nest", 1, "Eight oak logs around a small flower. Place it; the wood remembers wings."),
        ("A Flower to Argue Over", "minecraft:dandelion", 8, "Bone meal on grass. Bees will not stay where nothing blooms."),
        ("Bee Nest", "minecraft:bee_nest", 1, "Planks and flowers — a home a wild bee will move into."),
        ("Honeycomb", "minecraft:honeycomb", 16, "Shears on a full nest. Stand behind a campfire's smoke and nobody gets stung."),
        ("Beehive", "minecraft:beehive", 1, "Three comb and planks. Now the colony is yours to move."),
        ("Honey Bottle", "minecraft:honey_bottle", 8, "Bottle from a full hive. Sweet, and the first thing bees make that money cannot."),
        ("Honey Treat", "productivebees:honey_treat", 8, "Honey and sugar: bee candy. Feed a bee to nudge breeding."),
        ("Ring of Grit", "productivebees:gravel_nest", 1, "Gravel around a flower. Mining bees and diggers like the dust."),
        ("Ring of Coarse Dirt", "productivebees:coarse_dirt_nest", 1, "Coarse dirt around a flower. Leafcutters and ashy miners."),
        ("Ring of Stone", "productivebees:stone_nest", 1, "Stone around a flower. Mason bees, and diggers that eat rock."),
        ("Advanced Beehive", "productivebees:advanced_oak_beehive", 1, "A productive home: bees inside, combs out the front."),
        ("Expansion Box", "productivebees:expansion_box_oak", 1, "Room for three more. Colonies like company."),
        ("Bottler", "productivebees:bottler", 1, "Bottles the yield without a hand on it."),
        ("Centrifuge", "productivebees:centrifuge", 1, "Spins combs into everything they hide."),
        ("Powered Centrifuge", "productivebees:powered_centrifuge", 1, "The same, faster, on power."),
        ("Catcher", "productivebees:catcher", 1, "Scoops wandering bees so the swarm stays on the pad."),
        ("Bee Cage", "productivebees:bee_cage", 4, "Carry a bee like a lantern."),
        ("Incubator", "productivebees:incubator", 1, "Hatch the genes you want."),
        ("Breeding Chamber", "productivebees:breeding_chamber", 1, "Pair two colonies on purpose."),
        ("Gene Indexer", "productivebees:gene_indexer", 1, "Sort traits like seed."),
        ("Feed Upgrade", "productivebees:honey_treat", 16, "A stack of treats: the colony's payroll."),
        ("Diamond Seeds", "mysticalagriculture:diamond_seeds", 1, "Deep crops: the other half of Colony."),
        ("Redstone Seeds", "mysticalagriculture:redstone_seeds", 1, "Dust from a row instead of a mesh."),
        ("Lapis Seeds", "mysticalagriculture:lapis_lazuli_seeds", 1, "Blue from leaves."),
        ("Nether Quartz Seeds", "mysticalagriculture:nether_quartz_seeds", 1, "Quartz without the Nether."),
        ("Glowstone Seeds", "mysticalagriculture:glowstone_seeds", 1, "Light you can plant."),
        ("Obsidian Seeds", "mysticalagriculture:obsidian_seeds", 1, "Hard leaves."),
        ("Imperium", "mysticalagriculture:imperium_essence", 16, "High essence. The fields are industry now."),
        ("Supremium", "mysticalagriculture:supremium_essence", 8, "Peak green."),
        ("Honey Block", "minecraft:honey_block", 8, "Swarm surplus, stacked."),
    ])
    hums = task_quest(
        s, title="Something New Hums", subtitle="Colony",
        desc=["A bee that did not exist before you built the nest.", "Mining, mason, digger, carpenter — look at one."],
        task={"type": "observation", "observe_type": 5, "timer": 0, "to_observe": "productivebees:configurable_bee"},
        rewards=[reward_item("productivebees:honey_treat", 8), reward_xp_levels(2)],
        x=5.4, y=-1.4, shape="diamond",
    )
    side = grid_optional(s, [
        ("Ring of Sand", "productivebees:sand_nest", 1, "Sand around a flower. Ashy and chocolate miners."),
        ("Ring of Reed", "productivebees:sugar_cane_nest", 1, "Sugar cane around a flower. Reed bees and masons."),
        ("Ring of Slime", "productivebees:slimy_nest", 1, "Slime blocks around a flower. Guess."),
        ("Ring of Hay", "productivebees:bumble_bee_nest", 1, "Hay around a flower. Bumble bees, and plain bees too."),
        ("Ring of Snow", "productivebees:snow_nest", 1, "Snow around a flower. Sweat bees, oddly."),
        ("Honey Generator", "productivebees:honey_generator", 1, "Burns honey for power. The Drumhearts would call it cheating."),
        ("Jar", "productivebees:jar_oak", 1, "A bee on a shelf. Decorative, and a little sad."),
        ("Campfire", "minecraft:campfire", 1, "Smoke under a hive keeps the harvest calm."),
        ("Flowering Azalea", "minecraft:flowering_azalea", 4, "Bee food."),
        ("Sunflower", "minecraft:sunflower", 4, "Bee food that faces the same way you do."),
        ("Lilac", "minecraft:lilac", 4, "Bee food."),
        ("Rose Bush", "minecraft:rose_bush", 4, "Bee food."),
        ("Peony", "minecraft:peony", 4, "Bee food."),
        ("Orange Tulip", "minecraft:orange_tulip", 8, "Bee food."),
    ], origin=(-3.5, 7.5), cols=6)
    finale = knot_finale(s, "swarm", main, 12.0, -2.0)
    return main + [wings, hums] + side + finale


def build_sigil() -> list[dict]:
    s = 8
    main = chain(s, [
        ("Amethyst", "minecraft:amethyst_shard", 32, "Old stewards left tricks."),
        # Peer braid early — do not gate Bind behind deep Occultism.
        ("Braid Cord", "ninjacatskies:braid_cord", 1, "Spun at the Tension Post from a Strand Filament, once two of Clock, Swarm, or Spark are seated."),
        ("Book and Quill", "minecraft:writable_book", 1, "Write the rite."),
        ("Enchanting Table", "minecraft:enchanting_table", 1, "Soft magic gate."),
        ("Lapis Block", "minecraft:lapis_block", 16, "Fuel the table."),
        ("Bookshelf", "minecraft:bookshelf", 15, "Full power."),
        ("Golden Apple", "minecraft:golden_apple", 1, "Rare bite."),
        ("Ender Pearl", "minecraft:ender_pearl", 16, "Skip the drop."),
        ("Brewing Stand", "minecraft:brewing_stand", 1, "Bottled tricks."),
        ("Blaze Powder", "minecraft:blaze_powder", 16, "Heat for potions."),
        ("Blaze Rod", "minecraft:blaze_rod", 8, "Nether fuel."),
        ("Fermented Eye", "minecraft:fermented_spider_eye", 4, "Corrupt potions."),
        ("Glowstone Dust", "minecraft:glowstone_dust", 16, "Glowstone dust for recipes."),
        ("Dragon Breath", "minecraft:dragon_breath", 1, "Dragon breath for potions."),
        ("Totem", "minecraft:totem_of_undying", 1, "One more chance."),
        ("Source Gem", "ars_nouveau:source_gem", 16, "Ars fuel."),
        ("Archwood", "ars_nouveau:blue_archwood_log", 16, "Mage wood."),
        ("Novice Spell Book", "ars_nouveau:novice_spell_book", 1, "First spells."),
        ("Mage Bloom", "ars_nouveau:magebloom", 8, "Arcane crop."),
        ("Ritual Brazier", "ars_nouveau:ritual_brazier", 1, "Brazier for ritual work."),
        ("Arcane Pedestal", "ars_nouveau:arcane_pedestal", 4, "Display reagents."),
        ("Scribes Table", "ars_nouveau:scribes_table", 1, "Scribe spells and pages."),
        ("Imbuement Chamber", "ars_nouveau:imbuement_chamber", 1, "Imbue reagents with source."),
        ("Source Jar", "ars_nouveau:source_jar", 2, "Store source."),
        ("Occultism Dictionary", "occultism:dictionary_of_spirits", 1, "Call spirits."),
        ("Spirit Fire", "occultism:spirit_fire", 1, "Otherworld light."),
    ])
    side = grid_optional(s, [
        ("Golden Sacrificial Bowl", "occultism:golden_sacrificial_bowl", 1, "Summon focus — Bind braid is already on the main path."),
        ("Nature Altar", "naturesaura:nature_altar", 1, "Aura craft."),
        ("Gold Fiber", "naturesaura:gold_fiber", 8, "Infused plants."),
        ("Gold Leaf", "naturesaura:gold_leaf", 8, "Aura material."),
        ("Infused Iron", "naturesaura:infused_iron", 8, "Aura metal."),
        ("Eye", "naturesaura:eye", 1, "See aura."),
        ("Token Joy", "naturesaura:token_joy", 1, "Aura token."),
        ("Spell Parchment", "ars_nouveau:spell_parchment", 4, "Spell parchment stock."),
        ("Warp Scroll", "ars_nouveau:warp_scroll", 2, "Teleport note."),
        ("Magebloom Crop", "ars_nouveau:magebloom_crop", 4, "Plant magic."),
        ("Blank Glyph", "ars_nouveau:blank_glyph", 4, "Glyph base."),
        ("Iron's Spell Book", "irons_spellbooks:iron_spell_book", 1, "Combat casting."),
        ("Arcane Essence", "irons_spellbooks:arcane_essence", 8, "Spell fuel."),
        ("Ink Common", "irons_spellbooks:common_ink", 8, "Inscribe spells."),
        ("Mystical Flower", "minecraft:allium", 8, "Color for rites."),
        ("Echo Shard", "minecraft:echo_shard", 2, "Deep dark echo."),
    ], origin=(-4.0, 7.5), cols=6)
    finale = knot_finale(s, "sigil", main, 12.0, -2.0)
    return main + side + finale


def build_spindle() -> list[dict]:
    s = 9
    main = chain(s, [
        ("Spin the Filament", "voidloom:strand_filament", 1, "Iron mesh, gravel or sand, patience."),
        ("Splice a Braid", "ninjacatskies:braid_cord", 1, "Two braid paths seated, one Filament, one right-click on the Post."),
        ("Cold Weft", "ae2:certus_quartz_crystal", 32, "Certus — the cold thread of a digital loom."),
        ("Certus Dust", "ae2:certus_quartz_dust", 16, "Ground quartz."),
        ("Sky Stone", "ae2:sky_stone_block", 16, "AE2 shell."),
        ("Charged Warp", "ae2:fluix_crystal", 32, "Fluix — certus, quartz, redstone, charged in water."),
        ("Fluix Dust", "ae2:fluix_dust", 16, "Ground fluix."),
        ("Silicon", "ae2:silicon", 32, "Silicon for AE2 processors."),
        ("Press the Pattern", "ae2:inscriber", 1, "The inscriber presses circuits the way a loom presses cloth."),
        ("Inscriber Silicon Press", "ae2:silicon_press", 1, "Silicon die."),
        ("Logic Press", "ae2:logic_processor_press", 1, "Logic die."),
        ("Calculation Press", "ae2:calculation_processor_press", 1, "Calc die."),
        ("Engineering Press", "ae2:engineering_processor_press", 1, "Engineering die craft."),
        ("Logic Processor", "ae2:logic_processor", 8, "Logic processor for AE2."),
        ("Calculation Processor", "ae2:calculation_processor", 8, "Calculation processor."),
        ("Engineering Processor", "ae2:engineering_processor", 8, "Engineering processor."),
        ("ME Drive", "ae2:drive", 1, "Store cells."),
        ("Item Cell Housing", "ae2:item_cell_housing", 4, "Cell shell."),
        ("1k Item Cell", "ae2:item_storage_cell_1k", 2, "First digital chest."),
        ("ME Terminal", "ae2:terminal", 1, "See the net."),
        ("Crafting Terminal", "ae2:crafting_terminal", 1, "Craft on-net."),
        ("Digital Loom", "ae2:controller", 1, "The controller. Wants a Binding Knot at its centre."),
        # Reweave braid + March after controller — not behind late AE2 autocraft.
        # Spindle token before Loom Fragment (fragment recipe consumes all nine tokens).
        ("Gate Drum", "tribalpower:gate_drum", 1, "Strike it open. The March is on the other side."),
        ("March Stone", "tribalpower:march_stone", 1, "Footing from beyond the gate. Bring one home."),
        ("Fluix Cable", "ae2:fluix_glass_cable", 32, "Link machines."),
        ("Import Bus", "ae2:import_bus", 2, "Pull items into storage."),
        ("Export Bus", "ae2:export_bus", 2, "Push out."),
        ("Storage Bus", "ae2:storage_bus", 2, "Attach inventory."),
        ("Crafting Unit", "ae2:crafting_unit", 8, "Autocraft body."),
        ("Crafting Co-Processing Unit", "ae2:crafting_accelerator", 2, "Faster crafts."),
        ("1k Crafting Storage", "ae2:1k_crafting_storage", 2, "Pattern memory."),
        ("Pattern Provider", "ae2:pattern_provider", 2, "Emit patterns."),
        ("Molecular Assembler", "ae2:molecular_assembler", 2, "Build from patterns — needs braid_cord in the craft."),
        ("Blank Pattern", "ae2:blank_pattern", 16, "Encode recipes."),
        ("Energy Acceptor", "ae2:energy_acceptor", 1, "Feed FE into machines."),
    ])
    side = grid_optional(s, [
        ("Vibration Chamber", "ae2:vibration_chamber", 1, "Burn for AE — optional power branch."),
        ("4k Item Cell", "ae2:item_storage_cell_4k", 1, "More space."),
        ("16k Item Cell", "ae2:item_storage_cell_16k", 1, "Dense space."),
        ("Fluid Cell Housing", "ae2:fluid_cell_housing", 2, "Liquid cells."),
        ("1k Fluid Cell", "ae2:fluid_storage_cell_1k", 1, "Digital tank."),
        ("Formation Plane", "ae2:formation_plane", 1, "Place blocks."),
        ("Annihilation Plane", "ae2:annihilation_plane", 1, "Break blocks."),
        ("Level Emitter", "ae2:level_emitter", 2, "Redstone from net."),
        ("Interface", "ae2:interface", 2, "Bridge nets."),
        ("Quantum Ring", "ae2:quantum_ring", 1, "Long link."),
        ("Quantum Link", "ae2:quantum_link", 1, "Pair rings."),
        ("Wireless Terminal", "ae2:wireless_terminal", 1, "Pocket access."),
        ("Memory Card", "ae2:memory_card", 1, "Copy settings."),
        ("Network Tool", "ae2:network_tool", 1, "Network tool for AE2."),
        ("Charger", "ae2:charger", 1, "Charge certus."),
        ("Crystal Growth Accelerator", "ae2:growth_accelerator", 2, "Grow buds."),
        ("Spirit Reed", "tribalpower:spirit_reed", 4, "March canopy proof — optional Reweave souvenir."),
    ], origin=(-4.0, 7.5), cols=6)
    finale = knot_finale(s, "spindle", main, 12.0, -2.0)
    fragment = task_quest(
        s,
        title="Loom Fragment",
        subtitle="Reweave",
        desc=["Nine seated, one March stone, one right-click on the Post: the Fragment.", "Seat it. The cut closes above your pad."],
        task={"type": "item", "item": {"id": "ninjacatskies:spindle_loom_fragment", "count": 1}},
        rewards=[reward_item("ninjacatskies:frayed_thread", 16), reward_xp_levels(5)],
        deps=[finale[1]["id"]],
        x=15.2,
        y=-2.0,
        shape="hexagon",
    )
    fragment["size"] = "1.5d"
    reweave = task_quest(
        s,
        title="Reweave",
        subtitle="The cut, closed",
        desc=["Seat the Fragment at the Tension Post.", "Nine tribes, one thread. Go and see what the March kept for you."],
        task={"type": "advancement", "advancement": "ninjacatskies:reweave", "criterion": ""},
        rewards=[reward_crate("reweave"), reward_xp_levels(10)],
        deps=[fragment["id"]],
        x=16.8,
        y=-2.0,
        shape="gear",
    )
    reweave["size"] = "2.0d"
    return main + side + finale + [fragment, reweave]


def build_exdeorum_side() -> list[dict]:
    s = 10
    return chain(s, [
        ("Crook Basics", "exdeorum:crook", 1, "Leaves drop more saplings."),
        ("Bone Crook", "exdeorum:bone_crook", 1, "Better crook."),
        ("String Mesh", "exdeorum:string_mesh", 1, "Vanilla mesh path."),
        ("Flint Mesh", "exdeorum:flint_mesh", 1, "Better drops."),
        ("Iron Mesh", "exdeorum:iron_mesh", 1, "Iron tier mesh."),
        ("Golden Mesh", "exdeorum:golden_mesh", 1, "Gold tier mesh."),
        ("Diamond Mesh", "exdeorum:diamond_mesh", 1, "Diamond tier mesh."),
        ("Netherite Mesh", "exdeorum:netherite_mesh", 1, "Top mesh."),
        ("Porcelain Clay", "exdeorum:porcelain_clay_ball", 16, "Clay refined."),
        ("Unfired Crucible", "exdeorum:unfired_porcelain_crucible", 1, "Fuel a furnace generator."),
        ("Porcelain Crucible", "exdeorum:porcelain_crucible", 1, "Hot safe."),
        ("Watering Can Wood", "exdeorum:wooden_watering_can", 1, "Splash growth."),
        ("Watering Can Iron", "exdeorum:iron_watering_can", 1, "Bigger splash."),
        ("Silkworm", "exdeorum:silkworm", 4, "Infest leaves."),
        ("Witch Water Bucket", "exdeorum:witch_water_bucket", 1, "Strange fluid."),
        ("Mycelium Spores", "exdeorum:mycelium_spores", 4, "Spread fungi."),
        ("Grass Seeds", "exdeorum:grass_seeds", 4, "Spread grass."),
        ("Stone Pebble", "exdeorum:stone_pebble", 64, "Hammer output."),
        ("Compressed Cobble", "exdeorum:compressed_cobblestone", 16, "Bulk stone."),
        ("Netherite Hammer", "exdeorum:netherite_hammer", 1, "Top hammer."),
    ]) + grid_optional(s, [
        ("Blackstone Pebble", "exdeorum:blackstone_pebble", 32, "Nether stone."),
        ("Deepslate Pebble", "exdeorum:deepslate_pebble", 32, "Deep grit."),
        ("Calcite", "exdeorum:calcite_pebble", 16, "White stone."),
        ("Tuff", "exdeorum:tuff_pebble", 16, "Grey stone."),
        ("Dripstone", "minecraft:pointed_dripstone", 8, "Cave spike."),
        ("Sponge", "minecraft:sponge", 1, "Dry the pad."),
    ], origin=(0.0, 7.5), cols=6)


def build_storage_side() -> list[dict]:
    s = 11
    return chain(s, [
        ("Oak Drawer 1x1", "functionalstorage:oak_1", 2, "Simple drawers."),
        ("Oak Drawer 1x2", "functionalstorage:oak_2", 2, "Split drawer."),
        ("Oak Drawer 2x2", "functionalstorage:oak_4", 2, "Quad drawer."),
        ("Compacting Drawer", "functionalstorage:compacting_drawer", 1, "Auto compact."),
        ("Storage Controller", "functionalstorage:storage_controller", 1, "Link drawers."),
        ("Collector Upgrade", "functionalstorage:collector_upgrade", 1, "Pull drops."),
        ("Puller Upgrade", "functionalstorage:puller_upgrade", 1, "Pull inventories."),
        ("Pusher Upgrade", "functionalstorage:pusher_upgrade", 1, "Push inventories."),
        ("Void Upgrade", "functionalstorage:void_upgrade", 1, "Overflow sink."),
        ("Backpack", "sophisticatedbackpacks:backpack", 1, "Carry more."),
        ("Iron Backpack", "sophisticatedbackpacks:iron_backpack", 1, "Upgrade pack."),
        ("Gold Backpack", "sophisticatedbackpacks:gold_backpack", 1, "Bigger pack."),
        ("Diamond Backpack", "sophisticatedbackpacks:diamond_backpack", 1, "Deep pockets."),
        ("Pickup Upgrade", "sophisticatedbackpacks:pickup_upgrade", 1, "Pickup upgrade vacuum."),
        ("Filter Upgrade", "sophisticatedbackpacks:filter_upgrade", 1, "Filter what enters packs."),
        ("Crafting Upgrade", "sophisticatedbackpacks:crafting_upgrade", 1, "Craft in pack."),
        ("Feeding Upgrade", "sophisticatedbackpacks:feeding_upgrade", 1, "Auto eat."),
        ("Restock Upgrade", "sophisticatedbackpacks:restock_upgrade", 1, "Restock tools."),
        ("Deposit Upgrade", "sophisticatedbackpacks:deposit_upgrade", 1, "Dump to chests."),
        ("Tank Upgrade", "sophisticatedbackpacks:tank_upgrade", 1, "Carry fluids."),
    ])


def build_mekanism_side() -> list[dict]:
    s = 12
    return chain(s, [
        ("Steel Ingot", "mekanism:ingot_steel", 16, "Industrial spine."),
        ("Osmium Ingot", "mekanism:ingot_osmium", 16, "Mekanism core metal."),
        ("Refined Obsidian", "mekanism:ingot_refined_obsidian", 4, "Hard alloy."),
        ("Basic Control Circuit", "mekanism:basic_control_circuit", 8, "Mekanism control circuit."),
        ("Advanced Control Circuit", "mekanism:advanced_control_circuit", 4, "Smarter brain."),
        ("Elite Control Circuit", "mekanism:elite_control_circuit", 2, "Elite brain."),
        ("Metallurgic Infuser", "mekanism:metallurgic_infuser", 1, "Infuse metals."),
        ("Enrichment Chamber", "mekanism:enrichment_chamber", 1, "Enrich ores."),
        ("Crusher", "mekanism:crusher", 1, "Mill or crush bulk materials."),
        ("Energized Smelter", "mekanism:energized_smelter", 1, "FE smelt."),
        ("Purification Chamber", "mekanism:purification_chamber", 1, "Pure ores."),
        ("Chemical Injection", "mekanism:chemical_injection_chamber", 1, "Chemical injection chamber."),
        ("Osmium Compressor", "mekanism:osmium_compressor", 1, "Osmium compressor."),
        ("Basic Bin", "mekanism:basic_bin", 2, "Bulk items."),
        ("Basic Fluid Tank", "mekanism:basic_fluid_tank", 2, "Bulk fluid."),
        ("Basic Energy Cube", "mekanism:basic_energy_cube", 1, "Energy cube buffer."),
        ("Basic Universal Cable", "mekanism:basic_universal_cable", 16, "FE cable."),
        ("Basic Mechanical Pipe", "mekanism:basic_mechanical_pipe", 16, "Fluid pipe."),
        ("Basic Logistical Transporter", "mekanism:basic_logistical_transporter", 16, "Item pipe."),
        ("Configurator", "mekanism:configurator", 1, "Configure all."),
    ]) + grid_optional(s, [
        ("Jetpack", "mekanism:jetpack", 1, "Mek jetpack — optional lift."),
        ("Free Runners", "mekanism:free_runners", 1, "Forgiving void safety."),
        ("Atomic Disassembler", "mekanism:atomic_disassembler", 1, "Late tool."),
        ("Steel Casing", "mekanism:steel_casing", 8, "Machine frame."),
        ("Teleporter", "mekanism:teleporter", 1, "Warp pad."),
        ("Digital Miner", "mekanism:digital_miner", 1, "Auto mine."),
    ], origin=(0.0, 7.5), cols=6)


def build_powah_side() -> list[dict]:
    s = 13
    return chain(s, [
        ("Dielectric Paste", "powah:dielectric_paste", 32, "Powah craft goo."),
        ("Capacitor Basic", "powah:capacitor_basic", 8, "Store a pulse of FE."),
        ("Energy Cell Basic", "powah:energy_cell_basic", 1, "Bigger buffer."),
        ("Furnator Basic", "powah:furnator_basic", 1, "Burn better."),
        ("Magmator Basic", "powah:magmator_basic", 1, "Lava power."),
        ("Solar Basic", "powah:solar_panel_basic", 4, "Better solar."),
        ("Thermo Basic", "powah:thermo_generator_basic", 1, "Better thermo."),
        ("Reactor Basic", "powah:reactor_basic", 1, "Solid fuel reactor."),
        ("Energy Cable Basic", "powah:energy_cable_basic", 16, "Thicker cable."),
        ("Player Transmitter Basic", "powah:player_transmitter_basic", 1, "Charge the player."),
        ("Energy Hopper Basic", "powah:energy_hopper_basic", 1, "Charge inventories."),
        ("Energizing Rod Basic", "powah:energizing_rod_basic", 1, "Faster energize."),
        ("Battery Basic", "powah:battery_basic", 1, "Pocket FE+."),
        ("Niotic Crystal", "powah:crystal_niotic", 4, "Crystal tier."),
        ("Spirited Crystal", "powah:crystal_spirited", 2, "Higher crystal."),
        ("Nitro Crystal", "powah:crystal_nitro", 1, "Top crystal."),
    ])


def build_ars_side() -> list[dict]:
    s = 14
    return chain(s, [
        ("Mage Fiber", "ars_nouveau:magebloom_fiber", 16, "Weave magecloth."),
        ("Magebloom", "ars_nouveau:magebloom", 16, "Bloom again."),
        ("Source Gem Block", "ars_nouveau:source_gem_block", 4, "Dense source."),
        ("Apprentice Spell Book", "ars_nouveau:apprentice_spell_book", 1, "More glyphs."),
        ("Archmage Spell Book", "ars_nouveau:archmage_spell_book", 1, "Full book."),
        ("Spell Turret", "ars_nouveau:basic_spell_turret", 1, "Auto cast."),
        ("Timer Spell Turret", "ars_nouveau:timer_spell_turret", 1, "Timed cast."),
        ("Enchanting Apparatus", "ars_nouveau:enchanting_apparatus", 1, "Arcane craft."),
        ("Arcane Core", "ars_nouveau:arcane_core", 1, "Apparatus core."),
        ("Relay", "ars_nouveau:relay", 2, "Move source."),
        ("Relay Splitter", "ars_nouveau:relay_splitter", 1, "Split source."),
        ("Agronomic Sourcelink", "ars_nouveau:agronomic_sourcelink", 1, "Crops to source."),
        ("Volcanic Sourcelink", "ars_nouveau:volcanic_sourcelink", 1, "Heat to source."),
        ("Wixie Charm", "ars_nouveau:wixie_charm", 1, "Craft familiar."),
        ("Starbuncle Charm", "ars_nouveau:starbuncle_charm", 1, "Item familiar."),
        ("Drygmy Charm", "ars_nouveau:drygmy_charm", 1, "Loot familiar."),
        ("Whirlisprig Charm", "ars_nouveau:whirlisprig_charm", 1, "Farm familiar."),
        ("Amethyst Golem Charm", "ars_nouveau:amethyst_golem_charm", 1, "Bud familiar."),
        ("Dominion Wand", "ars_nouveau:dominion_wand", 1, "Bind systems."),
        ("Allow Scroll", "ars_nouveau:allow_scroll", 2, "Filter allow."),
        ("Deny Scroll", "ars_nouveau:deny_scroll", 2, "Filter deny."),
    ])


def build_clowder() -> list[dict]:
    s = 15
    ceremony = [
        task_quest(s, title="Raise the Post", desc=["Logs around a Binding Knot, Thread on top. Place it on the pad.", "Stand near it: the pad starts mending you once a Strand is seated."],
                   task={"type": "observation", "observe_type": 0, "timer": 0, "to_observe": "ninjacatskies:tension_post"},
                   rewards=[reward_item("ninjacatskies:frayed_thread", 4)], x=-2.0, y=-2.0, shape="hexagon"),
        task_quest(s, title="Enter the Hall", desc=["Hub Key in hand, or /clowder hub. Every Clowder on the server meets here.", "/clowder return brings you home."],
                   task={"type": "dimension", "dimension": "clowderhall:clowder_hall"},
                   rewards=[reward_item("ninjacatskies:frayed_thread", 4), reward_xp_levels(1)], x=-0.4, y=-2.0, shape="hexagon"),
        task_quest(s, title="Look at the Fray", desc=["Above the Dock stands a slow dark column: the cut itself.", "It thins as Clowders seat Strands. Come back and check it now and then."],
                   task={"type": "checkmark"}, rewards=[reward_item("ninjacatskies:codex_page", 1)], x=1.2, y=-2.0, shape="diamond"),
    ]
    return ceremony + chain(s, [
        ("Island Charter", "clowderhall:island_charter", 1, "Name a pad as yours."),
        ("Hub Key", "clowderhall:hub_key", 1, "Find the Hall."),
        ("Strand Banner", "clowderhall:strand_banner_pattern", 1, "Mark progress."),
        ("Quest Book", "ftbquests:book", 1, "Open the Codex path."),
        ("Chunk Claim Snack", "minecraft:golden_carrot", 8, "Stay fed on claim runs."),
        ("Map", "minecraft:map", 1, "See neighbors."),
        ("Compass", "minecraft:compass", 1, "Find home."),
        ("Lodestone", "minecraft:lodestone", 1, "Lodestone compass anchor."),
        ("Recovery Compass", "minecraft:recovery_compass", 1, "Death path."),
        ("Bell", "minecraft:bell", 1, "Call the Clowder."),
        ("Lectern", "minecraft:lectern", 1, "Rules book stand."),
        ("Oak Sign", "minecraft:oak_sign", 8, "Label districts."),
        ("White Banner", "minecraft:white_banner", 1, "Team color."),
        ("Shield Banner Ready", "minecraft:shield", 1, "Shield ready for banners."),
        ("Firework", "minecraft:firework_rocket", 8, "Celebrate Strand clears."),
    ]) + grid_optional(s, [
        ("Cookie Tribute", "minecraft:cookie", 16, "Share with the Hall."),
        ("Cake", "minecraft:cake", 1, "Cake for celebrations."),
        ("Music Disc", "minecraft:music_disc_cat", 1, "Cat disc — pack mood."),
        ("Lead", "minecraft:lead", 2, "Bring mobs home."),
        ("Saddle", "minecraft:saddle", 1, "Mount when you find a saddle."),
        ("Boat", "minecraft:oak_boat", 1, "If you somehow find water seas."),
    ], origin=(0.0, 7.5), cols=6)


def build_aura_side() -> list[dict]:
    s = 17
    return chain(s, [
        ("Eye", "naturesaura:eye", 1, "See the aura."),
        ("Gold Fiber", "naturesaura:gold_fiber", 16, "Infuse plants."),
        ("Gold Leaf", "naturesaura:gold_leaf", 16, "Aura material."),
        ("Golden Leaves", "naturesaura:golden_leaves", 8, "Glow canopy."),
        ("Wood Stand", "naturesaura:wood_stand", 1, "Offering stand."),
        ("Nature Altar", "naturesaura:nature_altar", 1, "Aura crafts."),
        ("Infused Iron", "naturesaura:infused_iron", 16, "Aura metal."),
        ("Ancient Bark", "naturesaura:ancient_bark", 8, "Old wood."),
        ("Token Joy", "naturesaura:token_joy", 1, "Joy token."),
        ("Token Fear", "naturesaura:token_fear", 1, "Fear token."),
        ("Token Anger", "naturesaura:token_anger", 1, "Anger token."),
        ("Token Sorrow", "naturesaura:token_sorrow", 1, "Sorrow token."),
        ("Calling Spirit", "naturesaura:calling_spirit", 1, "Aura spirit for rituals."),
        ("Birth Spirit", "naturesaura:birth_spirit", 1, "Birth spirit for aura rites."),
        ("Aura Troves", "naturesaura:aura_trove", 1, "Store aura."),
        ("Generator Puzzle", "naturesaura:generator_limit_remover", 1, "If present — late."),
        ("Environmental Eye", "naturesaura:eye_improved", 1, "Better sight."),
        ("Crushing Catalyst", "naturesaura:crushing_catalyst", 1, "Crush with aura."),
        ("Conversion Catalyst", "naturesaura:conversion_catalyst", 1, "Conversion catalyst."),
        ("Depths Powder", "naturesaura:depth_ingot", 4, "Deep metal."),
    ]) + grid_optional(s, [
        ("Farming Stencil", "naturesaura:farming_stencil", 1, "Farm aura patterns."),
        ("Projectile Generator", "naturesaura:projectile_generator", 1, "Aura from shots."),
        ("Flower Generator", "naturesaura:flower_generator", 1, "Aura from flowers."),
        ("Oak Generator", "naturesaura:oak_generator", 1, "Aura from oaks."),
        ("End Flower", "naturesaura:end_flower", 1, "End flora."),
        ("Spawn Lamp", "naturesaura:spawn_lamp", 1, "Light spawns."),
    ], origin=(0.0, 7.5), cols=6)


def build_food_side() -> list[dict]:
    s = 18
    return chain(s, [
        ("Cooking Pot", "farmersdelight:cooking_pot", 1, "Kitchen heart."),
        ("Skillet", "farmersdelight:skillet", 1, "Skillet pan fry meals."),
        ("Stove", "farmersdelight:stove", 1, "Stove for Farmer's Delight."),
        ("Cutting Board", "farmersdelight:cutting_board", 1, "Prep ingredients cleanly."),
        ("Basket", "farmersdelight:wooden_basket", 1, "Basket for farm haul."),
        ("Rope", "farmersdelight:rope", 16, "Climb and craft."),
        ("Safety Net", "farmersdelight:safety_net", 4, "Soft landing."),
        ("Rich Soil", "farmersdelight:rich_soil", 16, "Better crops."),
        ("Organic Compost", "farmersdelight:organic_compost", 16, "Make rich soil."),
        ("Cabbage Rolls", "farmersdelight:cabbage_rolls", 8, "Cabbage rolls meal."),
        ("Bacon Sandwich", "farmersdelight:bacon_sandwich", 4, "Crisp lunch."),
        ("Hamburger", "farmersdelight:hamburger", 4, "Hamburger comfort food."),
        ("Chicken Soup", "farmersdelight:chicken_soup", 4, "Chicken soup warm-up."),
        ("Beef Stew", "farmersdelight:beef_stew", 4, "Beef stew fills hard."),
        ("Noodle Soup", "farmersdelight:noodle_soup", 4, "Noodle soup bowl."),
        ("Apple Pie", "farmersdelight:apple_pie", 2, "Apple pie finish."),
        ("Sweet Berry Cheesecake", "farmersdelight:sweet_berry_cheesecake", 2, "Tart sweet."),
        ("Rice", "farmersdelight:rice", 16, "Rice for kitchen line."),
        ("Fried Rice", "farmersdelight:fried_rice", 4, "Kitchen line comfort food."),
        ("Dumplings", "farmersdelight:dumplings", 8, "Filled dough."),
        ("Hot Cocoa", "farmersdelight:hot_cocoa", 4, "Warm drink."),
        ("Melon Juice", "farmersdelight:melon_juice", 4, "Cool drink."),
        ("Canvas", "farmersdelight:canvas", 8, "Cloth craft."),
        ("Tatami", "farmersdelight:tatami", 8, "Tatami pad flooring."),
    ])


def build_spells_side() -> list[dict]:
    s = 19
    return chain(s, [
        ("Iron Spell Book", "irons_spellbooks:iron_spell_book", 1, "Battle casting."),
        ("Gold Spell Book", "irons_spellbooks:gold_spell_book", 1, "Better book."),
        ("Diamond Spell Book", "irons_spellbooks:diamond_spell_book", 1, "Hard book."),
        ("Arcane Essence", "irons_spellbooks:arcane_essence", 32, "Spell fuel."),
        ("Common Ink", "irons_spellbooks:common_ink", 16, "Scribe spells and pages."),
        ("Uncommon Ink", "irons_spellbooks:uncommon_ink", 8, "Better ink."),
        ("Rare Ink", "irons_spellbooks:rare_ink", 4, "Rare ink."),
        ("Epic Ink", "irons_spellbooks:epic_ink", 2, "Epic ink."),
        ("Legendary Ink", "irons_spellbooks:legendary_ink", 1, "Peak ink."),
        ("Scroll", "irons_spellbooks:scroll", 4, "Cast once."),
        ("Magic Cloth", "irons_spellbooks:magic_cloth", 8, "Magic cloth for robes."),
        ("Wandering Magician Helmet", "irons_spellbooks:wandering_magician_helmet", 1, "Light spellcaster headgear."),
        ("Wandering Magician Chestplate", "irons_spellbooks:wandering_magician_chestplate", 1, "Spellcaster chest armor."),
        ("Pyrium Staff", "irons_spellbooks:pyrium_staff", 1, "If present."),
        ("Graybeard Staff", "irons_spellbooks:graybeard_staff", 1, "Starter staff."),
        ("Magehunter", "irons_spellbooks:magehunter", 1, "Anti-mage blade."),
        ("Copper Spell Book", "irons_spellbooks:copper_spell_book", 1, "Early book."),
        ("Netherite Spell Book", "irons_spellbooks:netherite_spell_book", 1, "End book."),
        ("Arcane Ingot", "irons_spellbooks:arcane_ingot", 8, "Spell metal."),
        ("Ruined Codex", "irons_spellbooks:ruined_book", 1, "Salvage lore."),
    ])


def build_solar_side() -> list[dict]:
    s = 20
    return chain(s, [
        ("Mirror", "solarflux:mirror", 16, "Bounce light."),
        ("Photovoltaic Cell 1", "solarflux:photovoltaic_cell_1", 8, "Cell tier 1."),
        ("Photovoltaic Cell 2", "solarflux:photovoltaic_cell_2", 4, "Cell tier 2."),
        ("Photovoltaic Cell 3", "solarflux:photovoltaic_cell_3", 4, "Cell tier 3."),
        ("Photovoltaic Cell 4", "solarflux:photovoltaic_cell_4", 2, "Cell tier 4."),
        ("Photovoltaic Cell 5", "solarflux:photovoltaic_cell_5", 2, "Cell tier 5."),
        ("Photovoltaic Cell 6", "solarflux:photovoltaic_cell_6", 2, "Cell tier 6."),
        ("Capacity Upgrade", "solarflux:capacity_upgrade", 2, "More buffer."),
        ("Efficiency Upgrade", "solarflux:efficiency_upgrade", 2, "More gen."),
        ("Transfer Upgrade", "solarflux:transfer_rate_upgrade", 2, "Faster out."),
        ("Traversal Upgrade", "solarflux:traversal_upgrade", 1, "Solar traversal upgrade."),
        ("Dispersive Upgrade", "solarflux:dispersive_upgrade", 1, "Spread charge."),
        ("Block Charging Upgrade", "solarflux:block_charging_upgrade", 1, "Charge blocks."),
        ("Furnace Upgrade", "solarflux:furnace_upgrade", 1, "Burn with sun."),
        ("Emerald Glass", "solarflux:emerald_glass", 4, "Green glass."),
        ("Ender Glass", "solarflux:ender_glass", 4, "Ender glass."),
        ("Blazing Coating", "solarflux:blazing_coating", 4, "Hot coat."),
        ("Blank Upgrade", "solarflux:blank_upgrade", 4, "Upgrade base."),
    ])


def build_decor_side() -> list[dict]:
    s = 21
    blocks = [
        ("Stone Bricks", "minecraft:stone_bricks", 32, "Clean stone."),
        ("Mossy Stone Bricks", "minecraft:mossy_stone_bricks", 16, "Mossy brick pad trim."),
        ("Cracked Stone Bricks", "minecraft:cracked_stone_bricks", 16, "Cracked brick texture."),
        ("Chiseled Stone Bricks", "minecraft:chiseled_stone_bricks", 8, "Chiseled brick detail."),
        ("Smooth Stone", "minecraft:smooth_stone", 32, "Smooth stone surfaces."),
        ("Polished Andesite", "minecraft:polished_andesite", 32, "Grey polish."),
        ("Polished Diorite", "minecraft:polished_diorite", 16, "White polish."),
        ("Polished Granite", "minecraft:polished_granite", 16, "Pink polish."),
        ("Bricks", "minecraft:bricks", 32, "Clay fired."),
        ("Mud Bricks", "minecraft:mud_bricks", 16, "Mud brick trim."),
        ("Deepslate Bricks", "minecraft:deepslate_bricks", 16, "Dark bricks."),
        ("Deepslate Tiles", "minecraft:deepslate_tiles", 16, "Dark tiles."),
        ("Blackstone", "minecraft:blackstone", 16, "Nether grey."),
        ("Polished Blackstone", "minecraft:polished_blackstone", 16, "Polished dark."),
        ("Gilded Blackstone", "minecraft:gilded_blackstone", 4, "Gold flecks."),
        ("Quartz Block", "minecraft:quartz_block", 16, "Clean white."),
        ("Smooth Quartz", "minecraft:smooth_quartz", 8, "Smooth quartz trim."),
        ("Purpur Block", "minecraft:purpur_block", 8, "End purple."),
        ("Prismarine", "minecraft:prismarine", 8, "Sea stone."),
        ("Dark Prismarine", "minecraft:dark_prismarine", 8, "Deep sea."),
        ("Sea Lantern", "minecraft:sea_lantern", 4, "Wet light."),
        ("Shroomlight", "minecraft:shroomlight", 4, "Fungus light."),
        ("Ochre Froglight", "minecraft:ochre_froglight", 2, "Frog light."),
        ("Pearlescent Froglight", "minecraft:pearlescent_froglight", 2, "Pearl light."),
        ("Verdant Froglight", "minecraft:verdant_froglight", 2, "Green light."),
        ("Tinted Glass", "minecraft:tinted_glass", 8, "Dim glass."),
        ("White Stained Glass", "minecraft:white_stained_glass", 8, "Soft glass."),
        ("Light Blue Stained Glass", "minecraft:light_blue_stained_glass", 8, "Sky glass."),
        ("Cyan Stained Glass", "minecraft:cyan_stained_glass", 8, "Teal glass."),
        ("Purple Stained Glass", "minecraft:purple_stained_glass", 8, "Void glass."),
        ("Candle", "minecraft:candle", 8, "Quiet flame."),
        ("White Candle", "minecraft:white_candle", 4, "Pale flame."),
        ("Scaffolding Tower", "minecraft:scaffolding", 64, "Climb the pad edge safely."),
        ("Ladder Stock", "minecraft:ladder", 32, "Ladders for vertical pads."),
        ("Rail Spare", "minecraft:rail", 64, "Rails across the void."),
        ("Oak Boat", "minecraft:oak_boat", 1, "Just in case."),
        ("Painting Spare", "minecraft:painting", 4, "Decor for the pad walls."),
        ("Armor Stand", "minecraft:armor_stand", 2, "Display gear."),
        ("Glow Item Frame", "minecraft:glow_item_frame", 4, "Lit frame."),
        ("Flower Pot Spare", "minecraft:flower_pot", 8, "Flower pots for green."),
        ("Oak Hanging Sign", "minecraft:oak_hanging_sign", 4, "Hanging signs for rooms."),
        ("Loom", "minecraft:loom", 1, "Loom for banner work."),
        ("Stonecutter", "minecraft:stonecutter", 1, "Detail stone."),
        ("Grindstone", "minecraft:grindstone", 1, "Grindstone resets gear."),
        ("Smithing Table", "minecraft:smithing_table", 1, "Upgrade gear."),
        ("Cartography Table", "minecraft:cartography_table", 1, "Chart the island grid."),
        ("Fletching Table", "minecraft:fletching_table", 1, "Fletching table utility."),
        ("Blast Furnace Spare", "minecraft:blast_furnace", 1, "Metal heat."),
        ("Smoker Spare", "minecraft:smoker", 1, "Food heat."),
        ("Cauldron", "minecraft:cauldron", 1, "Hold water."),
        ("Hopper Spare", "minecraft:hopper", 4, "Move more."),
        ("Dispenser Spare", "minecraft:dispenser", 2, "Auto use."),
        ("Observer Spare", "minecraft:observer", 2, "Watch more."),
        ("Redstone Block", "minecraft:redstone_block", 4, "Dense signal."),
        ("Target Spare", "minecraft:target", 2, "Signal catch."),
        ("Note Block Spare", "minecraft:note_block", 2, "Jukebox for pad morale."),
        ("Jukebox Spare", "minecraft:jukebox", 1, "Jukebox for discs."),
        ("Bell Spare", "minecraft:bell", 1, "Bell marks the Clowder."),
        ("Respawn Anchor", "minecraft:respawn_anchor", 1, "Nether bed."),
        ("Lodestone Spare", "minecraft:lodestone", 1, "Compass lock."),
        ("Lightning Rod Spare", "minecraft:lightning_rod", 2, "Storm rod."),
        ("Ender Chest", "minecraft:ender_chest", 1, "Shared void box."),
        ("Shulker Shell", "minecraft:shulker_shell", 2, "Box shell."),
    ]
    return chain(s, blocks[:20]) + grid_optional(s, blocks[20:], origin=(0.0, 7.5), cols=6)


def build_nether_side() -> list[dict]:
    s = 22
    return chain(s, [
        ("Netherrack Stock", "minecraft:netherrack", 64, "Hell grit."),
        ("Nether Bricks", "minecraft:nether_bricks", 32, "Fortress look."),
        ("Red Nether Bricks", "minecraft:red_nether_bricks", 16, "Bloody brick."),
        ("Basalt", "minecraft:basalt", 32, "Column stone."),
        ("Polished Basalt", "minecraft:polished_basalt", 16, "Smooth column."),
        ("Smooth Basalt", "minecraft:smooth_basalt", 16, "Flat basalt."),
        ("Blackstone Stock", "minecraft:blackstone", 32, "Bastion stone."),
        ("Magma Block", "minecraft:magma_block", 16, "Hot floor."),
        ("Soul Sand Stock", "minecraft:soul_sand", 16, "Soul sand foothold stock."),
        ("Soul Soil", "minecraft:soul_soil", 16, "Soul fire base."),
        ("Glowstone", "minecraft:glowstone", 16, "Nether light."),
        ("Shroomlight Stock", "minecraft:shroomlight", 8, "Fungus glow."),
        ("Nether Wart Block", "minecraft:nether_wart_block", 8, "Crimson mass."),
        ("Warped Wart Block", "minecraft:warped_wart_block", 8, "Warped mass."),
        ("Crimson Stem", "minecraft:crimson_stem", 16, "Crimson wood."),
        ("Warped Stem", "minecraft:warped_stem", 16, "Warped wood."),
        ("Weeping Vines", "minecraft:weeping_vines", 8, "Chain for hanging flair."),
        ("Twisting Vines", "minecraft:twisting_vines", 8, "Twisting vines foothold."),
        ("Crying Obsidian", "minecraft:crying_obsidian", 8, "Sad portal."),
        ("Ancient Debris", "minecraft:ancient_debris", 4, "Netherite path."),
        ("Netherite Scrap", "minecraft:netherite_scrap", 4, "Netherite scrap stock."),
        ("Netherite Ingot", "minecraft:netherite_ingot", 1, "Peak metal."),
        ("Blaze Rod Stock", "minecraft:blaze_rod", 16, "Brew and fuel."),
        ("Ghast Tear", "minecraft:ghast_tear", 4, "Regen brew."),
        ("Magma Cream", "minecraft:magma_cream", 8, "Fire resist."),
        ("Wither Skeleton Skull", "minecraft:wither_skeleton_skull", 1, "Boss bait."),
        ("Gold Nugget Pile", "minecraft:gold_nugget", 64, "Piglin trade."),
        ("Nether Gold Ore", "minecraft:nether_gold_ore", 16, "Piglin stone."),
        ("Quartz", "minecraft:quartz", 32, "Nether quartz."),
        ("Fire Charge", "minecraft:fire_charge", 8, "Throw fire."),
    ])


def build_end_side() -> list[dict]:
    s = 23
    return chain(s, [
        ("End Stone", "minecraft:end_stone", 64, "Pale void."),
        ("End Stone Bricks", "minecraft:end_stone_bricks", 32, "Clean end."),
        ("Purpur Block Stock", "minecraft:purpur_block", 32, "Chorus stone."),
        ("Purpur Pillar", "minecraft:purpur_pillar", 8, "Purpur pillar column."),
        ("End Rod", "minecraft:end_rod", 8, "Pale light."),
        ("Chorus Fruit", "minecraft:chorus_fruit", 16, "Teleport snack."),
        ("Popped Chorus", "minecraft:popped_chorus_fruit", 16, "Purpur craft."),
        ("Ender Pearl Stock", "minecraft:ender_pearl", 32, "Ender pearl stock."),
        ("Eye of Ender Stock", "minecraft:ender_eye", 8, "Eyes of Ender stock."),
        ("Dragon Breath Stock", "minecraft:dragon_breath", 4, "Dragon breath for potions."),
        ("Dragon Egg Show", "minecraft:dragon_egg", 1, "Dragon egg showpiece."),
        ("Elytra Show", "minecraft:elytra", 1, "Elytra for skybound travel."),
        ("Shulker Shell Stock", "minecraft:shulker_shell", 4, "Shulker shells for boxes."),
        ("Shulker Box Show", "minecraft:shulker_box", 1, "Shulker box inventory."),
        ("End Crystal Show", "minecraft:end_crystal", 4, "End crystals — handle gently."),
        ("Ender Chest Show", "minecraft:ender_chest", 1, "Linked void."),
        ("Chorus Flower", "minecraft:chorus_flower", 2, "Grow chorus."),
        ("End Portal Frame", "minecraft:end_portal_frame", 1, "If obtained."),
        ("Black Concrete", "minecraft:black_concrete", 16, "Void floor."),
        ("Purple Concrete", "minecraft:purple_concrete", 16, "End accent."),
        ("Obsidian Stock", "minecraft:obsidian", 32, "Obsidian platform stock."),
        ("Crying Obsidian Stock", "minecraft:crying_obsidian", 16, "Sad stone."),
        ("Respawn Anchor Show", "minecraft:respawn_anchor", 1, "Alt spawn."),
        ("Totem Show", "minecraft:totem_of_undying", 1, "Second chance."),
        ("Nether Star Show", "minecraft:nether_star", 1, "Beacon fuel."),
        ("Beacon Show", "minecraft:beacon", 1, "Clowder monument."),
        ("Conduit Show", "minecraft:conduit", 1, "Sea power."),
        ("Heart of the Sea", "minecraft:heart_of_the_sea", 1, "Conduit core."),
        ("Nautilus Shell", "minecraft:nautilus_shell", 8, "Conduit ring."),
        ("Trident Show", "minecraft:trident", 1, "Sea claw."),
    ])



def build_crops_side() -> list[dict]:
    s = 24
    main = chain(s, [
        ("Inferium Stock", "mysticalagriculture:inferium_essence", 64, "Essence engine fuel."),
        ("Prosperity Base", "mysticalagriculture:prosperity_seed_base", 4, "Seed skeleton."),
        ("Infusion Crystal", "mysticalagriculture:infusion_crystal", 1, "Tier catalyst."),
        ("Prudentium Stock", "mysticalagriculture:prudentium_essence", 32, "Tier two green."),
        ("Tertium Stock", "mysticalagriculture:tertium_essence", 32, "Tier three."),
        ("Imperium Stock", "mysticalagriculture:imperium_essence", 16, "Tier four."),
        ("Supremium Stock", "mysticalagriculture:supremium_essence", 8, "Tier five."),
        ("Awakened Essence", "mysticalagriculture:awakened_supremium_essence", 4, "Peak green."),
        ("Awakening Altar", "mysticalagriculture:awakening_altar", 1, "Raise the peak."),
        ("Awakening Pedestal", "mysticalagriculture:awakening_pedestal", 4, "Circle the peak."),
        ("Master Crystal", "mysticalagriculture:master_infusion_crystal", 1, "Endless catalyst."),
        ("Essence Vessel", "mysticalagriculture:essence_vessel", 1, "Hold the glow."),
        ("Machine Frame", "mysticalagriculture:machine_frame", 1, "Farm hardware."),
        ("Harvester", "mysticalagriculture:harvester", 1, "Auto cut."),
        ("Seed Reprocessor", "mysticalagriculture:seed_reprocessor", 1, "Recycle seeds."),
        ("Inferium Accel", "mysticalagriculture:inferium_growth_accelerator", 4, "Faster rows."),
        ("Prudentium Accel", "mysticalagriculture:prudentium_growth_accelerator", 2, "Faster still."),
        ("Tertium Accel", "mysticalagriculture:tertium_growth_accelerator", 2, "Mid speed."),
        ("Imperium Accel", "mysticalagriculture:imperium_growth_accelerator", 1, "High speed."),
        ("Supremium Accel", "mysticalagriculture:supremium_growth_accelerator", 1, "Peak speed."),
        ("Watering Can", "mysticalagriculture:watering_can", 1, "Splash growth."),
        ("Inferium Can", "mysticalagriculture:inferium_watering_can", 1, "Tier splash."),
        ("Prudentium Can", "mysticalagriculture:prudentium_watering_can", 1, "Better splash."),
        ("Tertium Can", "mysticalagriculture:tertium_watering_can", 1, "Wide splash."),
        ("Imperium Can", "mysticalagriculture:imperium_watering_can", 1, "Strong splash."),
        ("Supremium Can", "mysticalagriculture:supremium_watering_can", 1, "Peak splash."),
        ("Fertilized Essence", "mysticalagriculture:fertilized_essence", 16, "Growth food."),
        ("Soulium Dust", "mysticalagriculture:soulium_dust", 16, "Mob farm dust."),
        ("Soulium Ingot", "mysticalagriculture:soulium_ingot", 8, "Soul metal."),
        ("Soulium Dagger", "mysticalagriculture:soulium_dagger", 1, "Soul harvest."),
        ("Soulium Seed Base", "mysticalagriculture:soulium_seed_base", 4, "Hostile seeds."),
    ])
    seeds = [
        ("Redstone Seeds", "mysticalagriculture:redstone_seeds", 1, "Dust farm."),
        ("Lapis Seeds", "mysticalagriculture:lapis_lazuli_seeds", 1, "Blue farm."),
        ("Diamond Seeds", "mysticalagriculture:diamond_seeds", 1, "Hard farm."),
        ("Emerald Seeds", "mysticalagriculture:emerald_seeds", 1, "Trade farm."),
        ("Obsidian Seeds", "mysticalagriculture:obsidian_seeds", 1, "Dark farm."),
        ("Nether Quartz Seeds", "mysticalagriculture:nether_quartz_seeds", 1, "Quartz farm."),
        ("Glowstone Seeds", "mysticalagriculture:glowstone_seeds", 1, "Light farm."),
        ("Netherite Seeds", "mysticalagriculture:netherite_seeds", 1, "Peak metal farm."),
        ("Amethyst Seeds", "mysticalagriculture:amethyst_seeds", 1, "Shard farm."),
        ("Honey Seeds", "mysticalagriculture:honey_seeds", 1, "Sweet farm."),
        ("Prismarine Seeds", "mysticalagriculture:prismarine_seeds", 1, "Sea farm."),
        ("Basalt Seeds", "mysticalagriculture:basalt_seeds", 1, "Column farm."),
        ("Nether Seeds", "mysticalagriculture:nether_seeds", 1, "Hell farm."),
        ("End Seeds", "mysticalagriculture:end_seeds", 1, "Pale farm."),
        ("Sky Stone Seeds", "mysticalagriculture:sky_stone_seeds", 1, "AE stone farm."),
        ("Certus Seeds", "mysticalagriculture:certus_quartz_seeds", 1, "Certus farm."),
        ("Fluix Seeds", "mysticalagriculture:fluix_seeds", 1, "Fluix farm."),
        ("Silicon Seeds", "mysticalagriculture:silicon_seeds", 1, "Chip farm."),
        ("Steel Seeds", "mysticalagriculture:steel_seeds", 1, "Steel farm."),
        ("Osmium Seeds", "mysticalagriculture:osmium_seeds", 1, "Osmium farm."),
        ("Tin Seeds", "mysticalagriculture:tin_seeds", 1, "Tin farm."),
        ("Aluminum Seeds", "mysticalagriculture:aluminum_seeds", 1, "Alu farm."),
        ("Uranium Seeds", "mysticalagriculture:uranium_seeds", 1, "Hot farm."),
        ("Uraninite Seeds", "mysticalagriculture:uraninite_seeds", 1, "Powah farm."),
        ("Experience Seeds", "mysticalagriculture:experience_seeds", 1, "Experience farm setup."),
        ("Slime Seeds", "mysticalagriculture:slime_seeds", 1, "Slime farm."),
        ("Blaze Seeds", "mysticalagriculture:blaze_seeds", 1, "Rod farm."),
        ("Ghast Seeds", "mysticalagriculture:ghast_seeds", 1, "Tear farm."),
        ("Enderman Seeds", "mysticalagriculture:enderman_seeds", 1, "Pearl farm."),
        ("Wither Skel Seeds", "mysticalagriculture:wither_skeleton_seeds", 1, "Skull farm."),
        ("Cow Seeds", "mysticalagriculture:cow_seeds", 1, "Leather farm."),
        ("Sheep Seeds", "mysticalagriculture:sheep_seeds", 1, "Wool farm."),
        ("Chicken Seeds", "mysticalagriculture:chicken_seeds", 1, "Feather farm."),
        ("Pig Seeds", "mysticalagriculture:pig_seeds", 1, "Pork farm."),
        ("Skeleton Seeds", "mysticalagriculture:skeleton_seeds", 1, "Bone farm."),
        ("Zombie Seeds", "mysticalagriculture:zombie_seeds", 1, "Flesh farm."),
        ("Creeper Seeds", "mysticalagriculture:creeper_seeds", 1, "Powder farm."),
        ("Iron Essence", "mysticalagriculture:iron_essence", 32, "Metal leaves."),
        ("Gold Essence", "mysticalagriculture:gold_essence", 16, "Gilded leaves."),
        ("Diamond Essence", "mysticalagriculture:diamond_essence", 8, "Hard leaves."),
        ("Coal Essence", "mysticalagriculture:coal_essence", 32, "Fuel leaves."),
        ("Copper Essence", "mysticalagriculture:copper_essence", 32, "Copper leaves."),
        ("Redstone Essence", "mysticalagriculture:redstone_essence", 32, "Dust leaves."),
    ]
    return main + grid_optional(s, seeds, origin=(-5.0, 7.5), cols=6)


def build_bees_side() -> list[dict]:
    s = 25
    main = chain(s, [
        ("Nest Locator", "productivebees:nest_locator", 1, "Points at nests you placed and forgot about."),
        ("Ring of Birch", "productivebees:birch_wood_nest", 1, "Birch logs around a flower: carpenter bees of a different colour."),
        ("Ring of Spruce", "productivebees:spruce_wood_nest", 1, "Spruce around a flower: resin bees."),
        ("Ring of Dark Oak", "productivebees:dark_oak_wood_nest", 1, "Dark oak around a flower: blue-banded bees."),
        ("Ring of Glowstone", "productivebees:glowstone_nest", 1, "Glowstone around a flower: bees that light up."),
        ("Ring of Quartz", "productivebees:nether_quartz_nest", 1, "Quartz around a flower: crystalline bees, the root of the ore lines."),
        ("Ring of Nether Brick", "productivebees:nether_brick_nest", 1, "Nether bricks around a flower: magmatic."),
        ("Ring of Soul Sand", "productivebees:soul_sand_nest", 1, "Soul sand around a flower: ghostly."),
        ("Ring of End Stone", "productivebees:end_stone_nest", 1, "End stone around a flower: ender bees, and the far end of breeding."),
        ("Ring of Obsidian", "productivebees:obsidian_nest", 1, "Obsidian around a flower: draconic. Do not ask what it eats."),
        ("Advanced Oak Hive", "productivebees:advanced_oak_beehive", 1, "Serious swarm home."),
        ("Expansion Box", "productivebees:expansion_box_oak", 2, "More bee rooms."),
        ("Jar Oak", "productivebees:jar_oak", 1, "Catch and keep."),
        ("Bee Cage", "productivebees:bee_cage", 4, "Cage bees for moving hives."),
        ("Sturdy Cage", "productivebees:sturdy_bee_cage", 2, "Tough transport."),
        ("Catcher", "productivebees:catcher", 1, "Auto scoop."),
        ("Feeder", "productivebees:feeder", 1, "Keep them fed."),
        ("Bottler", "productivebees:bottler", 1, "Bottle the sweet."),
        ("Centrifuge", "productivebees:centrifuge", 1, "Spin the comb."),
        ("Powered Centrifuge", "productivebees:powered_centrifuge", 1, "Powered spin."),
        ("Heated Centrifuge", "productivebees:heated_centrifuge", 1, "Hot spin."),
        ("Incubator", "productivebees:incubator", 1, "Hatch genes."),
        ("Breeding Chamber", "productivebees:breeding_chamber", 1, "Pair the swarm."),
        ("Gene Indexer", "productivebees:gene_indexer", 1, "Catalog traits."),
        ("Honey Generator", "productivebees:honey_generator", 1, "Sweet power."),
        ("Honey Treat", "productivebees:honey_treat", 16, "Bee snacks."),
        ("Honey Bucket", "productivebees:honey_bucket", 4, "Bulk sweet."),
        ("Wax Stock", "productivebees:wax", 32, "Build and seal."),
        ("Configurable Comb", "productivebees:configurable_honeycomb", 16, "Custom comb."),
        ("Gene Sample", "productivebees:gene", 4, "Trait bottle prep."),
        ("Gene Bottle", "productivebees:gene_bottle", 2, "Stored trait."),
        ("Honeycomb Block", "minecraft:honeycomb_block", 8, "Solid sweet."),
        ("Honey Block", "minecraft:honey_block", 8, "Sticky pad."),
        ("Beehive Vanilla", "minecraft:beehive", 2, "Simple home."),
        ("Campfire Under", "minecraft:campfire", 1, "Calm harvest."),
        ("Flower Carpet", "minecraft:poppy", 16, "Flowers for bee work."),
        ("Dandelion Field", "minecraft:dandelion", 16, "More pollen."),
        ("Azalea Bloom", "minecraft:flowering_azalea", 4, "Fancy flowers."),
        ("Chorus Snack", "minecraft:chorus_fruit", 8, "End pollen bait."),
        ("Obsidian Treat", "minecraft:obsidian", 4, "Tough bee bait."),
    ])
    side = grid_optional(s, [
        ("Birch Expansion", "productivebees:expansion_box_birch", 1, "Birch rooms."),
        ("Spruce Expansion", "productivebees:expansion_box_spruce", 1, "Spruce rooms."),
        ("Dark Oak Expansion", "productivebees:expansion_box_dark_oak", 1, "Dark rooms."),
        ("Acacia Expansion", "productivebees:expansion_box_acacia", 1, "Acacia rooms."),
        ("Jungle Expansion", "productivebees:expansion_box_jungle", 1, "Jungle rooms."),
        ("Cherry Expansion", "productivebees:expansion_box_cherry", 1, "Cherry rooms."),
        ("Crimson Expansion", "productivebees:expansion_box_crimson", 1, "Crimson rooms."),
        ("Warped Expansion", "productivebees:expansion_box_warped", 1, "Warped rooms."),
        ("Bamboo Expansion", "productivebees:expansion_box_bamboo", 1, "Bamboo rooms."),
        ("Mangrove Expansion", "productivebees:expansion_box_mangrove", 1, "Mangrove rooms."),
        ("Honey Bottle Stock", "minecraft:honey_bottle", 16, "Drinkable."),
        ("Sugar Stock", "minecraft:sugar", 32, "Treat craft."),
        ("Glass Bottle Stock", "minecraft:glass_bottle", 32, "Empty bottles."),
        ("Shears Spare", "minecraft:shears", 1, "Comb cut."),
    ], origin=(-4.0, 7.5), cols=6)
    return main + side


def build_pipes_side() -> list[dict]:
    s = 26
    return chain(s, [
        ("Item Pipe", "pipez:item_pipe", 16, "Move stacks."),
        ("Fluid Pipe", "pipez:fluid_pipe", 16, "Move liquids."),
        ("Energy Pipe", "pipez:energy_pipe", 16, "Move power."),
        ("Gas Pipe", "pipez:gas_pipe", 8, "Move chemicals."),
        ("Universal Pipe", "pipez:universal_pipe", 8, "One pipe, many jobs."),
        ("Pipe Wrench", "pipez:wrench", 1, "Configure."),
        ("Basic Upgrade", "pipez:basic_upgrade", 4, "Speed upgrade for machines."),
        ("Improved Upgrade", "pipez:improved_upgrade", 4, "Faster still."),
        ("Advanced Upgrade", "pipez:advanced_upgrade", 2, "Serious speed."),
        ("Ultimate Upgrade", "pipez:ultimate_upgrade", 1, "Top Pipez throughput tier."),
        ("Infinity Upgrade", "pipez:infinity_upgrade", 1, "Remove Pipez rate caps."),
        ("Filter Tool", "pipez:filter_destination_tool", 1, "Route smart."),
        ("Hopper Spare", "minecraft:hopper", 16, "Vanilla move."),
        ("Dropper Line", "minecraft:dropper", 8, "Dropper line for logistics."),
        ("Dispenser Line", "minecraft:dispenser", 4, "Automate a right-click."),
        ("Comparator", "minecraft:comparator", 8, "Read stacks."),
        ("Observer Line", "minecraft:observer", 8, "Observer reads the beat."),
        ("Redstone Torch", "minecraft:redstone_torch", 16, "Redstone signal line."),
        ("Repeater", "minecraft:repeater", 16, "Repeater times the circuit."),
        ("Target Block", "minecraft:target", 4, "Analog catch."),
        ("Daylight Detector", "minecraft:daylight_detector", 2, "Sky signal."),
        ("Lectern", "minecraft:lectern", 1, "Book signal."),
        ("Trapped Chest", "minecraft:trapped_chest", 2, "Open signal."),
        ("Create Funnel", "create:andesite_funnel", 8, "Belt insert."),
        ("Brass Funnel", "create:brass_funnel", 4, "Filtered insert."),
        ("Chute", "create:chute", 8, "Drop down."),
        ("Smart Chute", "create:smart_chute", 4, "Smart drop."),
        ("Mek Logistical", "mekanism:basic_logistical_transporter", 16, "Mek items."),
        ("Mek Pipe", "mekanism:basic_mechanical_pipe", 16, "Mek fluids."),
        ("Mek Cable", "mekanism:basic_universal_cable", 16, "Mek power."),
        ("Mek Tube", "mekanism:basic_pressurized_tube", 8, "Mekanism gas handling."),
        ("Adv Transporter", "mekanism:advanced_logistical_transporter", 8, "Faster Mek items."),
        ("Elite Transporter", "mekanism:elite_logistical_transporter", 4, "Elite items."),
        ("Ult Transporter", "mekanism:ultimate_logistical_transporter", 2, "Ultimate items."),
        ("Ult Cable", "mekanism:ultimate_universal_cable", 4, "Ultimate power."),
    ])


def build_occult_side() -> list[dict]:
    s = 27
    main = chain(s, [
        ("Dictionary of Spirits", "occultism:dictionary_of_spirits", 1, "Read the otherworld."),
        ("Spirit Fire", "occultism:spirit_fire", 1, "Purple flame."),
        ("Divination Rod", "occultism:divination_rod", 1, "Find the other."),
        ("Brush", "occultism:brush", 1, "Clear chalk."),
        ("Otherworld Sapling", "occultism:otherworld_sapling", 1, "Strange wood."),
        ("Otherworld Log", "occultism:otherworld_log", 16, "Ritual timber."),
        ("Sacrificial Bowl", "occultism:sacrificial_bowl", 1, "Offerings."),
        ("Golden Bowl", "occultism:golden_sacrificial_bowl", 1, "Gilded offerings."),
        ("Empty Binding Book", "occultism:book_of_binding_empty", 1, "Blank contract."),
        ("Foliot Book", "occultism:book_of_binding_foliot", 1, "Least spirit."),
        ("Djinni Book", "occultism:book_of_binding_djinni", 1, "Mid spirit."),
        ("Afrit Book", "occultism:book_of_binding_afrit", 1, "Fierce spirit."),
        ("Marid Book", "occultism:book_of_binding_marid", 1, "Great spirit."),
        ("Spirit Attuned Gem", "occultism:spirit_attuned_gem", 4, "Gem focus."),
        ("Raw Iesnium", "occultism:raw_iesnium", 8, "Otherworld ore."),
        ("Iesnium Ingot", "occultism:iesnium_ingot", 8, "Spirit metal."),
        ("Dimensional Mineshaft", "occultism:dimensional_mineshaft", 1, "Send miners out."),
        ("Foliot Miner", "occultism:miner_foliot_unspecialized", 1, "First miner."),
        ("Storage Controller", "occultism:storage_controller", 1, "Spirit warehouse."),
        ("Amethyst Focus", "minecraft:amethyst_shard", 16, "Purple bait."),
        ("Gold Ingot Stock", "minecraft:gold_ingot", 16, "Bowl metal."),
        ("Book Stock", "minecraft:book", 8, "Binding pages."),
        ("Purple Dye", "minecraft:purple_dye", 16, "Chalk color."),
        ("White Dye", "minecraft:white_dye", 16, "Chalk color."),
        ("Black Dye", "minecraft:black_dye", 8, "Chalk color."),
        ("Soul Sand Stock", "minecraft:soul_sand", 16, "Ritual grit."),
        ("Netherrack Stock", "minecraft:netherrack", 32, "Hell base."),
        ("Obsidian Stock", "minecraft:obsidian", 16, "Dark frame."),
        ("Ender Pearl Stock", "minecraft:ender_pearl", 16, "Teleport bait."),
        ("Diamond Stock", "minecraft:diamond", 8, "High offering."),
    ])
    side = grid_optional(s, [
        ("Bound Foliot Book", "occultism:book_of_binding_bound_foliot", 1, "Filled contract."),
        ("Bound Djinni Book", "occultism:book_of_binding_bound_djinni", 1, "Filled mid."),
        ("Bound Afrit Book", "occultism:book_of_binding_bound_afrit", 1, "Filled fierce."),
        ("Bound Marid Book", "occultism:book_of_binding_bound_marid", 1, "Filled great."),
        ("Iesnium Ore", "occultism:iesnium_ore", 4, "Vein sample."),
        ("Miner Afrit Deeps", "occultism:miner_afrit_deeps", 1, "Deep miner."),
    ], origin=(-3.0, 7.5), cols=6)
    return main + side


def build_factory_side() -> list[dict]:
    s = 28
    main = chain(s, [
        ("Hand Crank", "create:hand_crank", 1, "Manual spin."),
        ("Shaft Stock", "create:shaft", 32, "Rotation spine."),
        ("Cogwheel Stock", "create:cogwheel", 32, "Cogwheel bites the shaft."),
        ("Large Cog", "create:large_cogwheel", 16, "Big teeth."),
        ("Gearbox", "create:gearbox", 4, "Turn the corner."),
        ("Clutch", "create:clutch", 2, "Engage a machine mode."),
        ("Gearshift", "create:gearshift", 2, "Gearshift flips rotation."),
        ("Chain Drive", "create:encased_chain_drive", 4, "Chain power."),
        ("Adj Chain", "create:adjustable_chain_gearshift", 2, "Tuned chain."),
        ("Water Wheel", "create:water_wheel", 2, "River power."),
        ("Large Wheel", "create:large_water_wheel", 1, "River torque."),
        ("Windmill Bearing", "create:windmill_bearing", 1, "Sky spin."),
        ("Mechanical Bearing", "create:mechanical_bearing", 1, "Rotate structure."),
        ("Clockwork Bearing", "create:clockwork_bearing", 1, "Timed rotate."),
        ("Steam Engine", "create:steam_engine", 1, "Boiler power."),
        ("Steam Whistle", "create:steam_whistle", 1, "Announce."),
        ("Blaze Burner", "create:blaze_burner", 2, "Hot craft."),
        ("Basin", "create:basin", 2, "Mix bowl."),
        ("Mechanical Mixer", "create:mechanical_mixer", 1, "Mix bulk recipes fast."),
        ("Mechanical Press", "create:mechanical_press", 1, "Smash blocks for grit."),
        ("Millstone", "create:millstone", 1, "Grindstone or mill work."),
        ("Crushing Wheel", "create:crushing_wheel", 2, "Pair crush."),
        ("Encased Fan", "create:encased_fan", 2, "Fan for washing and drying."),
        ("Whisk", "create:whisk", 1, "Mixer tool."),
        ("Propeller", "create:propeller", 2, "Fan blade."),
        ("Depot", "create:depot", 4, "Hold one."),
        ("Belt", "create:belt_connector", 16, "Move along."),
        ("Andesite Funnel", "create:andesite_funnel", 8, "In and out."),
        ("Brass Funnel", "create:brass_funnel", 4, "Filtered."),
        ("Chute Line", "create:chute", 8, "Vertical."),
        ("Smart Chute", "create:smart_chute", 4, "Smart vertical."),
        ("Fluid Pipe", "create:fluid_pipe", 16, "Liquid line."),
        ("Smart Fluid Pipe", "create:smart_fluid_pipe", 4, "Smart liquid."),
        ("Mechanical Pump", "create:mechanical_pump", 2, "Push liquid."),
        ("Hose Pulley", "create:hose_pulley", 1, "Pump fluids from a source."),
        ("Spout", "create:spout", 2, "Fill items."),
        ("Item Drain", "create:item_drain", 2, "Empty items."),
        ("Fluid Tank", "create:fluid_tank", 8, "Hold liquid."),
        ("Item Vault", "create:item_vault", 4, "Bulk items."),
        ("Portable Storage", "create:portable_storage_interface", 2, "Train items."),
        ("Portable Fluid", "create:portable_fluid_interface", 2, "Train fluid."),
        ("Precision Mech", "create:precision_mechanism", 2, "Brass brain."),
        ("Electron Tube", "create:electron_tube", 8, "Logic light."),
        ("Brass Hand", "create:brass_hand", 1, "Deployer hand."),
        ("Mechanical Arm", "create:mechanical_arm", 1, "Pick and place."),
        ("Speed Controller", "create:rotation_speed_controller", 1, "Tune RPM."),
        ("Sequenced Gearshift", "create:sequenced_gearshift", 1, "Program rotate."),
        ("Redstone Link", "create:redstone_link", 4, "Wireless signal."),
        ("Stockpile Switch", "create:stockpile_switch", 2, "Inventory signal."),
        ("Content Observer", "create:content_observer", 2, "Watch contents."),
        ("Nixie Tube", "create:nixie_tube", 4, "Display digits."),
        ("Display Board", "create:display_board", 2, "Show text."),
        ("Factory Gauge", "create:factory_gauge", 2, "Factory meter."),
        ("Packager", "create:packager", 1, "Box items for shipping."),
        ("Repackager", "create:repackager", 1, "Repackage storage drawers."),
        ("Stock Ticker", "create:stock_ticker", 1, "Request stock."),
        ("Track", "create:track", 32, "Train path."),
        ("Track Station", "create:track_station", 1, "Stop here."),
        ("Schedule", "create:schedule", 1, "Train plan."),
        ("Cart Assembler", "create:cart_assembler", 1, "Assemble cart."),
        ("Controller Rail", "create:controller_rail", 8, "Powered rail+."),
        ("Rope Pulley", "create:rope_pulley", 1, "Rope pulley for vertical move."),
        ("Elevator Pulley", "create:elevator_pulley", 1, "Floor lift."),
        ("Gantry Shaft", "create:gantry_shaft", 8, "Gantry spine."),
        ("Gantry Carriage", "create:gantry_carriage", 1, "Gantry ride."),
    ])
    return main


def build_network_side() -> list[dict]:
    s = 29
    main = chain(s, [
        ("Certus Crystal", "ae2:certus_quartz_crystal", 32, "Network quartz."),
        ("Charged Certus", "ae2:charged_certus_quartz_crystal", 16, "Charged energy cell."),
        ("Fluix Crystal", "ae2:fluix_crystal", 32, "Purple network."),
        ("Fluix Dust", "ae2:fluix_dust", 16, "Dusted fluix."),
        ("Silicon", "ae2:silicon", 32, "Chip base."),
        ("Sky Stone", "ae2:sky_stone_block", 32, "Meteor stone."),
        ("Smooth Sky Stone", "ae2:smooth_sky_stone_block", 16, "Controller shell."),
        ("Press the Pattern", "ae2:inscriber", 1, "The inscriber presses circuits the way a loom presses cloth."),
        ("Charger", "ae2:charger", 1, "Charge certus."),
        ("Printed Calc", "ae2:printed_calculation_processor", 8, "Calc print."),
        ("Printed Logic", "ae2:printed_logic_processor", 8, "Logic print."),
        ("Printed Eng", "ae2:printed_engineering_processor", 8, "Eng print."),
        ("Calc Processor", "ae2:calculation_processor", 8, "Calc chip."),
        ("Logic Processor", "ae2:logic_processor", 8, "Logic chip."),
        ("Eng Processor", "ae2:engineering_processor", 8, "Eng chip."),
        ("Fluix Glass Cable", "ae2:fluix_glass_cable", 32, "See the net."),
        ("Fluix Covered", "ae2:fluix_covered_cable", 16, "Covered net."),
        ("Fluix Smart", "ae2:fluix_smart_cable", 16, "Smart net."),
        ("Energy Acceptor", "ae2:energy_acceptor", 1, "Power in."),
        ("Energy Cell", "ae2:energy_cell", 2, "Buffer energy or items."),
        ("Dense Energy", "ae2:dense_energy_cell", 1, "Big buffer."),
        ("Controller", "ae2:controller", 1, "Network heart."),
        ("Drive", "ae2:drive", 2, "Cell bay."),
        ("1k Component", "ae2:cell_component_1k", 4, "Tiny cell."),
        ("4k Component", "ae2:cell_component_4k", 4, "Small cell."),
        ("16k Component", "ae2:cell_component_16k", 2, "Mid cell."),
        ("64k Component", "ae2:cell_component_64k", 2, "Large cell."),
        ("256k Component", "ae2:cell_component_256k", 1, "Huge cell."),
        ("1k Item Cell", "ae2:item_storage_cell_1k", 2, "Store items."),
        ("4k Item Cell", "ae2:item_storage_cell_4k", 2, "More items."),
        ("16k Item Cell", "ae2:item_storage_cell_16k", 1, "Lots of items."),
        ("64k Item Cell", "ae2:item_storage_cell_64k", 1, "Massive items."),
        ("256k Item Cell", "ae2:item_storage_cell_256k", 1, "Archive pages and notes."),
        ("1k Fluid Cell", "ae2:fluid_storage_cell_1k", 1, "Store fluids."),
        ("Interface", "ae2:interface", 2, "World bridge."),
        ("Import Bus", "ae2:import_bus", 4, "Pull items into storage."),
        ("Export Bus", "ae2:export_bus", 4, "Push out."),
        ("Storage Bus", "ae2:storage_bus", 4, "Attach inventory."),
        ("Terminal", "ae2:terminal", 1, "Browse networked storage."),
        ("Crafting Terminal", "ae2:crafting_terminal", 1, "Craft from net."),
        ("Pattern Encode", "ae2:pattern_encoding_terminal", 1, "Write patterns."),
        ("Pattern Access", "ae2:pattern_access_terminal", 1, "View patterns."),
        ("Pattern Provider", "ae2:pattern_provider", 2, "Auto craft out."),
        ("Molecular Assembler", "ae2:molecular_assembler", 2, "Craft machine."),
        ("Crafting Unit", "ae2:crafting_unit", 4, "CPU brick."),
        ("Crafting Accel", "ae2:crafting_accelerator", 2, "Faster CPU."),
        ("1k Craft Storage", "ae2:1k_crafting_storage", 2, "CPU memory."),
        ("4k Craft Storage", "ae2:4k_crafting_storage", 1, "More CPU mem."),
        ("16k Craft Storage", "ae2:16k_crafting_storage", 1, "Big CPU mem."),
        ("64k Craft Storage", "ae2:64k_crafting_storage", 1, "Huge CPU mem."),
        ("256k Craft Storage", "ae2:256k_crafting_storage", 1, "Archive CPU."),
        ("Level Emitter", "ae2:level_emitter", 2, "Stock signal."),
        ("Formation Plane", "ae2:formation_plane", 1, "Place blocks."),
        ("Annihilation Plane", "ae2:annihilation_plane", 1, "Break blocks."),
        ("P2P Tunnel", "ae2:me_p2p_tunnel", 2, "Channel tunnel."),
        ("Spatial 2", "ae2:spatial_storage_cell_2", 1, "Pocket space."),
        ("Wireless Terminal", "ae2:wireless_terminal", 1, "Pocket browse."),
        ("Wireless Craft", "ae2:wireless_crafting_terminal", 1, "Pocket craft."),
        ("Matter Cannon", "ae2:matter_cannon", 1, "Shoot matter."),
        ("Quartz Glass", "ae2:quartz_glass", 16, "Network glass."),
        ("Quartz Vibrant", "ae2:quartz_vibrant_glass", 8, "Bright glass."),
        ("Fluix Block", "ae2:fluix_block", 8, "Solid fluix."),
        ("Cell Workbench", "ae2:cell_workbench", 1, "Partition cells."),
    ])
    return main


def build_voidcraft_side() -> list[dict]:
    s = 30
    main = chain(s, [
        ("Porcelain Clay", "exdeorum:porcelain_clay_ball", 32, "White clay."),
        ("Porcelain Bucket", "exdeorum:porcelain_bucket", 1, "Clay bucket."),
        ("Porcelain Crucible", "exdeorum:porcelain_crucible", 1, "Hot porcelain."),
        ("String Mesh", "exdeorum:string_mesh", 1, "Vanilla mesh."),
        ("Flint Mesh", "exdeorum:flint_mesh", 1, "Better mesh."),
        ("Iron Mesh", "exdeorum:iron_mesh", 1, "Metal mesh."),
        ("Golden Mesh", "exdeorum:golden_mesh", 1, "Lucky mesh."),
        ("Diamond Mesh", "exdeorum:diamond_mesh", 1, "Hard mesh."),
        ("Netherite Mesh", "exdeorum:netherite_mesh", 1, "Peak mesh."),
        ("Void Yarn Stock", "voidloom:void_yarn", 32, "Pack yarn."),
        ("Binding Knot Stock", "voidloom:binding_knot", 8, "Gate knots."),
        ("Thread Mesh String", "voidloom:thread_mesh_string", 2, "Pack string mesh."),
        ("Thread Mesh Flint", "voidloom:thread_mesh_flint", 2, "Pack flint mesh."),
        ("Thread Mesh Iron", "voidloom:thread_mesh_iron", 2, "Pack iron mesh."),
        ("Spindle Hammer", "voidloom:spindle_hammer", 1, "Pack hammer."),
        ("Spindle Crook", "voidloom:spindle_crook", 1, "Pack crook."),
        ("Loomframe", "voidloom:loomframe", 2, "Station mark."),
        ("Tension Barrel", "voidloom:tension_barrel", 2, "Hold strain."),
        ("Compressed Dirt", "exdeorum:compressed_dirt", 16, "Dense dirt."),
        ("Compressed Cobble", "exdeorum:compressed_cobblestone", 32, "Dense stone."),
        ("Compressed Gravel", "exdeorum:compressed_gravel", 32, "Dense gravel."),
        ("Compressed Sand", "exdeorum:compressed_sand", 32, "Dense sand."),
        ("Compressed Dust", "exdeorum:compressed_dust", 16, "Dense dust."),
        ("Compressed Netherrack", "exdeorum:compressed_netherrack", 16, "Dense hell."),
        ("Compressed End Stone", "exdeorum:compressed_end_stone", 8, "Dense end."),
        ("Compressed Deepslate", "exdeorum:compressed_deepslate", 16, "Dense deep."),
        ("Compressed Hammer", "exdeorum:compressed_diamond_hammer", 1, "Smash piles."),
        ("Compressed Iron Hammer", "exdeorum:compressed_iron_hammer", 1, "Mid smash."),
        ("Compressed Sieve", "exdeorum:oak_compressed_sieve", 2, "Wide sieve."),
        ("Birch Sieve", "exdeorum:birch_sieve", 1, "Alt wood sieve."),
        ("Birch Barrel", "exdeorum:birch_barrel", 1, "Alt barrel."),
        ("Birch Crucible", "exdeorum:birch_crucible", 1, "Alt crucible."),
        ("Frayed Thread Stock", "ninjacatskies:frayed_thread", 64, "Currency pile."),
        ("Codex Pages", "ninjacatskies:codex_page", 16, "Archive pages and notes."),
        ("Whisker Codex", "ninjacatskies:whisker_codex", 1, "Always assign."),
    ])
    return main


def build_packaged_side() -> list[dict]:
    s = 31
    return chain(s, [
        ("Package Component", "packagedauto:package_component", 8, "Box guts."),
        ("ME Package Comp", "packagedauto:me_package_component", 4, "AE box guts."),
        ("Packager", "packagedauto:packager", 1, "Make packages."),
        ("Packager Ext", "packagedauto:packager_extension", 2, "Extend packing."),
        ("Unpackager", "packagedauto:unpackager", 1, "Open packages."),
        ("Encoder", "packagedauto:encoder", 1, "Encode recipes."),
        ("Crafter", "packagedauto:crafter", 1, "Craft packages."),
        ("Distributor", "packagedauto:distributor", 1, "Route packages."),
        ("Distributor Marker", "packagedauto:distributor_marker", 4, "Mark routes."),
        ("Packaging Provider", "packagedauto:packaging_provider", 1, "Provide packs."),
        ("Crafting Proxy", "packagedauto:crafting_proxy", 1, "Proxy craft."),
        ("Recipe Holder", "packagedauto:recipe_holder", 4, "Hold recipes."),
        ("Settings Cloner", "packagedauto:settings_cloner", 1, "Copy settings."),
        ("Fluid Package Filler", "packagedauto:fluid_package_filler", 1, "Fill fluids."),
        ("Package Item", "packagedauto:package", 8, "A package."),
        ("Volume Package", "packagedauto:volume_package", 4, "Bulk package."),
        ("Proxy Marker", "packagedauto:proxy_marker", 4, "Proxy marks."),
        ("AE Interface", "ae2:interface", 2, "Bridge AE."),
        ("Pattern Provider", "ae2:pattern_provider", 2, "AE patterns."),
        ("Molecular Assembler", "ae2:molecular_assembler", 2, "AE craft."),
        ("ME Controller", "ae2:controller", 1, "Need a net."),
        ("Fluix Cable", "ae2:fluix_glass_cable", 16, "Wire power or signals."),
        ("Create Packager", "create:packager", 1, "Factory boxes."),
        ("Create Repackager", "create:repackager", 1, "Factory rebox."),
        ("Stock Ticker", "create:stock_ticker", 1, "Request lines."),
        ("Item Vault", "create:item_vault", 4, "Bulk buffer."),
    ])


def build_qio_side() -> list[dict]:
    s = 32
    return chain(s, [
        ("QIO Drive Base", "mekanism:qio_drive_base", 2, "Quantum disk."),
        ("QIO Hyper Dense", "mekanism:qio_drive_hyper_dense", 1, "Denser disk."),
        ("QIO Time Dilating", "mekanism:qio_drive_time_dilating", 1, "Warped disk."),
        ("QIO Supermassive", "mekanism:qio_drive_supermassive", 1, "Peak disk."),
        ("QIO Drive Array", "mekanism:qio_drive_array", 1, "Disk bay."),
        ("QIO Dashboard", "mekanism:qio_dashboard", 1, "Browse QIO."),
        ("Portable QIO", "mekanism:portable_qio_dashboard", 1, "Pocket QIO."),
        ("Steel Casing", "mekanism:steel_casing", 16, "Machine shell."),
        ("Ultimate Cube", "mekanism:ultimate_energy_cube", 1, "Big power."),
        ("Ultimate Bin", "mekanism:ultimate_bin", 2, "Huge bin."),
        ("Ult Smelt Factory", "mekanism:ultimate_smelting_factory", 1, "Peak smelt."),
        ("Ult Enrich Factory", "mekanism:ultimate_enriching_factory", 1, "Peak enrich."),
        ("Ult Crush Factory", "mekanism:ultimate_crushing_factory", 1, "Peak crush."),
        ("Digital Miner", "mekanism:digital_miner", 1, "Auto mine void."),
        ("Atomic Disassembler", "mekanism:atomic_disassembler", 1, "Swiss army claw."),
        ("Configurator", "mekanism:configurator", 1, "Configure Mek."),
        ("Teleporter", "mekanism:teleporter", 1, "Pad jump."),
        ("Teleporter Frame", "mekanism:teleporter_frame", 16, "Frame the jump."),
        ("SPS Casing", "mekanism:sps_casing", 8, "Supercritical."),
        ("SPS Port", "mekanism:sps_port", 2, "SPS input/output ports."),
        ("Supercharged Coil", "mekanism:supercharged_coil", 1, "Coil power."),
        ("Isotopic Centrifuge", "mekanism:isotopic_centrifuge", 1, "Spin isotopes."),
        ("Chem Dissolution", "mekanism:chemical_dissolution_chamber", 1, "Dissolve."),
        ("Chem Washer", "mekanism:chemical_washer", 1, "Wash chem."),
        ("Chem Crystallizer", "mekanism:chemical_crystallizer", 1, "Crystalize."),
        ("Solar Neutron", "mekanism:solar_neutron_activator", 1, "Sun neutrons."),
        ("Resistive Heater", "mekanism:resistive_heater", 1, "Electric heat."),
        ("Fuelwood Heater", "mekanism:fuelwood_heater", 1, "Burn heat."),
        ("Antiprotonic", "mekanism:antiprotonic_nucleosynthesizer", 1, "Late nucleosynth."),
        ("Meka Tool", "mekanism:meka_tool", 1, "Modular tool."),
        ("Meka Helmet", "mekanism:mekasuit_helmet", 1, "Suit head."),
        ("Meka Body", "mekanism:mekasuit_bodyarmor", 1, "Suit chest."),
        ("Meka Pants", "mekanism:mekasuit_pants", 1, "Suit legs."),
        ("Meka Boots", "mekanism:mekasuit_boots", 1, "Suit feet."),
        ("Boiler Casing", "mekanism:boiler_casing", 16, "Steam shell."),
        ("Elite Energy Cube", "mekanism:elite_energy_cube", 2, "Elite power."),
        ("Adv Energy Cube", "mekanism:advanced_energy_cube", 2, "Adv power."),
        ("Basic Energy Cube", "mekanism:basic_energy_cube", 2, "Basic power."),
        ("Metallurgic Infuser", "mekanism:metallurgic_infuser", 1, "Infuse metals."),
        ("Enrichment Chamber", "mekanism:enrichment_chamber", 1, "Enrich materials further."),
        ("Crusher", "mekanism:crusher", 1, "Mill or crush bulk materials."),
        ("Energized Smelter", "mekanism:energized_smelter", 1, "Power smelt."),
        ("Precision Sawmill", "mekanism:precision_sawmill", 1, "Precision Create cutting."),
        ("Electrolytic Sep", "mekanism:electrolytic_separator", 1, "Split water."),
        ("Chemical Infuser", "mekanism:chemical_infuser", 1, "Mix chem."),
        ("Purification", "mekanism:purification_chamber", 1, "Purify fluids or ores."),
        ("Chem Injection", "mekanism:chemical_injection_chamber", 1, "Chemical injection chamber."),
        ("Osmium Compressor", "mekanism:osmium_compressor", 1, "Osmium compressor."),
        ("Combiner", "mekanism:combiner", 1, "Combine components."),
    ])


def build_mobfarm_side() -> list[dict]:
    s = 33
    main = chain(s, [
        ("Rotten Flesh Stock", "minecraft:rotten_flesh", 64, "Zombie tax."),
        ("Bone Stock", "minecraft:bone", 64, "Skeleton tax."),
        ("Gunpowder Stock", "minecraft:gunpowder", 64, "Creeper tax."),
        ("String Stock", "minecraft:string", 64, "Spider tax."),
        ("Spider Eye Stock", "minecraft:spider_eye", 32, "Brew bait."),
        ("Ender Pearl Farm", "minecraft:ender_pearl", 32, "Pearl farm."),
        ("Blaze Rod Farm", "minecraft:blaze_rod", 32, "Rod farm."),
        ("Ghast Tear Farm", "minecraft:ghast_tear", 8, "Tear farm."),
        ("Magma Cream Farm", "minecraft:magma_cream", 16, "Cream farm."),
        ("Slimeball Farm", "minecraft:slime_ball", 32, "Slime farm."),
        ("Wither Skull", "minecraft:wither_skeleton_skull", 3, "Boss bait trio."),
        ("Nether Star", "minecraft:nether_star", 1, "Boss tax."),
        ("Shulker Shell Farm", "minecraft:shulker_shell", 8, "Box shells."),
        ("Phantom Membrane", "minecraft:phantom_membrane", 8, "Repair elytra."),
        ("Ink Sac Farm", "minecraft:ink_sac", 32, "Squid tax."),
        ("Glow Ink", "minecraft:glow_ink_sac", 16, "Glow squid."),
        ("Prismarine Shard", "minecraft:prismarine_shard", 32, "Guardian tax."),
        ("Prismarine Crystal", "minecraft:prismarine_crystals", 16, "Sea light."),
        ("Heart of the Sea", "minecraft:heart_of_the_sea", 1, "Conduit core."),
        ("Nautilus Shell", "minecraft:nautilus_shell", 8, "Conduit ring."),
        ("Totem", "minecraft:totem_of_undying", 1, "Second life."),
        ("Iron Golem Gift", "minecraft:iron_ingot", 36, "Golem drops."),
        ("Snow Golem", "minecraft:snowball", 16, "Snowman ammo."),
        ("Arrow Farm", "minecraft:arrow", 64, "Skeleton ammo."),
        ("Spectral Arrow", "minecraft:spectral_arrow", 16, "Glow shot."),
        ("Saddle", "minecraft:saddle", 1, "Mount when you find a saddle."),
        ("Name Tag Farm", "minecraft:name_tag", 2, "Name them."),
        ("Lead", "minecraft:lead", 4, "Tether a link or cable."),
        ("Egg Stock", "minecraft:egg", 16, "Chicken tax."),
        ("Leather Stock", "minecraft:leather", 32, "Leather and beef stock."),
        ("Wool Stock", "minecraft:white_wool", 32, "Sheep tax."),
        ("Beef Stock", "minecraft:beef", 32, "Food stock for the kitchen."),
        ("Pork Stock", "minecraft:porkchop", 32, "More meat."),
        ("Chicken Stock", "minecraft:chicken", 32, "Chicken for meals and feathers."),
        ("Mutton Stock", "minecraft:mutton", 32, "Sheep meat."),
        ("Rabbit Hide", "minecraft:rabbit_hide", 8, "Small hide."),
        ("Rabbit Foot", "minecraft:rabbit_foot", 2, "Brew luck."),
    ])
    side = grid_optional(s, [
        ("Zombie Head", "minecraft:zombie_head", 1, "Dragon egg showpiece."),
        ("Skeleton Skull", "minecraft:skeleton_skull", 1, "Dragon egg showpiece."),
        ("Creeper Head", "minecraft:creeper_head", 1, "Dragon egg showpiece."),
        ("Piglin Head", "minecraft:piglin_head", 1, "Dragon egg showpiece."),
        ("Dragon Head", "minecraft:dragon_head", 1, "Dragon egg showpiece."),
        ("Player Head", "minecraft:player_head", 1, "If obtained."),
    ], origin=(-3.0, 7.5), cols=6)
    return main + side



def build_tribal_side() -> list[dict]:
    """Steward technomancy — Tribal Power side path born from the Loom."""
    s = 34
    # Jar order: chime → shard → copper (before Codex, which spends a Chime); chalk needs shard.
    main = chain(s, [
        ("Bone Chime", "tribalpower:bone_chime", 2, "First craft yields 2 — keep one for Codex later."),
        ("Spirit Shard", "tribalpower:spirit_shard", 2, "Shard of old tribe song — needs a Chime."),
        ("Copper Resonator", "tribalpower:copper_resonator", 1, "Tune metal to spirit — copper around a Chime."),
        ("Ritual Chalk", "tribalpower:ritual_chalk", 4, "Mark the lattice lines — chalk needs a Shard."),
        ("Drumheart Beat", "tribalpower:drumheart", 1, "Place the heart — Chime + Shard + leather (Desk sells leather)."),
        ("Spirit Codex", "tribalpower:spirit_codex", 1, "Nine tribes hummed once — needs a spare Chime + Shard."),
        ("Ley Collector", "tribalpower:ley_collector", 1, "Draw ley into beats."),
        ("Pulse Cell", "tribalpower:pulse_cell", 4, "Carry a measure of Pulse."),
        ("Pulse Resonator", "tribalpower:pulse_resonator", 1, "Burn coal for denser beats — feed lattice and cells."),
        ("Earth Totem", "tribalpower:resonance_totem_earth", 1, "Tribe of stone answers."),
        ("Fire Totem", "tribalpower:resonance_totem_fire", 1, "Tribe of flame answers."),
        ("Water Totem", "tribalpower:resonance_totem_water", 1, "Tribe of tide answers."),
        ("Air Totem", "tribalpower:resonance_totem_air", 1, "Tribe of wind answers."),
        ("Spirit Totem", "tribalpower:resonance_totem_spirit", 1, "Fifth tribe — steward core."),
        ("Song Bench", "tribalpower:song_bench", 1, "Start the lattice song."),
        ("Lattice Conductor", "tribalpower:lattice_conductor", 2, "Route harmonics between totems."),
        ("Echo Shatter", "tribalpower:echo_shatter", 1, "Hum stage one — break the ore."),
        ("Echo Shard", "tribalpower:echo_shard", 8, "Shard that heard the shatter."),
        ("Echo Attune", "tribalpower:echo_attune", 1, "Hum stage two — attune."),
        ("Attuned Echo", "tribalpower:attuned_echo", 8, "Echo that found a key."),
        ("Echo Bind", "tribalpower:echo_bind", 1, "Bind stage — knot spirit to metal."),
        ("Bound Echo", "tribalpower:bound_echo", 8, "Echo that will not slip."),
        ("Echo Manifest", "tribalpower:echo_manifest", 1, "Reweave stage — call the ingot."),
        ("Manifested Ingot", "tribalpower:manifested_ingot", 8, "Loom-born metal."),
        ("Ancestral Cache", "tribalpower:ancestral_cache", 1, "Keep what the tribes left."),
        ("Deep Cache", "tribalpower:deep_cache", 1, "Vault linked toward The March."),
        ("Blank Seal", "tribalpower:blank_seal", 4, "Unwritten rite token."),
        ("Earth Seal", "tribalpower:earth_seal", 1, "Seal of the stone tribe."),
        ("Fire Seal", "tribalpower:fire_seal", 1, "Seal of the flame tribe."),
        ("Water Seal", "tribalpower:water_seal", 1, "Seal of the tide tribe."),
        ("Air Seal", "tribalpower:air_seal", 1, "Seal of the wind tribe."),
        ("Spirit Seal", "tribalpower:spirit_seal", 1, "Seal of the steward tribe."),
        ("Rite Pedestal", "tribalpower:rite_pedestal", 1, "Offer seals. Ask the Loom."),
        ("Gate Drum", "tribalpower:gate_drum", 1, "Strike open The March."),
        ("Spirit Door", "tribalpower:spirit_door", 1, "Threshold for spirit traffic."),
        ("Spiritgear Pick", "tribalpower:spiritgear_pickaxe", 1, "Tool that spends Pulse."),
        ("Spiritgear Blade", "tribalpower:spiritgear_blade", 1, "Edge that spends Pulse."),
    ])
    side = grid_optional(s, [
        ("March Stone", "tribalpower:march_stone", 16, "Otherworld footing."),
        ("March Cobble", "tribalpower:march_cobble", 32, "March rubble."),
        ("March Log", "tribalpower:march_log", 16, "Wood from beyond."),
        ("March Planks", "tribalpower:march_planks", 32, "Sawn March timber."),
        ("March Leaf", "tribalpower:march_leaf", 16, "Whispering canopy."),
        ("Spirit Reed", "tribalpower:spirit_reed", 8, "Reed that hums."),
    ], origin=(-3.0, 7.5), cols=6)
    return main + side


def build_shop() -> list[dict]:
    """Frayed Thread Desk — spend Thread (consume) for QoL / alternate mats."""
    s = 16
    thread = "ninjacatskies:frayed_thread"
    # Unlock spine: spend Thread, receive useful mats (not Thread-for-Thread).
    main = chain(s, [
        ("Desk Deposit I", thread, 8, "The Desk opens. Saplings for the pad.", "minecraft:oak_sapling", 4, False, True),
        # Early bucket — Soft Soil water path before deep Desk spend.
        ("Buy Empty Bucket", thread, 8, "Fill from melted ice — Tension Barrel clay.", "minecraft:bucket", 1, False, True),
        ("Desk Deposit II", thread, 16, "Bone meal softens Root.", "minecraft:bone_meal", 16, False, True),
        ("Desk Deposit III", thread, 24, "Spare yarn for Recover.", "voidloom:void_yarn", 4, False, True),
        ("Buy String Mesh", thread, 12, "Catch grit without crafting the mesh.", "voidloom:thread_mesh_string", 1, False, True),
        ("Buy Spindle Crook", thread, 8, "Leaf work on demand.", "voidloom:spindle_crook", 1, False, True),
        ("Buy Dirt Bundle", thread, 10, "Expand the pad.", "minecraft:dirt", 32, False, True),
        ("Buy Cobble Bundle", thread, 10, "Stone for days.", "minecraft:cobblestone", 64, False, True),
        ("Buy Iron Starter", thread, 20, "Nuggets toward Edge.", "minecraft:iron_nugget", 27, False, True),
        ("Buy Slime Kit", thread, 16, "Knot binder stock.", "minecraft:slime_ball", 8, False, True),
        ("Buy Pearl Seed", thread, 28, "One pearl — yarn or teleport.", "minecraft:ender_pearl", 1, False, True),
        ("Buy Feather Pack", thread, 10, "Air totem / seal / arrows.", "minecraft:feather", 8, False, True),
        ("Buy Lapis Pack", thread, 14, "Ritual chalk fuel.", "minecraft:lapis_lazuli", 16, False, True),
        ("Buy Codex Page", thread, 8, "Margin note from the Desk.", "ninjacatskies:codex_page", 1, False, True),
        ("Buy Bread Line", thread, 12, "Hunger is a soft void.", "minecraft:bread", 16, False, True),
        ("Buy Torch Line", thread, 6, "See the edge.", "minecraft:torch", 32, False, True),
    ])
    # Optional side purchases — still consume Thread.
    side = grid_optional(s, [
        ("Buy XP Bottles", thread, 20, "Bottled practice.", "minecraft:experience_bottle", 8, True),
        ("Buy Emeralds", thread, 24, "Trade bait.", "minecraft:emerald", 8, True),
        ("Buy Diamonds", thread, 30, "Hard currency, two at a time.", "minecraft:diamond", 2, True),
        ("Buy Shulker", thread, 90, "A portable room. The End is cheaper if you can reach it.", "minecraft:shulker_box", 1, True),
        ("Buy Vault", thread, 40, "Bulk Create storage, two vaults.", "create:item_vault", 2, True),
        ("Buy Gold", thread, 18, "Gilded bits.", "minecraft:gold_ingot", 4, True),
        ("Buy Copper", thread, 14, "Wire and bulbs.", "minecraft:copper_ingot", 8, True),
        ("Buy Amethyst", thread, 22, "Sigil bait.", "minecraft:amethyst_shard", 4, True),
        ("Buy Leather", thread, 18, "Drumheart skin — Hum gate.", "minecraft:leather", 2, True),
        ("Buy Honeycomb", thread, 16, "Swarm bait.", "minecraft:honeycomb", 8, True),
        ("Buy Nether Wart", thread, 20, "Brew stock.", "minecraft:nether_wart", 8, True),
        ("Buy Chorus", thread, 26, "End grit snack.", "minecraft:chorus_fruit", 8, True),
        ("Buy Obsidian", thread, 30, "Portal thoughts.", "minecraft:obsidian", 4, True),
        ("Buy Beacon Frame", thread, 200, "A star for a Clowder monument. Two hundred Thread is a campaign, not a tip.", "minecraft:nether_star", 1, True),
    ], origin=(-3.0, 7.5), cols=6)
    # Desk buys are personal + repeatable Thread sinks (PLAYTHROUGH targets).
    shop = main + side
    for q in shop:
        q["repeatable"] = True
        for reward in q.get("rewards", []):
            reward["team_reward"] = False
    return shop


def write_lang():
    LANG.mkdir(parents=True, exist_ok=True)
    lines = ["{"]
    for k in sorted(lang.keys(), key=str):
        v = lang[k]
        if isinstance(v, list):
            arr = ",\n\t\t".join(json.dumps(x) for x in v)
            lines.append(f"\t{k}: [\n\t\t{arr}\n\t]")
        else:
            lines.append(f"\t{k}: {json.dumps(v)}")
    lines.append("}")
    (LANG / "en_us.snbt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_groups():
    body = {
        "chapter_groups": [
            {"id": GROUP_SURVIVAL},
            {"id": GROUP_CRAFT},
            {"id": GROUP_LATE},
            {"id": GROUP_SIDE},
        ]
    }
    (QUESTS / "chapter_groups.snbt").write_text(to_snbt(body) + "\n", encoding="utf-8")


def main() -> None:
    write_groups()
    write_reward_tables()
    write_chapter("01_soil", CH["soil"], GROUP_SURVIVAL, 0, "minecraft:dirt", build_soil(), "Strand: Soil")
    write_chapter("02_stone", CH["stone"], GROUP_SURVIVAL, 1, "minecraft:cobblestone", build_stone(), "Strand: Stone")
    write_chapter("03_sprout", CH["sprout"], GROUP_SURVIVAL, 2, "minecraft:wheat_seeds", build_sprout(), "Strand: Sprout")
    write_chapter("04_claw", CH["claw"], GROUP_CRAFT, 3, "silentgear:blueprint_package", build_claw(), "Strand: Claw")
    write_chapter("05_spark", CH["spark"], GROUP_CRAFT, 4, "minecraft:redstone", build_spark(), "Strand: Spark")
    write_chapter("06_clock", CH["clock"], GROUP_CRAFT, 5, "create:cogwheel", build_clock(), "Strand: Clock")
    write_chapter("07_swarm", CH["swarm"], GROUP_LATE, 6, "minecraft:honeycomb", build_swarm(), "Strand: Swarm")
    write_chapter("08_sigil", CH["sigil"], GROUP_LATE, 7, "minecraft:amethyst_shard", build_sigil(), "Strand: Sigil")
    write_chapter("09_spindle", CH["spindle"], GROUP_LATE, 8, "ae2:controller", build_spindle(), "Strand: Spindle")
    write_chapter("10_exdeorum", CH["exdeorum"], GROUP_SIDE, 9, "exdeorum:oak_sieve", build_exdeorum_side(), "Deep Sieve")
    write_chapter("11_storage", CH["storage"], GROUP_SIDE, 10, "functionalstorage:oak_1", build_storage_side(), "Storage & Packs")
    write_chapter("12_mekanism", CH["mekanism"], GROUP_SIDE, 11, "mekanism:ingot_steel", build_mekanism_side(), "Mekanism Works")
    write_chapter("13_powah", CH["powah"], GROUP_SIDE, 12, "powah:energy_cell_basic", build_powah_side(), "Powah Grid")
    write_chapter("14_ars", CH["ars"], GROUP_SIDE, 13, "ars_nouveau:source_gem", build_ars_side(), "Arcane Side")
    write_chapter("15_clowder", CH["clowder"], GROUP_SIDE, 14, "clowderhall:island_charter", build_clowder(), "Clowder Hall")
    write_chapter("16_shop", CH["shop"], GROUP_SIDE, 15, "ninjacatskies:frayed_thread", build_shop(), "Frayed Thread Desk")
    write_chapter("17_aura", CH["aura"], GROUP_SIDE, 16, "naturesaura:eye", build_aura_side(), "Nature's Aura")
    write_chapter("18_food", CH["food"], GROUP_SIDE, 17, "farmersdelight:cooking_pot", build_food_side(), "Kitchen Line")
    write_chapter("19_spells", CH["spells"], GROUP_SIDE, 18, "irons_spellbooks:iron_spell_book", build_spells_side(), "Battle Spells")
    write_chapter("20_solar", CH["solar"], GROUP_SIDE, 19, "solarflux:photovoltaic_cell_1", build_solar_side(), "Solar Flux")
    write_chapter("21_decor", CH["decor"], GROUP_SIDE, 20, "minecraft:flower_pot", build_decor_side(), "Pad Decor")
    write_chapter("22_nether", CH["nether"], GROUP_SIDE, 21, "minecraft:netherrack", build_nether_side(), "Nether Foothold")
    write_chapter("23_end", CH["end"], GROUP_SIDE, 22, "minecraft:end_stone", build_end_side(), "End Foothold")
    write_chapter("24_crops", CH["crops"], GROUP_SIDE, 23, "mysticalagriculture:infusion_altar", build_crops_side(), "Essence Fields")
    write_chapter("25_bees", CH["bees"], GROUP_SIDE, 24, "productivebees:advanced_oak_beehive", build_bees_side(), "Swarm Apiary")
    write_chapter("26_pipes", CH["pipes"], GROUP_SIDE, 25, "pipez:item_pipe", build_pipes_side(), "Pipeworks")
    write_chapter("27_occult", CH["occult"], GROUP_SIDE, 26, "occultism:dictionary_of_spirits", build_occult_side(), "Otherworld")
    write_chapter("28_factory", CH["factory"], GROUP_SIDE, 27, "create:mechanical_arm", build_factory_side(), "Clockworks Deep")
    write_chapter("29_network", CH["network"], GROUP_SIDE, 28, "ae2:drive", build_network_side(), "Spindle Network")
    write_chapter("30_voidcraft", CH["voidcraft"], GROUP_SIDE, 29, "voidloom:loomframe", build_voidcraft_side(), "Voidcraft")
    write_chapter("31_packaged", CH["packaged"], GROUP_SIDE, 30, "packagedauto:packager", build_packaged_side(), "Packaged Lines")
    write_chapter("32_qio", CH["qio"], GROUP_SIDE, 31, "mekanism:qio_dashboard", build_qio_side(), "QIO & Mek Peak")
    write_chapter("33_mobfarm", CH["mobfarm"], GROUP_SIDE, 32, "minecraft:rotten_flesh", build_mobfarm_side(), "Hunt & Farm")
    write_chapter("34_tribal", CH["tribal"], GROUP_SIDE, 33, "tribalpower:drumheart", build_tribal_side(), "Tribal Weave")
    write_lang()
    titles = sum(1 for k in lang if k.startswith("quest.") and k.endswith(".title"))
    print(f"Wrote chapters + lang. Quest titles: {titles}. Skipped invalid: {len(WARNED)}")


if __name__ == "__main__":
    main()
