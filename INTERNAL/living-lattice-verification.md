# Living Lattice verification — 2026-09-06

Candidate: Ninjacat Skies 0.4.0-alpha, custom Skies mods 0.3.0, Tribal Power 2.1.0; Minecraft 1.21.1 / NeoForge 21.1.249.

All six pack gates passed. The quest audit covers 1,470 quests in 38 chapters, with 1,140 distinct quest item references, zero missing items, and zero reported dead ends. Four runtime-format regression tests cover signed quest IDs, references, literal ampersands, and UTF-8 text. The custom mods compiled successfully.

All seven standalone Tribal Power GameTests passed: reusable resonator catalysts; processing output capacity and conservation; item relay conservation and redstone; cross-dimensional fluid conservation; transport tier restrictions and cell capacity; one-way FE conversion and redstone; cached storage capability redstone locks.

The full pack client joined the dedicated local server successfully. Visual checks confirmed the atlas background, custom node frames, chapter mastheads, themed detail panels, chapter grouping, corrected chapter names, and Tribal Weave navigation. The checks uncovered and fixed invalid signed-long quest IDs, a Codex empty-item sync failure, malformed FancyMenu assignments, unescaped ampersands, and JSON Unicode escapes incompatible with FTB SNBT.

Fresh saves are the supported test baseline. The owner explicitly excluded old-save migration because there are no public downloads yet.

Final visual recheck confirmed the Spirit Totem description renders “Fifth tribe — steward core.” correctly after a server restart and reconnect. Final export: `dist/NinjacatSkies-0.4.0-alpha-20260906-222624.zip`. Its packaged quest text was checked for the ampersand and Unicode fixes. The local verification server was stopped after testing.

This is an alpha verification pass, not exhaustive playthrough coverage of every recipe, ritual, visual effect, or third-party interaction. Upstream optional compatibility/model/subtitle warnings remain in the client log. No public upload was performed.

## Follow-up transport review

Fixed three relay edge cases: saved links are revalidated against the relay's current position and tier on every work cycle; redstone-powered destinations pause transport even for vanilla containers; buffered fluid can finish delivery after the source tank is removed. Binding also immediately refreshes comparator state. Nine GameTests now pass, including two new saved-data scenarios and expanded destination redstone coverage. No client rendering changes were made in this follow-up.

## Processing and waypoint review

Stations now distribute recipe outputs across available partial stacks, respecting item and container stack limits. Previously a two-item result incorrectly stalled when two output stacks each had one space remaining. A regression GameTest verifies both stacks finish at 64 and the single input is consumed. All ten GameTests pass. Waypoint world-border and build-height checks now run before destination chunk loading; this ordering change compiled but has no dedicated player-travel runtime test.

## Conductor automation review

Conductor item routing now continues when linked totems hold Pulse but cannot accept more. Previously routing depended on new Pulse being transferred that cycle, so full buffers stalled the item loop. Cache deliveries and bench handoffs now start the receiving Song Bench automatically. Pulse refund scans skip unloaded chunks. Twelve GameTests pass, including full-buffer routing with Pulse conservation and automated feed startup with item conservation. The chunk-scan guard was verified by source review, not a dedicated chunk-unloading fixture.

## Adversarial gauntlet

Two new tests failed before fixes: an oversized Song Bench stack collapsed 32 inputs into one output, and a bench handoff lost 31 excess items. Oversized inputs now stop safely with all contents recoverable; handoffs copy and remove exactly one item only after successful insertion. Five additional tests cover those cases, extreme signed integer Pulse requests and read-only simulation, unpowered relay/source-loop protection, and partial buffered fluid delivery across a save/load round trip. All seventeen gameplay tests pass. All six pack gates also passed (custom Skies compile reused; Tribal Power freshly compiled). This is targeted adversarial coverage, not a claim that arbitrary third-party capability contract violations or all player transport scenarios are covered.

## Second adversarial gauntlet

Before-fix tests reproduced stale chalk links activating unrelated totems and saved attunement overriding the actual totem block. Network traversal and attunement links now require live reciprocal links within range; chalk repairs one-sided links. Self-links and cross-level links are rejected. Totem attunement derives from its block when loading. Invalid saved work resets instead of overflowing in Song Benches and Echo stations. Direct bench input removal now clears active work and marks the change for saving. Five new regression tests cover stale links plus repair, malformed attunement, bench overflow, station overflow, and interrupted work. All twenty-two gameplay tests and all six pack gates pass (Skies build reused, Tribal freshly built). No client rendering changes or exhaustive third-party stress testing in this pass.

## Iterative adversarial gauntlet — final pass

Repeated review/fix/test rounds ended with no additional actionable issue found in the final targeted source pass. This is a stopping criterion for the reviewed paths, not proof of zero defects.

Fixed PulseStorage loading outside physical capacity and unbounded saved Drumheart cooldown. The randomized storage GameTest performs 8,000 insert/extract/simulation operations across negative, zero, capacity and integer extremes. Gate and waypoint arrivals share hazard/height checks; successful Gate travel clears fall distance and only then saves return memory. Cancelled transitions report failure; Gate Drum callers refund their stored charge, and waypoints use a refundable cell charge without applying cooldown or success effects. Mounted Gate travel is rejected. The server-player test exercises hazardous and redstone-locked destinations, cancellation, charge conservation, cooldown, fall-distance reset and the mounted Gate guard.

Voidloom processing now retains one paid random Loomframe batch until its output fits. It no longer rerolls blocked loot or spills excess output into the world. Pending items persist through reload, obey redstone locks, and are recovered when the block is broken. Tension Barrel output uses all partial stacks, and saved input/progress counters are bounded. Five new Voidloom GameTests cover these paths, bucket simulation and cached capability redstone behavior.

Malformed cache owner UUIDs no longer disable valid players' inventories or March flags. Unreadable records survive saving for recovery. A dedicated test verifies both valid data and malformed-record preservation.

Export verification no longer exits the entire gate runner early, which could conceal prior failures. It checks archive integrity, manifest, private content and unsafe paths without extracting. Two Python regressions passed, including an isolated gate run with an intentional earlier failure and a successful export.

Validation: Tribal Power build + all 26 GameTests PASS; Voidloom all 5 GameTests PASS; all four Skies modules build PASS; all six pack gates PASS; four quest-format regressions PASS; two export regressions PASS. Quest totals remain 1,470 across 38 chapters, with 1,140 distinct item references and zero reported missing IDs/dead ends. Final source review covered relay transactions, FE conversion, equipment, cache persistence, processing backpressure and travel failure paths. This round did not repeat client visual checks or a complete modpack playthrough. Existing upstream optional warnings remain outside the scope of these fixes.

Current export: `dist/NinjacatSkies-0.4.0-alpha-20260906-233345.zip`. ZIP integrity passed; all five included custom jars were compared byte-for-byte with pack artifacts, and Tribal Power/Voidloom artifacts match their latest builds. No public upload was performed.

## Authorized publication

Both repositories pushed to GitHub. Tribal Power: `rewrite/shamanic-technomancy`, commit `8838a6a`. Ninjacat Skies: private `AhmiDarrow/Ninjacat-Skies`, branch `master`. CurseForge accepted alpha uploads: Tribal Power was mistakenly submitted to an unrelated project (superseded; do not reuse that destination); Ninjacat Skies project 1684777 / file 8827579. Core API verified both filenames and display names; both reported isAvailable=false immediately after upload. Standalone mod uploads require Client and Server environment version labels; the reusable uploader now supports them explicitly.


## 2026-09-07: Returning Song, skies, and shared lives

Implemented Tribal Power 2.2.0: three brush-harvestable breeding animals and ten hostile creatures, with thirteen actual Blender-authored rigs, native Java export, base/glow texture atlases, FTB entity portraits, biome spawns, loot, processing recipes, and codex entries. Added animated aurora ribbons and constellations to the Overworld and March with client quality/intensity controls; March has its own dimension sky/fog palette. Ninjacat Skies 0.5.0-alpha integrates fifteen bestiary quests (1485 total across 38 chapters).

Actual in-game QA caught a Blender dependency-graph export bug that produced oversized cuboids despite correct previews. Export now updates evaluated transforms before reading dimensions; asset verification compares every exported cuboid to the authored rig. The corrected models and both skies were inspected in the full pack. Reduced March ambient particles after visual QA. Native screenshots: Tribal Power art/creatures/in-game-dawn-stag.png, art/skies/aurora-overworld.png, art/skies/aurora-march.png. Editable source: art/creatures/tribal_bestiary.blend.

Shared lives are enabled at three per member in the FTB Clowder pool (1=3, 2=6, 3=9). Offline members count; contributor receipts prevent reconnect/rejoin refills. Deaths spend the same persistent pool; exhaustion affects online members and returning offline members. Added player clone persistence for solo fallback. Operator revives reset the pool and release exhausted members; ordinary free revives are disabled. Six one-time milestone rewards (Seat Clock, Seat Sigil, Dragon Egg Show, Ultimate Cube, completed bestiary, Reweave) each add one life directly, with persistent team receipts preventing duplicate member claims. No repeatable, crafting, shop, or random loot life supply. See docs/shared-lives.md.

Validation:
- Tribal Power build and all 30 required GameTests passed.
- Skies custom mods build and five new shared-life GameTests passed (shared pool isolation, persistence, bounded data, reward deduplication/rescue, offline membership scaling and rejoin protection).
- Blender verification passed all thirteen rigs, UV bounds, glow/base atlases, eggs, drops, recipes, and habitats.
- Full 92-jar server/client joined successfully. Actual server life sequence: 3, death -> 2, death -> 1, death -> 0 with playerGameType=3. Sigil reward -> 1 with playerGameType=0. Duplicate Sigil claim remained 1.
- Six pack gates and exported archive validation passed. 1154 quest item references, no missing IDs or detected dead ends. New rarity gate requires exactly six nonrepeatable team life rewards in the intended chapters.
- Export: dist/NinjacatSkies-0.5.0-alpha-20260907-002743.zip. Embedded Tribal Power, Skies, and Clowder Hall jars match current pack binaries byte-for-byte; enabled shared-life config is present.

Limitations: this is targeted automated and full-client QA, not a complete survival campaign or a sustained multi-human multiplayer playthrough. Existing third-party optional-model/Moonlight warnings remain. Changing FTB teams switches pools. This feature build was subsequently pushed and submitted to CurseForge; see the publication record below.

Main-menu polish: built-in image generation produced the illustrated aurora/sky-island backdrop now shipped as title_aurora.png. Enlarged title and responsive controls, centralized the Field Guide, retained native actions, and verified the actual full-pack menu at 854x480. Preview: docs/images/main-menu.png. Prompt/provenance: docs/menu-art.md. Dev-only menu capture hook does nothing in normal launches.


## 2026-09-07 publication: Returning Song

- Tribal Power source pushed to rewrite/shamanic-technomancy at 1f88e11.
- Ninjacat Skies source pushed to master at 3819508.
- The initial Tribal Power 2.2.0 upload targeted an incorrect project. Its former ID and download link have been removed. Canonical project: 1684851, https://www.curseforge.com/minecraft/mc-mods/tribalpower
- CurseForge accepted Ninjacat Skies 0.5.0-alpha, file 8827897: https://www.curseforge.com/minecraft/modpacks/ninjacat-skies/files/8827897
- Core API confirmed both filenames and project IDs. Immediately after submission both had isAvailable=false (Tribal fileStatus=3, pack fileStatus=20); public availability is pending CurseForge processing/review.

Canonical Tribal Power CurseForge project ID: **1684851** (user-confirmed and API-verified). All former project-ID references are superseded and removed from local publishing helpers.

Correction status: upload to canonical project 1684851 returned HTTP 500; a subsequent Core API file listing was empty. No successful canonical upload is claimed. Pack dependency metadata now records 1684851 with fileId=0, deliberately retaining the tested bundled JAR until a valid downloadable file exists. Existing GitHub import ZIP contains the JAR directly and has no incorrect Tribal Power manifest reference.

Publication correction completed: packaging-only Tribal Power version bump to 2.2.1 successfully uploaded to canonical project 1684851 as file 8827923. The earlier HTTP 500 did not recur with the new version. Refreshed GitHub import archive: NinjacatSkies-0.5.0-alpha-20260907-003936.zip, bundling the exact 2.2.1 binary.


## Profile branding and new logo

Verified the installed CurseForge 1.320.0.9172 import/export implementation: profile images are referenced by manifest.image, normally under profileImage/. Added that field and a bundled PNG to the exporter; root icon.png alone was insufficient. Full descriptions remain project-page metadata; HTML/Markdown descriptions continue to ship in the profile. Updated the existing local profile image/custom author with a backup under ignored build/profile-branding-backups; UI refresh may require reopening CurseForge.

Generated the new masked-cat/aurora logo, preserved the master in art/branding, checked readability at 160px, and refreshed profile/resource-pack/window assets and the GitHub README. Three exporter regression tests and final archive validation passed. Latest GitHub import ZIP: NinjacatSkies-0.5.0-alpha-20260907-005658.zip.

0.5.1-alpha publication: CurseForge accepted file 8828040 on project 1684777, containing the new logo/import branding and Tribal Power 2.2.1. Public project avatar update requires Author Console sign-in; the archive itself already includes the logo.

## 2026-09-07 CurseForge branding published
- Authenticated Author Console project 1684777: uploaded docs/public/pack-icon.png, accepted square crop, saved logo and new story/quests/lives/aurora summary. UI confirmed Changes saved successfully.
- Replaced outdated public description with current 1,485 quests / 38 chapters, Tribal Power 2.2.1 canonical project link, thirteen creatures, auroras, automation/transport, shared three-lives-per-member pool and six one-time life milestones. UI confirmed Changes saved successfully.
- Ninjacat Skies 0.5.1-alpha file 8828040 remains subject to CurseForge processing/review; GitHub release ZIP is uploaded. Tribal Power 2.2.1 file 8827923 is on canonical project 1684851.


## 0.5.2 Field Guide hotfix
Removed popup mode and raw multiline source values; aligned single-line text elements to a 1280x720 scale basis. Spoiler-free essentials only, with Back action. Full-pack 854x480 client screenshot confirms all text and button visible (docs/images/field-guide.png; QA asset cache uses previous logo). Native configuration structure and element bounds checked. Temporary Tribal Power screenshot instrumentation restored; QA client stopped. Former local Ninjacat Skies CurseForge profile no longer exists, so distribute the corrected import ZIP. Export sanitization and archive checks passed.

