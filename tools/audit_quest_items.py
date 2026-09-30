#!/usr/bin/env python3
"""Quest item audit: every task/reward item must exist, and no non-optional quest may ask for something the
void world cannot produce. Exit code 1 on any failure so the gates can call it."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
known = set((ROOT / "INTERNAL/known_item_ids.txt").read_text(encoding="utf-8").split())

# Loot-only / structure-only / mob-only items with no pack recipe, sieve drop, or seed. Keep in sync with
# generate_quests.py REMOVE_ITEMS / FORCE_OPTIONAL. Anything here on a non-optional quest is a dead end.
UNREACHABLE = {
    "minecraft:heart_of_the_sea",     # buried treasure only
    "minecraft:recovery_compass",     # echo shards: ancient city (crushed end stone + netherite mesh is the only out)
    "minecraft:elytra",               # end cities — custom End keeps the main island only
    "minecraft:rabbit_hide",          # no rabbits
    "minecraft:turtle_helmet",        # no turtles
    "minecraft:wolf_armor",           # no armadillos
    "minecraft:sponge",               # ocean monuments
    "minecraft:music_disc_cat",       # dungeon chests / creeper luck
    "pipez:infinity_upgrade",         # creative-only: Pipez ships no survival recipe
    "productivebees:sturdy_bee_cage", # village chests / hero-of-the-village gifts only
}
# Structure/raid-only items the pack makes craftable in kubejs/server_scripts/quest_reachability.js. Each must keep
# its recipe there, stay off UNREACHABLE, and every quest asking for it must name the pack recipe in its How line.
PACK_CRAFTED = {
    "minecraft:shulker_shell",        # Packaged Auto Distributor / Crafting Proxy
    "minecraft:totem_of_undying",     # Ars Nouveau Archmage Spell Book
    "irons_spellbooks:ruined_book",   # Iron's Spells Ancient Codex (netherite book)
    "irons_spellbooks:magehunter",    # Magehunter Vindicators spawn in evoker forts only
}
REACH_JS = (ROOT / "pack/overrides/kubejs/server_scripts/quest_reachability.js").read_text(encoding="utf-8")

CHAPTERS = ROOT / "pack/overrides/config/ftbquests/quests/chapters"
LANG = (ROOT / "pack/overrides/config/ftbquests/quests/lang/en_us.snbt").read_text(encoding="utf-8")
titles = dict(re.findall(r'quest\.([0-9A-F]+)\.title: "(.*?)"', LANG))

text = ""
for p in (ROOT / "pack/overrides/config/ftbquests").rglob("*.snbt"):
    text += p.read_text(encoding="utf-8") + "\n"
items = sorted(set(re.findall(r'id: "([a-z0-9_]+:[a-z0-9_/]+)"', text)))
# reward-table loot_table_id values are vanilla loot tables, not items
items = [i for i in items if not i.startswith("ninjacatskies:steward_cache/")]



def ok(i: str) -> bool:
    return i.startswith("minecraft:") or i in known


miss = [i for i in items if not ok(i)]
dead = []
unnamed = []
for chapter in sorted(CHAPTERS.glob("*.snbt")):
    body = chapter.read_text(encoding="utf-8")
    for quest in re.split(r"\n\t\t\{\n", body)[1:]:
        qid = re.search(r'id: "([0-9A-F]+)"', quest)
        task = re.search(r'tasks: \[.*?item: \{\n\t*id: "([^"]+)"', quest, re.S)
        if not qid or not task:
            continue
        if task.group(1) in UNREACHABLE and "optional: true" not in quest:
            dead.append((chapter.name, titles.get(qid.group(1), qid.group(1)), task.group(1)))
        if task.group(1) in PACK_CRAFTED:
            desc = re.search(r"quest\." + qid.group(1) + r"\.quest_desc: \[(.*?)\n\t\]", LANG, re.S)
            if not desc or "pack recipe" not in desc.group(1):
                unnamed.append((chapter.name, titles.get(qid.group(1), qid.group(1)), task.group(1)))

lost = sorted(i for i in PACK_CRAFTED if f"event.shaped('{i}'" not in REACH_JS or i in UNREACHABLE)
print(f"quest_items={len(items)} missing={len(miss)} dead_ends={len(dead)} pack_crafted_lost={len(lost)} "
      f"how_without_pack_recipe={len(unnamed)}")
for i in miss:
    print("MISS", i)
for chapter, title, item in dead:
    print("DEAD", chapter, title, item)
for i in lost:
    print("LOST", i, "has no shaped recipe in quest_reachability.js (or is back on UNREACHABLE)")
for chapter, title, item in unnamed:
    print("HOW", chapter, title, item, "- How line does not name the pack recipe")
sys.exit(1 if (miss or dead or lost or unnamed) else 0)
