# Clowder Hall review — 2026-09-08

Scope: `mods/clowderhall` (Island Charter, Hub Key, Clowder Hall dimension, `/clowder` commands, team checks) plus the team surfaces it leans on: Sky GUIs 21.1.10 / Skyblock Builder 21.1.31 for pads, FTB Teams 2101.1.11 for everything the pack calls a Clowder. Evidence: source, decompiled jars, the verification screenshots in `docs/images`, and the real instance's `latest.log` from the 2026-09-07 LAN session with RabidWraith (pad creation worked, panel invites did not, `/skyblock team …` commands did).

## The core problem: a "Clowder" is two unrelated teams

Clowder Hall does not own a team UI at all. `ClowderClient.open()` is one line: it calls Sky GUIs' `AllTeamsScreen.open()`. The K key is Sky GUIs' own `skyguis.key.all_teams_screen` binding remapped by the pack preset. So "the Clowder panel" is Sky GUIs' All Teams screen, and "Create Team" creates a **Skyblock Builder** team (pad, spawns, visits, join requests). That part works — `docs/images/clowders-from-charter.png` and `create-team-from-panel.png` show it.

Everything the pack *means* by Clowder lives somewhere else. `LoomTension` resolves a player's Clowder through `FtbTeamsBridge.forPlayer` → `FTBTeamsAPI.getManager().getTeamForPlayer`. `ClowderLives` (shared lives pool), Loom Tension, aura passives, the Reweave Ring, and FTB Quests progress (`default_reward_team: true`) are all keyed on the **FTB Teams** team. Nothing links the two systems. After "Create Team" the player is on a pad but still in their FTB solo "player team"; a second player invited onto the same pad keeps their own quest progress, their own Tension, their own 3-life pool, unless someone separately opens Alt+K, creates an FTB party and invites. No book, sign, tooltip or quest mentions that second step. Even with the Sky GUIs invite flow working perfectly, two people on one pad are not a Clowder.

`ClowderTeams.sameClowder` (used by `/clowder revive <mate>`) checks *either* system, so it papers over the split there, but it is the only place that does.

## Why the panel invite failed while commands worked

Sky GUIs' invite path is technically sound (verified in bytecode: `InvitablePlayersScreen` lists online players not on a team, `InvitePlayers` handler adds the invite and sends the invitee a gold clickable chat line, `AnswerInvitation` accepts via `SkyblockHooks.onAccept`). The failure is discoverability and defaults, not a crash — the log has no Sky GUIs or Clowder Hall errors for the whole five-hour session:

- The path is unlabelled: All Teams → click your team's *name* in the list ("Click me" tooltip) → Team screen → Invite → tick players → Invite → confirm. The invitee then has to open the panel again and press **Review Invites**, or click the gold chat line. Nothing in the pack says any of this; every book says "Create Team".
- The Create Team screen defaults both **Visits** and **Join requests** to *off* (visible in the screenshot). With join requests off, a second player who clicks the team sees no "Request to Join"; the only route is an invite from the owner. Clowder Hall never flips these defaults (`SkyblockManageTeamEvent.ToggleRequests/ToggleVisits` exist for it).
- The invite list is built from the client's synced copy of `SkyblockSavedData`, refreshed only when a screen opens. If the target already has a stale/sync-lagged team entry they silently disappear from the list.

`/skyblock team invite <name>` and `/skyblock accept` bypass all of that, which is why commands worked.

## Findings in Clowder Hall itself

**Hall return point is lost on death.** `ModDimensions.storeReturnPoint` writes to `player.getPersistentData()` under a top-level `clowderhall` key. NeoForge only carries the `PlayerPersisted` sub-tag across death/respawn, so dying in the Hall (it is a void dimension with no damage suppression) drops the saved pad position and `/clowder return` falls back to the Dock. Fix: nest under `Player.PERSISTED_NBT_TAG`, or store the return point in the FTB/Skyblock team data instead.

**"Create Team is Dock-only" is asserted, not enforced.** The Hall lectern book and the How to Start book both say it; `IslandCharterItem.use` opens the panel from anywhere and Sky GUIs will create a team from anywhere. Either enforce it (open the panel only `onDock`, otherwise a nudge) or drop the claim.

**`/clowder revive` is op-only but advertised to players.** `ClowderCommands` requires permission 2; the Hall book's "Begin" page lists `/clowder revive (self) or <mate>` as if any player can run it. On a LAN world only the host is op. `docs/shared-lives.md` is correct; the in-game book is not.

**`isOnDock` is a 24-block radius around shared spawn.** Fine for Skyblock Builder's 4096-block island spacing, but it also means a pad built within 24 blocks of world spawn by an op (or the Hall pad at 0,63,0 if `spawnDimension` were ever changed) is treated as Dock and spawn-sealing is refused.

**Ceremony chest hands out Charters and Hub Keys once, then never again.** `ensureHubHall` fills the chest only when built. Later joiners find an empty chest; Hub Key is otherwise only in pad starter chests. Minor, but the Hall is described as "always safe" and the place to recover.

**Reflection in `ClowderTeams` is currently correct** (`SkyblockSavedData.get(Level)`, `getTeamFromPlayer(Player)`, `Team.hasPlayer(Player)`, `FTBTeamsAPI.api().getManager().arePlayersInSameTeam(UUID,UUID)` all exist in the shipped versions) but every failure is swallowed, so a future Skyblock Builder rename would silently make mates non-mates. Since `clowderhall` already compiles against the Skyblock Builder jar (`compileOnly fileTree`), the reflection buys nothing; call the API directly behind `ModList.isLoaded`.

**Client class reference from common code.** `IslandCharterItem` references `ClowderClient` inside the `isClientSide` branch. Safe today because the JVM only resolves it when executed, but it is the pattern that produces `NoClassDefFoundError` on dedicated servers the moment someone adds a static field. Move the call behind a `DistExecutor`-style holder or a client-only event.

## Recommended fix (what "smoothing the team part" should mean)

Make Clowder Hall the bridge so a Clowder is one thing again:

1. **Mirror Skyblock Builder teams into FTB Teams automatically.** Listen on the NeoForge bus for `SkyblockCreateTeamEvent`, `SkyblockInvitationEvent.Accept`, `SkyblockJoinRequestEvent.AcceptRequest`, `SkyblockManageTeamEvent.Leave`, `SkyblockOpManageEvent.*`, plus `PlayerLoggedInEvent`, and one tick later reconcile: the player's FTB team must be a party named after the Skyblock team containing exactly its members. FTB Teams exposes `TeamManager.createPartyTeam(owner, shortName, displayName, color)` and `PartyTeam.invite/join/kick/leave`. Tag mirrored parties in `Team.getExtraData()` so hand-made parties are left alone. Loom Tension, lives, quests and the Reweave Ring then follow the pad with no second step.
2. **Set sane team defaults on creation.** On `SkyblockCreateTeamEvent`/first reconcile, turn **Join requests** on (and Visits on) so a second player can click the pad in the panel and request; the owner sees it under Requests. Keep invites too.
3. **Give players a one-click invite that does not depend on the Sky GUIs screens.** `/clowder invite <player>` and `/clowder accept` (no op requirement) that call `SkyblockHooks.onInvite`/`acceptInvite` and then reconcile FTB, plus a Charter interaction: right-click another player while holding the Charter on your pad = invite; the invitee's Charter tooltip and a chat line with a clickable accept.
4. **Tell the player the path.** Rules book / How to Start / Hall lectern: "Create Team → your pad. Invite: hold the Charter and right-click a friend, or /clowder invite <name>. They accept with /clowder accept or the panel's Review Invites." Remove "Create Team is Dock-only" unless enforced.
5. **Fix the small bugs above** (persisted return point, op-only wording, chest restock, drop reflection).

Nothing here changes item/quest IDs or world data; a mirrored party is created lazily, so existing worlds heal on next login.
