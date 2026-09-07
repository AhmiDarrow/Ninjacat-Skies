"""Check the actual export without extracting untrusted archive paths."""
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath


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
        manifest = json.loads(z.read("manifest.json"))
        if manifest.get("manifestType") != "minecraftModpack" or "overrides" not in manifest:
            raise ValueError("Invalid modpack manifest")
    print(f"PASS ExportDryRun ({archive.name})")


if __name__ == "__main__":
    archives = list(Path(sys.argv[1]).glob("NinjacatSkies-*.zip"))
    if not archives:
        raise SystemExit("No exported archive found")
    verify(max(archives, key=lambda p: p.stat().st_mtime_ns))
