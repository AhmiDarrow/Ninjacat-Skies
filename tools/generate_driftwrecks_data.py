#!/usr/bin/env python3
"""Driftwrecks data + assets JSON: lang, blockstates, models, loot tables, recipes, advancements, tags, sounds.

    python tools/generate_driftwrecks_data.py

Deterministic. Words come from tools/driftwrecks_content.py; textures from tools/generate_driftwrecks_art.py; wreck
plans from tools/wreck_factory.py. Items from other mods live in small per-mod loot tables guarded by
neoforge:conditions (NeoForge 1.21.1 only conditions whole tables) and are pulled in by reference.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from driftwrecks_content import C, CORES, CORE_TITLES, HEART, STRANDS, TRIBES, check  # noqa: E402

NS = "driftwrecks"
RES = ROOT / "mods/driftwrecks/src/main/resources"
ASSETS = RES / "assets" / NS
DATA = RES / "data" / NS
MODIFIERS = ["unmarked", "overgrown", "frozen", "haunted", "burning", "unstable"]
STRAND_TITLE = {s: s.title() for s in STRANDS}


def w(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def rl(p: str) -> str:
    return f"{NS}:{p}"


# ================================================================== lang

def lang() -> dict:
    L = {
        "itemGroup.driftwrecks": "Driftwrecks",
        "item.driftwrecks.salvaged_weft": "Salvaged Weft",
        "item.driftwrecks.frayed_core": "Frayed Core",
        "item.driftwrecks.driftwreck_seal": "Driftwreck Seal",
        "item.driftwrecks.rift_shard": "Rift Shard",
        "item.driftwrecks.drift_needle": "Drift Needle",
        "item.driftwrecks.tether_spool": "Tether Spool",
        "item.driftwrecks.driftlure": "Driftlure",
        "item.driftwrecks.driftlure.tip": "Hang it on your Tension Post: a wreck drifts in soon after.",
        "item.driftwrecks.strand_lure": "Strand Lure",
        "item.driftwrecks.strand_lure.named": "Strand Lure (%s)",
        "item.driftwrecks.strand_lure.tip": "Hang it on your Tension Post: the wreck likely wears this Strand's skin.",
        "item.driftwrecks.weft_key": "Weft Key",
        "item.driftwrecks.weft_key.named": "Weft Key (%s)",
        "item.driftwrecks.weft_key.tip": "Opens a Hold's sealed rift of this Strand. Spent on use.",
        "item.driftwrecks.salvage_bundle": "Salvage Bundle",
        "item.driftwrecks.salvage_bundle.owner": "Left behind by %s",
        "item.driftwrecks.salvage_bundle.tip": "Right-click to unpack what the wreck was holding for you.",
        "item.driftwrecks.wreck_atlas": "Wreck Atlas",
        "item.driftwrecks.wreck_map_scroll": "Wreck-Map Scroll",
        "item.driftwrecks.wreck_map_scroll.tip": "Read it: the next wreck is a place your Atlas has not seen.",
        "item.driftwrecks.hint_page": "Hint Page",
        "item.driftwrecks.hint_page.named": "Hint Page: the %s",
        "item.driftwrecks.hint_page.tip": "Read it to file it in the Codex for your whole Clowder.",
        "block.driftwrecks.tether_thread": "Tether Thread",
        "block.driftwrecks.wreck_chest": "Wreck Chest",
        "block.driftwrecks.frayed_spawner": "Frayed Spawner",
        "block.driftwrecks.thread_pillar": "Thread Pillar",
        "block.driftwrecks.thread_idol": "Thread-Wound Idol",
        "block.driftwrecks.thread_lock": "Thread Lock",
        "block.driftwrecks.rift_tear": "Sealed Rift",
        "block.driftwrecks.salvage_crate": "Salvage Crate",
        "block.driftwrecks.salvagers_frame": "Salvager's Frame",
        "block.driftwrecks.trophy_plinth": "Trophy Plinth",
        "block.driftwrecks.keepsake_heartwreck": HEART[0],
        "block.driftwrecks.keepsake_heartwreck.inscription": HEART[1],
        "container.driftwrecks.wreck_chest": "Wreck Chest",
        "container.driftwrecks.heart_chest": "Heart of the Wreck",
        "container.driftwrecks.hidden_chest": "Hidden Room",
        "container.driftwrecks.salvage_crate": "Salvage Crate",
        "container.driftwrecks.salvagers_frame": "Salvager's Frame",
        "entity.driftwrecks.steward_echo": "Steward Echo",
        "entity.driftwrecks.remnant": "Remnant",
        "gui.driftwrecks.atlas.locked": "Tension the %s Strand to hear from its wrecks.",
        "gui.driftwrecks.atlas.unseen": "Not yet found.",
        "gui.driftwrecks.atlas.stamps": "Stamps",
        "gui.driftwrecks.atlas.remnants": "Remnants",
        "gui.driftwrecks.atlas.perks": "Perks",
        "gui.driftwrecks.atlas.no_perks": "Finish a column or a row.",
        "gui.driftwrecks.atlas.heart.1": "The Heartwreck is drifting your way.",
        "gui.driftwrecks.atlas.heart.2": "The Heartwreck is here.",
        "gui.driftwrecks.atlas.heart.3": "You stood in the heart of the old world.",
    }
    remnant_names = {"soil": "Remnant of the Beddown", "stone": "Remnant of the Grindmaw", "sprout": "Remnant of the Thornmother",
                     "claw": "Remnant of the Edgewalker", "spark": "Remnant of the Drumheart", "clock": "Remnant of the Cogwright",
                     "swarm": "Remnant of the Hivemind", "sigil": "Remnant of the Sealbreaker", "spindle": "Remnant of the Unwoven"}
    for s in STRANDS:
        L[f"entity.driftwrecks.remnant.{s}"] = remnant_names[s]
        L[f"block.driftwrecks.tribe_banner_{s}"] = f"{TRIBES[s]} Banner"
        for c in CORES:
            name, ins, place, _ = C[s][c]
            L[f"block.driftwrecks.keepsake_{s}_{c}"] = name
            L[f"block.driftwrecks.keepsake_{s}_{c}.inscription"] = ins
            L[f"gui.driftwrecks.place.{s}_{c}"] = f"The {TRIBES[s]} called it {place}."
    for a, (title, desc) in ADVANCEMENTS.items():
        L[f"advancements.driftwrecks.{a}.title"] = title
        L[f"advancements.driftwrecks.{a}.description"] = desc
    for sound in SOUNDS:
        L[f"subtitles.driftwrecks.{sound}"] = SOUNDS[sound][0]
    return L


# ================================================================== models

def item_model(name: str, tex: str | None = None, parent: str = "minecraft:item/generated"):
    """tex is a texture path under textures/ (default item/<name>)."""
    w(ASSETS / "models/item" / f"{name}.json", {"parent": parent, "textures": {"layer0": rl(tex or f"item/{name}")}})


def block_item_model(name: str, model: str | None = None):
    w(ASSETS / "models/item" / f"{name}.json", {"parent": rl(f"block/{model or name}")})


def simple_block(name: str, textures: dict, parent: str = "minecraft:block/cube_all"):
    w(ASSETS / "models/block" / f"{name}.json", {"parent": parent, "textures": textures})


def facing_variants(model: str, extra: str = "") -> dict:
    rot = {"north": 0, "east": 90, "south": 180, "west": 270}
    return {f"facing={f}{extra}": {"model": rl(f"block/{model}"), "y": r} if r else {"model": rl(f"block/{model}")} for f, r in rot.items()}


def box(frm, to, tex, faces="nsewud", uv=None, tint=None):
    f = {}
    for d, k in zip("nsewud", ["north", "south", "east", "west", "up", "down"]):
        if d in faces:
            face = {"texture": tex}
            if uv:
                face["uv"] = uv
            f[k] = face
    return {"from": frm, "to": to, "faces": f}


def models():
    # tether thread: half-height weave, bottom/top
    w(ASSETS / "models/block/tether_thread.json", {"parent": "minecraft:block/slab", "render_type": "minecraft:cutout", "textures": {"bottom": rl("block/tether_thread"), "top": rl("block/tether_thread"), "side": rl("block/tether_thread_side")}})
    w(ASSETS / "models/block/tether_thread_top.json", {"parent": "minecraft:block/slab_top", "render_type": "minecraft:cutout", "textures": {"bottom": rl("block/tether_thread"), "top": rl("block/tether_thread"), "side": rl("block/tether_thread_side")}})
    w(ASSETS / "blockstates/tether_thread.json", {"variants": {"half=bottom": {"model": rl("block/tether_thread")}, "half=top": {"model": rl("block/tether_thread_top")}}})
    block_item_model("tether_thread")

    # wreck chest: a banded trunk
    w(ASSETS / "models/block/wreck_chest.json", {
        "parent": "minecraft:block/block", "textures": {"particle": rl("block/wreck_chest_side"), "front": rl("block/wreck_chest_front"), "side": rl("block/wreck_chest_side"), "top": rl("block/wreck_chest_top")},
        "elements": [{"from": [1, 0, 1], "to": [15, 14, 15], "faces": {
            "north": {"texture": "#front"}, "south": {"texture": "#side"}, "east": {"texture": "#side"}, "west": {"texture": "#side"},
            "up": {"texture": "#top"}, "down": {"texture": "#top"}}}]})
    w(ASSETS / "blockstates/wreck_chest.json", {"variants": facing_variants("wreck_chest")})
    block_item_model("wreck_chest")

    simple_block("frayed_spawner", {"all": rl("block/frayed_spawner")}, "minecraft:block/cube_all")
    w(ASSETS / "blockstates/frayed_spawner.json", {"variants": {"": {"model": rl("block/frayed_spawner")}}})
    block_item_model("frayed_spawner")

    for lit in ("off", "on"):
        w(ASSETS / f"models/block/thread_pillar_{lit}.json", {
            "parent": "minecraft:block/block", "textures": {"particle": rl(f"block/thread_pillar_{lit}"), "side": rl(f"block/thread_pillar_{lit}"), "end": rl("block/thread_pillar_top")},
            "elements": [{"from": [3, 0, 3], "to": [13, 16, 13], "faces": {d: {"texture": "#side"} for d in ["north", "south", "east", "west"]} | {"up": {"texture": "#end"}, "down": {"texture": "#end"}}}]})
    w(ASSETS / "blockstates/thread_pillar.json", {"variants": {f"index={i},lit={str(l).lower()}": {"model": rl(f"block/thread_pillar_{'on' if l else 'off'}")} for i in range(5) for l in (False, True)}})
    block_item_model("thread_pillar", "thread_pillar_off")

    w(ASSETS / "models/block/thread_idol.json", {
        "parent": "minecraft:block/block", "textures": {"particle": rl("block/thread_idol"), "side": rl("block/thread_idol"), "top": rl("block/thread_idol_top")},
        "elements": [box([4, 0, 4], [12, 3, 12], "#top"), box([5, 3, 5], [11, 13, 11], "#side"), box([4, 13, 4], [12, 15, 12], "#top")]})
    w(ASSETS / "blockstates/thread_idol.json", {"variants": {"": {"model": rl("block/thread_idol")}}})
    block_item_model("thread_idol")

    w(ASSETS / "models/block/thread_lock.json", {"parent": "minecraft:block/cube_all", "render_type": "minecraft:translucent", "textures": {"all": rl("block/thread_lock")}})
    w(ASSETS / "blockstates/thread_lock.json", {"variants": {"": {"model": rl("block/thread_lock")}}})

    w(ASSETS / "models/block/rift_tear.json", {"parent": "minecraft:block/cross", "render_type": "minecraft:translucent", "textures": {"cross": rl("block/rift_tear")}})
    w(ASSETS / "blockstates/rift_tear.json", {"variants": {"": {"model": rl("block/rift_tear")}}})

    simple_block("salvage_crate", {"top": rl("block/salvage_crate_top"), "bottom": rl("block/salvage_crate_top"), "side": rl("block/salvage_crate_side")}, "minecraft:block/cube_bottom_top")
    w(ASSETS / "blockstates/salvage_crate.json", {"variants": {"": {"model": rl("block/salvage_crate")}}})
    block_item_model("salvage_crate")

    w(ASSETS / "models/block/salvagers_frame.json", {
        "parent": "minecraft:block/block", "render_type": "minecraft:cutout",
        "textures": {"particle": rl("block/salvagers_frame_wood"), "wood": rl("block/salvagers_frame_wood"), "warp": rl("block/salvagers_frame_warp")},
        "elements": [box([1, 0, 1], [3, 15, 3], "#wood"), box([13, 0, 1], [15, 15, 3], "#wood"), box([1, 0, 13], [3, 15, 15], "#wood"), box([13, 0, 13], [15, 15, 15], "#wood"),
                     box([1, 12, 1], [15, 15, 3], "#wood"), box([1, 3, 1], [15, 5, 3], "#wood"), box([1, 12, 13], [15, 15, 15], "#wood"),
                     {"from": [3, 5, 2], "to": [13, 12, 2], "faces": {"north": {"texture": "#warp"}, "south": {"texture": "#warp"}}},
                     box([2, 7, 3], [14, 8, 13], "#wood")]})
    w(ASSETS / "blockstates/salvagers_frame.json", {"variants": facing_variants("salvagers_frame")})
    block_item_model("salvagers_frame")

    w(ASSETS / "models/block/trophy_plinth.json", {
        "parent": "minecraft:block/block", "textures": {"particle": rl("block/trophy_plinth_side"), "side": rl("block/trophy_plinth_side"), "top": rl("block/trophy_plinth_top")},
        "elements": [box([0, 0, 0], [16, 3, 16], "#top"), box([2, 3, 2], [14, 10, 14], "#side"), box([1, 10, 1], [15, 12, 15], "#top")]})
    w(ASSETS / "blockstates/trophy_plinth.json", {"variants": {"": {"model": rl("block/trophy_plinth")}}})
    block_item_model("trophy_plinth")

    def keepsake(name):
        w(ASSETS / f"models/block/{name}.json", {"parent": "minecraft:block/cross", "render_type": "minecraft:cutout", "textures": {"cross": rl(f"item/{name}")}})
        w(ASSETS / f"blockstates/{name}.json", {"variants": facing_variants(name)})
        item_model(name)
    keepsake("keepsake_heartwreck")
    for s in STRANDS:
        for c in CORES:
            keepsake(f"keepsake_{s}_{c}")
        b = f"tribe_banner_{s}"
        w(ASSETS / f"models/block/{b}.json", {
            "parent": "minecraft:block/block", "render_type": "minecraft:cutout", "textures": {"particle": rl(f"block/{b}"), "cloth": rl(f"block/{b}"), "pole": "minecraft:block/dark_oak_log"},
            "elements": [box([0, 15, 7], [16, 16, 9], "#pole"),
                         {"from": [1, 0, 8], "to": [15, 15, 8], "faces": {"north": {"texture": "#cloth"}, "south": {"texture": "#cloth"}}}]})
        w(ASSETS / f"blockstates/{b}.json", {"variants": facing_variants(b)})
        item_model(b, f"block/{b}")

    # items
    for n in ["salvaged_weft", "frayed_core", "driftwreck_seal", "rift_shard", "tether_spool", "driftlure", "strand_lure", "weft_key",
              "salvage_bundle", "wreck_atlas", "wreck_map_scroll", "hint_page"]:
        item_model(n)
    # the needle: 32 angle frames, like a compass
    # vanilla compass scheme: angle 0 shows frame 16 (target straight ahead); frame (16 + k) % 32 from angle (2k - 1) / 64
    for i in range(32):
        item_model(f"drift_needle_{i:02d}")
    overrides = [{"predicate": {"angle": 0.0}, "model": rl("item/drift_needle_16")}]
    for k in range(1, 33):
        overrides.append({"predicate": {"angle": (2 * k - 1) / 64}, "model": rl(f"item/drift_needle_{(16 + k) % 32:02d}")})
    w(ASSETS / "models/item/drift_needle.json", {"parent": "minecraft:item/generated", "textures": {"layer0": rl("item/drift_needle_16")}, "overrides": overrides})


# ================================================================== loot

def count(lo, hi):
    return {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}} if lo != hi else {"function": "minecraft:set_count", "count": lo}


def item(name, weight=1, lo=1, hi=1, extra=None):
    e = {"type": "minecraft:item", "name": name, "weight": weight}
    fns = [count(lo, hi)] if (lo, hi) != (1, 1) else []
    if extra:
        fns += extra
    if fns:
        e["functions"] = fns
    return e


def ref(table, weight=1):
    return {"type": "minecraft:loot_table", "value": table, "weight": weight}


def pool(rolls, entries, chance=None):
    p = {"rolls": rolls if isinstance(rolls, (int, float)) else {"type": "minecraft:uniform", "min": rolls[0], "max": rolls[1]}, "entries": entries}
    if chance is not None:
        p["conditions"] = [{"condition": "minecraft:random_chance", "chance": chance}]
    return p


def table(pools, mod=None):
    t = {"type": "minecraft:chest", "pools": pools}
    if mod:
        t["neoforge:conditions"] = [{"type": "neoforge:mod_loaded", "modid": mod}]
    return t


def hint_pages(weight):
    return [item(rl("hint_page"), weight, extra=[{"function": "minecraft:set_components", "components": {rl("core"): c}}]) for c in CORES]


MOD_LOOT = {
    # tier: {modid: [(item, weight, lo, hi)]}
    1: {"exdeorum": [("exdeorum:string_mesh", 2, 1, 1), ("exdeorum:flint_mesh", 1, 1, 1), ("exdeorum:porcelain_clay_ball", 2, 2, 6)],
        "farmersdelight": [("farmersdelight:cabbage_seeds", 2, 2, 5), ("farmersdelight:tomato_seeds", 2, 2, 5), ("farmersdelight:rice", 1, 2, 4)],
        "pamhc2crops": [("pamhc2crops:cornseeditem", 1, 1, 3)]},
    2: {"create": [("create:andesite_alloy", 3, 8, 16), ("create:cogwheel", 2, 4, 8), ("create:shaft", 2, 8, 16), ("create:zinc_ingot", 2, 4, 8)],
        "mekanism": [("mekanism:ingot_osmium", 2, 4, 8), ("mekanism:basic_control_circuit", 1, 1, 3)],
        "mysticalagriculture": [("mysticalagriculture:inferium_essence", 3, 8, 16), ("mysticalagriculture:prosperity_shard", 2, 2, 6)],
        "ars_nouveau": [("ars_nouveau:source_gem", 2, 2, 4)]},
    3: {"create": [("create:brass_ingot", 3, 4, 10), ("create:precision_mechanism", 1, 1, 2), ("create:electron_tube", 2, 2, 6)],
        "mekanism": [("mekanism:alloy_infused", 2, 2, 6), ("mekanism:upgrade_speed", 1, 1, 1), ("mekanism:advanced_control_circuit", 1, 1, 2)],
        "mysticalagriculture": [("mysticalagriculture:prudentium_essence", 3, 6, 12), ("mysticalagriculture:inferium_seeds", 1, 1, 2)],
        "ae2": [("ae2:certus_quartz_crystal", 2, 4, 8), ("ae2:fluix_crystal", 1, 2, 4)]},
}


def loot():
    L = DATA / "loot_table"
    weft = rl("salvaged_weft")
    t1 = [item("minecraft:bone_meal", 4, 3, 8), item("minecraft:oak_sapling", 2, 1, 3), item("minecraft:birch_sapling", 2, 1, 3), item("minecraft:spruce_sapling", 2, 1, 3),
          item("minecraft:jungle_sapling", 1, 1, 2), item("minecraft:acacia_sapling", 1, 1, 2), item("minecraft:dark_oak_sapling", 1, 1, 2), item("minecraft:cherry_sapling", 1, 1, 2),
          item("minecraft:wheat_seeds", 3, 3, 8), item("minecraft:pumpkin_seeds", 2, 1, 3), item("minecraft:melon_seeds", 2, 1, 3), item("minecraft:beetroot_seeds", 2, 2, 5),
          item("minecraft:sugar_cane", 2, 1, 3), item("minecraft:cactus", 1, 1, 2), item("minecraft:sweet_berries", 2, 2, 5),
          item("minecraft:iron_nugget", 3, 4, 12), item("minecraft:copper_ingot", 2, 2, 6), item("minecraft:string", 3, 2, 6), item("minecraft:bread", 2, 1, 3)]
    t2 = [item("minecraft:iron_ingot", 4, 3, 8), item("minecraft:gold_ingot", 2, 2, 5), item("minecraft:redstone", 3, 6, 16), item("minecraft:lapis_lazuli", 2, 4, 10),
          item("minecraft:glow_berries", 2, 3, 8), item("minecraft:amethyst_shard", 2, 2, 6), item("minecraft:honeycomb", 1, 2, 4), item("minecraft:name_tag", 1),
          item("minecraft:experience_bottle", 2, 2, 6), item("minecraft:ender_pearl", 1, 1, 2)]
    t3 = [item("minecraft:diamond", 3, 1, 3), item("minecraft:emerald", 3, 2, 6), item("minecraft:gold_block", 1, 1, 2), item("minecraft:experience_bottle", 3, 4, 10),
          item("minecraft:book", 2, extra=[{"function": "minecraft:enchant_with_levels", "levels": {"type": "minecraft:uniform", "min": 15, "max": 30}}]),
          item("minecraft:golden_apple", 1), item("minecraft:ender_pearl", 2, 2, 4), item("minecraft:blaze_rod", 1, 1, 3)]
    t4 = [item("minecraft:diamond", 3, 2, 5), item("minecraft:netherite_scrap", 1), item("minecraft:emerald_block", 1),
          item("minecraft:book", 3, extra=[{"function": "minecraft:enchant_with_levels", "levels": 30}]), item("minecraft:golden_apple", 2, 1, 2),
          item("minecraft:echo_shard", 1, 1, 2)]
    mods = lambda tier: [ref(rl(f"chests/mods/tier{tier}_{m}"), 2) for m in MOD_LOOT.get(tier, {})]
    w(L / "chests/tier1.json", table([pool((3, 5), t1 + mods(1)), pool(1, [item(weft, 1, 1, 3)])]))
    w(L / "chests/tier2.json", table([pool((3, 5), t2 + t1[:6] + mods(2)), pool(1, [item(weft, 1, 3, 6)]),
                                     pool(1, hint_pages(1) + [item(rl("tether_spool"), 3)], chance=0.25)]))
    w(L / "chests/tier3.json", table([pool((3, 6), t3 + t2[:5] + mods(3) + mods(2)), pool(1, [item(weft, 1, 6, 10)]),
                                     pool(1, hint_pages(1) + [item(rl("wreck_map_scroll"), 2), item(rl("driftlure"), 2)], chance=0.4)]))
    w(L / "chests/tier4.json", table([pool((3, 5), t4 + t3[:4] + mods(3)), pool(1, [item(weft, 1, 8, 14)]), pool(1, hint_pages(1), chance=0.6)]))
    for tier, per in MOD_LOOT.items():
        for mod, entries in per.items():
            w(L / f"chests/mods/tier{tier}_{mod}.json", table([pool(1, [item(i, wt, lo, hi) for i, wt, lo, hi in entries])], mod=mod))
    w(L / "chests/heart.json", table([pool(1, [item(weft, 1, 2, 4)]), pool(1, hint_pages(1) + [item(rl("wreck_map_scroll"), 2)], chance=0.3)]))
    w(L / "chests/rift.json", table([pool((2, 3), [item("minecraft:diamond", 3, 2, 4), item("minecraft:netherite_scrap", 1), item("minecraft:echo_shard", 2, 1, 3),
                                                    item("minecraft:book", 3, extra=[{"function": "minecraft:enchant_with_levels", "levels": 30}]), item("minecraft:enchanted_golden_apple", 1)]),
                                     pool(1, [item(weft, 1, 10, 16)])]))
    for s in STRANDS:
        w(L / f"chests/skin/{s}.json", table([pool(1, [ref(f"ninjacatskies:steward_cache/{s}")], chance=0.3)]))
    # blocks
    def drops(name, entries=None):
        w(L / f"blocks/{name}.json", {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": entries or [item(rl(name))],
                                                                                "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
    for n in ["salvage_crate", "salvagers_frame", "trophy_plinth", "keepsake_heartwreck"]:
        drops(n)
    for s in STRANDS:
        drops(f"tribe_banner_{s}")
        for c in CORES:
            drops(f"keepsake_{s}_{c}")
    w(L / "blocks/frayed_spawner.json", {"type": "minecraft:block", "pools": [
        {"rolls": 1, "entries": [item(weft, 1, 1, 2)]}, {"rolls": 1, "entries": [item(rl("frayed_core"))]}]})


# ================================================================== recipes

def recipes():
    R = DATA / "recipe"
    weft = {"item": rl("salvaged_weft")}
    w(R / "salvagers_frame.json", {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": ["SWS", "P P", "PPP"],
                                    "key": {"S": {"item": "minecraft:string"}, "W": weft, "P": {"tag": "minecraft:planks"}}, "result": {"id": rl("salvagers_frame")}})
    w(R / "salvage_crate.json", {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": ["PWP", "P P", "PPP"],
                                  "key": {"W": weft, "P": {"tag": "minecraft:planks"}}, "result": {"id": rl("salvage_crate")}})
    w(R / "trophy_plinth.json", {"type": "minecraft:crafting_shaped", "category": "misc", "pattern": ["WSW", "SSS"],
                                  "key": {"W": weft, "S": {"item": "minecraft:smooth_stone"}}, "result": {"id": rl("trophy_plinth")}})
    w(R / "tether_spool.json", {"type": "minecraft:crafting_shapeless", "category": "misc",
                                 "ingredients": [weft, {"item": "minecraft:string"}, {"item": "minecraft:string"}, {"item": "minecraft:string"}, {"item": "minecraft:stick"}],
                                 "result": {"id": rl("tether_spool")}})
    w(R / "driftlure.json", {"type": "minecraft:crafting_shapeless", "category": "misc",
                              "ingredients": [weft, weft, weft, {"item": "minecraft:string"}, {"item": "minecraft:gold_nugget"}], "result": {"id": rl("driftlure")}})
    w(R / "drift_needle.json", {"type": "minecraft:crafting_shaped", "category": "equipment", "pattern": [" I ", "IRI", " W "],
                                 "key": {"I": {"item": "minecraft:iron_nugget"}, "R": {"item": "minecraft:redstone"}, "W": weft}, "result": {"id": rl("drift_needle")}})
    w(R / "wreck_atlas.json", {"type": "minecraft:crafting_shapeless", "category": "misc",
                                "ingredients": [{"item": "minecraft:book"}, weft, {"item": "minecraft:ink_sac"}], "result": {"id": rl("wreck_atlas")}})


# ================================================================== advancements

ADVANCEMENTS = {
    "root": ("Something Drifting", "See a Driftwreck caught on your Clowder's weft"),
    "cross": ("Cross the Void", "Throw a tether to a Driftwreck"),
    "salvage": ("Salvage", "Finish a Driftwreck's objective"),
    "atlas": ("The Atlas", "Open the Wreck Atlas"),
    "keepsake": ("Keepsake", "Bring home a Keepsake from a Driftwreck"),
    "hidden_room": ("Behind the Shelf", "Open a hidden room's chest"),
    "rift": ("Into the Rift", "Open a Hold's sealed rift with a Weft Key"),
    "remnant": ("Mended", "Unravel a Remnant in its rift"),
    "remnants": ("Every Remnant", "Mend all nine Remnants"),
    "column": ("A Whole Column", "Fill every core of one Strand in the Atlas"),
    "row": ("A Whole Row", "Fill one core in every Strand in the Atlas"),
    "cells_25": ("Half the Atlas", "Fill 25 cells of the Wreck Atlas"),
    "cells_54": ("Every Page", "Fill all 54 cells of the Wreck Atlas"),
    "modifiers": ("Six Stamps", "Finish a wreck of every modifier"),
    "heartwreck": ("Heart of the Weave", "Re-thread the Heartwreck"),
}
ADV_TREE = {  # child: (parent, icon, frame)
    "root": (None, "tether_spool", "task"), "cross": ("root", "tether_spool", "task"), "salvage": ("cross", "salvaged_weft", "task"),
    "atlas": ("salvage", "wreck_atlas", "task"), "keepsake": ("salvage", "keepsake_soil_shrine", "task"), "hidden_room": ("salvage", "hint_page", "goal"),
    "modifiers": ("atlas", "driftwreck_seal", "goal"), "column": ("atlas", "tribe_banner_soil", "goal"), "row": ("atlas", "wreck_map_scroll", "goal"),
    "cells_25": ("atlas", "wreck_atlas", "goal"), "cells_54": ("cells_25", "wreck_atlas", "challenge"), "rift": ("salvage", "weft_key", "goal"),
    "remnant": ("rift", "rift_shard", "goal"), "remnants": ("remnant", "rift_shard", "challenge"), "heartwreck": ("cells_54", "keepsake_heartwreck", "challenge"),
}


def advancements():
    A = DATA / "advancement"
    impossible = {"criteria": {"done": {"trigger": "minecraft:impossible"}}, "requirements": [["done"]]}
    for a, (parent, icon, frame) in ADV_TREE.items():
        obj = {"display": {"icon": {"id": rl(icon)}, "title": {"translate": f"advancements.driftwrecks.{a}.title"},
                           "description": {"translate": f"advancements.driftwrecks.{a}.description"}, "frame": frame,
                           "show_toast": True, "announce_to_chat": frame != "task", "hidden": a in ("heartwreck", "remnants", "cells_54")}} | impossible
        if parent:
            obj["parent"] = rl(parent)
        else:
            obj["display"]["background"] = "minecraft:textures/block/cyan_terracotta.png"
        w(A / f"{a}.json", obj)
    # silent unlock flags for the Codex: lore per Atlas cell, hints per core, the Heartwreck finale
    for s in STRANDS:
        for c in CORES:
            w(A / f"lore/{s}_{c}.json", impossible)
    for c in CORES:
        w(A / f"hint/{c}.json", impossible)
    w(A / "lore/heart.json", impossible)


# ================================================================== tags, sounds

SOUNDS = {  # event: (subtitle, placeholder vanilla events until the sound pass)
    "driftwreck.arrive": ("A driftwreck creaks in", ["minecraft:block.respawn_anchor.charge", "minecraft:ambient.cave"]),
    "driftwreck.creak": ("Wreck creaks", ["minecraft:block.bamboo_wood.step"]),
    "driftwreck.crumble": ("Wreck crumbles", ["minecraft:block.gravel.break"]),
    "driftwreck.warn_final": ("The weft groans", ["minecraft:block.beacon.deactivate"]),
    "driftwreck.unravel": ("A driftwreck unravels", ["minecraft:block.amethyst_block.resonate", "minecraft:entity.illusioner.mirror_move"]),
    "tether.lay": ("Thread lays", ["minecraft:block.wool.place"]),
    "tether.catch": ("Thread catches", ["minecraft:entity.leash_knot.place"]),
    "rift.open": ("A rift opens", ["minecraft:block.end_portal_frame.fill"]),
    "keepsake.found": ("Keepsake found", ["minecraft:block.amethyst_block.chime"]),
    "atlas.page": ("Atlas page fills", ["minecraft:item.book.page_turn"]),
    "driftwreck.whisper": ("Whispers", ["minecraft:ambient.soul_sand_valley.mood"]),
}


def sounds_and_tags():
    sj = {}
    for ev, (sub, placeholders) in SOUNDS.items():
        own = ASSETS / "sounds" / (ev.replace(".", "/") + ".ogg")
        entries = [rl(ev.replace(".", "/"))] if own.exists() else [{"name": p, "type": "event"} for p in placeholders]
        sj[ev] = {"subtitle": f"subtitles.driftwrecks.{ev}", "sounds": entries}
    w(ASSETS / "sounds.json", sj)
    T = RES / "data/minecraft/tags/block"
    w(T / "mineable/pickaxe.json", {"replace": False, "values": [rl("frayed_spawner"), rl("trophy_plinth")]})
    w(T / "mineable/axe.json", {"replace": False, "values": [rl("salvage_crate"), rl("salvagers_frame")]})
    w(T / "needs_iron_tool.json", {"replace": False, "values": [rl("frayed_spawner")]})


def main():
    check()
    models()
    loot()
    recipes()
    advancements()
    sounds_and_tags()
    w(ASSETS / "lang/en_us.json", lang())
    print("Driftwrecks data written under", RES.relative_to(ROOT))


if __name__ == "__main__":
    main()
