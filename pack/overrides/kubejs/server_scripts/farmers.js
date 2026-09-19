// Rootbinders' kitchen — Farmer's Delight crops on a void pad.
// FD's cabbage and tomato only come from wild plants that generate in the world (and tomato seeds craft from a
// tomato you don't have yet — circular). Onion is fine: zombies drop it. So the missing seeds fall from the
// sieve alongside the vanilla ones, and cabbage leaf too, so the kitchen line is reachable from Root.
ServerEvents.recipes(event => {
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
      // Compressed sieves take the compressed block (Ex Deorum tag) and roll 9x — same shape as Ex Deorum's own tables.
      ingredient: compressed ? { tag: 'exdeorum:compressed/' + input.split(':')[1] } : { item: input },
      mesh: meshTier[mesh] ? { tag: meshTier[mesh] } : { item: mesh },
      result: { id: result, count: 1 },
      result_amount: { type: 'minecraft:binomial', n: compressed ? 9.0 : 1.0, p: p },
    }).id(`ninjacatskies:farmers/${compressed ? 'compressed_' : ''}${input.split(':')[1]}_${mesh.split(':')[1]}_${result.split(':')[1]}`)
  }
  const both = (input, mesh, result, p) => {
    sieve(input, mesh, result, p, false)
    sieve(input, mesh, result, p, true)
    if (input === 'minecraft:dirt' && Platform.isLoaded('tribalpower')) sieve('tribalpower:march_soil', mesh, result, p, false)
  }

  // Seeds from dirt, like the vanilla ones Ex Deorum already sieves. String mesh so Root can start.
  // voidloom_recipes.js rewrites these meshes to tier tags, so thread meshes share the same extras.
  ;[
    ['exdeorum:string_mesh', 0.05],
    ['exdeorum:flint_mesh', 0.07],
    ['exdeorum:iron_mesh', 0.09],
  ].forEach(row => {
    let m = row[0]
    let p = row[1]
    both('minecraft:dirt', m, 'farmersdelight:tomato_seeds', p)
    both('minecraft:dirt', m, 'farmersdelight:cabbage_seeds', p)
    both('minecraft:dirt', m, 'farmersdelight:rice', p)
  })

  // A cabbage seed grows cabbage, but the "from leaves" craft also wants leaves — let a leaf come off the sieve too.
  both('minecraft:dirt', 'exdeorum:flint_mesh', 'farmersdelight:cabbage_leaf', 0.05)

  // Onion is a zombie drop, but a seed on the sieve keeps a peaceful pad in the kitchen too.
  both('minecraft:dirt', 'exdeorum:flint_mesh', 'farmersdelight:onion', 0.04)
})
