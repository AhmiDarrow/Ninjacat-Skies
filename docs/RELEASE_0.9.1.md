# Ninjacat Skies 0.9.1 — Server installer fixes

Pack CurseForge client file **(pending)**, server additional **(pending)**.

Same 105 mods as 0.9.0 (101 on the server): Ninjacat Skies Core 0.5.17, Tribal Power 5.3.10, Chocobos Reborn 1.1.0,
Shamanic Mounts 0.1.3. Existing saves load as they are; no quest ids change. Only the dedicated-server installer changes.

- **`install.bat` works on a stock Windows PC.** It runs Windows PowerShell 5.1, where the installer's Java version
  check (`java -version` writes to stderr) was a fatal error: 0.9.0's installer stopped before downloading anything.
  The check now goes through `cmd`.
- **Updating no longer leaves old mod versions behind.** "Unzip the new pack over the old folder and run install" kept
  every replaced jar in `mods/`, so the server found two versions of the same mods and refused to start. Both installers
  now move jars this version no longer ships to `mods-removed/`. `.installed-mods.txt` records what the pack installed,
  so a mod you added yourself stays; on the first update without that record, every jar that is not part of the pack
  moves and is listed so you can put your own back.

Found while updating a live 0.8.16 server to 0.9.0. Both installers were tested on Windows PowerShell 5.1 and bash.
Also in the repo (not in the zips): the gates' own regression suites now run as a gate, and one-off scripts were removed.
