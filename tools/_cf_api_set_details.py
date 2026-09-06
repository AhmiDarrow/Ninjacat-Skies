"""Set CF project summary/description via Authors Console _api using live browser cookies."""
from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

NCS_ROOT = Path(__file__).resolve().parents[1]
ASSETS = NCS_ROOT / "docs" / "public" / "cf-assets"
CDP = "http://127.0.0.1:9333"

NCS_HTML = (NCS_ROOT / "docs" / "public" / "store-description.html").read_text(encoding="utf-8")
TP_HTML = (NCS_ROOT.parent / "tribal-power" / "docs" / "public" / "store-description.html").read_text(encoding="utf-8")

PROJECTS = [
    {
        "id": 1684777,
        "summary": "Void skyblock quest pack — Loom Braid Strands, Tribal Power, Clowder islands. NeoForge 1.21.1 · 8 GB RAM.",
        "description": NCS_HTML,
        "avatar": str(ASSETS / "ninjacat-skies-avatar-512.png"),
    },
    {
        "id": 253197,
        "summary": "Shamanic technomancy for NeoForge 1.21.1 — Spirit Pulse, Totem Lattice, Song Bench Echo, and The March.",
        "description": TP_HTML,
        "avatar": str(ASSETS / "tribal-power-avatar-512.png"),
    },
]


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP)
        ctx = browser.contexts[0]
        page = ctx.new_page()
        page.goto("https://authors.curseforge.com/", wait_until="domcontentloaded")
        time.sleep(2)
        if "sso.curseforge.com" in page.url:
            raise RuntimeError("Not logged in")

        # Discover update-details payload by GETting current project details if possible
        for proj in PROJECTS:
            pid = proj["id"]
            print(f"===== {pid} =====", flush=True)

            # Try common GET endpoints for current details
            detail = None
            for url in [
                f"https://authors.curseforge.com/_api/projects/{pid}",
                f"https://authors.curseforge.com/_api/projects/{pid}/details",
                f"https://authors.curseforge.com/_api/projects/{pid}/update-details",
            ]:
                resp = page.request.get(url)
                print(f"GET {url} -> {resp.status}", flush=True)
                if resp.status == 200:
                    try:
                        detail = resp.json()
                        (ASSETS / f"api-get-{pid}.json").write_text(json.dumps(detail, indent=2), encoding="utf-8")
                        print(f"  keys: {list(detail)[:30] if isinstance(detail, dict) else type(detail)}", flush=True)
                        break
                    except Exception as e:
                        print(f"  json fail: {e}", flush=True)

            # Upload avatar explicitly
            with open(proj["avatar"], "rb") as f:
                upload = page.request.post(
                    f"https://authors.curseforge.com/_api/projects/{pid}/upload-image",
                    multipart={
                        "file": {
                            "name": Path(proj["avatar"]).name,
                            "mimeType": "image/png",
                            "buffer": f.read(),
                        }
                    },
                )
            print(f"upload-image -> {upload.status} {upload.text()[:300]}", flush=True)
            avatar_payload = None
            try:
                avatar_payload = upload.json()
            except Exception:
                pass

            # Build update-details body. Probe a few shapes.
            bodies = []
            if isinstance(detail, dict):
                body = dict(detail)
                # common field names
                for k in list(body.keys()):
                    lk = k.lower()
                    if lk in ("summary", "shortdescription", "short_description", "excerpt"):
                        body[k] = proj["summary"]
                if "summary" not in body:
                    body["summary"] = proj["summary"]
                bodies.append(body)

            bodies.extend(
                [
                    {"summary": proj["summary"]},
                    {"Summary": proj["summary"]},
                    {"shortDescription": proj["summary"]},
                    {"project": {"summary": proj["summary"]}},
                    {"details": {"summary": proj["summary"]}},
                ]
            )
            if avatar_payload:
                bodies.insert(
                    0,
                    {"summary": proj["summary"], "avatar": avatar_payload, "logo": avatar_payload},
                )

            updated = False
            for body in bodies:
                resp = page.request.put(
                    f"https://authors.curseforge.com/_api/projects/{pid}/update-details",
                    data=json.dumps(body),
                    headers={"Content-Type": "application/json"},
                )
                print(f"update-details bodyKeys={list(body)[:8]} -> {resp.status} {resp.text()[:200]}", flush=True)
                if resp.status == 200:
                    updated = True
                    (ASSETS / f"api-update-details-{pid}.json").write_text(
                        json.dumps({"request": body, "response": resp.text()}, indent=2), encoding="utf-8"
                    )
                    break

            # Description API
            desc_bodies = [
                {"description": proj["description"]},
                {"Description": proj["description"]},
                {"html": proj["description"]},
                {"content": proj["description"]},
                {"value": proj["description"]},
                proj["description"],  # raw string
            ]
            for body in desc_bodies:
                headers = {"Content-Type": "application/json"}
                data = body if isinstance(body, str) else json.dumps(body)
                if isinstance(body, str):
                    headers["Content-Type"] = "text/html; charset=utf-8"
                resp = page.request.put(
                    f"https://authors.curseforge.com/_api/projects/description/{pid}",
                    data=data,
                    headers=headers,
                )
                print(f"description type={type(body).__name__} -> {resp.status} {resp.text()[:200]}", flush=True)
                if resp.status == 200:
                    (ASSETS / f"api-description-{pid}.json").write_text(
                        json.dumps({"status": resp.status, "response": resp.text()[:500]}, indent=2), encoding="utf-8"
                    )
                    break

            # Read back via UI
            page.goto(f"https://authors.curseforge.com/#/projects/{pid}", wait_until="domcontentloaded")
            time.sleep(2)
            page.locator("[role='tab']:has-text('General')").first.click()
            time.sleep(1.5)
            page.screenshot(path=str(ASSETS / f"verify-general-{pid}.png"))
            text = page.locator("body").inner_text()
            print("summary visible:", proj["summary"][:40] in text, flush=True)
            print("updated_details:", updated, flush=True)


if __name__ == "__main__":
    main()
