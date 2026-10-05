# 0.10.16 — The Woven Lattice

Tribal Power 5.6.0. Everything else stays as it is in 0.10.15. Existing saves load, but read the note below. 106 mods.

**Heads up: Tribal Power bases need a Lattice Conductor.** Machines no longer draw Pulse straight from nearby generators. Place a **Lattice Conductor** within 8 blocks of your generators and machines and your base comes back; one in the middle of a small camp is usually enough. You get a one-time chat message about it when you log in.

**Tribal Power**

- **Pulse travels along the lattice.** Anything within 8 blocks of a Lattice Conductor is on it, and conductors within 8 of each other link into one network. Machines draw only from their network's generators and Pulse Cairns.
- **Ranked conductors and cairns.** Conductors carry 64, 256, 1,024 or 4,096 Pulse a second by rank; Pulse Cairn stones hold 4,000 to 256,000 and move Pulse at the same rates.
- **Totems keep their voice on the lattice.** A totem's buffer fills while its network holds Pulse and drains when it doesn't; an empty totem is silent.
- **Clear readouts.** The Codex diagnosis, the Ley Lens and Jade show which network a block is on and what its conductor carries.
- **Lighter on servers.** Networks are woven once and cached instead of rescanned every tick.
