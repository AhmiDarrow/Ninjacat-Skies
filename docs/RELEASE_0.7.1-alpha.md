# Ninjacat Skies 0.7.1-alpha — the Nine Tribes, and the guardians finished

Tribal Power **3.0.0** comes into the pack with every one of its additions wired into the quests and the Codex, and the alpha gaps left open in 0.7.0 are closed. Companion mods move to **0.4.1**.

## Tribal Power 3.0 — the Nine Tribes
Tribal Weave (chapter 34) grows by 31 quests, every one reachable from a void pad because everything new stands in the March beyond the Gate Drum:
- **The March remembers.** Ancestor Halls (advancement), Loom Thread, Lore Tablets, the Silent Drum, The Unsung (advancement *The Drum Remembers*), the Unsung Heart and the **Resonance Totem (Loom)** — the sixth voice — plus the Loom Seal, the Echo Unweave and the Sixfold Staff's Tether and Stitch.
- **The Nine Tribes.** Offerings at a Tribe Hearth, Friend standing, the Tribe Mark from an Elder at Voice, the Kinship Totem (up to fifteen voices for the Pulse Resonator), and a camp Drummer feeding your Drumheart.
- **Rites.** All six Rite Tablets with their reagents and seals, and *First Rite*.
- **Bound spirits and shared camps.** Bonding Charm and *A friend in the dark*; Camp Charter and *One vault, one budget*.
- **Reading the lattice.** Ley Lens, Pulse Gauge, Pulse Threshold, and the Codex's diagnostic report.
- The Whisker Codex's nine tribe pages each gain their camp (where it stands, what its hearth favours, what its Elder trades), plus *The Nine Camps* and *The Unsung* entries and five new Living Lattice pages. Tooltips on the new items point at the right chapter.
- Existing quest progress is kept: no quest changes id.

## Snapped Guardians — the 0.7.0 gaps
- **Grindcore** now does what the design says, against the real Ex Deorum API: a wearer's hand sieves get one extra fortune roll (Ex Deorum's own 30 % odds, one more level). Mining Fatigue immunity stays; the Haste stand-in is gone.
- **Hivecall** hurries hives for real: every Productive Bees hive or nest and every vanilla hive within 16 blocks of the wearer gets one extra tick every ten — 10 % faster, through the mods' own tick methods.
- The Overweaver's **shades carry no boss bar**; only the loom itself does.
- **Totem recipes are gated.** They appear in the recipe book when the Strand is seated (Lint Golem with Soil, Tangle with Claw, the two insane ones after the Reweave), Clowder mates who were offline get theirs at login, and a gate totem only answers a Clowder that has seated that Strand — the tooltip says so.
- A new **Snapped Guardians** quest chapter (39, in the Reweave group): totem → re-tension → relic for all thirteen, the gate totems depending on each Strand's *Seat* quest, the sealed door on the Reweave. The Codex gains a **Snapped Guardians** category: the ritual, then one entry per guardian with its arena, its fight, its totem and its relic, unlocking as Strands seat.

## Bug sweep
A full pass over the pack's own mods, scripts and quest data, with the whole pack run as a server and the guardians played on a client. Fixed:

- **Voidloom recipes (broken since 0.6.6):** the Voidloom recipe script failed to load, so its recipes were missing in-game, and the thread meshes were not accepted by Ex Deorum sieves. Both work again.
- **Quests:** chapter and milestone subtitles now display.
- **Guardians, arenas:** several mechanics were aimed at the wrong spots in their arenas — the Overweaver's shades landed over the void, the Hivemind's cells could not be smoked, the Sealbreaker's wards, the Beddown's seams and the First Cut's seam were mirrored; all now match the built stages. The Unwoven's tile pattern no longer punishes every tick or draws unsolvable sequences; Drumheart lava stays off the beat pads; guardians no longer hurt themselves in their own scenery; the Unwoven's true-form threads and heddle drops behave; the Grindmaw only counts grit you bring; Thornmother stations sit at their lanterns; a server restart no longer ends a fight; a wipe cleans the arena properly; one player can no longer be in two arenas; the arenas are lit (noon under the End sky).
- **Guardians, relics:** relic cooldowns and timed effects survive restarts correctly (Edgestep could become permanent invulnerability after a restart; Edgestep charges could freeze); wearing two copies of a relic no longer doubles it; the Shard of the First Cut's armour pierce now applies; Reweave never makes a shared effect permanent; Downbeat stuns never stick; relic bees never linger or sting players; only real melee hits count as hits; Knotcharm no longer roots guardians or pets; Bloom hedges are not berry farms; boss animation stays smooth on old worlds.
- **Ninjacat Skies:** leaving or re-forming a party no longer restores a Clowder that has spent its last life; turning lives off in the config releases spectators; a solo player's Tension Post is never claimable by others; the Fragment on a second Post gives the right message.
- **Clowder Hall:** the ceremony chest kit is once per player (it refilled on every visit); travelling to the Hall while riding no longer freezes you; offline party owners are handled; parties keep their full display name; `/clowder accept` skips invites from deleted teams; team visit/join settings are no longer reset on every join; beds in the Hall do not set a respawn; the Dock is never altered by a spawn fallback; Charter invites are not re-sent. **Voidloom:** the Spindle Crook can be enchanted with books.

## Dedicated server pack
From this release every upload comes with **NinjacatSkies-Server-<version>.zip** as an additional file: the pack's five companion mods and Tribal Power, the server-side config, KubeJS scripts and Skyblock structures, a manifest of the exact CurseForge files the client uses, and `install.sh` / `install.bat` (PowerShell) that fetch NeoForge from maven.neoforged.net and every other mod from CurseForge's CDN with SHA-1 checks — no third-party jar is redistributed. `start.sh` / `start.bat` run it; `server.properties` already selects the Skyblock Builder void world. Tribal Power 3.0.0 is bundled directly in both zips for now (it is our own mod and its CurseForge file is still in review); once listed it goes back to a CurseForge reference.

Save compatibility: content only. New quests, new Codex pages, new recipes-unlock behaviour; nothing existing changes id. Tribal Power 3.0.0 is itself save-stable per its release notes; its structures appear in newly generated March chunks. Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21.
