package com.ninjacat.skies.driftwrecks.network;

import com.ninjacat.skies.driftwrecks.Driftwrecks;
import io.netty.buffer.ByteBuf;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/** The Clowder's Driftwreck tag (Atlas, stamps, hints, Keepsakes) for the client's Atlas screen. */
public record AtlasSyncPayload(CompoundTag data) implements CustomPacketPayload {
    public static final Type<AtlasSyncPayload> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath(Driftwrecks.MOD_ID, "atlas_sync"));
    public static final StreamCodec<ByteBuf, AtlasSyncPayload> STREAM_CODEC = ByteBufCodecs.COMPOUND_TAG.map(AtlasSyncPayload::new, AtlasSyncPayload::data);

    @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
}
