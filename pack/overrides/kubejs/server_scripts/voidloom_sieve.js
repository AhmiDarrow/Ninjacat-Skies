// Voidloom mesh identity — thread meshes catch the Loom's own scraps on top of the Ex Deorum tables.
// Additive only: Ex Deorum meshes are untouched; these lines fire only for voidloom meshes.
//   string mesh → Loom Lint (4 lint = 1 Void Yarn)
//   flint mesh  → Frayed Thread (Recover feeds the Desk economy, not only quests)
//   iron mesh   → Strand Filament (the Loom-native strand Braid Cord is spun from)
ServerEvents.recipes(event => {
  const sieve = (input, mesh, result, p, compressed) => {
    event.custom({
      type: compressed ? 'exdeorum:compressed_sieve' : 'exdeorum:sieve',
      // Compressed sieves take the compressed block (Ex Deorum tag) and roll 9x — same shape as Ex Deorum's own tables.
      ingredient: compressed ? { tag: 'exdeorum:compressed/' + input.split(':')[1] } : { item: input },
      mesh: { item: mesh },
      result: { id: result, count: 1 },
      result_amount: { type: 'minecraft:binomial', n: compressed ? 9.0 : 1.0, p: p },
    }).id(`ninjacatskies:sieve/${compressed ? 'compressed_' : ''}${input.split(':')[1]}_${mesh.split(':')[1]}_${result.split(':')[1]}`)
  }
  const both = (input, mesh, result, p) => {
    sieve(input, mesh, result, p, false)
    sieve(input, mesh, result, p, true)
  }

  both('minecraft:dirt', 'voidloom:thread_mesh_string', 'voidloom:loom_lint', 0.10)
  both('minecraft:dirt', 'voidloom:thread_mesh_flint', 'voidloom:loom_lint', 0.10)
  both('minecraft:dirt', 'voidloom:thread_mesh_iron', 'voidloom:loom_lint', 0.10)

  both('minecraft:dirt', 'voidloom:thread_mesh_flint', 'ninjacatskies:frayed_thread', 0.03)
  both('minecraft:gravel', 'voidloom:thread_mesh_flint', 'ninjacatskies:frayed_thread', 0.03)
  both('minecraft:dirt', 'voidloom:thread_mesh_iron', 'ninjacatskies:frayed_thread', 0.04)
  both('minecraft:gravel', 'voidloom:thread_mesh_iron', 'ninjacatskies:frayed_thread', 0.04)

  both('minecraft:gravel', 'voidloom:thread_mesh_iron', 'voidloom:strand_filament', 0.02)
  both('minecraft:sand', 'voidloom:thread_mesh_iron', 'voidloom:strand_filament', 0.015)
  both('exdeorum:dust', 'voidloom:thread_mesh_iron', 'voidloom:strand_filament', 0.02)

  // Lint back into yarn — the Loomframe's slow yarn engine.
  event.shapeless('voidloom:void_yarn', [
    'voidloom:loom_lint', 'voidloom:loom_lint', 'voidloom:loom_lint', 'voidloom:loom_lint'
  ]).id('ninjacatskies:void_yarn_from_lint')
})
