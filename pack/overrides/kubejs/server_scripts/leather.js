// Leather on a void pad — no cows, and Mystical cow seeds want leather to craft.
// Zombies already drop rotten flesh; smelt (or campfire) it. Flint mesh and up
// also pull a little leather from dirt, so a peaceful pad is not stuck on the Kin stalls.
ServerEvents.recipes(event => {
  event.smelting('minecraft:leather', 'minecraft:rotten_flesh')
    .xp(0.1)
    .id('ninjacatskies:leather/smelt_rotten_flesh')
  event.campfireCooking('minecraft:leather', 'minecraft:rotten_flesh')
    .xp(0.1)
    .cookingTime(600)
    .id('ninjacatskies:leather/campfire_rotten_flesh')

  // event.forEachRecipe only walks datapack recipes, never ones added in this event, so the mesh-tier
  // rewrite in voidloom_recipes.js and the March-soil copy in voidloom_sieve.js cannot reach these rows.
  // Write the tier tag (Ex Deorum mesh + matching thread mesh) and the March-soil row here instead.
  let meshTier = {
    'exdeorum:string_mesh': 'ninjacatskies:meshes/string',
    'exdeorum:flint_mesh': 'ninjacatskies:meshes/flint',
    'exdeorum:iron_mesh': 'ninjacatskies:meshes/iron',
  }
  const sieve = (input, mesh, result, p, compressed) => {
    event.custom({
      type: compressed ? 'exdeorum:compressed_sieve' : 'exdeorum:sieve',
      ingredient: compressed ? { tag: 'exdeorum:compressed/' + input.split(':')[1] } : { item: input },
      mesh: meshTier[mesh] ? { tag: meshTier[mesh] } : { item: mesh },
      result: { id: result, count: 1 },
      result_amount: { type: 'minecraft:binomial', n: compressed ? 9.0 : 1.0, p: p },
    }).id(`ninjacatskies:leather/${compressed ? 'compressed_' : ''}${input.split(':')[1]}_${mesh.split(':')[1]}_${result.split(':')[1]}`)
  }
  const both = (input, mesh, result, p) => {
    sieve(input, mesh, result, p, false)
    sieve(input, mesh, result, p, true)
    if (input === 'minecraft:dirt' && Platform.isLoaded('tribalpower')) sieve('tribalpower:march_soil', mesh, result, p, false)
  }

  ;[
    ['exdeorum:flint_mesh', 0.03],
    ['exdeorum:iron_mesh', 0.05],
  ].forEach(row => {
    both('minecraft:dirt', row[0], 'minecraft:leather', row[1])
  })
})
