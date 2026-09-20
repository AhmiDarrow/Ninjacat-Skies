# Ninjacat Skies 0.8.6 — Put it down somewhere

Pack CurseForge client file **8934522**, server additional **8934526**.

Tribal Power 3.7.1. Three of its recipes could not be crafted at all, and its camp furniture
stops being only furniture. Nothing else in the pack moves: same 104 mods, no quest ids
change, and existing saves load as they are.

- **Tribal Power 3.7.1 - Put it down somewhere** (project 1684851, file **8934331**):
  - **Three recipes were shadowed.** Two crafting recipes with the same shape and the same
    ingredients are not a duplicate but a disappearance — the recipe manager returns
    whichever it finds first and the other is silently uncraftable. **March Planks Slab**
    and the **Wall Shelf** were both a row of three March planks, so the shelf could not be
    made at all. The **Drift Plate** and **Hush Plate**, and the **Gate Sigil** and **Loom
    Seal**, were byte-identical pairs. The shelf is now three planks over a stick, the Hush
    Plate takes wool, and the Loom Seal is a blank seal and a Loom Thread — the pattern its
    sibling voice seals already follow. Drift Plate and Gate Sigil are unchanged, so
    anything already built or bookmarked still crafts the same way.
  - **Camp furniture holds things.** Four along a Wall Shelf's board, four on a March
    Table's top, one in a Spirit Urn's mouth: use with something in hand to set it down,
    empty-handed to take it back. What is set down is drawn where it was put, falls with
    the piece, and reads on a comparator. No face is open to a hopper or pipe — furniture,
    not storage. The **March Stool** seats one player, and the **Wind Charm** rings.
  - A GameTest now reads the recipes the server actually loaded and fails the build if any
    two ever claim one grid again, vanilla included.

Pins: Ninjacat Skies Core 0.5.4 (project 1689718, file **8927258**), Tribal Power 3.7.1
(project 1684851, file **8934331**), Chocobos Reborn 1.0.8 (project 1699008, file
**8926685**). Client zip carries all 104 mods; the server zip installs 100, the four
client-only ones left out as of 0.8.5. Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21.
