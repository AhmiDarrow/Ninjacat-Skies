// Client tooltips for early voidloom station blocks and end trophy
ItemEvents.modifyTooltips(event => {
  event.add('voidloom:loomframe', [
    Text.gray('Insert a sieve mesh, then right-click dirt/gravel for a small bonus scrap.'),
    Text.darkGray('Empty hand removes the mesh. Ex Deorum sieves still do the real work.')
  ])
  event.add('ninjacatskies:frayed_thread', [
    Text.gray('Unravel: 1 Thread → 3 string. Desk shop sinks Thread for QoL.')
  ])
  event.add('voidloom:void_yarn', [
    Text.gray('Early: 4 string → 2 yarn (unravel Thread first).'),
    Text.darkGray('Better later: 2 string + pearl/chorus → 2 yarn, or Tension Barrel.')
  ])
  event.add('voidloom:binding_knot', [
    Text.gray('Void Yarn ring + slime ball.'),
    Text.darkGray('Early slime: 2 dirt + wheat seeds + bone meal.')
  ])
  if (Item.exists('tribalpower:pulse_resonator')) {
    event.add('tribalpower:pulse_resonator', Text.gray('Feed coal/charcoal — denser Spirit Pulse for the lattice.'))
    event.add('tribalpower:ley_collector', Text.gray('Draw ambient ley into Pulse near a Drumheart.'))
    event.add('tribalpower:pulse_cell', Text.gray('Carry Pulse between Drumheart, Ley, and Resonator.'))
  }
  event.add('voidloom:tension_barrel', [
    Text.gray('Iron or porcelain water + dirt → clay (~10s).'),
    Text.gray('Empty bucket returns to you. String + pearl → yarn (~8s).'),
    Text.darkGray('No GUI — right-click to insert, empty hand to take.')
  ])
  event.add('ninjacatskies:spindle_loom_fragment', Text.gold('End trophy — nine Strand tokens plus March stone.'))
  event.add('ninjacatskies:braid_cord', [
    Text.gray('Loom braid — any two of Clock, Swarm, or Spark tokens.'),
    Text.gold('Consumes tokens — craft extras before the Spindle trophy.'),
  ])
  event.add(/ninjacatskies:strand_token_.*/, Text.darkGray('Keep a spare — braid crafts consume tokens.'))
  if (Item.exists('tribalpower:drumheart')) {
    event.add('tribalpower:drumheart', Text.gray('Hum lead-in — strike to store Spirit Pulse.'))
  }
})
