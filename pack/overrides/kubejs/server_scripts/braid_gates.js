// Loom Braid glue — Braid Cord is spun at the Tension Post (Strand Filament + two of Clock/Swarm/Spark seated).
// This file only keeps the Reweave soft gate: the molecular assembler wants a braid at its centre.
// Tribal Power ships its own Hum recipes in the jar — do not duplicate here.
ServerEvents.recipes(event => {
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
