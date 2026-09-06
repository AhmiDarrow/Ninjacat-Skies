// Tribal water totem/seal accept Ex Deorum porcelain water (iron-only in jar).
ServerEvents.recipes(event => {
  if (!Item.exists('tribalpower:resonance_totem_water')) return
  if (!Item.exists('exdeorum:porcelain_water_bucket')) return

  event.shaped('tribalpower:resonance_totem_water', [
    ' B ',
    'WXW',
    ' C '
  ], {
    W: '#minecraft:logs',
    B: 'tribalpower:bone_chime',
    C: 'tribalpower:copper_resonator',
    X: 'exdeorum:porcelain_water_bucket'
  }).id('ninjacatskies:tribal_totem_water_porcelain')

  event.shapeless('tribalpower:water_seal', [
    'tribalpower:blank_seal',
    'exdeorum:porcelain_water_bucket'
  ]).id('ninjacatskies:tribal_water_seal_porcelain')
})
