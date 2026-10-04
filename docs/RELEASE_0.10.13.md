# Ninjacat Skies 0.10.13 — Filtered Relays and Only Followers

Pack CurseForge client file **TBD**, server additional **TBD**. Tribal Power 5.3.19 is CurseForge file **9053012**;
Chocobos Reborn 1.1.12 is **9053026**; Shamanic Mounts 0.1.13 is **9053028**. Ninjacat Skies Core 0.5.21 (9025453)
and Lithium 0.15.4 (8330365) are unchanged.

106 mods (102 on the server). Existing saves load as they are; no quest ids change.

See `docs/cf-changelog-0.10.13.md` for the player-facing notes.

- **Tribal Power 5.3.19** (sha1 `129444e2ff4c596c12c89d115e1e72632713d4a7`): relay plates get a Rune slot (seals only) and
  an eight-slot ghost whitelist/blacklist (default empty blacklist); the Bond slot is retired and bonded pairs turn into
  tuner links the first time both plates load; wall-mounted relay hitboxes sit against the host instead of the far side.
- **Chocobos Reborn 1.1.12** (sha1 `5b902d3b8ada148ac2107b10295fc9af29af05af`): the whistle calls only birds on Follow;
  the ledger keeps each bird's command so parked birds are never force-loaded.
- **Shamanic Mounts 0.1.13** (sha1 `e20cc3d0050d63d94f4e79de622ec1f86434a4a7`): the Mount Flute calls only mounts on
  Follow and no longer sets called mounts to Follow.
