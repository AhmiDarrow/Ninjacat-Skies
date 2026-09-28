"""Loom's End, the hub town: the shipped plan is the generator's, the ceremony stays untouched, keepers and residents
line up with the scripts that look after them, and the saddle is sold where the town says it is."""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
PLAN = ROOT / 'pack/overrides/kubejs/data/clowderhall/towns/clowder_town.json'
LANG = ROOT / 'pack/overrides/kubejs/assets/ninjacatpack/lang/en_us.json'
STALLS = ROOT / 'pack/overrides/kubejs/server_scripts/dock_stalls.js'
LIFE = ROOT / 'pack/overrides/kubejs/server_scripts/hub_life.js'
SHOP = ROOT / 'pack/overrides/kubejs/data/ninjacatskies/tribalpower/dock_shop'


def cells(box):
    (x1, y1, z1), (x2, y2, z2) = box['from'], box['to']
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            for z in range(z1, z2 + 1):
                yield x, y, z


class HubTownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(PLAN.read_text(encoding='utf-8'))
        cls.lang = json.loads(LANG.read_text(encoding='utf-8'))

    def test_plan_is_what_the_generator_writes(self):
        """Hand edits to the 30k-box plan would be lost at the next regeneration; fix the generator instead."""
        import generate_hub_towns
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'town.json'
            generate_hub_towns.clowder(str(out))
            self.assertEqual(json.loads(out.read_text()), self.plan,
                             'regenerate: python -X utf8 tools/generate_hub_towns.py clowder ' + PLAN.relative_to(ROOT).as_posix()
                             + ' --lang ' + LANG.relative_to(ROOT).as_posix())

    def test_revision_and_bounds(self):
        self.assertEqual(self.plan['revision'], 2, 'a new town revision needs its marker below 0,59,0 in ModDimensions')
        for box in self.plan['boxes']:
            f, t = box['from'], box['to']
            self.assertTrue(-160 <= f[0] <= t[0] <= 160 and -160 <= f[2] <= t[2] <= 160 and 0 <= f[1] <= t[1] <= 128, box)

    def test_ceremony_cells_are_never_written(self):
        keep = {tuple(k) for k in self.plan['keep']}
        for need in [(0, 62, 0), (0, 59, 0), (0, 64, 1), (1, 64, 1), (0, 65, -4)]:
            self.assertIn(need, keep)
        written = set()
        for box in self.plan['boxes']:
            written.update(cells(box))
        self.assertFalse(written & keep, sorted(written & keep)[:5])

    def test_arrival_is_clear(self):
        solid = {}
        for box in self.plan['boxes']:
            for c in cells(box):
                solid[c] = box['block']
        for y in (64, 65, 66):
            self.assertIn(solid.get((0, y, 5), 'minecraft:air'), ('minecraft:air',), f'arrival blocked at y {y}')

    def test_keeper_posts_match_the_stall_script(self):
        js = STALLS.read_text(encoding='utf-8')
        block = js[js.index('const HUB_POSTS = {'):]
        block = block[:block.index('}')]
        posts = {m.group(1): [int(m.group(i)) for i in range(2, 6)]
                 for m in re.finditer(r'(\w+): \[(-?\d+), (-?\d+), (-?\d+), (-?\d+),', block)}
        self.assertEqual(posts, self.plan['posts'])

    def test_every_sign_and_message_has_english(self):
        for sign in self.plan['signs']:
            for line in sign['lines']:
                if line:
                    self.assertIn(line, self.lang, sign)
        for key in re.findall(r"'(message\.ninjacatpack\.hub\.\w+)'", LIFE.read_text(encoding='utf-8')):
            self.assertIn(key, self.lang)

    def test_one_bed_per_townsperson(self):
        """A villager with a spare bed breeds; the town's crowd must stay the size it was built."""
        heads = sum(1 for box in self.plan['boxes'] if re.match(r'minecraft:\w+_bed\[.*part=head', box['block'])
                    for _ in cells(box))
        folk = [r for r in self.plan['residents'] if r['type'] == 'minecraft:villager']
        self.assertEqual(heads, len(folk))
        names = [r['name'] for r in self.plan['residents']]
        self.assertEqual(len(names), len(set(names)), 'residents are found again by name')
        for r in self.plan['residents']:
            if r['type'] == 'minecraft:villager':
                self.assertIn('Offers:{Recipes:[]}', r['nbt'], f"{r['name']} must have nothing to sell")

    def test_sunfeather_is_the_halls(self):
        bird = [r for r in self.plan['residents'] if r['name'] == 'Sunfeather']
        self.assertEqual(len(bird), 1)
        self.assertEqual(bird[0]['type'], 'chocobosreborn:chocobo')
        self.assertIn('Plumage:5', bird[0]['nbt'])
        self.assertIn('TownBird:1b', bird[0]['nbt'], 'a town bird cannot be tamed, leashed or despawned')
        self.assertIn('ncs_hub_sunfeather', bird[0]['tags'])

    def test_the_pad_keepers_sell_the_saddle(self):
        listing = json.loads((SHOP / 'padkeepers_saddle.json').read_text(encoding='utf-8'))
        self.assertEqual(listing['stall'], 'padkeepers')
        self.assertEqual(listing['cost'], {'id': 'minecraft:diamond_block', 'count': 1})
        self.assertEqual(listing['result'], {'id': 'minecraft:saddle', 'count': 1})
        shown = [f for f in self.plan['frames'] if f['item'] == 'minecraft:saddle']
        self.assertGreaterEqual(len(shown), 3, 'the saddles hang on the Pad-keepers back wall')

    def test_core_ships_no_town(self):
        """The town is the pack's: Core without it raises only the ceremony pad."""
        self.assertFalse((ROOT / 'mods/clowderhall/src/main/resources/data/clowderhall/towns').exists())


if __name__ == '__main__':
    unittest.main()
