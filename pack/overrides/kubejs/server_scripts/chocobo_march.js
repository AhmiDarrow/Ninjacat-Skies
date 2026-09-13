// Wild pad-runners live in the March. Ember Wastes should hatch Flame, not yellow.
// Color is synched data; NBT merge alone can leave yellow HP/speed on a flame skin.
// Hoist Java.loadClass and use let in try: Rhino rethrows "redeclaration of var" on the second spawn.

let ChocoColor
let ChocoGrade
let McAttributes
try {
  ChocoColor = Java.loadClass('net.chococraft.common.entity.properties.ChocoboColor')
  ChocoGrade = Java.loadClass('net.chococraft.common.entity.properties.ChocoboGrade')
  McAttributes = Java.loadClass('net.minecraft.world.entity.ai.attributes.Attributes')
} catch (e) {}

EntityEvents.spawned('chococraft:chocobo', event => {
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
    try { if (raw.isPersistenceRequired && raw.isPersistenceRequired()) return } catch (e) {}
    if (ChocoColor && ChocoGrade && McAttributes) {
      let existing = raw.getChocoboColor()
      if (existing && existing != ChocoColor.YELLOW) return
      raw.setChocoboColor(ChocoColor.FLAME)
      raw.setGrade(ChocoGrade.GREAT)
      let info = raw.getChocoboColor().getAbilityInfo()
      raw.getAttribute(McAttributes.MAX_HEALTH).setBaseValue(info.getMaxHP())
      raw.setHealth(raw.getMaxHealth())
      raw.getAttribute(McAttributes.MOVEMENT_SPEED).setBaseValue(info.getLandSpeed() / 100)
      raw.getAttribute(McAttributes.FLYING_SPEED).setBaseValue(info.getAirbornSpeed() / 100)
      if (raw.setAllowedFlight) raw.setAllowedFlight(true)
      if (raw.reassessTameGoals) raw.reassessTameGoals()
      return
    }
  } catch (e) {}
  entity.mergeNbt({ Color: 9, Grade: 3 })
})
