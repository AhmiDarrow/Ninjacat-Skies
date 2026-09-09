# Ninjacat Skies 0.7.1-alpha — the Nine Tribes, and the guardians finished

Tribal Power **3.0.0** comes into the pack with every one of its additions wired into the quests and the Codex, and the alpha gaps left open in 0.7.0 are closed. Companion mods move to **0.4.1**.

## Tribal Power 3.0 — the Nine Tribes
Tribal Weave (chapter 34) grows by 31 quests, every one reachable from a void pad because everything new stands in the March beyond the Gate Drum:
- **The March remembers.** Ancestor Halls (advancement), Loom Thread, Lore Tablets, the Silent Drum, The Unsung (advancement *The Drum Remembers*), the Unsung Heart and the **Resonance Totem (Loom)** — the sixth voice — plus the Loom Seal, the Echo Unweave and the Sixfold Staff's Tether and Stitch.
- **The Nine Tribes.** Offerings at a Tribe Hearth, Friend standing, the Tribe Mark from an Elder at Voice, the Kinship Totem (up to fifteen voices for the Pulse Resonator), and a camp Drummer feeding your Drumheart.
- **Rites.** All six Rite Tablets with their reagents and seals, and *First Rite*.
- **Bound spirits and shared camps.** Bonding Charm and *A friend in the dark*; Camp Charter and *One vault, one budget*.
- **Reading the lattice.** Ley Lens, Pulse Gauge, Pulse Threshold, and the Codex's diagnostic report.
- The Whisker Codex's nine tribe pages each gain their camp (where it stands, what its hearth favours, what its Elder trades), plus *The Nine Camps* and *The Unsung* entries and five new Living Lattice pages. Tooltips on the new items point at the right chapter.
- Every quest keeps its id: appended quests draw ids from a per-chapter block, so no chapter after Tribal Weave moves and no progress is lost.

## Snapped Guardians — the 0.7.0 gaps
- **Grindcore** now does what the design says, against the real Ex Deorum API: a wearer's hand sieves get one extra fortune roll (Ex Deorum's own 30 % odds, one more level). Mining Fatigue immunity stays; the Haste stand-in is gone.
- **Hivecall** hurries hives for real: every Productive Bees hive or nest and every vanilla hive within 16 blocks of the wearer gets one extra tick every ten — 10 % faster, through the mods' own tick methods.
- The Overweaver's **shades carry no boss bar**; only the loom itself does.
- **Totem recipes are gated.** They appear in the recipe book when the Strand is seated (Lint Golem with Soil, Tangle with Claw, the two insane ones after the Reweave), Clowder mates who were offline get theirs at login, and a gate totem only answers a Clowder that has seated that Strand — the tooltip says so.
- A new **Snapped Guardians** quest chapter (39, in the Reweave group): totem → re-tension → relic for all thirteen, the gate totems depending on each Strand's *Seat* quest, the sealed door on the Reweave. The Codex gains a **Snapped Guardians** category: the ritual, then one entry per guardian with its arena, its fight, its totem and its relic, unlocking as Strands seat.

## Verified
All gates: sanitized public surface, quest item audit (1211 items, 0 missing, 0 dead ends), reachability (no unreachable main-line items), CF distribution and export dry-run. Guardians GameTests: 4/4 (arena plans, every guardian fights and dies, totem loop, and the new gate-refusal / no-boss-bar test). Companion mods compile against exdeorum-3.12 and productivebees-13.13.5 (ProductiveLib unpacked from the Productive Bees jar at build time).

## Still open
- The custom boss renderer has still only been compile-checked (no client in the build environment): check facing in-game; `-Dguardians.flipFacing=true` if wrong.
- Balance remains first-guess.

Save compatibility: content only. New quests, new Codex pages, new recipes-unlock behaviour; nothing existing changes id. Tribal Power 3.0.0 is itself save-stable per its release notes; its structures appear in newly generated March chunks. Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21.
