#!/usr/bin/env python3
"""Package the five companion mods into one CurseForge-hostable jar: Ninjacat Skies Core.

    python tools/build_core_jar.py                  # pack/mods/<mod>-<ver>.jar x5 -> pack/mods/ninjacatskies-core-<ver>.jar
    python tools/build_core_jar.py --keep-inputs    # leave the five loose jars in pack/mods (dev runs)
    python tools/build_core_jar.py --check-source   # exit 3 if mods/ changed since the released Core (pack/core-release.json)
    python tools/build_core_jar.py --record-release <fileId>   # after uploading pack/mods/ninjacatskies-core-<ver>.jar

CurseForge rejects modpack zips that carry unlisted jars in overrides/mods, so the companions ship as one CurseForge
mod project and the pack references it by project/file id like every other dependency. The outer jar has no code of
its own (modLoader "lowcodefml"); NeoForge's Jar-in-Jar loader pulls the five nested jars out of META-INF/jarjar/.
Mod ids, registries and saves are unchanged. The zip is written deterministically (fixed timestamps, sorted entries)
so an unchanged input set always produces the same SHA-1 as the CurseForge file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODS = ROOT / "pack/mods"
CORE_ID = "ninjacatskies_core"
CORE_JAR = "ninjacatskies-core-{ver}.jar"
GROUP = "com.ninjacat.skies"
# load order matters only for readability; FML resolves dependencies itself
COMPANIONS = ("ninjacatlib", "ninjacatskies", "voidloom", "clowderhall", "guardians")
EPOCH = (2026, 1, 1, 0, 0, 0)


def gradle_version() -> str:
    m = re.search(r"(?m)^mod_version=(\S+)", (ROOT / "mods/gradle.properties").read_text(encoding="utf-8"))
    if not m:
        raise SystemExit("mod_version missing from mods/gradle.properties")
    return m.group(1)


def mods_toml(ver: str) -> str:
    deps = "".join(f'''
[[dependencies.{CORE_ID}]]
    modId="{mid}"
    type="required"
    versionRange="[{ver},)"
    ordering="NONE"
    side="BOTH"
''' for mid in COMPANIONS)
    return f'''modLoader="lowcodefml"
loaderVersion="[4,)"
license="All Rights Reserved"
issueTrackerURL="https://github.com/AhmiDarrow/Ninjacat-Skies/issues"

[[mods]]
modId="{CORE_ID}"
version="{ver}"
displayName="Ninjacat Skies Core"
authors="Ninjacat Skies"
logoFile="ninjacatskies_core.png"
description=\'\'\'The Ninjacat Skies companion mods in one jar: Ninjacat Lib, Ninjacat Skies (Codex, kits, Strand story), Voidloom, Clowder Hall and the Snapped Guardians. Built for the Ninjacat Skies modpack.\'\'\'

[[dependencies.{CORE_ID}]]
    modId="neoforge"
    type="required"
    versionRange="[21.1.0,)"
    ordering="NONE"
    side="BOTH"

[[dependencies.{CORE_ID}]]
    modId="minecraft"
    type="required"
    versionRange="[1.21.1]"
    ordering="NONE"
    side="BOTH"
{deps}'''


def inner_mod(jar: Path) -> tuple[str, str]:
    with zipfile.ZipFile(jar) as z:
        toml = z.read("META-INF/neoforge.mods.toml").decode("utf-8")
    mid = re.search(r'(?m)^\s*modId\s*=\s*"([^"]+)"', toml.split("[[mods]]", 1)[1]).group(1)
    ver = re.search(r'(?m)^\s*version\s*=\s*"([^"]+)"', toml.split("[[mods]]", 1)[1]).group(1)
    return mid, ver


def put(z: zipfile.ZipFile, name: str, data: bytes, stored: bool = False) -> None:
    info = zipfile.ZipInfo(name, EPOCH)
    info.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, data)


def build(ver: str, mods_dir: Path, out_dir: Path) -> Path:
    inputs = []
    for mid in COMPANIONS:
        jar = mods_dir / f"{mid}-{ver}.jar"
        if not jar.is_file():
            raise SystemExit(f"missing companion jar: {jar.name} (build mods/ first)")
        got_id, got_ver = inner_mod(jar)
        if (got_id, got_ver) != (mid, ver):
            raise SystemExit(f"{jar.name} declares {got_id} {got_ver}, expected {mid} {ver}")
        inputs.append((mid, jar))
    metadata = {"jars": [{
        "identifier": {"group": GROUP, "artifact": mid},
        "version": {"range": f"[{ver},)", "artifactVersion": ver},
        "path": f"META-INF/jarjar/{jar.name}",
        "isObfuscated": False,
    } for mid, jar in inputs]}
    out = out_dir / CORE_JAR.format(ver=ver)
    tmp = out.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w") as z:
        put(z, "META-INF/MANIFEST.MF", (f"Manifest-Version: 1.0\r\nImplementation-Title: Ninjacat Skies Core\r\n"
                                        f"Implementation-Version: {ver}\r\n\r\n").encode())
        put(z, "META-INF/neoforge.mods.toml", mods_toml(ver).encode("utf-8"))
        put(z, "META-INF/jarjar/metadata.json", (json.dumps(metadata, indent=2) + "\n").encode("utf-8"))
        for _, jar in inputs:          # nested jars are already compressed; store them
            put(z, f"META-INF/jarjar/{jar.name}", jar.read_bytes(), stored=True)
        logo = ROOT / "docs/public/pack-icon-256.png"
        if logo.is_file():
            put(z, "ninjacatskies_core.png", logo.read_bytes(), stored=True)
    tmp.replace(out)
    return out


RELEASE = ROOT / "pack/core-release.json"
# Build tooling that never ends up in the jars. The wrapper jar was untracked (ignored) when Core 0.4.1 was recorded.
HASH_EXCLUDE = {"mods/gradle/wrapper/gradle-wrapper.jar"}
SOURCE_CHANGED = "differs from the released Core"


def source_hash() -> str:
    """SHA-1 over every non-ignored file under mods/ (paths sorted, CRLF folded to LF so Windows and Linux agree).
    Compiled jars are not reproducible byte-for-byte (debug names differ between incremental and clean javac runs),
    so "did the companion code change since the Core file on CurseForge?" is answered from the sources instead."""
    names = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "mods"], cwd=ROOT,
                           check=True, capture_output=True).stdout.decode("utf-8").split("\0")
    h = hashlib.sha1()
    for name in sorted(n for n in names if n and n not in HASH_EXCLUDE):
        path = ROOT / name
        if path.is_file():
            h.update(name.encode("utf-8") + b"\0" + path.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    return h.hexdigest()


def release_problems(ver: str | None = None) -> list[str]:
    """Why an export must not ship the Core jar in pack/mods; empty when it is the recorded CurseForge release and the
    companion sources still match it. Exports and every gate mode call this (no Gradle needed)."""
    ver = ver or gradle_version()
    if not RELEASE.is_file():
        return [f"{RELEASE.relative_to(ROOT).as_posix()} is missing"]
    rel = json.loads(RELEASE.read_text(encoding="utf-8"))
    problems = []
    try:
        now = source_hash()
    except (OSError, subprocess.CalledProcessError) as exc:
        return [f"cannot hash mods/ sources with git ({exc}); run from a git checkout"]
    if rel.get("sourceHash") != now or rel.get("version") != ver:
        problems.append(f"mods/ (version {ver}) {SOURCE_CHANGED} {rel.get('filename', '(none)')}")
    jar = MODS / CORE_JAR.format(ver=ver)
    if rel.get("filename") != jar.name:
        problems.append(f"pack/core-release.json records {rel.get('filename')}, expected {jar.name}")
    elif not jar.is_file():
        problems.append(f"pack/mods/{jar.name} is missing")
    elif hashlib.sha1(jar.read_bytes()).hexdigest() != rel.get("sha1"):
        problems.append(f"pack/mods/{jar.name} is not the uploaded CurseForge file {rel.get('fileId')} (SHA-1 differs)")
    return problems


def require_released_core() -> None:
    problems = release_problems()
    if problems:
        hint = "\n" + RELEASE_STEPS if any(SOURCE_CHANGED in p for p in problems) else ""
        raise SystemExit("Ninjacat Skies Core is not releasable:\n  - " + "\n  - ".join(problems) + hint)


RELEASE_STEPS = ("  -> bump mod_version, build, python tools/build_core_jar.py --mods-dir <built jars>, upload the jar to "
                 "CurseForge project 1689718, python tools/build_core_jar.py --record-release <fileId>, "
                 "and update its row in pack/modlist-resolved.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="")
    ap.add_argument("--mods-dir", default=str(MODS))
    ap.add_argument("--out-dir", default=str(MODS))
    ap.add_argument("--keep-inputs", action="store_true")
    ap.add_argument("--check-source", action="store_true", help="fail (exit 3) if mods/ differs from the released Core")
    ap.add_argument("--record-release", type=int, default=0, metavar="FILE_ID",
                    help="write pack/core-release.json for the Core jar in pack/mods, uploaded as this CurseForge file")
    args = ap.parse_args()
    ver = args.version or gradle_version()
    if args.check_source or args.record_release:
        if args.record_release:
            jar = MODS / CORE_JAR.format(ver=ver)
            if not jar.is_file():
                raise SystemExit(f"{jar.name} is not in pack/mods")
            RELEASE.write_text(json.dumps({"version": ver, "projectId": 1689718, "fileId": args.record_release,
                                           "filename": jar.name, "sha1": hashlib.sha1(jar.read_bytes()).hexdigest(),
                                           "sourceHash": source_hash()}, indent=2) + "\n", encoding="utf-8")
            print(f"recorded {jar.name} as CurseForge file {args.record_release}")
            return 0
        problems = release_problems(ver)
        if problems:
            print("CHANGED: " + "; ".join(problems) + ".")
            if any(SOURCE_CHANGED in p for p in problems):
                print(RELEASE_STEPS)
            return 3
        rel = json.loads(RELEASE.read_text(encoding="utf-8"))
        print(f"UNCHANGED: mods/ and pack/mods match the released {rel['filename']} (CurseForge file {rel['fileId']})")
        return 0
    mods_dir = Path(args.mods_dir)
    out = build(ver, mods_dir, Path(args.out_dir))
    print(f"{out.name}  {out.stat().st_size} bytes  sha1={hashlib.sha1(out.read_bytes()).hexdigest()}")
    if not args.keep_inputs and Path(args.out_dir).resolve() == mods_dir.resolve():
        for mid in COMPANIONS:
            (mods_dir / f"{mid}-{ver}.jar").unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main())
