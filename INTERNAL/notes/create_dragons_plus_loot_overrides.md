# Why pack/overrides/kubejs/data/create_dragons_plus/loot_table/blocks/*fragile_fluid_tank.json exist

Create Dragons Plus 1.11.8b registers `fragile_fluid_tank` / `levitite_fragile_fluid_tank` only when the `simulated`
mod is present, but ships their block loot tables unconditionally, so every server/client start logs
`Couldn't parse element ... Unknown registry key ... create_dragons_plus:fragile_fluid_tank`. The pack overrides both
tables with a copy carrying `neoforge:conditions: mod_loaded simulated`: without `simulated` the override is skipped
*and* the mod's own table is shadowed, so nothing is parsed and nothing is logged; with `simulated` the copy is the
mod's table. The blocks do not exist in this pack, so no drop is lost. Verified 2026-09-09 by booting the server pack
without the overrides (errors return) and with them (clean).
