// Void-pad reachability — items a quest asks for whose only source is a structure, a raid or a
// structure-only mob. None of those exist on the pad, so each gets one priced crafting recipe here.
// Grids were checked against every crafting recipe the pack loads (vanilla, all mod jars, pack datapacks,
// the other KubeJS scripts): none of them overlaps an existing recipe.
ServerEvents.recipes(event => {
  // Shulker shells: End cities are gone, so no shulkers. Packaged Auto's Distributor and Crafting Proxy
  // each want two. Chorus comes from the Edge-walkers' stall; popped chorus makes purpur. Two shells and
  // a chest cost about what the Edge-walkers ask for a finished box.
  event.shaped('minecraft:shulker_shell', [
    'PPP',
    'EKE',
    'PPP'
  ], {
    P: 'minecraft:purpur_block',
    E: 'minecraft:ender_pearl',
    K: 'voidloom:binding_knot'
  }).id('ninjacatskies:reachability/shulker_shell')

  // Totem of Undying: evokers only come with raids and woodland mansions. Ars Nouveau's Archmage Spell Book
  // needs one. Priced near a Thread Shard: a death saved is worth about a life.
  event.shaped('minecraft:totem_of_undying', [
    'GEG',
    'EAE',
    'GEG'
  ], {
    G: 'minecraft:gold_block',
    E: 'minecraft:emerald',
    A: 'minecraft:golden_apple'
  }).id('ninjacatskies:reachability/totem_of_undying')

  if (Platform.isLoaded('irons_spellbooks')) {
    // Ruined Codex: citadel and ancient-city loot only. The Netherite Spell Book needs one.
    event.shaped('irons_spellbooks:ruined_book', [
      'SES',
      'EBE',
      'SES'
    ], {
      S: 'minecraft:soul_sand',
      E: 'irons_spellbooks:arcane_essence',
      B: 'minecraft:enchanted_book'
    }).id('ninjacatskies:reachability/ruined_book')

    // Magehunter: only ever held by Magehunter Vindicators, which spawn in evoker-fort towers alone.
    // The crafted blade comes without the Sharpness V a Vindicator's copy carries.
    event.shaped('irons_spellbooks:magehunter', [
      '  I',
      'CI ',
      'DC '
    ], {
      I: 'irons_spellbooks:arcane_ingot',
      C: 'minecraft:chain',
      D: 'minecraft:diamond'
    }).id('ninjacatskies:reachability/magehunter')
  }
})
