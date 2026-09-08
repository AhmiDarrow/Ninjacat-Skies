"""Reject the packaging error behind CurseForge rejection 8834868."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from cf_distribution import manifest_entries, is_owned_jar
from test_export_archive import verify


class DistributionTests(unittest.TestCase):
    def test_actual_pack_has_only_four_owned_override_jars(self):
        jars = sorted((ROOT / 'pack/mods').glob('*.jar'))
        rows = json.loads((ROOT / 'pack/modlist-resolved.json').read_text(encoding='utf-8'))
        entries = manifest_entries(jars, rows)
        self.assertEqual(len(entries), 88)
        self.assertEqual(len(jars), 92)
        self.assertEqual(sum(is_owned_jar(p.name) for p in jars), 4)
        expected = {619320: 8687896, 235577: 8163135, 1684851: 8828297}
        actual = {e['projectID']: e['fileID'] for e in entries}
        for pid, fid in expected.items(): self.assertEqual(actual[pid], fid)

    def test_unresolved_and_changed_dependencies_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'third-party.jar';p.write_bytes(b'official contents')
            row = {'filename': p.name, 'projectId': 123, 'fileId': 456, 'sha1': hashlib.sha1(p.read_bytes()).hexdigest()}
            self.assertEqual(manifest_entries([p], [row])[0]['fileID'], 456)
            for rows in [[], [dict(row, fileId=0)], [dict(row, sha1='bad')], [row, row]]:
                with self.assertRaises(ValueError): manifest_entries([p], rows)
            p.write_bytes(b'changed jar')
            with self.assertRaises(ValueError): manifest_entries([p], [row])

    def test_rejected_third_party_jars_cannot_hide_in_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'bad.zip'
            for name in ['overrides/mods/sophisticatedstorage-1.21.1-1.5.91.2127.jar',
                         'overrides/mods/trashslot-neoforge-1.21.1-21.1.11.jar',
                         'overrides/mods/ae2wtlib-19.5.1.jar',
                         'overrides/mods/tribalpower-2.3.0.jar',
                         'overrides/hidden/unknown.jar']:
                with zipfile.ZipFile(p, 'w') as z:
                    z.writestr('manifest.json', json.dumps({'manifestType': 'minecraftModpack', 'overrides': 'overrides', 'image': 'icon.png'}))
                    z.writestr('icon.png', b'\x89PNG\r\n\x1a\n')
                    z.writestr(name, b'jar')
                with self.assertRaisesRegex(ValueError, 'Unapproved bundled mod'): verify(p)

    def test_old_rejected_release_fails_gate(self):
        paths = list((ROOT / 'dist').glob('NinjacatSkies-0.6.2-alpha-*.zip'))
        if not paths: self.skipTest('Historical rejected archive not retained locally')
        with self.assertRaisesRegex(ValueError, 'Unapproved bundled mod'): verify(paths[0])

if __name__ == '__main__': unittest.main()
