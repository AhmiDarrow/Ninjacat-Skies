# Ninjacat Skies 0.8.9 — The March speaks

Pack CurseForge client file **TBD**, server additional **TBD**.

Tribal Power 5.0.1, Ninjacat Skies Core 0.5.13 and Chocobos Reborn 1.0.13. Existing saves load as they are; no quest ids
change, and the mod list is unchanged at 104.

- **Ninjacat Skies Core 0.5.13 - Translatable, Codex for Tribal 5.0, yarn baskets** (project 1689718, file
  **8968452**). Changelog: `cf-changelog-core-0.5.13.md`.
- **Tribal Power 5.0.1 - Urns in their place** (project 1684851, file **8968467**; the four Soul Urn
  recipes' bad `tools` category, found by this pack's server boot), which also brings **5.0.0 - The
  world tells its own story** (file 8968154), 4.1.0 (spirit layer, table, weapons, healing), 4.2.0 (Elders, requests, stories, relics,
  eight guardians, Ninth Agreement) and 4.3.0 (weather, surges, festivals, spirits, music) to the
  pack. Tribal Power 5.0 requires a kept Resonance Totem of the right voice within eight blocks of
  every automated device (`automationNeedsVoices`, left on): existing camps' tenders, anchors, wards
  and relays stop until one is placed. The pack ships no tribalpower config, so all 5.0 defaults apply
  (`guardiansEnabled`, `eventWarningSeconds` 120, `requestsPerDay` 3).
- **Chocobos Reborn 1.0.13 - Clear pages** (project 1699008, file **8960886**): almanac birds drawn at
  full detail.
- **Chapter 34 grows by 50 quests** (late ids `4200000000228046`-`228077`, all `no_cache`, 3 Thread
  each): the table (9), healing (7), weapons and anointing (5), camp kit (4), stories and relics (11),
  guardians and the Ninth Agreement (10), the living March and Chronicle (4). Ten automation quest
  descriptions now name the kept totem voice each device needs. `test_steward_caches` counts move to
  1701 rows / 1587 Thread rewards. The Codex gains six tribes-category entries (`elders`,
  `march_guardians`, `living_march`, `the_table`, `spirit_arms`, `voices`; +88 keys) and three tribe
  pages are corrected for 5.0.
- **Translatable Core.** Every player-facing string in the six Core mods, the Whisker Codex (both
  copies, via the generator) and the KubeJS tooltips is a lang key; `tools/gates/test_lang_keys.py`
  (LangKeys in Invoke-AllGates) keeps it that way.
- **Quest generator drift.** `tools/generate_quests.py` no longer reproduces the shipped quests (18
  chapters differ); the new Tribal quests were authored in it and spliced into the shipped files. Never
  run it in place.
- **Dismount key.** `PlayerDismountMixin` makes `Player.wantsToStopRiding` answer a server-side
  request from the new Dismount key (Caps Lock, `key.ninjacatskies.dismount`, in the pack preset,
  now 53 shortcuts) instead of sneak. For that one ride tick the rider reads as sneaking, so Chocobos
  Reborn's mid-air, water and race dismount locks still apply. Config `controls.sneakDismounts`
  restores vanilla. `DismountGameTests` covers it. `LoomTension.sync` now skips a connection that
  never negotiated its channel.
- **Yarn Basket.** A `LivingDropsEvent` handler at LOWEST priority (after Curios adds its slots at
  HIGHEST, and after Guardians stashes stage deaths) puts a player's drops in a
  `ninjacatskies:yarn_basket` block entity where they died, or at their last solid footing after a
  void fall. It skips `guardians:arena`, where rift chambers are cleared. The owner, their Clowder or
  a creative player can right-click it (items to inventory) or break it (items spill); strangers get
  zero break progress. Explosion-proof, push-proof, drops its contents however it is removed. The
  Hall's break protection exempts it. Config `hardcore.yarnBasket`. `BasketGameTests` covers a real
  drop event, the void fallback, breaking, stranger protection and right-click recovery.
- **Stall prices over one stack.** `MerchantOffer.getCostA()` clamps a price to the cost item's max
  stack size, so Spark's 80 / 80 / 200 / 400 / 1000 Thread listings all charged 64. Core adds the
  Thread Skein (9) and Thread Bolt (81); the five listings are 9 / 9 / 22 skeins, 44 skeins and 12
  bolts (81 / 81 / 198 / 396 / 972 Thread). `test_life_rewards.py` now values Thread by denomination,
  keeps the shard at 300+ Thread, and fails any listing over 64. Quest how-lines, the Thread Shard
  tooltip, the Codex Thread entry and `shared-lives.md` quote the new prices.
- **Steward Caches.** Better supply pools per tier, a garden pool (saplings, seeds, crops, flowers and
  passive vanilla spawn eggs; quests assumed pad livestock nobody could get) and a decor pool, now
  written by `tools/generate_provisions.py`, and one rare draw per seal (Thread Shard 1% / 3% /
  10%, Thread of Return 0.2% / 0.5% / 1.5%). With 412 small, 114 medium and 6 large caches in the
  campaign, that averages about eleven Shards and 1.5 whole Threads per playthrough.

Pins: Ninjacat Skies Core 0.5.13 (project 1689718, file **8968452**), Tribal Power 5.0.1 (project
1684851, file **8968467**), Chocobos Reborn 1.0.13 (project 1699008, file **8960886**). Client zip
carries all 104 mods; the server zip installs 100. Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21.
