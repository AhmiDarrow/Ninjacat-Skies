import json
import re
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
            # stub every gate script the runner references, so a new gate never makes this test stale:
            # only PackStructure fails, and the export must not mask it
            runner = (source/"Invoke-AllGates.ps1").read_text(encoding="utf-8")
            for name in sorted(set(re.findall(r"Test-([A-Za-z]+)\.ps1", runner))):
                (gates/f"Test-{name}.ps1").write_text("exit 1" if name=="PackStructure" else "exit 0")
            for name in sorted(set(re.findall(r"(test_[a-z_]+\.py)", runner))):
                (gates/name).write_text("raise SystemExit(0)")
            for name in sorted(set(re.findall(r"tools\\(check_[a-z_]+\.py)", runner))):
                (root/"tools"/name).write_text("raise SystemExit(0)")
            (root/"tools"/"export-curseforge.ps1").write_text("exit 0")
            (gates/"test_export_archive.py").write_text("print('PASS stub export verification')")
            result=subprocess.run(["pwsh","-NoProfile","-File",str(gates/"Invoke-AllGates.ps1"),"-WithExportDryRun"],capture_output=True,text=True)
            self.assertEqual(result.returncode,1,result.stdout+result.stderr)
            self.assertIn("RESULT: 1 gate(s) failed",result.stdout)
            self.assertIn("PASS stub export verification",result.stdout)


class ServerInstallerTests(unittest.TestCase):
    """install.sh / install.bat / install.ps1 on an update: a jar the pack installed and no longer ships moves to
    mods-removed/, a jar the operator added stays, and a rerun changes nothing. Offline: every jar is already present and
    NeoForge is faked. The environment is inherited on purpose: run from pwsh 7, it carries 7's PSModulePath, which
    install.bat must clear for Windows PowerShell 5.1."""

    def make_server(self, directory, record, newline="\n"):
        import hashlib, sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        import export_server_pack as esp
        d = Path(directory); (d/"mods").mkdir(parents=True)
        fill = lambda t: t.replace("{MC}", esp.MC).replace("{NEO}", esp.NEO)
        files = []
        for i, name in enumerate(["alpha-2.0.jar", "beta+1.21.1.jar"]):
            (d/"mods"/name).write_bytes(name.encode())
            files.append({"projectID": i + 1, "fileID": 1000 + i, "filename": name, "sha1": hashlib.sha1(name.encode()).hexdigest()})
        (d/"server-manifest.json").write_text(json.dumps({"files": files, "bundled": []}), encoding="utf-8")
        (d/"server-mods.txt").write_text("".join(f"{f['fileID']}|{f['filename']}|{f['sha1']}\n" for f in files), encoding="utf-8", newline="\n")
        (d/"install.sh").write_text(fill(esp.INSTALL_SH), encoding="utf-8", newline="\n")
        (d/"install.ps1").write_text(fill(esp.INSTALL_PS1), encoding="utf-8", newline="\r\n")
        (d/"install.bat").write_text(esp.INSTALL_BAT, encoding="utf-8", newline="\r\n")
        for name in ("server.properties.default", "user_jvm_args.default.txt"): (d/name).write_text("x\n")
        (d/"eula.txt").write_text("eula=true\n")
        lib = d/"libraries/net/neoforged/neoforge"/esp.NEO; lib.mkdir(parents=True)
        (lib/"win_args.txt").write_text(""); (lib/"unix_args.txt").write_text("")
        (d/"mods"/"alpha-1.0.jar").write_bytes(b"old"); (d/"mods"/"mine.jar").write_bytes(b"mine")
        if record is not None:
            with open(d/".installed-mods.txt", "w", newline=newline) as f: f.write("\n".join(record) + "\n")
        return d

    def run_installer(self, command):
        return subprocess.run(command, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=120)

    def check(self, command, record, newline="\n"):
        if not shutil.which("java"): self.skipTest("java not on PATH")
        with tempfile.TemporaryDirectory() as directory:
            d = self.make_server(Path(directory)/"server one", record, newline)
            for _ in range(2):
                r = self.run_installer(command(d))
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual(sorted(p.name for p in (d/"mods").iterdir()), ["alpha-2.0.jar", "beta+1.21.1.jar"] + (["mine.jar"] if record else []))
                self.assertIn("alpha-1.0.jar", [p.name for p in (d/"mods-removed").iterdir()])
            lines = (d/".installed-mods.txt").read_text().split()
            self.assertEqual(lines, ["alpha-2.0.jar", "beta+1.21.1.jar"])

    def test_install_sh(self):
        import os
        bash = shutil.which("bash")
        if not bash or (os.name == "nt" and "system32" in bash.lower()): self.skipTest("no bash")
        # the CRLF record (written by install.ps1) only bites on a Linux grep; Git Bash's grep ignores the CR
        for record, newline in [(["alpha-1.0.jar", "alpha-2.0.jar"], "\n"), (["alpha-1.0.jar", "alpha-2.0.jar"], "\r\n"), (None, "\n")]:
            with self.subTest(record=record, newline=newline):
                self.check(lambda d: [bash, str(d/"install.sh"), "--accept-eula"], record, newline)

    def test_install_ps1(self):
        import os
        hosts = {}
        if os.name == "nt" and shutil.which("powershell"):   # the operator's path: install.bat -> Windows PowerShell 5.1
            hosts["install.bat"] = lambda d: f'cmd /c ""{d / "install.bat"}" --accept-eula"'
        if shutil.which("pwsh"):
            hosts["pwsh"] = lambda d: ["pwsh", "-NoProfile", "-File", str(d/"install.ps1"), "--accept-eula"]
        if not hosts: self.skipTest("no PowerShell")
        for host, command in hosts.items():
            for record in (["alpha-1.0.jar", "alpha-2.0.jar"], None):
                with self.subTest(host=host, record=record):
                    self.check(command, record)
            with self.subTest(host=host, folder="[brackets]"), tempfile.TemporaryDirectory() as directory:
                # PowerShell reads [..] in a path as a wildcard; the installer must refuse before touching mods/
                d = self.make_server(Path(directory)/"server [1]", ["alpha-1.0.jar"])
                r = self.run_installer(command(d))
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("Rename this folder", r.stdout)
                self.assertFalse((d/"mods-removed").exists())


if __name__=="__main__": unittest.main()
