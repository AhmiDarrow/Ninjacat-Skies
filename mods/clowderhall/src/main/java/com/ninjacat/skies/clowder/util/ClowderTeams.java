package com.ninjacat.skies.clowder.util;

import com.ninjacat.skies.clowder.team.FtbParties;
import com.ninjacat.skies.clowder.team.SkyTeams;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.fml.ModList;

/**
 * "Same Clowder?" — the Skyblock pad team when Skyblock Builder is present, then the FTB party.
 * Calls both APIs directly (guarded by ModList); the mod-typed work is isolated in the team package,
 * so nothing here is resolved unless the relevant mod is loaded.
 */
public final class ClowderTeams {
    private ClowderTeams() {}

    private static final boolean SKY = ModList.get().isLoaded("skyblockbuilder");
    private static final boolean FTB = ModList.get().isLoaded("ftbteams");

    public static boolean sameClowder(ServerPlayer a, ServerPlayer b) {
        if (a.getUUID().equals(b.getUUID())) {
            return true;
        }
        if (SKY && SkyTeams.sameTeam(a.server, a.getUUID(), b.getUUID())) {
            return true;
        }
        return FTB && FtbParties.loaded() && FtbParties.sameTeam(a.server, a.getUUID(), b.getUUID());
    }
}
