# Snapped Guardian arenas — build specs

One stage per guardian. All 13 live in a single `ninjacatskies:arena` dimension (void, fixed time, no weather, no mob spawns), each party's fight instanced in its own slot on a 4096-block grid (same offset trick as Skyblock islands), rebuilt fresh from code on every summon — the `ensureHubHall` pattern from Clowder Hall, one builder class per arena. Coordinates below are relative to the arena origin (boss spawn point, floor top = y0). Renders: `INTERNAL/guardians/arenas/<boss>_arena.png`; generator `arena_factory.py` + `voxel.py` (the voxel painter is the same geometry the Java builder should lay down, so the render *is* the block plan).

Every arena has: four **spawn pads** (teal-lit 3×3 discs, one per party member, extra members double up), the **Frayed Totem stone** (deepslate block + gold block + a rising thread particle; the totem is consumed here and the return countdown starts here on a wipe), a **return gate** (blackstone arch with a teal barrier that only opens on win/wipe), and an invisible **fence** 6 blocks outside the rim (players who fall are returned to their spawn pad with 3 hearts of damage — no void deaths in arenas; Edgewalker and the two insane arenas use 6 hearts).

Sizes are in blocks. "Boss" heights are the model heights from the Blender rigs (player = 2).

## 1 · Soil — the Beddown · THE BURROW BOWL
- **Footprint:** sunken bowl, rim ø 62, pit ø 22, four stepped tiers (pit y0 → +2 → +4 → +6 → +8 rim). Mud pit floor, rooted dirt / dirt / moss / grass tiers, dead-oak stumps on the rim, six dark-oak root arches from tier 3 over the pit, roots crawling down into the pit. Underside: dirt/rooted-dirt island keel.
- **Signature:** 7 teal glowing root-seams (sea-lantern-lit tinted glass strips) radiate across the pit floor: they are where the boss's buried core surfaces.
- **Mechanic (Bury):** every 25 % HP the boss slams and a 3-block layer of dirt floods the pit + tier 1 (raised from 6 soil slabs stacked on the rim); the boss goes immune inside it. Players dig channels to the glowing seam that lights up (one of the 7, random) and expose the core; hitting the core ends the immunity and drops the layer back into the rim slabs. Falling dirt cannot bury a player (pushes them up).
- **Hazards:** none beyond the burial; first real gate, forgiving. Boss 11 tall.
- **Spawn pads** on tier 2 at (19,4) (-16,9) (-6,-17) (14,-12); totem (0,-21) tier 2; gate (0,32) on the rim.

## 2 · Stone — the Grindmaw · THE MILLPIT
- **Footprint:** quarry ø 64: deepslate floor, 5-high stone wall with cobble rim, grit pit ø 18 of gravel in the centre. **Grindstone ring** — a stone annulus r 14–21 with 16 brass tooth ridges — rotates one block per 2 s (implemented as a block-swap animation; standing on it moves you). Four stone sieve chutes on the cardinal points (7 tall, brass cap) with iron slides pouring gravel into the pit; 8 iron lantern posts.
- **Signature:** the pit is the boss's own sieve grit; brass channels glow faint gold.
- **Mechanic (Route the grit):** the boss is immune while its maw is closed. Each chute drops a **grit block** every 15 s; carrying one (it's a placeable block) onto the grindstone ring and letting the ring carry it into the pit's mouth jams the maw open for 12 s. The ring reverses direction each phase. Boss 13 tall.
- **Hazards:** the ring pushes you into the pit (2 hearts + slowness), chute slides are 1 heart on contact.
- **Pads** (24,5) (-22,8) (-8,-23) (16,-18); totem (-24,-20); gate (0,34) on the wall, +7.

## 3 · Sprout — the Thornmother · THE OVERGROWTH TERRACE
- **Footprint:** four garden terraces ø 72/56/40/24 at y0/+3/+6/+9 with cobble retaining walls; grass/moss tops. Eight dark-oak trellis posts (15 tall) around the rim with a leaf canopy at +15 (open on the south side). Four **pruning stations** (planks platform, composter, teal lantern) on tier 2 at 45° points, each with a kept-clear grass circle r 4.
- **Mechanic (Prune):** the boss never attacks directly. Every 6 s it seeds a **thorn-hedge** block (custom block, 1 heart/s contact, spreads to an adjacent block every 4 s). If any pruning station's circle is overgrown for 10 s the boss heals 10 %. Shears/axes break hedge in one hit; composting 8 hedge at a station fires a "prune wave" that clears a 6-block radius and stuns the boss 4 s (the only damage window without thorns). Boss 12 tall on the top terrace.
- **Pads** (30,4) (-28,8) (-10,-29) (24,-18) tier 0; totem (0,-33); gate (0,38).

## 4 · Claw — the Edgewalker · THE SKY SHARDS
- **Footprint:** ten deepslate shards floating over the void, main shard ø 38 at y0, the rest ø 10–16 at +3 … +18, spread across 80×80. Blackstone rock keels under each; tuff rubble; 10 crumbling **bridges** of 3-wide deepslate (three already broken). No rails anywhere. Gold "claw mark" strips on the main shard mark where the boss lands.
- **Mechanic (Duel):** pure reflex fight; the boss leaps shard-to-shard (it never walks a bridge) and pounces the player who is furthest from a wall. Bridges crumble 2 s after a player crosses (block-by-block, restored after 20 s). The "tell" is a gold claw-mark that appears 0.7 s before each pounce; standing off it is the dodge. Boss 9 tall (long), fastest of the nine.
- **Hazards:** falling = fence return at 6 hearts.
- **Pads** on the main shard (9,2) (-8,6) (-2,-9) (6,-7); totem on shard 7 (-31,-6)+3; gate on the top shard (-9,37)+18.

## 5 · Spark — the Drumheart · THE FORGE DRUM
- **Footprint:** basalt crater ø 82 with a **lava pool** at −3; a brass drum-platform ø 46 at y0 on 12 iron struts, copper rim; an iron catwalk ring r 24–28 with copper rails; six basalt chimneys on the crater lip; ten copper bellows pipes arching from the wall to the drum.
- **Signature:** 8 copper **piston hammers** (5 tall) on r 17 with an amber **beat pad** in front of each; four **lava channels** cut through the platform at the 45° diagonals.
- **Mechanic (On the beat):** the boss is invulnerable except for 0.6 s after every 4th beat (a 120 BPM drum loop, hammers slam on beats 1–3, all eight slam on 4). Standing on a beat pad at the downbeat charges a "spark"; hitting the boss with a spark counts ×3. On beat 4 the lava channels rise to floor level for 1 s (3 hearts, fire). Every phase the tempo goes up 10 BPM. Boss 12 tall.
- **Pads** on the catwalk (25,4) (-24,6) (-6,-25) (20,-16); totem (0,-26); gate (0,41)+2 on the crater lip.

## 6 · Clock — the Cogwright · THE ESCAPEMENT
- **Footprint:** ø 70 blackstone base; four **rotating rings** (copper/brass annuli r 4–10, 11–17, 18–24, 25–31, iron lips) carrying 8/12/16/20 dark-oak **sequence tiles**; iron centre hub ø 8 for the boss; six iron gear-towers (12 tall, brass caps and 3-block brass gears); a 16-tall iron pendulum on the north edge; 12 copper lamp posts.
- **Mechanic (Pattern):** every phase the boss "winds": tiles light in a sequence (3, then 4, 5 …) across the rings; players must step on them in that order within 12 s while the rings rotate (inner ring 1 block / 3 s, outer faster). Success opens the boss's chassis for 8 s; failure fires all gear-towers (arc shock, 3 hearts, ring-wide). The pendulum's swing is the metronome; rings reverse when it hits the far side. Boss 11 tall (spider).
- **Pads** (27,4) (-26,7) (-8,-27) (20,-18) on the outer ring's lip; totem (-30,0); gate (0,36).

## 7 · Swarm — the Hivemind · THE COMB
- **Footprint:** hexagonal wax wall ø 72 (4 high), floor of ~200 hexagonal **cells** (r 2.6, 0–3 tall) in wax/comb with darkwax rims; ~18 **honey-pool cells** (honey block, slow + sticky); six **drone cells** in the wall (amber-lit comb hexes, 6 tall); nine oak roof struts with honey drips.
- **Mechanic (Queen and drones):** the boss (the tower, 12 tall) is fragile but every drone cell opens each wave and pours 4 drones; drones re-form at any honey cell. Cells rise/fall by one block every 5 s (block swap), reshaping cover. A **smoker** (campfire) placed on a drone cell seals it for 30 s; sealing all six exposes the royal chamber (the boss's belly mouth) for 10 s. Your own bees (Productive Bees) attack drones on sight.
- **Pads** (24,4) (-22,8) (-8,-23) (18,-16); totem (0,-27); gate (0,36).

## 8 · Sigil — the Sealbreaker · THE WARD CIRCLE
- **Footprint:** stone sanctum ø 66, deepslate wall 12 high with blackstone cap and 18 purpur windows; three gold-inlaid circles (r 8/16/24) and nine gold spokes; nine stone **glyph pillars** (10 tall, gold caps, amethyst spire, soul-lantern) on r 24 with a 3-block glyph band (teal = active ward, violet = dormant); ward-glass panels between pillars; a 9-sided deepslate dais with gold pegs in the centre.
- **Mechanic (Read the room):** the boss hides behind 3 active wards (teal). Each ward pillar shows a rune; the **order** is written on the dais pegs (which light in sequence once per phase — watch, don't fight). Dispelling in the right order (Ars dispel, or hitting the pillar's glyph with any Sigil-strand item) drops a ward; wrong order re-arms all three and the ward-glass fires a 3-heart arc. Three correct dispels = boss vulnerable 12 s. Phase 2 shuffles runes; phase 3 adds a decoy ward. Boss 13 tall.
- **Pads** (20,4) (-18,8) (-6,-20) (15,-14); totem (0,-20); gate (0,35).

## 9 · Spindle — the Unwoven · THE COLLAPSING LOOM
- **Footprint:** a giant loom 66 wide × 48 deep: two dark-oak uprights (32 tall), top/bottom beams, a spruce loom-bed; the **floor is the warp** — 23 plank strips (2 wide, 62 long) with 4 already unravelled into sagging thread; 31 vertical warp threads (teal/gold) from the top beam; two iron heddle bars at +18/+23; iron shuttle rails on both sides; six purpur bobbin pillars on the near edge.
- **Mechanic (Finale, five phases):** each phase quotes one of the eight mechanics for 30 s (bury → grit → prune → pounce → beat → pattern → drones → wards, two per phase, drawn at random) and then a **heddle bar drops**, unravelling 3 more strips (they become 1-block thread bridges). Phase 5 (true form): the last four strips only; the boss stands on the top beam and the warp threads become the only way up — climbable (ladder logic). Kill it on the beam → the Reweave. Boss 13 tall, 16 in true form.
- **Pads** (14,6) (-14,8) (-6,-14) (12,-10) on strips; totem (0,-20); gate (0,24).

## Easy · Lint Golem · THE DOCK DUSTBIN
- **Footprint:** a 30×30 dock-planks yard: two oak posts with a rope washing line and 7 cloth sheets, four oak baskets with wool, a red rug, lint tufts everywhere. Fits *on the Dock* itself (it is the one arena that is not instanced: a corner of the Dock is reserved for it).
- **Mechanic:** the golem (6 tall) throws lint balls (0 damage, Blindness 2 s) and hides behind the washing; beating the rug (right-click) makes it sneeze and stagger. Teaches totem → arena → gate with zero risk. Two pads (9,-3) (-9,3); totem (0,10); gate (0,15).

## Easy · the Tangle · THE KNOTGARDEN
- **Footprint:** grass island ø 62 with four concentric hedge rings (r 10/16/22/28, 3 tall, three gaps each) plus radial spurs — a real maze; cobble paths crossing; 12 rope-knot rings hung over paths.
- **Mechanic:** the spider (7 tall, 5 legs) strings paths shut behind you (a rope-knot block, 3 hits to cut) and prefers to bite whoever is alone in a dead end. Optional mid-game; cosmetic reward. Three pads (26,5) (-24,9) (-6,-26); totem (0,-30); gate (0,33).

## Insane · the First Cut · THE SEVERANCE
- **Footprint:** 160×160. Main obsidian shard ø 84 with a blackstone keel; the **Cut** — a jagged 2-wide gold seam (glowing) crossing the whole floor and continuing as six golden rifts into the sky; 20 drifting world-shards (end stone / deepslate / grass / obsidian, ø 10–26, at −22 … +48, some with purpur ruins) orbiting slowly (block-swap drift 1 block / 4 s); 14 teal void tears floating in the air.
- **Mechanic:** the boss (32 tall) severs: every 20 s it cuts a line across the main shard — blocks along the line fall into the void for 15 s (a gap you must jump or bridge with a drifting shard). Standing on the seam gives Speed III but the boss's beam follows the seam. Phases: shards begin colliding with the main shard (crush zones, 8 hearts), the void tears pull (levitation lines), and at 20 % the main shard splits in half along the Cut — you fight on two halves drifting apart. Reachable only after all nine Reweaves through the sealed door in the arena dimension.
- **Pads** (30,6) (-28,10) (-10,-31) (24,-22); totem (0,-36); gate (0,44); fence at 6 hearts.

## Insane · the Overweaver · THE LOOM ABOVE
- **Footprint:** 170×170. Central purpur weave ø 72 with a gold ring; nine plank **strand-bridges** (5 wide) to nine ø 22 strand-platforms, each with a 30-tall dark-oak pillar (purpur cap, amethyst point) and its guardian's colour line on the bridge; 27 cathedral threads (gold centre, teal sides) from the pillar tops to a gold keystone 64 blocks up.
- **Mechanic:** the boss (40 tall) *is* the loom — it stands on the weave and throws **shades** of the nine guardians one at a time onto their strand-platform (a shade is a 40 % HP, single-mechanic copy). Killing a shade lights its bridge line and pulls one thread taut — the boss takes damage only while at least one thread is taut, and a taut thread slackens after 25 s, so the party has to keep killing shades while somebody hits the boss. At 50 % it throws three shades at once; at 20 % all nine, and the keystone descends (standing under it is the only damage spot). Win → the Loom is yours.
- **Pads** (20,6) (-18,10) (-8,-21) (16,-15); totem (0,-27); gate (0,40).

## Builder notes
- Each arena is a static block layout (from `arena_factory.py` — the voxel calls translate 1:1 to `level.setBlock`) plus a small list of **dynamic elements** (rotating ring, rising layer, crumbling bridge, cell rise/fall, lava channel, heddle drop, seam gap, shard drift). Dynamic elements are block-swap animations driven from the boss entity's phase controller; nothing uses entities except the shades and the Lint Golem's lint balls.
- Custom blocks needed: `thorn_hedge`, `grit_block`, `rope_knot`, `ward_glass`, `honey_cell` (variants of honey block with slow), `seam_glass` (gold-lit), `spawn_pad`, `return_gate` (barrier variant). All decorative others are vanilla/Create/Ars blocks already in the pack.
- Fence, pads, totem and gate are shared code; a `ArenaTemplate` with `spawnPads`, `totem`, `gate`, `radius`, `fallDamage` and `build(level, origin)` per arena.
- Party scaling: boss HP ×(0.6 + 0.4·members); drone/shade counts +1 per member beyond 2.
- On wipe: everyone is returned to their stored return point (PlayerPersisted, as Clowder Hall does it), the totem is consumed, the arena slot is wiped on the next summon.
