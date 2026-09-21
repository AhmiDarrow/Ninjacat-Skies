# Ninjacat Skies 0.8.7 — A braid needs a Post

Ninjacat Skies Core 0.5.6. One progression fix: the **Braid Cord** no longer waits on seated
Strands, which moves the **Thread of Return** out of the late game. Existing saves load as they
are; no quest ids change, nothing already seated or earned is touched, and the mod list is
unchanged at 104.

- **Ninjacat Skies Core 0.5.6 - Sixteen filaments to a braid** (project 1689718, file
  **8935836**): spinning a Braid Cord used to need two of **Clock**, **Swarm** or **Spark**
  seated at a Tension Post. A Strand token is the reward at the end of a whole Strand chapter, so
  the Cord — and the Thread of Return built around it — sat most of the way through the pack,
  behind the players least likely to have a spare life to fall back on. Now it costs **16 Strand
  Filaments** at the Post and no Strand has to be seated: the gate that moved was progression,
  not effort. A Post short of the price takes nothing and says how many more it wants.
  Changelog: `cf-changelog-core-0.5.6.md`.
- **Filaments are work, not a wall.** They come out of an iron Thread Mesh over gravel, sand or
  dust, and the Post itself is logs around a Binding Knot, so both ends of the recipe are early.
- **The rule is rewritten everywhere it was written down**, not just in the code: the Codex
  (`braid/bind`, `first_steps/choose_branches`, `the_cut/tension`, `the_work/the_campaign`), both
  Bind quest descriptions and their shared "How:" line, the Strand Filament tooltip, and the
  starter book.
- **Nothing else about the Post moves.** Strand tokens seat the same way, the **Spindle Loom
  Fragment** still wants all nine Strands and a March stone, and seating the Fragment is still the
  Reweave.

Known, and unchanged here: a Thread of Return is four **Thread Shards** around the Cord, and a
Shard still costs four diamonds, four Void Yarn and a `driftwrecks:rift_shard` — or 400 Frayed
Thread at the Spark stall, four a day. The rift shard comes from mending a Remnant, which needs a
Weft Key, which the Salvager only sells at **seven Strands seated**. So the craft path to a life is
still late; the stall path (1600 Thread and a braid) is the one that is now open from the Post.

Pins: Ninjacat Skies Core 0.5.6 (project 1689718, file **8935836**), Tribal Power 3.7.1
(project 1684851, file **8934331**), Chocobos Reborn 1.0.8 (project 1699008, file **8926685**).
Client zip carries all 104 mods; the server zip installs 100. Minecraft 1.21.1 / NeoForge
21.1.249 / Java 21.
