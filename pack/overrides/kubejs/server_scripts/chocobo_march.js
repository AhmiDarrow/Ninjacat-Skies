// Wild pad-runners live in the March. Ember Wastes should hatch Flame, not yellow.
// Reborn only paints Flame in the Nether; the wastes are still The March.

let ChocoColor
try {
  ChocoColor = Java.loadClass('tk.darrow.chocobosreborn.breed.ChocoboColor')
} catch (e) {}

EntityEvents.spawned('chocobosreborn:chocobo', event => {
  if (!event.server) return
  let entity = event.entity
  if (!entity) return
  let biome = ''
  try {
    biome = String(entity.block.biomeId || '')
  } catch (e) {
    try { biome = String(event.level.getBiome(entity.block.pos)) } catch (e2) { return }
  }
  if (biome.indexOf('march_ember_wastes') < 0) return
  try {
    if (entity.baby) return
  } catch (e) {}
  try {
    let raw = entity.minecraftEntity || entity
    try { if (raw.isTame && raw.isTame()) return } catch (e) {}
    try { if (raw.isBaby && raw.isBaby()) return } catch (e) {}
    if (ChocoColor) {
      let existing = raw.color()
      if (existing && existing != ChocoColor.YELLOW && existing != ChocoColor.FLAME) return
      raw.setColor(ChocoColor.FLAME)
      return
    }
  } catch (e) {}
  // Flame id is 7 (Purple is 6). byId(8) would paint Yellow.
  entity.mergeNbt({ Plumage: 7 })
})
