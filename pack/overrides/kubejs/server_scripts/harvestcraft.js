// HarvestCraft gardens and fruit trees are biome worldgen. They never appear on a void pad.
// Gardens drop the crop seeds when broken; a few kitchen saplings cover Food Extended starters.
ServerEvents.recipes(event => {
  const sieve = (input, mesh, result, p, compressed) => {
    event.custom({
      type: compressed ? 'exdeorum:compressed_sieve' : 'exdeorum:sieve',
      ingredient: compressed ? { tag: 'exdeorum:compressed/' + input.split(':')[1] } : { item: input },
      mesh: { item: mesh },
      result: { id: result, count: 1 },
      result_amount: { type: 'minecraft:binomial', n: compressed ? 9.0 : 1.0, p: p },
    }).id(`ninjacatskies:harvestcraft/${compressed ? 'compressed_' : ''}${input.split(':')[1]}_${mesh.split(':')[1]}_${result.split(':')[1]}`)
  }
  const both = (input, mesh, result, p) => {
    sieve(input, mesh, result, p, false)
    sieve(input, mesh, result, p, true)
  }

  const gardenMeshes = [
    ['exdeorum:string_mesh', 0.04],
    ['exdeorum:flint_mesh', 0.06],
    ['exdeorum:iron_mesh', 0.08],
    ['voidloom:thread_mesh_string', 0.04],
    ['voidloom:thread_mesh_flint', 0.06],
    ['voidloom:thread_mesh_iron', 0.08],
  ]
  const gardens = [
    'pamhc2crops:aridgarden',
    'pamhc2crops:frostgarden',
    'pamhc2crops:shadedgarden',
    'pamhc2crops:soggygarden',
    'pamhc2crops:tropicalgarden',
    'pamhc2crops:windygarden',
  ]
  gardenMeshes.forEach(row => {
    gardens.forEach(garden => {
      both('minecraft:dirt', row[0], garden, row[1])
    })
  })

  const saplings = [
    'pamhc2trees:apple_sapling',
    'pamhc2trees:avocado_sapling',
    'pamhc2trees:cinnamon_sapling',
    'pamhc2trees:coconut_sapling',
    'pamhc2trees:lemon_sapling',
    'pamhc2trees:maple_sapling',
    'pamhc2trees:olive_sapling',
    'pamhc2trees:orange_sapling',
    'pamhc2trees:peach_sapling',
    'pamhc2trees:peppercorn_sapling',
    'pamhc2trees:vanillabean_sapling',
  ]
  ;[
    ['exdeorum:iron_mesh', 0.03],
    ['voidloom:thread_mesh_iron', 0.03],
  ].forEach(row => {
    saplings.forEach(sapling => {
      both('minecraft:dirt', row[0], sapling, row[1])
    })
  })

  // No cows on the pad. Coconut (iron-mesh dirt) plus freshwater is kitchen milk.
  // Tools already return themselves (ItemPamTool remainder); do not add a second remainder here.
  event.shapeless('4x pamhc2foodcore:freshmilkitem', [
    'pamhc2trees:coconutitem',
    'pamhc2foodcore:freshwateritem',
  ]).id('ninjacatskies:harvestcraft/coconut_freshmilk')
  event.shapeless('minecraft:milk_bucket', [
    'minecraft:bucket',
    'pamhc2foodcore:freshmilkitem',
    'pamhc2foodcore:freshmilkitem',
    'pamhc2foodcore:freshmilkitem',
    'pamhc2foodcore:freshmilkitem',
    'pamhc2foodcore:freshmilkitem',
    'pamhc2foodcore:freshmilkitem',
    'pamhc2foodcore:freshmilkitem',
    'pamhc2foodcore:freshmilkitem',
  ]).id('ninjacatskies:harvestcraft/freshmilk_bucket')
})

ServerEvents.tags('item', event => {
  // Fried rice and mayo ask for eggs. Silken tofu is the pad stand-in until chickens exist.
  event.add('c:egg', 'pamhc2foodextended:silkentofuitem')
  event.add('c:egg/egg', 'pamhc2foodextended:silkentofuitem')
})
