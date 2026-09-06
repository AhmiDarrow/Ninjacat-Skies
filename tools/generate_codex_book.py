#!/usr/bin/env python3
"""Whisker Codex — Modonomicon book data for the ninjacatskies mod.

Three categories: The Cut (what happened, how the Loom works now), The Braid (the campaign, phase by phase,
pointing at quest chapters and key blocks — no recipe walls), and Nine Tribes (steward entries that unlock
as a Clowder seats each Strand). Every page is one screen, one thought. Codex voice: wry, tactile, practical.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "mods/ninjacatskies/src/main/resources/data/ninjacatskies/modonomicon/books/whisker_codex"
NS = "ninjacatskies"


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
        "background": "modonomicon:textures/gui/dark_slate_seamless.png",
        "background_parallax_layers": [
            {"background": "modonomicon:textures/gui/parallax/flow/base.png", "speed": 1.0},
            {"background": "modonomicon:textures/gui/parallax/flow/1.png", "speed": 1.0},
            {"background": "modonomicon:textures/gui/parallax/flow/2.png", "speed": 1.15},
        ],
    })


def advancement(path: str) -> dict:
    return {"type": "modonomicon:advancement", "advancement_id": f"{NS}:{path}"}


# ------------------------------------------------------------------------------------ book

w(BOOK / "book.json", {
    "name": "Whisker Codex",
    "tooltip": "Damaged, but it still assigns work.",
    "description": "The Loom was cut. This is what is left of the manual.",
    "generate_book_item": False,
    "custom_book_item": f"{NS}:whisker_codex",
    "default_title_color": 0xD4A84B,
    "auto_add_read_conditions": False,
})

# ------------------------------------------------------------------------------------ The Cut

category("the_cut", "The Cut", f"{NS}:whisker_codex", 0, "What happened, and what still works.")

entry("the_cut", "loom", "The Loom of Worlds", "What held the sky up.", f"{NS}:spindle_loom_fragment", 0, 0, [
    text("The Loom of Worlds",
         "The skies were held by a lattice of living thread. Nine Strands, tended by nine tribes of Ninjacats, "
         "pulled taut across the whole sky.\n\nContinents hung from it. Weather ran along it. Nothing fell "
         "that was not meant to."),
    text("What the tribes made",
         "From their shared pull on the Loom came **Tribal Power**: shamanic technomancy of pulse, lattice, "
         "seal, and the road into the March-lands.\n\nThe engines are still out there. Orphaned, humming, "
         "sacred. Treat them like an inheritance, not a scrap pile."),
])

entry("the_cut", "cut", "The Cut", "Something severed the Loom.", "minecraft:shears", 2, 0, [
    text("The Cut",
         "Something severed the Loom. The Codex does not know what. Neither did the tribes, by the end.\n\n"
         "Continents fell. The tribes scattered. What did not fall is what you are standing on: pads of earth "
         "the Strands still remember."),
    text("The Fray",
         "Above the Dock stands a slow dark column. That is the cut itself — the **Fray** — standing over "
         "the place the sky used to knot.\n\nIt thins as Clowders tension Strands. When every Clowder has "
         "rewoven, it turns to lit thread. Go look at it now and then. It is the only clock this campaign has."),
], parents=["loom"])

entry("the_cut", "skybound", "Skybound", "You, on a pad, with a damaged book.", f"{NS}:frayed_thread", 4, 0, [
    text("Skybound",
         "You are Skybound: whoever the Loom dropped on a pad with enough grit to stay. The Codex assigns work. "
         "You do it. That is the arrangement.\n\nOpen the **quest book** for the work. This book is for "
         "why, and for what the tribes left in the margins."),
    text("Nine Strands",
         "Nine Strands still answer if pulled correctly: Soil, Stone, Sprout, Claw, Spark, Clock, Swarm, "
         "Sigil, Spindle.\n\nEach one ends in a **Strand token**. A token is proof, not fuel — it is never "
         "crafted, never consumed by a recipe. Seat it at a Tension Post and it stays seated."),
], parents=["cut"])

entry("the_cut", "clowder", "Clowders", "Teams, pads, and the Hall.", "clowderhall:island_charter", 6, 0, [
    text("Clowders",
         "A team is a **Clowder**. Clowders share a pad, share quests, and share Loom Tension: when one of "
         "you seats a Strand, all of you hear it.\n\nThe **Island Charter** claims a pad from the Dock. The "
         "**Hub Key** opens the Clowder Hall, where every Clowder on the server meets."),
    text("Specialise",
         "A Clowder does not have to climb everything in lockstep. Mid-campaign the braid opens three ways — "
         "Pattern, Colony, Hum — and any two carry the whole team into Bind.\n\nOne of you can farm. One "
         "can drum. Nobody has to be everyone."),
], parents=["skybound"])

entry("the_cut", "tension", "Loom Tension", "The Post, the seat, the hum.", f"{NS}:tension_post", 8, 0, [
    spotlight(f"{NS}:tension_post", "Tension Post",
              "Logs, a Binding Knot, and a scrap of Thread make a **Tension Post**. Raise one on the pad. "
              "Right-click it with a Strand token to seat that Strand; the notch lights, the tribe chimes, "
              "and the Post starts to hum."),
    text("What Tension does",
         "Seated Strands are **Loom Tension**. It is not a bar and it does not nag. It changes the pad.\n\n"
         "Near the Post: the pad mends you (Soil). It feeds you a little (Sprout). Fall damage stops within "
         "sight of it (Claw). Hands quicken (five Strands). Luck (Sigil). And the horizon warms, one Strand "
         "at a time."),
    text("Spun at the Post",
         "Two things are made at the Post, not the bench.\n\n**Braid Cord**: right-click with a Strand "
         "Filament once two of Clock, Swarm, or Spark are seated.\n\n**Spindle Loom Fragment**: right-click "
         "with a March stone once all nine are seated. Seat the Fragment to Reweave."),
], parents=["clowder"])

entry("the_cut", "thread", "Frayed Thread", "Currency, string, and the Desk.", f"{NS}:frayed_thread", 4, 2, [
    spotlight(f"{NS}:frayed_thread", "Frayed Thread",
              "Every quest returns a little **Frayed Thread** — scraps of the Loom that still hold. Unravel one "
              "for three string. Or keep it: the **Frayed Thread Desk** (a quest chapter) sells saplings, "
              "buckets, meshes, pearls, and other things a pad runs short of."),
    text("Codex Pages",
         "Every third Strand a Clowder seats, a **Codex Page** slips free — a margin note from that tribe. "
         "Right-click to read it. Pages are kept, not spent.\n\nThe Desk sells a few loose ones too. "
         "Those pick a tribe on their own."),
], parents=["skybound"])

entry("the_cut", "voidloom", "Voidloom", "Yarn, knots, meshes, and two stations.", "voidloom:void_yarn", 6, 2, [
    spotlight("voidloom:void_yarn", "Void Yarn",
              "Thread that remembers where it came from. Early: four string make two yarn. Later: string and an "
              "ender pearl in the Tension Barrel make two. The Loomframe combs a little out of dirt as **Loom "
              "Lint** — four lint, one yarn."),
    spotlight("voidloom:binding_knot", "Binding Knot",
              "A ring of yarn around a slime ball. Early slime is pad compost: dirt, seeds, bone meal.\n\n"
              "The Knot is the Loom's soft gate: Loomframes, Tension Posts, the first precision mechanism, "
              "and the AE2 controller all want one."),
    spotlight("voidloom:loomframe", "Loomframe",
              "Stretch a mesh, load it with dirt or gravel, and let it work — one piece every few seconds "
              "with a shuttle clack. Hoppers feed the top and pull the sides.\n\nThread meshes catch what "
              "Ex Deorum meshes do **and** the Loom's own scraps: Lint on string, Thread on flint, **Strand "
              "Filament** on iron."),
    spotlight("voidloom:tension_barrel", "Tension Barrel",
              "Pour water (the bucket comes straight back), add up to eight dirt, come back for clay. String "
              "and pearls in the same barrel make yarn.\n\nClay to porcelain clay to a porcelain bucket: that "
              "is how a pad first carries lava."),
], parents=["thread"])

# ------------------------------------------------------------------------------------ The Braid

category("braid", "The Loom Braid", "minecraft:string", 1, "The campaign, phase by phase.")

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
     "**Sprout.** A wheat field, a kitchen, Mystical Agriculture from Inferium up. Botany pots if you like "
     "compact.\n\nFood is infrastructure here. A Clowder that eats well leaves the pad sooner."),
    ("edge", "Edge", "Claw", "silentgear:blueprint_paper", 6, 0, "root",
     "**Claw.** Silent Gear blueprints, iron on your back, a bow, a portal frame. Leave the pad on purpose.\n\n"
     "Edge opens the braid: after Claw, Pattern, Colony, and Hum are all yours to choose from."),
    ("pattern", "Pattern", "Clock", "create:cogwheel", 8, -2, "edge",
     "**Clock.** Create. Water wheels, presses, mixers, belts — one cog, then the same cog again.\n\nThe "
     "precision mechanism wants a Binding Knot at its heart. That is the Loom asking to be included."),
    ("colony", "Colony", "Swarm", "productivebees:advanced_beehive", 8, 0, "edge",
     "**Swarm.** Productive Bees and deep crops. Living industry that forgives mistakes machines do not.\n\n"
     "A honeycomb, a hive, a bottle: Swarm's token is earned by keeping something alive that keeps something "
     "else alive."),
    ("hum", "Hum", "Spark", "tribalpower:drumheart", 8, 2, "edge",
     "**Spark.** Strike a Drumheart before you touch a wire. Spirit Pulse is the power fantasy here; Powah "
     "and Mekanism are bridges you cross later, if you want.\n\nBone Chime, Spirit Shard, Copper Resonator, "
     "Drumheart. Then listen."),
    ("bind", "Bind", "Sigil", f"{NS}:braid_cord", 10, 0, None,
     "**Sigil.** Two of Clock, Swarm, Spark seated, a Strand Filament in hand, right-click the Post: **Braid "
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

# ------------------------------------------------------------------------------------ Nine Tribes

category("tribes", "Nine Tribes", f"{NS}:strand_token_spindle", 2, "Who kept the Loom. Unlocks as you seat Strands.")

TRIBES = [
    ("soil", "Pad-keepers", -4, -2,
     "The Pad-keepers kept the hearths. Not the fires — the *warmth*: the banked heat in thin dirt that let a "
     "pad hold a family through a long dark.\n\nThey were the first to notice the Loom was fraying, because "
     "the pads got cold before anything fell.",
     "We never called it dirt. We called it what was left, and we kept it warm."),
    ("stone", "Grit-singers", -2, -3,
     "The Grit-singers named every shard by its echo. Iron is low and patient. Gold barely bothers to "
     "answer. Diamond does not answer at all; you find it by the silence around it.\n\nThey built the first "
     "meshes: not to find ore, but to give it somewhere to land.",
     "The mesh does not find the ore. The mesh gives the ore somewhere to land."),
    ("sprout", "Rootbinders", 0, -4,
     "The Rootbinders grew living anchors: March flora whose roots ran along the Strands and held pads that "
     "would otherwise have drifted.\n\nWhen the Loom was cut, the roots held for a season. That season is why "
     "anything is still up here.",
     "Roots are the only rope the void respects."),
    ("claw", "Edge-walkers", 2, -3,
     "The Edge-walkers kept footholds past the last fence post — cuts in the Loom that led somewhere on "
     "purpose. Spiritgear was theirs: tools that spend Pulse instead of edge.\n\nThey left the footholds so "
     "nobody would have to be brave in the same place twice.",
     "Boots first. Then the bridge. Then the courage; it arrives on its own."),
    ("spark", "Drumhearts", 4, -2,
     "The Drumhearts kept the beat under the whole sky. Spirit Pulse — power as rhythm before it was a "
     "number — ran from their drums along the lattice to every tribe.\n\nThe orphan engines you find still "
     "keep their time. Listen before you feed one.",
     "The drum is not loud. The drum is steady. Be the drum."),
    ("clock", "Pattern-weavers", 4, 0,
     "The Pattern-weavers sang factories the way you would sing a round: one figure, then the same figure "
     "again, until the work carried itself.\n\nTheir timed lattice songs are the ancestor of every belt and "
     "cog you will build. You already know this craft.",
     "A factory is a song that has stopped needing the singer."),
    ("swarm", "Colony-keepers", 2, 2,
     "The Colony-keepers tended hives that hummed in the Loom's own key, and March flowers that hummed back.\n\n"
     "They did not own their colonies. They were on good terms with them. That is the whole of the method.",
     "You do not own a hive. You are on good terms with it."),
    ("sigil", "Seal-carvers", 0, 3,
     "The Seal-carvers pressed spirit into matter and made it stay. A seal is a promise carved so the world "
     "has to keep it; a rite is asking the Loom, politely, for an exception.\n\nNever bind what you would "
     "not be willing to unbind.",
     "Spirit goes where it is asked politely and stays where it is fed."),
    ("spindle", "Loom-stitchers", -2, 2,
     "The Loom-stitchers cut the gate-paths — into the March, into the Nether and End, into places the map "
     "does not have words for — and always meant to come back and mend them.\n\nThey did not get to. You "
     "will.",
     "The Loom was never one thread. It was nine agreeing."),
]
for sid, tribe, x, y, lore, margin in TRIBES:
    entry("tribes", sid, tribe, f"Keepers of the {sid.title()} Strand.", f"{NS}:strand_token_{sid}", x, y, [
        text(tribe, lore),
        spotlight(f"{NS}:strand_token_{sid}", f"{sid.title()} Strand", f"*{margin}*\n\nSeated. The {tribe} answer when this Post hums."),
    ], condition=advancement(f"strand/{sid}"), hide=False)

entry("tribes", "reweave", "Reweave", "The cut, closed.", f"{NS}:spindle_loom_fragment", 0, 0, [
    text("Reweave",
         "Nine tribes, one thread. Your Clowder closed its Strand of the sky.\n\nThe Fray over the Dock is "
         "thinner for it. When every Clowder has done the same, it turns to lit thread and stays that way.\n\n"
         "Go and see what the March kept for you. Tell it we are sorry it took so long."),
], condition=advancement("reweave"), hide=True)

print("Whisker Codex book written to", BOOK.relative_to(ROOT))
