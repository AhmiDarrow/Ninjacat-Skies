"""Shipped Core config must list every key the spec defines, or NeoForge rewrites it and leaves a .bak on first launch."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / 'mods/ninjacatskies/src/main/java/com/ninjacat/skies/core/config/SkiesConfig.java'
SHIPPED = ROOT / 'pack/overrides/config/ninjacatskies-common.toml'


def spec_keys():
    keys, path = set(), []
    for token in re.finditer(r'\.(push|pop|define\w*)\("?([\w.]*)"?', SPEC.read_text(encoding='utf-8')):
        kind, name = token.groups()
        if kind == 'push':
            path.append(name)
        elif kind == 'pop':
            path.pop()
        else:
            keys.add('.'.join(path + [name]))
    return keys


def shipped_keys():
    keys, section = set(), ''
    for line in SHIPPED.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('['):
            section = line.strip('[]')
        elif '=' in line:
            keys.add(f"{section}.{line.split('=', 1)[0].strip()}")
    return keys


class ShippedConfigTests(unittest.TestCase):
    def test_core_config_is_complete(self):
        spec, shipped = spec_keys(), shipped_keys()
        self.assertTrue(spec, 'no keys parsed from SkiesConfig.java')
        self.assertEqual(sorted(spec - shipped), [], 'keys missing from the shipped config')
        self.assertEqual(sorted(shipped - spec), [], 'shipped config has keys the spec no longer defines')


if __name__ == '__main__':
    result = unittest.main(exit=False, verbosity=1).result
    sys.exit(0 if result.wasSuccessful() else 1)
