// Progression helpers — original Ninjacat Skies gates
// Loom Braid pair crafts + assembler soft-gate live in braid_gates.js (no Tribal Hum dupes).
ServerEvents.recipes(event => {
  // Strand tokens — distinct flavored crafts (frayed_thread x2 + strand items)
  const tokens = {
    soil: ['minecraft:dirt', 'minecraft:oak_sapling'],
    stone: ['minecraft:cobblestone', 'minecraft:flint'],
    sprout: ['minecraft:wheat_seeds', 'minecraft:bone_meal'],
    claw: ['minecraft:iron_ingot', 'minecraft:string'],
    spark: ['minecraft:redstone', 'minecraft:coal'],
    clock: ['create:cogwheel', 'minecraft:clock'],
    swarm: ['minecraft:honeycomb', 'minecraft:glass_bottle'],
    sigil: ['minecraft:amethyst_shard', 'minecraft:book'],
    spindle: ['ae2:fluix_crystal', 'voidloom:binding_knot'],
  }

  Object.entries(tokens).forEach(([name, extras]) => {
    event.shapeless(`ninjacatskies:strand_token_${name}`, [
      'ninjacatskies:frayed_thread',
      'ninjacatskies:frayed_thread',
      ...extras,
    ]).id(`ninjacatskies:strand_token_${name}_manual`)
  })

  // Soft AE2 controller gate: needs spindle-flavored binder
  event.remove({ output: 'ae2:controller' })
  event.shaped('ae2:controller', [
    'SFS',
    'FBF',
    'SFS'
  ], {
    S: 'ae2:smooth_sky_stone_block',
    F: 'ae2:fluix_block',
    B: 'voidloom:binding_knot'
  }).id('ninjacatskies:ae2_controller_bound')

  // Soft Create precision_mechanism gate — Binding Knot required.
  // Sequenced assembly removed so the Loom binder is the intentional Soft gate;
  // hand-shaped craft replaces it for early pads without a full Create line.
  event.remove({ id: 'create:sequenced_assembly/precision_mechanism' })
  event.shaped('create:precision_mechanism', [
    'CLC',
    'GBG',
    'NIN'
  ], {
    C: 'create:cogwheel',
    L: 'create:large_cogwheel',
    G: '#c:plates/gold',
    B: 'voidloom:binding_knot',
    N: '#c:nuggets/iron',
    I: 'create:andesite_alloy'
  }).id('ninjacatskies:precision_mechanism_bound')

  // End trophy — nine Strand tokens + March-attuned footing (Tribal Reweave proof)
  if (Item.exists('tribalpower:march_stone')) {
    event.shapeless('ninjacatskies:spindle_loom_fragment', [
      'ninjacatskies:strand_token_soil',
      'ninjacatskies:strand_token_stone',
      'ninjacatskies:strand_token_sprout',
      'ninjacatskies:strand_token_claw',
      'ninjacatskies:strand_token_spark',
      'ninjacatskies:strand_token_clock',
      'ninjacatskies:strand_token_swarm',
      'ninjacatskies:strand_token_sigil',
      'ninjacatskies:strand_token_spindle',
      'tribalpower:march_stone',
    ]).id('ninjacatskies:spindle_loom_fragment')
  }
})

ServerEvents.tags('item', event => {
  event.add('exdeorum:hammers', 'voidloom:spindle_hammer')
  event.add('minecraft:tools', 'voidloom:spindle_hammer')
  event.add('c:tools/hammers', 'voidloom:spindle_hammer')
  // spindle_crook also tagged via voidloom datapack data/exdeorum/tags/item/crooks.json
  event.add('exdeorum:crooks', 'voidloom:spindle_crook')
})
