"""Driftwrecks words: Keepsakes, the tribes' names for their places, and the Wreck Atlas lore pages.

One source of truth for tools/generate_driftwrecks_data.py (lang, Codex entries). Voice: the story bible's
(docs/STORY.md) — concrete verbs, no chosen one, no prophecy, end on a verb where it fits. Down a Strand column the six
pages read as one short story (a place, a craft, a loss); across a row, the same kind of place in nine cultures.
"""

STRANDS = ["soil", "stone", "sprout", "claw", "spark", "clock", "swarm", "sigil", "spindle"]
TRIBES = {"soil": "Pad-keepers", "stone": "Grit-singers", "sprout": "Rootbinders", "claw": "Edge-walkers", "spark": "Drumhearts",
          "clock": "Pattern-weavers", "swarm": "Colony-keepers", "sigil": "Seal-carvers", "spindle": "Loom-stitchers"}
CORES = ["shrine", "watchtower", "library", "forge", "garden", "vault"]
CORE_TITLES = {"shrine": "Shrine", "watchtower": "Watchtower", "library": "Library", "forge": "Forge", "garden": "Garden", "vault": "Vault"}

# (keepsake name, inscription, place name, lore page)
C = {
    "soil": {
        "shrine": ("Cracked Root-Bell", "Ring it softly. The roots remember the tune.", "the Hearthbank",
                   "The Pad-keepers rang a root-bell at dusk so the soil would hold its warmth through the night. Every family carried a handful of hearth-ash to the Hearthbank. When the Cut came the bell was still warm, and someone kept ringing it."),
        "watchtower": ("Soil-Reading Rod", "Push it in. It tells you what the ground wants.", "the Long Furrow Post",
                       "From the Long Furrow Post a Pad-keeper could see every field at once and tell which one was thirsty by its colour. They signalled with lanterns: green for rain, red for frost. The last lantern hung red for a week before the post let go."),
        "library": ("Pressed Seed Ledger", "Every seed has a name. Most of them are lullabies.", "the Seedlist House",
                    "The Seedlist House kept one page for every seed the Pad-keepers ever planted, with who planted it and what it gave back. Children learned to read from the harvest columns. Half the pages are still blank. They were saving room."),
        "forge": ("Worn Mattock Head", "Sharpened so often it is mostly memory.", "the Mattock Shed",
                  "The Pad-keepers forged nothing sharper than a mattock and needed nothing sharper. They re-edged the same heads for generations, so a tool outlived three owners. The shed smelled of wet iron and bread. Bank the fire before you leave."),
        "garden": ("Clay Seed Jar", "Sealed with wax and a thumbprint. Whose, nobody knows.", "the Warm Bed",
                   "The Warm Bed was a garden built over the Hearthbank's ash pit, so it never froze. Pad-keepers grew their first shoots there and carried them out to the cold fields in clay jars. It fed everyone. It could not feed a pad that was drifting."),
        "vault": ("Sealed Seed Tin", "Open it only when the ground is ready.", "the Seed-Cellar",
                  "Under the Warm Bed the Pad-keepers dug a cellar and filled it with one of every seed, sealed in tin, against a bad year. The bad year was worse than they planned for. The tins are still full. Plant them."),
    },
    "stone": {
        "shrine": ("Echo Shard Pendant", "Tap it and it sings back your name.", "the Hall of Echoes",
                   "Grit-singers named every shard by the note it gave when struck, and the Hall of Echoes was where the names were sung aloud. A choir of forty could make the whole cliff hum. After the Cut the hall kept humming with nobody in it."),
        "watchtower": ("Tuning Fork of Slate", "Strike it on stone. Listen for what is hollow.", "the Listening Spire",
                       "The Listening Spire leaned into the wind so its stones would ring when a rockfall began far off. Grit-singers took turns sleeping at the top with their ear to the wall. The last watcher heard the Cut coming. There was no note for it."),
        "library": ("Scale of Grit Notes", "Every stone has a pitch. Write it down before you break it.", "the Echo Register",
                    "The Echo Register was a wall of carved staves, one for every quarry, marking the pitch of its best stone. Masons came from nine valleys to read it. Where a stave is chipped, the quarry is gone."),
        "forge": ("Singing Chisel", "It rings true only when it cuts true.", "the Grit Mill",
                  "The Grit Mill ground stone to sand by song: the millstones turned faster when the singers held a high note. A good miller could grade grit by ear alone. The mill still turns when the wind is right. Nobody grades the grit now."),
        "garden": ("Lichen Stone", "It grew one ring a year. Count them.", "the Moss Terraces",
                   "Grit-singers grew lichen on their terraces the way others grew flowers, and read the seasons in its rings. A lichen stone was a gift for a newborn. Some of these rings are older than the Cut. Keep counting."),
        "vault": ("Resonance Key", "Hum the right note and the lock gives way.", "the Hollow Vault",
                  "The Hollow Vault had no keyhole: its door opened to a single sustained note that only its keepers knew. When the keepers scattered, the note scattered with them. This key hums the first half of it. Find the rest."),
    },
    "sprout": {
        "shrine": ("Living Knot Charm", "Still growing. Water it.", "the Anchor Grove",
                   "Rootbinders tied a living knot into a sapling for every child and planted it at the Anchor Grove. The trees grew roots deep enough to hold the island still in a gale. Where the Cut ran, the roots held on to both halves. They are holding still."),
        "watchtower": ("Vine-Wound Spyglass", "The vines grew around it while someone was looking.", "the Canopy Lookout",
                       "The Canopy Lookout was never built: the Rootbinders grew it, coaxing a trunk into a stair over forty summers. From the top you could watch weather roll across nine islands. The trunk kept growing after the watchers left. It is taller now."),
        "library": ("Pressed-Flower Frame", "Nine flowers, one from each island. One is missing.", "the Leaf Archive",
                    "In the Leaf Archive, Rootbinders pressed one leaf from every plant they tended, with the date it first bloomed. Reading the pages in order is like watching a spring arrive. The last page holds a leaf nobody could name. It arrived with the Cut."),
        "forge": ("Grafting Knife", "Cut clean, bind tight, wait.", "the Grafting Shed",
                  "Rootbinders did not forge metal; they grafted. In the Grafting Shed a patient hand could join an apple to a thorn and make it fruit. Their best work was a bridge of two trees grown together across a gap. Half of it fell when the island did."),
        "garden": ("Sprouting Acorn", "It will not stop trying.", "the Nursery Terraces",
                   "The Nursery Terraces fed three islands from one slope, watered by roots that pulled mist out of the clouds. Rootbinders sang to the seedlings, mostly to keep themselves awake. Something in the soil still sprouts at dawn. Feed it."),
        "vault": ("Heartwood Box", "Grown shut. It opens for the patient.", "the Root Cellar",
                  "The Rootbinders' vault was a hollow grown inside one ancient trunk, sealed by bark as it healed. What they kept there was not treasure but cuttings of every tree, alive and asleep. The trunk is still healing around them. Wake one."),
    },
    "claw": {
        "shrine": ("Claw-Marked Stone", "Four scratches: one for every edge they came back from.", "the Last Post Shrine",
                   "Edge-walkers left a claw mark on the Last Post Shrine each time they returned from past the fence. Old walkers had stones covered in marks. Young ones had one, and were loud about it. The newest mark on this stone is unfinished."),
        "watchtower": ("Rim-Walker's Lantern", "It never went out. It was only put down.", "the Brink Watch",
                       "The Brink Watch hung over nothing, braced on three iron claws driven into the cliff. Edge-walkers stood there to learn the wind before they stepped off. You were not an Edge-walker until you had eaten a meal at the Brink with your feet dangling. Sit."),
        "library": ("Knotted Route Cord", "Each knot a foothold. Read it with your fingers.", "the Route Loft",
                    "Edge-walkers wrote their routes as knotted cords, one knot for every safe foothold, so they could read them in the dark. The Route Loft held thousands. The longest cord led to an island nobody else believed in. The cord ends past the edge."),
        "forge": ("Spiked Boot-Iron", "For ice, for rock, for the parts of the map that were never drawn.", "the Claw Smithy",
                  "The Claw Smithy made crampons, hooks and pitons, and tested every one by hanging the smith from it over the void. A smith who trusted their work was a smith who lived. Their hooks still hold. The walls around them do not."),
        "garden": ("Cliff-Rose Cutting", "It grows only where nothing should.", "the Ledge Beds",
                   "Edge-walkers kept gardens on ledges no one else could reach: cliff-roses, rope-moss, a stubborn kind of bean. A ledge bed was a reward for a new route. Some of these beds are still blooming on a piece of cliff that is no longer attached to anything. Climb."),
        "vault": ("Gold Claw Clasp", "Worn by whoever went farthest. Pass it on.", "the Far Cache",
                  "At the end of their longest route the Edge-walkers built the Far Cache: rope, food, a bed, a note for the next walker. Whoever reached it wore the gold clasp home. The clasp never made it home the last time. It is going home now."),
    },
    "spark": {
        "shrine": ("Ember Drumstick", "Warm to the touch, whatever the weather.", "the Pulse Circle",
                   "Drumhearts believed the sky had a heartbeat and that someone had to keep time with it. At the Pulse Circle a drummer played every hour of every day for three hundred years. The beat stopped during the Cut. Then, faintly, it started again."),
        "watchtower": ("Copper Signal Horn", "One long note: all is well. Three short: come home.", "the Thunder Mast",
                       "The Thunder Mast caught lightning and stored it in copper coils for the drums below. Drumhearts climbed it in storms to listen to the coils hum. When the Cut opened, the mast caught something that was not lightning. The horn blew three short notes."),
        "library": ("Rhythm Score Tablet", "Beats carved in copper. Play it and you will not be alone.", "the Measure House",
                    "The Measure House kept every rhythm the Drumhearts ever played, scratched into copper plates. A child could learn the whole history of the tribe by drumming it. The last plate is only four beats long. Someone was in a hurry."),
        "forge": ("Bellows Nozzle", "It still breathes when you hold it near a fire.", "the Spark Forge",
                  "In the Spark Forge the bellows worked in time with a drum, so the fire rose and fell like breath. Drumhearts said iron forged off the beat would crack. Their tools are still whole. Keep time."),
        "garden": ("Pepper-Flower Pod", "Hot enough to wake the dead. Plant with care.", "the Ember Gardens",
                   "The Ember Gardens grew around the forge's warm run-off: fire-peppers, sunroot, a flower that bloomed only at a hard beat. Drumhearts ate spicy and played loud. The run-off is cold now. The peppers are still hot."),
        "vault": ("Sealed Spark Coil", "Something is still humming inside.", "the Charge Vault",
                  "The Charge Vault stored the Thunder Mast's catch in sealed coils for the long, still winters. One coil could keep a hall warm for a season. This one was never opened. Listen before you open it."),
    },
    "clock": {
        "shrine": ("Escapement Wheel", "Tick. Tick. It keeps going without being told.", "the Round Chapel",
                   "Pattern-weavers sang in rounds: one voice began, the next followed, until a hall of voices turned like gears. The Round Chapel was built so the echo arrived exactly one beat late. The echo is still arriving. Nobody started it."),
        "watchtower": ("Brass Sun-Dial", "It tells the time in a world that has stopped keeping it.", "the Hour Tower",
                       "The Hour Tower rang every hour for every island, so nine tribes could keep one time. Pattern-weavers adjusted it with a key the size of an arm. After the Cut the islands drifted apart and the hours stopped matching. The tower rings anyway."),
        "library": ("Loop-Stitched Manual", "Page one refers to page nine. Page nine refers to page one.", "the Pattern Stacks",
                    "The Pattern Stacks held every loop the Pattern-weavers ever sang into a machine. Their machines ran on patterns the way others ran on fire. The last loop in the stacks was never finished. It keeps trying to repeat."),
        "forge": ("Cog of Nine Teeth", "Nine teeth, one missing. It still turns.", "the Gear Loft",
                  "In the Gear Loft Pattern-weavers cut cogs by hand and matched them by ear. A good pair of gears hummed a single note. This cog belonged to a machine that fed a whole island. One cog, then the same cog again."),
        "garden": ("Clockwork Seed", "Wind it once a year. It will know when to open.", "the Hedge Maze",
                   "Pattern-weavers grew a garden that repeated: a hedge maze whose paths were a round sung in green. Walk it right and you came out singing. Walk it wrong and you came out where you began. Try again."),
        "vault": ("Timed Lock-Box", "It opens at an hour that no longer exists.", "the Strongroom Clock",
                  "The Pattern-weavers' vault opened once a year, at a minute only the Hour Tower could count. The minute came and went during the Cut with no one at the door. The box is still waiting for its hour. Wind it."),
    },
    "swarm": {
        "shrine": ("Queen's Wax Idol", "It smells of summer, still.", "the Humming Altar",
                   "Colony-keepers built their altar inside a hive and prayed by humming in the same key as the bees. The whole island buzzed on feast days. When the Cut came, the bees went quiet first. Then they hummed louder than they ever had."),
        "watchtower": ("Swarm-Reading Glass", "Watch which way they fly. They know before you do.", "the Drone Tower",
                       "From the Drone Tower the Colony-keepers read the swarms like weather: which way they flew, how high, how loud. A low swarm meant rain. On the day of the Cut every swarm on the island flew straight up. Look up."),
        "library": ("Wax-Sealed Ledger", "Honey accounts, forty years of them. Every jar is written down.", "the Comb Archive",
                    "The Comb Archive kept the tribe's accounts on wax tablets, stacked like honeycomb: every hive, every harvest, every jar given away. Colony-keepers gave away more than they kept. The last tablet is a list of names. They are all marked as fed."),
        "forge": ("Smoker Can", "A little smoke calms the hive. A little more calms the keeper.", "the Wax Works",
                  "At the Wax Works, Colony-keepers cast candles, sealed jars and poured the wax that held their houses together. Nothing they built had a nail in it. Warm hands kept it all standing. It stood for longer than anyone expected."),
        "garden": ("Honey-Flower Bulb", "Bees will find it before you have finished planting.", "the Bloom Fields",
                   "The Bloom Fields were planted for bees, not people: row on row of flowers timed so something was always open. Colony-keepers ate what the bees left. The fields still bloom on schedule. Keep something alive that keeps something else alive."),
        "vault": ("Royal Jelly Jar", "Sealed for a queen that never hatched.", "the Brood Vault",
                  "Deep in the comb the Colony-keepers kept a vault for the next queen: royal jelly, the warmest wax, a cell nobody else could enter. She had not hatched when the Cut came. The cell is still warm. Wait."),
    },
    "sigil": {
        "shrine": ("Ward-Key Sigil", "Turn it once for a promise. Twice to keep it.", "the Oath Stone",
                   "Seal-carvers made promises in stone: a sigil carved at the Oath Stone bound whoever carved it. The stone was covered edge to edge with oaths kept and broken. One oath at the centre is still glowing. It is still being kept."),
        "watchtower": ("Warding Lantern", "What it lights cannot cross the line.", "the Ward Beacon",
                       "The Ward Beacon lit a ring of wards around the Seal-carvers' island every night. Nothing walked through the light that was not invited. The night of the Cut the ring held. It was the island underneath that broke. Carve carefully."),
        "library": ("Rubbing of the First Seal", "Charcoal on paper. The seal itself is lost.", "the Rune Library",
                    "The Rune Library held a rubbing of every seal ever carved, so a broken seal could be carved again. Seal-carvers read by candlelight, tracing runes with a finger. This is a rubbing of their first seal. Nobody alive can carve it."),
        "forge": ("Engraving Burin", "The point is worn to the exact width of a promise.", "the Carving Bench",
                  "At the Carving Bench a Seal-carver could press spirit into matter and make it stay. Their tools wore down to fit the hand of one carver and no other. When a carver died, their burin was buried with their last seal. This one was not buried."),
        "garden": ("Amethyst Seedling", "Grows a new facet every full moon.", "the Crystal Beds",
                   "Seal-carvers grew amethyst the way others grew herbs, in beds of calcite watered with salt. Each crystal took a lifetime and a seal pressed into it at the start. The beds are still growing. The seals are still working."),
        "vault": ("Unbroken Seal", "Whatever is inside, they wanted it kept.", "the Sealed Undercroft",
                  "Under the Oath Stone the Seal-carvers built a vault closed with nine seals and no door. What it holds is a question for a braver Clowder. A seal is a promise the world has to keep. This one is still kept."),
    },
    "spindle": {
        "shrine": ("Spindle-Whorl Charm", "It spins even when your hand is still.", "the Loom Chapel",
                   "The Loom-stitchers' chapel held a small loom that was never stopped: whoever passed added a thread. It was a weaving of everyone who ever visited. When they cut the gate-paths, they meant to come back and finish it. It is still unfinished."),
        "watchtower": ("Weaver's Beacon", "It points toward whatever needs mending.", "the Gate Lookout",
                       "From the Gate Lookout the Loom-stitchers watched the gate-paths they had cut through the sky, and mended them when they frayed. Every stitch in the sky was theirs. The day of the Cut they saw the whole weave tear at once. They ran to fix it."),
        "library": ("Pattern Card of the Old Sky", "Punched holes, a shuttle's path. The whole weave of the world.", "the Thread Archive",
                    "The Thread Archive kept the pattern of the old sky on punched cards: every island, every path, every knot between them. The Loom-stitchers could weave it again if they had to. They had to. The cards are nearly all still here."),
        "forge": ("Bone Shuttle", "Worn smooth by a thousand crossings.", "the Shuttle Works",
                  "At the Shuttle Works the Loom-stitchers carved shuttles that could carry thread through the sky itself. Each one crossed the void a thousand times before it wore out. This one did not wear out. It was dropped."),
        "garden": ("Flax Bloom", "Every thread starts as a flower.", "the Flax Field",
                   "The Loom-stitchers grew their own thread: a blue flax field on a slope above the looms, harvested by every hand on the island at once. It was the only day the looms were quiet. The field still flowers blue. Harvest it."),
        "vault": ("Unfinished Tapestry", "Every tribe, one thread each. One is still loose.", "the Gate Vault",
                  "In the Gate Vault the Loom-stitchers kept the one tapestry they never showed: all nine tribes woven together, with a thread left loose at the edge on purpose. They always meant to come back. Stitch the cut. Then go and see what the March kept for you."),
    },
}

HEART = ("Heart of the Weave", "Nine threads, one knot. It is warm.", "the Heartwreck",
         "Before the Cut the nine tribes met in one hall at the centre of the old world, each district facing the loom in the middle. They were not one people and never tried to be. They were one weave. The Skies were never an ending. They were the Loom, holding its breath while you learned to hold the thread. Go on weaving.")


def keepsake(strand, core):
    return C[strand][core][0]


def inscription(strand, core):
    return C[strand][core][1]


def place(strand, core):
    return C[strand][core][2]


def lore(strand, core):
    return C[strand][core][3]


def check():
    for s in STRANDS:
        assert set(C[s]) == set(CORES), s
        for c in CORES:
            name, ins, pl, lo = C[s][c]
            assert name and ins and pl and lo, (s, c)
            assert 2 <= lo.count(".") + lo.count("!") + lo.count("?") <= 6, (s, c, "2-4 sentences")
    names = [C[s][c][0] for s in STRANDS for c in CORES]
    assert len(set(names)) == len(names), "keepsake names must be unique"
    return len(names)


if __name__ == "__main__":
    print(check(), "keepsakes")
