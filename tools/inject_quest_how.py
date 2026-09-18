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
    "ninjacatskies:codex_page": "How: seating a Strand at the Post, or Desk/Kin. Right-click to read; they are kept, not spent.",
    "ninjacatskies:braid_cord": "How: seat any two of Clock, Swarm, Spark, then right-click the Tension Post with Strand Filament.",
    "ninjacatskies:strand_filament": "How: iron thread mesh on gravel, sand, or dust (Loomframe or sieve).",
    "voidloom:strand_filament": "How: iron thread mesh on gravel, sand, or dust (Loomframe or sieve).",
    "ninjacatskies:spindle_loom_fragment": "How: nine tokens seated, then right-click the Post with March Stone.",
    "voidloom:void_yarn": "How: four string → two yarn. Tension Barrel: string + pearl. Four Loom Lint.",
    "voidloom:spindle_hammer": "How: cobble + sticks. Break grit into gravel, sand, dust.",
    "voidloom:thread_mesh_string": "How: string around yarn. Grit stall sells one.",
    "voidloom:thread_mesh_flint": "How: flint around a string thread mesh.",
    "voidloom:thread_mesh_iron": "How: iron around a flint thread mesh. Strand Filament starts here.",
    "voidloom:loomframe": "How: planks around a Binding Knot. Stretch a mesh, hopper grit in, sit it on a hopper.",
    "voidloom:tension_barrel": "How: planks, string, and Void Yarn. Pour water (bucket returns), add dirt → clay.",
    "voidloom:binding_knot": "How: Void Yarn ring around a slime ball.",
    "voidloom:spindle_crook": "How: four sticks. Grit stall sells one.",
    "voidloom:loom_lint": "How: string/flint/iron thread mesh on dirt in a sieve or Loomframe. Four lint → yarn.",
    "exdeorum:porcelain_clay": "How: clay + bone meal.",
    "exdeorum:porcelain_bucket": "How: smelt porcelain clay.",
    "exdeorum:string_mesh": "How: string on a mesh craft, or Grit stall.",
    "exdeorum:flint_mesh": "How: flint on a mesh craft after Recover starts sieving.",
    "exdeorum:iron_mesh": "How: iron on a mesh craft. Grit stall sells one.",
    "tribalpower:bone_chime": "How: one bone, string, amethyst. /clowder hub Pad-keepers sell bones. Spark / Hum gate.",
    "tribalpower:spirit_shard": "How: Bone Chime, amethyst and redstone, shapeless. Yields two.",
    "tribalpower:copper_resonator": "How: copper around a Bone Chime. Yields two.",
    "tribalpower:drumheart": "How: Chime + Shard + leather. Strike empty-handed on tempo (17–23 ticks) for 24 Pulse.",
    "tribalpower:pulse_cell": "How: craft, then fill from a Drumheart (click with the cell).",
    "tribalpower:ley_collector": "How: place under sky near water/green. Slow Pulse. Spark ladder.",
    "tribalpower:pulse_resonator": "How: seat an Echo catalyst, two different totems within 8. Redstone pauses it.",
    "tribalpower:echo_shatter": "How: stone + Bone Chime + Copper Resonator. Earth totem within 8. Stone → shards; cobble → gravel.",
    "tribalpower:echo_shard": "How: Echo Shatter stone (not cobble). Font stone tier, or silk-touched stone.",
    "tribalpower:ember_kiln": "How: furnace + resonators + chime. Fire totem. Smelts grit for Pulse — a hand Drumheart cannot run it.",
    "tribalpower:spirit_codex": "How: craft or Spark/Tribal Weave reward. Right-click: how the lattice works.",
    "tribalpower:gate_drum": "How: charge the Gate Drum with Pulse, then empty-handed use it. Do not strike it like a Drumheart. Bind a return compass first.",
    "tribalpower:spirit_cistern": "How: craft, fill with a bucket or pipe, pick it up — fluid stays. AE2 Sky Stone Tanks empty when broken.",
    "minecraft:conduit": "How: needs Heart of the Sea and nautilus. Ocean-only. Optional.",
    "minecraft:nautilus_shell": "How: ocean-only. Optional.",
    "minecraft:rabbit_foot": "How: rabbits do not spawn on the pad. Optional.",
    "minecraft:name_tag": "How: fishing / rare chests, not a pad craft. Optional.",
    "minecraft:ender_eye": "How: pearl (Spark stall / endermen) plus blaze powder from a Nether fortress after Claw obsidian. Eight-eye stock is optional; End crystals use the same craft.",
    "minecraft:raw_iron": "How: sieve gravel (flint mesh and up) or smelt iron grit from Echo Shatter.",
    "minecraft:glass": "How: smelt sand. Hammer cobble to gravel, gravel to sand, then furnace.",
    "minecraft:lava_bucket": "How: Ex Deorum lava crucible, or a Nether lava pool after Claw obsidian.",
    "minecraft:obsidian": "How: water on a lava source (or lava on water). Keep the lava source.",
    "minecraft:diamond": "How: sieve gravel with an iron mesh or better, or Echo Shatter diamond ore.",
    "minecraft:ender_chest": "How: eight obsidian around an Eye of Ender. Eye is pearl plus blaze powder.",
    "minecraft:chorus_fruit": "How: Spark stall at /clowder hub. Outer End islands are gone.",
    "minecraft:popped_chorus_fruit": "How: smelt chorus fruit from the Spark stall.",
    "minecraft:gunpowder": "How: creepers on the pad at night. Keep edges lit after you have some.",
    "minecraft:redstone": "How: sieve gravel, or Echo Shatter redstone ore after Recover.",
    "minecraft:lapis_lazuli": "How: sieve gravel, or Echo Shatter lapis ore.",
    "minecraft:andesite": "How: sieve dirt/gravel pebbles, or cobble plus diorite in JEI.",
    "minecraft:diorite": "How: sieve pebbles, or cobble plus nether quartz.",
    "minecraft:granite": "How: sieve pebbles, or diorite plus nether quartz.",
    "minecraft:netherrack": "How: Nether after Claw obsidian.",
    "minecraft:soul_sand": "How: Nether after Claw obsidian. Three skulls on soul sand make a Wither.",
    "minecraft:glowstone_dust": "How: break Nether glowstone, or witches on the pad.",
    "minecraft:spider_eye": "How: spiders on the pad at night.",
    "minecraft:iron_hoe": "How: two iron ingots over a stick.",
    "minecraft:wither_skeleton_skull": "How: Nether fortress after Claw obsidian. Three skulls start a Wither.",
    "minecraft:lead": "How: four string around a slime ball. Slime is pad compost (dirt, seeds, bone meal).",
    "minecraft:egg": "How: wheat seeds to chickens on the pad, or a Mob Farm chapter coop.",
    "minecraft:white_wool": "How: shear sheep after grass, or four string.",
    "minecraft:beef": "How: wheat to cows on the pad.",
    "minecraft:porkchop": "How: potatoes or carrots to pigs on the pad.",
    "minecraft:chicken": "How: seeds to chickens on the pad.",
    "minecraft:mutton": "How: wheat to sheep on the pad.",
    "minecraft:ghast_tear": "How: Nether ghasts after Claw obsidian.",
    "minecraft:magma_cream": "How: Nether magma cubes, or slime plus blaze powder.",
    "minecraft:arrow": "How: flint, stick, feather. Skeletons drop extras.",
    "minecraft:spectral_arrow": "How: glowstone dust around an arrow.",
    "minecraft:book": "How: three paper plus leather. Paper is sugar cane.",
    "minecraft:paper": "How: three sugar cane in a row. Cane from sieve dirt or Pad-keepers.",
    "minecraft:amethyst_shard": "How: sieve, or budding amethyst if you grow a geode line. Occultism wants shards.",
    "minecraft:purple_dye": "How: blue plus red, or a purple flower. Occultism wants it.",
    "minecraft:white_dye": "How: bone meal in a grid, or a white flower.",
    "minecraft:black_dye": "How: charcoal or an ink sac (charcoal plus a glass bottle).",
    "minecraft:repeater": "How: redstone torch, redstone, stone. Pipes chapter uses it for clocks.",
    "minecraft:comparator": "How: nether quartz, redstone torch, stone.",
    "minecraft:redstone_torch": "How: redstone over a stick.",
    "minecraft:target": "How: redstone around hay. Hay is three wheat.",
    "minecraft:daylight_detector": "How: glass, nether quartz, wood slabs.",
    "minecraft:lectern": "How: wood slabs around a bookshelf.",
    "minecraft:trapped_chest": "How: tripwire hook plus a chest.",
    "minecraft:crying_obsidian": "How: Nether ruined portals after Claw, or barter.",
    "minecraft:respawn_anchor": "How: crying obsidian plus glowstone. Nether-only respawn.",
    "minecraft:black_concrete": "How: concrete powder plus water. Powder is sand, gravel, and dye.",
    "minecraft:purple_concrete": "How: concrete powder plus water. Powder is sand, gravel, and dye.",
    "minecraft:saddle": "How: not a pad craft. Optional hunt / leatherworker. Chocobo Saddle is a different item.",
    "minecraft:wheat": "How: wheat seeds on farmland, then bone meal. Seeds from breaking grass or the starter chest.",
    "minecraft:wheat_seeds": "How: break grass, or Pad-keepers. Plant on farmland; bone meal speeds the first field.",
    "minecraft:shears": "How: two iron ingots diagonal. Shear sheep and bee nests.",
    "minecraft:hopper": "How: five iron around a chest. Sit it under a Loomframe or Tension Barrel (extract DOWN).",
    "minecraft:bone_block": "How: nine bone meal. Bones from skeletons or Pad-keepers.",
    "minecraft:hay_block": "How: nine wheat. Three wheat also makes bread.",
    "minecraft:quartz": "How: Nether quartz ore after Claw obsidian, or barter.",
    "minecraft:netherite_ingot": "How: four scrap plus four gold. Debris is rare Nether after Claw.",
    "minecraft:ancient_debris": "How: rare Nether after Claw obsidian. Blast-mine or strip at y=15.",
    "minecraft:netherite_scrap": "How: smelt ancient debris. Four scrap plus gold makes an ingot.",
    "minecraft:gold_nugget": "How: one ingot makes nine, or Nether gold ore.",
    "minecraft:nether_gold_ore": "How: Nether after Claw obsidian.",
    "minecraft:fire_charge": "How: blaze powder, coal, and gunpowder.",
    "minecraft:nether_bricks": "How: smelt netherrack, then four nether brick items.",
    "minecraft:blackstone": "How: Nether after Claw obsidian. Basalt deltas and bastions.",
    "minecraft:basalt": "How: Nether after Claw, or soul soil plus blue ice over lava.",
    "minecraft:glowstone": "How: four glowstone dust, or break Nether glowstone.",
    "minecraft:soul_soil": "How: Nether soul-sand valleys after Claw obsidian.",
    "minecraft:purpur_block": "How: four popped chorus. Chorus fruit is the Spark stall.",
    "minecraft:purpur_pillar": "How: two purpur slabs, or stonecutter. Popped chorus first.",
    "minecraft:end_rod": "How: blaze rod plus popped chorus. Nether after Claw; chorus is Spark stall.",
    "minecraft:dropper": "How: cobble around redstone.",
    "minecraft:dispenser": "How: cobble, bow, and redstone.",
    "minecraft:observer": "How: cobble, redstone, and nether quartz.",
    "minecraft:trident": "How: drowned only. Optional.",
    "minecraft:shield": "How: six planks around iron. Off-hand block.",
    "minecraft:iron_chestplate": "How: eight iron ingots. Smelt sieve grit.",
    "minecraft:iron_helmet": "How: five iron ingots.",
    "minecraft:iron_leggings": "How: seven iron ingots.",
    "minecraft:iron_boots": "How: four iron ingots.",
    "minecraft:bow": "How: three string and three sticks.",
    "minecraft:flint_and_steel": "How: iron ingot plus flint.",
    "minecraft:enchanting_table": "How: two diamonds, four obsidian, book. Diamonds from iron-mesh gravel.",
    "minecraft:anvil": "How: three iron blocks over four ingots.",
    "minecraft:bookshelf": "How: six planks and three books. Books are paper plus leather.",
    "minecraft:lapis_block": "How: nine lapis. Sieve gravel or Echo Shatter lapis ore.",
    "minecraft:golden_apple": "How: eight gold around an apple. Not the enchanted one.",
    "minecraft:fermented_spider_eye": "How: spider eye, brown mushroom, sugar.",
    "minecraft:honeycomb": "How: shear a nest or hive after bees work a flower.",
    "minecraft:beehive": "How: three honeycomb and six planks. Campfire underneath calms them.",
    "minecraft:bee_nest": "How: oak log ring around a small flower; wait for wings. Swarm names the nest.",
    "minecraft:honey_bottle": "How: glass bottle on a full hive. Campfire underneath.",
    "minecraft:honey_block": "How: four honey bottles. Bottles return.",
    "minecraft:honeycomb_block": "How: four honeycomb.",
    "minecraft:campfire": "How: logs, sticks, and coal or charcoal.",
    "minecraft:poppy": "How: bone-meal grass, or a small flower for the oak nest.",
    "minecraft:dandelion": "How: bone-meal grass. Bees want any small flower.",
    "minecraft:flowering_azalea": "How: moss plus oak, or bone-meal moss. Bees accept the bloom.",
    "minecraft:compass": "How: iron around redstone.",
    "minecraft:map": "How: compass surrounded by paper.",
    "minecraft:lodestone": "How: netherite ingot in chiseled stone bricks. Late Clowder luxury.",
    "minecraft:bell": "How: gold plus a stone slab. Clowder meeting mark.",
    "minecraft:oak_sign": "How: planks over a stick.",
    "minecraft:white_banner": "How: six wool over a stick.",
    "minecraft:firework_rocket": "How: paper plus gunpowder. Optional burst.",
    "minecraft:golden_carrot": "How: eight gold nuggets around a carrot. Carrots are rare zombie drops; the snack is optional.",
    "minecraft:stone_bricks": "How: four stone in a square, or the stonecutter.",
    "minecraft:mossy_stone_bricks": "How: stone bricks plus vines or moss. Stonecutter after that.",
    "minecraft:cracked_stone_bricks": "How: smelt stone bricks.",
    "minecraft:chiseled_stone_bricks": "How: two stone brick slabs, or the stonecutter.",
    "minecraft:smooth_stone": "How: smelt stone. Slabs come from the stonecutter.",
    "minecraft:polished_andesite": "How: four andesite, or the stonecutter.",
    "minecraft:polished_diorite": "How: four diorite, or the stonecutter.",
    "minecraft:polished_granite": "How: four granite, or the stonecutter.",
    "minecraft:bricks": "How: four brick items. Clay balls smelt into bricks.",
    "minecraft:mud_bricks": "How: four packed mud. Mud is dirt plus a water bottle.",
    "minecraft:deepslate_bricks": "How: polished deepslate in a square, or the stonecutter. Deepslate from Echo Shatter or the Nether.",
    "minecraft:deepslate_tiles": "How: deepslate bricks in a square, or the stonecutter.",
    "minecraft:polished_blackstone": "How: four blackstone, or the stonecutter. Nether after Claw.",
    "minecraft:quartz_block": "How: four nether quartz. Nether after Claw.",
    "minecraft:smooth_quartz": "How: smelt a quartz block.",
    "minecraft:red_nether_bricks": "How: nether bricks plus nether wart. Nether after Claw.",
    "minecraft:polished_basalt": "How: stonecutter, or four basalt. Nether after Claw.",
    "minecraft:smooth_basalt": "How: smelt basalt. Nether after Claw.",
    "minecraft:magma_block": "How: four magma cream, or Nether magma. Nether after Claw.",
    "minecraft:shroomlight": "How: crimson/warped forests after Claw. Bone-meal nylium helps.",
    "minecraft:nether_wart_block": "How: nine nether wart, or crimson forests after Claw.",
    "minecraft:warped_wart_block": "How: warped forests after Claw.",
    "minecraft:crimson_stem": "How: crimson fungus on nylium after Claw. Bone-meal the fungus.",
    "minecraft:warped_stem": "How: warped fungus on nylium after Claw. Bone-meal the fungus.",
    "minecraft:weeping_vines": "How: crimson forests after Claw. Hang from the ceiling.",
    "minecraft:twisting_vines": "How: warped forests after Claw. Grow up from nylium.",
    "minecraft:enchanted_golden_apple": "How: not a pad craft. Optional secret — it does not gate the Sigil Knot.",
    "minecraft:nether_star": "How: Wither after Claw obsidian (three skulls on soul sand). Optional trophy — it does not gate End or Mob Farm 100%.",
    "minecraft:gilded_blackstone": "How: Nether bastion after Claw obsidian. A Decor leaf, not a later gate.",
    "minecraft:beacon": "How: nether star, glass, and obsidian. Optional trophy — ocean leaves hang off Obsidian Stock.",
    "minecraft:poisonous_potato": "How: a rare potato harvest. Optional Sprout secret.",
    "minecraft:blaze_rod": "How: Nether fortress after Claw obsidian. Brewing wants a rod; Ars and Occultism do not wait on it.",
    "minecraft:blaze_powder": "How: craft from a blaze rod, or a fortress after Claw obsidian.",
    "minecraft:brewing_stand": "How: blaze rod over three cobble. The rod is a Nether fortress after Claw obsidian.",
    "minecraft:dragon_breath": "How: glass bottle on the dragon. The End island is gone. Optional.",
    "minecraft:dragon_egg": "How: the dragon is gone with the End island. Optional trophy — it does not gate Ender Chests.",
    "minecraft:writable_book": "How: book, ink sac, feather. Charcoal plus a glass bottle makes the ink.",
    "minecraft:ink_sac": "How: charcoal plus a glass bottle. Squid never spawn here.",
    "minecraft:end_stone": "How: chorus fruit and ender pearls (Spark stall) around a Binding Knot. Yields eight. The End island is gone.",
    "minecraft:end_stone_bricks": "How: four End Stone in a square, or the stonecutter. End Stone is the Knot craft.",
    "minecraft:snowball": "How: one ice (kit / ice gen) shapeless into four snowballs.",
    "minecraft:elytra": "How: End cities are gone. Optional.",
    "minecraft:totem_of_undying": "How: raids and evokers do not happen on the pad. Optional.",
    "ae2:silicon_press": "How: iron block, Binding Knot, iron, and quartz. AE2 only duplicates a press you already have.",
    "ae2:logic_processor_press": "How: iron block, Binding Knot, iron, and gold. First copy is the Knot craft.",
    "ae2:calculation_processor_press": "How: iron block, Binding Knot, iron, and certus (sieve sand). First copy is the Knot craft.",
    "ae2:engineering_processor_press": "How: iron block, Binding Knot, iron, and diamond. First copy is the Knot craft.",
    "minecraft:shulker_shell": "How: End cities are gone from the main island. Optional.",
    "minecraft:shulker_box": "How: needs shulker shells. Optional.",
    "minecraft:glow_ink_sac": "How: glow squid never spawn on the pad. Optional.",
    "minecraft:end_portal_frame": "How: not a pad craft. Optional.",
    "minecraft:chorus_flower": "How: outer End islands are gone. Chorus fruit is the Spark stall. Optional.",
    "minecraft:phantom_membrane": "How: skip sleep three nights, then kill phantoms. Optional.",
    "minecraft:prismarine_shard": "How: ocean monuments are gone. Optional unless you grow a prismarine seed.",
    "minecraft:prismarine_crystals": "How: ocean monuments are gone. Optional.",
    "minecraft:prismarine": "How: needs prismarine shards. Ocean-only. Optional.",
    "minecraft:dark_prismarine": "How: needs prismarine shards. Ocean-only. Optional.",
    "minecraft:end_crystal": "How: glass, eye of ender, ghast tear. Nether after Claw obsidian; the egg is optional.",
    "clowderhall:island_charter": "How: K opens the island panel. Hold the Charter; sneak-use on Overworld pad ground to seal spawn. Start here names the steps.",
    "clowderhall:hub_key": "How: starter kit / Hall. `/clowder hub` and Hub Key go to Clowder Hall; `/clowder return` comes home.",
    "chocobosreborn:gysahl_green": "How: pick March thickets (Reed Fen is densest). Craft extras into seeds; plant on dirt or March soil.",
    "chocobosreborn:sage_notes": "How: book plus gysahl. Right-click a bird to read it.",
    "pamhc2crops:aridgarden": "How: sieve dirt with a string mesh or better (Ex Deorum or Voidloom).",
    "pamhc2crops:frostgarden": "How: sieve dirt with a string mesh or better.",
    "pamhc2crops:shadedgarden": "How: sieve dirt with a string mesh or better.",
    "pamhc2crops:soggygarden": "How: sieve dirt with a string mesh or better.",
    "pamhc2crops:tropicalgarden": "How: sieve dirt with a string mesh or better.",
    "pamhc2crops:windygarden": "How: sieve dirt with a string mesh or better.",
    "agricraft:wooden_crop_sticks": "How: four sticks in a square. Place on farmland, then plant a seed.",
    "agricraft:seed_analyzer": "How: glass panes, stone slab, planks, and sticks. Seat the journal, then a seed.",
    "agricraft:journal": "How: writable book (book, ink sac, feather) plus wheat seeds. Charcoal plus a glass bottle makes the ink.",
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

    "chocobosreborn:chocobo_saddle": "How: leather, string and iron. Tame a wild yellow with gysahl, then saddle it.",
    "chocobosreborn:square_gate": "How: gold, emeralds and gysahl. After the March, speak to Esther at /clowder hub while mounted.",
    "chocobosreborn:chocobo_lure": "How: craft the lure. Hold it to find March yellows.",
    "chocobosreborn:gysahl_green_seeds": "How: craft seeds from gysahl, or pick them with the greens.",
    "chocobosreborn:carob_nut": "How: ravagers drop Carob. Sage Wynn at the Square also sells nuts.",
    "chocobosreborn:curiel_green": "How: Sage Wynn at the Square, race prizes, or lucky harvests.",
    "chocobosreborn:sylkis_green": "How: Sage Wynn at the Square, or a race prize.",
    "chocobosreborn:zeio_nut": "How: piglin brutes drop Zeio. Bilo the Nutkeeper at the Square sells the rest of the nuts.",
    "chocobosreborn:gp": "How: finish a heat at Chocobo Square. Esther or a Farmhand sends a saddled rider.",
    "chocobosreborn:pepio_nut": "How: Bilo the Nutkeeper, or a Stablehand at a Chocobo Farm.",
    "chocobosreborn:krakka_green": "How: shapeless — two gysahl and bone meal.",
    "chocobosreborn:tantal_green": "How: Sage Wynn, or craft listed in JEI.",
    "chocobosreborn:pahsana_green": "How: Sage Wynn at the Square.",
    "chocobosreborn:mimett_green": "How: Sage Wynn at the Square.",
    "chocobosreborn:reagan_green": "How: Sage Wynn at the Square.",
    "chocobosreborn:luchile_nut": "How: Bilo the Nutkeeper, or a Stablehand.",
    "chocobosreborn:saraha_nut": "How: Bilo the Nutkeeper, or a Stablehand.",
    "chocobosreborn:lasan_nut": "How: Bilo the Nutkeeper, or a Stablehand.",
    "chocobosreborn:pram_nut": "How: Bilo the Nutkeeper, or a Stablehand.",
    "chocobosreborn:porov_nut": "How: Bilo the Nutkeeper, or a Stablehand.",
    "create:andesite_alloy": "How: andesite + iron nugget in a crafting table (or mixer).",
    "create:shaft": "How: andesite alloy in a cutting recipe / craft listed in JEI.",
    "create:cogwheel": "How: shaft + planks.",
    "create:water_wheel": "How: shafts + planks + slabs. Needs a water flow beside it.",
    "silentgear:blueprint_package": "How: four Blueprint Paper, shapeless. Right-click to unwrap starter plans. Claiming a pad wipes Silent Gear's join gift.",
    "silentgear:blueprint_paper": "How: four paper and one blue dye, shapeless. Yields four sheets.",
    "silentgear:rod_blueprint": "How: unwrap the Blueprint Package, or JEI. Claw names the tool line.",
    "silentgear:pickaxe_blueprint": "How: unwrap the Blueprint Package, or JEI. Claw names the tool line.",
    "silentgear:axe_blueprint": "How: unwrap the Blueprint Package, or JEI. Claw names the tool line.",
    "silentgear:shovel_blueprint": "How: unwrap the Blueprint Package, or JEI. Claw names the tool line.",
    "silentgear:sword_blueprint": "How: unwrap the Blueprint Package, or JEI. Claw names the tool line.",
    "silentgear:upgrade_base": "How: JEI after Blueprint Paper. Claw names the upgrade line.",
    "silentgear:hoe_blueprint": "How: unwrap the Blueprint Package, or JEI.",
    "silentgear:sickle_blueprint": "How: unwrap the Blueprint Package, or JEI.",
    "silentgear:paxel_blueprint": "How: unwrap the Blueprint Package, or JEI.",
    "silentgear:hammer_blueprint": "How: unwrap the Blueprint Package, or JEI.",
    "silentgear:excavator_blueprint": "How: unwrap the Blueprint Package, or JEI.",
    "silentgear:knife_blueprint": "How: unwrap the Blueprint Package, or JEI.",
    "ftbquests:book": "How: press Grave (`). Do not craft an FTB quest book.",
    "clowderhall:strand_banner_pattern": "How: craft at the Hall or JEI. A banner mark, not a Strand token.",
    "botanypots:terracotta_botany_pot": "How: terracotta Botany Pot in JEI. Dirt + a seed in the pot; bone meal still helps.",
    "botanypots:terracotta_hopper_botany_pot": "How: hopper Botany Pot in JEI. Sits over a chest/hopper and harvests itself.",
    "pipez:item_pipe": "How: iron + redstone. Faces with the Pipez wrench.",
    "pipez:fluid_pipe": "How: iron + buckets + redstone. Wrench for face and filter.",
    "pipez:energy_pipe": "How: iron + redstone. Carries FE between machines.",
    "pipez:wrench": "How: iron + redstone. Sneak-use a pipe to set direction without breaking it.",
    "solarflux:photovoltaic_cell_1": "How: Solar Flux mirror plus iron/glass. Cell 1 is the first panel craft.",
    "solarflux:mirror": "How: glass and iron in JEI. First Solar Flux part.",
    "occultism:dictionary_of_spirits": "How: book + purple dye (JEI). Read it; Spirit Fire is next.",
    "occultism:spirit_fire": "How: Dictionary rites. Not campfire. Otherworld chapter names the drop.",
    "occultism:golden_sacrificial_bowl": "How: gold around a sacrificial bowl. Dictionary names the ritual.",
    "naturesaura:gold_fiber": "How: seeds + gold nuggets, plant on grass in aura. Aura chapter starts here.",
    "naturesaura:gold_leaf": "How: break golden leaves grown from Gold Fiber.",
    "naturesaura:nature_altar": "How: wood + gold leaf. Heart of the Aura line.",
    "naturesaura:eye": "How: gold leaf + spider eye. Shows local aura.",
    "irons_spellbooks:iron_spell_book": "How: iron + paper + arcane essence. Spells chapter names ink.",
    "irons_spellbooks:arcane_essence": "How: kill casters or craft listed in JEI. Fuel for ink and books.",
    "irons_spellbooks:common_ink": "How: bottle + essence + dye. First inscription ink.",
    "sophisticatedstorage:controller": "How: barrel + iron/redstone in JEI. Links nearby Sophisticated barrels.",
    "sophisticatedstorage:copper_barrel": "How: upgrade a barrel with copper. JEI names the craft.",
    "functionalstorage:oak_1": "How: oak logs + chest. First drawer.",
    "sophisticatedbackpacks:backpack": "How: leather + chest. Then iron/gold/diamond upgrades.",
    "chipped:mason_table": "How: stone + table parts in JEI. Insert a block and pick a variant.",
    "chipped:carpenters_table": "How: Chipped carpenter table in JEI. Same idea as the mason table, for wood.",
    "handcrafted:oak_chair": "How: oak planks in JEI. First Handcrafted piece.",
    "framedblocks:framing_saw": "How: iron + planks. Cuts framed blocks.",
    "supplementaries:sconce": "How: torch + iron nuggets. First Stewardries craft.",
    "createaddition:copper_wire": "How: rolling mill (or JEI) from copper ingots. Current chapter starts here.",
    "modularrouters:modular_router": "How: iron + chest + paper in JEI. Modules go in the router.",
    "packagedauto:package_component": "How: iron + AE2/processor parts in JEI. First Packaged Auto craft.",
    "mekanismgenerators:heat_generator": "How: osmium + furnace + copper. First Mekanism generator.",
    "comforts:sleeping_bag_white": "How: wool in JEI. White sleeping bag; dye variants exist. Sets spawn without a full bed.",
    "comforts:hammock_white": "How: wool + string in JEI. Hang it from Rope and Nail.",
    "comforts:rope_and_nail": "How: iron nuggets + string. Place two, then hang the hammock.",
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
    "silentgear": "How: unwrap the Blueprint Package (four Blueprint Paper) or JEI. Claw names the tool line.",
    "chocobosreborn": "How: find it in the March or craft it from gysahl. Pad-runners names the step.",
    "pamhc2crops": "How: sieve dirt for a garden (string mesh and up), then break the bush for seeds.",
    "pamhc2trees": "How: sieve dirt with an iron mesh for kitchen saplings, then grow the fruit.",
    "pamhc2foodcore": "How: copper, andesite, or terracotta stations; coconut milk; tools come back after cooking. JEI names the craft.",
    "pamhc2foodextended": "How: gardens and fruit trees supply the ingredients. Soy tofu stands in for meat and egg. JEI names the station.",
    "agricraft": "How: wooden crop sticks from sticks; journal is a writable book plus seeds; analyzer is glass and wood. Plant on farmland.",
    "botanypots": "How: terracotta Botany Pot in JEI. Soil + seed in the pot; hopper pot harvests itself.",
    "pipez": "How: iron + redstone pipes in JEI. Wrench sets filter and face. Pipes chapter is the full ladder.",
    "solarflux": "How: Solar Flux — glass + iron mirror, then photovoltaic cells 1–6. Spark has a starter cell.",
    "occultism": "How: Dictionary of Spirits, then Spirit Fire and bowls. Otherworld chapter names the rites.",
    "naturesaura": "How: Gold Fiber on trees → Gold Leaf → Nature Altar. Aura chapter names tokens and generators.",
    "irons_spellbooks": "How: Arcane Essence and ink, then a spellbook. Spells chapter names the ladder.",
    "sophisticatedstorage": "How: barrels and upgrades in JEI. Controller ties a wall of barrels together.",
    "sophisticatedbackpacks": "How: leather backpack, then iron/gold/diamond upgrades in JEI.",
    "functionalstorage": "How: oak drawers 1x1 / 1x2 / 2x2, then compacting drawer and controller. JEI names the craft.",
    "modularrouters": "How: Modular Router plus blank modules in JEI. Puller/sender/breaker sit in the router.",
    "packagedauto": "How: package component, then Packager / Encoder. Needs an AE2 network for the ME piece.",
    "chipped": "How: Chipped workbench in JEI (mason, carpenter, glassblower…). Put the block in the table and pick a cut.",
    "handcrafted": "How: Handcrafted furniture from planks in JEI. First chair is oak.",
    "framedblocks": "How: Framing Saw, then framed cube/slab/stairs. Camo is right-click with a block.",
    "mcwbridges": "How: Macaw bridges from the matching stone/wood in JEI.",
    "mcwroofs": "How: Macaw roofs from the matching wood in JEI.",
    "supplementaries": "How: Supplementaries craft in JEI (sconce, sack, safe, rope…). Stewardries names the station.",
    "createaddition": "How: Create Crafts & Additions — copper wire from the rolling mill, then connectors and motor.",
    "create_enchantment_industry": "How: Create Enchantment Industry after a blaze burner. JEI names the printer and XP bucket.",
    "mekanismgenerators": "How: Mekanism generators after the Works line. Heat generator is the first craft.",
    "ae2wtlib": "How: Wireless Terminal after an AE2 network and a charged wireless kit. JEI names the craft.",
    "appmek": "How: Applied Mekanistics chemical cells after AE2 housing + Mekanism chemicals.",
    "comforts": "How: Comforts — sleeping bag from wool; hammock hangs on Rope and Nail. JEI names the dye variants.",
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
    if "look at the drop" in low:
        return "How: click the quest. Then punch the oak."
    if "look" in low or "wings" in low:
        return "How: look at the thing. The quest completes when it is in view."
    if "re-tension" in low:
        return "How: use the matching Frayed Totem, then win the arena. Advancement completes this."
    if "answer for the cut" in low:
        return "How: checkmark. Craft each Frayed Totem after that Strand is seated; use it outside an arena."
    if "sealed door" in low:
        return "How: seat all nine Strands, then Reweave. Advancement fires when the sky closes."
    if "quest book" in low or "assignment list" in low:
        return "How: press Grave (`). Do not craft an FTB quest book."
    if "raise the post" in low:
        return "How: logs around a Binding Knot, Thread on top. Place it on the pad. Look at it to complete."
    if "enter the hall" in low:
        return "How: Hub Key or `/clowder hub`. `/clowder return` comes home."
    if "something came up" in low:
        return "How: kill a zombie on the pad at night. Light the edges."
    if "boom, later" in low:
        return "How: kill three creepers. Gunpowder is the reward."
    if "edge of the edge" in low:
        return "How: kill an enderman. Pearls also come from the Spark stall."
    if "bottled trouble" in low:
        return "How: kill a witch on the pad at night."
    if "rattle in the gears" in low:
        return "How: kill twenty skeletons. Keep the pad lit."
    if "something new hums" in low:
        return "How: look at a Productive Bee after a nest wakes. First Wings is the oak nest."
    if low == "regret":
        return "How: kill a bee (hidden). The bottle is the lesson."
    if low == "reweave":
        return "How: seat the Spindle Loom Fragment at the Tension Post. Advancement fires when the sky closes."
    if "three voices awaken" in low:
        return "How: Spirit Seal in a Ritual Brazier; Earth, Air, Spirit totems within 8; 200 Pulse; three Spiritweave; use the imprinted effigy."
    if "answer from the cradle" in low:
        return "How: complete one successful summon from the cradle. Failed attempts spend nothing."
    if "halls that kept time" in low:
        return "How: Gate Drum into the March; read all four Lore Tablets in an Ancestor Hall."
    if "the drum remembers" in low:
        return "How: fight The Unsung at the Silent Drum. Sneak the Beat; four-beat the Silence."
    if "tether and stitch" in low:
        return "How: Sixfold Staff on Loom voice. Tether a target, then sneak-Stitch. Tick when both have fired."
    if low == "kept warm":
        return "How: right-click a March Tribe Hearth with that tribe's favour or a charged Pulse Cell."
    if "on good terms" in low:
        return "How: reach Friend (150) with a tribe. /tribalpower standing."
    if "nine agreeing" in low:
        return "How: Voice (800) with a tribe; the Elder gives a Tribe Mark once."
    if "camp keeps the beat" in low:
        return "How: place a Drumheart within 8 of a camp Drummer; tick when it is feeding Pulse."
    if "font of stone" in low:
        return "How: Spirit Codex + Tribal Weave. Station, totem, and Pulse cost are on the Codex page."
    if low == "draw the circle":
        return "How: place a rite pattern from the Spirit Codex; the advancement fires on the first complete circle."
    if low == "stone stays":
        return "How: run the Stone Font until cobble appears. Advancement on the first stay."
    if "font answers" in low:
        return "How: sneak-use the Spirit Codex on the Stone Font; tick when the report names a real fault or a full buffer."
    if "cell at the font" in low:
        return "How: fill a Pulse Cell from a Drumheart, then tick this when the font is fed."
    if "ask the ground" in low:
        return "How: Resonance Mesh over a pit with Anchor Stones; the advancement fires on the first ore."
    if "gold from the pit" in low:
        return "How: keep asking the ground; tick when gold grit is in hand."
    if "pit keeps time" in low:
        return "How: fill a Pulse Cell from a Drumheart and seat it where the Codex shows."
    if "open the way" in low:
        return "How: finish the ring and light it; the advancement fires when the way opens."
    if "long thread" in low:
        return "How: bind two keystones with a Gate Sigil, then walk the far gate."
    if "six voices singing" in low:
        return "How: Ember Horn, Wind Harp, Wave Drum, Wake Bell, Loom Anchor, and Drumheart within 32. Advancement on six voices."
    if "spring that keeps giving" in low:
        return "How: sneak-use the tablet on a Ritual Brazier in its Rite Circle with matching seal and Pulse."
    if "drum circle" in low:
        return "How: The Unsung at the Silent Drum can drop it. Optional."
    if "spare seal" in low:
        return "How: First Rite at the brazier; tick when a spare blank seal is in hand."
    if "first rite" in low:
        return "How: sneak-use any Rite Tablet on a Ritual Brazier in its Rite Circle with matching seal and Pulse."
    if "friend in the dark" in low:
        return "How: use a Bonding Charm on an adult familiar. Advancement on first bond."
    if "one vault, one budget" in low:
        return "How: /tribalpower camp create (not a Clowder). Advancement on first camp."
    if "ask the codex why" in low:
        return "How: sneak-use the Spirit Codex on a Tribal block; tick when the report names a real fault."
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
            generic = "How: make or find" in body
            if (item and item in HOW_ITEM) or (generic and not line.startswith("How: make or find")):
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
