# Shared Clowder lives

Lives are enabled by default. Each FTB team has one persistent pool, with each member contributing three starting lives: one member starts at 3, two at 6, three at 9. Offline members count. New members add their contribution once; reconnecting or leaving and rejoining the same team never refills it. Survival/adventure deaths spend one life. Creative and spectator players do not spend lives. At zero, surviving members become spectators and the dead member becomes a spectator on respawn. Offline members are checked when they return.

`/skybound lives` reports the current pool. Six scattered progression milestones offer a **Thread of Return**, each adding exactly one shared life: Seat Clock, Seat Sigil, Dragon Egg Show, Ultimate Cube, Thirteen voices, one sky, and Reweave. Claiming a reward credits the pool directly. Each milestone is recorded once per team, including across reloads and operator revives. There are no craftable, shop, mob-drop, loot-crate, or repeatable life rewards. Team size does not multiply them.

Operator-only `/skybound revive [player]` restores that player's team to the configured starting count multiplied by current team membership. `/clowder revive` is also operator-only. Ordinary players cannot reset their pool with a command. At zero with no earned reward left, an operator must decide whether to revive the team.

Configure `hardcore.livesEnabled` and `hardcore.startingLives` in `config/ninjacatskies-common.toml`. FTB team membership determines the pool; changing teams switches to the destination team's pool.
