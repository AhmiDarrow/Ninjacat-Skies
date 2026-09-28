package com.ninjacat.skies.core.network;

import com.ninjacat.skies.core.NinjacatSkies;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/**
 * Server → client: where the Fray stands (dimension and block) and how far the whole server has rewoven (0 open ..
 * 1 closed), so the client can draw the cut in the sky. The place comes from the server's config, not the client's.
 */
public record FraySyncPayload(boolean shown, String dimension, int x, int y, int z, float progress) implements CustomPacketPayload {
    public static final Type<FraySyncPayload> TYPE =
            new Type<>(ResourceLocation.fromNamespaceAndPath(NinjacatSkies.MOD_ID, "fray_sync"));

    public static final StreamCodec<RegistryFriendlyByteBuf, FraySyncPayload> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.BOOL, FraySyncPayload::shown,
            ByteBufCodecs.STRING_UTF8, FraySyncPayload::dimension,
            ByteBufCodecs.INT, FraySyncPayload::x,
            ByteBufCodecs.INT, FraySyncPayload::y,
            ByteBufCodecs.INT, FraySyncPayload::z,
            ByteBufCodecs.FLOAT, FraySyncPayload::progress,
            FraySyncPayload::new
    );

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
