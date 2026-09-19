# Ninjacat Skies Core 0.5.2

A bug-fix release. Existing saves load as they are.

**Snapped Guardians**
- A guardian knocked off its stage is put back. Before, dropping it into the void counted as a win and gave out the relic.
- Arena blocks drop nothing when broken, and explosions leave them alone. Blocks you place on a stage are cleared before the next fight there.
- Items you drop when you die in an arena come home with you.
- If you die, you are no longer pulled back into the fight when you respawn. You still get the relic if your party wins.
- An arena nobody is standing in ends after five minutes.
- The Drumheart's lava can no longer be left behind by a restart.

**Driftwrecks**
- Objectives, chests, mobs and rifts only appear where you can walk to them. They no longer end up in sealed crypts, on column tops or over the void.
- Hold crypts have working stairs. The watchtower has a ladder up to its crown.
- Hidden rooms keep their floor, and wells hold their water.
- A wreck that fails to arrive no longer affects the server.
- A win waiting for its Clowder to log in is still counted if the wreck unravels first.

**Ninjacat Skies**
- Joining a party brings everyone's Strands up to date at once.
- The Post's healing and fall protection no longer load its area from far away.
- With `sunderedSky = false` you get the normal overworld sky back, with clouds.
- Items saved for spectators are delivered even with lives turned off.

**Voidloom and Clowder Hall**
- The Island Charter seals a spawn point that actually holds, including on slabs and farmland.
- The Tension Barrel no longer drops empty buckets into the void or gives free bottles when broken.
- The Loomframe only takes in grit that its mesh can sift, so it no longer jams.
- Clowder Hall no longer gives a second starter kit.

1.21.1 / NeoForge 21.1.249.
