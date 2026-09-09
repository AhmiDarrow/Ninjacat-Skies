package com.ninjacat.skies.clowder.team;

import com.ninjacat.skies.clowder.ClowderHall;
import dev.ftb.mods.ftblibrary.icon.Color4I;
import dev.ftb.mods.ftbteams.api.FTBTeamsAPI;
import dev.ftb.mods.ftbteams.api.Team;
import dev.ftb.mods.ftbteams.api.TeamManager;
import dev.ftb.mods.ftbteams.data.PartyTeam;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

import java.util.Set;
import java.util.UUID;

/**
 * Direct FTB Teams access — the mirror that keeps a Skyblock pad team and an FTB party in step,
 * so Loom Tension, the shared-life pool and FTB Quests (all keyed on the FTB team) follow the pad.
 * Only referenced when "ftbteams" is loaded and its manager is up. Conservative: it only ever creates
 * a party or adds members; it removes a member only when they leave (or are removed from) the Skyblock team.
 */
public final class FtbParties {
    private FtbParties() {}

    private static final String TAG = ClowderHall.MOD_ID;   // nested key inside a team's extra data
    private static final String SKY = "skyblock";           // the mirrored Skyblock team id
    private static final Color4I PARTY_COLOR = Color4I.rgb(0x2AA198);

    public static boolean loaded() {
        try {
            return FTBTeamsAPI.api().isManagerLoaded();
        } catch (Throwable t) {
            return false;
        }
    }

    /** Ensure a single FTB party mirrors the given Skyblock team's members. */
    public static void reconcile(MinecraftServer server, UUID skyTeamId, Set<UUID> memberIds, String displayName, boolean allowCreate) {
        if (memberIds == null || memberIds.size() < 2) return; // solo pads are handled by LoomTension's solo path
        try {
            TeamManager manager = FTBTeamsAPI.api().getManager();
            Team party = findMirror(manager, skyTeamId);

            if (party == null) {
                // Never create/restructure a party on a passive trigger (login) — protects existing saves.
                if (!allowCreate) return;
                ServerPlayer anchor = firstOnline(server, memberIds);
                if (anchor == null) return; // nobody online to own/create the party yet
                Team anchorTeam = manager.getTeamForPlayer(anchor).orElse(null);
                if (anchorTeam != null && anchorTeam.isPartyTeam() && !isMirror(anchorTeam)) {
                    party = anchorTeam;                       // adopt a hand-made party as the mirror
                } else {
                    if (anchorTeam instanceof PartyTeam stale && isMirror(anchorTeam)) {
                        stale.kickPlayerForcibly(anchor);     // anchor still sits in another pad's mirror: leave it first
                    }
                    party = createParty(anchor, displayName);
                }
                if (party == null) return;
                tag(party, skyTeamId);
            }

            UUID partyId = party.getTeamId();
            for (UUID id : memberIds) {
                ServerPlayer member = server.getPlayerList().getPlayer(id);
                if (member == null) continue;
                try {
                    Team current = manager.getTeamForPlayer(member).orElse(null);
                    if (current != null && current.getTeamId().equals(partyId)) continue;
                    if (current instanceof PartyTeam other && other.isPartyTeam()) {
                        if (!isMirror(other)) {
                            ClowderHall.LOGGER.info("Not moving {} out of hand-made party {} for pad team {}", member.getGameProfile().getName(), other.getShortName(), skyTeamId);
                            continue;
                        }
                        other.kickPlayerForcibly(member);     // stale mirror from a previous pad
                    }
                    if (party instanceof PartyTeam pt) {
                        pt.join(member);
                    }
                } catch (Throwable t) {
                    ClowderHall.LOGGER.warn("Could not add {} to mirror party for Skyblock team {}: {}", id, skyTeamId, t.toString());
                }
            }
        } catch (Throwable t) {
            ClowderHall.LOGGER.warn("Could not mirror Skyblock team {} into an FTB party", skyTeamId, t);
        }
    }

    /** When a player leaves the Skyblock team, drop them from the mirror party too. */
    public static void leaveMirror(MinecraftServer server, UUID player) {
        try {
            TeamManager manager = FTBTeamsAPI.api().getManager();
            Team current = manager.getTeamForPlayerID(player).orElse(null);
            if (current instanceof PartyTeam pt && isMirror(current)) {
                ServerPlayer online = server.getPlayerList().getPlayer(player);
                if (online != null) {
                    pt.kickPlayerForcibly(online);            // handles the owner case (transfers ownership / disbands)
                } else if (pt.getMembers().size() <= 1 || !pt.isOwner(player)) {
                    pt.leave(player);
                } else {
                    // an offline owner cannot leave a party that still has members: hand it to someone else, then kick
                    var src = server.createCommandSourceStack();
                    UUID heir = pt.getMembers().stream().filter(m -> !m.equals(player)).findFirst().orElse(null);
                    if (heir != null) pt.transferOwnership(src, new com.mojang.authlib.GameProfile(heir, ""));
                    pt.kick(src, java.util.List.of(new com.mojang.authlib.GameProfile(player, "")));
                }
            }
        } catch (Throwable t) {
            ClowderHall.LOGGER.warn("Could not remove {} from a mirror party", player, t);
        }
    }

    public static boolean sameTeam(MinecraftServer server, UUID a, UUID b) {
        try {
            return FTBTeamsAPI.api().getManager().arePlayersInSameTeam(a, b);
        } catch (Throwable t) {
            return false;
        }
    }

    private static Team createParty(ServerPlayer anchor, String displayName) throws Exception {
        // createPartyTeam(owner, name, description, colour): the second argument is the party's display name
        return FTBTeamsAPI.api().getManager().createPartyTeam(anchor, displayName, null, PARTY_COLOR);
    }

    private static Team findMirror(TeamManager manager, UUID skyTeamId) {
        for (Team team : manager.getTeams()) {
            if (team.isPartyTeam() && skyTeamId.equals(mirrorId(team))) {
                return team;
            }
        }
        return null;
    }

    private static boolean isMirror(Team team) {
        return mirrorId(team) != null;
    }

    private static UUID mirrorId(Team team) {
        CompoundTag extra = team.getExtraData();
        if (!extra.contains(TAG)) return null;
        CompoundTag c = extra.getCompound(TAG);
        return c.hasUUID(SKY) ? c.getUUID(SKY) : null;
    }

    private static void tag(Team team, UUID skyTeamId) {
        CompoundTag extra = team.getExtraData();
        CompoundTag c = extra.getCompound(TAG);
        c.putUUID(SKY, skyTeamId);
        extra.put(TAG, c);
        team.markDirty();
    }

    private static ServerPlayer firstOnline(MinecraftServer server, Set<UUID> ids) {
        for (UUID id : ids) {
            ServerPlayer p = server.getPlayerList().getPlayer(id);
            if (p != null) return p;
        }
        return null;
    }

}
