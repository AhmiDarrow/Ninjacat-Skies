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
        raise SystemExit("Missing tools/secrets/.env - copy .env.example and fill it in")
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


LIVE_FILE = {4, 10}  # Approved, Released
FILE_STATUS = {1: "Processing", 2: "ChangesRequired", 3: "UnderReview", 4: "Approved", 5: "Rejected",
               6: "MalwareDetected", 7: "Deleted", 8: "Archived", 9: "Testing", 10: "Released",
               11: "ReadyForReview", 18: "UnderManualReview"}


def hosted_refs(zip_path: Path) -> list[tuple[int, int, str]]:
    """CurseForge project/file ids the archive tells the app to install."""
    import zipfile
    with zipfile.ZipFile(zip_path) as z:
        name = "server-manifest.json" if "-Server-" in zip_path.name else "manifest.json"
        manifest = json.loads(z.read(name))
    out = []
    for entry in manifest.get("files", []):
        pid, fid = entry.get("projectID"), entry.get("fileID")
        if type(pid) is int and type(fid) is int:
            out.append((pid, fid, str(entry.get("filename") or fid)))
    return out


def require_hosted_files_approved(zip_path: Path, api_key: str) -> None:
    """Pack zips that name an Under Review Core (or any other) file are rejected by CF moderation."""
    if zip_path.suffix.lower() != ".zip":
        return
    if not api_key:
        raise SystemExit("CF_API_KEY missing — cannot confirm hosted files are Approved before upload")
    bad = []
    for pid, fid, filename in hosted_refs(zip_path):
        req = urllib.request.Request(
            f"https://api.curseforge.com/v1/mods/{pid}/files/{fid}",
            headers={"x-api-key": api_key, "Accept": "application/json", "User-Agent": UA},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode())
        st = (data.get("data") or data).get("fileStatus")
        if st not in LIVE_FILE:
            bad.append(f"{filename} (project {pid} file {fid}: {FILE_STATUS.get(st, st)})")
    if bad:
        raise SystemExit("Refusing to upload: manifest names files that are not Approved yet:\n  - " + "\n  - ".join(bad))


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
    ap.add_argument("--environment", choices=["Client", "Server"], action="append", default=[], help="Required environment labels for standalone mods; omit for modpacks")
    ap.add_argument("--parent-file-id", type=int, default=0, help="Upload as an additional file of this CurseForge file (the dedicated-server pack rides on the client zip)")
    args = ap.parse_args()

    if not args.skip_sanitize:
        r = subprocess.run([sys.executable, str(ROOT / "tools/gates/test_sanitized_public_surface.py")])
        if r.returncode != 0:
            raise SystemExit("Sanitization gate failed - refusing to upload")

    secrets = load_secrets()
    token = secrets.get("CF_AUTHOR_TOKEN", "")
    if not token or token.startswith("your-"):
        raise SystemExit("CF_AUTHOR_TOKEN missing from tools/secrets/.env")
    is_tribal = Path(args.zip).name.lower().startswith("tribalpower-")
    if is_tribal and args.project_id not in (0, 1684851):
        raise SystemExit("Tribal Power must upload to its canonical CurseForge project: 1684851")
    project_id = (1684851 if is_tribal else args.project_id or int(secrets.get("CF_PROJECT_ID", "0") or 0))
    if project_id <= 0:
        raise SystemExit("CF_PROJECT_ID not set - create the project in the Author Console and put its id in tools/secrets/.env")

    zip_path = Path(args.zip)
    if not zip_path.exists():
        raise SystemExit(f"Zip not found: {zip_path}")
    if zip_path.suffix.lower() == ".zip":
        from gates.test_export_archive import verify, verify_server
        (verify_server if "-Server-" in zip_path.name else verify)(zip_path)
        require_hosted_files_approved(zip_path, secrets.get("CF_API_KEY", ""))
    display = args.display_name or zip_path.stem
    changelog = Path(args.changelog_file).read_text(encoding="utf-8") if args.changelog_file else f"## {display}\n\nNinjacat Skies alpha.\n"

    versions = api_get("/game/versions", token)
    game_versions = [resolve_version_id(versions, "1.21.1", MC_TYPE), resolve_version_id(versions, "NeoForge", LOADER_TYPE)]
    game_versions.extend(resolve_version_id(versions, name, 75208) for name in dict.fromkeys(args.environment))
    meta = {"changelog": changelog, "changelogType": "markdown", "displayName": display, "releaseType": args.release_type}
    if args.parent_file_id:
        meta["parentFileID"] = args.parent_file_id          # an additional file inherits its parent's game versions; CF rejects both together
    else:
        meta["gameVersions"] = game_versions
    metadata = json.dumps(meta)
    print(f"Uploading {zip_path.name} ({zip_path.stat().st_size // 1024} KiB) -> project {project_id} as {args.release_type}; gameVersions={game_versions}")
    file_ctype = "application/java-archive" if zip_path.suffix.lower() == ".jar" else "application/zip"
    body, boundary = multipart({
        "metadata": ("", metadata.encode("utf-8"), "application/json"),
        "file": (zip_path.name, zip_path.read_bytes(), file_ctype),
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
    print(f"OK - CurseForge file id={parsed['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
