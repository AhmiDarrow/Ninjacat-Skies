# Ninjacat Skies Core 0.5.19

**The Fray stands in the sky at Loom's End.** Existing saves load as they are; no ids change.

- **The cut is drawn on the sky, at Loom's End.** The Fray used to be a thin trickle of dark particles over the
  overworld Dock that only players standing there could see. It is now a real feature of the sundered sky, and it
  has moved to where the world was cut: past the broken end of the gate-path in Loom's End. Nine dark threads come
  up out of the bottom of the void, rooted far below the Hall, rise past the gate-path and fray two hundred blocks
  on into the sky, drawn on every client from anywhere in the town. It stands nowhere else.
- **It thins as the server reweaves.** The threads gather one at a time, outermost first, as any Clowder online seats
  a Strand, and the dark cut behind them narrows. The change eases in over a few seconds rather than snapping.
- **It lights at full Reweave.** Once every Clowder online has rewoven, only the spine is left and it turns to a
  single lit gold thread that breathes. The count now includes each Clowder's Reweave, not only its nine seats, so the
  thread lights when the last Fragment seats and not a step early.
- **Lint under the cut.** Near the gate-path's end the cut sheds dark lint; once the sky holds, lit motes climb the
  thread.
- **The server owns the Fray's place.** Clients are told which dimension and block the cut stands at
  (`loom.frayDimension`, `loom.frayX/Y/Z`; defaults are Loom's End at 0 63 -140) and how far the server has rewoven;
  an operator's config change moves it for everyone. Packs that put the Fray back over the overworld Dock can set
  `frayDimension = "minecraft:overworld"`.
- **`/skybound fray`** reports how far the server has rewoven. Operators can hold it at a value to look at it
  (`/skybound fray 0.5`, `/skybound fray 1`) and release it with `/skybound fray off`.

1.21.1 / NeoForge 21.1.249.
