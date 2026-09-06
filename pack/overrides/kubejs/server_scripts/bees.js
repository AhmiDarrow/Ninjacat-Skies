// Colony-keepers — bees in a world with no trees to find them in.
// Productive Bees nests normally only generate in worldgen; on a void pad you build one: a ring of the
// material the bee likes around a small flower, place it, and wait. Placed nests spawn their bee on their own.
// The oak wood nest also spawns plain honey bees so Beehives / honeycomb / breeding all start from the pad.
ServerEvents.recipes(event => {
  const ring = (nest, material, id) => {
    event.shaped(nest, [
      'MMM',
      'MFM',
      'MMM'
    ], {
      M: material,
      F: '#minecraft:small_flowers'
    }).id(`ninjacatskies:bees/${id}`)
  }

  // Wood — carpenter bees (and plain bees from oak)
  ring('productivebees:oak_wood_nest', '#minecraft:oak_logs', 'oak_wood_nest')
  ring('productivebees:birch_wood_nest', '#minecraft:birch_logs', 'birch_wood_nest')
  ring('productivebees:spruce_wood_nest', '#minecraft:spruce_logs', 'spruce_wood_nest')
  ring('productivebees:dark_oak_wood_nest', '#minecraft:dark_oak_logs', 'dark_oak_wood_nest')
  ring('productivebees:acacia_wood_nest', '#minecraft:acacia_logs', 'acacia_wood_nest')
  ring('productivebees:jungle_wood_nest', '#minecraft:jungle_logs', 'jungle_wood_nest')
  ring('productivebees:cherry_wood_nest', '#minecraft:cherry_logs', 'cherry_wood_nest')
  ring('productivebees:bumble_bee_nest', 'minecraft:hay_block', 'bumble_bee_nest')

  // Ground — mining, digger, mason, leafcutter, reed
  ring('productivebees:coarse_dirt_nest', 'minecraft:coarse_dirt', 'coarse_dirt_nest')
  ring('productivebees:gravel_nest', 'minecraft:gravel', 'gravel_nest')
  ring('productivebees:sand_nest', 'minecraft:sand', 'sand_nest')
  ring('productivebees:stone_nest', 'minecraft:stone', 'stone_nest')
  ring('productivebees:sugar_cane_nest', 'minecraft:sugar_cane', 'sugar_cane_nest')
  ring('productivebees:slimy_nest', 'minecraft:slime_block', 'slimy_nest')
  ring('productivebees:snow_nest', 'minecraft:snow_block', 'snow_nest')

  // Footholds — Nether and End bees once you have the blocks
  ring('productivebees:glowstone_nest', 'minecraft:glowstone', 'glowstone_nest')
  ring('productivebees:nether_quartz_nest', 'minecraft:quartz_block', 'nether_quartz_nest')
  ring('productivebees:nether_brick_nest', 'minecraft:nether_bricks', 'nether_brick_nest')
  ring('productivebees:soul_sand_nest', 'minecraft:soul_sand', 'soul_sand_nest')
  ring('productivebees:nether_gold_nest', 'minecraft:gilded_blackstone', 'nether_gold_nest')
  ring('productivebees:end_stone_nest', 'minecraft:end_stone', 'end_stone_nest')
  ring('productivebees:obsidian_nest', 'minecraft:obsidian', 'obsidian_nest')

  // Plain honey bees from an oak nest — the root of every breeding line.
  event.custom({
    type: 'productivebees:bee_spawning',
    ingredient: { item: 'productivebees:oak_wood_nest' },
    results: ['minecraft:bee'],
    biomes: '#c:is_overworld'
  }).id('ninjacatskies:bees/oak_wood_nest_honey_bee')
  event.custom({
    type: 'productivebees:bee_spawning',
    ingredient: { item: 'productivebees:bumble_bee_nest' },
    results: ['minecraft:bee'],
    biomes: '#c:is_overworld'
  }).id('ninjacatskies:bees/bumble_bee_nest_honey_bee')

  // A vanilla bee nest for the pad, so a colony can be moved in without an Advanced Beehive first.
  event.shaped('minecraft:bee_nest', [
    'PPP',
    'FFF',
    'PPP'
  ], {
    P: '#minecraft:planks',
    F: '#minecraft:small_flowers'
  }).id('ninjacatskies:bees/bee_nest')
})
