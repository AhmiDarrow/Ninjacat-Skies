package com.ninjacat.skies.guardians.network;

import com.ninjacat.skies.guardians.Guardians;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;

/**
 * Server → client: the guardian track this player's fight plays ({@code guardians:music.<id>}), or "" once the
 * player is out of a running fight (a win, a wipe, leaving, dying). The client's music manager plays it in place of
 * the situational music, the way vanilla plays the dragon fight's.
 */
public record GuardianMusicPayload(String track) implements CustomPacketPayload {
    public static final Type<GuardianMusicPayload> TYPE =
            new Type<>(ResourceLocation.fromNamespaceAndPath(Guardians.MOD_ID, "music"));

    public static final StreamCodec<ByteBuf, GuardianMusicPayload> STREAM_CODEC =
            ByteBufCodecs.STRING_UTF8.map(GuardianMusicPayload::new, GuardianMusicPayload::track);

    public static final GuardianMusicPayload NONE = new GuardianMusicPayload("");

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }
}
