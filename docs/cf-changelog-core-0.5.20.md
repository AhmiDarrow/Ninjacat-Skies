# Ninjacat Skies Core 0.5.20

**A long sweep: guardians fight as designed, wrecks behave, and the sky keeps its word.** Existing saves load as they
are; no ids change. Clients and servers must update together (two new server-to-client messages).

- **Guardian music plays.** Every guardian's own track now takes over the music while you are in its fight, loops
  until the fight ends, and stops on a win, a wipe or when you leave.
- **The Hivemind's drones fly.** They were spawning inside the amber wall and suffocating before they reached you;
  they now come out in open air in front of each cell, so the fight is as hard as it was built to be. Bee relics
  (Hivecall, the Shuttle) no longer calm the drones or any other bee inside a guardian arena.
- **Fairer guardian fights.** The Cogwright never repeats a tile in a pattern, so a correct run can no longer fail on
  a tile you already did. After a server restart the Overweaver waits for its shades to reload instead of opening a
  free damage window, and the Beddown's dirt flood drains. Grindmaw grit waits for room instead of vanishing and
  deleting the block in its way. Drumpulse no longer stuns guardians, the Remnant or other mods' bosses.
- **Leaving is clean.** `/guardians leave` and the end of a rift only move players who are still inside; anyone who
  already respawned at home stays home. "The Strand re-tensions" only shows for guardians that have one, and a stray
  debug line during the Overweaver fight is gone.
- **Drift wrecks.** A Heartwreck whose win was waiting for its owners now always comes back. A Tension Post in
  another dimension no longer places its wreck in the Overworld. Burning wrecks keep burning but can no longer spread
  fire (blue soul fire where wood is near). The crumble catches overhangs it used to leave hanging, and large wrecks no
  longer allocate millions of objects in one tick while they fall. Wreck placement spreads its chunk searches over
  several ticks instead of generating dozens of chunks at once. The Salvager's Frame closes its trade screen when you
  walk away or it breaks.
- **The Atlas.** Stamps show full names (Overgrown, Haunted, Burning, ...) instead of cut-off ones, and the Atlas
  forgets the previous world's wrecks when you log out.
- **The sky.** Joining no longer shows the Fray fully torn for twenty seconds before it settles; a config change that
  moves or hides it reaches players at once; the previous server's sky tint no longer follows you into the next.
  Short Nights now follows the server's setting on every client, so a client with a different config no longer
  jitters the night sky.
- **Craftweave.** On a server without Craftweave its buttons no longer appear, and clicking one no longer crashes the
  client. Grid changes are cheaper for players who never picked a recipe.
- **Smaller fixes.** Owners can break their own Yarn Basket in survival again. A dismount request left over from
  another world no longer throws you off your first ride. The dismount hint hides when a server lets sneak dismount.
- **The Codex.** The Fray stands at Loom's End on every page; Tribal Power trades, the Echo catalyst, the Silent Drum
  and several tooltips match Tribal Power 5.3.12; the tribe keepers are named for their tribes (Grit-singers,
  Drumhearts).

1.21.1 / NeoForge 21.1.249.
