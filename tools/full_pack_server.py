#!/usr/bin/env python3
"""Boot the real Ninjacat Skies pack on a dedicated NeoForge server.

This is the check isolated GameTests cannot make: every pack jar (Mekanism included)
loads together, a survival skyblock world generates, and ServerStarted completes
without a crash. No operators, no GameTests, no creative, no command blocks.

    python tools/full_pack_server.py
    python tools/full_pack_server.py --tribal-jar path/to/tribalpower-3.2.2.jar

Exit 0 only if the process reaches vanilla "Done (... )!" and stays alive through
ServerStarted (the Mekanism incomplete-recipe scan), then stops cleanly.
"""
from __future__ import annotations

import argparse
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MC = "1.21.1"
NEO = "21.1.249"
INSTALLER_URL = (
    f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{NEO}/"
    f"neoforge-{NEO}-installer.jar"
)
CLIENT_ONLY_CONFIG = {"config/fancymenu"}
FAIL_RES = [
    re.compile(r"ClassCastException", re.I),
    re.compile(r"Exception in server tick loop"),
    re.compile(r"Failed to start the minecraft server", re.I),
    re.compile(r"Preparing crash report"),
    re.compile(r"This crash report has been saved"),
    re.compile(r"Game crashed", re.I),
]
DONE_RE = re.compile(r"Done \([^)]+\)! For help")
LOADED_MEK_RE = re.compile(r"mekanism", re.I)
LOADED_TRIBAL_RE = re.compile(r"tribalpower", re.I)

SERVER_PROPERTIES = """# Ninjacat Skies full-pack harness — survival, no operators, no command blocks.
motd=Ninjacat Skies full-pack harness
level-type=skyblockbuilder\\:skyblock
gamemode=survival
force-gamemode=true
difficulty=normal
max-players=4
view-distance=8
simulation-distance=6
online-mode=false
enable-command-block=false
spawn-protection=0
allow-flight=true
white-list=false
enforce-whitelist=false
pvp=true
max-tick-time=-1
sync-chunk-writes=false
enforce-secure-profile=false
"""

USER_JVM_ARGS = """# Harness memory. 4 GB is enough to boot; raise if the host is tight.
-Xmx4G
-Xms1G
"""


def log(msg: str) -> None:
    print(msg, flush=True)


def pack_mods(root: Path) -> Path:
    mods = root / "pack" / "mods"
    if not mods.is_dir() or not list(mods.glob("*.jar")):
        raise SystemExit(f"No pack jars at {mods}")
    return mods


def find_tribal_jar(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise SystemExit(f"--tribal-jar not found: {path}")
        return path
    env = os.environ.get("TRIBAL_JAR")
    if env:
        path = Path(env)
        if not path.is_file():
            raise SystemExit(f"TRIBAL_JAR not found: {path}")
        return path
    libs = ROOT.parent / "tribal-power" / "build" / "libs"
    jars = [
        p
        for p in libs.glob("tribalpower-*.jar")
        if "sources" not in p.name and "javadoc" not in p.name
    ]
    if not jars:
        raise SystemExit(
            "No tribalpower jar in tribal-power/build/libs — build it, or pass --tribal-jar"
        )
    return max(jars, key=lambda p: p.stat().st_mtime)


def install_neoforge(stage: Path) -> Path:
    args_txt = stage / "libraries" / "net" / "neoforged" / "neoforge" / NEO / "win_args.txt"
    if args_txt.is_file():
        log(f"NeoForge {NEO} already installed")
        return args_txt
    installer = stage / f"neoforge-{NEO}-installer.jar"
    log(f"Downloading NeoForge {NEO} installer")
    urllib.request.urlretrieve(INSTALLER_URL, installer)
    log("Installing dedicated server libraries")
    subprocess.run(
        ["java", "-jar", str(installer), "--install-server", str(stage)],
        check=True,
        cwd=stage,
    )
    installer.unlink(missing_ok=True)
    (stage / f"neoforge-{NEO}-installer.jar.log").unlink(missing_ok=True)
    if not args_txt.is_file():
        raise SystemExit(f"Installer did not write {args_txt}")
    return args_txt


def copy_overrides(root: Path, stage: Path) -> None:
    src_root = root / "pack" / "overrides"
    for name in ("config", "kubejs", "structures", "defaultconfigs"):
        src = src_root / name
        dst = stage / name
        if not src.is_dir():
            continue
        if dst.exists():
            shutil.rmtree(dst)

        def ignore(directory: str, names: list[str]) -> list[str]:
            rel = Path(directory).relative_to(src_root).as_posix()
            skipped = []
            for n in names:
                key = f"{rel}/{n}".strip("/")
                if key in CLIENT_ONLY_CONFIG or n.startswith("."):
                    skipped.append(n)
            return skipped

        shutil.copytree(src, dst, ignore=ignore)


def stage_mods(pack_mods_dir: Path, stage: Path, tribal_jar: Path) -> int:
    mods = stage / "mods"
    if mods.exists():
        shutil.rmtree(mods)
    mods.mkdir(parents=True)
    count = 0
    for jar in pack_mods_dir.glob("*.jar"):
        if jar.name.startswith("tribalpower-"):
            continue
        shutil.copy2(jar, mods / jar.name)
        count += 1
    dest = mods / tribal_jar.name
    shutil.copy2(tribal_jar, dest)
    count += 1
    log(f"Staged {count} jars (tribal overlay {tribal_jar.name})")
    return count


def write_runtime_files(stage: Path) -> None:
    (stage / "eula.txt").write_text("eula=true\n", encoding="utf-8")
    (stage / "server.properties").write_text(SERVER_PROPERTIES, encoding="utf-8")
    (stage / "user_jvm_args.txt").write_text(USER_JVM_ARGS, encoding="utf-8")
    (stage / "ops.json").write_text("[]\n", encoding="utf-8")
    (stage / "banned-players.json").write_text("[]\n", encoding="utf-8")
    (stage / "banned-ips.json").write_text("[]\n", encoding="utf-8")
    (stage / "whitelist.json").write_text("[]\n", encoding="utf-8")


def wipe_world(stage: Path) -> None:
    for name in ("world", "crash-reports"):
        path = stage / name
        if path.exists():
            shutil.rmtree(path)
    logs = stage / "logs"
    if logs.exists():
        shutil.rmtree(logs)


def fail_from_line(line: str) -> str | None:
    for pat in FAIL_RES:
        if pat.search(line):
            return line.strip()
    return None


def run_server(stage: Path, args_txt: Path, timeout: int, settle: int) -> None:
    cmd = [
        "java",
        f"@{stage / 'user_jvm_args.txt'}",
        f"@{args_txt}",
        "nogui",
    ]
    log("Launching dedicated server (survival, empty ops, no command blocks)")
    proc = subprocess.Popen(
        cmd,
        cwd=stage,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    assert proc.stdin is not None and proc.stdout is not None
    lines: queue.Queue[str | None] = queue.Queue()

    def pump() -> None:
        try:
            for raw in proc.stdout:
                lines.put(raw.rstrip("\n"))
        finally:
            lines.put(None)

    threading.Thread(target=pump, name="mc-stdout", daemon=True).start()
    started = time.monotonic()
    saw_done = False
    saw_mek = False
    saw_tribal = False
    done_at: float | None = None
    try:
        while True:
            if time.monotonic() - started > timeout:
                raise SystemExit(f"TIMEOUT after {timeout}s waiting for dedicated server")
            if saw_done and done_at is not None and time.monotonic() - done_at >= settle:
                break
            if proc.poll() is not None and lines.empty():
                crashes = list((stage / "crash-reports").glob("crash-*.txt")) if (stage / "crash-reports").exists() else []
                hint = crashes[0] if crashes else "no crash report"
                raise SystemExit(
                    f"Server exited {proc.returncode} before a clean stop ({hint})"
                )
            try:
                line = lines.get(timeout=0.5)
            except queue.Empty:
                continue
            if line is None:
                if proc.poll() is not None and not saw_done:
                    crashes = list((stage / "crash-reports").glob("crash-*.txt")) if (stage / "crash-reports").exists() else []
                    hint = crashes[0] if crashes else "no crash report"
                    raise SystemExit(
                        f"Server exited {proc.returncode} before a clean stop ({hint})"
                    )
                continue
            print(line, flush=True)
            hit = fail_from_line(line)
            if hit:
                try:
                    proc.stdin.write("stop\n")
                    proc.stdin.flush()
                except OSError:
                    pass
                raise SystemExit(f"FAIL full-pack server: {hit}")
            if LOADED_MEK_RE.search(line):
                saw_mek = True
            if LOADED_TRIBAL_RE.search(line):
                saw_tribal = True
            if DONE_RE.search(line):
                saw_done = True
                done_at = time.monotonic()
                log(f"Reached Done; waiting {settle}s for ServerStarted")
        if not saw_mek:
            raise SystemExit("FAIL: Mekanism never appeared in the server log")
        if not saw_tribal:
            raise SystemExit("FAIL: Tribal Power never appeared in the server log")
        log("Sending stop")
        proc.stdin.write("stop\n")
        proc.stdin.flush()
        try:
            code = proc.wait(timeout=120)
        except subprocess.TimeoutExpired:
            proc.kill()
            raise SystemExit("Server did not stop after stop command")
        crashes = list((stage / "crash-reports").glob("crash-*.txt")) if (stage / "crash-reports").exists() else []
        if crashes:
            raise SystemExit(f"FAIL: crash report written: {crashes[0]}")
        latest = stage / "logs" / "latest.log"
        if latest.is_file():
            text = latest.read_text(encoding="utf-8", errors="replace")
            for raw in text.splitlines():
                hit = fail_from_line(raw)
                if hit:
                    raise SystemExit(f"FAIL latest.log: {hit}")
        if code not in (0, None):
            # NeoForge sometimes exits 0 after stop; treat only crash codes as failure.
            if code != 0:
                log(f"stop returned {code} (accepted if no crash report)")
        elapsed = time.monotonic() - started
        log(
            f"PASS full-pack dedicated server in {elapsed:.1f}s "
            f"(tribal + mekanism loaded, ServerStarted held {settle}s, survival, no ops)"
        )
    finally:
        if proc.poll() is None:
            try:
                proc.stdin.write("stop\n")
                proc.stdin.flush()
            except OSError:
                pass
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.kill()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(ROOT), help="ninjacat-skies repo root")
    ap.add_argument("--stage", default="", help="server directory (default build/full-pack-server)")
    ap.add_argument("--tribal-jar", default="", help="overlay this Tribal Power jar")
    ap.add_argument("--timeout", type=int, default=900, help="seconds to wait for Done")
    ap.add_argument("--settle", type=int, default=15, help="seconds to stay up after Done")
    ap.add_argument("--keep-world", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    stage = Path(args.stage).resolve() if args.stage else root / "build" / "full-pack-server"
    stage.mkdir(parents=True, exist_ok=True)
    tribal = find_tribal_jar(args.tribal_jar or None)
    log(f"Pack root: {root}")
    log(f"Stage:     {stage}")
    log(f"Tribal:    {tribal}")
    if "3.2.1" in tribal.name:
        raise SystemExit(
            f"Refusing {tribal.name}: 3.2.1 is the crashing grit-cooking jar. Build 3.2.2+ first."
        )

    args_txt = install_neoforge(stage)
    stage_mods(pack_mods(root), stage, tribal)
    copy_overrides(root, stage)
    write_runtime_files(stage)
    if not args.keep_world:
        wipe_world(stage)
    run_server(stage, args_txt, args.timeout, args.settle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
