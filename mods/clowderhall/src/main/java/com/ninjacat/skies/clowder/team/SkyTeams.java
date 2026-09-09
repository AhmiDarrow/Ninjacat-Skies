package com.ninjacat.skies.clowder.team;

import de.melanx.skyblockbuilder.data.SkyblockSavedData;
import de.melanx.skyblockbuilder.data.Team;
import de.melanx.skyblockbuilder.events.SkyblockCreateTeamEvent;
import de.melanx.skyblockbuilder.events.SkyblockInvitationEvent;
import de.melanx.skyblockbuilder.events.SkyblockJoinRequestEvent;
import de.melanx.skyblockbuilder.events.SkyblockManageTeamEvent;
import de.melanx.skyblockbuilder.events.SkyblockOpManageEvent;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.TickTask;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.server.ServerLifecycleHooks;

import java.util.HashSet;
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
    public static final int ALREADY = -4;      // invite: this team already invited that player (no re-send)

    private static SkyblockSavedData data(MinecraftServer server) {
        return SkyblockSavedData.get(server.overworld());
    }

    public static void registerListeners(IEventBus bus) {
        bus.addListener(SkyTeams::onCreate);
        bus.addListener(SkyTeams::onAccept);
        bus.addListener(SkyTeams::onJoinAccepted);
        bus.addListener(SkyTeams::onOpAdd);
        bus.addListener(SkyTeams::onOpRemove);
        bus.addListener(SkyTeams::onOpDelete);
        bus.addListener(SkyTeams::onOpClear);
        bus.addListener(SkyTeams::onLeave);
        bus.addListener(SkyTeams::onLogin);
    }

    /** Run after the current command/packet has finished (Skyblock fires its events before it acts). */
    private static void later(MinecraftServer server, Runnable task) {
        server.tell(new TickTask(server.getTickCount() + 1, task));
    }

    private static void onCreate(SkyblockCreateTeamEvent event) {
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null) return;
        String name = event.getName();
        later(server, () -> enableSocialByName(server, name));
    }

    private static void onOpRemove(SkyblockOpManageEvent.RemoveFromTeam event) {
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null || event.getPlayers() == null) return;
        Set<UUID> removed = new HashSet<>();
        for (ServerPlayer p : event.getPlayers()) removed.add(p.getUUID());
        later(server, () -> leaveIfGone(server, removed));
    }

    private static void onOpDelete(SkyblockOpManageEvent.DeleteTeam event) {
        deferLeaveAll(event.getTeam());
    }

    private static void onOpClear(SkyblockOpManageEvent.ClearTeam event) {
        deferLeaveAll(event.getTeam());
    }

    private static void deferLeaveAll(Team team) {
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null || team == null || team.isSpawn()) return;
        Set<UUID> members = new HashSet<>(team.getPlayers());
        later(server, () -> leaveIfGone(server, members));
    }

    /** Only drop players from the mirror party if Skyblock really removed them (the event may have been denied). */
    private static void leaveIfGone(MinecraftServer server, Set<UUID> players) {
        for (UUID id : players) {
            if (teamId(server, id) == null) {
                ClowderSync.onLeave(server, id);
            }
        }
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
        later(server, () -> leaveIfGone(server, Set.of(left)));
    }

    private static void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) return;
        MinecraftServer server = player.server;
        UUID id = player.getUUID();
        // Let Skyblock finish its own login handling before mirroring (next tick).
        later(server, () -> ClowderSync.reconcilePlayer(server, id));
    }

    private static void deferReconcile(Team team) {
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null || team == null || team.isSpawn()) return;          // the Dock's spawn team is not a Clowder
        UUID id = team.getId();
        later(server, () -> ClowderSync.reconcileTeam(server, id));
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
        if (d.hasInviteFrom(team, target)) return ALREADY;                      // one prompt per team, not one per right-click
        d.addInvite(team, inviter, target);
        d.setDirty();
        return OK;
    }

    public static int accept(MinecraftServer server, ServerPlayer player) {
        SkyblockSavedData d = data(server);
        if (d.hasPlayerTeam(player)) return TARGET_TEAM;
        var invites = d.getInvites(player);
        if (invites == null || invites.isEmpty()) return NO_TEAM;
        Team team = null;
        for (int i = invites.size() - 1; i >= 0 && team == null; i--) team = d.getTeam(invites.get(i));   // newest invite whose team still exists
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
