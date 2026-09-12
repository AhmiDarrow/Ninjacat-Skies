#!/usr/bin/env python3
"""Void-pad reachability backstop.

The bee / Mystical Agriculture / Farmer's Delight bugs were all the same shape: a main-line quest asked for an
item whose only source is worldgen, a wild plant, or a structure — none of which exist on a void pad. The
item-id audit couldn't see it because the id was perfectly valid.

This scans every jar's datapack recipes, the Ex Deorum sieve/hammer/crucible/barrel recipes, all loot tables
(mob + chest drops), and the pack's own KubeJS additions, to build the set of items that SOMETHING can produce.
It then reports any item required by a non-optional Strand/main quest that has no producer at all — the exact
signature of a void-blocked root.

Mods that register their recipes in code rather than JSON (Create, Mekanism, AE2 crystal growth, Solar Flux,
Botany Pots, Productive Bees, the magic mods, Tribal Power's Song Bench, Silent Gear's material system) are
allowlisted by namespace, since a static scan can't see their outputs. Exit 1 if anything real is flagged.

Run:  python tools/check_reachability.py [path/to/pack/mods]
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "pack/mods"
QUESTS = ROOT / "pack/overrides/config/ftbquests/quests"
KUBEJS = ROOT / "pack/overrides/kubejs"

# Namespaces whose progression is added in code / by processes a static scan cannot see. Their items are
# assumed reachable; each was reviewed by hand (see INTERNAL/REVIEW notes).
CODEGEN_NAMESPACES = {
    "create", "mekanism", "mekanismtools", "ae2", "solarflux", "botanypots", "productivebees",
    "naturesaura", "occultism", "ars_nouveau", "irons_spellbooks", "silentgear", "powah", "tribalpower",
    "sophisticatedbackpacks", "sophisticatedcore", "functionalstorage", "pipez", "packagedauto",
    "mysticalagriculture", "mysticalagradditions",
    "exdeorum",  # the skyblock sieve mod itself — fluids are bucket-filled, all items reachable by design
}
# Main Strand chapters — the spine. Side chapters (10+) are allowed to reference optional/aspirational items.
MAIN_CHAPTERS = {f"{i:02d}" for i in range(1, 10)}

PRIMITIVES_MC_OK = True  # trust minecraft: items unless in the worldgen/mob denylist below

# minecraft items that DON'T exist on a void pad without a pack bootstrap (kept in sync with audit denylist).
MC_UNREACHABLE = {
    "minecraft:heart_of_the_sea", "minecraft:recovery_compass", "minecraft:elytra", "minecraft:rabbit_hide",
    "minecraft:turtle_helmet", "minecraft:wolf_armor", "minecraft:sponge", "minecraft:music_disc_cat",
    "minecraft:totem_of_undying", "minecraft:trident", "minecraft:nautilus_shell",
}


def result_ids(obj) -> list[str]:
    """Pull item ids out of any recipe/loot JSON shape."""
    out = []
    if isinstance(obj, dict):
        r = obj.get("result")
        if isinstance(r, str):
            out.append(r)
        elif isinstance(r, dict):
            rid = r.get("id") or r.get("item")
            if rid:
                out.append(rid)
        # loot tables: entries[].name for type item
        for pool in obj.get("pools", []) or []:
            for e in pool.get("entries", []) or []:
                if e.get("type") in ("minecraft:item", "item") and e.get("name"):
                    out.append(e["name"])
        # Ex Deorum sieve/hammer already covered by result; results[] (bee_spawning etc.) are entities, skip
    return out


def scan_jar(path: Path, producible: set):
    try:
        z = zipfile.ZipFile(path)
    except Exception:
        return
    for n in z.namelist():
        if not n.endswith(".json"):
            continue
        if "/recipe" in n or "/loot_table" in n or "/loot_tables" in n:
            try:
                j = json.loads(z.read(n))
            except Exception:
                continue
            for rid in result_ids(j):
                producible.add(rid)


def scan_kubejs(producible: set):
    if not KUBEJS.exists():
        return
    for p in KUBEJS.rglob("*.js"):
        t = p.read_text(encoding="utf-8", errors="ignore")
        # event.shaped('id'/"id", ...) and event.shapeless('id', ...)
        for m in re.finditer(r"event\.(?:shaped|shapeless)\(\s*['\"](\d*x?\s*)?([a-z0-9_]+:[a-z0-9_/]+)['\"]", t):
            producible.add(m.group(2))
        # event.custom({... result: {id: 'x'} ...})  and sieve result ids
        for m in re.finditer(r"result:\s*\{\s*id:\s*['\"]([a-z0-9_]+:[a-z0-9_/]+)['\"]", t):
            producible.add(m.group(1))
        # both()/sieve() helpers pass the product as the 3rd argument (id is a JS variable inside event.custom)
        for m in re.finditer(
            r"\b(?:both|sieve)\(\s*['\"][^'\"]+['\"]\s*,\s*['\"][^'\"]+['\"]\s*,\s*['\"]([a-z0-9_]+:[a-z0-9_/]+)['\"]",
            t,
        ):
            producible.add(m.group(1))
        # bee_spawning results: results: ['minecraft:bee']
        for m in re.finditer(r"results:\s*\[\s*['\"]([a-z0-9_]+:[a-z0-9_/]+)['\"]", t):
            producible.add(m.group(1))
        # explicit event.custom nest ids passed as first arg to a helper 'ring(nest, ...)'
        for m in re.finditer(r"ring\(\s*'([a-z0-9_]+:[a-z0-9_/]+)'", t):
            producible.add(m.group(1))


# Pack items that come from quest rewards, the first-join kit, or a Tension Post interaction (Java), not a recipe.
PACK_PROVIDED = {
    "ninjacatskies:whisker_codex", "ninjacatskies:frayed_thread", "ninjacatskies:codex_page",
    "ninjacatskies:braid_cord", "ninjacatskies:spindle_loom_fragment",
    "clowderhall:island_charter", "clowderhall:hub_key",
} | {f"ninjacatskies:strand_token_{s}" for s in
     ["soil", "stone", "sprout", "claw", "spark", "clock", "swarm", "sigil", "spindle"]}


def scan_quest_rewards(producible: set):
    for chapter in (QUESTS / "chapters").glob("*.snbt"):
        body = chapter.read_text(encoding="utf-8")
        for m in re.finditer(r'rewards: \[(.*?)\n\t\t\t\]', body, re.S):
            for rid in re.findall(r'item: \{\n\t*id: "([a-z0-9_]+:[a-z0-9_/]+)"', m.group(1)):
                producible.add(rid)


def scan_overrides_datapacks(producible: set):
    for base in [QUESTS.parent.parent.parent / "kubejs"]:  # noqa (kubejs handled separately)
        pass
    dp = ROOT / "pack/overrides"
    for p in dp.rglob("*.json"):
        s = str(p)
        if "/recipe" in s or "/loot_table" in s:
            try:
                j = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            for rid in result_ids(j):
                producible.add(rid)


def main() -> int:
    producible: set[str] = set()
    for jar in sorted(MODS.glob("*.jar")):
        scan_jar(jar, producible)
    scan_kubejs(producible)
    scan_overrides_datapacks(producible)
    scan_quest_rewards(producible)
    producible |= PACK_PROVIDED

    lang = (QUESTS / "lang/en_us.snbt").read_text(encoding="utf-8")
    titles = dict(re.findall(r'quest\.([0-9A-F]+)\.title: "(.*?)"', lang))

    suspects = []
    for chapter in sorted((QUESTS / "chapters").glob("*.snbt")):
        num = chapter.name[:2]
        if num not in MAIN_CHAPTERS:
            continue
        body = chapter.read_text(encoding="utf-8")
        for quest in re.split(r"\n\t\t\{\n", body)[1:]:
            if "optional: true" in quest:
                continue
            qid = re.search(r'id: "([0-9A-F]+)"', quest)
            task = re.search(r'tasks: \[.*?type: "item".*?item: \{\n\t*id: "([^"]+)"', quest, re.S)
            if not task:
                continue
            item = task.group(1)
            ns = item.split(":")[0]
            if item in producible:
                continue
            if ns == "minecraft":
                if item in MC_UNREACHABLE:
                    suspects.append((chapter.name, titles.get(qid.group(1) if qid else "", item), item, "worldgen/mob-only vanilla"))
                continue  # trust other vanilla items (craftable/mob-droppable)
            if ns in CODEGEN_NAMESPACES:
                continue  # recipes registered in code — reviewed by hand
            suspects.append((chapter.name, titles.get(qid.group(1) if qid else "", item), item, "no producer found"))

    print(f"producible items scanned: {len(producible)}")
    if suspects:
        print(f"SUSPECT main-line items with no reachable source ({len(suspects)}):")
        for ch, title, item, why in suspects:
            print(f"  {ch}  {item}  [{title}]  — {why}")
        return 1
    print("No unreachable main-line quest items found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
