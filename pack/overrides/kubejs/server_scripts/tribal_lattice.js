// Pack-only workshop uses. Standalone Tribal Power recipes remain self-contained.
// These are normal, synced recipes and appear in Tribal Power's JEI category.
ServerEvents.recipes(event => {
  if (!Platform.isLoaded('tribalpower')) return
  const lattice = (id, station, ingredient, result, count, attunement, seconds, pulse) => {
    event.custom({
      type: 'tribalpower:lattice', station: station,
      ingredient: { item: ingredient }, result: { id: result, count: count },
      attunement: attunement, seconds: seconds, pulse_per_second: pulse
    }).id('ninjacatskies:lattice/' + id)
  }
  lattice('lint_to_thread', 'echo_bind', 'voidloom:loom_lint', 'minecraft:string', 2, 'water', 3, 8)
  lattice('yarn_to_spiritweave', 'echo_bind', 'voidloom:void_yarn', 'tribalpower:spiritweave', 1, 'water', 4, 12)
  // Raw ore chunks stay in the Recover line; no Strand token or Braid Cord can be bypassed.
})
