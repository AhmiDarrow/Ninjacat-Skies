// Hide Occultism JEI ritual-dummy clutter. Guarded: the KubeJS JEI event binding name varies by build,
// so a missing binding must never crash client-script loading (this replaces a hard JEIEvents reference).
if (typeof JEIEvents !== 'undefined') {
  try {
    JEIEvents.removeEntries(event => {
      event.remove('occultism:ritual_dummy')
      event.remove('occultism:jei_dummy')
    })
  } catch (err) {
    console.warn('[Ninjacat Skies] JEI hide skipped (binding differs this build): ' + err)
  }
}
