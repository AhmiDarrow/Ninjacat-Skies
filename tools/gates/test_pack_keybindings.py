"""Validate the pack preset against itself and an optional actual client key inventory."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def validate(options_path=None):
    rows = json.loads((ROOT / 'mods/ninjacatskies/src/main/resources/assets/ninjacatskies/keybindings.json').read_text(encoding='utf-8'))
    assert len({r['name'] for r in rows}) == len(rows), 'Duplicate action in preset'
    assert len({(r['key'], r['modifier']) for r in rows}) == len(rows), 'Duplicate chord in preset'
    for row in rows:
        assert row['key'].startswith('key.keyboard.') and not row['key'].endswith('unknown')
        assert row['modifier'] in {'NONE', 'CONTROL', 'ALT', 'SHIFT'}
        assert row['context'] in {'world', 'original'}
    required = {'key.ftbquests.quests', 'skyguis.key.all_teams_screen', 'key.ftbteams.open_gui', 'key.ae2.wireless_terminal'}
    assert required <= {r['name'] for r in rows}
    if options_path is not None:
        options = Path(options_path).read_text(encoding='utf-8')
        actual = {line.split(':', 1)[0][4:]: line.split(':', 1)[1] for line in options.splitlines() if line.startswith('key_')}
        missing = [r['name'] for r in rows if r['name'] not in actual]
        assert not missing, missing
        mismatches = [r['name'] for r in rows if actual[r['name']] != r['key'] + (':' + r['modifier'] if r['modifier'] != 'NONE' else '')]
        assert not mismatches, mismatches
    return len(rows)


class KeybindingTests(unittest.TestCase):
    def test_preset_is_complete_and_has_unique_chords(self):
        validate()

    def test_gear_screen_pack_default_is_numpad_minus(self):
        script = (ROOT / 'pack/overrides/kubejs/client_scripts/tribal_gear_key.js').read_text(encoding='utf-8')
        self.assertIn('key.tribalpower.gear', script)
        self.assertIn('key.keyboard.keypad.subtract', script)
        self.assertIn('isDefault()', script)
        self.assertNotIn('key.keyboard.grave.accent', script)
        controls = (ROOT / 'pack/overrides/CONTROLS.md').read_text(encoding='utf-8')
        self.assertIn('key.tribalpower.gear', controls)
        self.assertIn('Numpad minus', controls)


if __name__ == '__main__':
    count = validate(sys.argv[1] if len(sys.argv) > 1 else None)
    print(f'PASS: {count} unique shortcuts; quest, team and terminal essentials assigned.')
    if len(sys.argv) > 1:
        print('PASS: every preset binding is present and saved with its intended modifier in the live client.')
