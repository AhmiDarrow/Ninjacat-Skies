package com.ninjacat.skies.core.tension;

import com.ninjacat.skies.core.config.SkiesConfig;
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
            inheritSoloData(e);
            // The joiner's Strands may have been ORed into the party: every online member needs the new state.
            if (e.getTeam() != null) e.getTeam().getOnlineMembers().forEach(LoomTension::onClowderChanged);
            if (e.getPlayer() != null) LoomTension.onClowderChanged(e.getPlayer());
        });
        dev.ftb.mods.ftbteams.api.event.TeamEvent.PLAYER_LEFT_PARTY.register(e -> {
            copyPartyToPlayerTeam(e);
            if (e.getPlayer() != null) LoomTension.onClowderChanged(e.getPlayer());
        });
    }

    /**
     * FTB promoting a solo player-team into a party used to drop Loom Tension: the party extra-data was empty,
     * so seated Strands vanished and the Tension Post still pointed at the old UUID. Copy missing keys, OR the
     * strand bits, and retarget the remembered Post.
     */
    private static void inheritSoloData(dev.ftb.mods.ftbteams.api.event.PlayerJoinedPartyTeamEvent e) {
        Team prev = e.getPreviousTeam();
        Team next = e.getTeam();
        if (prev == null || next == null || prev.getTeamId().equals(next.getTeamId())) return;
        CompoundTag from = prev.getExtraData().getCompound(KEY);
        if (from.isEmpty()) return;
        CompoundTag extra = next.getExtraData();
        CompoundTag to = extra.contains(KEY) ? extra.getCompound(KEY) : new CompoundTag();
        int bits = from.getInt(LoomTension.KEY_STRANDS) | to.getInt(LoomTension.KEY_STRANDS);
        if (bits != 0) to.putInt(LoomTension.KEY_STRANDS, bits);
        if (from.getBoolean(LoomTension.KEY_REWOVEN)) to.putBoolean(LoomTension.KEY_REWOVEN, true);
        if (!to.contains(LoomTension.KEY_POST) && from.contains(LoomTension.KEY_POST)) {
            to.put(LoomTension.KEY_POST, from.get(LoomTension.KEY_POST).copy());
        }
        boolean joiningExisting = next.getMembers().size() > 1;
        for (String k : from.getAllKeys()) {
            if (joiningExisting && k.startsWith("life_reward_")) continue;
            if (!to.contains(k)) to.put(k, from.get(k).copy());
        }
        boolean joiningExhausted = e.getPlayer() != null
                && e.getPlayer().getPersistentData().getBoolean(ClowderLives.EXHAUSTED_FLAG);
        UUID joiningId = e.getPlayer() != null ? e.getPlayer().getUUID() : null;
        ClowderLives.inheritExhaustion(to, from, joiningId, joiningExhausted);
        extra.put(KEY, to);
        next.markDirty();
        if (e.getPlayer() != null) {
            LoomTension.retargetPost(e.getPlayer().getServer(), new TeamClowder(next));
        }
    }

    /**
     * Leaving a party used to restore the solo player-team snapshot: lives spent while grouped came back,
     * and Strands seated after joining vanished. Copy strand bits and receipts. Do not copy the party
     * life pool (that duplicated remaining lives). The party's Tension Post stays with the party.
     */
    private static void copyPartyToPlayerTeam(dev.ftb.mods.ftbteams.api.event.PlayerLeftPartyTeamEvent e) {
        Team party = e.getTeam();
        Team solo = e.getPlayerTeam();
        if (party == null || solo == null || party.getTeamId().equals(solo.getTeamId())) return;
        CompoundTag from = party.getExtraData().getCompound(KEY);
        if (from.isEmpty()) return;
        CompoundTag extra = solo.getExtraData();
        CompoundTag to = extra.contains(KEY) ? extra.getCompound(KEY) : new CompoundTag();
        int bits = from.getInt(LoomTension.KEY_STRANDS) | to.getInt(LoomTension.KEY_STRANDS);
        if (bits != 0) to.putInt(LoomTension.KEY_STRANDS, bits);
        if (from.getBoolean(LoomTension.KEY_REWOVEN)) to.putBoolean(LoomTension.KEY_REWOVEN, true);
        for (String k : from.getAllKeys()) {
            if (k.equals(LoomTension.KEY_POST) || k.equals("shared_lives")
                    || k.equals("life_contributors") || k.equals("exhausted_members")) continue;
            if (!to.contains(k)) to.put(k, from.get(k).copy());
        }
        to.remove(LoomTension.KEY_POST);
        // Strands stay. Lives do not: copying the party pool onto the solo team duplicated it.
        // A living leaver starts a solo pool of startingLives. A spent pool cannot be escaped by leaving.
        // Do not call remaining() here: that getter records contributors and can add starting lives
        // onto the party if the leaver is still listed as a member when this event fires.
        int starting = Math.max(1, Math.min(99, SkiesConfig.STARTING_LIVES.get()));
        UUID leaver = e.getPlayerId();
        int saved = ClowderLives.saved(from);
        boolean dead = (e.getPlayer() != null && e.getPlayer().getPersistentData().getBoolean(ClowderLives.EXHAUSTED_FLAG))
                || ClowderLives.isExhausted(new TeamClowder(party), leaver)
                || saved == 0;
        CompoundTag contrib = new CompoundTag();
        if (leaver != null) contrib.putBoolean(leaver.toString(), true);
        to.put("life_contributors", contrib);
        if (dead) {
            to.putInt("shared_lives", 0);
            CompoundTag ex = new CompoundTag();
            if (leaver != null) ex.putBoolean(leaver.toString(), true);
            to.put("exhausted_members", ex);
        } else {
            to.putInt("shared_lives", starting);
            to.remove("exhausted_members");
        }
        extra.put(KEY, to);
        solo.markDirty();
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
