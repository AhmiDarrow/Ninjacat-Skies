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


SERVER_SCRIPTS = {"install.sh", "install.ps1", "install.bat", "start.sh", "start.bat"}
SECRET_RX = [r"ghp_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}", r"CF_(?:API_KEY|AUTHOR_TOKEN)\s*=\s*\S+", r"BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY",
             r"(?i)C:[\\/]Users[\\/][^\\/\s\"'`]+", r"(?i)(?:/Users|/home)/[^/\s\"'`]+", r"INTERNAL/", r"\$2a\$\d{2}\$"]


def verify_server(archive):
    """The dedicated-server pack: only owned jars under mods/, the named install/start scripts as the only executables,
    a server-manifest whose every file is a positive CurseForge reference with a SHA-1, and no secret or personal text."""
    import re
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad:
            raise ValueError(f"CRC failure: {bad}")
        names = z.namelist()
        for name in names:
            path = PurePosixPath(name.replace("\\", "/"))
            if path.is_absolute() or ".." in path.parts or any(":" in part for part in path.parts):
                raise ValueError(f"Unsafe archive path: {name}")
            if any(part.upper() == "INTERNAL" for part in path.parts) or path.name == ".env" or path.name.endswith(".key"):
                raise ValueError(f"Private content: {name}")
            if path.suffix.lower() in (".ps1", ".bat", ".sh", ".py", ".exe", ".cmd") and not (len(path.parts) == 1 and path.name in SERVER_SCRIPTS):
                raise ValueError(f"Unexpected executable content: {name}")
            if path.suffix.lower() == ".jar" and (path.parent != PurePosixPath("mods") or not is_owned_jar(path.name)):
                raise ValueError(f"Unapproved bundled mod: {name}; the installer must fetch it from CurseForge")
            if path.suffix.lower() in (".md", ".txt", ".json", ".js", ".toml", ".properties", ".default", ".snbt", ".sh", ".ps1", ".bat", ".cfg"):
                text = z.read(name).decode("utf-8", errors="ignore")
                for rx in SECRET_RX:
                    if re.search(rx, text):
                        raise ValueError(f"Secret or personal text in {name}: /{rx}/")
        for required in ("server-manifest.json", "server-mods.txt", "install.sh", "install.ps1", "install.bat", "start.sh", "start.bat",
                         "server.properties.default", "user_jvm_args.default.txt", "README-SERVER.md"):
            if required not in names:
                raise ValueError(f"Server pack is missing {required}")
        manifest = json.loads(z.read("server-manifest.json"))
        projects = set()
        for entry in manifest.get("files", []):
            pid, fid = entry.get("projectID"), entry.get("fileID")
            if type(pid) is not int or type(fid) is not int or pid <= 0 or fid <= 0 or pid in projects or not re.fullmatch(r"[0-9a-f]{40}", str(entry.get("sha1"))) or not entry.get("filename"):
                raise ValueError("Invalid or duplicate CurseForge manifest reference in the server manifest")
            projects.add(pid)
        lines = [l for l in z.read("server-mods.txt").decode("utf-8").splitlines() if l.strip()]
        if len(lines) != len(manifest.get("files", [])):
            raise ValueError("server-mods.txt does not match server-manifest.json")
        if any(n == "eula.txt" for n in names):
            raise ValueError("A server pack must not pre-accept the EULA")
        # Operators unzip updates over their server folder: files they own must never be in the zip.
        for owned in ("server.properties", "user_jvm_args.txt", ".installed-mods.txt"):
            if owned in names:
                raise ValueError(f"Server pack must not ship {owned}: unzipping an update would overwrite the operator's copy")
    print(f"PASS ServerPackDryRun ({archive.name})")


if __name__ == "__main__":
    target = Path(sys.argv[1])
    archives = [target] if target.is_file() else [p for p in target.glob("NinjacatSkies-*.zip") if "-Server-" not in p.name]
    if not archives:
        raise SystemExit("No exported archive found")
    chosen = max(archives, key=lambda p: p.stat().st_mtime_ns)
    (verify_server if "-Server-" in chosen.name else verify)(chosen)
