// Claw's Blueprint Package is Silent Gear's first-join gift. Skyblock Builder
// clearInitialInventory wipes that gift when a pad is claimed, and the package
// has no vanilla recipe — so Claw's second quest was void-blocked.
ServerEvents.recipes(event => {
  if (!Item.exists('silentgear:blueprint_package')) return
  event.shapeless('silentgear:blueprint_package', [
    'silentgear:blueprint_paper',
    'silentgear:blueprint_paper',
    'silentgear:blueprint_paper',
    'silentgear:blueprint_paper',
  ]).id('ninjacatskies:blueprint_package')
})
