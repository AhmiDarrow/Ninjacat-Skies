package com.ninjacat.skies.core.client;

import com.ninjacat.skies.core.network.TensionSyncPayload;
import com.ninjacat.skies.core.tension.Strand;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Client-side view of the viewer's Clowder Tension. Safe to load on a dedicated server (no client classes). */
public final class ClientTension {
    private static int strandBits;
    private static boolean rewoven;

    private ClientTension() {}

    public static void handle(TensionSyncPayload payload, IPayloadContext context) {
        context.enqueueWork(() -> {
            strandBits = payload.strandBits();
            rewoven = payload.rewoven();
        });
    }

    public static int strandBits() {
        return strandBits;
    }

    public static boolean rewoven() {
        return rewoven;
    }

    public static int seated() {
        return Integer.bitCount(strandBits);
    }

    public static boolean isSeated(Strand s) {
        return (strandBits & s.bit()) != 0;
    }
}
