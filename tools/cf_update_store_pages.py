#!/usr/bin/env python3
"""Publish CurseForge store pages (summary + description) from each project's store-description files.

    python tools/render_store_html.py                    # pack + Core HTML (Tribal Power / Chocobos render their own)
    python tools/cf_update_store_pages.py [pack core tribalpower chocobos]   # default: all four

Sources: docs/public (modpack), docs/core (Ninjacat Skies Core), ../tribal-power/docs/public, ../chocobos-reborn/docs/public.
The summary is the "CurseForge summary (one line)" line of the .md; that paragraph is dropped from the published body.
Uses the saved Chrome profile that holds the Authors Console login; if it has expired, sign in in the window that
opens and the script waits.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PROFILE = Path.home() / "AppData" / "Local" / "ms-playwright" / "cf-logged-in"
PAGES = {
    "pack": (1684777, ROOT / "docs/public"),
    "core": (1689718, ROOT / "docs/core"),
    "tribalpower": (1684851, ROOT.parent / "tribal-power/docs/public"),
    "chocobos": (1699008, ROOT.parent / "chocobos-reborn/docs/public"),
}
SUMMARY_RE = re.compile(r"\*\*CurseForge summary \(one line\):\*\*\s*(.+)", re.I)
SUMMARY_P = re.compile(r"<p><strong>CurseForge summary \(one line\):</strong>.*?</p>\n?", re.I | re.S)


def source(folder: Path) -> tuple[str, str]:
    md = (folder / "store-description.md").read_text(encoding="utf-8")
    body = (folder / "store-description.html").read_text(encoding="utf-8")
    m = SUMMARY_RE.search(md)
    if not m:
        raise SystemExit(f"{folder}: no 'CurseForge summary (one line)' line in store-description.md")
    return re.sub(r"\s+", " ", m.group(1)).strip(), SUMMARY_P.sub("", body, count=1)


def main(names: list[str]) -> int:
    todo = {n: PAGES[n] for n in (names or PAGES)}
    failed = 0
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(user_data_dir=str(PROFILE), channel="chrome", headless=False,
                                                   viewport={"width": 1280, "height": 900},
                                                   args=["--disable-blink-features=AutomationControlled", "--profile-directory=Default"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            page.goto("https://authors.curseforge.com/", wait_until="domcontentloaded", timeout=90000)
            first = next(iter(todo.values()))[0]
            deadline = time.time() + 600
            while page.request.get(f"https://authors.curseforge.com/_api/projects/{first}").status != 200:
                if time.time() > deadline:
                    print("login timeout"); return 2
                print("WAITING: sign in to the CurseForge Authors Console in the Chrome window...", flush=True)
                time.sleep(5)
            for name, (pid, folder) in todo.items():
                summary, body = source(folder)
                detail = page.request.get(f"https://authors.curseforge.com/_api/projects/{pid}").json()
                payload = {
                    "name": detail.get("name"), "slug": detail.get("slug"), "summary": summary,
                    "primaryCategoryId": detail.get("primaryCategoryId"), "subCategoryIds": detail.get("subCategoryIds") or [],
                    "allowComments": bool(detail.get("allowComments", True)), "enableProjectPages": bool(detail.get("enableProjectPages", False)),
                }
                u = page.request.put(f"https://authors.curseforge.com/_api/projects/{pid}/update-details",
                                     data=json.dumps(payload), headers={"Content-Type": "application/json"})
                d = page.request.put(f"https://authors.curseforge.com/_api/projects/description/{pid}",
                                     data=json.dumps({"description": body, "descriptionType": 1}), headers={"Content-Type": "application/json"})
                ok = u.status == 200 and d.status == 200
                failed += not ok
                print(f"{name:12s} {pid}: summary {u.status}, description {d.status}{'' if ok else '  ' + d.text()[:160]}", flush=True)
        finally:
            ctx.close()
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
