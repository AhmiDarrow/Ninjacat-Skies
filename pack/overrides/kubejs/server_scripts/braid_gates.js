// Loom Braid glue — mid/late bridge from Clock/Swarm/Spark toward Sigil/Spindle.
// Tribal Power ships its own Hum recipes in the jar — do not duplicate here (JEI doubles + bypass).
// Pack teaches timing only; do not shrink Tribal's solo systems here.
ServerEvents.recipes(event => {
  // Any 2 of {clock, swarm, spark} strand tokens → braid_cord (3 pair variants)
  const braidPairs = [
    ['clock', 'swarm'],
    ['clock', 'spark'],
    ['swarm', 'spark'],
  ]
  braidPairs.forEach(([a, b]) => {
    event.shapeless('ninjacatskies:braid_cord', [
      `ninjacatskies:strand_token_${a}`,
      `ninjacatskies:strand_token_${b}`,
    ]).id(`ninjacatskies:braid_cord_${a}_${b}`)
  })

  // Soft Spindle-adjacent gate: molecular assembler center needs a Loom braid
  event.remove({ id: 'ae2:network/crafting/molecular_assembler' })
  event.shaped('ae2:molecular_assembler', [
    'IQI',
    'ABF',
    'IQI'
  ], {
    I: '#c:ingots/iron',
    Q: 'ae2:quartz_glass',
    A: 'ae2:annihilation_core',
    B: 'ninjacatskies:braid_cord',
    F: 'ae2:formation_core',
  }).id('ninjacatskies:molecular_assembler_braided')
})
