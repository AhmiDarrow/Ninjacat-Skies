# 0.9.1 — Server installer fixes

Same mods as 0.9.0. Only the dedicated-server installer changes; players do not need to do anything.

- **`install.bat` works on a normal Windows PC.** The 0.9.0 installer stopped at its Java check under Windows
  PowerShell 5.1 and downloaded nothing.
- **Updating no longer leaves old mod versions behind.** Replaced jars move to `mods-removed/` instead of staying in
  `mods/`, where two versions of the same mod stopped the server. Mods you added yourself stay.

**Server owners:** unzip the new server pack over the old folder and run `install` again.
