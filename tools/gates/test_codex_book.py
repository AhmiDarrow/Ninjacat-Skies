"""Regression checks for practical book navigation and native placement models."""
import json
from pathlib import Path
import unittest
import sys

ROOT = Path(__file__).resolve().parents[2]
BOOK = ROOT/'mods/ninjacatskies/src/main/resources/data/ninjacatskies/modonomicon/books/whisker_codex'
PACK = ROOT/'pack/overrides/kubejs/data/ninjacatskies/modonomicon/books/whisker_codex'

class CodexBookTests(unittest.TestCase):
    def test_pagination_preserves_conditions_and_is_repeatable(self):
        sys.path.insert(0,str(ROOT/'tools'))
        from whisker_lessons import paginate_pages
        condition={'type':'modonomicon:false'}
        source=[{'type':'modonomicon:spotlight','title':'A long teaching title that should fit',
                 'item':{'item':'minecraft:stone'},'condition':condition,
                 'anchor':'lesson','text':'\n\n'.join(['Read this sentence before the next step.']*16)}]
        pages=paginate_pages(source)
        self.assertGreater(len(pages),1)
        self.assertTrue(all(p['condition']==condition for p in pages))
        self.assertEqual(pages[0]['anchor'],'lesson')
        self.assertTrue(all(len(p['title'])<=22 for p in pages))
        self.assertIn('\\\n',pages[0]['text'])
        self.assertEqual(pages,paginate_pages(pages))
        empty={'type':'modonomicon:text','text':'','anchor':'empty'}
        self.assertEqual([empty],paginate_pages([empty]))

    def test_pack_categories_have_unique_sort_and_start_here_leads(self):
        sorts = {}
        for path in (PACK / 'categories').glob('*.json'):
            sorts[path.stem] = json.loads(path.read_text(encoding='utf-8'))['sort_number']
        self.assertEqual(sorts.get('first_steps'), 0)
        self.assertEqual(sorts.get('the_work'), 6)
        self.assertEqual(len(sorts), len(set(sorts.values())), sorts)
        overlay = json.loads((PACK / 'book.json').read_text(encoding='utf-8'))
        core = json.loads((BOOK / 'book.json').read_text(encoding='utf-8'))
        self.assertEqual(overlay['name'], core['name'])
        self.assertEqual(overlay['tooltip'], core['tooltip'])
        self.assertEqual(overlay['description'], core['description'])

    def test_codex_item_tooltip_points_at_start_here(self):
        core = json.loads((ROOT/'mods/ninjacatskies/src/main/resources/assets/ninjacatskies/lang/en_us.json').read_text(encoding='utf-8'))
        pack = json.loads((ROOT/'pack/overrides/kubejs/assets/ninjacatskies/lang/en_us.json').read_text(encoding='utf-8'))
        for key in ('tooltip.ninjacatskies.codex.book', 'tooltip.ninjacatskies.codex.quests'):
            self.assertIn('Start here', core[key], key)
            self.assertNotIn('story and what to do', core[key].lower())
            self.assertEqual(core[key], pack[key], key)

    def test_beginner_lessons_and_navigation(self):
        entries={f'ninjacatskies:{p.parent.name}/{p.stem}' for p in (BOOK/'entries').glob('*/*.json')}
        paths=list((BOOK/'entries/first_steps').glob('*.json'))
        self.assertEqual(len(paths),10)
        for p in paths:
            d=json.loads(p.read_text(encoding='utf-8'))
            self.assertFalse(d['hide_while_locked'])
            self.assertNotIn('condition',d)
            for parent in d.get('parents',[]):self.assertIn(parent['entry'],entries)
            for page in d['pages']:
                self.assertNotIn('\ufffd',page.get('text',''))
                self.assertLessEqual(len(page.get('text','').split()),120,p.name)
            self.assertEqual(d,json.loads((PACK/'entries/first_steps'/p.name).read_text(encoding='utf-8')))

    def test_models_have_one_origin_and_valid_layers(self):
        paths=list((BOOK.parents[1]/'multiblocks/codex').glob('*.json'))
        self.assertEqual(len(paths),5)
        for p in paths:
            shape=json.loads(p.read_text()); pattern=shape['pattern']
            flat=''.join(''.join(layer) for layer in pattern)
            self.assertEqual(flat.count('0'),1,p.name)
            self.assertEqual(len({len(layer) for layer in pattern}),1)
            self.assertEqual(len({len(row) for layer in pattern for row in layer}),1)
            self.assertLessEqual(set(flat),set(shape['mapping'])|{' ','_'})
            self.assertEqual(shape,json.loads((PACK.parents[1]/'multiblocks/codex'/p.name).read_text()))

    def test_every_placement_page_has_a_model(self):
        for p in (BOOK/'entries').glob('*/*.json'):
            for page in json.loads(p.read_text(encoding='utf-8'))['pages']:
                if page['type']=='modonomicon:multiblock':
                    self.assertTrue((BOOK.parents[1]/'multiblocks'/ (page['multiblock_id'].split(':')[1]+'.json')).exists())

if __name__=='__main__':unittest.main()
