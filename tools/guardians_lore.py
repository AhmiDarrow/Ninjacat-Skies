"""The thirteen Snapped Guardians as the quests and the Whisker Codex tell them. Ids match mods/guardians GuardianKind."""

# id, title, strand (None for the four extras), relic id, tier, arena, fight, relic passive / active
GUARDIANS = [
    ("beddown", "the Beddown", "soil", "rootheart", "gate",
     "The Burrow Bowl: a sunken bowl of four soil tiers stepping down to a mud pit under six dark-oak root arches, seven teal root-seams glowing across the pit floor.",
     "Every quarter of its health the Beddown slams and floods the pit with a layer of dirt, immune inside it. One of the seven seams lights: dig a channel to it, expose the core and hit it to break the burial. The first gate, and a forgiving one.",
     "Rootheart: knockback taken is cut by sixty percent and nothing can pull you. Root Down plants you for five seconds behind eight hearts of absorption."),
    ("grindmaw", "the Grindmaw", "stone", "grindcore", "gate",
     "The Millpit: a deepslate quarry with a rotating grindstone ring in the floor and four stone sieve chutes pouring gravel into the central grit pit.",
     "The Grindmaw is immune while its maw is closed. Each chute drops a grit block every fifteen seconds; carry one onto the ring and let it ride into the pit's mouth to jam the maw open for twelve seconds. The ring reverses every phase and shoves the careless into the pit.",
     "Grindcore: immune to Mining Fatigue, and your hand sieves get one extra fortune roll. Shred strips two armour from the next thing you hit."),
    ("thornmother", "the Thornmother", "sprout", "thornseed", "gate",
     "The Overgrowth Terrace: four garden terraces under a leaf canopy, eight trellis posts, and four pruning stations on the second tier.",
     "The Thornmother never strikes; she seeds thorn-hedge that spreads and burns to the touch, and heals whenever a pruning station is overgrown. Shears and axes clear it. Compost eight hedge at a station to fire a prune wave that clears the ground and stuns her — the only clean damage window.",
     "Thornseed: Thorns and no berry or cactus damage. Bloom raises a ring of hedge and gives Regeneration II to you and your Clowder inside it."),
    ("edgewalker", "the Edgewalker", "claw", "edgestep", "gate",
     "The Sky Shards: ten deepslate shards floating over the void, crumbling bridges between them, gold claw-marks on the main shard where the boss lands.",
     "A pure duel. The Edgewalker leaps shard to shard and pounces whoever stands furthest from a wall; a gold claw-mark shows where, a breath before it lands — step off it. Bridges crumble behind you and return later. Falling costs six hearts and a trip back to your pad.",
     "Edgestep: no fall damage under twelve blocks and no slipping off edges. Edgestep dashes six blocks, twice, with a stronger hit at the end."),
    ("drumheart", "the Drumheart", "spark", "drumpulse", "gate",
     "The Forge Drum: a brass drum-platform over a lava crater, eight copper piston hammers with beat pads before them, four lava channels through the floor.",
     "The Drumheart can only be hurt for a moment after every fourth beat. Stand on a beat pad at the downbeat to charge a spark that counts triple; on beat four the lava channels rise, so be on the pads, not in the channels. The tempo climbs every phase.",
     "Drumpulse: every fourth hit lands two extra hearts. Downbeat stuns and throws back everything within seven blocks."),
    ("cogwright", "the Cogwright", "clock", "cogloop", "gate",
     "The Escapement: four rotating copper rings carrying dark-oak sequence tiles around an iron hub, six gear-towers and a sixteen-block pendulum keeping time.",
     "Every phase the Cogwright winds: tiles light in sequence across the turning rings and you have twelve seconds to step them in order. Success opens its chassis for eight seconds; failure fires every gear-tower. The pendulum is the metronome; the rings reverse when it swings far.",
     "Cogloop: Haste I, and tools wear a fifth slower. Rewind resets every other relic you carry and snaps you back three seconds."),
    ("hivemind", "the Hivemind", "swarm", "hivecall", "gate",
     "The Comb: a hexagonal wax arena of rising and falling comb cells, honey pools, and six drone cells in the wall.",
     "The Hivemind is fragile but every wave its six cells pour drones. A campfire set on a drone cell seals it for thirty seconds; seal all six and the royal chamber opens for ten. Your own Productive Bees attack the drones on sight.",
     "Hivecall: bees never turn on you, and hives within sixteen blocks work a tenth faster. Call the Swarm sends four relic-bees after whatever you hit."),
    ("sealbreaker", "the Sealbreaker", "sigil", "sealmark", "gate",
     "The Ward Circle: a stone sanctum of gold circles and nine glyph pillars with amethyst spires, a nine-sided dais of gold pegs at the centre.",
     "The Sealbreaker hides behind three active wards. The dais pegs light the order once per phase — watch first. Dispel the pillars in that order with an Ars dispel or any Sigil-strand item; a wrong one re-arms all three and the ward-glass bites. Three right and it is open for twelve seconds. Later phases shuffle the runes and add a decoy.",
     "Sealmark: magic damage taken is cut by a fifth. Sealmark wards you, or a Clowder mate you look at, against one heavy hit."),
    ("unwoven", "the Unwoven", "spindle", "loomthread", "gate",
     "The Collapsing Loom: a loom sixty-six blocks wide whose floor is the warp — plank strips that unravel into thread bridges as the heddle bars drop.",
     "Five phases. Each quotes two of the other eight mechanics for thirty seconds, then a heddle bar drops and three more strips unravel. In its true form the last four strips remain and the warp threads are the only way up to the beam where it stands. Kill it there: the Reweave.",
     "Loomthread: two more Loom Tension for your Clowder and slower decay. Loomthread tethers your Clowder to your side. It is the keystone for the true Reweave and the key to the two sealed arenas."),
    ("lintgolem", "the Lint Golem", None, "lintwisp", "easy",
     "The Dock Dustbin: a corner of the Dock itself — a plank yard, a washing line of cloth sheets, baskets of wool, a red rug.",
     "The one fight with no risk. The golem throws lint balls that only blind for a moment and hides behind the washing; beat the rug and it sneezes and staggers. It teaches totem, arena and gate.",
     "Lintwisp: immune to cactus, berry and hedge damage and to being pushed. Puff blinds nearby mobs for an escape."),
    ("tangle", "the Tangle", None, "knotcharm", "easy",
     "The Knotgarden: a grass island under four rings of hedge maze with gaps and spurs, cobble paths, rope-knot rings hung over them.",
     "The spider strings the paths shut behind you with rope-knots that take three hits to cut, and bites whoever is alone in a dead end. Stay together in the maze. Optional, mid-game, a cosmetic prize.",
     "Knotcharm: no slowdown on cobweb, soul sand, honey or powder snow, and half the slip on ice. Tangle roots the first mob it hits."),
    ("firstcut", "the First Cut", None, "firstcut_shard", "insane",
     "The Severance: a great obsidian shard crossed by the glowing Cut, twenty world-shards drifting around it, teal void-tears in the air.",
     "What severed the Loom. Every twenty seconds it cuts a line across the shard and the blocks fall away for fifteen; the seam gives Speed but its beam follows the seam. Drifting shards crush, void-tears pull, and at a fifth of its health the shard splits in two along the Cut. After the Reweave only.",
     "Shard of the First Cut: cuts through ward phases. Best-in-pack, reserved for those who passed."),
    ("overweaver", "the Overweaver", None, "overweaver_shuttle", "insane",
     "The Loom Above: a purpur weave, nine strand-bridges to nine pillared platforms, twenty-seven cathedral threads to a keystone sixty-four blocks up.",
     "Your own restored Loom turned against you. The Overweaver throws shades of the nine guardians onto their strands; kill a shade and its thread pulls taut for twenty-five seconds, and only then can the loom itself be hurt. Later it throws three, then all nine.",
     "The Overweaver's Shuttle: an echo of every Strand relic in one, and it reweaves a fallen Clowder mate."),
]

STRAND_TITLES = {"soil": "Soil", "stone": "Stone", "sprout": "Sprout", "claw": "Claw", "spark": "Spark", "clock": "Clock", "swarm": "Swarm", "sigil": "Sigil", "spindle": "Spindle"}

# what unlocks each totem recipe and the summon (mirrors GuardianKind.unlockAdvancement)
def unlock(gid, strand):
    if strand: return "ninjacatskies:strand/" + strand
    return {"lintgolem": "ninjacatskies:strand/soil", "tangle": "ninjacatskies:strand/claw"}.get(gid, "ninjacatskies:reweave")
