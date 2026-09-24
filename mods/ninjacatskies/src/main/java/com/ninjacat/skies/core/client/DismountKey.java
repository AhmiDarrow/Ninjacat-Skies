package com.ninjacat.skies.core.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.ninjacat.skies.core.network.DismountPayload;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.client.settings.KeyConflictContext;
import net.neoforged.neoforge.network.PacketDistributor;
import org.lwjgl.glfw.GLFW;

/** The Dismount key: gets you off whatever you ride, so sneak is free to steer it. */
public final class DismountKey {
    public static final KeyMapping KEY = new KeyMapping("key.ninjacatskies.dismount", KeyConflictContext.IN_GAME,
            InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_CAPS_LOCK, "key.categories.ninjacatskies");
    private boolean wasRiding;

    public static void register(RegisterKeyMappingsEvent event) {
        event.register(KEY);
    }

    @SubscribeEvent
    public void tick(ClientTickEvent.Post event) {
        var mc = Minecraft.getInstance();
        var player = mc.player;
        if (player == null) return;
        boolean riding = player.isPassenger();
        // Vanilla's "Press Shift to dismount" is no longer true: name the key that is.
        if (riding && !wasRiding) {
            mc.gui.setOverlayMessage(Component.translatable("message.ninjacatskies.dismount_hint", KEY.getTranslatedKeyMessage()), false);
        }
        wasRiding = riding;
        while (KEY.consumeClick()) {
            if (player.isPassenger()) PacketDistributor.sendToServer(DismountPayload.INSTANCE);
        }
    }
}
