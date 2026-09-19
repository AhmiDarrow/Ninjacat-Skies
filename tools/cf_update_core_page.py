#!/usr/bin/env python3
"""Push the Ninjacat Skies Core CurseForge page (project 1689718): summary and description from docs/core/.

    python tools/render_core_store_html.py && python tools/cf_update_core_page.py

Uses the saved Chrome profile that holds the Authors Console login (the same one tools/_cf_finalize_pages.py uses).
If the login has expired, sign in in the Chrome window that opens; the script waits. Only this project is touched.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PROFILE = Path.home() / "AppData" / "Local" / "ms-playwright" / "cf-logged-in"
PID = 1689718
MD = (ROOT / "docs/core/store-description.md").read_text(encoding="utf-8")
HTML = (ROOT / "docs/core/store-description.html").read_text(encoding="utf-8")
SUMMARY = re.search(r"\*\*CurseForge summary \(one line\):\*\* (.+)", MD).group(1).strip()
# the summary line is for the author; the public page starts at the title
BODY = re.sub(r"<p><strong>CurseForge summary \(one line\):</strong>.*?</p>\n?", "", HTML, count=1)


def main() -> int:
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(user_data_dir=str(PROFILE), channel="chrome", headless=False,
                                                   viewport={"width": 1280, "height": 900},
                                                   args=["--disable-blink-features=AutomationControlled", "--profile-directory=Default"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            page.goto("https://authors.curseforge.com/", wait_until="domcontentloaded", timeout=90000)
            deadline = time.time() + 600
            while time.time() < deadline:
                r = page.request.get(f"https://authors.curseforge.com/_api/projects/{PID}")
                if r.status == 200:
                    break
                print("WAITING: sign in to the CurseForge Authors Console in the Chrome window...", flush=True)
                time.sleep(5)
            else:
                print("login timeout")
                return 2
            detail = r.json()
            print("before:", detail.get("summary"), flush=True)
            body = {
                "name": detail.get("name"), "slug": detail.get("slug"), "summary": SUMMARY,
                "primaryCategoryId": detail.get("primaryCategoryId"), "subCategoryIds": detail.get("subCategoryIds") or [],
                "allowComments": bool(detail.get("allowComments", True)), "enableProjectPages": bool(detail.get("enableProjectPages", False)),
            }
            u = page.request.put(f"https://authors.curseforge.com/_api/projects/{PID}/update-details",
                                 data=json.dumps(body), headers={"Content-Type": "application/json"})
            print("summary:", u.status, u.text()[:200], flush=True)
            ok = False
            for dtype in (1, 2, 0):
                d = page.request.put(f"https://authors.curseforge.com/_api/projects/description/{PID}",
                                     data=json.dumps({"description": BODY, "descriptionType": dtype}),
                                     headers={"Content-Type": "application/json"})
                print(f"description (type {dtype}):", d.status, d.text()[:200], flush=True)
                if d.status == 200:
                    ok = True
                    break
            return 0 if (u.status == 200 and ok) else 1
        finally:
            ctx.close()


if __name__ == "__main__":
    raise SystemExit(main())
