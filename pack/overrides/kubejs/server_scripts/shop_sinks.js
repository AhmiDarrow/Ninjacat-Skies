// Soft skyblock utility sinks — frayed thread / void yarn conversions.
// Complements Frayed Thread Desk quest shop (quests consume Thread for bigger QoL).
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
})
