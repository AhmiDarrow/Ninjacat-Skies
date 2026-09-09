# Snapped Guardians — boss art pipeline (Blender 4.2, headless)

Everything here is generated procedurally; the `.py` files are the source of truth for every model and animation.

- `pipeline/boss_lib2.py` — modelling helpers: `fuse` (overlapping primitives → voxel remesh → displace → decimate/flat shade = one solid body), `limb()` joint-to-joint chains, `surface()` procedural material (noise colour, moss, radial glowing crack network, bump, thread stripes, metal/sheen), `glow/plain/glass`, `studio()` lighting + camera + AgX + fog-glow compositor.
- `pipeline/rig_lib.py` — `humanoid_armature`, `custom_armature`, `skin()` (auto weights with a manual nearest-bone fallback — bone heat silently fails on big meshes), `bone_parent_nearest`, `key(..., wloc=)` (world-space location keys; pose-bone location is bone-local).
- `pipeline/rig_pro.py` — the animation system: `Anim` with Catmull-Rom pose timelines, sinusoidal secondary layers, child-lag follow-through, decaying impact shake, settle overshoot, seamless loops at 24 fps (idle 48f, walk 32f, attack 40f, death 48f). `humanoid/quad/spider/tower` kinds.
- `pipeline/boss_factory.py` — `BOSSES` dict: 13 unique builders. Set `NCS_ART_ROOT` to the work folder (defaults to `$HOME`; renders go to `<root>/renders`). Run: `blender --background --python boss_factory.py -- <boss> hero` or `-- <boss> idle,walk,attack,death`.
- `pipeline/reel.sh <boss>` — gifs + reel + key stills from the frame folders.
- `heroes/` — approved hero renders. `reels/` — idle→walk→attack→death reels (h264).

Boss ids: beddown, grindmaw, thornmother, edgewalker, drumheart, cogwright, hivemind, sealbreaker, unwoven, lintgolem, tangle, firstcut, overweaver.

Next step in the tech plan is GeckoLib export: the armatures and keyed actions in the .blend produced by `boss_factory.py` are the input for the geo/animation JSON.
