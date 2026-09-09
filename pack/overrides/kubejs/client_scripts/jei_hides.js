// Hide Occultism's ritual/JEI dummy items from the recipe viewer (JEI, EMI or REI — KubeJS 2101 unifies them).
// Guarded so a binding change in a future KubeJS build can never break client-script loading.
if (typeof RecipeViewerEvents !== 'undefined') {
  try {
    RecipeViewerEvents.removeEntries('item', event => {
      event.remove(/^occultism:ritual_dummy(\/.*)?$/)
      event.remove(/^occultism:jei_dummy(\/.*)?$/)
    })
  } catch (err) {
    console.warn('[Ninjacat Skies] recipe-viewer hide skipped: ' + err)
  }
}
