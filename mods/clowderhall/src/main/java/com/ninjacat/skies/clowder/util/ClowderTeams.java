package com.ninjacat.skies.clowder.util;

import net.minecraft.server.level.ServerPlayer;

import java.lang.reflect.Method;
import java.util.UUID;

/**
 * Soft checks for "same Clowder" without compile deps on Skyblock Builder / FTB Teams.
 * Prefer Skyblock pad team (Create Team / Charter), then FTB party team.
 */
public final class ClowderTeams {
    private ClowderTeams() {}

    public static boolean sameClowder(ServerPlayer a, ServerPlayer b) {
        if (a.getUUID().equals(b.getUUID())) {
            return true;
        }
        if (sameSkyblockTeam(a, b)) {
            return true;
        }
        return sameFtbTeam(a, b);
    }

    private static boolean sameSkyblockTeam(ServerPlayer a, ServerPlayer b) {
        try {
            Class<?> dataClass = Class.forName("de.melanx.skyblockbuilder.data.SkyblockSavedData");
            Method get = dataClass.getMethod("get", net.minecraft.world.level.Level.class);
            // Skyblock island data lives on the overworld — Hall/Nether revive must not miss the team.
            Object data = get.invoke(null, a.server.overworld());
            if (data == null) {
                return false;
            }
            Method teamOf = dataClass.getMethod("getTeamFromPlayer", net.minecraft.world.entity.player.Player.class);
            Object team = teamOf.invoke(data, a);
            if (team == null) {
                return false;
            }
            Method hasPlayer = team.getClass().getMethod("hasPlayer", net.minecraft.world.entity.player.Player.class);
            Object result = hasPlayer.invoke(team, b);
            return Boolean.TRUE.equals(result);
        } catch (ReflectiveOperationException | RuntimeException ignored) {
            return false;
        }
    }

    private static boolean sameFtbTeam(ServerPlayer a, ServerPlayer b) {
        try {
            Class<?> apiClass = Class.forName("dev.ftb.mods.ftbteams.api.FTBTeamsAPI");
            Method apiMethod = apiClass.getMethod("api");
            Object api = apiMethod.invoke(null);
            Method loaded = api.getClass().getMethod("isManagerLoaded");
            if (!Boolean.TRUE.equals(loaded.invoke(api))) {
                return false;
            }
            Method getManager = api.getClass().getMethod("getManager");
            Object manager = getManager.invoke(api);
            Method same = manager.getClass().getMethod("arePlayersInSameTeam", UUID.class, UUID.class);
            Object result = same.invoke(manager, a.getUUID(), b.getUUID());
            return Boolean.TRUE.equals(result);
        } catch (ReflectiveOperationException | RuntimeException ignored) {
            return false;
        }
    }
}
