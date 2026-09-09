package com.ninjacat.skies.clowder.team;

import net.minecraft.server.MinecraftServer;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModList;

import java.util.Set;
import java.util.UUID;

/**
 * Keeps a Clowder one thing: a Skyblock pad team and its FTB party stay in step, so quests,
 * Loom Tension and shared lives (all keyed on the FTB team) follow the pad with no second step.
 * Named only with native types; the mod-specific work lives behind {@link SkyTeams} / {@link FtbParties},
 * which are only touched when their mods are present.
 */
public final class ClowderSync {
    private ClowderSync() {}

    private static final boolean SKY = ModList.get().isLoaded("skyblockbuilder");
    private static final boolean FTB = ModList.get().isLoaded("ftbteams") && ModList.get().isLoaded("ftblibrary");

    public static void register(IEventBus gameBus) {
        if (SKY) {
            SkyTeams.registerListeners(gameBus);
        }
    }

    /** Forward team actions (invite/accept/join/op-add) turn social defaults on and may create a party; passive ones (login) may only join. */
    public static void reconcileTeam(MinecraftServer server, UUID skyTeamId) {
        reconcileTeam(server, skyTeamId, true);
    }

    public static void reconcileTeam(MinecraftServer server, UUID skyTeamId, boolean allowCreate) {
        if (!SKY || skyTeamId == null) return;
        if (allowCreate) SkyTeams.enableSocial(server, skyTeamId);   // never rewrite a team's settings on a passive login
        Set<UUID> members = SkyTeams.members(server, skyTeamId);
        if (members == null || members.size() < 2) return;
        if (FTB && FtbParties.loaded()) {
            FtbParties.reconcile(server, skyTeamId, members, SkyTeams.name(server, skyTeamId), allowCreate);
        }
    }

    /** Login path: only join an existing mirror party, never create one, so old worlds load unchanged. */
    public static void reconcilePlayer(MinecraftServer server, UUID player) {
        if (!SKY) return;
        UUID teamId = SkyTeams.teamId(server, player);
        if (teamId != null) {
            reconcileTeam(server, teamId, false);
        }
    }

    public static void onLeave(MinecraftServer server, UUID player) {
        if (FTB && FtbParties.loaded()) {
            FtbParties.leaveMirror(server, player);
        }
    }
}
