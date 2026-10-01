package com.ninjacat.skies.core.client;

import com.ninjacat.skies.core.network.FraySyncPayload;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Client-side view of the Fray: where it stands and how far the server has rewoven. Safe to load on a dedicated server. */
public final class ClientFray {
    private static boolean shown;
    /** Parsed once per sync, so the per-frame check compares ids instead of building a string; null never matches. */
    private static ResourceLocation dimension;
    private static int x, y, z;
    /** The server's value. */
    private static float target;
    /** What is drawn: eased toward the target so a seat anywhere on the server thins the cut over a few seconds. */
    private static float displayed = -1F;

    private ClientFray() {}

    public static void handle(FraySyncPayload payload, IPayloadContext context) {
        context.enqueueWork(() -> {
            shown = payload.shown();
            dimension = ResourceLocation.tryParse(payload.dimension());
            x = payload.x();
            y = payload.y();
            z = payload.z();
            target = payload.progress();
            if (displayed < 0F) {
                displayed = target;
            }
        });
    }

    /** Once a client tick. */
    public static void tick() {
        if (displayed < 0F) {
            return;   // nothing from the server yet: the first sync sets it outright
        }
        displayed += (target - displayed) * 0.02F;
        if (Math.abs(target - displayed) < 0.0005F) {
            displayed = target;
        }
    }

    /** On leaving a server: the next one tells us its own Fray. */
    public static void reset() {
        shown = false;
        displayed = -1F;
        target = 0F;
    }

    public static boolean shown() {
        return shown;
    }

    /** Whether the Fray stands in this level: it belongs to Loom's End, and nowhere else. */
    public static boolean standsIn(net.minecraft.world.level.Level level) {
        return shown && level != null && level.dimension().location().equals(dimension);
    }

    public static int x() {
        return x;
    }

    public static int y() {
        return y;
    }

    public static int z() {
        return z;
    }

    /** The server's value, 0 open .. 1 closed. */
    public static float progress() {
        return target;
    }

    /** The eased value the sky is drawn from. */
    public static float displayed() {
        return displayed < 0F ? target : displayed;
    }
}
