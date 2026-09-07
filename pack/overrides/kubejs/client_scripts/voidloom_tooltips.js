// Client tooltips for Loom stations and proof items. Short; the Codex book carries the rest.
ItemEvents.modifyTooltips(event => {
  event.add('voidloom:loomframe', [
    Text.gray('Stretch a mesh, load dirt or gravel, let it work. Hoppers feed the top and pull the sides.'),
    Text.darkGray('Empty hand takes scraps; sneak to pull the mesh. Thread meshes catch Loom Lint, Thread, and Filament.')
  ])
  event.add('voidloom:tension_barrel', [
    Text.gray('Pour water (bucket comes back) and add dirt → clay. String + ender pearl → 2 yarn.'),
    Text.darkGray('Holds 8 of each. Empty hand takes what settled; sneak to pull dry inputs.')
  ])
  event.add('voidloom:loom_lint', Text.gray('Combed out of dirt by a thread mesh. Four make a Void Yarn.'))
  event.add('voidloom:strand_filament', [
    Text.gray('Rare iron-mesh catch. Right-click a Tension Post with it to spin a Braid Cord.'),
    Text.darkGray('Needs two of Clock, Swarm, or Spark seated.')
  ])
  event.add('ninjacatskies:frayed_thread', Text.gray('Unravel: 1 Thread → 3 string. The Desk chapter sells things for Thread.'))
  event.add('voidloom:void_yarn', [
    Text.gray('Early: 4 string → 2 yarn. Later: string + pearl in the Tension Barrel → 2 yarn.'),
    Text.darkGray('Or four Loom Lint from the Loomframe.')
  ])
  event.add('voidloom:binding_knot', [
    Text.gray('Void Yarn ring around a slime ball. The Loom\'s soft gate.'),
    Text.darkGray('Early slime: 2 dirt + wheat seeds + bone meal.')
  ])
  event.add('ninjacatskies:tension_post', [
    Text.gray('Seat Strand tokens here. Each one lights a notch, chimes for the Clowder, and changes the pad.'),
    Text.darkGray('Braid Cord and the Spindle Loom Fragment are spun here, not crafted.')
  ])
  event.add('ninjacatskies:braid_cord', Text.gray('Two braid paths, one cord. Heart of the molecular assembler.'))
  event.add('ninjacatskies:spindle_loom_fragment', Text.gold('Seat it at the Tension Post to Reweave.'))
  if (Item.exists('mysticalagriculture:inferium_ore')) {
    event.add('mysticalagriculture:inferium_essence', Text.gray('Smelt Inferium Ore — sieve dirt for it. Hostile mobs drop essence too.'))
    event.add('mysticalagriculture:prosperity_shard', Text.gray('Smelt Prosperity Ore — sieve gravel or sand. Rarer than Inferium; it gates seed bases.'))
    event.add('mysticalagriculture:inferium_ore', Text.gray('From the sieve. Smelt for Inferium Essence — the floor of every crop tier.'))
    event.add('mysticalagriculture:prosperity_ore', Text.gray('From the sieve. Smelt for a Prosperity Shard — every seed base needs one.'))
  }
  event.add(/productivebees:.*_nest$/, Text.gray('A ring of this around a small flower. Place it on the pad and wait for wings.'))
  event.add('productivebees:oak_wood_nest', Text.darkGray('Also spawns plain honey bees — the root of every breeding line.'))
  event.add('minecraft:bee_nest', Text.gray('Planks and flowers. A wild bee will move in; shear it with smoke underneath.'))
  if (Item.exists('tribalpower:pulse_resonator')) {
    event.add('tribalpower:pulse_resonator', Text.gray('Feed coal or charcoal — denser Spirit Pulse for the lattice.'))
    event.add('tribalpower:ley_collector', Text.gray('Draw ambient ley into Pulse near a Drumheart.'))
    event.add('tribalpower:pulse_cell', Text.gray('Carry Pulse between Drumheart, Ley, and Resonator.'))
  }
  if (Item.exists('tribalpower:drumheart')) {
    event.add('tribalpower:drumheart', Text.gray('Strike it and listen before you wire anything.'))
  }
  if (Item.exists('tribalpower:march_stone')) {
    event.add('tribalpower:march_stone', Text.gold('Right-click a Tension Post with it once nine Strands are seated.'))
  }
})
