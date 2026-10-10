# Ninjacat Skies 0.11.2 — Smooth Heats

Pack CurseForge client file **pending**, server additional **pending**. Chocobos Reborn 1.1.15 is CurseForge file **9118527**. Ninjacat Skies Core 0.5.24 (9095225), Tribal Power 6.1.0 (9115266), Shamanic Mounts 0.1.16 (9096218) and Lithium 0.15.4 (8330365) are unchanged.

106 mods (102 on the server). Existing saves load; no March reset. Whiskerwind relays each course once on its first heat after the update, and the race village once.

See `docs/cf-changelog-0.11.2.md` for the player-facing notes.

- **Chocobos Reborn 1.1.15 "Clean Sweep"** (sha1 `03aaec8ea12950b8ee053740acfbe1ee79bb8191`, GitHub release v1.1.15): birds skinned on the GPU (`skinned_bird` core shader; Iris/Oculus and glowing birds keep the CPU path), breed and blink atlases derived off the render thread, courses laid over the heat countdown within a 5 ms tick budget instead of in one tick, the Square sky from a vertex buffer. Betting: a waiting bet attaches to the next ranked heat wherever its owner stands, field odds `max(2, round(6 / fieldBirds))`, no field bets without field birds, refunds on an unfinished heat, Rook names the refusal. Plus the gauntlet bug sweep (race HUD as its own GUI layer, wins booked at placement, one-minute call and board fireworks restored, gate ride-through, safe whistle landings, spawn-egg fixes, fences/walls joined, Almanac on small windows). Verified: 326 unit tests, 125 GameTests, the five-profile latency harness on C_MEADOW with no corrections.
