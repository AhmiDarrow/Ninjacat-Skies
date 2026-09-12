// Dock Kin stalls — Frayed Thread shop, not a quest chapter.
// Spawn three Elders (Stall=1) at world spawn if the dock has none. Spawn protection
// still blocks eggs; baked-or-scripted entities are the only way to trade here.
const DOCK_STALLS_FLAG = 'ncs_dock_stalls_v1'

function spawnStall(level, x, y, z, tribeOrdinal, stallId) {
  const entity = level.createEntity('tribalpower:tribal_kin')
  if (!entity) return
  entity.mergeNbt({
    Tribe: tribeOrdinal,
    Role: 'ELDER',
    Stall: true,
    StallId: stallId,
    PersistenceRequired: true,
    NoAI: false,
  })
  entity.setPosition(x + 0.5, y, z + 0.5)
  entity.spawn()
}

PlayerEvents.loggedIn(event => {
  const server = event.server
  const overworld = server.getLevel('minecraft:overworld')
  if (!overworld) return
  if (overworld.persistentData.getBoolean(DOCK_STALLS_FLAG)) return
  overworld.persistentData.putBoolean(DOCK_STALLS_FLAG, true)
  // Clowder Dock sits at world center (template offset -7). Stalls stand on the planks.
  spawnStall(overworld, -4, 2, 1, 0, 'padkeepers') // Soil
  spawnStall(overworld, 0, 2, -3, 1, 'grit')        // Stone
  spawnStall(overworld, 4, 2, 1, 4, 'spark')        // Spark
})
