// Client tooltips for Loom stations and proof items. Short; the Codex book carries the rest.
ItemEvents.modifyTooltips(event => {
  event.add('voidloom:loomframe', [
    Text.gray('Stretch a mesh, hopper grit in the top, sit it on a hopper for scraps. Same table as an Ex Deorum sieve, a little less per block because it runs itself.'),
    Text.darkGray('Empty hand takes scraps; sneak to pull the mesh. Mesh is hand-only. Redstone pauses it.')
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
  event.add('ninjacatskies:whisker_codex', [
    Text.gray('Right-click: the campaign book — story and what to do.'),
    Text.darkGray('Grave (`): the assignment list and rewards. Same campaign, not a second mode.')
  ])
  event.add('ninjacatskies:frayed_thread', Text.gray('Unravel: 1 Thread → 3 string. Dock Kin stalls sell things for Thread.'))
  event.add('minecraft:rotten_flesh', Text.gray('Smelt or campfire it for leather. Zombies on the pad are the cow.'))
  event.add('minecraft:leather', Text.gray('Smelt rotten flesh, or sieve dirt with flint mesh and up. Pad-keepers at the Dock sell a little.'))
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
  event.add(/productivebees:.*_nest$/, Text.gray('A ring of this around a small flower. Place it, then right-click it with a small flower to wake the bee.'))
  event.add('productivebees:oak_wood_nest', Text.darkGray('Also spawns plain honey bees — the root of every breeding line.'))
  event.add('minecraft:bee_nest', Text.gray('Planks and flowers. A wild bee will move in; shear it with smoke underneath.'))
  if (Item.exists('tribalpower:pulse_resonator')) {
    event.add('tribalpower:pulse_resonator', Text.gray('Seat a reusable Echo catalyst. Distinct totem voices strengthen the song; a Voice Ring at radius 3 is what six voices now means. Redstone pauses it.'))
    event.add('tribalpower:ley_collector', Text.gray('Draw ambient ley into Pulse near a Drumheart. Still the voice-less starter passive.'))
    event.add('tribalpower:pulse_cell', Text.gray('Carry Pulse between Drumheart, Ley, generators and the pit.'))
  }
  if (Item.exists('tribalpower:drumheart')) {
    event.add('tribalpower:drumheart', Text.gray('Strike it and listen. 24 Pulse on a 17-to-23-tick rising edge, 10 otherwise; nothing closer than 8 ticks counts.'))
  }
  if (Item.exists('tribalpower:march_stone')) {
    event.add('tribalpower:march_stone', Text.gold('Right-click a Tension Post with it once nine Strands are seated.'))
  }
  // Tribal Power 3.0 — the Nine Tribes. Camps stand in the March; the pack's quests are in Tribal Weave.
  if (Item.exists('tribalpower:tribe_hearth')) {
    event.add('tribalpower:tribe_hearth', Text.gray('Offer what the tribe favours. Standing opens trades, then the Mark. Sixty standing a day per tribe. Do not break it.'))
    event.add('tribalpower:tribe_mark', Text.gray('An Elder gives it once, at Voice. Craft it into a Kinship Totem.'))
    event.add('tribalpower:kinship_totem', Text.gray('One more voice for the Pulse Resonator — up to fifteen with all nine tribes.'))
    event.add('tribalpower:loom_thread', Text.gray('Ancestor Halls, The Unsung, or a Loom-stitcher at Friend. The sixth voice starts here.'))
    event.add('tribalpower:silent_drum', Text.gray('Four strikes, a breath apart. Sneak against the Beat; answer the Silence with the same rhythm.'))
    event.add(/tribalpower:rite_(green|rain|sky|dawn|still|ley|spring).*/, Text.gray('Sneak-use on a Ritual Brazier with the matching seal seated. A tablet wants a Rite Circle. Pulse comes from the lattice around it.'))
    event.add('tribalpower:bonding_charm', Text.gray('Adult Lantern Fox, Mossback or Dawn Stag. Kept when the bond fails.'))
    event.add('tribalpower:camp_charter', Text.gray('Use on a Clowder mate to share one vault, one anchor budget, one standing.'))
    event.add('tribalpower:ley_lens', Text.gray('Hold to see the ley. Sneak-use a Ley Collector for its numbers.'))
  }
  // Tribal Power 3.2 — Listening Pit, gates, six voices. Quests are the rest of Tribal Weave.
  if (Item.exists('tribalpower:stone_font')) {
    event.add('tribalpower:stone_font', Text.gray('Four chalk marks. Cobble at 4 Pulse/s; Earth for stone; Fire and Water, or water plus lava, for obsidian. Sneak-use the Codex on it.'))
    event.add('tribalpower:resonance_mesh', Text.gray('Centre of a Listening Pit. Sample on top is a filter. Mining stays cheaper.'))
    event.add('tribalpower:anchor_stone', Text.gray('Braces a font, a pit and a Far Gate. Four corners.'))
    event.add('tribalpower:gate_frame', Text.gray('A five-by-five Way Gate ring without its corners. Keystone at the bottom centre.'))
    event.add('tribalpower:gate_keystone', Text.gray('Lights the gate. Waystone Compass or chalk within 64 blocks; Gate Sigil for a Far Gate.'))
    event.add('tribalpower:gate_sigil', Text.gray('Names a Far Gate pair. Loom voice nearby. 120 Pulse a traveller.'))
    event.add('tribalpower:ember_horn', Text.gray('Fire. Burns furnace fuel for up to 20 Pulse a second while lit.'))
    event.add('tribalpower:wind_harp', Text.gray('Air. Altitude, open sky, weather. Harps within 12 blocks divide the wind.'))
    event.add('tribalpower:wave_drum', Text.gray('Water. Adjacent water or piped. Passive drums within 8 blocks divide the water.'))
    event.add('tribalpower:wake_bell', Text.gray('Spirit. Nearby deaths, tolled out at no more than 8 Pulse a second.'))
    event.add('tribalpower:loom_anchor', Text.gray('Loom. One Pulse a second per distinct nearby voice, doubled during a Ley Binding.'))
    event.add('tribalpower:pulse_cairn', Text.gray('4,000 Pulse. Stack five. Turns a bursty bell into a steady pit.'))
    event.add('tribalpower:music_disc_drum_circle', Text.gray('From a chest at the Drum Circle, or from The Unsung. Play it in a jukebox.'))
  }
})
