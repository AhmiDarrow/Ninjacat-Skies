#!/usr/bin/env python3
"""Build the dedicated-server pack that accompanies each CurseForge release.

    python tools/export_server_pack.py                      # -> dist/NinjacatSkies-Server-<version>-<stamp>.zip

The zip is "ready to go" without redistributing anyone else's jar: it carries our companion mods, the server-side
config / KubeJS / structures, a manifest of the exact CurseForge files the client zip references, and install
scripts (bash and PowerShell) that fetch the NeoForge installer from maven.neoforged.net and every mod from
CurseForge's CDN, verifying each SHA-1 against the manifest. Then `start.sh` / `start.bat`.

Same distribution rules as the client zip (tools/cf_distribution.py): only the five owned jars are bundled, every
third-party mod must be a verified CurseForge file; the sanitization gate runs first and the produced archive is
checked by tools/gates/test_export_archive.verify_server.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cf_distribution import is_owned_jar, manifest_entries  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MC = "1.21.1"
NEO = "21.1.249"
# server-side overrides; resource packs and the FancyMenu client config stay out
OVERRIDE_DIRS = ["config", "kubejs", "structures", "defaultconfigs"]
CLIENT_ONLY = {"config/fancymenu"}


def pack_version() -> str:
    m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', (ROOT / "pack/pack.toml").read_text(encoding="utf-8"))
    return m.group(1) if m else "0.0.0"


INSTALL_SH = r'''#!/usr/bin/env bash
# Ninjacat Skies dedicated server — installer. Needs: java 21, curl, sha1sum (or shasum).
set -euo pipefail
cd "$(dirname "$0")"
MC="{MC}"; NEO="{NEO}"
say() { printf '%s\n' "$*"; }
need() { command -v "$1" >/dev/null 2>&1 || { say "missing: $1"; exit 1; }; }
need java; need curl
if command -v sha1sum >/dev/null 2>&1; then SHA1="sha1sum"; elif command -v shasum >/dev/null 2>&1; then SHA1="shasum -a 1"; else say "missing: sha1sum"; exit 1; fi
JV=$(java -version 2>&1 | grep -m1 -oE 'version "[0-9]+' | grep -oE '[0-9]+$' || true); [ "${JV:-0}" -ge 21 ] || { say "Java 21 or newer is required (found: $(java -version 2>&1 | grep -m1 version))"; exit 1; }

say "== NeoForge $NEO server"
if [ ! -f "libraries/net/neoforged/neoforge/$NEO/unix_args.txt" ]; then
  curl -fsSL -o neoforge-installer.jar "https://maven.neoforged.net/releases/net/neoforged/neoforge/$NEO/neoforge-$NEO-installer.jar"
  java -jar neoforge-installer.jar --install-server . >/dev/null
  rm -f neoforge-installer.jar neoforge-installer.jar.log
fi

say "== mods (from CurseForge, verified by SHA-1)"
mkdir -p mods
n=0; total=$(grep -c . server-mods.txt || true)
# server-mods.txt: one line per mod, fileID|filename|sha1 (the same data as server-manifest.json)
while IFS='|' read -r fid fn sha; do
  [ -n "$fid" ] || continue
  n=$((n+1))
  dst="mods/$fn"
  if [ -f "$dst" ] && [ "$($SHA1 "$dst" | cut -d' ' -f1)" = "$sha" ]; then continue; fi
  enc=$(printf '%s' "$fn" | sed 's/ /%20/g; s/+/%2B/g')
  url="https://edge.forgecdn.net/files/$((fid/1000))/$((fid%1000))/$enc"
  say "  [$n/$total] $fn"
  curl -fsSL --retry 3 -o "$dst.part" "$url" || { say "download failed: $fn ($url)"; rm -f "$dst.part"; exit 1; }
  got=$($SHA1 "$dst.part" | cut -d' ' -f1)
  [ "$got" = "$sha" ] || { say "checksum mismatch for $fn (expected $sha, got $got)"; rm -f "$dst.part"; exit 1; }
  mv -f "$dst.part" "$dst"
done < server-mods.txt

[ -f server.properties ] || cp -n server.properties.default server.properties
[ -f user_jvm_args.txt ] || cp -n user_jvm_args.default.txt user_jvm_args.txt

if [ ! -f eula.txt ] || ! grep -qi 'eula=true' eula.txt; then
  if [ "${1:-}" = "--accept-eula" ]; then echo "eula=true" > eula.txt
  else
    say ""
    say "Minecraft's EULA (https://aka.ms/MinecraftEULA) must be accepted to run a server."
    read -r -p "Accept it now? [y/N] " a; case "$a" in y|Y|yes|YES) echo "eula=true" > eula.txt;; *) say "Not accepted — edit eula.txt later.";; esac
  fi
fi
say ""
say "Installed. Start with ./start.sh (edit server.properties and user_jvm_args.txt first if you like)."
'''

INSTALL_PS1 = r'''# Ninjacat Skies dedicated server — installer (Windows PowerShell). Needs Java 21.
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot
$MC = "{MC}"; $NEO = "{NEO}"
$jvLine = (& java -version 2>&1 | Select-String -Pattern 'version "(\d+)' | Select-Object -First 1)
$jv = if ($jvLine) { [int]$jvLine.Matches[0].Groups[1].Value } else { 0 }
if ($jv -lt 21) { Write-Host "Java 21 or newer is required (found: $jvLine)"; exit 1 }

Write-Host "== NeoForge $NEO server"
if (-not (Test-Path "libraries/net/neoforged/neoforge/$NEO/win_args.txt")) {
  Invoke-WebRequest -Uri "https://maven.neoforged.net/releases/net/neoforged/neoforge/$NEO/neoforge-$NEO-installer.jar" -OutFile neoforge-installer.jar
  & java -jar neoforge-installer.jar --install-server . | Out-Null
  Remove-Item -Force neoforge-installer.jar, neoforge-installer.jar.log -ErrorAction SilentlyContinue
}

Write-Host "== mods (from CurseForge, verified by SHA-1)"
New-Item -ItemType Directory -Force -Path mods | Out-Null
$manifest = Get-Content server-manifest.json -Raw | ConvertFrom-Json
$i = 0; $total = $manifest.files.Count
foreach ($f in $manifest.files) {
  $i++
  $dst = Join-Path mods $f.filename
  if ((Test-Path $dst) -and ((Get-FileHash $dst -Algorithm SHA1).Hash.ToLower() -eq $f.sha1)) { continue }
  $enc = [uri]::EscapeDataString($f.filename)
  $url = "https://edge.forgecdn.net/files/$([math]::Floor($f.fileID / 1000))/$($f.fileID % 1000)/$enc"
  Write-Host "  [$i/$total] $($f.filename)"
  Invoke-WebRequest -Uri $url -OutFile "$dst.part"
  $got = (Get-FileHash "$dst.part" -Algorithm SHA1).Hash.ToLower()
  if ($got -ne $f.sha1) { Remove-Item -Force "$dst.part"; throw "checksum mismatch for $($f.filename)" }
  Move-Item -Force "$dst.part" $dst
}

if (-not (Test-Path server.properties)) { Copy-Item server.properties.default server.properties }
if (-not (Test-Path user_jvm_args.txt)) { Copy-Item user_jvm_args.default.txt user_jvm_args.txt }

if (-not (Test-Path eula.txt) -or -not (Select-String -Path eula.txt -Pattern 'eula=true' -Quiet)) {
  if ($args -contains "--accept-eula") { Set-Content eula.txt "eula=true" }
  else {
    Write-Host ""; Write-Host "Minecraft's EULA (https://aka.ms/MinecraftEULA) must be accepted to run a server."
    $a = Read-Host "Accept it now? [y/N]"
    if ($a -match '^(y|yes)$') { Set-Content eula.txt "eula=true" } else { Write-Host "Not accepted - edit eula.txt later." }
  }
}
Write-Host ""; Write-Host "Installed. Start with start.bat (edit server.properties and user_jvm_args.txt first if you like)."
'''

INSTALL_BAT = r'''@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
pause
'''

START_SH = r'''#!/usr/bin/env bash
cd "$(dirname "$0")"
[ -f "libraries/net/neoforged/neoforge/{NEO}/unix_args.txt" ] || { echo "Run ./install.sh first."; exit 1; }
exec java @user_jvm_args.txt @libraries/net/neoforged/neoforge/{NEO}/unix_args.txt nogui "$@"
'''

START_BAT = r'''@echo off
cd /d "%~dp0"
if not exist "libraries\net\neoforged\neoforge\{NEO}\win_args.txt" ( echo Run install.bat first. & pause & exit /b 1 )
java @user_jvm_args.txt @libraries/net/neoforged/neoforge/{NEO}/win_args.txt nogui %*
pause
'''

SERVER_PROPERTIES = '''# Ninjacat Skies dedicated server. Everything here is a normal Minecraft server setting.
motd=Ninjacat Skies \\u2014 nine tribes, one thread
level-type=skyblockbuilder\\:skyblock
gamemode=survival
difficulty=normal
max-players=10
view-distance=10
simulation-distance=8
online-mode=true
enable-command-block=true
spawn-protection=0
allow-flight=true
max-tick-time=-1
sync-chunk-writes=false
enforce-secure-profile=false
'''

USER_JVM_ARGS = '''# Memory for the server. 6 GB is comfortable for a small Clowder; 4 GB is the floor.
-Xmx6G
-Xms2G
'''

README = '''# Ninjacat Skies — dedicated server

Minecraft {MC} · NeoForge {NEO} · pack {VERSION}

This server pack does not redistribute other people's mods. `install` downloads NeoForge from maven.neoforged.net
and every mod from CurseForge's CDN, checking each file against the checksums in `server-manifest.json`.

## Install
1. Install Java 21 (Temurin, Microsoft or Oracle builds all work).
2. Linux / macOS: `./install.sh`   Windows: double-click `install.bat`
   (add `--accept-eula` to accept Minecraft's EULA non-interactively).
3. Start: `./start.sh` or `start.bat`. First start generates the world; `level-type` is already set to
   Skyblock Builder's void world so players spawn at the Dock.

## Settings
- `server.properties` — memory is in `user_jvm_args.txt` (6 GB default, 4 GB minimum).
- `config/` and `kubejs/` are the pack's own settings and scripts; they match the client zip of the same version.
- Give yourself operator once: `op <name>` in the console. `/clowder`, `/skybound`, `/guardians` are the pack's commands.

## Updating
Unzip the newer server pack over this folder and run `install` again: it fetches only files whose checksum changed
and keeps `world/`, `server.properties`, `eula.txt` and `user_jvm_args.txt`.
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(ROOT / "dist"))
    ap.add_argument("--skip-sanitize", action="store_true")
    args = ap.parse_args()

    if not args.skip_sanitize:
        print("Running sanitization gate (no tokens / personal paths)...")
        r = subprocess.run([sys.executable, str(ROOT / "tools/gates/test_sanitized_public_surface.py")])
        if r.returncode != 0:
            raise SystemExit("Sanitization gate failed — refusing to export")

    resolved = json.loads((ROOT / "pack/modlist-resolved.json").read_text(encoding="utf-8"))
    jars = sorted((ROOT / "pack/mods").glob("*.jar"))
    if not jars:
        raise SystemExit("No jars in pack/mods")
    entries = manifest_entries(jars, resolved)              # fail-closed: every third-party jar verified against CF
    by_project = {row["projectId"]: row for row in resolved}
    files = []
    for e in entries:
        row = by_project[e["projectID"]]
        files.append({"projectID": e["projectID"], "fileID": e["fileID"], "filename": row["filename"], "sha1": row["sha1"]})
    files.sort(key=lambda f: f["filename"].lower())

    version = pack_version()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    stage = out_dir / f"stage-server-{stamp}"
    zip_path = out_dir / f"NinjacatSkies-Server-{version}-{stamp}.zip"
    shutil.rmtree(stage, ignore_errors=True); stage.mkdir(parents=True)

    (stage / "mods").mkdir()
    bundled = []
    for jar in jars:
        if is_owned_jar(jar.name):
            shutil.copy2(jar, stage / "mods" / jar.name); bundled.append(jar.name)
    for d in OVERRIDE_DIRS:
        src = ROOT / "pack/overrides" / d
        if src.is_dir():
            shutil.copytree(src, stage / d, ignore=lambda p, names: [n for n in names if f"{Path(p).relative_to(ROOT / 'pack/overrides').as_posix()}/{n}".strip("/") in CLIENT_ONLY or n.startswith(".")])
    for p in list(stage.rglob("*")):                       # nothing internal, nothing executable-by-accident, nothing secret
        s = p.relative_to(stage).as_posix()
        if p.is_file() and (re.match(r"^\.env$|.*\.key$|.*credentials.*", p.name) or re.search(r"(^|/)(INTERNAL|agent)/|requirements", s) or p.suffix in (".py",)):
            p.unlink()

    subst = {"MC": MC, "NEO": NEO, "VERSION": version}
    def fill(t: str) -> str:
        for k, v in subst.items(): t = t.replace("{" + k + "}", v)
        return t
    (stage / "server-manifest.json").write_text(json.dumps({
        "minecraft": MC, "neoforge": NEO, "pack": "Ninjacat Skies", "version": version,
        "bundled": sorted(bundled), "files": files}, indent=2) + "\n", encoding="utf-8")
    (stage / "server-mods.txt").write_text("".join(f"{f['fileID']}|{f['filename']}|{f['sha1']}\n" for f in files), encoding="utf-8", newline="\n")
    (stage / "install.sh").write_text(fill(INSTALL_SH), encoding="utf-8", newline="\n")
    (stage / "install.ps1").write_text(fill(INSTALL_PS1), encoding="utf-8", newline="\r\n")
    (stage / "install.bat").write_text(INSTALL_BAT, encoding="utf-8", newline="\r\n")
    (stage / "start.sh").write_text(fill(START_SH), encoding="utf-8", newline="\n")
    (stage / "start.bat").write_text(fill(START_BAT), encoding="utf-8", newline="\r\n")
    (stage / "server.properties.default").write_text(SERVER_PROPERTIES, encoding="utf-8", newline="\n")
    (stage / "user_jvm_args.default.txt").write_text(USER_JVM_ARGS, encoding="utf-8", newline="\n")
    (stage / "README-SERVER.md").write_text(fill(README), encoding="utf-8")
    icon = ROOT / "docs/public/pack-icon-400.png"
    if icon.is_file(): shutil.copy2(icon, stage / "server-icon-source.png")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob("*")):
            if p.is_file():
                info = zipfile.ZipInfo(p.relative_to(stage).as_posix(), date_time=time.localtime(p.stat().st_mtime)[:6])
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o755 if p.suffix == ".sh" else 0o644) << 16
                z.writestr(info, p.read_bytes())
    shutil.rmtree(stage, ignore_errors=True)

    sys.path.insert(0, str(ROOT / "tools/gates"))
    from test_export_archive import verify_server  # noqa: E402
    verify_server(zip_path)
    print(f"Exported {zip_path}")
    print(f"manifest.files={len(files)}  bundled={len(bundled)}  size={zip_path.stat().st_size // 1024} KiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
