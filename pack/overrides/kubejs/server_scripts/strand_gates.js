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
