"""An incomplete local mod install must not silently delete released quests."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate_quests as g


class QuestPreflight(unittest.TestCase):
    def test_missing_shipped_mod_aborts_before_any_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            chapter = Path(folder) / "40_chocobo.snbt"
            original = '{ quests: [{ item: "example:missing_item" }] }'
            chapter.write_text(original)
            with patch.object(g, "CHAPTERS", Path(folder)), patch.object(g, "KNOWN", {"example:known_item"}), patch.object(g, "write_groups") as writer:
                with self.assertRaisesRegex(RuntimeError, "example:missing_item"):
                    g.main()
                writer.assert_not_called()
                self.assertEqual(chapter.read_text(), original)

    def test_complete_index_accepts_vanilla_and_mod_items(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "chapter.snbt").write_text('{ item: "example:known_item", icon: "minecraft:book" }')
            with patch.object(g, "CHAPTERS", Path(folder)), patch.object(g, "KNOWN", {"example:known_item"}):
                g.validate_shipped_items()

    def test_absent_index_fails_closed(self):
        with patch.object(g, "KNOWN", set()):
            with self.assertRaisesRegex(RuntimeError, "rebuild the item index"):
                g.validate_shipped_items()


if __name__ == "__main__":
    unittest.main()
