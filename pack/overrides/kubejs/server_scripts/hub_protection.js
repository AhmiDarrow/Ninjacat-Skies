// Clowder Hall is a shared town. Skyblock Builder's spawn protection only covers the Dock in
// the overworld, so the Hall gets the same treatment here: nothing breaks, nothing gets placed.
// Creative players (builders, ops fixing the town) are let through.

const HALL_DIM = 'clowderhall:clowder_hall'

function inHall(level) {
  try {
    return String(level.dimension) === HALL_DIM
  } catch (e) {
    return false
  }
}

function mayEditHall(player) {
  try {
    return !!player && player.isCreative()
  } catch (e) {
    return false
  }
}

BlockEvents.broken(event => {
  if (!inHall(event.level)) return
  if (mayEditHall(event.player)) return
  // A Yarn Basket holds someone's death drops; it guards itself (owner and Clowder only).
  if (String(event.block.id) === 'ninjacatskies:yarn_basket') return
  event.cancel()
})

BlockEvents.placed(event => {
  if (!inHall(event.level)) return
  if (mayEditHall(event.player)) return
  event.cancel()
})

// Items that change a block without breaking or placing it: buckets, fire, stripping,
// tilling, pathing, bone meal. Everything else still right-clicks, so stalls, lecterns,
// the Hub Key and the Charter keep working.
function reshapesBlocks(item) {
  try {
    if (!item || item.isEmpty()) return false
    let id = String(item.id)
    if (id.indexOf('bucket') >= 0) return true
    if (id === 'minecraft:flint_and_steel' || id === 'minecraft:fire_charge' || id === 'minecraft:bone_meal') return true
    return item.hasTag('minecraft:axes') || item.hasTag('minecraft:shovels') || item.hasTag('minecraft:hoes')
  } catch (e) {
    return false
  }
}

// Nothing in Loom's End is taken or worn down: a right-click only works on what is meant for visitors. The drop
// chest on the ceremony pad (the newcomer's kit) and Yarn Baskets (someone's death drops) open; doors, gates and
// hatches swing; the Songkeeper Drums play; the bell rings; tables that only craft in your own hands work. Every
// barrel, crate, pot, hive, crop, cauldron, lectern, jukebox, anvil and furnace stays as the town left it.
const HALL_DROP_CHEST = [1, 64, 1]
const HALL_OPEN = ['ninjacatskies:yarn_basket', 'minecraft:bell', 'tribalpower:songkeeper_drum', 'minecraft:crafting_table',
  'minecraft:cartography_table', 'minecraft:stonecutter', 'minecraft:smithing_table', 'minecraft:loom',
  'minecraft:enchanting_table']

function hallUsable(block) {
  try {
    let id = String(block.id)
    if (HALL_OPEN.indexOf(id) >= 0) return true
    if (id.indexOf('_door') >= 0 || id.indexOf('_trapdoor') >= 0 || id.indexOf('fence_gate') >= 0) return true
    return block.x === HALL_DROP_CHEST[0] && block.y === HALL_DROP_CHEST[1] && block.z === HALL_DROP_CHEST[2]
  } catch (e) {
    return false
  }
}

function hallDeniesUse(player, block, item) {
  if (reshapesBlocks(item) || !hallUsable(block)) return true
  // Sneaking with something in hand skips the block and uses the item on it instead: an item frame, armor stand or
  // spawn egg against a door or table, honeycomb on a door, a wrench taking a gate apart.
  try {
    return player.isShiftKeyDown() && !!item && !item.isEmpty()
  } catch (e) {
    return true
  }
}

BlockEvents.rightClicked(event => {
  if (!inHall(event.level)) return
  if (mayEditHall(event.player)) return
  if (hallDeniesUse(event.player, event.block, event.item)) event.cancel()
})

// KubeJS does not post BlockEvents.rightClicked while the held item is on cooldown (an ender pearl just thrown, a
// shield just disabled), which would open every pot, lectern and composter in town for that second. Catch those
// clicks from NeoForge's own event.
let HallRightClickBlock = null
let HallProjectileImpact = null
try {
  HallRightClickBlock = Java.loadClass('net.neoforged.neoforge.event.entity.player.PlayerInteractEvent$RightClickBlock')
  HallProjectileImpact = Java.loadClass('net.neoforged.neoforge.event.entity.ProjectileImpactEvent')
} catch (e) {}

if (HallRightClickBlock) {
  NativeEvents.onEvent(HallRightClickBlock, event => {
    try {
      let level = event.getLevel()
      if (level.isClientSide() || !inHall(level)) return
      let player = event.getEntity()
      if (mayEditHall(player)) return
      let item = event.getItemStack()
      if (!player.getCooldowns().isOnCooldown(item.getItem())) return
      if (hallDeniesUse(player, level.getBlock(event.getPos()), item)) event.setCanceled(true)
    } catch (e) {}
  })
}

// Buckets act from Item#use, not on the clicked block: the client sends a plain "use item" once the block click
// passes, so a bucket still scooped the fountains or poured water and lava. Milk is still drunk.
ItemEvents.rightClicked(event => {
  if (!inHall(event.level)) return
  if (mayEditHall(event.player)) return
  let id = ''
  try {
    id = String(event.item.id)
  } catch (e) {}
  if (id.indexOf('bucket') >= 0 && id !== 'minecraft:milk_bucket') event.cancel()
})

// Arrows, tridents, snowballs and eggs break decorated pots (dropping them) and pointed dripstone, and burning ones
// light campfires, candles and TNT; none of that is a break or place event.
const HALL_SHOT_PROOF = ['minecraft:decorated_pot', 'minecraft:pointed_dripstone', 'minecraft:campfire',
  'minecraft:soul_campfire', 'minecraft:tnt', 'minecraft:chorus_flower']

if (HallProjectileImpact) {
  NativeEvents.onEvent(HallProjectileImpact, event => {
    try {
      let hit = event.getRayTraceResult()
      if (!hit || String(hit.getType()) !== 'BLOCK') return
      let level = event.getProjectile().level()
      if (level.isClientSide() || !inHall(level)) return
      let id = String(level.getBlock(hit.getBlockPos()).id)
      if (HALL_SHOT_PROOF.indexOf(id) >= 0 || id.indexOf('candle') >= 0) event.setCanceled(true)
    } catch (e) {}
  })
}

BlockEvents.farmlandTrampled(event => {
  if (inHall(event.level)) event.cancel()
})

LevelEvents.beforeExplosion(event => {
  if (inHall(event.level)) event.cancel()
})
