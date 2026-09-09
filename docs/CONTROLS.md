# Pack controls

The pack applies its curated defaults once on first launch or upgrade. Existing customized bindings are preserved. Use **Options → Controls → Key Binds → Pack defaults** to explicitly reapply the preset. Graphics, audio, mouse sensitivity and accessibility settings are untouched.

## Everyday controls

- **Grave / backtick (`):** quests. Right-click the Whisker Codex also opens the live quest book; Shift + right-click opens its lore pages.
- **K:** Clowder island and invitation panel. Hold the Island Charter and **right-click a friend to invite** them (or `/clowder invite <name>`; they run `/clowder accept`). The Island Charter opens the same panel anywhere; sneak-use on solid Overworld pad ground seals spawn.
- **Alt+K:** FTB party team panel.
- **M:** Xaero world map. **Ctrl+M:** FTB claims map. **Ctrl+Comma:** claim manager.
- **B:** Sophisticated Backpack. **Ctrl+B:** Occultism backpack. **G:** Curios.
- **C / V / Z / X:** Ars spellbook, selection, previous spell, next spell.
- **R / H:** Iron's spell casting and spell wheel.
- **J:** AE2 wireless terminal. **N:** Mekanism tool mode.
- **Y / U / O:** create waypoint, manage waypoints, enlarge minimap.

JEI recipe/uses keys remain R/U while hovering items in an inventory. Those are contextual shortcuts, not competing world actions. Modifier and tooltip keys such as Shift and Ctrl intentionally have contextual uses. Optional quick-cast slots, familiar abilities, debug tools and duplicate minimap functions can remain unbound; their normal menus/items remain available.

## Complete curated preset

- `key.ftbquests.quests`: **Grave Accent** (world context).
- `skyguis.key.all_teams_screen`: **K** (world context).
- `gui.xaero_open_map`: **M** (world context).
- `key.sophisticatedbackpacks.open_backpack`: **B** (world context).
- `key.curios.open.desc`: **G** (world context).
- `key.ars_nouveau.open_book`: **C** (world context).
- `key.ars_nouveau.selection_hud`: **V** (world context).
- `key.ars_nouveau.next_slot`: **X** (world context).
- `key.ars_nouveau.previous_slot`: **Z** (world context).
- `key.irons_spellbooks.spellbook_cast`: **R** (world context).
- `key.irons_spellbooks.spell_wheel`: **H** (world context).
- `key.mekanism.mode`: **N** (world context).
- `key.mekanism.module_tweaker`: **Backslash** (world context).
- `key.mekanism.key_hud`: **F10** (world context).
- `key.ae2.wireless_terminal`: **J** (world context).
- `gui.xaero_new_waypoint`: **Y** (world context).
- `gui.xaero_waypoints_key`: **U** (world context).
- `gui.xaero_enlarge_map`: **O** (world context).
- `key.ftbchunks.map`: **Control+M** (world context).
- `key.ftbchunks.claim_manager`: **Control+Comma** (world context).
- `key.ftbquests.cycle_pinned_tracker`: **Control+Grave Accent** (world context).
- `key.occultism.backpack`: **Control+B** (world context).
- `key.occultism.storage_remote`: **Control+N** (world context).
- `key.ae2.wireless_pattern_access_terminal`: **Control+J** (world context).
- `key.ae2.portable_item_cell`: **Control+I** (world context).
- `gui.xaero_minimap_settings`: **Control+Y** (world context).
- `gui.xaero_toggle_map`: **Control+O** (world context).
- `gui.xaero_toggle_waypoints`: **Control+U** (world context).
- `key.ftbteams.open_gui`: **Alt+K** (world context).
- `key.mekanism.head_mode`: **Alt+V** (world context).
- `key.mekanism.chest_mode`: **Alt+G** (world context).
- `key.mekanism.legs_mode`: **Alt+J** (world context).
- `key.mekanism.feet_mode`: **Alt+B** (world context).
- `key.ars_nouveau.head_curio_hotkey`: **Alt+C** (world context).
- `key.occultism.ender_bag`: **Alt+N** (world context).
- `key.ae2.wireless_pattern_encoding_terminal`: **Alt+P** (world context).
- `key.ae2.portable_fluid_cell`: **Alt+I** (world context).
- `supplementaries.keybind.quiver`: **Alt+R** (world context).
- `gui.xaero_open_settings`: **Alt+Y** (world context).
- `key.guideme.guide`: **Control+G** (original context).
- `key.kubejs.kubedex`: **F8** (original context).
- `key.modularrouters.configure`: **Control+C** (original context).
- `key.modularrouters.moduleInfo`: **I** (original context).
- `key.silentgear.cycle.back`: **Control+Z** (original context).
- `key.silentgear.cycle.next`: **Control+X** (original context).
- `key.silentgear.openItem`: **Alt+X** (original context).
- `key.sophisticatedbackpacks.inventory_interaction`: **Alt+Semicolon** (original context).
- `key.sophisticatedbackpacks.tool_swap`: **Control+Semicolon** (original context).
- `key.saveToolbarActivator`: **F6** (original context).
- `key.loadToolbarActivator`: **F7** (original context).

## Snapped Guardians (0.7.0)
- **Frayed Totem** (one per guardian): right-click anywhere outside an arena to call that guardian. Clowder mates within 32 blocks are pulled in with you. The totem is spent when the fight starts.
- In the arena: the teal **spawn pads** are where you land; falling off the stage returns you to your pad with damage; the **return gate** (teal arch) opens on a win or a wipe and everyone is sent home after a few seconds.
- `/guardians leave` — abandon the fight (counts as a wipe). `/guardians status` — running arenas. Operators: `/guardians summon <id>`.
- **Woven Relics**: worn in the Curios "relic" slot, the off-hand, or any hotbar slot. Right-click to use the active; the cooldown shows on the item.
- Totem recipes appear in the recipe book when their Strand is seated (Lint Golem with Soil, Tangle with Claw, the two insane ones after the Reweave), and a totem only answers once that is true.

## Tribal Power 3.0 — the Nine Tribes (0.7.1)
- **Tribe Hearth** (in the nine March camps): right-click with a favoured item or a charged Pulse Cell to raise standing. Sneak-use the Spirit Codex on any Tribal block for a diagnostic report.
- **Elder**: right-click to trade (two offers per rank). At Voice standing the Elder hands over the tribe's **Mark**.
- **Silent Drum**: right-click four times, a breath apart, to wake The Unsung; the same rhythm resyncs it during its Silence.
- **Rite Tablet**: sneak-right-click a Ritual Brazier that has the matching seal seated.
- **Bonding Charm**: right-click an adult Lantern Fox, Mossback or Dawn Stag. Sneak-right-click a bonded animal to toggle stay/follow; empty-hand sneak-right-click a Mossback opens its saddlebag; right-click a bonded Dawn Stag to ride.
- **Camp Charter**: right-click a player to invite; right-click the air to see your camp.
- `/tribalpower standing [player]` — the nine standings. `/tribalpower camp create|invite|join|leave|kick|info|rename`.
