// March grit on a Recover pad — soil sieves like dirt, cobble hammers like cobble.
// Ex Deorum tables name minecraft:dirt / cobblestone / stone; March blocks are not those items.
ServerEvents.recipes(event => {
  if (!Platform.isLoaded('tribalpower')) return
  if (!Platform.isLoaded('exdeorum')) return

  let cloned = 0
  event.forEachRecipe({ type: 'exdeorum:sieve' }, r => {
    try {
      let ing = r.json.get('ingredient')
      if (!ing || !ing.isJsonObject() || !ing.getAsJsonObject().has('item')) return
      if (String(ing.getAsJsonObject().get('item').getAsString()) !== 'minecraft:dirt') return
      let copy = JSON.parse(r.json.toString())
      copy.ingredient = { item: 'tribalpower:march_soil' }
      let rid = String(r.getId()).split(':').join('_').split('/').join('_')
      event.custom(copy).id('ninjacatskies:march/sieve_' + rid)
      cloned++
    } catch (err) {
      console.warn('[Ninjacat Skies] march soil sieve skipped for ' + r.getId() + ': ' + err)
    }
  })
  console.info('[Ninjacat Skies] March soil shares ' + cloned + ' dirt sieve tables')

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
