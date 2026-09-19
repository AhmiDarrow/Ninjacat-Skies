#!/usr/bin/env python3
"""Gate: nothing the main line needs may come only from a Driftwreck (tools/check_reachability.py rule)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_reachability as R  # noqa: E402


class WreckOnlyRule(unittest.TestCase):
    def test_wreck_namespace_is_never_mainline(self):
        self.assertTrue(R.wreck_only("driftwrecks:salvaged_weft", set(), set()))

    def test_item_only_in_wreck_loot_is_flagged(self):
        self.assertTrue(R.wreck_only("create:precision_mechanism", set(), {"create:precision_mechanism"}))

    def test_item_with_another_source_passes(self):
        self.assertFalse(R.wreck_only("create:precision_mechanism", {"create:precision_mechanism"}, {"create:precision_mechanism"}))

    def test_vanilla_items_are_trusted(self):
        self.assertFalse(R.wreck_only("minecraft:diamond", set(), {"minecraft:diamond"}))

    def test_wreck_sources_are_scanned(self):
        sources = R.scan_wreck_sources()
        self.assertIn("driftwrecks:salvaged_weft", sources)
        self.assertIn("driftwrecks:drift_needle", sources)   # the Driftwrecks chapter reward

    def test_mainline_passes(self):
        self.assertEqual(R.main(), 0)


if __name__ == "__main__":
    unittest.main()
