#!/usr/bin/env python3
"""Upload a Ninjacat Skies zip through the CurseForge Author Upload API. Cross-platform twin of
upload-curseforge.ps1. Reads CF_AUTHOR_TOKEN / CF_PROJECT_ID from tools/secrets/.env; never prints them.

  python tools/upload_curseforge.py --zip dist/NinjacatSkies-0.2.0-alpha-....zip --release-type alpha \
      --changelog-file dist/changelog.md
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://minecraft.curseforge.com/api"
UA = "ninjacat-skies-uploader/0.2"
MC_TYPE = 77784      # Minecraft 1.21 version type
LOADER_TYPE = 68441  # modloader version type


def load_secrets() -> dict[str, str]:
    env_file = ROOT / "tools/secrets/.env"
    if not env_file.exists():
        raise SystemExit("Missing tools/secrets/.env — copy .env.example and fill it in")
    out: dict[str, str] = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def api_get(path: str, token: str):
    req = urllib.request.Request(API + path, headers={"X-Api-Token": token, "Accept": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def resolve_version_id(versions, name: str, type_id: int) -> int:
    for v in versions:
        if v.get("name") == name and v.get("gameVersionTypeID") == type_id:
            return int(v["id"])
    for v in versions:
        if v.get("name") == name:
            return int(v["id"])
    raise SystemExit(f"Could not resolve game version '{name}' (type {type_id})")


def multipart(fields: dict[str, tuple[str, bytes, str]]) -> tuple[bytes, str]:
    boundary = "----ncs" + uuid.uuid4().hex
    body = bytearray()
    for name, (filename, data, ctype) in fields.items():
        body += f"--{boundary}\r\n".encode()
        disp = f'Content-Disposition: form-data; name="{name}"'
        if filename:
            disp += f'; filename="{filename}"'
        body += (disp + "\r\n").encode()
        body += f"Content-Type: {ctype}\r\n\r\n".encode()
        body += data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return bytes(body), boundary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--project-id", type=int, default=0)
    ap.add_argument("--release-type", choices=["alpha", "beta", "release"], default="alpha")
    ap.add_argument("--display-name", default="")
    ap.add_argument("--changelog-file", default="")
    ap.add_argument("--skip-sanitize", action="store_true")
    args = ap.parse_args()

    if not args.skip_sanitize:
        r = subprocess.run([sys.executable, str(ROOT / "tools/gates/test_sanitized_public_surface.py")])
        if r.returncode != 0:
            raise SystemExit("Sanitization gate failed — refusing to upload")

    secrets = load_secrets()
    token = secrets.get("CF_AUTHOR_TOKEN", "")
    if not token or token.startswith("your-"):
        raise SystemExit("CF_AUTHOR_TOKEN missing from tools/secrets/.env")
    project_id = args.project_id or int(secrets.get("CF_PROJECT_ID", "0") or 0)
    if project_id <= 0:
        raise SystemExit("CF_PROJECT_ID not set — create the project in the Author Console and put its id in tools/secrets/.env")

    zip_path = Path(args.zip)
    if not zip_path.exists():
        raise SystemExit(f"Zip not found: {zip_path}")
    display = args.display_name or zip_path.stem
    changelog = Path(args.changelog_file).read_text(encoding="utf-8") if args.changelog_file else f"## {display}\n\nNinjacat Skies alpha.\n"

    versions = api_get("/game/versions", token)
    game_versions = [resolve_version_id(versions, "1.21.1", MC_TYPE), resolve_version_id(versions, "NeoForge", LOADER_TYPE)]
    metadata = json.dumps({
        "changelog": changelog,
        "changelogType": "markdown",
        "displayName": display,
        "gameVersions": game_versions,
        "releaseType": args.release_type,
    })
    print(f"Uploading {zip_path.name} ({zip_path.stat().st_size // 1024} KiB) → project {project_id} as {args.release_type}; gameVersions={game_versions}")
    body, boundary = multipart({
        "metadata": ("", metadata.encode("utf-8"), "application/json"),
        "file": (zip_path.name, zip_path.read_bytes(), "application/zip"),
    })
    req = urllib.request.Request(
        f"{API}/projects/{project_id}/upload-file",
        data=body,
        method="POST",
        headers={
            "X-Api-Token": token,
            "Accept": "application/json",
            "User-Agent": UA,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            resp = r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Upload failed: HTTP {e.code} {e.read().decode('utf-8', 'ignore')[:500]}")
    parsed = json.loads(resp)
    if not parsed.get("id"):
        raise SystemExit(f"Upload response missing file id: {resp[:300]}")
    print(f"OK — CurseForge file id={parsed['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
