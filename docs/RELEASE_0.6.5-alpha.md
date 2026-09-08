# Ninjacat Skies 0.6.5-alpha — Clowder teams that actually team up

The Clowder team flow is smoothed out. Before, "Create Team" made a Skyblock Builder pad team, but Loom Tension, the shared-life pool and FTB Quests are all keyed on the FTB Teams party — and nothing linked the two, so two players on one pad still had separate quests, Tension and lives. Inviting through the panel also went unlabelled and defaulted join requests off.

- **Pad teams now mirror into an FTB party automatically.** When a player creates, invites into, or joins a Clowder (or an operator adds them), Clowder Hall reconciles the matching FTB party so quests, Loom Tension and shared lives follow the pad with no second step. The mirror only ever creates a party or adds members on a deliberate team action; it removes a member only when they leave the Skyblock team.
- **New pad teams default to join requests and visits ON**, so a second player can click the pad in the panel and request to join.
- **One-click invites that do not depend on the panel:** `/clowder invite <player>` and `/clowder accept` (no operator needed), and holding the Island Charter and right-clicking a friend invites them. The invitee gets a clickable chat line.
- **Books and controls rewritten** to describe the invite path; the unenforced "Create Team is Dock-only" claim is gone, and the Hall book no longer advertises operator-only `/clowder revive` as a player command.
- **Fixes:** the Clowder Hall return point is stored under PlayerPersisted so dying in the Hall no longer drops your saved pad exit; the Hall ceremony chest restocks when found empty; `ClowderTeams` calls the Skyblock/FTB APIs directly instead of reflection.

Save compatibility: no item, block or quest IDs change. Existing worlds are not restructured on load — a login only joins an already-formed mirror party, never creates one, so established teams and their quest progress are left exactly as they were; the mirror forms when someone takes a team action after updating. No world reset is required.

Companion mods 0.3.4. Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21. Import the attached ZIP in CurseForge, or restart an already patched profile.
