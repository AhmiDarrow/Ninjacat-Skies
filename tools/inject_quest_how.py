#!/usr/bin/env python3
"""Append a How: line to every FTB quest description that lacks one."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "pack/overrides/config/ftbquests/quests/chapters"
LANG = ROOT / "pack/overrides/config/ftbquests/quests/lang/en_us.snbt"

HOW_ITEM = {
    "minecraft:oak_log": "How: punch the oak on your pad. Eight logs start Wake.",
    "minecraft:dirt": "How: starter chest, cobble+thread sink, sieve leftovers, or /clowder hub (Pad-keepers).",
    "minecraft:crafting_table": "How: four planks in a square.",
    "minecraft:wooden_pickaxe": "How: three planks over two sticks.",
    "minecraft:oak_sapling": "How: break oak leaves, or /clowder hub Pad-keepers (8 Thread).",
    "minecraft:oak_planks": "How: one log in the crafting grid makes four.",
    "minecraft:stick": "How: two planks in a column.",
    "minecraft:chest": "How: eight planks around an empty centre.",
    "minecraft:torch": "How: coal or charcoal over a stick. /clowder hub Kin sell a pack.",
    "minecraft:cobblestone": "How: lava next to water (or ice melt). Hammer stone. /clowder hub Grit stall sells a bundle.",
    "minecraft:furnace": "How: eight cobble around an empty centre.",
    "minecraft:bread": "How: three wheat in a row, or /clowder hub Pad-keepers.",
    "minecraft:bucket": "How: three iron ingots, or /clowder hub Pad-keepers (8 Thread). Fill from melted ice.",
    "minecraft:water_bucket": "How: empty bucket on a water source. Normal/Hard: place lava, melt ice, fill.",
    "minecraft:leather": "How: smelt or campfire rotten flesh. Sieve dirt with flint mesh. /clowder hub Pad-keepers sell two for 18 Thread.",
    "minecraft:rotten_flesh": "How: kill zombies on the pad at night, or a dark hole.",
    "minecraft:string": "How: unravel Frayed Thread (1 → 3). Spiders. Sieve. Yarn reverse sink.",
    "minecraft:bone": "How: skeletons at night, or /clowder hub Pad-keepers (16 Thread for 8).",
    "minecraft:bone_meal": "How: bones in a grid, or Thread + rotten flesh sink, or /clowder hub Pad-keepers.",
    "minecraft:slime_ball": "How: two dirt + wheat seeds + bone meal (pad compost), or /clowder hub Pad-keepers.",
    "minecraft:ender_pearl": "How: endermen, or /clowder hub Spark stall.",
    "minecraft:iron_ingot": "How: smelt raw iron / iron grit (furnace or Ember Kiln). Sieve gravel for chunks.",
    "minecraft:copper_ingot": "How: smelt raw copper / copper grit. Sieve gravel.",
    "minecraft:gold_ingot": "How: smelt raw gold / gold grit. Rarer sieve catch.",
    "minecraft:coal": "How: sieve dirt/gravel, or coal ore through Echo Shatter then furnace.",
    "minecraft:gravel": "How: hammer cobble (Spindle Hammer or Echo Shatter).",
    "minecraft:sand": "How: hammer gravel.",
    "minecraft:flint": "How: gravel, or Thread + gravel sink.",
    "minecraft:clay_ball": "How: Tension Barrel — water + dirt. Echo Shatter hammers sand to clay.",
    "minecraft:iron_nugget": "How: one ingot makes nine, or Grit stall.",
    "ninjacatskies:frayed_thread": "How: quest rewards, flint-mesh dirt on a Loomframe, steward caches.",
    "ninjacatskies:whisker_codex": "How: starter kit / dock chest. Right-click the book; Grave (`) is the assignment list.",
    "voidloom:void_yarn": "How: four string → two yarn. Tension Barrel: string + pearl. Four Loom Lint.",
    "voidloom:spindle_hammer": "How: cobble + sticks. Break grit into gravel, sand, dust.",
    "voidloom:thread_mesh_string": "How: string around yarn. Grit stall sells one.",
    "voidloom:thread_mesh_flint": "How: flint around yarn after a flint mesh upgrade.",
    "voidloom:thread_mesh_iron": "How: iron around yarn. Iron mesh is Recover's target.",
    "voidloom:loomframe": "How: planks around a Binding Knot. Stretch a mesh, hopper grit in, sit it on a hopper.",
    "voidloom:tension_barrel": "How: barrels + Binding Knot. Pour water (bucket returns), add dirt → clay.",
    "voidloom:binding_knot": "How: Void Yarn ring around a slime ball.",
    "voidloom:spindle_crook": "How: sticks + flint. Grit stall sells one.",
    "voidloom:loom_lint": "How: string/flint/iron thread mesh on dirt in a sieve or Loomframe. Four lint → yarn.",
    "exdeorum:porcelain_clay": "How: clay + bone meal.",
    "exdeorum:porcelain_bucket": "How: smelt porcelain clay.",
    "exdeorum:string_mesh": "How: string on a mesh craft, or Grit stall.",
    "exdeorum:flint_mesh": "How: flint on a mesh craft after Recover starts sieving.",
    "exdeorum:iron_mesh": "How: iron on a mesh craft. Strand Filament starts here.",
    "tribalpower:bone_chime": "How: one bone, string, amethyst. /clowder hub Pad-keepers sell bones. Spark / Hum gate.",
    "tribalpower:spirit_shard": "How: Echo Attune line / Unweave. Spark quest names it.",
    "tribalpower:copper_resonator": "How: copper + echo bits. Spark ladder.",
    "tribalpower:drumheart": "How: Chime + Shard + leather. Strike empty-handed on tempo (17–23 ticks) for 24 Pulse.",
    "tribalpower:pulse_cell": "How: craft, then fill from a Drumheart (click with the cell).",
    "tribalpower:ley_collector": "How: place under sky near water/green. Slow Pulse. Spark ladder.",
    "tribalpower:pulse_resonator": "How: seat an Echo catalyst, two different totems within 8. Redstone pauses it.",
    "tribalpower:echo_shatter": "How: stone + Bone Chime + Copper Resonator. Earth totem within 8. Stone → shards; cobble → gravel.",
    "tribalpower:echo_shard": "How: Echo Shatter stone (not cobble). Font stone tier, or silk-touched stone.",
    "tribalpower:ember_kiln": "How: furnace + resonators + chime. Fire totem. Smelts grit for Pulse — a hand Drumheart cannot run it.",
    "tribalpower:spirit_codex": "How: craft or Spark/Tribal Weave reward. Right-click: how the lattice works.",
    "create:andesite_alloy": "How: andesite + iron nugget in a crafting table (or mixer).",
    "create:shaft": "How: andesite alloy in a cutting recipe / craft listed in JEI.",
    "create:cogwheel": "How: shaft + planks.",
    "create:water_wheel": "How: shafts + planks + slabs. Needs a water flow beside it.",
}

HOW_NS = {
    "minecraft": "How: craft, smelt, sieve, or mob-drop this. JEI lists every source on the pad.",
    "voidloom": "How: Voidloom — yarn, meshes, Loomframe, Tension Barrel. Recover chapter names the craft.",
    "ninjacatskies": "How: pack item — Codex, Knot, token, or Thread. Earlier Strand nodes name the seat.",
    "exdeorum": "How: Ex Deorum sieve, hammer, crucible, or barrel. Match the mesh to the grit.",
    "tribalpower": "How: Spirit Codex + Tribal Weave. Station, totem, and Pulse cost are on the Codex page.",
    "create": "How: Create — bench, millstone, mixer, or press. JEI, then the Clock chapter.",
    "farmersdelight": "How: sieve dirt for seeds (flint mesh), then the cutting board / pot.",
    "mysticalagriculture": "How: sieve dirt/gravel for Inferium and Prosperity ore, smelt, then craft the seed.",
    "productivebees": "How: ring of the nest material around a small flower, place, wait for wings.",
    "mekanism": "How: Mekanism Works chapter — ore chunks from the sieve, then the factory line.",
    "powah": "How: Powah Grid chapter — energizing orb and cables after Spark Pulse exists.",
    "ars_nouveau": "How: Arcane Side — archwood and sourceberry from moss, then the cascade.",
    "ae2": "How: Spindle Network — certus from sand, controller wants a Knot.",
    "guardians": "How: Whisker Codex Snapped Guardians — totem, arena, relic. Totem answers on the pad.",
}


def parse_quest_items() -> dict[str, str]:
    items: dict[str, str] = {}
    id_re = re.compile(r'id:\s*"([0-9A-Fa-f]+)"')
    item_re = re.compile(r'id:\s*"([a-z0-9_]+:[a-z0-9_/]+)"')
    for path in CHAPTERS.glob("*.snbt"):
        text = path.read_text(encoding="utf-8")
        current = None
        in_tasks = False
        for line in text.splitlines():
            if line.strip().startswith("id:") and current is None:
                m = id_re.search(line)
                if m and m.group(1).startswith("42"):
                    current = m.group(1)
            if "tasks:" in line:
                in_tasks = True
            if current and in_tasks:
                m = item_re.search(line)
                if m and ":" in m.group(1) and not m.group(1).startswith("42"):
                    items.setdefault(current, m.group(1))
            if current and line.strip() == "}":
                current = None
                in_tasks = False
    return items


def how_line(item: str | None, title: str) -> str:
    if item and item in HOW_ITEM:
        return HOW_ITEM[item]
    if item and ":" in item:
        ns = item.split(":", 1)[0]
        if ns in HOW_NS:
            return HOW_NS[ns]
    low = title.lower()
    if "knot" in low:
        return "How: craft the Knot from the chapter's last items, then seat the token at a Tension Post."
    if "seat" in low:
        return "How: right-click your Tension Post with the Strand token in hand."
    if "look" in low or "wings" in low:
        return "How: look at the thing. The quest completes when it is in view."
    return f"How: make or find {title}. JEI names the recipe; earlier quests in this chapter name the station and inputs."


def main() -> None:
    items = parse_quest_items()
    text = LANG.read_text(encoding="utf-8")
    title_re = re.compile(r'quest\.([0-9A-Fa-f]+)\.title:\s*"([^"]*)"')
    titles = {m.group(1): m.group(2) for m in title_re.finditer(text)}

    desc_re = re.compile(
        r'(quest\.([0-9A-Fa-f]+)\.quest_desc:\s*\[)(.*?)(\n\t\])',
        re.S,
    )

    added = 0
    already = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal added, already
        qid = m.group(2)
        body = m.group(3)
        if "How:" in body:
            already += 1
            return m.group(0)
        title = titles.get(qid, "this")
        line = how_line(items.get(qid), title).replace("\\", "\\\\").replace('"', '\\"')
        added += 1
        body = body.rstrip()
        if not body.endswith(','):
            body = body + ','
        return f'{m.group(1)}{body}\n\t\t"{line}"{m.group(4)}'

    new = desc_re.sub(repl, text)
    LANG.write_text(new, encoding="utf-8")
    missing = [qid for qid in titles if f"quest.{qid}.quest_desc" not in new]
    print(f"How lines added: {added}; already had How: {already}; titles without desc: {len(missing)}")


if __name__ == "__main__":
    main()
