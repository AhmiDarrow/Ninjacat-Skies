"""Finish General-tab updates (summary + logo + save) for both CF projects."""
from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

NCS_ROOT = Path(__file__).resolve().parents[1]
ASSETS = NCS_ROOT / "docs" / "public" / "cf-assets"
CDP = "http://127.0.0.1:9333"
OUT = ASSETS

PROJECTS = [
    {
        "id": 1684777,
        "name": "Ninjacat Skies",
        "summary": (
            "Void skyblock quest pack — Loom Braid Strands, Tribal Power, "
            "Clowder islands. NeoForge 1.21.1 · 8 GB RAM."
        ),
        "avatar": ASSETS / "ninjacat-skies-avatar-512.png",
        "description_html": (
            NCS_ROOT / "docs" / "public" / "store-description.html"
        ).read_text(encoding="utf-8"),
    },
    {
        "id": 253197,
        "name": "Tribal Power",
        "summary": (
            "Shamanic technomancy for NeoForge 1.21.1 — Spirit Pulse, Totem Lattice, "
            "Song Bench Echo, and The March."
        ),
        "avatar": ASSETS / "tribal-power-avatar-512.png",
        "description_html": (
            NCS_ROOT.parent / "tribal-power" / "docs" / "public" / "store-description.html"
        ).read_text(encoding="utf-8"),
    },
]


def log(msg: str) -> None:
    print(msg, flush=True)


def dump(page, name: str) -> None:
    page.screenshot(path=str(OUT / f"fix-{name}.png"), full_page=False)
    log(f"shot fix-{name}.png")


def click_tab(page, label: str) -> None:
    # Prefer the project settings tab strip (General / Description / License / Export)
    selectors = [
        f"button[role='tab']:has-text('{label}')",
        f"[role='tab']:has-text('{label}')",
        f".MuiTab-root:has-text('{label}')",
        f"button:has-text('{label}')",
    ]
    for sel in selectors:
        loc = page.locator(sel)
        if loc.count() == 0:
            continue
        # Prefer visible ones in main content
        for i in range(loc.count()):
            item = loc.nth(i)
            try:
                if item.is_visible():
                    item.click(timeout=3000)
                    time.sleep(1.5)
                    log(f"clicked tab via {sel} #{i}")
                    return
            except Exception:
                continue
    raise RuntimeError(f"Could not click tab {label}")


def fill_by_nearby_label(page, label: str, value: str) -> bool:
    """Find a label text node and fill the nearest following input/textarea."""
    ok = page.evaluate(
        """({label, value}) => {
            const norm = (s) => (s || '').replace(/\\s+/g, ' ').trim().toLowerCase();
            const want = norm(label);
            const candidates = Array.from(document.querySelectorAll('label, p, span, div, h1, h2, h3, h4, h5, h6'));
            let targetLabel = null;
            for (const el of candidates) {
                const t = norm(el.childNodes.length === 1 ? el.textContent : Array.from(el.childNodes).filter(n => n.nodeType===3).map(n=>n.textContent).join(''));
                if (t === want || t.startsWith(want + ' ')) { targetLabel = el; break; }
                if (norm(el.textContent) === want) { targetLabel = el; break; }
            }
            if (!targetLabel) return {ok:false, reason:'label-not-found'};
            // Walk forward for an input/textarea
            let root = targetLabel.closest('.MuiFormControl-root, .MuiGrid-root, form, section, div') || targetLabel.parentElement;
            const tryFill = (scope) => {
                if (!scope) return false;
                const field = scope.querySelector('textarea, input[type="text"], input:not([type]), input[type="search"]');
                if (!field) return false;
                field.focus();
                const setter = Object.getOwnPropertyDescriptor(field.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype, 'value').set;
                setter.call(field, value);
                field.dispatchEvent(new Event('input', {bubbles:true}));
                field.dispatchEvent(new Event('change', {bubbles:true}));
                return true;
            };
            if (tryFill(root)) return {ok:true, via:'root'};
            // next siblings
            let sib = targetLabel.parentElement;
            for (let i=0; i<5 && sib; i++) {
                if (tryFill(sib)) return {ok:true, via:'ancestor'+i};
                sib = sib.parentElement;
            }
            // aria-labelledby / for=
            if (targetLabel.htmlFor) {
                const f = document.getElementById(targetLabel.htmlFor);
                if (f) {
                    f.focus();
                    const setter = Object.getOwnPropertyDescriptor(f.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype, 'value').set;
                    setter.call(f, value);
                    f.dispatchEvent(new Event('input', {bubbles:true}));
                    f.dispatchEvent(new Event('change', {bubbles:true}));
                    return {ok:true, via:'htmlFor'};
                }
            }
            return {ok:false, reason:'field-not-found', labelText: targetLabel.textContent.slice(0,80)};
        }""",
        {"label": label, "value": value},
    )
    log(f"  fill '{label}': {ok}")
    return bool(ok and ok.get("ok"))


def upload_logo(page, path: Path) -> bool:
    # Prefer .image-input (project logo), not dzu-input (attachments)
    loc = page.locator("input.image-input[type='file']")
    if loc.count() > 0:
        loc.first.set_input_files(str(path))
        time.sleep(2)
        log("  logo via .image-input")
        return True
    loc = page.locator("input[type='file'][accept*='image']")
    if loc.count() > 0:
        loc.first.set_input_files(str(path))
        time.sleep(2)
        log("  logo via accept=image")
        return True
    return False


def save(page) -> bool:
    for sel in [
        "button:has-text('Save Changes')",
        "button:has-text('Save')",
        "button:has-text('Update Project')",
        "button:has-text('Update')",
    ]:
        loc = page.locator(sel)
        for i in range(loc.count()):
            btn = loc.nth(i)
            try:
                if btn.is_visible() and btn.is_enabled():
                    btn.click(timeout=3000)
                    time.sleep(2)
                    log(f"  saved via {sel} #{i}")
                    return True
            except Exception:
                continue
    return False


def set_tinymce(page, html: str) -> bool:
    # TinyMCE react embeds a hidden textarea + iframe
    frames = page.frames
    for fr in frames:
        try:
            url = fr.url or ""
            name = fr.name or ""
            if "tiny" in url.lower() or "tiny" in name.lower() or fr.locator("body#tinymce, body.mce-content-body").count():
                fr.locator("body").evaluate("(el, html) => { el.innerHTML = html; el.dispatchEvent(new Event('input',{bubbles:true})); }", html)
                log("  tinymce body set")
                return True
        except Exception:
            continue
    # Try markdown editor textarea (.mde-text)
    try:
        # Switch to markdown if needed
        page.get_by_role("button", name="Markdown").click(timeout=2000)
        time.sleep(0.5)
    except Exception:
        pass
    try:
        page.locator("textarea.mde-text").fill(html)
        log("  mde-text set")
        return True
    except Exception as e:
        log(f"  mde fail: {e}")
    return False


def update_one(page, project: dict, network_log: list) -> dict:
    result = {"id": project["id"], "steps": []}
    page.goto(f"https://authors.curseforge.com/#/projects/{project['id']}", wait_until="domcontentloaded")
    time.sleep(3)
    dump(page, f"open-{project['id']}")

    # GENERAL
    click_tab(page, "General")
    time.sleep(2)
    dump(page, f"general-{project['id']}")

    # Capture page text labels for debugging
    labels = page.evaluate(
        """() => Array.from(document.querySelectorAll('label,h1,h2,h3,h4,h5,h6,p,span'))
            .map(el => (el.textContent||'').replace(/\\s+/g,' ').trim())
            .filter(t => t && t.length < 40)
            .filter((t,i,a) => a.indexOf(t)===i)
            .slice(0,80)"""
    )
    (OUT / f"labels-{project['id']}.json").write_text(json.dumps(labels, indent=2), encoding="utf-8")
    log(f"  labels sample: {labels[:20]}")

    if fill_by_nearby_label(page, "Summary", project["summary"]):
        result["steps"].append("summary")
    else:
        # Fallback: fill the 2nd visible text input in main (1st often Name)
        filled = page.evaluate(
            """(value) => {
                const inputs = Array.from(document.querySelectorAll('main input[type=text], main textarea, .MuiInputBase-input'))
                    .filter(el => el.offsetParent !== null && !el.disabled);
                // Prefer longer textareas / inputs that already have short summary-like text
                const scored = inputs.map((el, idx) => ({el, idx, len: (el.value||'').length, tag: el.tagName}));
                // Heuristic: summary is often the only textarea or the input after Name
                let target = inputs.find(el => el.tagName === 'TEXTAREA');
                if (!target && inputs.length >= 2) target = inputs[1];
                if (!target && inputs.length >= 1) target = inputs[0];
                if (!target) return false;
                target.focus();
                const proto = target.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
                Object.getOwnPropertyDescriptor(proto, 'value').set.call(target, value);
                target.dispatchEvent(new Event('input', {bubbles:true}));
                target.dispatchEvent(new Event('change', {bubbles:true}));
                return true;
            }""",
            project["summary"],
        )
        log(f"  summary fallback: {filled}")
        if filled:
            result["steps"].append("summary-fallback")

    if upload_logo(page, project["avatar"]):
        result["steps"].append("logo")

    if save(page):
        result["steps"].append("general-saved")
        time.sleep(2)
        dump(page, f"general-saved-{project['id']}")
    else:
        result["steps"].append("general-save-miss")

    # DESCRIPTION reinforce
    click_tab(page, "Description")
    time.sleep(2)
    dump(page, f"desc-{project['id']}")
    if set_tinymce(page, project["description_html"]):
        result["steps"].append("description")
    if save(page):
        result["steps"].append("description-saved")
        time.sleep(2)
        dump(page, f"desc-saved-{project['id']}")

    return result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    network_log: list = []
    results = []
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP)
        ctx = browser.contexts[0]

        def on_response(resp):
            try:
                url = resp.url
                if any(k in url for k in ("project", "author", "forge", "curse", "graphql", "api")):
                    if resp.request.method in ("POST", "PUT", "PATCH"):
                        network_log.append({"method": resp.request.method, "url": url, "status": resp.status})
            except Exception:
                pass

        page = ctx.new_page()
        page.on("response", on_response)
        # Ensure logged in
        page.goto("https://authors.curseforge.com/", wait_until="domcontentloaded")
        time.sleep(2)
        if "sso.curseforge.com" in page.url:
            raise RuntimeError("Not logged in")
        for project in PROJECTS:
            log(f"\n===== {project['name']} =====")
            results.append(update_one(page, project, network_log))
        (OUT / "fix-general-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        (OUT / "network-writes.json").write_text(json.dumps(network_log[-50:], indent=2), encoding="utf-8")
        log(json.dumps(results, indent=2))
        log(f"network writes: {len(network_log)}")


if __name__ == "__main__":
    main()
