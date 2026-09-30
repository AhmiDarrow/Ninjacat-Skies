// Kin stalls in Clowder Hall (/clowder hub). Frayed Thread shop, not a quest chapter.
// Spawn protection on the Dock still blocks eggs; the Hall is a void pad we raise in Java.
// Use let inside try/for: Rhino throws "redeclaration of var" if const runs twice.

const HUB_STALLS_FLAG = 'ncs_hub_stalls_v3'
const HUB_ESTER_FLAG = 'ncs_hub_ester_v1'
const HUB_DIM = 'clowderhall:clowder_hall'
const MARCH_DIM = 'tribalpower:the_march'

// The Whiskerwind guide is a Kin with no stock: a right-click is a ride to the race town.
const GUIDE_STALL_ID = 'whiskerwind'

// Keeper posts inside Loom's End: x, y, z of the cell their feet stand in (the floor is y - 1), the way they face,
// their tribe, their name.
// HUB_POSTS:BEGIN — written by tools/generate_hub_towns.py from the town plan; tools/gates/test_hub_town.py checks it
const HUB_POSTS = {
  padkeepers: [-39, 64, -13, 0, 0, 'Pad-keepers'],
  rootbinders: [-57, 64, -13, 0, 2, 'Rootbinders'],
  grit: [39, 64, -13, 0, 1, 'Grit-singers'],
  patternweavers: [57, 64, -13, 0, 5, 'Pattern-weavers'],
  colony: [-39, 64, 13, 180, 6, 'Colony-keepers'],
  loomstitchers: [-57, 64, 13, 180, 8, 'Loom-stitchers'],
  spark: [39, 64, 13, 180, 4, 'Drumhearts'],
  edgewalkers: [57, 64, 13, 180, 3, 'Edge-walkers'],
  sealcarvers: [-13, 64, 39, -90, 7, 'Seal-carvers'],
  whiskerwind: [8, 64, 69, 90, 6, 'Whiskerwind Guide'],
  esther: [-12, 64, 73, -90, 6, 'Esther'],
  hearth: [-57, 64, -34, -90, 7, 'Hearth-keeper'],
}
// HUB_POSTS:END

let HubModDimensions
let DeepCacheManager
let HubBlockPos
let HubChunkPos
try {
  HubBlockPos = Java.loadClass('net.minecraft.core.BlockPos')
  HubChunkPos = Java.loadClass('net.minecraft.world.level.ChunkPos')
} catch (e) {}
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

// Each keeper lives in a different chunk and their entities stream in at different moments.
// One "not found" is not proof: only respawn after several misses in a row while the post's
// chunk has its entities loaded (the posts reach 70+ blocks from the pad, past a low view
// distance, so "a player at the pad" proves nothing there).
const HUB_MISS_LIMIT = 3
let hubMisses = {}

function postEntitiesLoaded(hub, found, post) {
  try {
    let raw = hub.minecraftLevel ? hub.minecraftLevel : hub
    if (HubChunkPos && raw.areEntitiesLoaded) return !!raw.areEntitiesLoaded(HubChunkPos.asLong(post[0] >> 4, post[2] >> 4))
  } catch (e) {}
  return playerAtPad(found)
}

function playerAtPad(found) {
  for (let entity of found) {
    try {
      if (String(entity.type) !== 'minecraft:player') continue
      if (Math.abs(entity.x) <= 24 && Math.abs(entity.z) <= 24) return true
    } catch (e) {}
  }
  return false
}

function confirmedMissing(hub, found, key, post) {
  if (!postEntitiesLoaded(hub, found, post)) return false
  hubMisses[key] = (hubMisses[key] || 0) + 1
  if (hubMisses[key] < HUB_MISS_LIMIT) return false
  hubMisses[key] = 0
  return true
}

// A keeper found away from its post (an older town put the stalls round the pad) walks over: moved, re-anchored
// so it keeps to its counter, and turned to face the street.
function settle(entity, post) {
  let x = post[0], y = post[1], z = post[2], yaw = post[3]
  let dx = entity.x - (x + 0.5)
  let dz = entity.z - (z + 0.5)
  if (dx * dx + dz * dz <= 2.25 && Math.abs(entity.y - y) < 1.5) return
  try { entity.teleportTo(x + 0.5, y, z + 0.5) } catch (e) {
    try { entity.setPosition(x + 0.5, y, z + 0.5) } catch (e2) {}
  }
  try { if (HubBlockPos && entity.setAnchor) entity.setAnchor(new HubBlockPos(x, y, z)) } catch (e) {}
  try { entity.setRotation(yaw, 0) } catch (e) {}
  try { entity.setYHeadRot(yaw); entity.setYBodyRot(yaw) } catch (e) {}
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

function hubHasStall(hub, found, stallId, name, x, z) {
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
    for (let entity of matches) {
      if (entity.isAlive && !entity.isAlive()) continue
      // The Hall is locked down: a keeper cannot be struck (and their kin do not turn on the town over it).
      try { entity.setInvulnerable(true) } catch (e) {}
      settle(entity, HUB_POSTS[stallId])
    }
    return true
  }
  return confirmedMissing(hub, found, stallId, HUB_POSTS[stallId]) ? false : null
}

function spawnStall(level, found, x, y, z, yaw, tribeOrdinal, stallId, name) {
  let present = hubHasStall(level, found, stallId, name, x, z)
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
    Invulnerable: true,
    NoAI: false,
    CustomName: `{"text":"${name}"}`,
    CustomNameVisible: true,
  })
  entity.setPosition(x + 0.5, y, z + 0.5)
  // KubeJS 2101 has no setYaw; setRotation(yaw, pitch) is EntityKJS. Head and body follow for mobs.
  try { entity.setRotation(yaw, 0) } catch (e) {}
  try { entity.setYHeadRot(yaw); entity.setYBodyRot(yaw) } catch (e) {}
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
  // Each keeper stands behind the counter of their own shop in Loom's End; the Whiskerwind Guide keeps the
  // gate booth at the south road. Esther is placed by ensureHubEster once the March is open.
  // One listing serves every post (this runs every 4 s for each player in the Hall).
  let found = listHubEntities(hub)
  let all = true
  for (let id in HUB_POSTS) {
    if (id === 'esther') continue
    let p = HUB_POSTS[id]
    if (!spawnStall(hub, found, p[0], p[1], p[2], p[3], p[4], id, p[5])) all = false
  }
  if (all) hub.persistentData.putBoolean(HUB_STALLS_FLAG, true)
}

function isKeeper(entity, stallId) {
  try {
    if (String(entity.type || '').indexOf('tribal_kin') < 0) return false
    return entityLabel(entity) === stallId
  } catch (e) {
    return false
  }
}

function isWhiskerwindGuide(entity) {
  return isKeeper(entity, GUIDE_STALL_ID)
}

// The Hearth-keeper keeps the Purring Hearth's kitchen, not a tribe's stall. It only wears a tribe's look (see
// HUB_POSTS), and Tribal Power would greet in that tribe's name ("The Seal-carvers keep a stall"), so the inn's own
// counter is opened here: its own greeting and title, the same stock and daily restock (stallOffers is Tribal Power's).
const HEARTH_STALL_ID = 'hearth'

function openHearth(player, keeper) {
  let raw = player.minecraftPlayer ? player.minecraftPlayer : player
  try {
    // Another customer still at the counter keeps it (as a tribe's stall does).
    let other = keeper.getTradingPlayer()
    if (other && String(other.getStringUUID()) !== String(raw.getStringUUID()) && other.isAlive()
        && other.containerMenu && other.containerMenu.getOffers && keeper.distanceToSqr(other) <= 64) return
    raw.sendSystemMessage(Text.translate('message.ninjacatpack.hub.hearth_line1'))
    raw.sendSystemMessage(Text.translate('message.ninjacatpack.hub.hearth_line2'))
    if (keeper.stallOffers().isEmpty()) {
      raw.displayClientMessage(Text.translate('message.tribalpower.kin.stall.empty'), true)
      return
    }
    keeper.setTradingPlayer(raw)
    keeper.openTradingScreen(raw, Text.translate('container.ninjacatpack.hub.hearth'), 0)
  } catch (e) {
    console.warn('[Ninjacat Skies] Purring Hearth counter failed to open: ' + e)
  }
}

// On foot or in the saddle: a ridden pad-runner comes along, and the Square remembers
// the Hall as the way home.
function sendToWhiskerwind(player) {
  if (!RaceManager) {
    player.tell(Text.translate('message.ninjacatpack.hub.whiskerwind_closed'))
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
  if (isWhiskerwindGuide(event.target)) {
    // Cancel both hands so the empty stall screen never opens; travel once.
    if (String(event.hand) === 'MAIN_HAND') sendToWhiskerwind(event.player)
    event.cancel()
  } else if (isKeeper(event.target, HEARTH_STALL_ID)) {
    // Both hands again, so Tribal Power never greets for the tribe; the counter opens once.
    if (String(event.hand) === 'MAIN_HAND') openHearth(event.player, event.target)
    event.cancel()
  }
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
  for (let entity of found) {
    if (String(entity.type || '').indexOf('kin_steward') >= 0) stewards.push(entity)
  }
  let post = HUB_POSTS.esther
  if (stewards.length > 1) keepNearest(stewards, post[0] + 0.5, post[2] + 0.5)
  for (let steward of stewards) {
    if (steward.isAlive && !steward.isAlive()) continue
    try { steward.setInvulnerable(true) } catch (e) {}
    settle(steward, post)
  }
  if (stewards.length > 0) {
    hubMisses.ester = 0
    return true
  }
  return confirmedMissing(hub, found, 'ester', post) ? false : null
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
    Invulnerable: true,
    NoAI: true,
    Role: 0,
    CustomName: '{"translate":"chocobosreborn.kin.steward"}',
    CustomNameVisible: true,
  })
  // Behind the counter of Esther's Roost on the Whiskerwind road, looking out at it.
  let post = HUB_POSTS.esther
  entity.setPosition(post[0] + 0.5, post[1], post[2] + 0.5)
  // KubeJS 2101 has no setYaw; setRotation(yaw, pitch) is EntityKJS. Head and body follow for mobs.
  try { entity.setRotation(post[3], 0) } catch (e) {}
  try { entity.setYHeadRot(post[3]); entity.setYBodyRot(post[3]) } catch (e) {}
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

// Each check lists every entity in the Hall, so it runs once per 80 server ticks however many players are in the
// Hall or the March (each player's own tickCount would otherwise start one scan per player per window).
const HUB_CHECK_TICKS = 80
let hubStallsLast = -HUB_CHECK_TICKS
let hubEsterLast = -HUB_CHECK_TICKS

function hubCheckDue(server, last) {
  let now = Number(server.getTickCount())
  return now - last >= HUB_CHECK_TICKS || now < last ? now : -1
}

PlayerEvents.tick(event => {
  if (event.player.tickCount % HUB_CHECK_TICKS !== 0) return
  let dim = String(event.player.level.dimension)
  if (dim === MARCH_DIM) markMarchVisit(event.player)
  if (dim !== MARCH_DIM && dim !== HUB_DIM) return
  let due
  if (dim === HUB_DIM && (due = hubCheckDue(event.server, hubStallsLast)) >= 0) {
    hubStallsLast = due
    ensureHubStalls(event.server)
  }
  if ((due = hubCheckDue(event.server, hubEsterLast)) >= 0) {
    hubEsterLast = due
    ensureHubEster(event.server)
  }
})

LevelEvents.loaded(event => {
  if (String(event.level.dimension) === HUB_DIM) {
    ensureHubStalls(event.server)
    ensureHubEster(event.server)
  }
})
