"""Upload CurseForge project logos via Author Console General tab."""
from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

NCS_ROOT = Path(__file__).resolve().parents[1]
ASSETS = NCS_ROOT / "docs" / "public" / "cf-assets"
PROJECTS = [
    (1684777, ASSETS / "ninjacat-skies-avatar-512.png"),
    (253197, ASSETS / "tribal-power-avatar-512.png"),
]


def main() -> None:
    captured: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
        page = browser.contexts[0].new_page()

        def on_req(req):
            if req.method in ("POST", "PUT") and "_api/projects" in req.url:
                body = None
                try:
                    body = req.post_data
                except Exception:
                    pass
                captured.append({"method": req.method, "url": req.url, "body": (body[:800] if body else None)})
                print("REQ", req.method, req.url, (body or "")[:160], flush=True)

        page.on("request", on_req)

        for pid, avatar in PROJECTS:
            print(f"===== logo {pid} =====", flush=True)
            page.goto(f"https://authors.curseforge.com/#/projects/{pid}", wait_until="domcontentloaded")
            time.sleep(2)
            page.locator("[role='tab']:has-text('General')").first.click()
            time.sleep(2)
            page.screenshot(path=str(ASSETS / f"logo-before-{pid}.png"))

            info = page.evaluate(
                """() => {
                  const out=[];
                  document.querySelectorAll('input[type=file]').forEach((i,idx)=>{
                    const r=i.getBoundingClientRect();
                    let p=i.parentElement; let txt='';
                    for (let k=0;k<5 && p;k++){ txt += ' ' + (p.innerText||'').slice(0,100); p=p.parentElement; }
                    out.push({idx, cls:i.className, accept:i.accept, txt:txt.replace(/\\s+/g,' ').trim().slice(0,200), w:r.width, h:r.height, top:r.top, left:r.left});
                  });
                  const labels=[...document.querySelectorAll('button,label,span,p,h1,h2,h3,h4')]
                    .map(e=>(e.textContent||'').replace(/\\s+/g,' ').trim())
                    .filter(t=>/logo|avatar|image|upload|change|browse|replace/i.test(t))
                    .filter((t,i,a)=>a.indexOf(t)===i).slice(0,40);
                  const imgs=[...document.querySelectorAll('img')].filter(i=>i.width>=48).map(i=>({
                    src:i.src, w:i.width, h:i.height, alt:i.alt, cls:(i.className||'').toString().slice(0,80)
                  }));
                  return {files:out, labels, imgs:imgs.slice(0,20)};
                }"""
            )
            (ASSETS / f"logo-info-{pid}.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
            print("labels:", info.get("labels"), flush=True)
            print("files:", info.get("files"), flush=True)

            uploaded = False

            # 1) Click avatar/logo image
            for img in info.get("imgs", []):
                src = img.get("src") or ""
                if "avatar" not in src and "forgecdn" not in src:
                    continue
                try:
                    with page.expect_file_chooser(timeout=2500) as fc:
                        page.locator(f"img[src='{src}']").first.click(timeout=2500)
                    fc.value.set_files(str(avatar))
                    print("clicked avatar img", src[:100], flush=True)
                    uploaded = True
                    time.sleep(3)
                    break
                except Exception as e:
                    print("img click fail", e, flush=True)

            # 2) Labels
            if not uploaded:
                for label in info.get("labels", []):
                    try:
                        with page.expect_file_chooser(timeout=1500) as fc:
                            page.get_by_text(label, exact=True).first.click(timeout=1500)
                        fc.value.set_files(str(avatar))
                        print("clicked label", label, flush=True)
                        uploaded = True
                        time.sleep(3)
                        break
                    except Exception:
                        continue

            # 3) image-input near Logo text (skip dzu)
            if not uploaded:
                for f in info.get("files", []):
                    cls = f.get("cls") or ""
                    txt = (f.get("txt") or "").lower()
                    if "dzu" in cls:
                        continue
                    if "logo" in txt or "avatar" in txt or "image-input" in cls:
                        page.locator("input[type=file]").nth(f["idx"]).set_input_files(str(avatar))
                        print("set files", f, flush=True)
                        uploaded = True
                        time.sleep(3)
                        break

            # Save
            btns = page.locator("button:has-text('Save')")
            for i in range(btns.count()):
                b = btns.nth(i)
                try:
                    if b.is_enabled():
                        b.click()
                        print("saved", flush=True)
                        time.sleep(3)
                        break
                except Exception:
                    pass

            page.screenshot(path=str(ASSETS / f"logo-after-{pid}.png"))
            after = page.request.get(f"https://authors.curseforge.com/_api/projects/{pid}").json()
            print("avatar now", after.get("avatarUrl"), flush=True)
            print("summary now", after.get("summary"), flush=True)

            # Re-clean summary if polluted again
            if after.get("summary") and "Uploading image" in after["summary"]:
                body = {
                    "name": after.get("name"),
                    "slug": after.get("slug"),
                    "summary": after["summary"].split("![Uploading image")[0].strip(),
                    "primaryCategoryId": after.get("primaryCategoryId"),
                    "subCategoryIds": after.get("subCategoryIds") or [],
                    "allowComments": bool(after.get("allowComments", True)),
                    "enableProjectPages": bool(after.get("enableProjectPages", False)),
                }
                r = page.request.put(
                    f"https://authors.curseforge.com/_api/projects/{pid}/update-details",
                    data=json.dumps(body),
                    headers={"Content-Type": "application/json"},
                )
                print("re-clean", r.status, flush=True)

        (ASSETS / "logo-captured.json").write_text(json.dumps(captured, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
