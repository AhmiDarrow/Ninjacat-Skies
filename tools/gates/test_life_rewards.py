"""Keep campaign lives scarce and shared when regenerating quests, and keep the priced life path priced."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SHOP = ROOT / "pack/overrides/kubejs/data/ninjacatskies/tribalpower/dock_shop"
THREAD = "ninjacatskies:frayed_thread"
# A trade slot holds one stack, so big prices are paid in denser Thread: a skein is 9, a bolt 9 skeins.
THREAD_VALUE = {THREAD: 1, "ninjacatskies:thread_skein": 9, "ninjacatskies:thread_bolt": 81}

# What one exchanged block is worth if you bought the same material back from a stall, so the two
# directions can be compared: (unit item sold by a stall, how many of that unit the cost block is).
EXCHANGED = {
    "grit_exchange_copper.json": ("minecraft:copper_ingot", 9),
    "grit_exchange_iron.json": ("minecraft:iron_nugget", 81),
    "grit_exchange_gold.json": ("minecraft:gold_ingot", 9),
    "grit_exchange_amethyst.json": ("minecraft:amethyst_shard", 4),
    "grit_exchange_emerald.json": ("minecraft:emerald", 9),
    "grit_exchange_diamond.json": ("minecraft:diamond", 9),
    "grit_exchange_netherite.json": (None, 1),   # no stall sells netherite, so there is nothing to loop against
}


def listings():
    return {path.name: json.loads(path.read_text(encoding="utf-8")) for path in SHOP.glob("*.json")}


def thread_cost(entry):
    """What a listing costs in Frayed Thread, or None when it is not priced in Thread."""
    unit = THREAD_VALUE.get(entry["cost"]["id"])
    return None if unit is None else unit * entry["cost"]["count"]


class LifeRewardTests(unittest.TestCase):
    def test_exactly_six_late_team_rewards(self):
        chapters = ROOT / "pack/overrides/config/ftbquests/quests/chapters"
        found = []
        for path in chapters.glob("*.snbt"):
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r'command: "skybound rewardlife @s (\w+)"', text):
                found.append((path.stem, match.group(1)))
                reward = text[match.start():text.index("}", match.end())]
                self.assertIn("team_reward: true", reward)
                self.assertIn("elevate_perms: true", reward)
                self.assertNotIn("repeatable: true", text)
        self.assertEqual(sorted(found), [("06_clock", "clock"), ("08_sigil", "sigil"), ("09_spindle", "reweave"), ("23_end", "dragon"), ("32_qio", "power"), ("34_tribal", "bestiary")])

    def test_only_the_item_grants_a_repeatable_life(self):
        """award() keeps a milestone receipt; grant() is the repeatable one and must stay item-only."""
        lives = (ROOT / "mods/ninjacatskies/src/main/java/com/ninjacat/skies/core/tension/ClowderLives.java").read_text(encoding="utf-8")
        body = lives[lives.index("public static boolean grant("):]
        self.assertNotIn("life_reward_", body[:body.index("\n    }")], "a repeatable grant must not write a milestone receipt")
        self.assertIn("if (!grant(team, startingLives)) return false;", lives, "award() must go through grant()")
        callers = set()
        for path in (ROOT / "mods").rglob("*.java"):
            if "/build/" in path.as_posix() or path.name in ("ClowderLives.java", "LivesGameTests.java"):
                continue
            if "ClowderLives.grant(" in path.read_text(encoding="utf-8"):
                callers.add(path.name)
        self.assertEqual(callers, {"SkyboundEvents.java"}, "only the Thread of Return path may grant a repeatable life")

    def test_a_life_costs_four_shards_and_a_shard_is_not_cheap(self):
        recipe = json.loads((ROOT / "mods/ninjacatskies/src/main/resources/data/ninjacatskies/recipe/thread_of_return.json").read_text(encoding="utf-8"))
        self.assertEqual("".join(recipe["pattern"]).count("S"), 4)
        self.assertEqual(recipe["key"]["S"]["item"], "ninjacatskies:thread_shard")
        self.assertEqual(recipe["result"]["count"], 1)

        shard = listings()["spark_thread_shard.json"]
        self.assertIsNotNone(thread_cost(shard), "the shard is priced in Thread")
        self.assertEqual(shard["result"], {"id": "ninjacatskies:thread_shard", "count": 1})
        self.assertGreaterEqual(thread_cost(shard), 300, "a bought life must stay in nether-star territory")
        self.assertLessEqual(shard["max_uses"], 4, "stall stock restocks daily; more than 4 is a life a day")

        craft = (ROOT / "pack/overrides/kubejs/server_scripts/lives.js").read_text(encoding="utf-8")
        self.assertIn("driftwrecks:rift_shard", craft, "the craft path must stay gated behind a mended Remnant")
        self.assertIn("ninjacatskies:thread_shard", craft)

    def test_every_stall_price_fits_one_stack(self):
        """The trade screen clamps a price to one stack: 400 Thread silently charged 64 until 0.8.9."""
        for name, entry in listings().items():
            with self.subTest(name):
                self.assertLessEqual(entry["cost"]["count"], 64, "price it in skeins or bolts instead")
                self.assertLessEqual(entry["result"]["count"], 64)

    def test_turning_resources_into_thread_never_pays(self):
        """Grit buys materials back for Thread; every rate must stay far under what a stall sells them for."""
        shop = listings()
        sell = {}   # item -> cheapest Thread per unit across the stalls
        for entry in shop.values():
            if thread_cost(entry) is None:
                continue
            per = thread_cost(entry) / entry["result"]["count"]
            item = entry["result"]["id"]
            sell[item] = min(sell.get(item, per), per)

        self.assertEqual(set(EXCHANGED), {n for n in shop if n.startswith("grit_exchange_")},
                         "a new exchange listing needs a loop check here")
        for name, (unit, count) in EXCHANGED.items():
            entry = shop[name]
            with self.subTest(name):
                self.assertEqual(entry["stall"], "grit")
                self.assertEqual(entry["cost"]["count"], 1)
                self.assertEqual(entry["result"]["id"], THREAD)
                paid = entry["result"]["count"]
                if unit is None:
                    self.assertNotIn(entry["cost"]["id"], sell, "this one is priced as unbuyable")
                    continue
                buy_back = sell[unit] * count
                self.assertGreaterEqual(buy_back, paid * 8,
                                        f"{name}: {paid} Thread for materials worth {buy_back} is close to a loop")


if __name__ == "__main__":
    unittest.main()
