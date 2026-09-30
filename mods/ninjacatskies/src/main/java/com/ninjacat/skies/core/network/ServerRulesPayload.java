package com.ninjacat.skies.core.network;

import com.ninjacat.skies.core.NinjacatSkies;
import com.ninjacat.skies.core.config.SkiesConfig;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/**
 * Server → client: the server's config values that change what the client does or shows, so a client never acts
 * on its own copy of the common config. Short Nights steps the client's clock with the server's; with sneak
 * dismounting back on, the Dismount-key hint is not shown. Sent on login and whenever the config reloads.
 */
public record ServerRulesPayload(boolean shortNights, boolean sneakDismounts) implements CustomPacketPayload {
    public static final Type<ServerRulesPayload> TYPE =
            new Type<>(ResourceLocation.fromNamespaceAndPath(NinjacatSkies.MOD_ID, "server_rules"));

    public static final StreamCodec<ByteBuf, ServerRulesPayload> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.BOOL, ServerRulesPayload::shortNights,
            ByteBufCodecs.BOOL, ServerRulesPayload::sneakDismounts,
            ServerRulesPayload::new
    );

    /** The rules as this server's config has them now. */
    public static ServerRulesPayload current() {
        return new ServerRulesPayload(SkiesConfig.SHORT_NIGHTS.get(), SkiesConfig.SNEAK_DISMOUNTS.get());
    }

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
