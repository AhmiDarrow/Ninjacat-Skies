package com.ninjacat.skies.core.network;

import com.ninjacat.skies.core.NinjacatSkies;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/** Server → client: the viewer's Clowder Loom Tension, for horizon tint and Post visuals. */
public record TensionSyncPayload(int strandBits, boolean rewoven) implements CustomPacketPayload {
    public static final Type<TensionSyncPayload> TYPE =
            new Type<>(ResourceLocation.fromNamespaceAndPath(NinjacatSkies.MOD_ID, "tension_sync"));

    public static final StreamCodec<RegistryFriendlyByteBuf, TensionSyncPayload> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.VAR_INT, TensionSyncPayload::strandBits,
            ByteBufCodecs.BOOL, TensionSyncPayload::rewoven,
            TensionSyncPayload::new
    );

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
