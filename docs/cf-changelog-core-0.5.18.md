# Ninjacat Skies Core 0.5.18

**Clowder Hall builds its town from the pack.** Existing saves load as they are; no ids change.

- **The hub town comes from a datapack.** Clowder Hall now raises its town from `data/clowderhall/towns/clowder_town.json`
  when a pack provides one (Ninjacat Skies 0.10.0 ships Loom's End). Each plan carries a revision: a world is rebuilt
  once when the revision goes up, and whatever the older town left behind is cleared. Without a plan, Core raises only
  the ceremony pad, as before.
- **Your things are never replaced.** A rebuild leaves the drop chest, any stocked container and every Yarn Basket
  exactly as they were, and never touches the chest, lectern, beacon or reweave ring.
- **Town residents.** A plan can seat any creature with its own data and tags; residents keep their names across
  revisions and walk to their new places instead of doubling up. Shop wares hang in fixed frames nobody can empty.
- **The Hall keeps the world's time.** It no longer stays at noon, so its townsfolk can work, gather and sleep.
- **Safer building.** A block from a mod that is not installed, or a renamed block state, is skipped with a warning
  instead of stopping the whole town; a broken plan is logged and never locks players out of `/clowder hub`.
- The Whisker Codex's "Earning Thread back" page names the Seal-carvers as the diamond sellers.

1.21.1 / NeoForge 21.1.249.
