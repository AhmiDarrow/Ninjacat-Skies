// Kin stalls in Clowder Hall (/clowder hub). Frayed Thread shop, not a quest chapter.
// Spawn protection on the Dock still blocks eggs; the Hall is a void pad we raise in Java.
// Use let inside try/for: Rhino throws "redeclaration of var" if const runs twice.

const HUB_STALLS_FLAG = 'ncs_hub_stalls_v2'
const HUB_ESTER_FLAG = 'ncs_hub_ester_v1'
const HUB_DIM = 'clowderhall:clowder_hall'
const MARCH_DIM = 'tribalpower:the_march'

// The Whiskerwind guide is a Kin with no stock: a right-click is a ride to the race town.
const GUIDE_STALL_ID = 'whiskerwind'

let HubModDimensions
let DeepCacheManager
let RaceManager
try {
  RaceManager = Java.loadClass('tk.darrow.chocobosreborn.race.RaceManager')
} catch (e) {}
try {
  HubModDimensions = Java.loadClass('com.ninjacat.skies.clowder.world.ModDimensions')
} catch (e) {}
try {
  DeepCacheManager = Java.loadClass('tk.darrow.tribalpower.storage.DeepCacheManager')
} catch (e) {}

function entityLabel(entity) {
  try {
    if (entity.stallId) return String(entity.stallId())
  } catch (e) {}
  try {
    if (entity.nbt && entity.nbt.contains('StallId')) return String(entity.nbt.getString('StallId'))
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

// The pad sits on a chunk corner, so each keeper lives in a different chunk and their
// entities stream in at different moments. One "not found" is not proof: only respawn
// after several misses in a row with a player standing at the pad.
const HUB_MISS_LIMIT = 3
let hubMisses = {}

function playerAtPad(found) {
  for (let entity of found) {
    try {
      if (String(entity.type) !== 'minecraft:player') continue
      if (Math.abs(entity.x) <= 24 && Math.abs(entity.z) <= 24) return true
    } catch (e) {}
  }
  return false
}

function confirmedMissing(found, key) {
  if (!playerAtPad(found)) return false
  hubMisses[key] = (hubMisses[key] || 0) + 1
  if (hubMisses[key] < HUB_MISS_LIMIT) return false
  hubMisses[key] = 0
  return true
}

// Keep the one nearest its post, discard the rest (cleans up earlier double-spawns).
function keepNearest(matches, x, z) {
  let best = null
  let bestDist = 0
  for (let entity of matches) {
    let dx = entity.x - x
    let dz = entity.z - z
    let dist = dx * dx + dz * dz
    if (best === null || dist < bestDist) {
      best = entity
      bestDist = dist
    }
  }
  for (let entity of matches) {
    if (entity !== best) entity.discard()
  }
}

function hubHasStall(hub, stallId, name, x, z) {
  let found = listHubEntities(hub)
  if (!found || found.length === 0) return null
  let matches = []
  for (let entity of found) {
    let t = String(entity.type || '')
    if (t.indexOf('tribal_kin') < 0) continue
    let label = entityLabel(entity)
    if (label === stallId || (name && label.indexOf(name) >= 0)) matches.push(entity)
  }
  if (matches.length > 0) {
    hubMisses[stallId] = 0
    if (matches.length > 1) keepNearest(matches, x + 0.5, z + 0.5)
    return true
  }
  return confirmedMissing(found, stallId) ? false : null
}

function spawnStall(level, x, y, z, yaw, tribeOrdinal, stallId, name) {
  let present = hubHasStall(level, stallId, name, x, z)
  if (present === true) return true
  // Unconfirmed: a set flag means they were placed before, so wait for the next check.
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
  // South-west of the arrival point, so it is the first keeper a newcomer sees.
  let d = spawnStall(hub, -3, 64, 5, -90, 6, GUIDE_STALL_ID, 'Whiskerwind Guide')
  if (a && b && c && d) hub.persistentData.putBoolean(HUB_STALLS_FLAG, true)
}

function isWhiskerwindGuide(entity) {
  try {
    if (String(entity.type || '').indexOf('tribal_kin') < 0) return false
    return entityLabel(entity) === GUIDE_STALL_ID
  } catch (e) {
    return false
  }
}

// On foot or in the saddle: a ridden pad-runner comes along, and the Square remembers
// the Hall as the way home.
function sendToWhiskerwind(player) {
  if (!RaceManager) {
    player.tell('The road to Whiskerwind is closed.')
    return
  }
  let raw = player.minecraftPlayer ? player.minecraftPlayer : player
  let bird = null
  try {
    let vehicle = raw.getVehicle()
    if (vehicle && String(vehicle.type) === 'chocobosreborn:chocobo') bird = vehicle
  } catch (e) {}
  if (bird) RaceManager.enterSquare(raw, bird)
  else RaceManager.enterSquareOnFoot(raw)
}

ItemEvents.entityInteracted(event => {
  if (!isWhiskerwindGuide(event.target)) return
  // Cancel both hands so the empty stall screen never opens; travel once.
  if (String(event.hand) === 'MAIN_HAND') sendToWhiskerwind(event.player)
  event.cancel()
})

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
  let stewards = []
  let other = false
  for (let entity of found) {
    let t = String(entity.type || '')
    if (t.indexOf('kin_steward') >= 0) stewards.push(entity)
    else if (t.indexOf('race_master') >= 0) other = true
  }
  if (stewards.length > 1) keepNearest(stewards, -3.5, -1.5)
  if (stewards.length > 0 || other) {
    hubMisses.ester = 0
    return true
  }
  return confirmedMissing(found, 'ester') ? false : null
}

function spawnEster(hub) {
  let present = esterAlreadyPresent(hub)
  if (present === true) {
    hub.persistentData.putBoolean(HUB_ESTER_FLAG, true)
    return
  }
  // Unconfirmed: trust the flag so a later tick does not double-spawn.
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
