// Progression gates — original Ninjacat Skies.
// Strand tokens are NOT crafted: each Strand chapter ends in a Knot quest that rewards the token,
// and the token is seated at a Tension Post (ninjacatskies). Braid Cord and the Spindle Loom Fragment
// are spun at the Post too (see braid_gates.js for the assembler gate).
ServerEvents.recipes(event => {
  // Tension Post — logs around a Binding Knot, a scrap of Thread on top.
  event.shaped('ninjacatskies:tension_post', [
    ' T ',
    'LKL',
    ' L '
  ], {
    T: 'ninjacatskies:frayed_thread',
    L: '#minecraft:logs',
    K: 'voidloom:binding_knot'
  }).id('ninjacatskies:tension_post')

  // Soft AE2 controller gate: needs the Loom's binder.
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

  // First AE2 inscriber presses — AE2 only duplicates an existing press (iron block + press).
  // Meteorites do not generate on this void pad, so the first copy is a Binding-Knot craft.
  event.shaped('ae2:silicon_press', [
    ' I ',
    'KBK',
    ' Q '
  ], {
    I: 'minecraft:iron_block',
    K: 'voidloom:binding_knot',
    B: 'minecraft:iron_ingot',
    Q: 'minecraft:quartz'
  }).id('ninjacatskies:ae2_silicon_press_first')

  event.shaped('ae2:logic_processor_press', [
    ' I ',
    'KBK',
    ' G '
  ], {
    I: 'minecraft:iron_block',
    K: 'voidloom:binding_knot',
    B: 'minecraft:iron_ingot',
    G: 'minecraft:gold_ingot'
  }).id('ninjacatskies:ae2_logic_press_first')

  event.shaped('ae2:calculation_processor_press', [
    ' I ',
    'KBK',
    ' C '
  ], {
    I: 'minecraft:iron_block',
    K: 'voidloom:binding_knot',
    B: 'minecraft:iron_ingot',
    C: 'ae2:certus_quartz_crystal'
  }).id('ninjacatskies:ae2_calculation_press_first')

  event.shaped('ae2:engineering_processor_press', [
    ' I ',
    'KBK',
    ' D '
  ], {
    I: 'minecraft:iron_block',
    K: 'voidloom:binding_knot',
    B: 'minecraft:iron_ingot',
    D: 'minecraft:diamond'
  }).id('ninjacatskies:ae2_engineering_press_first')

  // Soft Create precision_mechanism gate — Binding Knot at the heart.
  // Sequenced assembly removed so the Knot is the intentional soft gate; hand-shaped craft replaces it.
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

  // Belt and braces: if any old token / fragment / braid recipe survives a datapack, remove it.
  event.remove({ output: /ninjacatskies:strand_token_.*/ })
  event.remove({ output: 'ninjacatskies:spindle_loom_fragment' })
  event.remove({ output: 'ninjacatskies:braid_cord' })
})

ServerEvents.tags('item', event => {
  event.add('exdeorum:hammers', 'voidloom:spindle_hammer')
  event.add('minecraft:tools', 'voidloom:spindle_hammer')
  event.add('c:tools/hammers', 'voidloom:spindle_hammer')
  // spindle_crook also tagged via voidloom datapack data/exdeorum/tags/item/crooks.json
  event.add('exdeorum:crooks', 'voidloom:spindle_crook')
})
