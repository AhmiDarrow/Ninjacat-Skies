// Voidloom mesh identity — thread meshes catch the Loom's own scraps on top of the Ex Deorum tables.
// Additive only: Ex Deorum meshes are untouched; these lines fire only for voidloom meshes.
//   string mesh → Loom Lint (4 lint = 1 Void Yarn)
//   flint mesh  → Frayed Thread (Recover feeds the Kin stall economy, not only quests)
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
    // The March-soil copy below only sees datapack recipes, not these; give March soil its row directly.
    if (input === 'minecraft:dirt' && Platform.isLoaded('tribalpower')) sieve('tribalpower:march_soil', mesh, result, p, false)
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

  // Catch any datapack Ex Deorum item-meshes still left, then clone datapack dirt tables onto March soil.
  // (forEachRecipe does not see recipes added by scripts in this event; those write tags and March rows themselves.)
  const meshTags = {
    'exdeorum:string_mesh': 'ninjacatskies:meshes/string',
    'exdeorum:flint_mesh': 'ninjacatskies:meshes/flint',
    'exdeorum:iron_mesh': 'ninjacatskies:meshes/iron',
  }
  let rewritten = 0
  for (let type of ['exdeorum:sieve', 'exdeorum:compressed_sieve']) {
    event.forEachRecipe({ type: type }, r => {
      try {
        let mesh = r.json.get('mesh')
        if (!mesh || !mesh.isJsonObject() || !mesh.getAsJsonObject().has('item')) return
        let tag = meshTags[String(mesh.getAsJsonObject().get('item').getAsString())]
        if (!tag) return
        r.merge({ mesh: { tag: tag } })
        rewritten++
      } catch (err) {
        console.warn('[Ninjacat Skies] late mesh alias skipped for ' + r.getId() + ': ' + err)
      }
    })
  }
  if (rewritten) console.info('[Ninjacat Skies] late mesh alias rewrote ' + rewritten + ' leftover sieve tables')

  if (Platform.isLoaded('tribalpower')) {
    let cloned = 0
    event.forEachRecipe({ type: 'exdeorum:sieve' }, r => {
      try {
        let rid = String(r.getId())
        if (rid.indexOf('ninjacatskies:march/') === 0) return
        let ing = r.json.get('ingredient')
        if (!ing || !ing.isJsonObject() || !ing.getAsJsonObject().has('item')) return
        if (String(ing.getAsJsonObject().get('item').getAsString()) !== 'minecraft:dirt') return
        let copy = JSON.parse(r.json.toString())
        copy.ingredient = { item: 'tribalpower:march_soil' }
        let nid = rid.split(':').join('_').split('/').join('_')
        event.custom(copy).id('ninjacatskies:march/sieve_' + nid)
        cloned++
      } catch (err) {
        console.warn('[Ninjacat Skies] march soil sieve skipped for ' + r.getId() + ': ' + err)
      }
    })
    console.info('[Ninjacat Skies] March soil shares ' + cloned + ' dirt sieve tables')
  }
})
