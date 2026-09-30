# Ninjacat Skies 0.10.4 — Mended and Measured, Earned in Class and Drums Side by Side

Pack CurseForge client file **TBD**, server additional **TBD**. Ninjacat Skies Core 0.5.20 is CurseForge file **9018084**
(unchanged); Tribal Power 5.3.13 is **9022118**; Chocobos Reborn 1.1.4 is **9022598**; Shamanic Mounts 0.1.4 is
**9018208** (unchanged).

105 mods (101 on the server): Ninjacat Skies Core 0.5.20, Tribal Power 5.3.13, Chocobos Reborn 1.1.4, Shamanic Mounts
0.1.4. Existing saves load as they are; no quest ids change. Loom's End rebuilds once (hub revision 3).

See `docs/cf-changelog-0.10.4.md` for the player-facing notes.

- **Tribal Power 5.3.13** (5.3.12 → 5.3.13, sha1 `362928f20cf5117a22dfe723a6ee3831661e832c`): item-restore-on-reload
  exploits on lattice machines, relays, horns and benches; Song Bench shift-click overflow dropped at your feet; silk-touch
  ore XP repeat and auto-smelt output; one marked wall no longer fills every building request. Owner checks on gate
  keystones, the Wireless Relay and bonded-animal brushing (pre-update relays stay open). Comparator output for Stone Font,
  Resonance Mesh and Silent Drum; Wind Snare / Ward Drum Pulse waste; Ley Collector rate in Codex and Ley Lens; Pulse
  Gauge overflow; directional logic plates. Kinship Totem counts for the voice gate; voice-waiting machines stop pushing
  items. Grove Tender fells only grown trees (whole tall/wide trees, never log builds); Spiritgear Hoe replant only on a
  real seed. Weaver's Wand respects protected land; Totem Wrench piston/wall-attachment checks. Wave Drum / Wind Harp
  crowding over full range (8/12). Drum practice lockout and cross-dimension finish; familiar revive stat cleanup; wild
  remnants vs familiars; Mossback saddlebag on dimension change; guardian altar unload/sleep states. Boss themes no longer
  dropped for starting silent. Codex, recipe viewer, familiar panel, Elder dialogue and Songkeeper screen layout fixes;
  ~60 Codex name spellings, doubled bullets and relic names, corrected facts. March Stool log spam removed. Server tick
  savings: single-pass Pulse lookup, cached conductor lines, Echo Station totem scan per beat, Spirit Cistern update
  throttle, ley ropes sent on change, no per-tick item data copies.
- **Chocobos Reborn 1.1.4** (1.1.2 → 1.1.4, sha1 `f69f9117c0b92b95947e286a4bc623a2592dc17e`): 1.1.4 counts colour-breeding wins in the stage's own
  class (Green/Blue 5 Class C wins each, certain at 16 combined; Black 8 Class B from Great parents, 24; Gold 10 Class A
  from a Wonderful Yellow and Black, 32; save format 5 shares old wins out by class). 1.1.3: Class C ranked heats seat
  Ahmi and Risika as the named rivals (Yellows with Flame and Purple look plumage, player skins on the course, named by
  Rook, the board and the almanac); Teiyo and Jolo from Class B up. Per-class promotion bars C36 / B54 / A72 (Class S
  shows the A bar); older birds on the uniform-36 ladder rescale on world load. Course picker, gossip, lounge signs,
  Race Hall board and almanac updated.
- **Pack:** Loom's End hub revision 3 (`tools/hub_loomsend.py`, regenerated `clowder_town.json`): the Drum Circle's two
  Songkeeper Drums now stand side by side so players at them can duel; existing worlds rebuild the hub once. Store page
  Tribal Power pin bumped to 5.3.13 (`docs/public/store-description.md`, re-rendered HTML).
