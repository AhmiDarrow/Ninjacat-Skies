package com.ninjacat.skies.core.network;

import com.ninjacat.skies.core.NinjacatSkies;
import com.ninjacat.skies.core.event.DismountRequests;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Client → server: the rider pressed the Dismount key. */
public record DismountPayload() implements CustomPacketPayload {
    public static final DismountPayload INSTANCE = new DismountPayload();
    public static final Type<DismountPayload> TYPE =
            new Type<>(ResourceLocation.fromNamespaceAndPath(NinjacatSkies.MOD_ID, "dismount"));
    public static final StreamCodec<ByteBuf, DismountPayload> STREAM_CODEC = StreamCodec.unit(INSTANCE);

    public static void handle(DismountPayload payload, IPayloadContext context) {
        context.enqueueWork(() -> {
            if (context.player() instanceof ServerPlayer player) DismountRequests.request(player);
        });
    }

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
