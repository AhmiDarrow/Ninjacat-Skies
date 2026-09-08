"""Check the actual export without extracting untrusted archive paths."""
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cf_distribution import is_owned_jar


def verify(archive):
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad:
            raise ValueError(f"CRC failure: {bad}")
        for name in z.namelist():
            path = PurePosixPath(name.replace("\\", "/"))
            if path.is_absolute() or ".." in path.parts or any(":" in part for part in path.parts):
                raise ValueError(f"Unsafe archive path: {name}")
            if any(part.upper() == "INTERNAL" for part in path.parts) or path.name == ".env" or path.suffix.lower() == ".ps1":
                raise ValueError(f"Private or executable content: {name}")
            if path.suffix.lower() == ".jar" and (path.parent != PurePosixPath("overrides/mods") or not is_owned_jar(path.name)):
                raise ValueError(f"Unapproved bundled mod: {name}; reference its CurseForge file in the manifest")
        manifest = json.loads(z.read("manifest.json"))
        if manifest.get("manifestType") != "minecraftModpack" or "overrides" not in manifest:
            raise ValueError("Invalid modpack manifest")
        projects = set()
        for entry in manifest.get("files", []):
            pid, fid = entry.get("projectID"), entry.get("fileID")
            if type(pid) is not int or type(fid) is not int or pid <= 0 or fid <= 0 or pid in projects:
                raise ValueError("Invalid or duplicate CurseForge manifest reference")
            projects.add(pid)
        icon = manifest.get("image")
        if not icon or icon not in z.namelist():
            raise ValueError("Manifest must reference a bundled profile image for CurseForge import")
        if not z.read(icon).startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("Profile image must be a valid PNG asset")
    print(f"PASS ExportDryRun ({archive.name})")


if __name__ == "__main__":
    target = Path(sys.argv[1])
    archives = [target] if target.is_file() else list(target.glob("NinjacatSkies-*.zip"))
    if not archives:
        raise SystemExit("No exported archive found")
    verify(max(archives, key=lambda p: p.stat().st_mtime_ns))
