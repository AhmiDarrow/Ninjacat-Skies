# Ninjacat Skies 0.12.1 — Held Thread

Pack CurseForge client file **9851082**, server additional **9851090**. Ninjacat Skies Core 0.6.1 is file **9850769** (sha1 `878f9f64ed47e1871debddf0ef37872445c38f8f`). Tribal Power moves to 6.2.0, file **9643408**.

106 mods (102 on the server). Existing saves load. See `docs/cf-changelog-0.12.1.md` and `docs/cf-changelog-core-0.6.1.md` for the player-facing notes.

Guardian arenas remember player-placed blocks by block id now. Positions saved by older versions are still cleared on reuse, but blocks already standing there no longer drop.

Verified: all release gates with the export dry run; GameTests craftweave 5, voidloom 12, ninjacatskies 25, guardians 10, driftwrecks 22; the Tribal Bench patch attaching with the pack's jars loaded. Not run: the full-pack dedicated server gate and a client play test.
