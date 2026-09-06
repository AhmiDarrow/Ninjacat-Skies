"""Clean polluted summaries and capture Authors Console request bodies."""
from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

NCS_ROOT = Path(__file__).resolve().parents[1]
ASSETS = NCS_ROOT / "docs" / "public" / "cf-assets"
NCS_HTML = (NCS_ROOT / "docs" / "public" / "store-description.html").read_text(encoding="utf-8")
TP_HTML = (
    NCS_ROOT.parent / "tribal-power" / "docs" / "public" / "store-description.html"
).read_text(encoding="utf-8")

PROJECTS = [
    {
        "id": 1684777,
        "name": "Ninjacat Skies",
        "slug": "ninjacat-skies",
        "summary": (
            "Void skyblock quest pack — Loom Braid Strands, Tribal Power, "
            "Clowder islands. NeoForge 1.21.1 · 8 GB RAM."
        ),
        "html": NCS_HTML,
        "avatar": ASSETS / "ninjacat-skies-avatar-512.png",
    },
    {
        "id": 253197,
        "name": "Tribal Power",
        "slug": "tribal-power",
        "summary": (
            "Shamanic technomancy for NeoForge 1.21.1 — Spirit Pulse, Totem Lattice, "
            "Song Bench Echo, and The March."
        ),
        "html": TP_HTML,
        "avatar": ASSETS / "tribal-power-avatar-512.png",
    },
]


def main() -> None:
    captured: list[dict] = []

    def on_request(req):
        if req.method in ("POST", "PUT", "PATCH") and "_api/projects" in req.url:
            body = None
            try:
                body = req.post_data
            except Exception:
                pass
            captured.append(
                {
                    "method": req.method,
                    "url": req.url,
                    "body": (body[:4000] if body else None),
                }
            )
            print("REQ", req.method, req.url, (body or "")[:240], flush=True)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
        ctx = browser.contexts[0]
        page = ctx.new_page()
        page.on("request", on_request)
        page.goto("https://authors.curseforge.com/", wait_until="domcontentloaded")
        time.sleep(1)

        for proj in PROJECTS:
            pid = proj["id"]
            detail = page.request.get(f"https://authors.curseforge.com/_api/projects/{pid}").json()
            body = {
                "name": proj["name"],
                "slug": proj["slug"],
                "summary": proj["summary"],
                "primaryCategoryId": detail.get("primaryCategoryId"),
                "subCategoryIds": detail.get("subCategoryIds") or [],
                "allowComments": detail.get("allowComments", True),
                "enableProjectPages": detail.get("enableProjectPages", False),
            }
            r = page.request.put(
                f"https://authors.curseforge.com/_api/projects/{pid}/update-details",
                data=json.dumps(body),
                headers={"Content-Type": "application/json"},
            )
            print("clean", pid, r.status, r.text()[:300], flush=True)
            detail2 = page.request.get(f"https://authors.curseforge.com/_api/projects/{pid}").json()
            print(" summary now:", detail2.get("summary"), flush=True)

        # Capture UI save bodies for description + avatar on first project
        proj = PROJECTS[0]
        page.goto(
            f"https://authors.curseforge.com/#/projects/{proj['id']}",
            wait_until="domcontentloaded",
        )
        time.sleep(2)

        # General: upload logo via image-input then save
        page.locator("[role='tab']:has-text('General')").first.click()
        time.sleep(1.5)
        # Clear summary field properly with React-aware fill, then save
        page.evaluate(
            """(summary) => {
                const labels = Array.from(document.querySelectorAll('label,p,span,div,h1,h2,h3,h4,h5,h6'));
                const lab = labels.find(el => ((el.textContent||'').trim().toLowerCase()) === 'summary');
                if (!lab) return false;
                const root = lab.closest('.MuiFormControl-root, .MuiGrid-root, form, section, div') || lab.parentElement;
                const field = root && root.querySelector('textarea, input[type="text"], input:not([type])');
                if (!field) return false;
                const proto = field.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
                const desc = Object.getOwnPropertyDescriptor(proto, 'value');
                desc.set.call(field, summary);
                field.dispatchEvent(new Event('input', {bubbles:true}));
                field.dispatchEvent(new Event('change', {bubbles:true}));
                // React 17+ tracker
                const tracker = field._valueTracker;
                if (tracker) tracker.setValue('');
                field.dispatchEvent(new InputEvent('input', {bubbles:true, data: summary}));
                return true;
            }""",
            proj["summary"],
        )
        loc = page.locator("input.image-input[type='file']")
        if loc.count():
            loc.first.set_input_files(str(proj["avatar"]))
            time.sleep(2)
        page.locator("button:has-text('Save')").first.click()
        time.sleep(4)
        page.screenshot(path=str(ASSETS / "capture-general-save.png"))

        # Description tab save
        page.locator("[role='tab']:has-text('Description')").first.click()
        time.sleep(2)
        set_ok = False
        for fr in page.frames:
            try:
                if fr.locator("body#tinymce, body.mce-content-body").count():
                    fr.locator("body").evaluate(
                        "(el, html) => { el.innerHTML = html; el.dispatchEvent(new Event('input',{bubbles:true})); }",
                        proj["html"],
                    )
                    set_ok = True
                    break
            except Exception:
                continue
        print("tinymce set:", set_ok, flush=True)
        page.locator("button:has-text('Save')").first.click()
        time.sleep(4)
        page.screenshot(path=str(ASSETS / "capture-desc-save.png"))

        (ASSETS / "captured-requests.json").write_text(json.dumps(captured, indent=2), encoding="utf-8")
        print(f"captured {len(captured)} requests", flush=True)

        # Final verify via authors API
        for proj in PROJECTS:
            d = page.request.get(f"https://authors.curseforge.com/_api/projects/{proj['id']}").json()
            print(
                f"FINAL {proj['id']} summary={d.get('summary')!r} avatar={d.get('avatarUrl')}",
                flush=True,
            )


if __name__ == "__main__":
    main()
