// Loom's End keeps its own: the townsfolk, cats, sheep, bees, the spirit herd and Sunfeather, the Hall's golden
// chocobo. They belong to the town (tag ncs_hub_resident, set by Clowder Hall's town plan): nobody tames, rides,
// leads, shears or trades them, and anything that wanders over the rim is brought back.
// Use let inside try/for: Rhino throws "redeclaration of var" if const runs twice.

const LIFE_HUB_DIM = 'clowderhall:clowder_hall'
const SUNFEATHER_HOME = [8, 64, 16]
const SUNFEATHER_RANGE = 44
const RESIDENT_RESCUE = [0, 64, 12]

let LifeComponent
let LifeBlockPos
try {
  LifeComponent = Java.loadClass('net.minecraft.network.chat.Component')
  LifeBlockPos = Java.loadClass('net.minecraft.core.BlockPos')
} catch (e) {}

function lifeTell(player, key) {
  try {
    if (LifeComponent) player.displayClientMessage(LifeComponent.translatable(key), true)
  } catch (e) {}
}

function lifeTags(entity) {
  try {
    return entity.getTags()
  } catch (e) {
    return null
  }
}

function lifeHas(entity, tag) {
  let tags = lifeTags(entity)
  try {
    return !!tags && tags.contains(tag)
  } catch (e) {
    return false
  }
}

function inLifeHub(level) {
  try {
    return String(level.dimension) === LIFE_HUB_DIM
  } catch (e) {
    return false
  }
}

ItemEvents.entityInteracted(event => {
  let target = event.target
  if (!lifeHas(target, 'ncs_hub_resident')) return
  let player = event.player
  try {
    if (player.isCreative()) return
  } catch (e) {}
  if (String(event.hand) === 'MAIN_HAND') {
    if (lifeHas(target, 'ncs_hub_sunfeather')) lifeTell(player, 'message.ninjacatpack.hub.sunfeather')
    else if (lifeHas(target, 'ncs_hub_herd')) lifeTell(player, 'message.ninjacatpack.hub.herd')
    else lifeTell(player, 'message.ninjacatpack.hub.resident')
  }
  event.cancel()
})

// Hall beds belong to its folk: sleeping in one would move a player's spawn off their pad.
BlockEvents.rightClicked(event => {
  if (!inLifeHub(event.level)) return
  try {
    if (event.player.isCreative()) return
  } catch (e) {}
  try {
    if (!event.block.hasTag('minecraft:beds')) return
  } catch (e) {
    return
  }
  lifeTell(event.player, 'message.ninjacatpack.hub.bed')
  event.cancel()
})

function keepSunfeather(bird) {
  try {
    if (LifeBlockPos && bird.restrictTo) {
      bird.restrictTo(new LifeBlockPos(SUNFEATHER_HOME[0], SUNFEATHER_HOME[1], SUNFEATHER_HOME[2]), SUNFEATHER_RANGE)
    }
  } catch (e) {}
  let dx = bird.x - SUNFEATHER_HOME[0]
  let dz = bird.z - SUNFEATHER_HOME[2]
  // Gold birds climb and flap: over the rim, or out past the town, she comes home.
  if (bird.y < 58 || dx * dx + dz * dz > (SUNFEATHER_RANGE + 18) * (SUNFEATHER_RANGE + 18)) {
    try { bird.teleportTo(SUNFEATHER_HOME[0] + 0.5, SUNFEATHER_HOME[1], SUNFEATHER_HOME[2] + 0.5) } catch (e) {}
    try { bird.resetFallDistance() } catch (e) {}
  }
}

function rescueFallen(entity) {
  if (entity.y >= 50) return
  try { entity.teleportTo(RESIDENT_RESCUE[0] + 0.5, RESIDENT_RESCUE[1], RESIDENT_RESCUE[2] + 0.5) } catch (e) {}
  try { entity.resetFallDistance() } catch (e) {}
  try { entity.setDeltaMovement(0, 0, 0) } catch (e) {}
}

// Once a second while someone is in the Hall (the town's chunks only tick then anyway). The sweep follows the
// Hall's clock, not each player's, so five visitors still mean one sweep a second, not five.
let lifeLastSweep = -1

PlayerEvents.tick(event => {
  let hub = event.player.level
  let now
  try {
    now = Number(hub.getGameTime())
  } catch (e) {
    return
  }
  if (now % 20 !== 0 || now === lifeLastSweep) return
  if (!inLifeHub(hub)) return
  lifeLastSweep = now
  let found
  try {
    found = hub.getEntities()
  } catch (e) {
    return
  }
  if (!found) return
  for (let entity of found) {
    if (!lifeHas(entity, 'ncs_hub_resident')) continue
    if (lifeHas(entity, 'ncs_hub_sunfeather')) keepSunfeather(entity)
    rescueFallen(entity)
  }
})
