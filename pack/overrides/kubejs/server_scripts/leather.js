// Leather on a void pad — no cows, and Mystical cow seeds want leather to craft.
// Zombies already drop rotten flesh; smelt (or campfire) it. Flint mesh and up
// also pull a little leather from dirt, so a peaceful pad is not stuck on the Desk.
ServerEvents.recipes(event => {
  event.smelting('minecraft:leather', 'minecraft:rotten_flesh')
    .xp(0.1)
    .id('ninjacatskies:leather/smelt_rotten_flesh')
  event.campfireCooking('minecraft:leather', 'minecraft:rotten_flesh')
    .xp(0.1)
    .cookingTime(600)
    .id('ninjacatskies:leather/campfire_rotten_flesh')

  const sieve = (input, mesh, result, p, compressed) => {
    event.custom({
      type: compressed ? 'exdeorum:compressed_sieve' : 'exdeorum:sieve',
      ingredient: compressed ? { tag: 'exdeorum:compressed/' + input.split(':')[1] } : { item: input },
      mesh: { item: mesh },
      result: { id: result, count: 1 },
      result_amount: { type: 'minecraft:binomial', n: compressed ? 9.0 : 1.0, p: p },
    }).id(`ninjacatskies:leather/${compressed ? 'compressed_' : ''}${input.split(':')[1]}_${mesh.split(':')[1]}_${result.split(':')[1]}`)
  }
  const both = (input, mesh, result, p) => {
    sieve(input, mesh, result, p, false)
    sieve(input, mesh, result, p, true)
  }

  ;[
    ['exdeorum:flint_mesh', 0.03],
    ['exdeorum:iron_mesh', 0.05],
    ['voidloom:thread_mesh_flint', 0.03],
    ['voidloom:thread_mesh_iron', 0.05],
  ].forEach(row => {
    both('minecraft:dirt', row[0], 'minecraft:leather', row[1])
  })
})
