package com.ninjacat.skies.driftwrecks.client;

import net.minecraft.client.Minecraft;

/** Client-only calls made from common code, isolated so servers never load client classes. */
public final class ClientHooks {
    private ClientHooks() {}

    public static void openAtlas() { Minecraft.getInstance().setScreen(new AtlasScreen()); }
}
