// Wild pad-runners live in the March. Ember Wastes should hatch Flame, not yellow.
// Color is synched data; NBT merge alone can leave yellow HP/speed on a flame skin.

EntityEvents.spawned('chococraft:chocobo', event => {
  if (!event.server) return
  const entity = event.entity
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
    const Color = Java.loadClass('net.chococraft.common.entity.properties.ChocoboColor')
    const Grade = Java.loadClass('net.chococraft.common.entity.properties.ChocoboGrade')
    const Attributes = Java.loadClass('net.minecraft.world.entity.ai.attributes.Attributes')
    const raw = entity.minecraftEntity || entity
    try { if (raw.isTame && raw.isTame()) return } catch (e) {}
    try { if (raw.isBaby && raw.isBaby()) return } catch (e) {}
    try { if (raw.isPersistenceRequired && raw.isPersistenceRequired()) return } catch (e) {}
    try {
      const existing = raw.getChocoboColor()
      if (existing && existing != Color.YELLOW) return
    } catch (e) {}
    raw.setChocoboColor(Color.FLAME)
    raw.setGrade(Grade.GREAT)
    const info = raw.getChocoboColor().getAbilityInfo()
    raw.getAttribute(Attributes.MAX_HEALTH).setBaseValue(info.getMaxHP())
    raw.setHealth(raw.getMaxHealth())
    raw.getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(info.getLandSpeed() / 100)
    raw.getAttribute(Attributes.FLYING_SPEED).setBaseValue(info.getAirbornSpeed() / 100)
    if (raw.setAllowedFlight) raw.setAllowedFlight(true)
    if (raw.reassessTameGoals) raw.reassessTameGoals()
  } catch (e) {
    entity.mergeNbt({ Color: 9, Grade: 3 })
  }
})
