#!/usr/bin/env python3
"""Build a CurseForge-importable client zip (manifest.json + overrides/). Cross-platform twin of
export-curseforge.ps1 — same layout, same exclusions, version read from pack/pack.toml.

  python tools/export_curseforge.py                # CurseForge mode (CF-hosted mods in manifest.files)
  Third-party mods must have verified CurseForge manifest references; never bundle them.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import time
import zipfile
from cf_distribution import is_owned_jar, manifest_entries
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MC = "1.21.1"
NEO = "21.1.249"


def pack_version() -> str:
    m = re.search(r'(?m)^version\s*=\s*"([^"]+)"', (ROOT / "pack/pack.toml").read_text(encoding="utf-8"))
    return m.group(1) if m else "0.0.0"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(ROOT / "dist"))
    ap.add_argument("--self-contained", action="store_true")
    ap.add_argument("--skip-sanitize", action="store_true")
    args = ap.parse_args()
    if args.self_contained:
        raise SystemExit("Self-contained exports are disabled: third-party jars must be installed through CurseForge.")
    source_overrides = ROOT / "pack/overrides"
    if any(p.suffix.lower() == ".jar" for p in source_overrides.rglob("*")):
        raise SystemExit("Do not place jars inside pack/overrides; use verified pack/mods dependency metadata.")
    resolved_path = ROOT / "pack/modlist-resolved.json"
    resolved = json.loads(resolved_path.read_text(encoding="utf-8"))
    jars = sorted((ROOT / "pack/mods").glob("*.jar"))
    if not jars:
        raise SystemExit("No jars in pack/mods")
    manifest_files = manifest_entries(jars, resolved)


    if not args.skip_sanitize:
        print("Running sanitization gate (no tokens / personal paths)...")
        r = subprocess.run([sys.executable, str(ROOT / "tools/gates/test_sanitized_public_surface.py")])
        if r.returncode != 0:
            raise SystemExit("Sanitization gate failed — refusing to export")

    version = pack_version()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    stage = out_dir / f"stage-ninjacat-skies-{stamp}"
    zip_path = out_dir / f"NinjacatSkies-{version}-{stamp}.zip"
    shutil.rmtree(stage, ignore_errors=True)
    stage.mkdir(parents=True)

    # overrides
    shutil.copytree(ROOT / "pack/overrides", stage / "overrides")
    ov_mods = stage / "overrides/mods"
    ov_mods.mkdir(parents=True, exist_ok=True)

    # Only our four unhosted companion mods may be redistributed as override jars.
    bundled = []
    for jar in jars:
        if is_owned_jar(jar.name):
            shutil.copy2(jar, ov_mods / jar.name)
            bundled.append(jar.name)

    manifest = {
        "minecraft": {"version": MC, "modLoaders": [{"id": f"neoforge-{NEO}", "primary": True}], "recommendedRam": 8192},
        "manifestType": "minecraftModpack",
        "manifestVersion": 1,
        "name": "Ninjacat Skies",
        "version": version,
        "author": "Ahmi & Risika Darrow",
        "image": "profileImage/ninjacat-skies.png",
        "files": manifest_files,
        "overrides": "overrides",
    }
    (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # icon + store helpers + install notes
    icon = ROOT / "docs/public/pack-icon-400.png"
    if not icon.is_file():
        raise FileNotFoundError(f"Required profile logo missing: {icon}")
    if icon.exists():
        (stage / "profileImage").mkdir(exist_ok=True)
        shutil.copy2(icon, stage / "profileImage/ninjacat-skies.png")
        shutil.copy2(icon, stage / "icon.png")
        shutil.copy2(icon, stage / "overrides/pack-icon.png")
    for name in ("store-description.html", "store-description.md"):
        src = ROOT / "docs/public" / name
        if src.exists():
            shutil.copy2(src, stage / "overrides" / name)
    (stage / "overrides/INSTALL.txt").write_text(
        "Ninjacat Skies — install notes\n"
        "==============================\n\n"
        f"Minecraft {MC} · NeoForge {NEO} · pack {version}\n\n"
        "MEMORY (required)\n"
        "  CurseForge App → Ninjacat Skies → ⋮ → Profile Options → Memory\n"
        "  Prefer \"Recommended by Author\" (8 GB / 8192 MB from the pack manifest).\n"
        "  Or Custom RAM Allocation = 8192 MB. 4096 MB is not enough.\n"
        "  Minimum viable: 6144 MB. Recommended: 8192–10240 MB.\n\n"
        "ICON\n"
        "  manifest.image references the bundled 400x400 sky-cat profile logo.\n"
        "  CurseForge PROJECT page avatar/description must still be set in the\n"
        "  Author Console (General + Description tabs) — zip import alone does not.\n\n"
        "UI\n"
        "  Enable the ninjacat-skies-ui resource pack if title/splashes look vanilla.\n\n"
        "Full store blurb: see the project page / docs/public/store-description.md\n",
        encoding="utf-8",
    )

    rows = []
    for r in sorted(resolved, key=lambda x: (str(x.get("name", "")), str(x.get("key", "")))):
        try:
            pid = int(r.get("projectId", 0))
        except (TypeError, ValueError):
            pid = 0
        if pid <= 0:
            continue
        rows.append(f'<li><a href="https://www.curseforge.com/minecraft/mc-mods/{r.get("slug", "")}">{html.escape(str(r.get("name", "")))}</a> (file {r.get("fileId")})</li>')
    for name in sorted(bundled):
        rows.append(f"<li>{html.escape(name)} <em>(bundled override)</em></li>")
    (stage / "modlist.html").write_text("<ul>\n" + "\n".join(rows) + "\n</ul>\n", encoding="utf-8")

    # strip anything internal / tooling that rode along
    for p in list(stage.rglob("*")):
        s = str(p.relative_to(stage)).replace("\\", "/")
        if p.is_file() and (re.match(r"^\.env$|.*\.key$|.*credentials.*", p.name) or re.search(r"(^|/)(INTERNAL|agent)/|requirements", s) or p.suffix in (".ps1", ".py")):
            p.unlink()

    # zip with forward-slash entries
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob("*")):
            if p.is_file():
                z.write(p, str(p.relative_to(stage)).replace("\\", "/"))
    shutil.rmtree(stage, ignore_errors=True)

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        parsed = json.loads(z.read("manifest.json"))
        ov_count = sum(1 for n in names if n.startswith("overrides/mods/"))
        top_mods = sum(1 for n in names if n.startswith("mods/"))
        internal = [n for n in names if "INTERNAL" in n or n.endswith(".env") or n.endswith(".ps1")]
    print(f"Exported {zip_path}")
    print(f"Mode={'SelfContained' if args.self_contained else 'CurseForge'}  manifest.files={len(parsed['files'])}  overrides/mods={ov_count}  top-level mods/={top_mods} (must be 0)")
    if top_mods or internal:
        raise SystemExit(f"Export produced illegal entries: top_mods={top_mods} internal={internal[:3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
