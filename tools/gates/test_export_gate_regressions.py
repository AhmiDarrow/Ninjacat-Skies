import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from test_export_archive import verify


class ExportGateTests(unittest.TestCase):
    def test_archive_contents(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"sample.zip"
            for extra in ["../escape", "overrides/INTERNAL/private.txt", "overrides/.env", "overrides/run.ps1"]:
                with zipfile.ZipFile(path,"w") as z:
                    z.writestr("manifest.json",json.dumps({"manifestType":"minecraftModpack","overrides":"overrides"}))
                    z.writestr(extra,"bad")
                with self.assertRaises(ValueError): verify(path)
            with zipfile.ZipFile(path,"w") as z:
                z.writestr("manifest.json",json.dumps({"manifestType":"minecraftModpack","overrides":"overrides","image":"profileImage/logo.png"}))
                z.writestr("overrides/config/ok.json","{}")
                z.writestr("profileImage/logo.png", b"\x89PNG\r\n\x1a\n")
            verify(path)

    def test_import_branding_requires_manifest_reference_and_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "branding.zip"
            for image in [None, "profileImage/missing.png"]:
                with zipfile.ZipFile(path, "w") as z:
                    z.writestr("manifest.json", json.dumps({"manifestType": "minecraftModpack", "overrides": "overrides", "image": image}))
                    z.writestr("icon.png", b"\x89PNG\r\n\x1a\n")
                with self.assertRaisesRegex(ValueError, "profile image"):
                    verify(path)

    def test_export_success_cannot_mask_prior_gate_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);gates=root/"tools"/"gates";gates.mkdir(parents=True)
            source=Path(__file__).parent
            shutil.copyfile(source/"Invoke-AllGates.ps1",gates/"Invoke-AllGates.ps1")
            for name in ["SanitizedPublicSurface","PackStructure","QuestConsistency","QuestItemIds","CustomModsBuild","SmokeHarness"]:
                (gates/f"Test-{name}.ps1").write_text("exit 1" if name=="PackStructure" else "exit 0")
            (root/"tools"/"export-curseforge.ps1").write_text("exit 0")
            (gates/"test_export_archive.py").write_text("print('PASS stub export verification')")
            result=subprocess.run(["pwsh","-NoProfile","-File",str(gates/"Invoke-AllGates.ps1"),"-WithExportDryRun"],capture_output=True,text=True)
            self.assertEqual(result.returncode,1,result.stdout+result.stderr)
            self.assertIn("RESULT: 1 gate(s) failed",result.stdout)
            self.assertIn("PASS stub export verification",result.stdout)


if __name__=="__main__": unittest.main()
