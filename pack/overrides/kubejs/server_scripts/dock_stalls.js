// Kin stalls in Clowder Hall (/clowder hub). Frayed Thread shop, not a quest chapter.
// Spawn protection on the Dock still blocks eggs; the Hall is a void pad we raise in Java.
const HUB_STALLS_FLAG = 'ncs_hub_stalls_v2'
const HUB_ESTER_FLAG = 'ncs_hub_ester_v1'
const HUB_DIM = 'clowderhall:clowder_hall'
const MARCH_DIM = 'tribalpower:the_march'

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
  spawnStall(hub, -3, 64, 2, -90, 0, 'padkeepers', 'Pad-keepers') // Soil, look east; off the south banner posts
  spawnStall(hub, 3, 64, 2, 90, 1, 'grit', 'Grit')               // Stone, look west
  spawnStall(hub, 3, 64, -1, 90, 4, 'spark', 'Spark')            // Spark, look west; clear of banners
  hub.persistentData.putBoolean(HUB_STALLS_FLAG, true)
}

function playerVisitedMarch(player) {
  if (!player) return false
  try {
    if (player.persistentData && player.persistentData.getBoolean('ncs_visited_march')) return true
  } catch (e) {}
  try {
    const DeepCacheManager = Java.loadClass('tk.darrow.tribalpower.storage.DeepCacheManager')
    const uuid = player.getUuid ? player.getUuid() : player.uuid
    return DeepCacheManager.data(player.server).hasVisitedMarch(uuid)
  } catch (e) {
    return false
  }
}

function markMarchVisit(player) {
  if (!player) return
  try { player.persistentData.putBoolean('ncs_visited_march', true) } catch (e) {}
  try { player.server.persistentData.putBoolean('ncs_march_opened', true) } catch (e) {}
}

function esterAlreadyPresent(hub) {
  try {
    const found = hub.getEntities ? hub.getEntities() : null
    if (!found) return false
    for (const entity of found) {
      const t = String(entity.type || '')
      if (t.indexOf('race_master') >= 0) return true
    }
  } catch (e) {}
  return false
}

function spawnEster(hub) {
  if (esterAlreadyPresent(hub)) {
    hub.persistentData.putBoolean(HUB_ESTER_FLAG, true)
    return
  }
  const entity = hub.createEntity('chococraft:race_master')
  if (!entity) return
  entity.mergeNbt({
    PersistenceRequired: true,
    CustomName: '{"translate":"entity.chococraft.race_master"}',
    CustomNameVisible: true,
  })
  // West of the pad, opposite Spark, looking east toward the shop line.
  entity.setPosition(-3.5, 64, -1.5)
  if (entity.setYaw) entity.setYaw(-90)
  entity.spawn()
  hub.persistentData.putBoolean(HUB_ESTER_FLAG, true)
}

function someoneOpenedMarch(server) {
  try {
    if (server.persistentData.getBoolean('ncs_march_opened')) return true
  } catch (e) {}
  const players = server.players || server.getPlayers()
  if (!players) return false
  for (const player of players) {
    if (playerVisitedMarch(player)) return true
  }
  return false
}

function ensureHubEster(server) {
  if (!someoneOpenedMarch(server)) return
  const hub = server.getLevel(HUB_DIM)
  if (!hub) return
  // Trust the world flag so a failed entity scan cannot duplicate Ester every 80 ticks.
  if (hub.persistentData.getBoolean(HUB_ESTER_FLAG)) return
  spawnEster(hub)
}

PlayerEvents.loggedIn(event => {
  ensureHubStalls(event.server)
  if (String(event.player.level.dimension) === MARCH_DIM) markMarchVisit(event.player)
  ensureHubEster(event.server)
})

PlayerEvents.tick(event => {
  if (event.player.tickCount % 80 !== 0) return
  const dim = String(event.player.level.dimension)
  if (dim === MARCH_DIM) markMarchVisit(event.player)
  if (dim === MARCH_DIM || dim === HUB_DIM) ensureHubEster(event.server)
})

LevelEvents.loaded(event => {
  if (String(event.level.dimension) === HUB_DIM) {
    ensureHubStalls(event.server)
    ensureHubEster(event.server)
  }
})
