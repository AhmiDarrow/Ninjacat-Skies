# Ninjacat Skies 0.6.3-alpha — CurseForge distribution correction

This release corrects the packaging rejected for 0.6.2. All 88 CurseForge-hosted dependencies are now referenced by project ID and file ID in manifest.json. The CurseForge app downloads them from their original projects. Only Ninjacat Skies, Ninjacat Lib, Clowder Hall and Voidloom remain bundled as our own companion mods.

Sophisticated Storage 1.5.91.2127 and TrashSlot 21.1.11 are installed through CurseForge, not redistributed in the ZIP. Tribal Power uses project 1684851, file 8828297. All 25 other jars listed by moderation now have exact hash-verified manifest references; Just Enough Professions is referenced as well.

No gameplay version changes: the three jars that differed from the official archives were replaced with same-version CurseForge artifacts. Their class files and resources are identical; differences were ZIP packaging or META-INF/MANIFEST.MF metadata. Quest rewards, configs, worlds, teams and save data are unchanged from 0.6.2.

The exporter now refuses unresolved or hash-mismatched dependencies. Self-contained third-party exports are disabled. Both export entry points use the same rules, and uploads reject unexpected bundled jars before contacting CurseForge.

Validation: 88 official file IDs and SHA-1 hashes verified against CurseForge; archive contains 88 manifest entries and four companion jars. Regression tests reject the formerly accepted 0.6.2 archive and catch unresolved dependencies, changed jars and prohibited override jars. Pack gates pass.

Minecraft 1.21.1 / NeoForge 21.1.249 / Java 21. Import the attached ZIP using CurseForge.
