// Voidloom crafting — early Strand sinks
ServerEvents.recipes(event => {
  // Recover softlock: unravel kit Thread → string before spiders/wool exist.
  event.shapeless('3x minecraft:string', [
    'ninjacatskies:frayed_thread'
  ]).id('ninjacatskies:string_from_frayed_thread')

  // Early yarn — string only (no flint/pearl; hammers & sieves come later).
  // 4 string → 2 yarn so Recover does not eat the whole Thread stock.
  event.shapeless('2x voidloom:void_yarn', [
    'minecraft:string',
    'minecraft:string',
    'minecraft:string',
    'minecraft:string'
  ]).id('ninjacatskies:void_yarn_from_string')

  // Better yarn once pearls/chorus exist — same 2 string, but 2 yarn out (vs early 4→2).
  event.shapeless('2x voidloom:void_yarn', [
    'minecraft:string',
    'minecraft:string',
    'minecraft:ender_pearl'
  ]).id('ninjacatskies:void_yarn_from_pearl')

  event.shapeless('2x voidloom:void_yarn', [
    'minecraft:string',
    'minecraft:string',
    'minecraft:chorus_fruit'
  ]).id('ninjacatskies:void_yarn_from_chorus')

  // Early slime for Binding Knot — pad compost before sieve luck / bees.
  event.shapeless('minecraft:slime_ball', [
    'minecraft:dirt',
    'minecraft:dirt',
    'minecraft:wheat_seeds',
    'minecraft:bone_meal'
  ]).id('ninjacatskies:slime_from_pad_compost')

  event.shaped('voidloom:binding_knot', [
    ' Y ',
    'YSY',
    ' Y '
  ], {
    Y: 'voidloom:void_yarn',
    S: 'minecraft:slime_ball'
  })

  event.shaped('voidloom:thread_mesh_string', [
    'SSS',
    'SYS',
    'SSS'
  ], {
    S: 'minecraft:string',
    Y: 'voidloom:void_yarn'
  })

  event.shaped('voidloom:thread_mesh_flint', [
    'FFF',
    'FMF',
    'FFF'
  ], {
    F: 'minecraft:flint',
    M: 'voidloom:thread_mesh_string'
  })

  event.shaped('voidloom:thread_mesh_iron', [
    'III',
    'IMI',
    'III'
  ], {
    I: 'minecraft:iron_ingot',
    M: 'voidloom:thread_mesh_flint'
  })

  // No diamond/netherite voidloom meshes exist — stop at iron

  // Stone-tier hammer (matches Tiers.STONE) — iron would softlock Recover before sieve iron.
  event.shaped('voidloom:spindle_hammer', [
    ' CC',
    ' SC',
    'S  '
  ], {
    C: 'minecraft:cobblestone',
    S: 'minecraft:stick'
  })

  event.shaped('voidloom:spindle_crook', [
    'SS ',
    ' S ',
    ' S '
  ], {
    S: 'minecraft:stick'
  })

  event.shaped('voidloom:loomframe', [
    'PPP',
    'PYP',
    'PPP'
  ], {
    P: '#minecraft:planks',
    Y: 'voidloom:binding_knot'
  }).id('ninjacatskies:loomframe_bound')

  // Alternate loomframe — logs + void yarn
  event.shaped('voidloom:loomframe', [
    'LLL',
    'LYL',
    'LLL'
  ], {
    L: '#minecraft:logs',
    Y: 'voidloom:void_yarn'
  }).id('ninjacatskies:loomframe_yarn')

  event.shaped('voidloom:tension_barrel', [
    'PSP',
    'PYP',
    'PPP'
  ], {
    P: '#minecraft:planks',
    S: 'minecraft:string',
    Y: 'voidloom:void_yarn'
  })
})

ServerEvents.tags('item', event => {
  // Wire voidloom meshes into Ex Deorum sieve mesh tag
  event.add('exdeorum:sieve_meshes', 'voidloom:thread_mesh_string')
  event.add('exdeorum:sieve_meshes', 'voidloom:thread_mesh_flint')
  event.add('exdeorum:sieve_meshes', 'voidloom:thread_mesh_iron')
  event.add('c:meshes', 'voidloom:thread_mesh_string')
  event.add('c:meshes', 'voidloom:thread_mesh_flint')
  event.add('c:meshes', 'voidloom:thread_mesh_iron')

  // Tier aliases so voidloom meshes share Ex Deorum drop tables
  event.add('ninjacatskies:meshes/string', 'exdeorum:string_mesh')
  event.add('ninjacatskies:meshes/string', 'voidloom:thread_mesh_string')
  event.add('ninjacatskies:meshes/flint', 'exdeorum:flint_mesh')
  event.add('ninjacatskies:meshes/flint', 'voidloom:thread_mesh_flint')
  event.add('ninjacatskies:meshes/iron', 'exdeorum:iron_mesh')
  event.add('ninjacatskies:meshes/iron', 'voidloom:thread_mesh_iron')
})

// Share sieve (and compressed sieve) drops between Ex Deorum and voidloom meshes
ServerEvents.recipes(event => {
  const meshAliases = {
    'exdeorum:string_mesh': '#ninjacatskies:meshes/string',
    'exdeorum:flint_mesh': '#ninjacatskies:meshes/flint',
    'exdeorum:iron_mesh': '#ninjacatskies:meshes/iron',
  }
  for (const [from, to] of Object.entries(meshAliases)) {
    event.replaceInput({ type: 'exdeorum:sieve' }, from, to)
    event.replaceInput({ type: 'exdeorum:compressed_sieve' }, from, to)
  }
})
