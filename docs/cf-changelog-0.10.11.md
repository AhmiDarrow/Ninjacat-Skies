# 0.10.11 — Smooth Riding, a Cooler March, Small Foals

Chocobos Reborn 1.1.10, Tribal Power 5.3.18 and Shamanic Mounts 0.1.11. Everything else stays as it is in 0.10.10.
Existing saves load as they are; no quest ids change. 106 mods. Clients and servers must update together.

**Chocobos Reborn**

- **No more snapping back.** Your bird is yours to move. The server used to replay every step you took and pull you
  back whenever it disagreed, even by a sliver; on ground that steps by a sixteenth of a block (Heartfield's dip) a
  fast bird lost its pace about three times a lap. Now the server takes your move unless it is truly impossible.
- After a set-back, moves your game had already sent from the old place are dropped instead of each one snapping
  you back again.
- **Smoother rivals at speed.** The other birds are drawn from timed snapshots sent every tick instead of
  Minecraft's entity updates, which on a pack this size could stall and make the field freeze, then jump ahead.
- Every set-back now says why in the server log.

**Tribal Power**

- **A cooler March.** The Ember Wastes take only hot, dry ground now: hot, wet land becomes Reed Fen and hot high
  ground becomes Highlands, so a long flight through a warm stretch passes several biomes instead of one. Land you
  have already explored keeps its biomes; new ground uses the new layout.

**Shamanic Mounts**

- **One herd.** Tame mounts never fight each other: a maul, ram or coil that catches another tame mount does
  nothing, and tames never target each other. Wild mounts are still fair game.
- **Small foals.** A newborn foal is under a third of its grown size and grows a step every minute until it is
  full size at twenty minutes. Foals already in your world take the size for their age when they next load.
