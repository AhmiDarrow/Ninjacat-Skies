# Ninjacat Skies 0.7.4

Packaging fix over 0.7.3-alpha. The client zip called `event.addAdvanced` in `kubejs/client_scripts/voidloom_tooltips.js`. KubeJS 2101.7.2 only has `event.add` on `ItemEvents.modifyTooltips`, so Prism/CurseForge installs opened the KubeJS error screen after an otherwise successful load (Core 0.4.2 and Tribal Power 3.2.1 were present).

This release is that tooltip line plus the same 0.7.3-alpha pad. CurseForge file type is **release**.

Pins: Tribal Power 3.2.1 (project 1684851, file **8858043**), Ninjacat Skies Core 0.4.2 (project 1689718, file **8857851**). Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21.
