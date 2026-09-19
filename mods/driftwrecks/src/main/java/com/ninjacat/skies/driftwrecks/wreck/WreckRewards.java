package com.ninjacat.skies.driftwrecks.wreck;

import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.Driftwrecks;
import com.ninjacat.skies.driftwrecks.network.AtlasSyncPayload;
import com.ninjacat.skies.driftwrecks.registry.DwBlocks;
import com.ninjacat.skies.driftwrecks.registry.DwItems;
import com.ninjacat.skies.driftwrecks.registry.DwRegistries;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.advancements.AdvancementHolder;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.PacketDistributor;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

/**
 * What finishing a wreck pays: Weft and a Seal for everyone who set foot on it, the Atlas cell and its lore, the
 * modifier stamp, a Keepsake roll, and the perks and milestones those unlock. All team-scoped.
 */
public final class WreckRewards {
    public static final float KEEPSAKE_NEW = 0.35F, KEEPSAKE_DUPE = 0.10F;
    private WreckRewards() {}

    public static void complete(DriftManager m, ServerLevel level, Wreck w) {
        MinecraftServer server = level.getServer();
        Optional<Clowder> oc = LoomTension.clowderById(server, w.team);
        if (oc.isEmpty()) return;
        Clowder c = oc.get();
        TeamDrift team = TeamDrift.of(c);
        List<ServerPlayer> recipients = new ArrayList<>();
        for (ServerPlayer p : c.onlineMembers()) if (w.visitors.contains(p.getUUID()) || w.contains(p.blockPosition(), 24)) recipients.add(p);
        if (recipients.isEmpty()) recipients.addAll(c.onlineMembers());

        int weft = switch (w.tier) { case RAFT -> 3; case RUIN -> 5; case HOLD -> 8; } + (w.modifier == WreckModifier.UNSTABLE ? 2 : 0);
        for (ServerPlayer p : recipients) {
            LoomTension.giveOrDrop(p, new ItemStack(DwItems.SALVAGED_WEFT.get(), weft));
            LoomTension.giveOrDrop(p, new ItemStack(DwItems.DRIFTWRECK_SEAL.get()));
            award(p, "salvage");
        }
        team.count("objectives");
        team.count("obj_" + w.objective.id);

        Collection<ServerPlayer> all = c.onlineMembers();
        if (w.heartwreck) {
            team.setHeartwreck(3);
            if (!team.heartKeepsake()) team.setHeartKeepsake();
            for (ServerPlayer p : recipients) LoomTension.giveOrDrop(p, new ItemStack(DwItems.HEART_KEEPSAKE.get()));
            for (ServerPlayer p : all) {
                award(p, "heartwreck");
                award(p, "lore/heart");
                p.sendSystemMessage(NinjacatText.teal("The Skies were never an ending. They were the Loom, holding its breath."));
                p.sendSystemMessage(NinjacatText.gold("The Heartwreck lets go. Keep what it gave you—and go on weaving."));
            }
            server.getPlayerList().broadcastSystemMessage(NinjacatText.gold("A Clowder stood in the heart of the old world: ")
                    .append(c.name().copy().withStyle(s -> s.withColor(NinjacatText.TEAL))), false);
            team.dirty();
            syncAll(c);
            return;
        }

        // the Atlas
        boolean newCell = w.core != null && team.fillCell(w.skin, w.core);
        if (newCell) {
            for (ServerPlayer p : all) {
                award(p, "lore/" + w.skin.id() + "_" + w.core.id);
                p.playNotifySound(DwRegistries.sound("atlas.page"), SoundSource.PLAYERS, 1.0F, 1.0F);
                p.sendSystemMessage(NinjacatText.teal("A page of the Wreck Atlas fills in: ")
                        .append(NinjacatText.gold(w.skin.tribe() + " " + w.core.title + ".")));
            }
            if (team.columnComplete(w.skin)) {
                for (ServerPlayer p : all) {
                    award(p, "column");
                    p.sendSystemMessage(NinjacatText.gold("The " + w.skin.title() + " column is whole. " + w.skin.tribe() + " lures cost half, their wrecks come oftener, and their banner is yours to weave."));
                }
            }
            if (team.rowComplete(w.core)) {
                for (ServerPlayer p : all) {
                    award(p, "row");
                    p.sendSystemMessage(NinjacatText.gold("Every tribe's " + w.core.title.toLowerCase() + " is in the Atlas. Their hidden rooms will always open for you."));
                }
            }
            int cells = team.cellCount();
            if (cells >= 25) for (ServerPlayer p : all) award(p, "cells_25");
            if (cells >= Strand.ALL.length * WreckCore.ALL.length && team.heartwreck() == 0) {
                team.setHeartwreck(1);
                for (ServerPlayer p : all) {
                    award(p, "cells_54");
                    p.sendSystemMessage(NinjacatText.teal("Every page answers. Somewhere under the Skies, the heart of the old world starts to drift your way."));
                }
            }
        }
        if (team.stampModifier(w.modifier)) {
            for (ServerPlayer p : all) p.sendSystemMessage(NinjacatText.teal("Atlas stamp: " + w.modifier.title + "."));
            if (team.allModifierStamps()) for (ServerPlayer p : all) {
                award(p, "modifiers");
                p.sendSystemMessage(NinjacatText.gold("All six stamps. Your wrecks hold a quarter longer."));
            }
        }

        // a Keepsake roll
        if (w.core != null && !recipients.isEmpty()) {
            boolean had = team.hasKeepsake(w.skin, w.core);
            if (level.random.nextFloat() < (had ? KEEPSAKE_DUPE : KEEPSAKE_NEW)) giveKeepsake(team, w.skin, w.core, recipients.get(level.random.nextInt(recipients.size())));
        }
        team.dirty();
        syncAll(c);
    }

    public static void giveKeepsake(TeamDrift team, Strand s, WreckCore core, ServerPlayer to) {
        boolean first = team.findKeepsake(s, core);
        team.dirty();
        LoomTension.giveOrDrop(to, new ItemStack(DwBlocks.keepsake(s, core).asItem()));
        to.playNotifySound(DwRegistries.sound("keepsake.found"), SoundSource.PLAYERS, 1.0F, 1.0F);
        for (ServerPlayer p : team.clowder().onlineMembers()) {
            p.sendSystemMessage(NinjacatText.gold(first ? "A Keepsake: " : "Another Keepsake: ").append(keepsakeName(s, core)));
            award(p, "keepsake");
        }
    }

    public static net.minecraft.network.chat.MutableComponent keepsakeName(Strand s, WreckCore c) {
        return net.minecraft.network.chat.Component.translatable("block.driftwrecks.keepsake_" + s.id() + "_" + c.id)
                .withStyle(st -> st.withColor(s.color()));
    }

    /** Grant a driftwrecks advancement (all its criteria). Missing advancements are ignored. */
    public static void award(ServerPlayer p, String path) {
        AdvancementHolder holder = p.server.getAdvancements().get(ResourceLocation.fromNamespaceAndPath(Driftwrecks.MOD_ID, path));
        if (holder == null) return;
        var progress = p.getAdvancements().getOrStartProgress(holder);
        if (progress.isDone()) return;
        for (String crit : progress.getRemainingCriteria()) p.getAdvancements().award(holder, crit);
    }

    /** Login / party change: grant the lore and hint unlocks the Clowder already earned, and sync the Atlas. */
    public static void onJoin(ServerPlayer p) {
        LoomTension.clowderOf(p).ifPresent(c -> {
            TeamDrift t = TeamDrift.of(c);
            for (Strand s : Strand.ALL) for (WreckCore core : WreckCore.ALL) if (t.hasCell(s, core)) award(p, "lore/" + s.id() + "_" + core.id);
            for (WreckCore core : WreckCore.ALL) if (t.hintRead(core)) award(p, "hint/" + core.id);
            if (t.heartwreck() >= 3) { award(p, "lore/heart"); award(p, "heartwreck"); }
            sync(p, t);
        });
    }

    public static void sync(ServerPlayer p, TeamDrift t) {
        PacketDistributor.sendToPlayer(p, new AtlasSyncPayload(t.snapshot()));
    }

    public static void syncAll(Clowder c) {
        TeamDrift t = TeamDrift.of(c);
        for (ServerPlayer p : c.onlineMembers()) sync(p, t);
    }
}
