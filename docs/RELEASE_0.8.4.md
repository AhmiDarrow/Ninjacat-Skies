# Ninjacat Skies 0.8.4 — Thread of Return

Pack CurseForge client file **TBD**, server additional **TBD**.

A Core build plus the pack economy around it: the shared Clowder life becomes something a
team can earn again after the six quest milestones run out. Existing saves load as they
are; no quest ids change and no other mod moves.

- **Ninjacat Skies Core 0.5.4 - Thread of Return** (project 1689718, file **8927258**):
  `ninjacatskies:thread_of_return` is an item that grants exactly one shared Clowder life
  and keeps no milestone receipt, so it is repeatable; `ninjacatskies:thread_shard` is the
  lives piece, four around a Braid Cord. Both drawn to the 32x32 house style. The six
  `skybound rewardlife` milestones are untouched. Changelog: `cf-changelog-core-0.5.4.md`.
- **Pack economy.** The Shard craft (`pack/overrides/kubejs/server_scripts/lives.js`) costs
  four diamonds, four Void Yarn and one `driftwrecks:rift_shard`, gating the craft path
  behind a mended Remnant. The Spark stall sells one Shard for 400 Frayed Thread,
  `max_uses: 4` against a daily restock — so a life is four Remnant kills or 1600 Thread.
- **Grit exchange counter.** Seven `grit_exchange_*.json` listings turn blocks of copper,
  iron, gold, amethyst, emerald and diamond, and netherite ingots, into Frayed Thread at
  9–15x worse than the buy-back price, capped by the daily restock at roughly 864 Thread a
  day. `tools/gates/test_life_rewards.py` fails if any rate drifts within 8x of a loop.
- **Docs and in-game text.** `docs/shared-lives.md` rewritten (it previously stated there
  was no craftable or shop life reward). Codex entries `first_steps/stuck` and
  `the_cut/thread` regenerated from `tools/whisker_lessons.py` and
  `tools/generate_codex_book.py`; tooltips in `voidloom_tooltips.js`.

Known drift, not addressed here: six Codex entries (`braid/colony`, `braid/listening_pit`,
`braid/living_lattice`, `first_steps/pad_runners`, `tribes/camps`, `tribes/spindle`) are
stale against their generators — the generators say Chocobo Almanac, the Gate Rite beats
and waking a bee nest with a second flower, while `tools/gates/test_codex_book.py` still
asserts the old `chocobosreborn:sage_notes` text. Regenerating them fails that gate, so
they were left at their shipped state. Resolve the generator/gate disagreement separately.

Pins: Ninjacat Skies Core 0.5.4 (project 1689718, file **8927258**), Tribal Power 3.6.2
(project 1684851, file **8925225**), Chocobos Reborn 1.0.8 (project 1699008, file
**8926685**). Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21.
