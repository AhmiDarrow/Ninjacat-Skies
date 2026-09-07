"""Keep campaign lives scarce and shared when regenerating quests."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]

class LifeRewardTests(unittest.TestCase):
    def test_exactly_six_late_team_rewards(self):
        chapters = ROOT / "pack/overrides/config/ftbquests/quests/chapters"
        found = []
        for path in chapters.glob("*.snbt"):
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r'command: "skybound rewardlife @s (\w+)"', text):
                found.append((path.stem, match.group(1)))
                reward = text[match.start():text.index("}", match.end())]
                self.assertIn("team_reward: true", reward)
                self.assertIn("elevate_perms: true", reward)
                self.assertNotIn("repeatable: true", text)
        self.assertEqual(sorted(found), [("06_clock", "clock"), ("08_sigil", "sigil"), ("09_spindle", "reweave"), ("23_end", "dragon"), ("32_qio", "power"), ("34_tribal", "bestiary")])

if __name__ == "__main__":
    unittest.main()
