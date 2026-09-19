package com.ninjacat.skies.driftwrecks.wreck;

import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.driftwrecks.block.ThreadPillarBlock;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.block.state.BlockState;
import org.joml.Vector3f;

import java.util.List;
import java.util.Optional;

/** The five objectives: who counts as on the wreck, pillar order, spawner tally, the echo walk, Hold waves. */
public final class WreckObjectives {
    public static final int HOLD_WAVE_TICKS = 40 * 20;
    private WreckObjectives() {}

    public static void tick(DriftManager m, ServerLevel level, Wreck w) {
        MinecraftServer server = level.getServer();
        if (server.getTickCount() % 20 != 0) return;
        Optional<Clowder> c = LoomTension.clowderById(server, w.team);
        if (c.isEmpty()) return;
        for (ServerPlayer p : c.get().onlineMembers()) {
            if (p.level() != level || p.isSpectator() || !w.contains(p.blockPosition(), 1)) continue;
            if (w.visitors.add(p.getUUID())) {
                m.markDirty();
                WreckRewards.award(p, "root");
                if (w.visitors.size() == 1) {
                    TeamDrift t = TeamDrift.of(c.get()); t.count("explored"); t.dirty();
                    if (w.heartwreck) for (ServerPlayer q : c.get().onlineMembers()) q.sendSystemMessage(NinjacatText.teal("You stand in the heart of the old world. It starts to slip the moment you arrive."));
                }
            }
        }
        if (w.objectiveDone) return;
        if (w.objective == WreckObjective.HOLD) tickHold(m, level, w, c.get());
    }

    // ------------------------------------------------------------------ re-thread

    /** A player touched pillar {@code index}. Right in sequence lights it; wrong resets all and angers the wreck. */
    public static void touchPillar(DriftManager m, ServerLevel level, Wreck w, int index, BlockPos at, ServerPlayer p) {
        if (w.objectiveDone || w.pillarOrder.length == 0) return;
        if (w.objective != WreckObjective.RETHREAD && !w.heartwreck) return;
        int want = w.pillarOrder[w.pillarStep];
        if (index == want) {
            level.setBlock(at, level.getBlockState(at).setValue(ThreadPillarBlock.LIT, true), 3);
            level.playSound(null, at, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.BLOCKS, 1.2F, 0.7F + 0.12F * w.pillarStep);
            level.sendParticles(ParticleTypes.GLOW, at.getX() + 0.5, at.getY() + 1.2, at.getZ() + 0.5, 12, 0.3, 0.6, 0.3, 0.02);
            w.pillarStep++;
            m.markDirty();
            if (w.pillarStep >= w.pillarOrder.length) {
                p.sendSystemMessage(NinjacatText.gold(w.heartwreck ? "Nine threads, one weave. The heart holds its breath." : "The pillars sing in order. The seam steadies."));
                m.completeObjective(level, w);
            } else {
                p.displayClientMessage(NinjacatText.teal(w.pillarStep + " of " + w.pillarOrder.length + " threads hold."), true);
            }
        } else {
            for (int i = 0; i < w.pillarOrder.length; i++) {
                BlockPos pp = DriftManager.pillarPos(level.getServer(), w, w.pillarOrder[i]);
                if (pp == null) continue;
                BlockState s = level.getBlockState(pp);
                if (s.getBlock() instanceof ThreadPillarBlock && s.getValue(ThreadPillarBlock.LIT)) level.setBlock(pp, s.setValue(ThreadPillarBlock.LIT, false), 3);
            }
            w.pillarStep = 0;
            m.markDirty();
            level.playSound(null, at, SoundEvents.NOTE_BLOCK_BASS.value(), SoundSource.BLOCKS, 1.0F, 0.5F);
            p.displayClientMessage(NinjacatText.teal("Wrong thread. The pillars go dark—watch the idol again."), true);
            spawnAt(m, level, w, at.above(), m.mobFor(w, level.random.nextInt(4)));
        }
    }

    /** The idol shows the order: each pillar flares in turn. */
    public static void showOrder(ServerLevel level, Wreck w, ServerPlayer p) {
        if (w.pillarOrder.length == 0) {
            p.displayClientMessage(NinjacatText.teal("The idol is quiet. This wreck asks something else of you."), true);
            return;
        }
        int[] order = w.pillarOrder;
        for (int i = 0; i < order.length; i++) {
            BlockPos pp = DriftManager.pillarPos(level.getServer(), w, order[i]);
            if (pp == null) continue;
            int delay = i * 25;
            final int step = i;
            level.getServer().tell(new net.minecraft.server.TickTask(level.getServer().getTickCount() + delay, () -> {
                level.sendParticles(new DustParticleOptions(new Vector3f(0.24F, 0.85F, 0.8F), 2.0F), pp.getX() + 0.5, pp.getY() + 1.5, pp.getZ() + 0.5, 30, 0.2, 1.0, 0.2, 0.0);
                level.playSound(null, pp, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.BLOCKS, 1.5F, 0.7F + 0.12F * step);
            }));
        }
        p.displayClientMessage(NinjacatText.gold("Watch, then act."), true);
    }

    // ------------------------------------------------------------------ clear

    public static void spawnerBroken(DriftManager m, ServerLevel level, Wreck w) {
        w.spawnersLeft = Math.max(0, w.spawnersLeft - 1);
        m.markDirty();
        Optional<Clowder> c = LoomTension.clowderById(level.getServer(), w.team);
        c.ifPresent(cl -> { TeamDrift t = TeamDrift.of(cl); t.count("spawners"); t.dirty(); });
        if (w.objective == WreckObjective.CLEAR && w.spawnersLeft == 0 && !w.objectiveDone) {
            c.ifPresent(cl -> { for (ServerPlayer p : cl.onlineMembers()) p.sendSystemMessage(NinjacatText.gold("The last frayed spawner goes quiet.")); });
            m.completeObjective(level, w);
        }
    }

    // ------------------------------------------------------------------ escort

    public static void echoHome(DriftManager m, ServerLevel level, Wreck w) {
        if (w.objective != WreckObjective.ESCORT || w.objectiveDone) return;
        LoomTension.clowderById(level.getServer(), w.team).ifPresent(cl -> { for (ServerPlayer p : cl.onlineMembers()) p.sendSystemMessage(NinjacatText.gold("The echo steps onto your pad and settles, purring. Thank you, it seems to say.")); });
        m.completeObjective(level, w);
    }

    public static void echoLost(DriftManager m, ServerLevel level, Wreck w) {
        if (w.objectiveDone) return;
        w.echo = null;
        m.markDirty();
        LoomTension.clowderById(level.getServer(), w.team).ifPresent(cl -> { for (ServerPlayer p : cl.onlineMembers()) p.sendSystemMessage(NinjacatText.teal("The echo fades. The chests are still yours.")); });
    }

    // ------------------------------------------------------------------ hold

    private static void tickHold(DriftManager m, ServerLevel level, Wreck w, Clowder c) {
        MinecraftServer server = level.getServer();
        WreckPlan plan = WreckPlan.get(server, w.planId);
        List<WreckPlan.Marker> centers = plan.markers("center");
        BlockPos center = centers.isEmpty() ? w.center() : w.origin.offset(centers.get(0).pos());
        boolean someone = false;
        for (ServerPlayer p : c.onlineMembers()) if (!p.isSpectator() && p.level() == level && p.blockPosition().closerThan(center, 12)) someone = true;
        if (w.holdWave == 0) {
            if (!someone) return;
            startWave(m, level, w, c, center, 1);
            return;
        }
        if (!someone) {
            w.holdWave = 0; w.holdTicks = 0; m.markDirty();
            for (ServerPlayer p : c.onlineMembers()) p.displayClientMessage(NinjacatText.teal("Nobody holds the seam. It will wait for you."), true);
            return;
        }
        w.holdTicks += 20;
        level.sendParticles(ParticleTypes.GLOW, center.getX() + 0.5, center.getY() + 0.5, center.getZ() + 0.5, 6, 1.5, 0.2, 1.5, 0.01);
        if (w.holdTicks >= HOLD_WAVE_TICKS) {
            if (w.holdWave >= 3) {
                w.holdWave = 4; m.markDirty();
                for (ServerPlayer p : c.onlineMembers()) p.sendSystemMessage(NinjacatText.gold("The seam holds. The wreck will stay a while longer."));
                m.completeObjective(level, w);
            } else {
                startWave(m, level, w, c, center, w.holdWave + 1);
            }
        }
    }

    private static void startWave(DriftManager m, ServerLevel level, Wreck w, Clowder c, BlockPos center, int wave) {
        w.holdWave = wave; w.holdTicks = 0; m.markDirty();
        int n = Math.round((2 + wave * 2) * DriftManager.partyScale(c.onlineMembers().size()));
        for (int i = 0; i < n; i++) {
            double a = level.random.nextDouble() * Math.PI * 2, r = 5 + level.random.nextDouble() * 4;
            BlockPos at = BlockPos.containing(center.getX() + Math.cos(a) * r, center.getY() + 1, center.getZ() + Math.sin(a) * r);
            spawnAt(m, level, w, at, m.mobFor(w, i + wave));
        }
        level.playSound(null, center, SoundEvents.RAID_HORN.value(), SoundSource.HOSTILE, 2.0F, 1.4F);
        for (ServerPlayer p : c.onlineMembers()) p.displayClientMessage(NinjacatText.teal("Wave " + wave + " of 3. Hold the seam."), true);
    }

    static void spawnAt(DriftManager m, ServerLevel level, Wreck w, BlockPos at, EntityType<?> type) {
        Entity e = type.create(level);
        if (!(e instanceof Mob mob)) return;
        BlockPos stand = at;
        for (int dy = 0; dy < 6 && !level.getBlockState(stand).isAir(); dy++) stand = stand.above();
        mob.moveTo(stand.getX() + 0.5, stand.getY(), stand.getZ() + 0.5, level.random.nextFloat() * 360, 0);
        mob.finalizeSpawn(level, level.getCurrentDifficultyAt(stand), MobSpawnType.EVENT, null);
        m.tagMob(w, mob);
        level.addFreshEntity(mob);
        level.sendParticles(ParticleTypes.ASH, stand.getX() + 0.5, stand.getY() + 1, stand.getZ() + 0.5, 10, 0.4, 0.6, 0.4, 0.02);
    }

}
