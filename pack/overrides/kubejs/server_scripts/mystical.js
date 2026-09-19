// Rootbinders — Mystical Agriculture on a void pad.
// Inferium and Prosperity essences smelt from c:ores/inferium and c:ores/prosperity — worldgen ores that
// never spawn in the void, and Prosperity has no mob drop. Without this the whole essence-seed line (and the
// deep-crops half of Colony) is unreachable. So the ores fall from the sieve, like every other ore here:
// Inferium is common (it is the floor of the whole system); Prosperity is rarer (it gates seed bases).
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
    }).id(`ninjacatskies:mystical/${compressed ? 'compressed_' : ''}${input.split(':')[1]}_${mesh.split(':')[1]}_${result.split(':')[1]}`)
  }
  const both = (input, mesh, result, p) => {
    sieve(input, mesh, result, p, false)
    sieve(input, mesh, result, p, true)
    if (input === 'minecraft:dirt' && Platform.isLoaded('tribalpower')) sieve('tribalpower:march_soil', mesh, result, p, false)
  }

  // Inferium ore — the floor. Available from a string mesh so Root can start it, richer with better meshes.
  both('minecraft:dirt', 'exdeorum:string_mesh', 'mysticalagriculture:inferium_ore', 0.06)
  both('minecraft:dirt', 'exdeorum:flint_mesh', 'mysticalagriculture:inferium_ore', 0.10)
  both('minecraft:dirt', 'exdeorum:iron_mesh', 'mysticalagriculture:inferium_ore', 0.14)

  // Prosperity ore — rarer; it is what gates every seed base. Gravel and sand, flint mesh and up.
  both('minecraft:gravel', 'exdeorum:flint_mesh', 'mysticalagriculture:prosperity_ore', 0.04)
  both('minecraft:gravel', 'exdeorum:iron_mesh', 'mysticalagriculture:prosperity_ore', 0.06)
  both('minecraft:sand', 'exdeorum:iron_mesh', 'mysticalagriculture:prosperity_ore', 0.05)
})
