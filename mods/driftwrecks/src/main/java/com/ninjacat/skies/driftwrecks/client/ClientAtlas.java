package com.ninjacat.skies.driftwrecks.client;

import net.minecraft.nbt.CompoundTag;

/** The last Driftwreck state the server sent for this player's Clowder. */
public final class ClientAtlas {
    private static CompoundTag data = new CompoundTag();
    private ClientAtlas() {}

    public static void set(CompoundTag tag) { data = tag == null ? new CompoundTag() : tag; }
    public static CompoundTag get() { return data; }
}
