#!/usr/bin/env python3
"""Whisker Codex — Modonomicon book data for the ninjacatskies mod.

Categories: The Cut, The Old Sky (lore that unlocks as Strands seat), The Braid, Nine Tribes, Snapped Guardians.
The Work lives only in the pack kubejs copy. Category maps share the questline atlas. Codex voice: wry, tactile, practical.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "mods/ninjacatskies/src/main/resources/data/ninjacatskies/modonomicon/books/whisker_codex"
PACK_BOOK = ROOT / "pack/overrides/kubejs/data/ninjacatskies/modonomicon/books/whisker_codex"
NS = "ninjacatskies"
ATLAS = f"{NS}:textures/gui/quest_atlas.png"


def w(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def text(title: str, body: str) -> dict:
    return {"type": "modonomicon:text", "title": title, "text": body}


def spotlight(item: str, title: str, body: str) -> dict:
    return {"type": "modonomicon:spotlight", "item": {"id": item, "count": 1}, "title": title, "text": body}


def entry(cat: str, eid: str, name: str, desc: str, icon: str, x: int, y: int, pages: list, *,
          parents: list[str] | None = None, condition: dict | None = None, hide: bool = False,
          bg: tuple[int, int] = (0, 0)) -> None:
    obj = {
        "category": f"{NS}:{cat}",
        "name": name,
        "description": desc,
        "icon": icon,
        "x": x,
        "y": y,
        "background_u_index": bg[0],
        "background_v_index": bg[1],
        "hide_while_locked": hide,
        "pages": pages,
    }
    if parents:
        obj["parents"] = [{"entry": f"{NS}:{cat}/{p}", "draw_arrow": True, "line_enabled": True} for p in parents]
    if condition:
        obj["condition"] = condition
    w(BOOK / "entries" / cat / f"{eid}.json", obj)


def category(cid: str, name: str, icon: str, sort: int, desc: str = "") -> None:
    w(BOOK / "categories" / f"{cid}.json", {
        "name": name,
        "description": desc,
        "icon": icon,
        "sort_number": sort,
        "background": ATLAS,
        "background_width": 1536,
        "background_height": 1024,
    })


def advancement(path: str) -> dict:
    return {"type": "modonomicon:advancement", "advancement_id": f"{NS}:{path}"}


# ------------------------------------------------------------------------------------ book

w(BOOK / "book.json", {
    "name": "Whisker Codex",
    "tooltip": "Build, check, and explore the campaign.",
    "description": "Start here for practical lessons, placement diagrams and the story of the broken sky.",
    "generate_book_item": False,
    "custom_book_item": f"{NS}:whisker_codex",
    "default_title_color": 0xD4A84B,
    "auto_add_read_conditions": False,
})

# ------------------------------------------------------------------------------------ The Cut

category("the_cut", "The Cut", f"{NS}:whisker_codex", 1, "What happened, and what still works.")

entry("the_cut", "loom", "The Loom of Worlds", "What held the sky up.", f"{NS}:spindle_loom_fragment", 0, 0, [
    text("The Loom of Worlds",
         "Before the void had a name, the sky was a floor. Nine Strands of living thread — Soil, Stone, Sprout, "
         "Claw, Spark, Clock, Swarm, Sigil, Spindle — were pulled taut by nine tribes of Ninjacats. Continents "
         "hung from that lattice the way fruit hangs from a well-kept vine. Weather ran along it. Rain knew "
         "where to fall. Nothing dropped that was not meant to."),
    text("A sky that worked",
         "Roads were not cut into dirt. They were sung into the thread and walked. Crops rooted into Strand as "
         "much as soil. Drums under one pad were heard as Pulse under another. The Loom was not a god and it "
         "was not a machine. It was nine agreements kept at once.\n\nWhen the tribes pulled together, the "
         "horizon stayed put. That is the whole of the old physics."),
    text("What the tribes made",
         "From their shared pull came **Tribal Power**: shamanic technomancy of Pulse, lattice, seal, and the "
         "road into the March-lands. Workshops that listen. Totems that speak in six voices. A drum that is "
         "not loud, only steady.\n\nThe engines are still out there. Orphaned, humming, sacred. Treat them "
         "like an inheritance, not a scrap pile."),
])

entry("the_cut", "cut", "The Cut", "Something severed the Loom.", "minecraft:shears", 2, 0, [
    text("The Cut",
         "Something severed the Loom. The Codex does not know what. Neither did the tribes, by the end. One "
         "moment the sky was a floor. The next, the agreements failed in the same breath.\n\nContinents fell. "
         "Weather forgot its roads. The tribes scattered with whatever dirt they could carry. What did not "
         "fall is what you are standing on: pads of earth the Strands still remember."),
    text("How it came apart",
         "The Pad-keepers felt it first — hearths went cold while the sky still looked whole. Then the "
         "Rootbinders' living anchors held for a season, and that season is why anything is still up here. "
         "Guardians snapped in their arenas. Songs kept playing with nobody to hear them. Gate-paths stayed "
         "open into nowhere.\n\nThe Cut was not a war. It was a knot coming undone."),
    text("The Fray",
         "Above the Dock stands a slow dark column. That is the cut itself — the **Fray** — standing over "
         "the place the sky used to knot.\n\nIt thins as Clowders tension Strands. When every Clowder has "
         "rewoven, it turns to lit thread. Go look at it now and then. It is the only clock this campaign has."),
], parents=["loom"])

entry("the_cut", "skybound", "Skybound", "You, on a pad, with a damaged book.", f"{NS}:frayed_thread", 4, 0, [
    text("Skybound",
         "You are Skybound: whoever the Loom dropped on a pad with enough grit to stay. The Codex teaches. "
         "Grave assigns the work. That is the arrangement.\n\nOpen **Grave** (backtick) for the assignment list. Click a "
         "quest item to open its recipe in JEI. This book is for why, and for how to place the work. They are "
         "the same campaign."),
    text("What fixing it means",
         "You are not rebuilding the old continents. You are teaching nine Strands to agree again, one pad "
         "at a time. A seated token is a promise kept. A thinned Fray is the sky noticing.\n\nWhen a Clowder "
         "reweaves, that Clowder's Strand of the sky closes. When every Clowder has done the same, the Fray "
         "turns to lit thread and stays that way. The world does not snap back. It learns to hold."),
    text("Nine Strands",
         "Nine Strands still answer if pulled correctly: Soil, Stone, Sprout, Claw, Spark, Clock, Swarm, "
         "Sigil, Spindle.\n\nEach one ends in a **Strand token**. A token is proof, not fuel — it is never "
         "crafted, never consumed by a recipe. Seat it at a Tension Post and it stays seated."),
], parents=["cut"])

entry("the_cut", "clowder", "Clowders", "Teams, pads, and the Hall.", "clowderhall:island_charter", 6, 0, [
    text("Clowders",
         "A team is a **Clowder**. Clowders share a pad, share quests, and share Loom Tension: when one of "
         "you seats a Strand, all of you hear it."),
    text("Hall and Charter",
         "**Goal:** claim a pad and reach the Hall.\n\n"
         "You need the **Island Charter** and a **Hub Key** (starter kit / Hall).\n\n"
         "1. **K** or the **Island Charter** opens the island/team panel. Join or create a team, then pick a pad.\n"
         "2. Right-click a friend with the Charter to invite, or `/clowder invite` / `/clowder accept`.\n"
         "3. Sneak-use the Charter on solid pad ground to seal spawn.\n"
         "4. **Hub Key** or `/clowder hub` reaches Clowder Hall. `/clowder return` sends you home. Right-click a Hall Elder to trade Thread.\n\n"
         "**Check:** you are on the intended pad, and `/clowder hub` works."),
    text("Specialise",
         "A Clowder does not have to climb everything in lockstep. Mid-campaign the braid opens three ways — "
         "Pattern, Colony, Hum — and any two carry the whole team into Bind.\n\nOne of you can farm. One "
         "can drum. Nobody has to be everyone."),
], parents=["skybound"])

entry("the_cut", "tension", "Loom Tension", "The Post, the seat, the hum.", f"{NS}:tension_post", 8, 0, [
    spotlight(f"{NS}:tension_post", "Tension Post",
              "**Goal:** raise a Post and seat the first token.\n\n"
              "You need logs, a **Binding Knot**, and a scrap of **Frayed Thread**.\n\n"
              "Logs, a Binding Knot, and a scrap of Thread make a **Tension Post**. Raise one on the pad. "
              "Right-click it with a Strand token to seat that Strand; the notch lights, the tribe chimes, "
              "and the Post starts to hum.\n\n"
              "**Check:** the Soil notch is lit, and the pad starts mending you near the Post."),
    text("What Tension does",
         "Seated Strands are **Loom Tension**. It is not a bar and it does not nag. It changes the pad.\n\n"
         "Near the Post: the pad mends you (Soil). It feeds you a little (Sprout). Fall damage stops within "
         "sight of it (Claw). Hands quicken (five Strands). Luck (Sigil). And the horizon warms, one Strand "
         "at a time."),
    text("Spun at the Post",
         "**Goal:** spin **Braid Cord**, then a **Spindle Loom Fragment**, at the Post — not the bench.\n\n"
         "You need a **Strand Filament**; **March Stone** once all nine are seated.\n\n"
         "**Braid Cord**: right-click with a Strand Filament. The Post is the only requirement.\n\n"
         "**Spindle Loom Fragment**: right-click with a March stone once all nine are seated. Seat the Fragment to Reweave.\n\n"
         "**Check:** a Strand Filament at the Post gives you Braid Cord, and a Fragment after nine seats plus March Stone."),
], parents=["clowder"])

entry("the_cut", "thread", "Frayed Thread", "Currency, string, and Hall stalls.", f"{NS}:frayed_thread", 4, 2, [
    spotlight(f"{NS}:frayed_thread", "Frayed Thread",
              "**Goal:** keep Thread as currency, and unravel it only when you need string.\n\n"
              "You need quest rewards, flint-mesh dirt on a Loomframe, or a steward cache.\n\n"
              "Every quest returns a little **Frayed Thread** — scraps of the Loom that still hold. Unravel one "
              "for three string. Or keep it: **Kin stalls in Clowder Hall** (`/clowder hub`) sell saplings, "
              "buckets, meshes, pearls, and other things a pad runs short of. Right-click an Elder.\n\n"
              "**Check:** you can buy a sapling or mesh at a Hall Elder without going broke on string."),
    text("Earning Thread back",
         "**Goal:** turn a mined stockpile into spendable Thread.\n\n"
         "You need blocks of copper, iron, gold, amethyst, emerald or diamond, or a netherite ingot.\n\n"
         "**Grit** in Clowder Hall takes them across the counter for Thread. The rate is bad on purpose "
         "— a whole diamond block comes back as 24 Thread, and Spark sells two diamonds for 80 — so it "
         "is a way to spend a surplus, never a loop to farm. Stock returns each Minecraft day.\n\n"
         "**Check:** you can price one life at the Spark stall (four Shards, 400 Thread each) and say "
         "how many blocks that is before you start digging."),
    text("Codex Pages",
         "**Goal:** read a margin note without spending the page.\n\n"
         "You need a **Codex Page** from seating (every third Strand) or a Hall Kin stall.\n\n"
         "Every third Strand a Clowder seats, a **Codex Page** slips free — a margin note from that tribe. "
         "Right-click to read it. Pages are kept, not spent.\n\nHall Kin stalls at `/clowder hub` sell a few "
         "loose ones too. Those pick a tribe on their own.\n\n"
         "**Check:** right-click a page; it stays in your hand."),
], parents=["skybound"])

entry("the_cut", "voidloom", "Voidloom", "Yarn, knots, meshes, and two stations.", "voidloom:void_yarn", 6, 2, [
    spotlight("voidloom:void_yarn", "Void Yarn",
              "**Goal:** have yarn without eating the whole string stock.\n\n"
              "You need four string (early) or string plus a pearl in the Tension Barrel.\n\n"
              "Thread that remembers where it came from. Early: four string make two yarn. Later: string and an "
              "ender pearl in the Tension Barrel make two. The Loomframe combs a little out of dirt as **Loom "
              "Lint** — four lint, one yarn.\n\n"
              "**Check:** JEI shows two yarn from four string, and you have yarn in the inventory."),
    spotlight("voidloom:binding_knot", "Binding Knot",
              "**Goal:** tie the Loom's soft gate so Recover stations can exist.\n\n"
              "You need Void Yarn and a slime ball (pad compost: dirt, seeds, bone meal).\n\n"
              "A ring of yarn around a slime ball. Early slime is pad compost: dirt, seeds, bone meal.\n\n"
              "The Knot is the Loom's soft gate: Loomframes, Tension Posts, the first precision mechanism, "
              "and the AE2 controller all want one.\n\n"
              "**Check:** you hold a Binding Knot."),
    spotlight("voidloom:loomframe", "Loomframe",
              "**Goal:** a hopper sieve that also catches Loom scraps.\n\n"
              "You need planks around a Binding Knot, a mesh, and grit.\n\n"
              "Stretch a mesh, load it with dirt, gravel, sand or dust, and let it work — one piece every few "
              "seconds with a shuttle clack. Hoppers feed the top and pull from below. The mesh is hand-only. "
              "An oak sieve is still click; this machine is the hopper one.\n\nThread meshes catch what Ex "
              "Deorum meshes do **and** the Loom's own scraps: Lint on string, Thread on flint, **Strand "
              "Filament** on iron (gravel, sand or dust).\n\n"
              "**Check:** a hopper above feeds grit and a hopper below pulls scraps."),
    spotlight("voidloom:tension_barrel", "Tension Barrel",
              "**Goal:** clay without a clay biome, and yarn from string plus a pearl.\n\n"
              "You need planks, string, Void Yarn, then water and dirt (or string and pearls).\n\n"
              "Pour water (the bucket comes straight back), add up to eight dirt, come back for clay. String "
              "and pearls in the same barrel make yarn.\n\nClay to porcelain clay to a porcelain bucket: that "
              "is how a pad first carries lava.\n\n"
              "**Check:** empty-hand the barrel and take clay; the empty bucket came back when you poured."),
], parents=["thread"])

# ------------------------------------------------------------------------------------ The Old Sky (unlocks with the campaign)

category("memory", "The Old Sky", f"{NS}:codex_page", 2, "What the world was, and what mending it costs. Unlocks as you seat Strands.")

entry("memory", "hanging_sky", "A sky that was a floor", "Before anything fell.", f"{NS}:spindle_loom_fragment", 0, 0, [
    text("Hanging continents",
         "Ask a Pad-keeper what a continent was and they will tell you: a pad that had forgotten it was a pad. "
         "Fields ran to the horizon because the Soil Strand ran with them. Rivers kept to their beds because "
         "the Sprout Strand taught water manners. Cities did not float. They hung, and hanging felt like "
         "standing, the way a well-tied hammock feels like a floor."),
    text("A maintained floor",
         "The sky-floor was a job, not a miracle. Pad-keepers walked the hearths. Grit-singers listened for "
         "cracks. Rootbinders checked the living anchors. Edge-walkers walked the rim and came back with a "
         "list. Drumhearts kept the beat so the rest of the work had a tempo. Pattern-weavers sang the "
         "factories that fed the rest. Colony-keepers kept the hives that kept the flowers that kept the "
         "roots. Seal-carvers asked, politely, for exceptions. Loom-stitchers mended the roads so nobody "
         "had to jump.\n\nA continent that looked like ground was a continent whose last inspection had gone well."),
    text("Weather with a road",
         "Rain did not guess. It followed Clock-sung channels along the lattice and arrived when the Pattern-"
         "weavers said it should. Storms were a Drumheart argument that got out of hand, then got walked back. "
         "Night was a veil the Seal-carvers asked for, politely, and the Loom kept the appointment.\n\n"
         "You can still see the habit in the aurora. It is the sky trying to remember a schedule."),
    text("A schedule, not a mood",
         "Weather was a roster. You could set a table by it, because the table had been sung. Wind had a "
         "shift. Fog had a route. Harvest rain arrived on the day the Pattern-weavers marked, not when a "
         "cloud felt generous.\n\nWhen the Cut came the appointments kept firing into empty air. That is "
         "why the aurora still tries. It is not pretty. It is a timetable with nobody on it."),
    text("Nine agreeing",
         "No tribe could hold the sky alone. Soil without Stone is warmth with nowhere to stand. Spark without "
         "Clock is a beat with no song. Sigil without Spindle is a promise with no road home.\n\n"
         "The old world was not peace. It was nine pulls kept taut at once. Peace was a side effect, and a thin one."),
    text("Maintenance, not peace",
         "Nine tribes is nine jobs. They argued. They borrowed each other's tools and forgot to bring them "
         "back. They wrote rude notes on each other's drums. What they did not do was let a Strand slacken "
         "because they were sulking.\n\nThe floor held because the work got done in public. The Cut is what "
         "happens when maintenance stops: the hammock remembers it was never ground."),
], parents=None)

MEMORY = [
    ("first_cold", "The first cold", "soil", "minecraft:campfire", 2, -1,
     "The hearths went out while the sky still looked whole.",
     [
         text("The first cold",
              "The Pad-keepers kept the warmth, not the fires — banked heat in thin dirt that let a family "
              "sleep through a long dark. They felt the Cut before anyone named it. Pads got cold. Bread "
              "took longer to rise. Moss would not take.\n\nThey carried dirt in baskets, a pad at a time, "
              "and set a hearth on every scrap they saved. That is why you have a pad at all."),
         text("What Soil remembers",
              "Seat Soil and the pad starts mending you. That is not a blessing invented for Skybound. It is "
              "the old hearth-trick, scaled down to whatever dirt is left. The Strand still knows how to "
              "keep a body warm if you ask it in the old way: a token, a Post, a promise kept."),
     ]),
    ("named_shards", "Named by echo", "stone", "minecraft:iron_ore", 4, -2,
     "Iron is low and patient. Diamond does not answer at all.",
     [
         text("Named by echo",
              "The Grit-singers named every shard by its voice. Iron is low and patient. Gold barely bothers "
              "to answer. Diamond does not answer at all; you find it by the silence around it.\n\nWhen the "
              "Cut came, the meshes kept humming to nothing. Ore had nowhere to land. Continents that were "
              "mostly stone fell as gravel and still fall, somewhere below the void, if below still means "
              "anything."),
         text("What Stone mends",
              "A mesh is not a finder. It is a welcome. Seat Stone and you are telling the ground it may "
              "arrive again. The Listening Pit, the Loomframe, the hammer chain — they are all the same "
              "courtesy: give the shard a place to sit."),
     ]),
    ("living_rope", "The season the roots held", "sprout", "minecraft:oak_sapling", 6, -2,
     "Roots are the only rope the void respects.",
     [
         text("The season the roots held",
              "The Rootbinders grew living anchors: March flora whose roots ran along the Strands and held "
              "pads that would otherwise have drifted. When the Loom was cut, those roots held for a season. "
              "Half of them. That season is why anything is still up here.\n\nAfter that, the anchors went "
              "feral, or quiet, or into the March. You will meet what they became."),
         text("What Sprout mends",
              "Food is infrastructure. A Clowder that eats well leaves the pad sooner because the Strand "
              "remembers being a continent's pantry. Seat Sprout and the Post feeds you a little. Plant "
              "something. The void respects a root more than a rope."),
     ]),
    ("last_foothold", "Boots first", "claw", "minecraft:iron_boots", 8, -1,
     "Then the bridge. Then the courage; it arrives on its own.",
     [
         text("Boots first",
              "The Edge-walkers kept footholds past the last fence post — cuts in the Loom that led somewhere "
              "on purpose. When the sky came apart they were already standing on the thin bits. Some of them "
              "walked people home. Some of them walked off the edge because that was the job.\n\nSpiritgear "
              "was theirs: tools that spend Pulse instead of edge, so a foothold could be cut without "
              "wearing the mountain out."),
         text("What Claw mends",
              "Seat Claw and fall damage stops within sight of the Post. That is a foothold, scaled to a pad. "
              "Edge is also when the braid opens: Pattern, Colony, Hum. The Edge-walkers never asked anyone "
              "to be brave in the same place twice. Pick a way and walk it."),
     ]),
    ("orphan_beat", "Orphan engines", "spark", "tribalpower:drumheart", 8, 1,
     "The drum is not loud. The drum is steady.",
     [
         text("Orphan engines",
              "The Drumhearts kept the beat under the whole sky. Spirit Pulse ran from their drums along the "
              "lattice to every tribe. When the Cut came, the drums did not stop. They had nobody left to "
              "stop for.\n\nYou will find engines still keeping time in the March and on pads that have not "
              "seen a cat in an age. Listen before you feed one. It may still be waiting for a beat you have "
              "not struck yet."),
         text("What Spark mends",
              "Seat Spark and you are not inventing power. You are sitting down at a drum that never learned "
              "how to quit. Strike empty-handed, about a breath apart. The drum is not loud. The drum is "
              "steady. Be the drum."),
     ]),
    ("songs_playing", "Songs still playing", "clock", "minecraft:clock", 6, 2,
     "A factory is a song that has stopped needing the singer.",
     [
         text("Songs still playing",
              "The Pattern-weavers sang factories the way you would sing a round: one figure, then the same "
              "figure again, until the work carried itself. When the Cut came the songs kept playing. Belts "
              "in empty halls. Clicks before a hum nobody owned.\n\nSome are playing still. That is not "
              "haunting. That is good engineering with no audience."),
         text("What Clock mends",
              "Seat Clock and you tell those songs they have a singer again. Create, timed plates, Song "
              "Thread — they are the same craft in different decades. A factory is a song that has stopped "
              "needing the singer. You are allowed to start it needing one."),
     ]),
    ("good_terms", "On good terms", "swarm", "minecraft:honeycomb", 4, 2,
     "You do not own a hive. You are on good terms with it.",
     [
         text("On good terms",
              "The Colony-keepers tended hives that hummed in the Loom's own key, and March flowers that "
              "hummed back. They did not own their colonies. They were on good terms with them. When the sky "
              "fell, a great many hives went quiet rather than angry. Quiet is a kind of loyalty.\n\n"
              "There are no bees to find in the void. You make somewhere a bee wants to be, and you wait."),
         text("What Swarm mends",
              "Seat Swarm and you are resuming a conversation, not founding a livestock industry. Keep "
              "something alive that keeps something else alive. Take without asking and the comb goes quiet. "
              "It is very patient about this."),
     ]),
    ("polite_ask", "Asked politely", "sigil", f"{NS}:braid_cord", 2, 1,
     "Spirit goes where it is asked politely and stays where it is fed.",
     [
         text("Asked politely",
              "The Seal-carvers pressed spirit into matter and made it stay. A seal is a promise carved so "
              "the world has to keep it. A rite is asking the Loom, politely, for an exception. They cut "
              "blank seals by the thousand before the Cut, and asked for far too much.\n\nBind is their "
              "chapter. Braid Cord is spun at the Post once two peers are seated. That is not a recipe. "
              "That is three Strands agreeing in public."),
         text("What Sigil mends",
              "Seat Sigil and you are allowed to ask again — smaller this time. Never bind what you would "
              "not be willing to unbind. Feed what you ask to stay. The old world broke on appetite. The "
              "new one will hold on manners."),
     ]),
    ("unmended_gates", "Roads into nowhere", "spindle", "minecraft:ender_pearl", 0, 2,
     "They always meant to come back and mend them.",
     [
         text("Roads into nowhere",
              "The Loom-stitchers cut the gate-paths — into the March, into the Nether and End, into places "
              "the map does not have words for — and always meant to come back and mend them. They did not "
              "get to. Open gates dumped weather into the void. Closed ones trapped whole roads in the "
              "March, still walking."),
         text("What Spindle mends",
              "Seat Spindle and you pick up a needle they dropped. The digital loom, the Gate Drum, a March "
              "stone, the Fragment. Nine seated, one stone, one right-click: the cut closes above your pad. "
              "They will not be there to thank you. Do it anyway."),
     ]),
    ("continents_named", "Named continents", "soil", "minecraft:grass_block", -2, -1,
     "Pads that forgot they were pads. Cities that hung. Hearths first.",
     [
         text("Named continents",
              "The old maps did not say *island*. They named continents the way you name a house: by who "
              "kept the hearth, by which river had manners, by which city hung over which Strand-knot. A "
              "pad that had forgotten it was a pad got a name. A name was a promise that the inspection "
              "had gone well for long enough to stop calling it a pad."),
         text("Cities that hung",
              "Markets sat on lattice, not bedrock. Stairs went down to the under-thread and up to the "
              "weather-road. You could walk a street and never think about the drop because the Soil Strand "
              "ran under the cobbles the way warmth runs under a well-kept floor.\n\nHanging felt like "
              "standing. That was the trick, and it was work."),
         text("Hearths as first physics",
              "Before Stone named shards, before Clock sang a factory, a Pad-keeper banked heat in thin "
              "dirt and called it a world. The hearth is the first physics. A continent is a hearth that "
              "got out of hand in the useful direction.\n\nSeat Soil and you are not founding a nation. "
              "You are reminding a scrap of dirt that it used to be allowed to stay warm."),
     ]),
    ("the_argument", "Nine pulls, nine arguments", "clock", "minecraft:compass", 8, 3,
     "Maintenance stopped. Eight pulls became eight arguments. The Spindle seam tore.",
     [
         text("Nine pulls, nine arguments",
              "The Cut was not a war. It was the moment the work stopped being done. Nine tribes had nine "
              "pulls. When the schedule failed, eight of those pulls turned into eight arguments about whose "
              "fault the slack was. Blame is a kind of tension. It does not hold a sky."),
         text("The Spindle seam",
              "The Loom-stitchers were the ones who mended the joins. While the others argued, the Spindle "
              "seam — the road between pads, the stitch that let nine pulls act as one floor — tore. Gates "
              "that should have led home led into weather. Weather that should have had a road had a hole.\n\n"
              "A clock with no stitch is just nine ticking things, each sure it is on time."),
         text("What Clock still knows",
              "The Pattern-weavers kept trying to sing the factories through it. Songs do not stop because "
              "the choir is fighting. Seat Clock and you are not picking a side in the old argument. You "
              "are putting a tempo back under work that has been improvising since the Cut."),
     ]),
    ("silence_after", "Songs with no singer", "sigil", "minecraft:note_block", -2, 0,
     "Factories running. Drums beating. Gates open into nowhere.",
     [
         text("Songs with no singer",
              "After the Cut the world did not go quiet. It went unattended. Factories kept the round the "
              "Pattern-weavers had taught them. Drums kept the beat the Drumhearts had left in them. Gates "
              "stood open into nowhere because a Loom-stitcher had always meant to come back and close them "
              "after lunch.\n\nLunch did not come. The work did."),
         text("Asking politely",
              "The Seal-carvers had a rule: spirit goes where it is asked politely and stays where it is "
              "fed. After the Cut, a lot of asking kept happening with nobody to feed the answer. Seals "
              "held promises to empty rooms. Rites fired into the Fray.\n\nPolite is still the method. The "
              "budget is smaller. Ask for a pad, not a continent."),
         text("Asking too much",
              "The old world broke on appetite as much as on slack. Exceptions stacked until the Loom had "
              "more appointments than thread. You will find blank seals by the thousand in the March. That "
              "is not treasure. That is a warning written in inventory.\n\nNever bind what you would not "
              "unbind. Feed what you ask to stay. The new sky will hold on manners."),
     ]),
    ("march_as_rest", "Where the fallen came to rest", "spindle", "minecraft:amethyst_cluster", -2, 2,
     "A frayed-thread grave. A harbour. Halls sunk to the lintel.",
     [
         text("Where the fallen came to rest",
              "The March was always a road. After the Cut it became a harbour for whatever could still "
              "walk. Frayed thread washed up there the way wreckage finds a quiet bay. Camps. Halls. "
              "Drums that never learned how to quit. The March is a grave and a harbour at once. Treat "
              "it like both."),
         text("Halls to the lintel",
              "Ancestor Halls stand in the steppe and highlands with their doors at the lintel — sunk, "
              "not fallen. Four tablets in each hall. Hollow Sentinels on a job nobody cancelled. "
              "Read every tablet. The dead are not asking for worship. They are asking for the record to "
              "be finished."),
         text("Where tension pools",
              "In the crystal fields the remaining pull gathers: March Crystal, the Spire, the Loom-"
              "stitchers' waystation. Tension that had nowhere to seat ran downhill into stone that would "
              "hold it. That is why Reweave wants a March stone. You are not fetching a trophy. You are "
              "bringing pooled tension home to a Post that can keep it."),
     ]),
]
for eid, name, strand, icon, x, y, desc, pages in MEMORY:
    entry("memory", eid, name, desc, icon, x, y, pages,
          parents=["hanging_sky"], condition=advancement(f"strand/{strand}"), hide=True)

entry("memory", "what_mending_means", "What mending means", "Nine agreeing, again.", f"{NS}:spindle_loom_fragment", 4, 0, [
    text("Not the old world",
         "Reweave does not put the continents back. It does not un-kill the guardians or un-scatter the "
         "tribes. It teaches nine Strands to hold a pad, then a Dock, then a sky that is honest about being "
         "made of thread.\n\nThe old world was a floor that pretended it was ground. The mended world is a "
         "floor that knows it is a promise."),
    text("A Clowder's share",
         "When your Clowder seats the Fragment, your Strand of the Fray closes. Other Clowders still have "
         "theirs to do. You do not own the sky you just taught to hold. You own a share of the work, and "
         "the share is public.\n\nA seated Fragment is a Clowder saying, in front of the Dock: we kept nine "
         "promises. The next Clowder still has nine to keep."),
    text("The Fray is the clock",
         "The column over the Dock is not scenery. It is the only honest clock this campaign has. It thins "
         "when a Clowder reweaves. It turns to lit thread when every Clowder has done the same. Go look at "
         "it. If it is still dark, the work is not finished — not because you failed, but because someone "
         "else has not had their hour yet."),
    text("Tablets and drums",
         "The March kept the record. Ancestor Halls: four tablets each, three rooms, sentinels on a job "
         "nobody cancelled. Read every tablet before you call the work done. The Silent Drum in the "
         "highlands still takes four beats, a breath apart. Strike it when you are ready. The Unsung is "
         "not a boss to loot. It is the March asking whether you learned the tempo."),
    text("Help them",
         "If the Fray has gone to lit thread, the sky has learned to hold. If it has not, someone else "
         "still has work. Help them. Share a mesh. Walk their pad. Sit at their drum. Mending that stays "
         "on one Clowder's island is just a nicer hammock.\n\nTell the camps we are sorry it took so long. "
         "Then make sure it does not take that long for the next team."),
], parents=["unmended_gates"], condition=advancement("reweave"), hide=True)

entry("memory", "how_the_sky_holds", "How the sky learns to hold", "Nine agreements, kept in public.", f"{NS}:spindle_loom_fragment", 6, 0, [
    text("How the sky learns to hold",
         "The sky does not snap back. It learns. A seated token is a lesson. Nine seated tokens are a "
         "pad that remembers how to be a floor. A Fragment seated is that pad telling the Dock it can "
         "stop holding its breath.\n\nYou are not restoring continents. You are teaching nine agreements "
         "to stay taut where everyone can see them."),
    text("Public, or it does not count",
         "A private mend is a secret. Secrets do not hold weather. The Tension Post hums for the whole "
         "Clowder. The Fray thins for the whole Dock. The lit thread, when it comes, is a server-wide "
         "fact.\n\nKeep the work in the open. That is how the old sky held, and it is the only method "
         "the new one will accept."),
    text("What you are not doing",
         "You will not get the hanging cities back. You will not get the schedule that let you set a "
         "table by the rain. You will get a sky that knows it is thread, and holds anyway.\n\nThat is "
         "the better physics. Honest hammocks last longer than floors that lie."),
], parents=["hanging_sky"], condition=advancement("reweave"), hide=True)

# ------------------------------------------------------------------------------------ The Braid

category("braid", "The Loom Braid", "minecraft:string", 3, "The campaign, phase by phase.")

BRAID = [
    ("wake", "Wake", "Soil", "minecraft:oak_sapling", 0, 0, None,
     "**Soil.** Wood, dirt, a bench, a sapling, a chest, warmth. Melt ice with lava for water on Normal and "
     "Hard. Cook something.\n\nThe Soil token comes from the **Soil Knot** at the end of the chapter. Raise a "
     "Tension Post and seat it. The pad starts mending you."),
    ("recover", "Recover", "Stone", "voidloom:spindle_hammer", 2, 0, "wake",
     "**Stone.** Unravel Thread to string, spin yarn, tie a Knot, raise a Loomframe. The Tension Barrel makes "
     "clay; clay makes porcelain; porcelain carries lava.\n\nThen the sieve. It is a tool inside Recover, not "
     "the name of it. Iron mesh is the target: that is where Strand Filament starts falling."),
    ("root", "Root", "Sprout", "mysticalagriculture:inferium_essence", 4, 0, "recover",
     "**Sprout.** A wheat field, a kitchen, then Mystical Agriculture. Sieve dirt for Inferium Ore and "
     "gravel for Prosperity Ore — smelt them, and the essence-seed tiers open up. Botany pots if you like compact.\n\n"
     "Food is infrastructure here. A Clowder that eats well leaves the pad sooner."),
    ("edge", "Edge", "Claw", "silentgear:blueprint_paper", 6, 0, "root",
     "**Claw.** Silent Gear plans, iron on your back, a bow, a portal frame. Leave the pad on purpose.\n\n"
     "Claiming a pad wipes Silent Gear's join gift. Four **Blueprint Paper**, shapeless, make a **Blueprint "
     "Package**. Right-click to unwrap starter plans.\n\n"
     "Edge opens the braid: after Claw, Pattern, Colony, and Hum are all yours to choose from."),
    ("pattern", "Pattern", "Clock", "create:cogwheel", 8, -2, "edge",
     "**Clock.** Create. Water wheels, presses, mixers, belts — one cog, then the same cog again.\n\nThe "
     "precision mechanism wants a Binding Knot at its heart. That is the Loom asking to be included."),
    ("colony", "Colony", "Swarm", "productivebees:advanced_oak_beehive", 8, 0, "edge",
     "**Swarm.** There are no bees to find in the void, so you make somewhere a bee wants to be: a ring of "
     "oak logs around a small flower, placed on the pad and woken with another flower (right-click it). "
     "Wait. Wings.\n\nEvery nest is the same trick with a "
     "different ring — gravel, coarse dirt, stone, quartz, end stone. Then hives, a centrifuge, an incubator, "
     "and deep essence crops. Keep something alive that keeps something else alive."),
    ("hum", "Hum", "Spark", "tribalpower:drumheart", 8, 2, "edge",
     "**Spark.** Strike a Drumheart before you touch a wire. Spirit Pulse is the power fantasy here; Powah "
     "and Mekanism are bridges you cross later, if you want.\n\nBone Chime, Spirit Shard, Copper Resonator, "
     "Drumheart. Then listen."),
    ("bind", "Bind", "Sigil", f"{NS}:braid_cord", 10, 0, None,
     "**Sigil.** A Strand Filament in hand, right-click the Post: **Braid "
     "Cord**.\n\nThen seals and rites — Tribal Power's own, with Nature's Aura, Ars Nouveau, and Occultism as "
     "peers. Carve carefully."),
    ("reweave", "Reweave", "Spindle", "ae2:controller", 12, 0, "bind",
     "**Spindle.** A digital loom (AE2, with a Knot in the controller and a Braid in the assembler). A Gate "
     "Drum. The March, and a March stone from it.\n\nNine seated, one stone, one right-click: the Fragment. "
     "Seat it. The cut closes above your pad."),
]
for eid, name, strand, icon, x, y, parent, body in BRAID:
    parents = [parent] if parent else None
    if eid == "bind":
        parents = ["pattern", "colony", "hum"]
    entry("braid", eid, name, f"{strand} Strand.", icon, x, y, [text(name, body)], parents=parents)

entry("braid", "living_lattice", "The Living Lattice", "Workshops, rites and paths.", "tribalpower:resonant_core", 8, 5, [
    text("The camp answers",
         "Tribal Weave is the workshop beside the nine Strands. Rhythm, landscape and reusable Echo catalysts "
         "make Pulse.\n\n"
         "Open the **Spirit Codex** for every generator, station, relay, Kiln, Voice Ring and rite. Sneak-use "
         "it on a silent machine. This book does not copy those manuals."),
    text("What the pack needs",
         "**Goal:** a Resonator that can feed Spark, then the later workshops the Spirit Codex diagrams.\n\n"
         "You need the **Spirit Codex** and a working Pulse Resonator from Start here.\n\n"
         "1. Finish **Make the first Echo Shard** and **Start automatic power** in Start here.\n"
         "2. Keep the Spirit Codex on your hotbar while you run Tribal Weave.\n"
         "3. Slot faces, Shatter-on-Kiln, relays, compass landings, ranked machines, Spirit Charms, Pulse lamps and the sixth Loom voice live in that book, not here.\n"
         "A held redstone signal pauses generators other than the Drumheart."),
    text("Check",
         "**Check:** sneak-use the Spirit Codex on the Resonator. Stored Pulse should rise with two different "
         "voices and a catalyst seated."),
], parents=["hum"])

entry("braid", "listening_pit", "Listening Pit and Gates", "Patterns, ore, voices, travel.", "tribalpower:resonance_mesh", 8, 7, [
    text("Goal",
         "**Goal:** run one rite and one travel tool the Spirit Codex already diagrams.\n\n"
         "You need the **Spirit Codex**; those shapes live there, not here.\n\n"
         "Stone Font, Listening Pit, Rite Circle, Voice Ring, Shatter Array, Way Gate and Far Gate are Spirit "
         "Codex shapes. Whisker does not reprint them."),
    text("March travel",
         "The Gate Drum is the portable way into the March. Use it empty-handed and play the Gate Rite: hit the falling beats on A, S, D, F. Land 60% and it opens; no Pulse needed. "
         "Do not strike it like a Drumheart.\n\n"
         "Bind a return compass before you go. `/tribalpower gate list` names later gates."),
    text("Check",
         "**Check:** one Font or Pit from the Spirit Codex diagram produces an output. If it stays silent, "
         "crouch and right-click with the Spirit Codex."),
], parents=["living_lattice"])

# ------------------------------------------------------------------------------------ Nine Tribes

category("tribes", "Nine Tribes", f"{NS}:strand_token_spindle", 4, "Who kept the Loom. Unlocks as you seat Strands.")

TRIBES = [
    ("soil", "Pad-keepers", -4, -2,
     "The Pad-keepers kept the hearths. Not the fires — the *warmth*: the banked heat in thin dirt that let a "
     "pad hold a family through a long dark.\n\nThey were the first to notice the Loom was fraying, because "
     "the pads got cold before anything fell.\n\nBefore the Cut they banked heat under whole continents: "
     "hearths under markets, under fields, under the first stair of every hanging city. What they lost was "
     "the long dark they had already solved — warmth as a public fact. Now they keep scraps, and they keep them anyway.",
     "We never called it dirt. We called it what was left, and we kept it warm."),
    ("stone", "Grit-singers", -2, -3,
     "The Grit-singers named every shard by its echo. Iron is low and patient. Gold barely bothers to "
     "answer. Diamond does not answer at all; you find it by the silence around it.\n\nThey built the first "
     "meshes: not to find ore, but to give it somewhere to land.\n\nBefore the Cut they named ore as it "
     "arrived, not as it was dug — continents of stone that answered when sung to, meshes hung in the "
     "under-lattice like welcome mats. What they lost was a ground that wanted to be found. The shards still "
     "fall. They just have nowhere to land unless you build the welcome again.",
     "The mesh does not find the ore. The mesh gives the ore somewhere to land."),
    ("sprout", "Rootbinders", 0, -4,
     "The Rootbinders grew living anchors: March flora whose roots ran along the Strands and held pads that "
     "would otherwise have drifted.\n\nWhen the Loom was cut, the roots held for a season. That season is why "
     "anything is still up here.\n\nBefore the Cut those anchors were a public rope, thick as roads, holding "
     "pads that had grown into continents. What they lost was a season that did not have to end. Half the "
     "anchors held. The rest went feral, or quiet, or into the March, and you will meet what they became.",
     "Roots are the only rope the void respects."),
    ("claw", "Edge-walkers", 2, -3,
     "The Edge-walkers kept footholds past the last fence post — cuts in the Loom that led somewhere on "
     "purpose. Spiritgear was theirs: tools that spend Pulse instead of edge.\n\nThey left the footholds so "
     "nobody would have to be brave in the same place twice.\n\nBefore the Cut the rim was a job, not a dare: "
     "a list of places you could stand, a bridge already cut, courage allowed to arrive late. What they lost "
     "was a horizon that led somewhere on purpose. Some walked people home. Some walked off because that was "
     "the job. The thin bits are still thin.",
     "Boots first. Then the bridge. Then the courage; it arrives on its own."),
    ("spark", "Drumhearts", 4, -2,
     "The Drumhearts kept the beat under the whole sky. Spirit Pulse — power as rhythm before it was a "
     "number — ran from their drums along the lattice to every tribe.\n\nThe orphan engines you find still "
     "keep their time. Listen before you feed one.\n\nBefore the Cut the beat was civic: Pulse as a utility, "
     "drums as the sky's metronome, every pad on the same downbeat. What they lost was an audience. The "
     "engines did not stop. They had nobody left to stop for. You will find them still keeping time, waiting "
     "for a beat you have not struck yet.",
     "The drum is not loud. The drum is steady. Be the drum."),
    ("clock", "Pattern-weavers", 4, 0,
     "The Pattern-weavers sang factories the way you would sing a round: one figure, then the same figure "
     "again, until the work carried itself.\n\nTheir timed lattice songs are the ancestor of every belt and "
     "cog you will build. You already know this craft.\n\nBefore the Cut those songs fed hanging cities on a "
     "schedule you could set a table by. What they lost was the singer, not the song. Belts in empty halls. "
     "Clicks before a hum nobody owned. Seat Clock and you tell those songs they have a singer again.",
     "A factory is a song that has stopped needing the singer."),
    ("swarm", "Colony-keepers", 2, 2,
     "The Colony-keepers tended hives that hummed in the Loom's own key, and March flowers that hummed back.\n\n"
     "They did not own their colonies. They were on good terms with them. That is the whole of the method.\n\n"
     "Before the Cut that conversation ran at continent scale: hives in the Loom's key, flowers humming back "
     "across hanging fields. What they lost was the large talk. A great many hives went quiet rather than "
     "angry. Quiet is a kind of loyalty. There are no bees in the void until you make somewhere a bee wants to be.",
     "You do not own a hive. You are on good terms with it."),
    ("sigil", "Seal-carvers", 0, 3,
     "The Seal-carvers pressed spirit into matter and made it stay. A seal is a promise carved so the world "
     "has to keep it; a rite is asking the Loom, politely, for an exception.\n\nNever bind what you would "
     "not be willing to unbind.\n\nBefore the Cut they carved promises by the thousand — exceptions asked "
     "politely, then asked again, then asked too much. What they lost was manners with a budget. Bind is "
     "their chapter. The old world broke on appetite. The new one will hold on asking smaller.",
     "Spirit goes where it is asked politely and stays where it is fed."),
    ("spindle", "Loom-stitchers", -2, 2,
     "The Loom-stitchers cut the gate-paths — into the March, into the Nether and End, into places the map "
     "does not have words for — and always meant to come back and mend them.\n\nThey did not get to. You "
     "will.\n\nBefore the Cut they kept the roads between pads, between worlds, between the March and home. "
     "What they lost was the appointment. Open gates dumped weather into the void. Closed ones trapped whole "
     "roads still walking. The Spindle seam tore while the other eight pulls turned into arguments. You pick "
     "up the needle they dropped.",
     "The Loom was never one thread. It was nine agreeing."),
]
# 3.0: every tribe keeps a camp in the March — where it stands, what its hearth favours, what its Elder trades.
CAMPS = {
    "soil": ("the March steppe", "dirt and moss blocks, bread, Echo Shards", "Earth", "hearths and caches"),
    "stone": ("the March highlands", "raw ores, grits, Attuned Echo", "Earth", "Echo Shards for raw ore, Attuned Echo for grit"),
    "sprout": ("the March steppe", "saplings, seeds, Mossback Scale", "Water", "March saplings and Spirit Reed"),
    "claw": ("the March highlands", "leather, iron, Rift Tooth", "Fire", "Spiritgear and footholds"),
    "spark": ("the March steppe", "copper, charged Pulse Cells, Bone Chimes", "Fire", "Bone Chimes and Pulse Cells"),
    "clock": ("the March crystal fields", "redstone, clocks, Storm Wing", "Air", "timed songs and automation"),
    "swarm": ("the March steppe", "honey, flowers, Lantern Down", "Air", "hives and March flowers"),
    "sigil": ("the March highlands", "blank and element seals, Spirit Shards", "Spirit", "the tribe's Seal, Blank Seals and rite tablets"),
    "spindle": ("the March crystal fields, at the Crystal Spire", "March Crystal, Loom Thread, compasses", "Loom", "Loom Thread and a Waystone Compass at Friend, a Loom Anchor and a Loom Seal at Kin"),
}
for sid, tribe, x, y, lore, margin in TRIBES:
    where, favours, voice, trades = CAMPS[sid]
    entry("tribes", sid, tribe, f"Keepers of the {sid.title()} Strand.", f"{NS}:strand_token_{sid}", x, y, [
        text(tribe, lore),
        spotlight(f"{NS}:strand_token_{sid}", f"{sid.title()} Strand", f"*{margin}*\n\nSeated. The {tribe} answer when this Post hums."),
        text("Their camp", f"The {tribe} keep a camp in {where}: huts, a fire, a Tribe Hearth, a {voice} totem, a banner and four Kin — an Elder, a Drummer, a Hunter and a Weaver.\n\nTheir hearth favours {favours}. Their Elder trades {trades}, and at Voice standing presses the tribe's Mark into your hand."),
    ], condition=advancement(f"strand/{sid}"), hide=False)

entry("tribes", "camps", "The Nine Camps", "Standing, offerings, marks.", "tribalpower:tribe_hearth", -4, 0, [
    text("Standing", "Right-click a Tribe Hearth with what its tribe favours, or with a charged Pulse Cell, and your standing rises: Guest at 50, Friend at 150, Kin at 400, Voice at 800. Kills near the hearth and completed trades count. Hurting Kin costs 25 and turns the Hunters on you. Breaking a tribe banner costs five, the hearth forty. Generic camp blocks do not cost."),
    spotlight("tribalpower:tribe_mark", "Tribe Mark", "Given once, by an Elder, at Voice. With the tribe's Resonance Totem and two Spiritweave it becomes a Kinship Totem: an extra voice for the Pulse Resonator. Nine tribes can carry the song to fifteen voices."),
    text("The camp keeps the beat", "A Drummer plays every few seconds. A Drumheart within eight blocks takes two Pulse from each beat, so a camp is a small, honest source of power. `/tribalpower standing` prints all nine standings."),
], condition={"type": "modonomicon:advancement", "advancement_id": "tribalpower:tribes/offering"}, hide=False)

entry("tribes", "the_unsung", "The Unsung", "What the March remembers.", "tribalpower:silent_drum", 4, 2, [
    text("The halls that kept time", "Sunken Ancestor Halls stand in the March steppe and highlands: three rooms, four Lore Tablets in each hall, chests of Loom Thread and Echoes, Hollow Sentinels on guard. Read every tablet. The Crystal Spire in the crystal fields is the Loom-stitchers' waystation."),
    text("The Drum Circle", "Twelve pillars around a Silent Drum in the March highlands. Strike it four times, a breath apart, and The Unsung rises: an ancestor spirit shaped like a hollow standing drum.\n\nBeat: brace by sneaking against its shockwaves. Chorus: cut down the Echo Weavers it calls. Silence: it cannot be hurt until you strike the drum with the same four beats — then it is stunned and takes double."),
    spotlight("tribalpower:unsung_heart", "Unsung Heart", "One per kill, with Loom Thread and Resonant Cores. It crafts the Resonance Totem (Loom), the sixth voice."),
], condition={"type": "modonomicon:advancement", "advancement_id": "tribalpower:march/ancestor_hall"}, hide=False)

entry("tribes", "reweave", "Reweave", "The cut, closed.", f"{NS}:spindle_loom_fragment", 0, 0, [
    text("Reweave",
         "Nine tribes, one thread. Your Clowder closed its Strand of the sky.\n\nThe Fray over the Dock is "
         "thinner for it. When every Clowder has done the same, it turns to lit thread and stays that way.\n\n"
         "Go and see what the March kept for you. Tell it we are sorry it took so long."),
], condition=advancement("reweave"), hide=True)

# ------------------------------------------------------------------------------------ Snapped Guardians

import sys
sys.path.insert(0, str(ROOT / "tools"))
from guardians_lore import GUARDIANS, STRAND_TITLES, unlock

category("guardians", "Snapped Guardians", "guardians:frayed_totem_unwoven", 5, "The keepers the Cut snapped. Unlocks as you seat Strands.")

entry("guardians", "the_ritual", "Answer for the Cut", "Totems, arenas, relics.", "guardians:frayed_totem_beddown", 0, 0, [
    text("Answer for the Cut",
         "**Goal:** re-tension a snapped keeper on its own ground.\n\n"
         "You need that Strand seated, then its **Frayed Totem** from JEI. Gate totems are four **Frayed Thread** and four of "
         "the Strand's block around **Void Yarn**. Lint Golem uses white wool. First Cut uses obsidian around the Loomthread "
         "relic. Overweaver uses purpur around the Loomthread relic.\n\n"
         "Each Strand had a guardian: a Loom-construct that kept its thread taut. The Cut snapped them. They are not monsters "
         "to be killed but Strands to be re-tensioned, and the only way to re-tension one is to beat its keeper on its own ground.\n\n"
         "Craft the guardian's **Frayed Totem** once your Clowder has seated that Strand. Use it anywhere outside an arena. "
         "A spent life cannot call a guardian."),
    text("The arena",
         "You and every Clowder mate within 32 blocks are pulled to a stage built for that guardian alone: four spawn pads, "
         "the totem stone, and a sealed gate that opens on a win or a wipe. A fence returns anyone who falls, at a cost in hearts. "
         "Win and everyone goes home a few seconds later, each with the guardian's **Woven Relic**, including mates who spent a "
         "life during the fight. Wipe and you are spat back out with the totem spent; craft another.\n\n"
         "`/guardians leave` abandons a fight."),
    text("Relics",
         "A relic is a trophy with one power: a passive while worn — the Curios relic slot, the off-hand or the hotbar — and a "
         "right-click on a cooldown. `/guardians status` shows the Clowder's record.\n\n"
         "**Check:** `/guardians status` lists the win, and each living mate holds the Woven Relic."),
])

POS = {"beddown": (-4, -2), "grindmaw": (-2, -3), "thornmother": (0, -4), "edgewalker": (2, -3), "drumheart": (4, -2),
       "cogwright": (4, 0), "hivemind": (2, 2), "sealbreaker": (0, 3), "unwoven": (-2, 2),
       "lintgolem": (-4, 0), "tangle": (-4, 2), "firstcut": (4, 3), "overweaver": (4, -4)}
for gid, title, strand, relic, tier, arena, fight, power in GUARDIANS:
    x, y = POS[gid]
    where = (f"Keeper of the {STRAND_TITLES[strand]} Strand." if strand else
             "An optional fight after Claw." if gid == "tangle" else
             "A gentle first fight." if tier == "easy" else "After the Reweave.")
    entry("guardians", gid, title[0].upper() + title[1:], where, f"guardians:frayed_totem_{gid}", x, y, [
        text(title[0].upper() + title[1:],
             "**Goal:** beat this keeper and bring its relic home.\n\n"
             "You need its **Frayed Totem** after the unlock, used outside an arena. Mates within 32 blocks come with you.\n\n"
             + arena + "\n\n" + fight + "\n\n"
             "**Check:** `/guardians status` lists this win, and you hold the Woven Relic."),
        spotlight(f"guardians:frayed_totem_{gid}", "Frayed Totem",
                  "Four Frayed Thread and four of the Strand's block around a Void Yarn." if tier == "gate" else
                  "Frayed Thread and purpur around the Loomthread relic; the relic is handed back." if gid == "overweaver" else
                  "Frayed Thread and obsidian around the Loomthread relic; the relic is handed back." if tier == "insane" else
                  "Four Frayed Thread and four white wool around a Void Yarn." if gid == "lintgolem" else
                  "Four Frayed Thread and four leaves around a Void Yarn."),
        spotlight(f"guardians:relic_{relic}", "Woven Relic", power),
    ], parents=["the_ritual"], condition={"type": "modonomicon:advancement", "advancement_id": unlock(gid, strand)}, hide=False)

# ------------------------------------------------------------------------------------ Driftwrecks

from driftwrecks_content import C as DW, CORES as DW_CORES, CORE_TITLES as DW_CORE_TITLES, HEART as DW_HEART, STRANDS as DW_STRANDS, TRIBES as DW_TRIBES

DW_HINTS = {"shrine": "The shrine-tenders kept the best offering under the stone they knelt on.",
            "watchtower": "Three landings up, the watch kept a room nobody climbed to.",
            "library": "One shelf in every library was never meant to be read.",
            "forge": "The forge-keepers kept their best work where the hammer fell.",
            "garden": "The gardeners buried what they loved under the water they gave it.",
            "vault": "A vault with one wall is a door. A vault with two is a promise."}


def dw_adv(path: str) -> dict:
    return {"type": "modonomicon:advancement", "advancement_id": f"driftwrecks:{path}"}


category("driftwrecks", "Driftwrecks", "driftwrecks:wreck_atlas", 7, "Pieces of the old world, caught on your weft. They do not stay.")
entry("driftwrecks", "caught", "Something drifting", "How a wreck arrives, and how to reach it.", "driftwrecks:tether_spool", -5, 0, [
    text("Something drifting",
         "**Goal:** reach a Driftwreck before it unravels.\n\n"
         "Once your Clowder has tensioned Soil, pieces of the old world drift up to your pad now and then: roughly once "
         "every hour and a half of play, or sooner if you hang a **Driftlure** on your Tension Post. The Steward tells "
         "the whole Clowder when one is caught, and the **Drift Needle** points at it.\n\n"
         "Stand at your pad's edge, face the wreck and use a **Tether Spool**: a thread bridge lays itself across."),
    text("It will not hold",
         "A wreck only ages while someone in your Clowder is online. It creaks at half its time, starts to crumble at "
         "the rim near the end, and then unravels. Nobody falls: anyone on it is lifted home, and whatever you left in "
         "its chests comes home in a **Salvage Bundle** (in your **Salvage Crate**, if one stands by the Post).\n\n"
         "Fall off the tether and the thread catches you, for three hearts."),
    text("What to do there",
         "Every wreck asks one thing: open its heart chest, break its frayed spawners, light its thread pillars in the "
         "order the idol shows, walk a lost Steward echo home, or hold the seam through three waves. Do it and each of "
         "you gets **Salvaged Weft** and a **Seal**, the **Wreck Atlas** fills a page, and sometimes a **Keepsake** comes "
         "home.\n\n**Check:** your Atlas shows the new page."),
    spotlight("driftwrecks:salvagers_frame", "Salvager's Frame",
              "Spend Weft on spools, lures, needles, map scrolls, Weft Keys, tribe decor and reprints of Keepsakes you already found."),
], condition={"type": "modonomicon:advancement", "advancement_id": "ninjacatskies:strand/soil"})
for i, core in enumerate(DW_CORES):
    entry("driftwrecks", f"hint_{core}", f"The old {DW_CORE_TITLES[core].lower()}s", "A loose page about hidden rooms.", "driftwrecks:hint_page",
          -3, i - 2, [text(f"The old {DW_CORE_TITLES[core].lower()}s", DW_HINTS[core] + "\n\n*From now on, your Clowder's "
                           + DW_CORE_TITLES[core].lower() + " wrecks drift in with their hidden room open.*")],
          parents=["caught"], condition=dw_adv(f"hint/{core}"), hide=True)
for si, s in enumerate(DW_STRANDS):
    for ci, core in enumerate(DW_CORES):
        name, ins, place, lore = DW[s][core]
        entry("driftwrecks", f"{s}_{core}", place[0].upper() + place[1:], f"{DW_TRIBES[s]} · {DW_CORE_TITLES[core]}",
              f"driftwrecks:keepsake_{s}_{core}", si - 1, ci - 2, [text(place[0].upper() + place[1:], lore)],
              condition=dw_adv(f"lore/{s}_{core}"), hide=True)
entry("driftwrecks", "heart", "The heart of the old world", "Where all nine tribes met.", "driftwrecks:keepsake_heartwreck", 4, 5,
      [text("The heart of the old world", DW_HEART[3])], condition=dw_adv("lore/heart"), hide=True)

from whisker_lessons import build_lessons, sync_pack_primers, polish_book
build_lessons(BOOK, w, text, entry, category)
polish_book(BOOK, w)
print("Whisker Codex book written to", BOOK.relative_to(ROOT))

# Pack kubejs copy wins at runtime. Keep The Work (pack-only) and overlay generated cats/entries.
import shutil
PACK_BOOK.mkdir(parents=True, exist_ok=True)
(PACK_BOOK / "categories").mkdir(parents=True, exist_ok=True)
# Pack overlay wins at runtime. Keep Core name/tooltip/description so Start here stays first.
pack_book = json.loads((BOOK / "book.json").read_text(encoding="utf-8"))
w(PACK_BOOK / "book.json", pack_book)
for cat_file in (BOOK / "categories").glob("*.json"):
    shutil.copy2(cat_file, PACK_BOOK / "categories" / cat_file.name)
w(PACK_BOOK / "categories" / "the_work.json", {
    "name": "The Work",
    "description": "Pack primers that copy Start here, plus the always-open old-world page.",
    "icon": f"{NS}:whisker_codex",
    "sort_number": 6,
    "background": ATLAS,
    "background_width": 1536,
    "background_height": 1024,
})
for src_dir in (BOOK / "entries").iterdir():
    if not src_dir.is_dir():
        continue
    dest_dir = PACK_BOOK / "entries" / src_dir.name
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src in src_dir.glob("*.json"):
        shutil.copy2(src, dest_dir / src.name)

# Pack-only primer: always-open page in The Work that points at The Old Sky.
w(PACK_BOOK / "entries" / "the_work" / "old_world.json", {
    "category": f"{NS}:the_work",
    "name": "The old world",
    "description": "What hung, what fell, what fixing means.",
    "icon": f"{NS}:codex_page",
    "x": 0,
    "y": 2,
    "background_u_index": 0,
    "background_v_index": 0,
    "hide_while_locked": False,
    "pages": [
        text("What the world was",
             "Before the void had a name, the sky was a floor. Nine Strands of living thread — Soil, Stone, Sprout, "
             "Claw, Spark, Clock, Swarm, Sigil, Spindle — were pulled taut by nine tribes of Ninjacats. Continents "
             "hung from that lattice the way fruit hangs from a well-kept vine.\n\nCities did not float. They hung, "
             "and hanging felt like standing. Weather ran on a schedule, not a mood. Rain knew where to fall. "
             "Nothing dropped that was not meant to. The old world was not peace. It was maintenance."),
        text("How it fell",
             "Something severed the Loom. The Codex does not know what. Maintenance stopped. Eight pulls became "
             "eight arguments about whose fault the slack was. The Spindle seam tore. Continents fell. Weather "
             "forgot its roads. The tribes scattered with whatever dirt they could carry.\n\nWhat did not fall is "
             "what you are standing on: pads of earth the Strands still remember. Factories kept running. Drums "
             "kept beating. Gates stood open into nowhere. The March caught the wreckage — a grave and a harbour "
             "at once."),
        text("What fixing means",
             "You are not rebuilding the hanging continents. You are teaching nine Strands to agree again, one pad "
             "at a time. A seated token is a promise kept. A Clowder that seats the Fragment closes its Strand of "
             "the Fray. When every Clowder has done the same, the column over the Dock turns to lit thread.\n\n"
             "The world does not snap back. It learns to hold. Honest hammocks last longer than floors that lie."),
        text("The Old Sky chapter",
             "**The Old Sky** is the rest of this story, written as the tribes would tell it. It does not open all "
             "at once. As each Strand seats, that tribe's memory unlocks: hearths, meshes, roots, footholds, drums, "
             "songs, hives, seals, gates.\n\nCome back to that chapter when a token is seated. They only talk once "
             "you have kept their promise. This page is the always-open version — enough to start the work without "
             "waiting for the record."),
    ],
    "parents": [{"entry": f"{NS}:the_work/this_book", "draw_arrow": True, "line_enabled": True}],
})
print("Pack kubejs book synced to", PACK_BOOK.relative_to(ROOT))
sync_pack_primers(BOOK, PACK_BOOK, w)
polish_book(PACK_BOOK, w)
