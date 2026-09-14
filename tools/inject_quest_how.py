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
    "tribalpower:gate_drum": "How: craft, strike it, walk the March. Bind a return compass first.",
    "chococraft:gysahl_green": "How: pick March thickets (Reed Fen is densest). Craft extras into seeds; plant on dirt or March soil.",
    "chococraft:chocopedia": "How: book + chocobo feather. Right-click a bird to read grade, class, and wins.",
    "pamhc2crops:aridgarden": "How: sieve dirt with a string mesh or better (Ex Deorum or Voidloom).",
    "pamhc2crops:frostgarden": "How: sieve dirt with a string mesh or better.",
    "pamhc2crops:shadedgarden": "How: sieve dirt with a string mesh or better.",
    "pamhc2crops:soggygarden": "How: sieve dirt with a string mesh or better.",
    "pamhc2crops:tropicalgarden": "How: sieve dirt with a string mesh or better.",
    "pamhc2crops:windygarden": "How: sieve dirt with a string mesh or better.",
    "agricraft:wooden_crop_sticks": "How: four sticks in a square. Place on farmland, then plant a seed.",
    "agricraft:seed_analyzer": "How: glass panes, stone slab, planks, and sticks. Seat the journal, then a seed.",
    "agricraft:journal": "How: writable book (book, ink sac, feather) plus wheat seeds. Ink is the Soil chapter.",
    "agricraft:magnifying_glass": "How: glass pane between sticks, then a stick handle. Look at a planted crop.",
    "agricraft:wooden_rake": "How: wooden fence over a stick. Weeds are off; it still clears a stick.",
    "agricraft:trowel": "How: two iron ingots and a stick. Pick a plant up with its stats intact.",
    "agricraft:clipper": "How: shears, iron, and a stick. Clip a mature plant and reset it.",
    "agricraft:seed_bag": "How: leather and string. Fill from the analyzer.",
    "agricraft:iron_crop_sticks": "How: iron rods in the same square as wood. JEI names the craft.",
    "agricraft:iron_rake": "How: iron bars over a stick.",
    "agricraft:irrigation_tank": "How: planks. Hold water for the channels.",
    "agricraft:irrigation_channel": "How: shapeless from a tank — one tank becomes eight channels.",
    "agricraft:channel_valve": "How: craft onto a channel. Stop and start a line without breaking the tank.",
    "agricraft:sprinkler": "How: sit it on a channel over the sticks. JEI names the craft.",
    "agricraft:grate": "How: cover a channel so you can walk the row.",
    "agricraft:greenhouse_monitor": "How: craft, then place in the room to read light and humidity.",
    "agricraft:obsidian_crop_sticks": "How: obsidian in the stick square. Two neighbouring mature crops can cross-breed.",
    "agricraft:irrigation_channel_hollow": "How: a channel you can walk. Optional.",
    "pamhc2foodcore:cuttingboarditem": "How: copper, a stick, and a plank. Not the Farmer's Delight board.",
    "pamhc2foodcore:potitem": "How: copper and a stick. The pot comes back after every shapeless cook.",
    "pamhc2foodcore:skilletitem": "How: copper and sticks. Different from the Delight skillet.",
    "pamhc2foodcore:saucepanitem": "How: copper and a stick.",
    "pamhc2foodcore:bakewareitem": "How: eight terracotta around an empty centre.",
    "pamhc2foodcore:mixingbowlitem": "How: planks and a stick.",
    "pamhc2foodcore:juiceritem": "How: terracotta. Four in a T.",
    "pamhc2foodcore:rolleritem": "How: sticks either side of a log.",
    "pamhc2foodcore:grinderitem": "How: andesite (flint-sieve dirt or gravel pebbles) and a stick.",
    "pamhc2foodcore:freshwateritem": "How: one water bucket → eight freshwater.",
    "pamhc2foodcore:freshmilkitem": "How: coconut (iron-mesh dirt) plus freshwater, or split a milk bucket.",
    "pamhc2foodcore:saltitem": "How: pot plus water or freshwater. The pot comes back.",
    "pamhc2foodcore:flouritem": "How: grinder plus wheat (or another flour plant). The grinder comes back.",
    "pamhc2foodcore:doughitem": "How: mixing bowl, flour, water, salt.",
    "pamhc2foodcore:stockitem": "How: pot plus a bone (Pad-keepers sell bones) or leftover veg.",
    "pamhc2foodcore:applepieitem": "How: bakeware, dough, sugar, Pam's apples from the apple tree.",
    "pamhc2foodcore:fruitpunchitem": "How: juicer plus mixed fruit.",
    "pamhc2foodcore:grilledcheeseitem": "How: skillet, bread, butter, and cheese — all from freshwater, coconut milk, and flour.",
    "pamhc2foodextended:chiliitem": "How: pot, arid chili, tomato, onion, bean, spiceleaf, and meat or silken tofu.",
    "pamhc2foodextended:curryitem": "How: saucepan, rice, coconut, chili, black pepper, curry powder (spiceleaf + mustard + cinnamon).",
    "pamhc2foodextended:pepperonipizzaitem": "How: bakeware, dough, tomato, cheese, pepperoni (pork or tofu bacon from maple + soy).",
    "pamhc2foodextended:friedriceitem": "How: skillet, soggy-garden rice, carrot, onion, peas, and an egg — silken tofu counts as egg.",
    "pamhc2foodextended:greenteaitem": "How: pot, tea leaf, and spiceleaf. Shaded garden drops both tea and spice.",
    "pamhc2foodextended:avocadotoastitem": "How: iron-mesh avocado sapling, then skillet with toast, salt, garlic, spiceleaf.",
    "pamhc2foodcore:cookingoilitem": "How: press seeds or olives in JEI. Optional staple.",
    "pamhc2foodcore:butteritem": "How: pot plus milk (coconut freshwater milk works).",
    "pamhc2foodcore:mayonaiseitem": "How: eggs (or silken tofu) and oil. Optional.",
    "pamhc2foodcore:fruitsaladitem": "How: mixing bowl and mixed fruit. Optional.",
    "pamhc2foodcore:applejuiceitem": "How: juicer and Pam's apples. Optional.",
    "pamhc2foodcore:toastitem": "How: bakeware leftover bread. Optional.",
    "pamhc2trees:avocado_sapling": "How: sieve dirt with an iron mesh, then grow the fruit.",

    "chococraft:chocobo_saddle": "How: leather and feathers. Tame a wild yellow with gysahl, then saddle it.",
    "chococraft:chocobo_square_ticket": "How: paper, gold ingot, feather. After the March, speak to Ester at /clowder hub while mounted.",
    "chococraft:chocobo_whistle": "How: craft from feathers. Use it to follow / stay / wander.",
    "chococraft:straw": "How: craft, then floor a pen next to a water cauldron.",
    "chococraft:carob_nut": "How: gysahl + cocoa + wheat. Feed it, then Loverly or Gold gysahl, to mate.",
    "chococraft:loverly_gysahl_green": "How: 15% when harvesting mature gysahl. Not craftable into seeds.",
    "chococraft:gold_gysahl": "How: 5% when harvesting mature gysahl. Needed for Zeio and Gold chicks.",
    "chococraft:zeio_nut": "How: Gold Gysahl + Echo Shard + gold block. Gold never hatches without it.",
    "chococraft:chocobo_saddle_bags": "How: craft after a saddle. Sneak-use the bird to open 18 slots.",
    "chococraft:chocobo_saddle_pack": "How: craft from bags. Forty-five slots on the bird.",
    "chococraft:chocobo_feather": "How: kept birds shed them. Do not slaughter the line for feathers.",
    "chococraft:gysahl_cake": "How: craft from gysahl. Optional pen feast.",
    "chococraft:chocobo_drumstick_cooked": "How: cook a raw drumstick. Optional; the farm is for riding.",
    "chococraft:pickled_gysahl_cooked": "How: gysahl + sugar, then cook. Optional trail food.",
    "chococraft:choco_disguise_helmet": "How: craft from feathers. Optional vanity.",
    "chococraft:choco_disguise_chestplate": "How: craft from feathers. Optional vanity.",
    "chococraft:choco_disguise_leggings": "How: craft from feathers. Optional vanity.",
    "chococraft:choco_disguise_boots": "How: craft from feathers. Optional vanity.",
    "chococraft:pink_gysahl": "How: craft to dye a Gold bird pink. Optional Swarm echo.",
    "chococraft:red_gysahl": "How: craft to dye a Gold bird red. Optional Claw echo.",
    "chococraft:chocobo_square_gate": "How: Ester places the Square. You do not need to craft a gate.",
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
    "chococraft": "How: find it in the March or craft it from gysahl and feathers. Pad-runners names the step.",
    "pamhc2crops": "How: sieve dirt for a garden (string mesh and up), then break the bush for seeds.",
    "pamhc2trees": "How: sieve dirt with an iron mesh for kitchen saplings, then grow the fruit.",
    "pamhc2foodcore": "How: copper, andesite, or terracotta stations; coconut milk; tools come back after cooking. JEI names the craft.",
    "pamhc2foodextended": "How: gardens and fruit trees supply the ingredients. Soy tofu stands in for meat and egg. JEI names the station.",
    "agricraft": "How: wooden crop sticks from sticks; journal is a writable book plus seeds; analyzer is glass and wood. Plant on farmland.",
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
    replaced = [0]

    def repl(m: re.Match[str]) -> str:
        nonlocal added, already
        qid = m.group(2)
        body = m.group(3)
        title = titles.get(qid, "this")
        item = items.get(qid)
        line = how_line(item, title).replace("\\", "\\\\").replace('"', '\\"')
        if "How:" in body:
            if item and item in HOW_ITEM:
                replaced[0] += 1
                body = re.sub(r'\n\t\t"How:.*?"\s*$', f'\n\t\t"{line}"', body.rstrip(), count=1)
                return f'{m.group(1)}{body}{m.group(4)}'
            already += 1
            return m.group(0)
        added += 1
        body = body.rstrip()
        if not body.endswith(','):
            body = body + ','
        return f'{m.group(1)}{body}\n\t\t"{line}"{m.group(4)}'

    new = desc_re.sub(repl, text)
    LANG.write_text(new, encoding="utf-8")
    missing = [qid for qid in titles if f"quest.{qid}.quest_desc" not in new]
    print(f"How lines added: {added}; replaced: {replaced[0]}; already had How: {already}; titles without desc: {len(missing)}")


if __name__ == "__main__":
    main()
