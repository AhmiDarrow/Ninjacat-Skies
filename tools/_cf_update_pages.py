"""Update CurseForge Author Console pages via an already-running Chrome (CDP).

Launch Chrome with --remote-debugging-port=9333 first, sign into Authors Console,
then run this script.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "public" / "cf-assets"
OUT = ASSETS
CDP = "http://127.0.0.1:9333"

NCS = {
    "id": 1684777,
    "slug": "ninjacat-skies",
    "name": "Ninjacat Skies",
    "kind": "modpack",
    "summary": (
        "Void skyblock quest pack — Loom Braid Strands, Tribal Power, "
        "Clowder islands. NeoForge 1.21.1 · 8 GB RAM."
    ),
    "description_html": (ROOT / "docs" / "public" / "store-description.html").read_text(encoding="utf-8"),
    "avatar": ASSETS / "ninjacat-skies-avatar-512.png",
}
TP = {
    "id": 253197,
    "slug": "tribal-power",
    "name": "Tribal Power",
    "kind": "mod",
    "summary": (
        "Shamanic technomancy for NeoForge 1.21.1 — Spirit Pulse, Totem Lattice, "
        "Song Bench Echo, and The March."
    ),
    "description_html": (
        ROOT.parent / "tribal-power" / "docs" / "public" / "store-description.html"
    ).read_text(encoding="utf-8"),
    "avatar": ASSETS / "tribal-power-avatar-512.png",
}


def log(msg: str) -> None:
    print(msg, flush=True)


def dump(page, name: str) -> None:
    page.screenshot(path=str(OUT / f"update-{name}.png"), full_page=False)
    try:
        (OUT / f"update-{name}.txt").write_text(page.locator("body").inner_text()[:5000], encoding="utf-8")
    except Exception:
        pass
    log(f"dumped {name}")


def wait_logged_in(page, timeout_s: int = 600) -> None:
    page.goto("https://authors.curseforge.com/", wait_until="domcontentloaded", timeout=90000)
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        url = page.url
        try:
            text = page.locator("body").inner_text(timeout=3000)
        except Exception:
            text = ""
        if "sso.curseforge.com" in url or re.search(r"Log in with|Welcome back to CurseForge", text):
            log("WAITING: finish CurseForge SSO in the open Chrome window...")
            time.sleep(4)
            continue
        if "authors.curseforge.com" in url and (
            "Dashboard" in text or "Projects" in text or "Create A Project" in text or "Reward" in text
        ):
            log(f"Logged in at {url}")
            return
        # Sometimes SPA loads before body text settles
        if "authors.curseforge.com" in url and "sso" not in url:
            time.sleep(2)
            text2 = page.locator("body").inner_text()
            if "Log in with" not in text2:
                log(f"Assuming logged in at {url}")
                return
        time.sleep(3)
    raise RuntimeError("Timed out waiting for Author Console login")


def try_click(page, selectors: list[str], timeout: int = 4000) -> bool:
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() == 0:
                continue
            loc.click(timeout=timeout)
            return True
        except Exception:
            continue
    return False


def fill_first(page, selectors: list[str], value: str) -> bool:
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() == 0:
                continue
            loc.click(timeout=2000)
            # clear then fill
            loc.fill("")
            loc.fill(value, timeout=8000)
            return True
        except Exception:
            continue
    return False


def set_description_html(page, html: str) -> bool:
    # Try switch to HTML/Markdown source mode first for reliable paste
    try_click(
        page,
        [
            "button:has-text('HTML')",
            "button:has-text('Markdown')",
            "button:has-text('Source')",
            "[role=tab]:has-text('HTML')",
            "[role=tab]:has-text('Markdown')",
            "text=HTML",
            "text=Markdown",
        ],
    )
    time.sleep(1)

    for sel in [
        "textarea[name*='description' i]",
        "textarea#description",
        "textarea[placeholder*='description' i]",
        "textarea",
        ".cm-content",
        "div[contenteditable='true']",
        ".ProseMirror",
        ".ql-editor",
    ]:
        try:
            loc = page.locator(sel).first
            if loc.count() == 0:
                continue
            tag = loc.evaluate("el => el.tagName.toLowerCase()")
            if tag == "textarea":
                loc.fill(html)
                return True
            loc.click()
            ok = page.evaluate(
                """({sel, html}) => {
                    const el = document.querySelector(sel);
                    if (!el) return false;
                    el.focus();
                    if ('value' in el) { el.value = html; }
                    else { el.innerHTML = html; }
                    el.dispatchEvent(new Event('input', {bubbles:true}));
                    el.dispatchEvent(new Event('change', {bubbles:true}));
                    return true;
                }""",
                {"sel": sel, "html": html},
            )
            if ok:
                return True
        except Exception as e:
            log(f"  desc {sel}: {e}")
    # TinyMCE iframe
    try:
        frame = page.frame_locator("iframe.tox-edit-area__iframe, .tox-edit-area iframe").first
        frame.locator("body").evaluate("(el, html) => { el.innerHTML = html }", html)
        return True
    except Exception:
        pass
    return False


def upload_avatar(page, path: Path) -> bool:
    inputs = page.locator("input[type='file']")
    n = inputs.count()
    log(f"  file inputs: {n}")
    for i in range(n):
        inp = inputs.nth(i)
        try:
            accept = (inp.get_attribute("accept") or "").lower()
            if accept and not any(x in accept for x in ("image", "png", "jpg", "*")):
                continue
            inp.set_input_files(str(path))
            log(f"  uploaded via input[{i}] accept={accept}")
            time.sleep(2)
            return True
        except Exception as e:
            log(f"  input[{i}] fail: {e}")
    for label in ["Change logo", "Upload logo", "Choose File", "Browse", "Change avatar", "Upload", "Logo"]:
        try:
            with page.expect_file_chooser(timeout=2500) as fc_info:
                page.get_by_text(label, exact=False).first.click(timeout=2500)
            fc_info.value.set_files(str(path))
            log(f"  uploaded via chooser '{label}'")
            time.sleep(2)
            return True
        except Exception:
            continue
    return False


def save_project(page) -> bool:
    return try_click(
        page,
        [
            "button:has-text('Save Changes')",
            "button:has-text('Save')",
            "button:has-text('Update')",
            "button[type='submit']",
            "text=Save Changes",
            "text=Save",
        ],
        timeout=5000,
    )


def open_project(page, project: dict) -> None:
    urls = [
        f"https://authors.curseforge.com/#/projects/{project['id']}",
        f"https://authors.curseforge.com/#/project/{project['id']}",
        f"https://authors.curseforge.com/#/projects/{project['id']}/general",
        f"https://authors.curseforge.com/#/projects/{project['id']}/description",
    ]
    for u in urls:
        log(f"open {u}")
        page.goto(u, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        if "sso.curseforge.com" in page.url:
            wait_logged_in(page)
            page.goto(u, wait_until="domcontentloaded", timeout=60000)
            time.sleep(3)
        body = page.locator("body").inner_text()
        if any(k in body for k in (project["name"], "Summary", "Description", "General", "Logo", "Avatar")):
            dump(page, f"open-{project['id']}")
            return
    page.goto("https://authors.curseforge.com/#/projects", wait_until="domcontentloaded")
    time.sleep(3)
    dump(page, f"list-{project['id']}")
    if not try_click(page, [f"text={project['name']}", f"a:has-text('{project['name']}')"]):
        raise RuntimeError(f"Could not open {project['name']}")
    time.sleep(3)
    dump(page, f"open-{project['id']}")


def dump_inputs(page, project_id: int) -> None:
    try:
        info = page.evaluate(
            """() => Array.from(document.querySelectorAll('input,textarea,[contenteditable],iframe,button')).slice(0,80).map(el => ({
                tag: el.tagName, type: el.type||null, name: el.name||null, id: el.id||null,
                text: (el.innerText||'').slice(0,60),
                placeholder: el.placeholder||null,
                cls: el.className && String(el.className).slice(0,100)
            }))"""
        )
        (OUT / f"inputs-{project_id}.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
        log(f"  wrote inputs-{project_id}.json ({len(info)})")
    except Exception as e:
        log(f"  input dump fail: {e}")


def update_project(page, project: dict) -> dict:
    result = {"id": project["id"], "name": project["name"], "steps": []}
    open_project(page, project)

    try_click(page, ["text=General", "a:has-text('General')", "[role=tab]:has-text('General')", "button:has-text('General')"])
    time.sleep(2)
    dump(page, f"general-{project['id']}")
    dump_inputs(page, project["id"])

    filled = fill_first(
        page,
        [
            "textarea[name*='summary' i]",
            "input[name*='summary' i]",
            "textarea[placeholder*='summary' i]",
            "input[placeholder*='summary' i]",
            "textarea#summary",
            "input#summary",
            "textarea[name*='short' i]",
        ],
        project["summary"],
    )
    if not filled:
        try:
            page.get_by_label(re.compile("summary", re.I)).fill(project["summary"])
            filled = True
        except Exception as e:
            result["steps"].append(f"summary-miss:{e}")
            log(f"  summary miss: {e}")
    if filled:
        result["steps"].append("summary-filled")
        log("  summary filled")

    if upload_avatar(page, project["avatar"]):
        result["steps"].append("avatar-uploaded")
    else:
        result["steps"].append("avatar-miss")

    if save_project(page):
        result["steps"].append("general-saved")
        time.sleep(2)
    else:
        result["steps"].append("general-save-miss")

    try_click(page, ["text=Description", "a:has-text('Description')", "[role=tab]:has-text('Description')", "button:has-text('Description')"])
    time.sleep(2)
    dump(page, f"description-{project['id']}")
    dump_inputs(page, int(f"{project['id']}2"))

    if set_description_html(page, project["description_html"]):
        result["steps"].append("description-filled")
        log("  description filled")
    else:
        result["steps"].append("description-miss")
        log("  description miss")

    if save_project(page):
        result["steps"].append("description-saved")
        time.sleep(2)
    else:
        result["steps"].append("description-save-miss")

    dump(page, f"done-{project['id']}")
    return result


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP)
        ctx = browser.contexts[0]
        page = ctx.new_page()
        wait_logged_in(page, timeout_s=600)
        dump(page, "home")
        for project in (NCS, TP):
            log(f"\n===== {project['name']} ({project['id']}) =====")
            try:
                results.append(update_project(page, project))
            except Exception as e:
                log(f"FAILED {project['name']}: {e}")
                results.append({"id": project["id"], "name": project["name"], "error": str(e), "steps": []})
                dump(page, f"error-{project['id']}")
        (OUT / "update-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        log(json.dumps(results, indent=2))
    ok = any("summary-filled" in r.get("steps", []) or "description-filled" in r.get("steps", []) for r in results)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
