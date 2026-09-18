// March grit on a Recover pad — cobble hammers like cobble.
// Dirt-sieve clones live in voidloom_sieve.js so they copy tables after mesh-tag rewrite.
ServerEvents.recipes(event => {
  if (!Platform.isLoaded('tribalpower')) return
  if (!Platform.isLoaded('exdeorum')) return

  event.custom({
    type: 'exdeorum:hammer',
    ingredient: { item: 'tribalpower:march_cobble' },
    result: { count: 1, id: 'minecraft:gravel' },
    result_amount: 1.0
  }).id('ninjacatskies:march/hammer_cobble_gravel')

  event.custom({
    type: 'exdeorum:hammer',
    ingredient: { item: 'tribalpower:march_stone' },
    result: { count: 1, id: 'exdeorum:stone_pebble' },
    result_amount: { type: 'minecraft:uniform', min: 1.0, max: 6.0 }
  }).id('ninjacatskies:march/hammer_stone_pebble')
})
