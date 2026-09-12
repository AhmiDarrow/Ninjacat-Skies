// Kin stalls in Clowder Hall (/clowder hub). Frayed Thread shop, not a quest chapter.
// Spawn protection on the Dock still blocks eggs; the Hall is a void pad we raise in Java.
const HUB_STALLS_FLAG = 'ncs_hub_stalls_v1'
const HUB_DIM = 'clowderhall:clowder_hall'

function spawnStall(level, x, y, z, yaw, tribeOrdinal, stallId, name) {
  const entity = level.createEntity('tribalpower:tribal_kin')
  if (!entity) return
  entity.mergeNbt({
    Tribe: tribeOrdinal,
    Role: 'ELDER',
    Stall: true,
    StallId: stallId,
    PersistenceRequired: true,
    NoAI: false,
    CustomName: `{"text":"${name}"}`,
    CustomNameVisible: true,
  })
  entity.setPosition(x + 0.5, y, z + 0.5)
  if (entity.setYaw) entity.setYaw(yaw)
  entity.spawn()
}

function ensureHubStalls(server) {
  const hub = server.getLevel(HUB_DIM)
  if (!hub) return
  if (hub.persistentData.getBoolean(HUB_STALLS_FLAG)) return
  try {
    const ModDimensions = Java.loadClass('com.ninjacat.skies.clowder.world.ModDimensions')
    const raw = hub.minecraftLevel ? hub.minecraftLevel : hub
    ModDimensions.ensureHubHall(raw)
  } catch (e) {
    // Pad may already exist from a prior visit.
  }
  // Ceremony pad center is 0,63,0. Stand on the terracotta at y=64, flanking the south path
  // the player walks (arrive 0.5,65,5.5 facing the beacon).
  spawnStall(hub, -4, 64, 4, -90, 0, 'padkeepers', 'Pad-keepers') // Soil, look east
  spawnStall(hub, 4, 64, 4, 90, 1, 'grit', 'Grit')               // Stone, look west
  spawnStall(hub, 4, 64, 1, 90, 4, 'spark', 'Spark')             // Spark, look west
  hub.persistentData.putBoolean(HUB_STALLS_FLAG, true)
}

PlayerEvents.loggedIn(event => {
  ensureHubStalls(event.server)
})

LevelEvents.loaded(event => {
  if (String(event.level.dimension) === HUB_DIM) ensureHubStalls(event.server)
})
