# Ninjacat Skies 0.7.2-alpha — packaging

No gameplay changes. This release changes how the pack's own mods are installed, so CurseForge can accept the pack.

- The five companion mods (Ninjacat Lib, Ninjacat Skies, Voidloom, Clowder Hall and the Snapped Guardians) now come from their own CurseForge project, **[Ninjacat Skies Core](https://www.curseforge.com/minecraft/mc-mods/ninjacat-skies-core)**. It is one jar with all five inside, at the same 0.4.1 builds as 0.7.1. The CurseForge app downloads it like any other mod.
- **Tribal Power 3.0.0** is now downloaded from its CurseForge project too, instead of shipping inside the pack.
- The pack no longer carries any mod jars of its own. Mod ids are unchanged, so worlds from 0.7.0 and 0.7.1 load as before.

If you update an existing instance by hand, remove the old loose `ninjacatlib`, `ninjacatskies`, `voidloom`, `clowderhall`, `guardians` and `tribalpower` jars from its `mods` folder first. A fresh import or an update through the CurseForge app handles this for you.

**Dedicated server:** `NinjacatSkies-Server-0.7.2-alpha.zip` no longer includes any jars. `install.sh` / `install.bat` download Ninjacat Skies Core and Tribal Power from CurseForge along with every other mod, checking each file's SHA-1.

- `install.bat` now runs on the Windows PowerShell that ships with Windows (it stopped at the Java check before) and downloads much faster there.
- Updating a server no longer overwrites your settings: the zip carries `server.properties.default` and `user_jvm_args.default.txt`, and `install` only creates `server.properties` / `user_jvm_args.txt` when they don't exist yet.
- `install` moves mods that a new pack version dropped into `mods-removed/`. Jars you added to `mods/` yourself stay put.
- `install.sh --accept-eula` works in unattended setups; without it, a non-interactive run explains how to accept the EULA instead of failing.
