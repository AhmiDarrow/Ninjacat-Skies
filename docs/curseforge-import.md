# CurseForge import branding

The GitHub import ZIP includes `profileImage/ninjacat-skies.png`, referenced by the top-level `image` field in `manifest.json`. This matches the export/import implementation in CurseForge app 1.320.0.9172. A root `icon.png` on its own is not enough.

The manifest also credits Ahmi & Risika Darrow as authors. CurseForge may still label imported custom profiles “My creation”; project author links and the full description belong to the published CurseForge project. We do not bundle a machine-specific minecraftinstance.json or falsely link an imported archive to another published file.

The full description ships inside the profile as `store-description.html` and `store-description.md`. For the published project view, see [Ninjacat Skies on CurseForge](https://www.curseforge.com/minecraft/modpacks/ninjacat-skies).

Existing imports do not reread a newly exported manifest. Set the profile image through Profile Options, selecting the included `pack-icon.png`, or import the updated ZIP into a new profile.
