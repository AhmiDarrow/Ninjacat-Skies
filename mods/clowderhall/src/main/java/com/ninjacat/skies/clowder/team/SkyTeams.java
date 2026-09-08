package com.ninjacat.skies.clowder.team;

import de.melanx.skyblockbuilder.data.SkyblockSavedData;
import de.melanx.skyblockbuilder.data.Team;
import de.melanx.skyblockbuilder.events.SkyblockCreateTeamEvent;
import de.melanx.skyblockbuilder.events.SkyblockInvitationEvent;
import de.melanx.skyblockbuilder.events.SkyblockJoinRequestEvent;
import de.melanx.skyblockbuilder.events.SkyblockManageTeamEvent;
import de.melanx.skyblockbuilder.events.SkyblockOpManageEvent;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.server.ServerLifecycleHooks;

import java.util.Set;
import java.util.UUID;

/**
 * Direct Skyblock Builder access. Only referenced when "skyblockbuilder" is loaded — never touch
 * this class outside a ModList guard, or the JVM will try to resolve Skyblock classes that may be absent.
 * Returns and takes only vanilla / native types so {@link ClowderSync} never names a Skyblock class.
 */
public final class SkyTeams {
    private SkyTeams() {}

    // Result codes shared with the commands / Charter (kept as ints so callers need not load this class' enums).
    public static final int OK = 1;
    public static final int NO_TEAM = -1;      // invite: actor has no team | accept: no pending invite
    public static final int TARGET_TEAM = -2;  // invite: target already on a team | accept: you already on a team
    public static final int BAD = -3;          // self-invite / internal failure

    private static SkyblockSavedData data(MinecraftServer server) {
        return SkyblockSavedData.get(server.overworld());
    }

    public static void registerListeners(IEventBus bus) {
        bus.addListener(SkyTeams::onCreate);
        bus.addListener(SkyTeams::onAccept);
        bus.addListener(SkyTeams::onJoinAccepted);
        bus.addListener(SkyTeams::onOpAdd);
        bus.addListener(SkyTeams::onLeave);
        bus.addListener(SkyTeams::onLogin);
    }

    private static void onCreate(SkyblockCreateTeamEvent event) {
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null) return;
        String name = event.getName();
        server.execute(() -> enableSocialByName(server, name));
    }

    private static void onAccept(SkyblockInvitationEvent.Accept event) {
        deferReconcile(event.getTeam());
    }

    private static void onJoinAccepted(SkyblockJoinRequestEvent.AcceptRequest event) {
        deferReconcile(event.getTeam());
    }

    private static void onOpAdd(SkyblockOpManageEvent.AddToTeam event) {
        deferReconcile(event.getTeam());
    }

    private static void onLeave(SkyblockManageTeamEvent.Leave event) {
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null || event.getPlayer() == null) return;
        UUID left = event.getPlayer().getUUID();
        server.execute(() -> ClowderSync.onLeave(server, left));
    }

    private static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        MinecraftServer server = player.server;
        UUID id = player.getUUID();
        // Give Skyblock a couple of ticks to settle team/login state before mirroring.
        server.execute(() -> server.execute(() -> ClowderSync.reconcilePlayer(server, id)));
    }

    private static void deferReconcile(Team team) {
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null || team == null) return;
        UUID id = team.getId();
        server.execute(() -> ClowderSync.reconcileTeam(server, id));
    }

    /** Team id for a player, or null when they are on no (non-spawn) team. */
    public static UUID teamId(MinecraftServer server, UUID player) {
        Team team = data(server).getTeamFromPlayer(player);
        return team == null ? null : team.getId();
    }

    public static Set<UUID> members(MinecraftServer server, UUID teamId) {
        Team team = data(server).getTeam(teamId);
        return team == null ? null : team.getPlayers();
    }

    public static String name(MinecraftServer server, UUID teamId) {
        Team team = data(server).getTeam(teamId);
        return team == null ? "Clowder" : team.getName();
    }

    public static void enableSocial(MinecraftServer server, UUID teamId) {
        SkyblockSavedData d = data(server);
        Team team = d.getTeam(teamId);
        if (team != null) {
            team.setAllowVisit(true);
            team.setAllowJoinRequest(true);
            d.setDirty();
        }
    }

    private static void enableSocialByName(MinecraftServer server, String teamName) {
        SkyblockSavedData d = data(server);
        Team team = d.getTeam(teamName);
        if (team != null) {
            team.setAllowVisit(true);
            team.setAllowJoinRequest(true);
            d.setDirty();
        }
    }

    public static int invite(MinecraftServer server, ServerPlayer inviter, ServerPlayer target) {
        if (inviter.getUUID().equals(target.getUUID())) return BAD;
        SkyblockSavedData d = data(server);
        Team team = d.getTeamFromPlayer(inviter.getUUID());
        if (team == null) return NO_TEAM;
        if (d.hasPlayerTeam(target)) return TARGET_TEAM;
        d.addInvite(team, inviter, target);
        d.setDirty();
        return OK;
    }

    public static int accept(MinecraftServer server, ServerPlayer player) {
        SkyblockSavedData d = data(server);
        if (d.hasPlayerTeam(player)) return TARGET_TEAM;
        var invites = d.getInvites(player);
        if (invites == null || invites.isEmpty()) return NO_TEAM;
        Team team = d.getTeam(invites.get(0));
        if (team == null) return NO_TEAM;
        boolean ok = d.acceptInvite(team, player);
        if (ok) d.setDirty();
        return ok ? OK : BAD;
    }

    public static boolean sameTeam(MinecraftServer server, UUID a, UUID b) {
        Team team = data(server).getTeamFromPlayer(a);
        return team != null && team.hasPlayer(b);
    }
}
