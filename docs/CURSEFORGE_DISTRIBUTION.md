# CurseForge dependency packaging

CurseForge rejected file 8834868 because hosted dependencies were bundled as override jars, including two jars whose licenses forbid redistribution. Missing IDs used to fall back to copying a jar into the ZIP. That fallback has been removed.

Every external dependency must have a positive project ID, file ID and verified SHA-1 in `pack/modlist-resolved.json`. An unresolved file or changed local artifact now stops export. Duplicate project references are rejected. Tribal Power must use project 1684851 and is installed through the manifest like the other hosted mods.

Only the four original companion mods in this repository may be bundled: Ninjacat Skies, Ninjacat Lib, Clowder Hall and Voidloom. Third-party jars cannot be placed in `pack/overrides` or included through self-contained mode. Python and PowerShell exports use one implementation; both upload tools validate the actual archive.

`python -X utf8 tools/resolve_cf_manifest.py --write` resolves previously unreferenced local jars using the official [CurseForge fingerprint API](https://docs.curseforge.com/rest-api/), then confirms the SHA-1. If a file does not match, find its exact Minecraft/loader version on the original project and download the official artifact. Do not invent file IDs or treat an absent match as permission to bundle. Replacing a file requires reviewing code/resource differences and appropriate runtime checks.

For 0.6.3, all 88 dependencies were checked against their official available file records. Sophisticated Storage uses project 619320/file 8687896; TrashSlot uses project 235577/file 8163135. Their same-version official artifacts preserve gameplay content. Just Enough Professions similarly uses project 417645/file 7966681.

Run `python -X utf8 tools/gates/test_cf_distribution.py`, the normal pack gates, and `python -X utf8 tools/gates/test_export_archive.py dist` before release. A successful upload is submission only; moderation approval remains a separate CurseForge decision.
