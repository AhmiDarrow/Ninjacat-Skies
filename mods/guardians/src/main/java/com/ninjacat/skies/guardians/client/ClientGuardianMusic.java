package com.ninjacat.skies.guardians.client;

import com.ninjacat.skies.guardians.network.GuardianMusicPayload;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/**
 * The fight track the server last told this client to play ("" none). Pure state, safe to load on a dedicated
 * server; {@link GuardianMusicPlayer} (client only) hands it to the music manager.
 */
public final class ClientGuardianMusic {
    private static volatile String track = "";

    private ClientGuardianMusic() {}

    public static void handle(GuardianMusicPayload payload, IPayloadContext context) {
        context.enqueueWork(() -> track = payload.track());
    }

    public static String track() {
        return track;
    }

    /** On leaving a server. */
    public static void reset() {
        track = "";
    }
}
