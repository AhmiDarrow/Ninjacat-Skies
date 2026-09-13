// Wild pad-runners live in the March. Flame birds wear Ember Wastes; gysahl is packed in via datapack.

EntityEvents.spawned('chococraft:chocobo', event => {
  const entity = event.entity
  if (!entity || entity.level.clientSide) return
  let biome = ''
  try {
    biome = String(entity.block.biomeId || '')
  } catch (e) {
    try { biome = String(entity.level.getBiome(entity.block.pos)) } catch (e2) { return }
  }
  if (biome.indexOf('march_ember_wastes') < 0) return
  entity.mergeNbt({ Color: 9, Grade: 3 })
})
