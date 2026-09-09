package com.ninjacat.skies.core.tension;

import dev.ftb.mods.ftbteams.api.FTBTeamsAPI;
import dev.ftb.mods.ftbteams.api.Team;
import dev.ftb.mods.ftbteams.api.TeamManager;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * FTB Teams access. Only loaded when the mod is present — never reference this class directly;
 * go through {@link LoomTension}.
 */
final class FtbTeamsBridge {
    private static final String KEY = "ninjacatskies";

    private FtbTeamsBridge() {}

    static boolean ready() {
        return FTBTeamsAPI.api().isManagerLoaded();
    }

    /** Party membership changes re-sync the client and hand out any Strand advancements the new Clowder already earned. */
    static void registerPartyEvents() {
        dev.ftb.mods.ftbteams.api.event.TeamEvent.PLAYER_JOINED_PARTY.register(e -> {
            if (e.getPlayer() != null) LoomTension.onClowderChanged(e.getPlayer());
        });
        dev.ftb.mods.ftbteams.api.event.TeamEvent.PLAYER_LEFT_PARTY.register(e -> {
            if (e.getPlayer() != null) LoomTension.onClowderChanged(e.getPlayer());
        });
    }

    static Optional<Clowder> forPlayer(ServerPlayer player) {
        if (!ready()) {
            return Optional.empty();
        }
        return FTBTeamsAPI.api().getManager().getTeamForPlayer(player).map(TeamClowder::new);
    }

    static Optional<Clowder> byId(UUID id) {
        if (!ready()) {
            return Optional.empty();
        }
        return FTBTeamsAPI.api().getManager().getTeamByID(id).map(TeamClowder::new);
    }

    static List<Clowder> all(MinecraftServer server) {
        List<Clowder> out = new ArrayList<>();
        if (!ready()) {
            return out;
        }
        TeamManager manager = FTBTeamsAPI.api().getManager();
        for (Team team : manager.getTeams()) {
            if (!team.isValid() || team.isServerTeam()) continue;
            // A player-team whose owner currently sits in a party is not a Clowder of its own.
            if (team.isPlayerTeam()) {
                boolean inParty = manager.getTeamForPlayerID(team.getOwner())
                        .map(t -> !t.getId().equals(team.getId())).orElse(false);
                if (inParty) continue;
            }
            out.add(new TeamClowder(team));
        }
        return out;
    }

    private record TeamClowder(Team team) implements Clowder {
        @Override
        public UUID id() {
            return team.getTeamId();
        }

        @Override
        public Component name() {
            return team.getName();
        }

        @Override
        public CompoundTag data() {
            CompoundTag extra = team.getExtraData();
            if (!extra.contains(KEY)) {
                extra.put(KEY, new CompoundTag());
            }
            return extra.getCompound(KEY);
        }

        @Override
        public void markDirty() {
            team.markDirty();
        }

        @Override
        public Collection<UUID> memberIds() {
            return team.getMembers().isEmpty() ? java.util.Set.of(team.getOwner()) : team.getMembers();
        }

        @Override
        public Collection<ServerPlayer> onlineMembers() {
            return team.getOnlineMembers();
        }
    }
}
