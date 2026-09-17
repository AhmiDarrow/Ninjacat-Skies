// Soft skyblock utility sinks — frayed thread / void yarn conversions.
// Complements Hall Kin stalls (quests consume Thread for bigger QoL).
ServerEvents.recipes(event => {
  event.shapeless('4x minecraft:dirt', [
    'ninjacatskies:frayed_thread',
    'ninjacatskies:frayed_thread',
    'ninjacatskies:frayed_thread',
    'ninjacatskies:frayed_thread',
    'ninjacatskies:frayed_thread',
    'ninjacatskies:frayed_thread',
    'ninjacatskies:frayed_thread',
    'ninjacatskies:frayed_thread',
    'minecraft:cobblestone'
  ]).id('ninjacatskies:sink_dirt_from_thread')

  event.shapeless('2x minecraft:cobblestone', [
    'ninjacatskies:frayed_thread',
    'ninjacatskies:frayed_thread',
    'ninjacatskies:frayed_thread',
    'ninjacatskies:frayed_thread',
    'minecraft:dirt',
    'minecraft:flint'
  ]).id('ninjacatskies:sink_cobble_from_thread')

  event.shapeless('minecraft:oak_sapling', [
    'ninjacatskies:frayed_thread',
    'ninjacatskies:frayed_thread',
    'minecraft:wheat_seeds',
    'minecraft:bone_meal'
  ]).id('ninjacatskies:sink_sapling_from_thread')

  // Lossy reverse — never 1:1 with early 4 string → 2 yarn (that loop doubled string).
  event.shapeless('minecraft:string', [
    'voidloom:void_yarn'
  ]).id('ninjacatskies:sink_string_from_yarn')

  event.shapeless('minecraft:bone_meal', [
    'ninjacatskies:frayed_thread',
    'minecraft:rotten_flesh'
  ]).id('ninjacatskies:sink_bonemeal_from_thread')

  // Cheap flint once gravel exists (mesh upgrades / Ex Deorum).
  event.shapeless('minecraft:flint', [
    'ninjacatskies:frayed_thread',
    'minecraft:gravel'
  ]).id('ninjacatskies:sink_flint_from_thread')

  // Real loom banner pattern (BannerPatternItem + clowderhall:strand datapack).
  event.shapeless('clowderhall:strand_banner_pattern', [
    'minecraft:paper',
    'ninjacatskies:frayed_thread',
    'minecraft:cyan_dye'
  ]).id('ninjacatskies:strand_banner_pattern')

  // Squid never spawn on the pad. Charcoal + bottle is the journal / book-and-quill ink.
  event.shapeless('minecraft:ink_sac', [
    'minecraft:charcoal',
    'minecraft:glass_bottle'
  ]).id('ninjacatskies:ink_from_charcoal')

  // End island is gone. Chorus (Spark stall) and pearls around a Binding Knot make End Stone.
  event.shaped('8x minecraft:end_stone', [
    'CPC',
    'PBP',
    'CPC'
  ], {
    C: 'minecraft:chorus_fruit',
    P: 'minecraft:ender_pearl',
    B: 'voidloom:binding_knot'
  }).id('ninjacatskies:end_stone_from_chorus')

  // Ice in the kit does not vanilla-craft snowballs.
  event.shapeless('4x minecraft:snowball', [
    'minecraft:ice'
  ]).id('ninjacatskies:snowball_from_ice')
})
