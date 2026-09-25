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

BlockEvents.rightClicked(event => {
  if (!inHall(event.level)) return
  if (mayEditHall(event.player)) return
  if (reshapesBlocks(event.item)) event.cancel()
})

LevelEvents.beforeExplosion(event => {
  if (inHall(event.level)) event.cancel()
})
