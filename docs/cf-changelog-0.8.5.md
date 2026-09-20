# 0.8.5 — Frames to spare

A performance pass on the pack itself, plus Tribal Power 3.7.0. Existing saves load as
they are, no quest ids change, and nothing a Clowder has earned is touched.

- **The pack finally has a renderer optimiser.** **Sodium** goes in, with **Reese's
  Sodium Options** so its settings are readable. There was no Embeddium or Rubidium here
  before, so this is the first one — it joins the ImmediatelyFast, EntityCulling,
  FerriteCore and ModernFix that were already doing the quieter half of the work.
- **Less wasted work, on both sides.** **BadOptimizations** cuts client work that repeats
  for no reason and **Dynamic FPS** idles the game down when the window is behind
  something else. On the server, **AI Improvements** makes mob goal ticking cheaper and
  **Saturn** cuts the garbage that chunk and entity work leaves behind.
- **spark is in the pack now.** If a tick will not come down, `/spark profiler` is already
  there — nobody has to go and install a profiler before they can tell you what is wrong.
- **Tribal Power 3.7.0 — The carried kit.** Spiritgear Shears and a Spiritgear Hoe join
  the set and rank and bind like the rest of it. The **Spirit Flask** and **Greater Spirit
  Flask** carry 4,000 and 16,000 mB as ordinary fluid containers. The **Totem Wrench**
  turns a block without breaking it and steps a machine face through Both, Input, Output
  and Closed. The **Weaver's Wand** carries the face you click across matching neighbours,
  up to 32 blocks. Every inventory worth tidying — your pack, caches, and any chest,
  barrel, shulker box or hopper — gains a **Tidy** button. The mod also got its own
  performance pass around camps and on the HUD.
- **AgriCraft crossing is worth doing.** Mutation chance is three times what it was, so a
  cross crop ringed with parents seeds inside a play session instead of over a weekend.
  Two quest lines now spell out the loop the mod never explains: a second set of sticks on
  one block makes a cross crop, and fertility is the stat that decides which plants get
  picked as parents.

**Server owners:** the server zip leaves out the four client-only mods (Sodium, Reese's,
BadOptimizations, Dynamic FPS) on purpose. Sodium in a server's `mods/` folder is a boot
crash, not a wasted megabyte — it touches LWJGL before NeoForge has read a single mod's
side. Client installs get all 104 mods; the server installs 100. Unzip the new server pack
over the old folder and run `install` again as usual.

Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21.
