"""Finalize CF page content using a Playwright-managed Chrome profile."""
from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

NCS_ROOT = Path(__file__).resolve().parents[1]
ASSETS = NCS_ROOT / "docs" / "public" / "cf-assets"
PROFILE = Path.home() / "AppData" / "Local" / "ms-playwright" / "cf-logged-in"
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
        "id": 1684851,
        "name": "Tribal Power",
        "slug": "tribalpower",
        "summary": (
            "Shamanic technomancy for NeoForge 1.21.1 — Spirit Pulse, Totem Lattice, "
            "Song Bench Echo, and The March."
        ),
        "html": TP_HTML,
        "avatar": ASSETS / "tribal-power-avatar-512.png",
    },
]


def wait_login(page, timeout_s: int = 300) -> None:
    page.goto("https://authors.curseforge.com/", wait_until="domcontentloaded", timeout=90000)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        url = page.url
        text = ""
        try:
            text = page.locator("body").inner_text(timeout=2000)
        except Exception:
            pass
        if "sso.curseforge.com" in url or "Log in with" in text:
            print("WAITING for CurseForge SSO in the Chrome window...", flush=True)
            time.sleep(4)
            continue
        if "authors.curseforge.com" in url:
            print("Logged in:", url, flush=True)
            return
        time.sleep(2)
    raise RuntimeError("login timeout")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            channel="chrome",
            headless=False,
            viewport={"width": 1440, "height": 960},
            args=["--disable-blink-features=AutomationControlled", "--profile-directory=Default"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            wait_login(page, timeout_s=180)
            for proj in PROJECTS:
                pid = proj["id"]
                print(f"\n===== {proj['name']} ({pid}) =====", flush=True)
                detail = page.request.get(f"https://authors.curseforge.com/_api/projects/{pid}").json()
                print("before summary:", detail.get("summary"), flush=True)
                print("before avatar:", detail.get("avatarUrl"), flush=True)

                body = {
                    "name": proj["name"],
                    "slug": proj["slug"],
                    "summary": proj["summary"],
                    "primaryCategoryId": detail.get("primaryCategoryId"),
                    "subCategoryIds": detail.get("subCategoryIds") or [],
                    "allowComments": bool(detail.get("allowComments", True)),
                    "enableProjectPages": bool(detail.get("enableProjectPages", False)),
                }
                r = page.request.put(
                    f"https://authors.curseforge.com/_api/projects/{pid}/update-details",
                    data=json.dumps(body),
                    headers={"Content-Type": "application/json"},
                )
                print("update-details", r.status, r.text()[:300], flush=True)

                desc_ok = False
                for dtype in (1, 2, 0):
                    rr = page.request.put(
                        f"https://authors.curseforge.com/_api/projects/description/{pid}",
                        data=json.dumps({"description": proj["html"], "descriptionType": dtype}),
                        headers={"Content-Type": "application/json"},
                    )
                    print(f"description type={dtype} -> {rr.status} {rr.text()[:180]}", flush=True)
                    if rr.status == 200:
                        desc_ok = True
                        break

                # UI logo pass on General
                page.goto(f"https://authors.curseforge.com/#/projects/{pid}", wait_until="domcontentloaded")
                time.sleep(2)
                page.locator("[role='tab']:has-text('General')").first.click()
                time.sleep(2)
                page.screenshot(path=str(ASSETS / f"final-general-{pid}.png"))

                # Inspect and try logo upload without touching summary markdown uploader
                dom = page.evaluate(
                    """() => {
                      const files = Array.from(document.querySelectorAll('input[type=file]')).map((i, idx) => {
                        const rect = i.getBoundingClientRect();
                        const parentText = (i.parentElement && i.parentElement.innerText || '').slice(0,120);
                        return {idx, cls:i.className, accept:i.accept, parentText, w:rect.width, h:rect.height};
                      });
                      return files;
                    }"""
                )
                print("file inputs:", dom, flush=True)
                (ASSETS / f"final-files-{pid}.json").write_text(json.dumps(dom, indent=2), encoding="utf-8")

                logo_ok = False
                # Prefer file input whose parent mentions logo/avatar and is NOT dzu
                for item in dom:
                    if "dzu" in (item.get("cls") or ""):
                        continue
                    parent = (item.get("parentText") or "").lower()
                    cls = (item.get("cls") or "").lower()
                    if "logo" in parent or "avatar" in parent or "image-input" in cls:
                        page.locator("input[type='file']").nth(item["idx"]).set_input_files(str(proj["avatar"]))
                        print("uploaded via input", item, flush=True)
                        logo_ok = True
                        time.sleep(2)
                        break
                if not logo_ok:
                    # click logo image / change button near top
                    for label in ["Change logo", "Replace", "Upload logo", "Browse"]:
                        try:
                            with page.expect_file_chooser(timeout=1500) as fc:
                                page.get_by_text(label, exact=False).first.click(timeout=1500)
                            fc.value.set_files(str(proj["avatar"]))
                            print("uploaded via", label, flush=True)
                            logo_ok = True
                            time.sleep(2)
                            break
                        except Exception:
                            continue

                # Ensure summary field is clean in UI then save if enabled
                page.evaluate(
                    """(summary) => {
                        const nodes = Array.from(document.querySelectorAll('*'));
                        let lab=null;
                        for (const el of nodes) {
                          const own = Array.from(el.childNodes).filter(n=>n.nodeType===3).map(n=>n.textContent).join('').replace(/\\s+/g,' ').trim().toLowerCase();
                          if (own === 'summary') { lab = el; break; }
                        }
                        if (!lab) return false;
                        let root = lab;
                        for (let i=0;i<8;i++){
                          root = root.parentElement; if(!root) break;
                          const field = root.querySelector('textarea, input[type=text], input:not([type])');
                          if (!field) continue;
                          const proto = field.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;
                          const desc = Object.getOwnPropertyDescriptor(proto,'value');
                          const prev = field.value;
                          desc.set.call(field, summary);
                          const tracker = field._valueTracker;
                          if (tracker) tracker.setValue(prev);
                          field.dispatchEvent(new Event('input',{bubbles:true}));
                          field.dispatchEvent(new Event('change',{bubbles:true}));
                          return true;
                        }
                        return false;
                    }""",
                    proj["summary"],
                )
                saved = False
                btns = page.locator("button:has-text('Save')")
                for i in range(btns.count()):
                    btn = btns.nth(i)
                    try:
                        if btn.is_enabled():
                            btn.click(timeout=3000)
                            saved = True
                            time.sleep(3)
                            break
                    except Exception:
                        continue
                print("ui save", saved, "logo", logo_ok, flush=True)
                page.screenshot(path=str(ASSETS / f"final-after-{pid}.png"))

                # Re-assert clean summary after any UI save side-effects
                r2 = page.request.put(
                    f"https://authors.curseforge.com/_api/projects/{pid}/update-details",
                    data=json.dumps(body),
                    headers={"Content-Type": "application/json"},
                )
                print("re-assert summary", r2.status, flush=True)

                detail2 = page.request.get(f"https://authors.curseforge.com/_api/projects/{pid}").json()
                # Try fetch description endpoint if any
                desc_get = None
                for url in [
                    f"https://authors.curseforge.com/_api/projects/description/{pid}",
                    f"https://authors.curseforge.com/_api/projects/{pid}/description",
                ]:
                    g = page.request.get(url)
                    print("GET", url, g.status, flush=True)
                    if g.status == 200:
                        desc_get = g.text()[:300]
                        break

                entry = {
                    "id": pid,
                    "summary": detail2.get("summary"),
                    "avatarUrl": detail2.get("avatarUrl"),
                    "description_api_ok": desc_ok,
                    "desc_get_sample": desc_get,
                    "update_status": r.status,
                }
                print("FINAL", entry, flush=True)
                results.append(entry)
        finally:
            (ASSETS / "finalize-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
            ctx.close()


if __name__ == "__main__":
    main()
