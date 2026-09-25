// Client tooltips for Loom stations and proof items. Short; the Codex book carries the rest.
ItemEvents.modifyTooltips(event => {
  event.add('voidloom:loomframe', [
    Text.translate('tooltip.ninjacatpack.loomframe.1').gray(),
    Text.translate('tooltip.ninjacatpack.loomframe.2').darkGray()
  ])
  event.add('voidloom:tension_barrel', [
    Text.translate('tooltip.ninjacatpack.tension_barrel.1').gray(),
    Text.translate('tooltip.ninjacatpack.tension_barrel.2').darkGray()
  ])
  event.add('voidloom:loom_lint', Text.translate('tooltip.ninjacatpack.loom_lint').gray())
  event.add('voidloom:strand_filament', [
    Text.translate('tooltip.ninjacatpack.strand_filament.1').gray(),
    Text.translate('tooltip.ninjacatpack.strand_filament.2').darkGray()
  ])
  event.add('ninjacatskies:frayed_thread', Text.translate('tooltip.ninjacatpack.frayed_thread').gray())
  event.add('ninjacatskies:thread_skein', Text.translate('tooltip.ninjacatpack.thread_skein').gray())
  event.add('ninjacatskies:thread_bolt', Text.translate('tooltip.ninjacatpack.thread_bolt').gray())
  event.add('ninjacatskies:thread_shard', [
    Text.translate('tooltip.ninjacatpack.thread_shard.1').gray(),
    Text.translate('tooltip.ninjacatpack.thread_shard.2').darkGray()
  ])
  event.add('ninjacatskies:thread_of_return', Text.translate('tooltip.ninjacatpack.thread_of_return').darkGray())
  if (Item.exists('silentgear:blueprint_package')) {
    event.add('silentgear:blueprint_package', Text.translate('tooltip.ninjacatpack.blueprint_package').gray())
  }
  if (Item.exists('ae2:sky_stone_tank')) {
    event.add('ae2:sky_stone_tank', Text.translate('tooltip.ninjacatpack.sky_stone_tank').gray())
  }
  event.add('minecraft:rotten_flesh', Text.translate('tooltip.ninjacatpack.rotten_flesh').gray())
  if (Item.exists('pamhc2foodcore:freshmilkitem')) {
    event.add('pamhc2foodcore:freshmilkitem', Text.translate('tooltip.ninjacatpack.freshmilkitem').gray())
    event.add('pamhc2trees:coconutitem', Text.translate('tooltip.ninjacatpack.coconutitem').gray())
    event.add('pamhc2foodextended:silkentofuitem', Text.translate('tooltip.ninjacatpack.silkentofuitem').gray())
    event.add('pamhc2foodextended:firmtofuitem', Text.translate('tooltip.ninjacatpack.firmtofuitem').gray())
  }
  event.add('minecraft:leather', Text.translate('tooltip.ninjacatpack.leather').gray())
  event.add('voidloom:void_yarn', [
    Text.translate('tooltip.ninjacatpack.void_yarn.1').gray(),
    Text.translate('tooltip.ninjacatpack.void_yarn.2').darkGray()
  ])
  event.add('voidloom:binding_knot', [
    Text.translate('tooltip.ninjacatpack.binding_knot.1').gray(),
    Text.translate('tooltip.ninjacatpack.binding_knot.2').darkGray()
  ])
  event.add('ninjacatskies:tension_post', [
    Text.translate('tooltip.ninjacatpack.tension_post.1').gray(),
    Text.translate('tooltip.ninjacatpack.tension_post.2').darkGray()
  ])
  event.add('ninjacatskies:braid_cord', Text.translate('tooltip.ninjacatpack.braid_cord').gray())
  event.add('ninjacatskies:spindle_loom_fragment', Text.translate('tooltip.ninjacatpack.spindle_loom_fragment').gold())
  if (Item.exists('mysticalagriculture:inferium_ore')) {
    event.add('mysticalagriculture:inferium_essence', Text.translate('tooltip.ninjacatpack.inferium_essence').gray())
    event.add('mysticalagriculture:prosperity_shard', Text.translate('tooltip.ninjacatpack.prosperity_shard').gray())
    event.add('mysticalagriculture:inferium_ore', Text.translate('tooltip.ninjacatpack.inferium_ore').gray())
    event.add('mysticalagriculture:prosperity_ore', Text.translate('tooltip.ninjacatpack.prosperity_ore').gray())
  }
  event.add(/productivebees:.*_nest$/, Text.translate('tooltip.ninjacatpack.productivebees_nest').gray())
  event.add('productivebees:oak_wood_nest', Text.translate('tooltip.ninjacatpack.oak_wood_nest').darkGray())
  event.add('minecraft:bee_nest', Text.translate('tooltip.ninjacatpack.bee_nest').gray())
  if (Item.exists('tribalpower:pulse_resonator')) {
    event.add('tribalpower:pulse_resonator', Text.translate('tooltip.ninjacatpack.pulse_resonator').gray())
    event.add('tribalpower:ley_collector', Text.translate('tooltip.ninjacatpack.ley_collector').gray())
    event.add('tribalpower:pulse_cell', Text.translate('tooltip.ninjacatpack.pulse_cell').gray())
  }
  if (Item.exists('tribalpower:drumheart')) {
    event.add('tribalpower:drumheart', Text.translate('tooltip.ninjacatpack.drumheart').gray())
  }
  if (Item.exists('tribalpower:march_stone')) {
    event.add('tribalpower:march_stone', Text.translate('tooltip.ninjacatpack.march_stone').gold())
  }
  // Tribal Power 3.0 — the Nine Tribes. Camps stand in the March; the pack's quests are in Tribal Weave.
  if (Item.exists('tribalpower:tribe_hearth')) {
    event.add('tribalpower:tribe_hearth', Text.translate('tooltip.ninjacatpack.tribe_hearth').gray())
    event.add('tribalpower:tribe_mark', Text.translate('tooltip.ninjacatpack.tribe_mark').gray())
    event.add('tribalpower:kinship_totem', Text.translate('tooltip.ninjacatpack.kinship_totem').gray())
    event.add('tribalpower:loom_thread', Text.translate('tooltip.ninjacatpack.loom_thread').gray())
    event.add('tribalpower:silent_drum', Text.translate('tooltip.ninjacatpack.silent_drum').gray())
    event.add(/tribalpower:rite_(green|rain|sky|dawn|still|ley|spring).*/, Text.translate('tooltip.ninjacatpack.tribalpower_rite').gray())
    event.add('tribalpower:bonding_charm', Text.translate('tooltip.ninjacatpack.bonding_charm').gray())
    event.add('tribalpower:camp_charter', Text.translate('tooltip.ninjacatpack.camp_charter').gray())
    event.add('tribalpower:ley_lens', Text.translate('tooltip.ninjacatpack.ley_lens').gray())
    event.add('tribalpower:lattice_tuner', Text.translate('tooltip.ninjacatpack.lattice_tuner').gray())
    event.add('tribalpower:item_relay', Text.translate('tooltip.ninjacatpack.item_relay').gray())
    event.add('tribalpower:fluid_relay', Text.translate('tooltip.ninjacatpack.fluid_relay').gray())
  }
  // Tribal Power 3.2 — Listening Pit, gates, six voices. Quests are the rest of Tribal Weave.
  if (Item.exists('tribalpower:stone_font')) {
    event.add('tribalpower:stone_font', Text.translate('tooltip.ninjacatpack.stone_font').gray())
    event.add('tribalpower:resonance_mesh', Text.translate('tooltip.ninjacatpack.resonance_mesh').gray())
    event.add('tribalpower:anchor_stone', Text.translate('tooltip.ninjacatpack.anchor_stone').gray())
    event.add('tribalpower:gate_frame', Text.translate('tooltip.ninjacatpack.gate_frame').gray())
    event.add('tribalpower:gate_keystone', Text.translate('tooltip.ninjacatpack.gate_keystone').gray())
    event.add('tribalpower:gate_sigil', Text.translate('tooltip.ninjacatpack.gate_sigil').gray())
    event.add('tribalpower:ember_horn', Text.translate('tooltip.ninjacatpack.ember_horn').gray())
    event.add('tribalpower:wind_harp', Text.translate('tooltip.ninjacatpack.wind_harp').gray())
    event.add('tribalpower:wave_drum', Text.translate('tooltip.ninjacatpack.wave_drum').gray())
    event.add('tribalpower:wake_bell', Text.translate('tooltip.ninjacatpack.wake_bell').gray())
    event.add('tribalpower:loom_anchor', Text.translate('tooltip.ninjacatpack.loom_anchor').gray())
    event.add('tribalpower:pulse_cairn', Text.translate('tooltip.ninjacatpack.pulse_cairn').gray())
    event.add('tribalpower:music_disc_drum_circle', Text.translate('tooltip.ninjacatpack.music_disc_drum_circle').gray())
  }
  if (Item.exists('tribalpower:shard_lamp')) {
    event.add('tribalpower:shard_lamp', Text.translate('tooltip.ninjacatpack.shard_lamp').gray())
    event.add('tribalpower:glow_reed', Text.translate('tooltip.ninjacatpack.glow_reed').gray())
    event.add('tribalpower:echo_sconce', Text.translate('tooltip.ninjacatpack.echo_sconce').gray())
    event.add('tribalpower:ember_bowl', Text.translate('tooltip.ninjacatpack.ember_bowl').gray())
    event.add('tribalpower:sky_charm', Text.translate('tooltip.ninjacatpack.sky_charm').gray())
    event.add('tribalpower:chorus_charm', Text.translate('tooltip.ninjacatpack.chorus_charm').gray())
    event.add('tribalpower:seal_loom', Text.translate('tooltip.ninjacatpack.seal_loom').gray())
    event.add('tribalpower:tide_pump', Text.translate('tooltip.ninjacatpack.tide_pump').gray())
    event.add('tribalpower:ember_kiln', Text.translate('tooltip.ninjacatpack.ember_kiln').gray())
    event.add('tribalpower:pulse_adapter', Text.translate('tooltip.ninjacatpack.pulse_adapter').gray())
    event.add('tribalpower:wind_charm', Text.translate('tooltip.ninjacatpack.wind_charm').gray())
  }
})
