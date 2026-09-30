package com.ninjacat.skies.core.client;

import com.ninjacat.skies.core.network.ServerRulesPayload;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/**
 * The server's rules as it last sent them ({@link ServerRulesPayload}). Until a server says otherwise the client
 * assumes vanilla: no Short Nights and sneak dismounts. Safe to load on a dedicated server.
 */
public final class ClientServerRules {
    private static volatile boolean shortNights = false;
    private static volatile boolean sneakDismounts = true;

    private ClientServerRules() {}

    public static void handle(ServerRulesPayload payload, IPayloadContext context) {
        context.enqueueWork(() -> apply(payload));
    }

    public static void apply(ServerRulesPayload payload) {
        shortNights = payload.shortNights();
        sneakDismounts = payload.sneakDismounts();
    }

    /** On leaving a server: the next one sends its own rules. */
    public static void reset() {
        shortNights = false;
        sneakDismounts = true;
    }

    public static boolean shortNights() {
        return shortNights;
    }

    public static boolean sneakDismounts() {
        return sneakDismounts;
    }
}
