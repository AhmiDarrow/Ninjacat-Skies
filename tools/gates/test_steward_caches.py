"""Reward balance, recipe safety, and 0.6.1 quest-save identity regression checks."""
import hashlib
import json
import re
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import generate_quests as g
RES = ROOT / 'mods/ninjacatskies/src/main/resources'
TIERS = ('small', 'medium', 'large')

class StewardCaches(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = []
        g.write_groups = lambda: None
        g.write_reward_tables = lambda: None
        g.write_lang = lambda: None
        def capture(filename, cid, group, order, icon, quests, title):
            cls.rows.extend((filename, q) for q in g.finalize_chapter(order + 1, list(quests) + g.secret_quest(order + 1, -3, -2)))
        g.write_chapter = capture
        # Test authored quest identity independently of the locally installed
        # jars. QuestItemIds remains responsible for distribution completeness.
        fixture_items = set(g.KNOWN)
        for chapter in g.CHAPTERS.glob('*.snbt'):
            fixture_items.update(re.findall(r'(?:id|item):\s*"([a-z0-9_]+:[a-z0-9_/.-]+)"', chapter.read_text(encoding='utf-8')))
        with patch.object(g, 'KNOWN', fixture_items):
            g.main()

    @staticmethod
    def _added_after_0_6_1(oid: str) -> bool:
        """Quests appended since the 0.6.1 baseline: chapter 39 (Snapped Guardians) and any per-chapter late block (0x8000+)."""
        n = int(oid, 16)
        return ((n >> 16) & 0xFF) >= 0x27 or (n & 0xFFFF) >= 0x8000

    def test_existing_save_ids_preserved(self):
        ids = sorted(o['id'] for _, q in self.rows for o in [q] + q.get('tasks', []) + q.get('rewards', [])
                     if not o.get('item', {}).get('id', '').endswith('_steward_cache'))
        baseline = [i for i in ids if not self._added_after_0_6_1(i)]
        # The retired shop is absent by design, but its original allocation is
        # preserved. Fixture extracted from the pre-retirement bbe56fa chapter.
        baseline += json.loads(Path(__file__).with_name('retired-shop-ids.json').read_text())
        baseline.sort()
        # every id a 0.6.1 save knows is still there, unchanged
        self.assertEqual(hashlib.sha256('\n'.join(baseline).encode()).hexdigest(), '2c67f856be36222231dee7c0b46a6a4a4dd7bc4247722aad963aa70e5a4abb43')
        self.assertEqual(len([r for r in self.rows if not self._added_after_0_6_1(r[1]['id'])]), 1495 - 30)
        # Shop retired (−30). Then Guardians, Pad-runners, Harvest Table, Crop Sticks, Driftwrecks (+15), End Apple (+1).
        self.assertEqual(len(self.rows), 1651)

    def test_all_generated_quests_keep_their_shipped_ids(self):
        for chapter, q in self.rows:
            shipped = (g.CHAPTERS / (chapter + '.snbt')).read_text(encoding='utf-8')
            self.assertIn(q['id'], shipped, chapter)

    def test_distribution_preserves_threads_and_excludes_repeatable_shop(self):
        caches = {t: 0 for t in TIERS}
        threads = 0
        for chapter, q in self.rows:
            rewards = q.get('rewards', [])
            if chapter != '40_chocobo':
                threads += any(r.get('item', {}).get('id') == 'ninjacatskies:frayed_thread' for r in rewards)
            for r in rewards:
                for tier in TIERS:
                    if r.get('item', {}).get('id') == f'ninjacatskies:{tier}_steward_cache':
                        caches[tier] += 1
                        self.assertNotEqual(chapter, '16_shop')
                        self.assertFalse(q.get('repeatable'))
                        self.assertEqual(r['item']['count'], 1)
        self.assertEqual(threads, 1537)   # +1: the End Apple quest, which takes no cache
        self.assertTrue(350 <= sum(caches.values()) <= 550, caches)
        self.assertGreater(caches['small'], caches['medium'])
        self.assertGreater(caches['medium'], caches['large'])
        self.assertGreater(caches['large'], 0)
        print('Cache rewards:', caches)

    def test_supplies_are_bounded_and_cannot_recurse_or_skip_progression(self):
        allowed = set('bread torch bone_meal string clay_ball oak_sapling wheat_seeds leather copper_ingot iron_nugget flower_pot cooked_beef iron_ingot gold_ingot lantern book honeycomb experience_bottle redstone lapis_lazuli diamond emerald ender_pearl obsidian'.split())
        allowed = {'minecraft:' + i for i in allowed} | {'ninjacatskies:frayed_thread', 'ninjacatskies:thread_skein'}
        rare_odds = []
        for tier, rolls in zip(TIERS, (2, 5, 12)):
            data = json.loads((RES / f'data/ninjacatskies/loot_table/provisions/{tier}.json').read_text())
            self.assertEqual(data['type'], 'minecraft:gift')
            self.assertEqual(len(data['pools']), 2, 'supplies, then one rare draw')
            pool, rare = data['pools']
            self.assertEqual(pool['rolls'], rolls)
            for e in pool['entries']:
                self.assertIn(e['name'], allowed)
                self.assertGreater(e['weight'], 0)
                count = e['functions'][0]['count']
                self.assertTrue(1 <= count['min'] <= count['max'] <= 12)
            # The rare draw is the only way a cache touches a life: a Thread Shard, or very rarely a whole Thread of Return.
            self.assertEqual(rare['rolls'], 1)
            weights = {e.get('name', e['type']): e['weight'] for e in rare['entries']}
            self.assertEqual(set(weights), {'minecraft:empty', 'ninjacatskies:thread_shard', 'ninjacatskies:thread_of_return'})
            total = sum(weights.values())
            shard, whole = weights['ninjacatskies:thread_shard'] / total, weights['ninjacatskies:thread_of_return'] / total
            self.assertTrue(0 < whole < shard <= 0.12, (tier, shard, whole))
            self.assertLessEqual(whole, 0.015, 'a whole life stays a very long shot')
            rare_odds.append((shard, whole))
        self.assertEqual(rare_odds, sorted(rare_odds), 'a bigger seal never has worse odds')

    def test_combining_only_consumes_sealed_caches(self):
        for source, dest, count in [('small', 'medium', 4), ('medium', 'large', 3)]:
            recipe = json.loads((RES / f'data/ninjacatskies/recipe/{dest}_steward_cache.json').read_text())
            self.assertEqual(recipe['ingredients'], [{'item': f'ninjacatskies:{source}_steward_cache'}] * count)
            self.assertEqual(recipe['result'], {'id': f'ninjacatskies:{dest}_steward_cache', 'count': 1})

if __name__ == '__main__':
    unittest.main()
