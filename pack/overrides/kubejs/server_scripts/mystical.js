// Rootbinders — Mystical Agriculture on a void pad.
// Inferium and Prosperity essences smelt from c:ores/inferium and c:ores/prosperity — worldgen ores that
// never spawn in the void, and Prosperity has no mob drop. Without this the whole essence-seed line (and the
// deep-crops half of Colony) is unreachable. So the ores fall from the sieve, like every other ore here:
// Inferium is common (it is the floor of the whole system); Prosperity is rarer (it gates seed bases).
ServerEvents.recipes(event => {
  const sieve = (input, mesh, result, p, compressed) => {
    event.custom({
      type: compressed ? 'exdeorum:compressed_sieve' : 'exdeorum:sieve',
      // Compressed sieves take the compressed block (Ex Deorum tag) and roll 7x — same shape as Ex Deorum's own tables.
      ingredient: compressed ? { tag: 'exdeorum:compressed/' + input.split(':')[1] } : { item: input },
      mesh: { item: mesh },
      result: { id: result, count: 1 },
      result_amount: { type: 'minecraft:binomial', n: compressed ? 7.0 : 1.0, p: p },
    }).id(`ninjacatskies:mystical/${compressed ? 'compressed_' : ''}${input.split(':')[1]}_${mesh.split(':')[1]}_${result.split(':')[1]}`)
  }
  const both = (input, mesh, result, p) => {
    sieve(input, mesh, result, p, false)
    sieve(input, mesh, result, p, true)
  }

  // Inferium ore — the floor. Available from a string mesh so Root can start it, richer with better meshes.
  both('minecraft:dirt', 'exdeorum:string_mesh', 'mysticalagriculture:inferium_ore', 0.06)
  both('minecraft:dirt', 'exdeorum:flint_mesh', 'mysticalagriculture:inferium_ore', 0.10)
  both('minecraft:dirt', 'exdeorum:iron_mesh', 'mysticalagriculture:inferium_ore', 0.14)

  // Prosperity ore — rarer; it is what gates every seed base. Gravel and sand, flint mesh and up.
  both('minecraft:gravel', 'exdeorum:flint_mesh', 'mysticalagriculture:prosperity_ore', 0.04)
  both('minecraft:gravel', 'exdeorum:iron_mesh', 'mysticalagriculture:prosperity_ore', 0.06)
  both('minecraft:sand', 'exdeorum:iron_mesh', 'mysticalagriculture:prosperity_ore', 0.05)

  // Voidloom thread meshes catch them too, so the Loomframe automates the essence floor.
  both('minecraft:dirt', 'voidloom:thread_mesh_flint', 'mysticalagriculture:inferium_ore', 0.10)
  both('minecraft:dirt', 'voidloom:thread_mesh_iron', 'mysticalagriculture:inferium_ore', 0.14)
  both('minecraft:gravel', 'voidloom:thread_mesh_iron', 'mysticalagriculture:prosperity_ore', 0.06)
})
