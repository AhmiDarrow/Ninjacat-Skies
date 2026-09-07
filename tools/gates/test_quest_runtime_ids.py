"""Regression coverage for the signed-long parser used by FTB Quests 2101.1.x."""
import re
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import generate_quests as generator

class RuntimeQuestIds(unittest.TestCase):
    def test_unicode_is_literal_utf8_for_ftb_snbt(self):
        self.assertEqual(generator.to_snbt('Rhythm — Pulse'), '"Rhythm — Pulse"')
        text = (ROOT/'pack/overrides/config/ftbquests/quests/lang/en_us.snbt').read_text(encoding='utf-8')
        self.assertNotRegex(text, r'\\u[0-9a-fA-F]{4}', 'FTB SNBT does not decode JSON Unicode escapes')

    def test_quest_text_has_no_unescaped_literal_ampersands(self):
        text = (ROOT/'pack/overrides/config/ftbquests/quests/lang/en_us.snbt').read_text(encoding='utf-8')
        self.assertIsNone(re.search(r'(?<!\\)&\s', text), 'FTB text treats bare ampersands as formatting commands')

    def test_generated_id_fits_java_signed_long(self):
        self.assertEqual(generator.hid(0xB100000000000022),'3100000000000022')
        self.assertTrue(0<int(generator.hid(0xFFFFFFFFFFFFFFFF),16)<=0x7FFFFFFFFFFFFFFF)

    def test_shipped_ids_are_unique_and_references_resolve(self):
        folder=ROOT/'pack/overrides/config/ftbquests/quests'
        definitions=[];references=[]
        for path in folder.rglob('*.snbt'):
            text=path.read_text(encoding='utf-8')
            definitions += re.findall(r'(?<![\w.])id:\s*"([0-9A-F]{16})"',text)
            for dep in re.findall(r'dependencies:\s*\[([^\]]*)\]',text):
                references+=re.findall(r'"([0-9A-F]{16})"',dep)
            references+=re.findall(r'(?:group|table_id):\s*"([0-9A-F]{16})"',text)
        self.assertGreater(len(definitions),4000)
        self.assertEqual(len(definitions),len(set(definitions)), 'Duplicate quest objects break reference resolution')
        self.assertTrue(all(0<int(i,16)<=0x7FFFFFFFFFFFFFFF for i in definitions),'FTB regenerates invalid IDs silently')
        self.assertFalse(set(references)-set(definitions),'A dependency references a missing object')

if __name__=='__main__':unittest.main()
