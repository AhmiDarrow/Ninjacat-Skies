"""Probe CurseForge Author Console login + project edit URLs (headed)."""
from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

NCS_ROOT = Path(__file__).resolve().parents[1]
PROFILE = Path.home() / "AppData" / "Local" / "ms-playwright" / "cf-author-profile"
OUT = NCS_ROOT / "docs" / "public" / "cf-assets"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    PROFILE.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            headless=False,
            channel="chrome",
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        urls = [
            "https://authors.curseforge.com/",
            "https://authors.curseforge.com/#/projects",
            "https://authors.curseforge.com/#/project/1684777",
            "https://authors.curseforge.com/#/projects/1684777",
            "https://www.curseforge.com/account/projects",
        ]
        results = []
        for u in urls:
            page.goto(u, wait_until="domcontentloaded", timeout=60000)
            time.sleep(3)
            shot = OUT / f"probe-{abs(hash(u)) % 10_000_000}.png"
            page.screenshot(path=str(shot), full_page=False)
            results.append(
                {
                    "url": u,
                    "final": page.url,
                    "title": page.title(),
                    "shot": str(shot),
                    "body_sample": page.locator("body").inner_text()[:800],
                }
            )
            print("===", u)
            print(" final:", page.url)
            print(" title:", page.title())
            print(results[-1]["body_sample"][:400].replace("\n", " | "))
        (OUT / "probe-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        print("Waiting 20s so you can log in if needed...")
        time.sleep(20)
        page.goto("https://authors.curseforge.com/", wait_until="domcontentloaded")
        time.sleep(3)
        page.screenshot(path=str(OUT / "probe-authors-home.png"))
        print("home title:", page.title(), "url:", page.url)
        print(page.locator("body").inner_text()[:1000])
        ctx.close()


if __name__ == "__main__":
    main()
