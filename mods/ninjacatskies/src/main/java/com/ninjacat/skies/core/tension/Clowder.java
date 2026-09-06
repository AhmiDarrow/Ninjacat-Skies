package com.ninjacat.skies.core.tension;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

import java.util.Collection;
import java.util.UUID;

/**
 * A Clowder is whoever shares Loom Tension: the FTB Team when FTB Teams is loaded, otherwise the single player.
 * Data lives in a CompoundTag that persists with the team (or the player's persistent data as a fallback).
 */
public interface Clowder {
    UUID id();

    Component name();

    /** Mutable tag; call {@link #markDirty()} after changing it. */
    CompoundTag data();

    void markDirty();

    Collection<ServerPlayer> onlineMembers();
}
