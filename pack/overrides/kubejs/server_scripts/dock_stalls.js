// Kin stalls in Clowder Hall (/clowder hub). Frayed Thread shop, not a quest chapter.
// Spawn protection on the Dock still blocks eggs; the Hall is a void pad we raise in Java.
// Use let inside try/for: Rhino throws "redeclaration of var" if const runs twice.

const HUB_STALLS_FLAG = 'ncs_hub_stalls_v2'
const HUB_ESTER_FLAG = 'ncs_hub_ester_v1'
const HUB_DIM = 'clowderhall:clowder_hall'
const MARCH_DIM = 'tribalpower:the_march'

let HubModDimensions
let DeepCacheManager
try {
  HubModDimensions = Java.loadClass('com.ninjacat.skies.clowder.world.ModDimensions')
} catch (e) {}
try {
  DeepCacheManager = Java.loadClass('tk.darrow.tribalpower.storage.DeepCacheManager')
} catch (e) {}

function entityLabel(entity) {
  try {
    if (entity.nbt && entity.nbt.StallId) return String(entity.nbt.StallId)
  } catch (e) {}
  try {
    if (entity.username) return String(entity.username)
  } catch (e) {}
  try {
    if (entity.name) return String(entity.name)
  } catch (e) {}
  return ''
}

function listHubEntities(hub) {
  try {
    if (!hub.getEntities) return null
    let found = hub.getEntities()
    if (!found) return null
    let out = []
    for (let entity of found) out.push(entity)
    return out
  } catch (e) {
    return null
  }
}

function hubHasStall(hub, stallId, name) {
  let found = listHubEntities(hub)
  if (!found || found.length === 0) return null
  for (let entity of found) {
    let t = String(entity.type || '')
    if (t.indexOf('tribal_kin') < 0) continue
    let label = entityLabel(entity)
    if (label === stallId || (name && label.indexOf(name) >= 0)) return true
  }
  return false
}

function spawnStall(level, x, y, z, yaw, tribeOrdinal, stallId, name) {
  let present = hubHasStall(level, stallId, name)
  if (present === true) return true
  if (present === null && level.persistentData.getBoolean(HUB_STALLS_FLAG)) return true
  let entity = level.createEntity('tribalpower:tribal_kin')
  if (!entity) return false
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
  return true
}

function ensureHubStalls(server) {
  let hub = server.getLevel(HUB_DIM)
  if (!hub) return
  try {
    if (HubModDimensions) {
      let raw = hub.minecraftLevel ? hub.minecraftLevel : hub
      HubModDimensions.ensureHubHall(raw)
    }
  } catch (e) {
    // Pad may already exist from a prior visit.
  }
  // Ceremony pad center is 0,63,0. Stand on the terracotta at y=64, flanking the south path
  // the player walks (arrive 0.5,65,5.5 facing the beacon).
  let a = spawnStall(hub, -3, 64, 2, -90, 0, 'padkeepers', 'Pad-keepers')
  let b = spawnStall(hub, 3, 64, 2, 90, 1, 'grit', 'Grit')
  let c = spawnStall(hub, 3, 64, -1, 90, 4, 'spark', 'Spark')
  if (a && b && c) hub.persistentData.putBoolean(HUB_STALLS_FLAG, true)
}

function playerVisitedMarch(player) {
  if (!player) return false
  try {
    if (player.persistentData && player.persistentData.getBoolean('ncs_visited_march')) return true
  } catch (e) {}
  try {
    if (!DeepCacheManager) return false
    let uuid = player.getUuid ? player.getUuid() : player.uuid
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
  let found = listHubEntities(hub)
  if (!found || found.length === 0) return null
  for (let entity of found) {
    let t = String(entity.type || '')
    if (t.indexOf('kin_steward') >= 0 || t.indexOf('race_master') >= 0) return true
  }
  return false
}

function spawnEster(hub) {
  let present = esterAlreadyPresent(hub)
  if (present === true) {
    hub.persistentData.putBoolean(HUB_ESTER_FLAG, true)
    return
  }
  // Listing failed: trust the flag so a later tick does not double-spawn.
  if (present === null && hub.persistentData.getBoolean(HUB_ESTER_FLAG)) return
  let entity = hub.createEntity('chocobosreborn:kin_steward')
  if (!entity) return
  entity.mergeNbt({
    PersistenceRequired: true,
    NoAI: true,
    Role: 0,
    CustomName: '{"translate":"chocobosreborn.kin.steward"}',
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
  let players = server.players || server.getPlayers()
  if (!players) return false
  for (let player of players) {
    if (playerVisitedMarch(player)) return true
  }
  return false
}

function ensureHubEster(server) {
  if (!someoneOpenedMarch(server)) return
  let hub = server.getLevel(HUB_DIM)
  if (!hub) return
  spawnEster(hub)
}

PlayerEvents.loggedIn(event => {
  ensureHubStalls(event.server)
  if (String(event.player.level.dimension) === MARCH_DIM) markMarchVisit(event.player)
  ensureHubEster(event.server)
})

PlayerEvents.tick(event => {
  if (event.player.tickCount % 80 !== 0) return
  let dim = String(event.player.level.dimension)
  if (dim === MARCH_DIM) markMarchVisit(event.player)
  if (dim === HUB_DIM) ensureHubStalls(event.server)
  if (dim === MARCH_DIM || dim === HUB_DIM) ensureHubEster(event.server)
})

LevelEvents.loaded(event => {
  if (String(event.level.dimension) === HUB_DIM) {
    ensureHubStalls(event.server)
    ensureHubEster(event.server)
  }
})
