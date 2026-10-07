# Ninjacat Skies Core 0.5.23

**Said once.** A fix and a polish pass with nothing new to build. Existing saves load as they are; no ids change.

- **Hints print once.** With Tribal Power, Chocobos Reborn or Shamanic Mounts installed, every hint line showed once per mod, four times over. The Core's hint handler now speaks only for the companion mods' own items.
- **Guardians keep their shape across a reload.** The First Cut's severed strip mends after a reload instead of never; the Sealbreaker's ward glass and the Tangle's webs from before a reload are cleared and rot on schedule; the Lint Golem's void-lost snowballs and the Unwoven's quoted gravel are cleaned up on defeat; the Hivemind's smoked-cell count reads true; the Cogwright shows the first tile of its sequence, which it used to skip.
- **Driftwrecks.** Hovering a pillar objective after a deferred completion no longer crashes; the stone remnant's gravel count stays in sync for everyone watching; clients without the atlas channel are skipped rather than disconnected.
- **Voidloom.** The Loomframe's progress no longer climbs past full while a finished roll waits for room below; the Loomframe and Tension Barrel save and notify their neighbours less often, with the same output.
- **Clowder Hall.** A malformed block id in a town plan is skipped as documented instead of failing the whole town; plan scans are faster; the plan cache is released when the server stops.
- **Craftweave.** A recipe pick is tested against the grid alone on each grid change instead of against every recipe in the pack, and the recipe-count chip caches its count instead of rebuilding it every frame.
