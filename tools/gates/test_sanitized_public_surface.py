#!/usr/bin/env python3
"""Cross-platform twin of Test-SanitizedPublicSurface.ps1 (same forbidden names, same secret/PII patterns).

Exit 1 on any hit. Used by export_curseforge.py / upload_curseforge.py so the gate runs wherever Python runs.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN = [
    "agrarian", "jadedcat", "jaded packs", "skyopolis", "ftb skies", "project ozone", "hypnotizd",
    "spiritual successor", "agent conversation", "plan mode", "subagent", "INTERNAL/", "Load-Secrets",
    "grok/sessions", r"\.grok[/\\]sessions",
]
SECRETS = {
    "bcrypt-hash": r"\$2a\$\d{2}\$",
    "CF_API_KEY-assignment": r"CF_API_KEY\s*=\s*\S+",
    "CF_AUTHOR_TOKEN-assignment": r"CF_AUTHOR_TOKEN\s*=\s*\S+",
    "CF_PROJECT_ID-assignment": r"CF_PROJECT_ID\s*=\s*\d+",
    "github-pat": r"ghp_[A-Za-z0-9]{20,}",
    "github-fine-grained-pat": r"github_pat_[A-Za-z0-9_]{20,}",
    "openai-style-key": r"sk-[A-Za-z0-9]{20,}",
    "private-key-block": r"BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY",
    "windows-user-profile": r"(?i)C:[\\/]Users[\\/][^\\/\s\"'`]+",
    "unix-user-home": r"(?i)(?:/Users|/home)/[^/\s\"'`]+",
    "grok-session-path": r"(?i)\.grok[\\/]+sessions",
}
PLACEHOLDER = re.compile(r"=\s*(your-|changeme|TODO|<.*>|placeholder|\.\.\.)")
TEXTISH = re.compile(r"\.(md|txt|json|json5|snbt|js|java|toml|gradle|properties|lang|ps1|py|html|xml|yml|yaml|cfg|example)$")
SKIP_DIRS = {"build", ".gradle", "run", "runs", "mdk-extract", "dist", "node_modules", ".git", "_stage", "__pycache__",
             "_skyblockbuilder_jar_extract", "_fm_ref", "_sb_ref", "_sb_cmd", "_sg_cmd", "_fm_btn"}
PUBLIC_ROOTS = ["pack/overrides", "mods", "docs", "README.md", "pack/pack.toml"]
PUSH_ROOTS = ["pack/overrides", "mods", "docs", "art", "INTERNAL", "tools", "README.md", ".gitignore"]
TOOL_ALLOW = re.compile(r"tools/(Load-Secrets\.ps1|upload-curseforge\.ps1|download-mods\.ps1|export-curseforge\.ps1|export_curseforge\.py|upload_curseforge\.py|gates/|secrets/\.env\.example)")


def textish(p: Path) -> bool:
    return bool(TEXTISH.search(p.name)) or p.name in ("README", "LICENSE", ".gitignore")


def walk(rel: str):
    root = ROOT / rel
    if root.is_file():
        yield root
        return
    if not root.exists():
        return
    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        if p.is_file() and textish(p) and p.name != ".env":
            yield p


def main() -> int:
    fails: list[str] = []
    ov = ROOT / "pack/overrides"
    if ov.exists():
        for p in ov.rglob("*"):
            s = str(p.relative_to(ROOT)).replace("\\", "/")
            if re.search(r"/INTERNAL/|/secrets/|agent.conversation|requirements\.md", "/" + s):
                fails.append(f"Internal path leaked into overrides: {s}")
    pk = ROOT / "pack"
    for p in pk.rglob("*"):
        if p.is_file() and (re.match(r"^\.env$|.*\.key$|.*credentials.*", p.name) or "/secrets/" in str(p).replace("\\", "/")):
            fails.append(f"Secret-like file under pack/: {p.relative_to(ROOT)}")
    for rel in PUBLIC_ROOTS:
        for p in walk(rel):
            c = p.read_text(encoding="utf-8", errors="ignore")
            for pat in FORBIDDEN:
                if re.search(pat, c, re.I):
                    fails.append(f"{p.relative_to(ROOT)} matches /{pat}/")
    for rel in PUSH_ROOTS:
        for p in walk(rel):
            s = str(p.relative_to(ROOT)).replace("\\", "/")
            allow = bool(TOOL_ALLOW.search(s))
            c = p.read_text(encoding="utf-8", errors="ignore")
            for name, rx in SECRETS.items():
                m = re.search(rx, c)
                if not m:
                    continue
                if allow and name.endswith("assignment"):
                    real = [x for x in re.finditer(rx, c) if not PLACEHOLDER.search(x.group(0))]
                    if real:
                        fails.append(f"{s} has {name}: {real[0].group(0)[:40]}")
                    continue
                if allow and name == "openai-style-key":
                    continue
                fails.append(f"{s} matches secret/PII pattern {name}")
    for p in (ROOT / "mods").rglob("*"):
        s = str(p).replace("\\", "/")
        if "/src/main/resources/" in s and p.suffix in (".md", ".txt"):
            if s.endswith('/assets/ftbquests/ftb_quests_theme.txt'):
                continue  # Runtime theme configuration, not a development document.
            fails.append(f"Doc file inside mod resources: {p.relative_to(ROOT)}")
    if fails:
        print(f"FAIL sanitized public surface ({len(fails)})")
        for f in fails:
            print(" -", f)
        return 1
    print("PASS sanitized public surface")
    return 0


if __name__ == "__main__":
    sys.exit(main())
