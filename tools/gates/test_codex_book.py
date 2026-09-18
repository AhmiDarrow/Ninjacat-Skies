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
        tips = (ROOT/'pack/overrides/kubejs/client_scripts/voidloom_tooltips.js').read_text(encoding='utf-8')
        controls = (ROOT/'pack/overrides/CONTROLS.md').read_text(encoding='utf-8')
        self.assertNotIn('story and what to do', tips)
        self.assertNotIn('story and what to do', controls)
        self.assertIn('Start here', controls)
        welcome = (ROOT/'pack/overrides/config/fancymenu/customization/ninjacat_skies_welcome_layout.txt').read_text(encoding='utf-8')
        self.assertNotIn('Open FTB Quests', welcome)
        self.assertIn('Start here', welcome)
        import gzip
        islands = ROOT/'pack/overrides/config/skyblockbuilder/templates/islands'
        for path in islands.glob('*.nbt'):
            text = gzip.decompress(path.read_bytes()).decode('latin1')
            self.assertNotIn('Open FTB Quests', text, path.name)
            self.assertNotIn('press C', text, path.name)
            self.assertIn('Start here', text, path.name)
        quests = (ROOT/'pack/overrides/config/ftbquests/quests/lang/en_us.snbt').read_text(encoding='utf-8')
        self.assertNotIn('Shift + right-click', quests)
        self.assertIn('open Start here', quests)

    def test_beginner_lessons_and_navigation(self):
        entries={f'ninjacatskies:{p.parent.name}/{p.stem}' for p in (BOOK/'entries').glob('*/*.json')}
        paths=list((BOOK/'entries/first_steps').glob('*.json'))
        stems={p.stem for p in paths}
        self.assertEqual(stems, {
            'using_the_book','safe_start','water','first_token','materials','claw_blueprints',
            'first_power','automatic_power','hold_fluids','choose_branches','pad_runners','finish','stuck',
        })
        blob=' '.join(p.read_text(encoding='utf-8') for p in paths).lower()
        self.assertIn('silentgear:blueprint_package', blob)
        self.assertIn('tribalpower:spirit_cistern', blob)
        self.assertIn('chocobosreborn:sage_notes', blob)
        self.assertIn('esther', blob)
        self.assertIn('sky stone', blob)
        self.assertIn('no spawn-egg shortcut', blob)
        self.assertIn('/clowder hub', blob)
        self.assertIn('thread of return', blob)
        self.assertIn('oak sieve', blob)
        self.assertIn('empty-handed use', blob)
        self.assertIn('do not strike it like a drumheart', blob)
        self.assertIn('carob', blob)
        self.assertIn('no pink or red', blob)
        self.assertNotIn('strike a **gate drum**', blob)
        self.assertNotIn('chococraft', blob)
        self.assertNotIn('chocopedia', blob)
        self.assertNotIn('recovery item', blob)
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
        self.assertEqual({p.stem for p in paths}, {
            'starter_workshop','water_pool','material_workshop','shatter_workshop','resonator_workshop','cistern_corner',
        })
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

    def test_pack_primers_match_first_steps(self):
        mapping=[('this_book','using_the_book'),('first_hour','safe_start'),
                 ('tokens','first_token'),('the_campaign','choose_branches')]
        expected_parent={'this_book':None,'first_hour':'ninjacatskies:the_work/this_book',
                         'tokens':'ninjacatskies:the_work/first_hour',
                         'the_campaign':'ninjacatskies:the_work/tokens'}
        for target,source in mapping:
            pack=json.loads((PACK/'entries/the_work'/f'{target}.json').read_text(encoding='utf-8'))
            core=json.loads((BOOK/'entries/first_steps'/f'{source}.json').read_text(encoding='utf-8'))
            self.assertEqual(pack['pages'], core['pages'], target)
            parents=[p['entry'] for p in pack.get('parents',[])]
            want=expected_parent[target]
            if want is None:
                self.assertEqual(parents, [])
            else:
                self.assertEqual(parents, [want], target)
        self.assertFalse((BOOK/'categories'/'the_work.json').exists())
        titles=[]
        for p in (BOOK/'entries').glob('*/*.json'):
            titles += [page.get('title','') for page in json.loads(p.read_text(encoding='utf-8'))['pages']]
        self.assertFalse(any('...' in t for t in titles), [t for t in titles if '...' in t])

    def test_braid_stage_checks_are_single_and_specific(self):
        strand={'wake','recover','root','edge','pattern','colony','hum','bind','reweave'}
        for path in (BOOK/'entries/braid').glob('*.json'):
            titles=[p.get('title') for p in json.loads(path.read_text(encoding='utf-8'))['pages']]
            count=titles.count('Before you move on')
            if path.stem in strand:
                self.assertEqual(count, 1, path.name)
                blob=' '.join(p.get('text','') for p in json.loads(path.read_text(encoding='utf-8'))['pages'])
                self.assertIn('**Goal:**', blob, path.name)
                self.assertIn('You need', blob, path.name)
                self.assertIn('**Check:**', blob, path.name)
            else:
                self.assertEqual(count, 0, path.name)
        pit=json.loads((BOOK/'entries/braid/listening_pit.json').read_text(encoding='utf-8'))
        blob=' '.join(p.get('text','') for p in pit['pages'])
        self.assertIn('Spirit Codex', blob)
        self.assertIn('empty-handed use', blob.lower())
        self.assertNotIn('seat its Strand token', blob)
        self.assertNotIn('Earth is the Drumheart', blob)
        lattice=json.loads((BOOK/'entries/braid/living_lattice.json').read_text(encoding='utf-8'))
        lattice_blob=' '.join(p.get('text','') for p in lattice['pages'])
        self.assertIn('Spirit Codex', lattice_blob)
        self.assertNotIn('Feed slot 0', lattice_blob)
        edge=json.loads((BOOK/'entries/braid/edge.json').read_text(encoding='utf-8'))
        self.assertIn('Blueprint Package', ' '.join(p.get('text','') for p in edge['pages']))
        workshop=json.loads((BOOK.parents[1]/'multiblocks/codex/starter_workshop.json').read_text(encoding='utf-8'))
        self.assertEqual(workshop['mapping']['0']['block'], 'minecraft:crafting_table')
        materials=json.loads((BOOK.parents[1]/'multiblocks/codex/material_workshop.json').read_text(encoding='utf-8'))
        self.assertIn('exdeorum:oak_sieve', {v['block'] for v in materials['mapping'].values()})

    def test_cut_station_pages_have_goal_need_check(self):
        for stem in ('voidloom', 'tension', 'thread'):
            pages=json.loads((BOOK/'entries/the_cut'/f'{stem}.json').read_text(encoding='utf-8'))['pages']
            blob=' '.join(p.get('text','') for p in pages)
            self.assertIn('**Goal:**', blob, stem)
            self.assertIn('You need', blob, stem)
            self.assertIn('**Check:**', blob, stem)

    def test_guardians_walkthroughs_have_goal_need_check(self):
        ritual=json.loads((BOOK/'entries/guardians/the_ritual.json').read_text(encoding='utf-8'))
        blob=' '.join(p.get('text','') for p in ritual['pages'])
        self.assertIn('**Goal:**', blob)
        self.assertIn('You need', blob)
        self.assertIn('**Check:**', blob)
        self.assertIn('purpur', blob.lower())
        bed=json.loads((BOOK/'entries/guardians/beddown.json').read_text(encoding='utf-8'))
        bblob=' '.join(p.get('text','') for p in bed['pages'])
        self.assertIn('**Goal:**', bblob)
        self.assertIn('You need', bblob)
        self.assertIn('**Check:**', bblob)

if __name__=='__main__':unittest.main()
