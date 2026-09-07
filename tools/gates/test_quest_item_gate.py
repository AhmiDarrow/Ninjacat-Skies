"""Regression checks for the PowerShell gate's handling of failed audit processes."""
import subprocess
import unittest
from pathlib import Path


GATE = Path(__file__).with_name("Test-QuestItemIds.ps1")


class QuestItemGateTests(unittest.TestCase):
    def run_gate(self, extraction_exit=0, audit_exit=0, report="quest_items=1 missing=0 dead_ends=0"):
        script = f"""
function global:python {{
    if ($args[0] -like '*extract_item_ids.py') {{
        $global:LASTEXITCODE = {extraction_exit}
    }} else {{
        Write-Output '{report}'
        $global:LASTEXITCODE = {audit_exit}
    }}
}}
& '{str(GATE).replace(chr(39), chr(39) * 2)}'
"""
        return subprocess.run(["pwsh", "-NoProfile", "-Command", script], capture_output=True, text=True)

    def test_success(self):
        self.assertEqual(self.run_gate().returncode, 0)

    def test_extraction_failure(self):
        self.assertNotEqual(self.run_gate(extraction_exit=1).returncode, 0)

    def test_audit_crash(self):
        self.assertNotEqual(self.run_gate(audit_exit=1, report="Traceback").returncode, 0)

    def test_dead_end(self):
        self.assertNotEqual(self.run_gate(audit_exit=1, report="quest_items=1 missing=0 dead_ends=1").returncode, 0)

    def test_missing_summary(self):
        self.assertNotEqual(self.run_gate(report="").returncode, 0)


if __name__ == "__main__":
    unittest.main()
