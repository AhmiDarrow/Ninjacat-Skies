# UI and input verification

Use the isolated Tribal Power pack-verification server and pack-client profile. Copy the pack dependency jars, including Patchouli (Nature's Aura requires it), plus the current companion-mod jars. The Tribal Power Gradle run already supplies Tribal Power itself, so do not duplicate its jar.

Set `-Dninjacatskies.uiVerification=true` for `runPackClientVerification`. The opt-in client hook uses the actual held-item entry points for the Whisker Codex and Island Charter, then clicks the configured K and Grave mappings, logging the resulting screen class and taking screenshots. It only runs with the explicit system property.

After the tour, run `python tools/gates/test_pack_keybindings.py ../tribal-power/build/pack-client/options.txt` to verify every preset action exists in the real pack and saves its intended chord. Keep a separate options file with custom bindings to check migration preservation. Normal profiles do not run the UI tour.

Minecraft 1.21.1 places KeyBindsScreen under `net.minecraft.client.gui.screens.options.controls`, not `screens.controls`. Check mapped sources when updating. Use NeoForge's modifier-aware key lookup and release handling; do not use modifier-dependent conflict contexts, which can interfere with releasing held keys.
