package com.ninjacat.skies.core.client;

import com.google.gson.Gson;
import com.mojang.blaze3d.platform.InputConstants;
import com.ninjacat.skies.core.NinjacatSkies;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.options.controls.KeyBindsScreen;
import net.minecraft.network.chat.Component;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.loading.FMLPaths;
import net.neoforged.neoforge.client.event.ScreenEvent;
import net.neoforged.neoforge.client.settings.KeyConflictContext;
import net.neoforged.neoforge.client.settings.KeyModifier;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

/** A versioned, one-time default migration; never ship a complete options.txt over player settings. */
public final class PackKeybindings {
    private record Binding(String name, String key, KeyModifier modifier, String context) {}
    private static final Path MARKER = FMLPaths.CONFIGDIR.get().resolve("ninjacat-keybindings-v1.txt");
    private static final Binding[] PRESET = load();
    private boolean initialized;

    private static Binding[] load() {
        try (var stream = PackKeybindings.class.getResourceAsStream("/assets/ninjacatskies/keybindings.json")) {
            if (stream == null) throw new IllegalStateException("Missing pack keybindings");
            return new Gson().fromJson(new InputStreamReader(stream, StandardCharsets.UTF_8), Binding[].class);
        } catch (Exception ex) { throw new IllegalStateException("Invalid pack keybindings", ex); }
    }

    @SubscribeEvent
    public void screen(ScreenEvent.Init.Post event) {
        if (!initialized) {
            initialized = true;
            apply(false);
        }
        if (event.getScreen() instanceof KeyBindsScreen screen) {
            event.addListener(Button.builder(Component.literal("Pack defaults"), button -> {
                apply(true);
                Minecraft.getInstance().setScreen(screen);
            }).bounds(screen.width-110, 3, 104, 20).build());
        }
    }

    public static void apply(boolean reset) {
        var mc = Minecraft.getInstance();
        boolean migrate = reset || !Files.exists(MARKER);
        Map<String,KeyMapping> keys = new HashMap<>();
        for (var key : mc.options.keyMappings) keys.put(key.getName(), key);
        int changed = 0;
        for (var binding : PRESET) {
            KeyMapping key = keys.get(binding.name());
            if (key == null) continue; // Optional mods remain optional.
            if (migrate && (reset || key.isDefault() || key.isUnbound())) {
                key.setKeyModifierAndCode(binding.modifier(), InputConstants.getKey(binding.key()));
                changed++;
            }
            // NeoForge's modifier-aware lookup gives a modified shortcut priority over
            // the unmodified key and releases held keys correctly when modifiers lift.
            if (binding.context().equals("world")) key.setKeyConflictContext(KeyConflictContext.IN_GAME);
        }
        KeyMapping.resetMapping();
        if (migrate) {
            mc.options.save();
            try {
                Files.createDirectories(MARKER.getParent());
                Files.writeString(MARKER,"Pack bindings v1 applied. Change keys normally in Controls; Pack defaults reapplies this preset.\n",StandardCharsets.UTF_8);
            } catch (Exception ex) { NinjacatSkies.LOGGER.warn("Could not save keybinding migration marker",ex); }
            NinjacatSkies.LOGGER.info("Applied {} pack keybindings; preserved customized bindings",changed);
        }
    }

}
