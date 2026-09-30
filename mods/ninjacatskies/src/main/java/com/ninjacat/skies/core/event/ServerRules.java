package com.ninjacat.skies.core.event;

import com.ninjacat.skies.core.network.ServerRulesPayload;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/** Sends {@link ServerRulesPayload} to each player on login, and to everyone after the config reloads. */
public final class ServerRules {
    /** Set from the config-reload event (which may run off the server thread); read on the next server tick. */
    private static volatile boolean dirty;

    public static void markDirty() {
        dirty = true;
    }

    @SubscribeEvent
    public void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) send(player, ServerRulesPayload.current());
    }

    @SubscribeEvent
    public void onServerTick(ServerTickEvent.Post event) {
        if (!dirty) return;
        dirty = false;
        broadcast(event.getServer());
    }

    public static void broadcast(MinecraftServer server) {
        ServerRulesPayload payload = ServerRulesPayload.current();
        for (ServerPlayer player : server.getPlayerList().getPlayers()) send(player, payload);
    }

    private static void send(ServerPlayer player, ServerRulesPayload payload) {
        // A connection that never negotiated the channel (a GameTest mock player) cannot take it: sending would throw.
        if (player.connection == null || !player.connection.hasChannel(ServerRulesPayload.TYPE)) return;
        PacketDistributor.sendToPlayer(player, payload);
    }
}
