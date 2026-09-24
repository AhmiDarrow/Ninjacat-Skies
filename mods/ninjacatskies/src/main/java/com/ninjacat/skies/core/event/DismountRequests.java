package com.ninjacat.skies.core.event;

import net.minecraft.server.level.ServerPlayer;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Sneak steers mounts (a chocobo descends, a sneak-click reaches past the saddle), so it no longer dismounts.
 * The Dismount key asks the server instead; the rider's next ride tick honours the request.
 */
public final class DismountRequests {
    /** A request older than this many ticks is dropped rather than dismounting someone later by surprise. */
    private static final long FRESH_TICKS = 10;
    private static final Map<UUID, Long> PENDING = new ConcurrentHashMap<>();

    private DismountRequests() {}

    public static void request(ServerPlayer player) {
        if (player.isPassenger()) PENDING.put(player.getUUID(), player.serverLevel().getGameTime());
    }

    /** True once per request, if it is still fresh. */
    public static boolean take(ServerPlayer player) {
        Long at = PENDING.remove(player.getUUID());
        return at != null && player.serverLevel().getGameTime() - at <= FRESH_TICKS;
    }
}
