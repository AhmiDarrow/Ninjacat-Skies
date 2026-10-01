# Ninjacat Skies Core 0.5.21

**Lighter everywhere, measured on a real world.** A performance pass profiled on a copy of a long-running server.
Existing saves load as they are; no ids change. Clients and servers must update together.

- **Loom's End costs far less to run.** The hub no longer runs natural mob spawning, which could never place anything
  there (its ground is the void) but still cost about a fifth of the hub's tick. Residents, keepers, breeding and
  summoning work exactly as before.
- **A faster first build of the town.** When a new town revision raises the hub, each block type is read once instead
  of once per box, and cells that already hold the right block are skipped.
- **Idle machines rest.** Empty Loomframes and Tension Barrels stop checking redstone every tick, a working Loomframe
  remembers its last sieve answer, and Thread Locks stop scanning their whole neighbourhood once one plate is up.
- **Lighter every second.** The Clowder lives check, relic tracking and the wreck and arena block queues do less work and
  allocate less each tick.
- **The Fray draws in about half the time,** with the same look, and the Tension Post, Remnant and Craftweave table
  overlay do much less work per frame: the overlay no longer copies the grid and recounts your inventory several times
  a frame.
- **Fixed:** Craftweave remembered recipe picks forever; they are now cleared when a server stops, so a single-player
  world's picks no longer carry into the next world.
