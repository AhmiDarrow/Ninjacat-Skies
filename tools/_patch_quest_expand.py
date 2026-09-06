#!/usr/bin/env python3
"""One-shot patch: expand generate_quests.py with mid/late chapters toward 800-1100 titles."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "tools" / "generate_quests.py"
text = TARGET.read_text(encoding="utf-8")

OLD_CH_TAIL = '''    "decor": hid(0xB100000000000015),
    "nether": hid(0xB100000000000016),
    "end": hid(0xB100000000000017),
}'''

NEW_CH_TAIL = '''    "decor": hid(0xB100000000000015),
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
}'''

if "crops" not in text:
    if OLD_CH_TAIL not in text:
        raise SystemExit("CH dict tail not found")
    text = text.replace(OLD_CH_TAIL, NEW_CH_TAIL, 1)

NEW_BUILDERS = r'''
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
        ("Experience Seeds", "mysticalagriculture:experience_seeds", 1, "XP farm."),
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
    return main + grid_optional(s, seeds, origin=(-5.0, 3.0), cols=6)


def build_bees_side() -> list[dict]:
    s = 25
    main = chain(s, [
        ("Advanced Oak Hive", "productivebees:advanced_oak_beehive", 1, "Serious swarm home."),
        ("Expansion Box", "productivebees:expansion_box_oak", 2, "More bee rooms."),
        ("Jar Oak", "productivebees:jar_oak", 1, "Catch and keep."),
        ("Bee Cage", "productivebees:bee_cage", 4, "Transport."),
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
        ("Flower Carpet", "minecraft:poppy", 16, "Pollinate."),
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
    ], origin=(-4.0, 3.0), cols=5)
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
        ("Basic Upgrade", "pipez:basic_upgrade", 4, "Faster."),
        ("Improved Upgrade", "pipez:improved_upgrade", 4, "Faster still."),
        ("Advanced Upgrade", "pipez:advanced_upgrade", 2, "Serious speed."),
        ("Ultimate Upgrade", "pipez:ultimate_upgrade", 1, "Peak pipe."),
        ("Infinity Upgrade", "pipez:infinity_upgrade", 1, "No limit."),
        ("Filter Tool", "pipez:filter_destination_tool", 1, "Route smart."),
        ("Clear Upgrade", "pipez:clear_upgrade", 1, "Wipe settings."),
        ("Hopper Spare", "minecraft:hopper", 16, "Vanilla move."),
        ("Dropper Line", "minecraft:dropper", 8, "Push."),
        ("Dispenser Line", "minecraft:dispenser", 4, "Use."),
        ("Comparator", "minecraft:comparator", 8, "Read stacks."),
        ("Observer Line", "minecraft:observer", 8, "Watch."),
        ("Redstone Torch", "minecraft:redstone_torch", 16, "Signal."),
        ("Repeater", "minecraft:repeater", 16, "Delay."),
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
        ("Mek Tube", "mekanism:basic_pressurized_tube", 8, "Mek gas."),
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
    ], origin=(-3.0, 3.0), cols=3)
    return main + side


def build_factory_side() -> list[dict]:
    s = 28
    main = chain(s, [
        ("Hand Crank", "create:hand_crank", 1, "Manual spin."),
        ("Shaft Stock", "create:shaft", 32, "Rotation spine."),
        ("Cogwheel Stock", "create:cogwheel", 32, "Teeth."),
        ("Large Cog", "create:large_cogwheel", 16, "Big teeth."),
        ("Gearbox", "create:gearbox", 4, "Turn the corner."),
        ("Clutch", "create:clutch", 2, "Engage."),
        ("Gearshift", "create:gearshift", 2, "Reverse."),
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
        ("Mechanical Mixer", "create:mechanical_mixer", 1, "Stir."),
        ("Mechanical Press", "create:mechanical_press", 1, "Smash."),
        ("Millstone", "create:millstone", 1, "Grind."),
        ("Crushing Wheel", "create:crushing_wheel", 2, "Pair crush."),
        ("Encased Fan", "create:encased_fan", 2, "Blow."),
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
        ("Hose Pulley", "create:hose_pulley", 1, "Drain oceans."),
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
        ("Packager", "create:packager", 1, "Box it."),
        ("Repackager", "create:repackager", 1, "Rebox."),
        ("Stock Ticker", "create:stock_ticker", 1, "Request stock."),
        ("Track", "create:track", 32, "Train path."),
        ("Track Station", "create:track_station", 1, "Stop here."),
        ("Schedule", "create:schedule", 1, "Train plan."),
        ("Cart Assembler", "create:cart_assembler", 1, "Assemble cart."),
        ("Controller Rail", "create:controller_rail", 8, "Powered rail+."),
        ("Rope Pulley", "create:rope_pulley", 1, "Lift."),
        ("Elevator Pulley", "create:elevator_pulley", 1, "Floor lift."),
        ("Gantry Shaft", "create:gantry_shaft", 8, "Gantry spine."),
        ("Gantry Carriage", "create:gantry_carriage", 1, "Gantry ride."),
    ])
    return main


def build_network_side() -> list[dict]:
    s = 29
    main = chain(s, [
        ("Certus Crystal", "ae2:certus_quartz_crystal", 32, "Network quartz."),
        ("Charged Certus", "ae2:charged_certus_quartz_crystal", 16, "Charged."),
        ("Fluix Crystal", "ae2:fluix_crystal", 32, "Purple network."),
        ("Fluix Dust", "ae2:fluix_dust", 16, "Dusted fluix."),
        ("Silicon", "ae2:silicon", 32, "Chip base."),
        ("Sky Stone", "ae2:sky_stone_block", 32, "Meteor stone."),
        ("Smooth Sky Stone", "ae2:smooth_sky_stone_block", 16, "Controller shell."),
        ("Inscriber", "ae2:inscriber", 1, "Press circuits."),
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
        ("Energy Cell", "ae2:energy_cell", 2, "Buffer."),
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
        ("256k Item Cell", "ae2:item_storage_cell_256k", 1, "Archive."),
        ("1k Fluid Cell", "ae2:fluid_storage_cell_1k", 1, "Store fluids."),
        ("Interface", "ae2:interface", 2, "World bridge."),
        ("Import Bus", "ae2:import_bus", 4, "Pull in."),
        ("Export Bus", "ae2:export_bus", 4, "Push out."),
        ("Storage Bus", "ae2:storage_bus", 4, "Attach inventory."),
        ("Terminal", "ae2:terminal", 1, "Browse."),
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
        ("Codex Pages", "ninjacatskies:codex_page", 16, "Archive."),
        ("Whisker Codex", "ninjacatskies:whisker_codex", 1, "Always assign."),
    ])
    return main


def build_packaged_side() -> list[dict]:
    s = 31
    return chain(s, [
        ("Packaged Guide", "packagedauto:guide", 1, "Read the boxes."),
        ("Package Component", "packagedauto:package_component", 8, "Box guts."),
        ("ME Package Comp", "packagedauto:me_package_component", 4, "AE box guts."),
        ("Packager", "packagedauto:packager", 1, "Make packages."),
        ("Packager AE", "packagedauto:packager_ae", 1, "AE packager."),
        ("Packager Ext", "packagedauto:packager_extension", 2, "Extend packing."),
        ("Unpackager", "packagedauto:unpackager", 1, "Open packages."),
        ("Unpackager AE", "packagedauto:unpackager_ae", 1, "AE unpack."),
        ("Encoder", "packagedauto:encoder", 1, "Encode recipes."),
        ("Crafter", "packagedauto:crafter", 1, "Craft packages."),
        ("Crafter AE", "packagedauto:crafter_ae", 1, "AE craft."),
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
        ("Fluix Cable", "ae2:fluix_glass_cable", 16, "Wire it."),
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
        ("SPS Port", "mekanism:sps_port", 2, "SPS IO."),
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
        ("Enrichment Chamber", "mekanism:enrichment_chamber", 1, "Enrich."),
        ("Crusher", "mekanism:crusher", 1, "Crush."),
        ("Energized Smelter", "mekanism:energized_smelter", 1, "Power smelt."),
        ("Precision Sawmill", "mekanism:precision_sawmill", 1, "Saw."),
        ("Electrolytic Sep", "mekanism:electrolytic_separator", 1, "Split water."),
        ("Chemical Infuser", "mekanism:chemical_infuser", 1, "Mix chem."),
        ("Purification", "mekanism:purification_chamber", 1, "Purify."),
        ("Chem Injection", "mekanism:chemical_injection_chamber", 1, "Inject."),
        ("Osmium Compressor", "mekanism:osmium_compressor", 1, "Compress."),
        ("Combiner", "mekanism:combiner", 1, "Combine."),
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
        ("Saddle", "minecraft:saddle", 1, "Ride."),
        ("Name Tag Farm", "minecraft:name_tag", 2, "Name them."),
        ("Lead", "minecraft:lead", 4, "Tether."),
        ("Egg Stock", "minecraft:egg", 16, "Chicken tax."),
        ("Leather Stock", "minecraft:leather", 32, "Cow tax."),
        ("Wool Stock", "minecraft:white_wool", 32, "Sheep tax."),
        ("Beef Stock", "minecraft:beef", 32, "Meat."),
        ("Pork Stock", "minecraft:porkchop", 32, "More meat."),
        ("Chicken Stock", "minecraft:chicken", 32, "Fowl."),
        ("Mutton Stock", "minecraft:mutton", 32, "Sheep meat."),
        ("Rabbit Hide", "minecraft:rabbit_hide", 8, "Small hide."),
        ("Rabbit Foot", "minecraft:rabbit_foot", 2, "Brew luck."),
    ])
    side = grid_optional(s, [
        ("Zombie Head", "minecraft:zombie_head", 1, "Trophy."),
        ("Skeleton Skull", "minecraft:skeleton_skull", 1, "Trophy."),
        ("Creeper Head", "minecraft:creeper_head", 1, "Trophy."),
        ("Piglin Head", "minecraft:piglin_head", 1, "Trophy."),
        ("Dragon Head", "minecraft:dragon_head", 1, "Trophy."),
        ("Player Head", "minecraft:player_head", 1, "If obtained."),
    ], origin=(-3.0, 3.0), cols=3)
    return main + side


'''

MARKER = "\ndef build_shop() -> list[dict]:"
if "def build_crops_side()" not in text:
    if MARKER not in text:
        raise SystemExit("build_shop marker not found")
    text = text.replace(MARKER, "\n" + NEW_BUILDERS + MARKER, 1)

OLD_MAIN_TAIL = '''    write_chapter("21_decor", CH["decor"], GROUP_SIDE, 20, "minecraft:flower_pot", build_decor_side(), "Pad Decor")
    write_chapter("22_nether", CH["nether"], GROUP_SIDE, 21, "minecraft:netherrack", build_nether_side(), "Nether Foothold")
    write_chapter("23_end", CH["end"], GROUP_SIDE, 22, "minecraft:end_stone", build_end_side(), "End Foothold")
    write_lang()'''

NEW_MAIN_TAIL = '''    write_chapter("21_decor", CH["decor"], GROUP_SIDE, 20, "minecraft:flower_pot", build_decor_side(), "Pad Decor")
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
    write_lang()'''

if 'write_chapter("24_crops"' not in text:
    if OLD_MAIN_TAIL not in text:
        raise SystemExit("main tail not found")
    text = text.replace(OLD_MAIN_TAIL, NEW_MAIN_TAIL, 1)

TARGET.write_text(text, encoding="utf-8")
print("Patched", TARGET)
print("crops in file:", "def build_crops_side()" in text)
print("24_crops in main:", 'write_chapter("24_crops"' in text)
