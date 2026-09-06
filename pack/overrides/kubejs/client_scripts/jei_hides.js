// Hide JEI clutter that is not player-facing craft content.
JEIEvents.hideItems(event => {
  // Occultism ritual dummy icons flood JEI; rites still work in-world.
  event.hide(/occultism:ritual_dummy\/.*/)
  event.hide(/occultism:jei_dummy\/.*/)
})
