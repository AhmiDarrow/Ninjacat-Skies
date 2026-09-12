package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;

/**
 * Claw · the Edgewalker — DUEL. No gimmick: it leaps shard to shard and pounces the most exposed player. A gold
 * claw-mark (particle ring) appears on the landing spot 0.7 s before each pounce; standing off it is the dodge
 * (6 hearts + knockback in r 4). Bridges (thin deepslate spans with void beneath) crumble 2 s after a player
 * crosses and knit back after 20 s. It never uses a bridge — it jumps.
 */
public class EdgewalkerGuardian extends GuardianEntity {
    private static final int ARENA_R = 42, TELL = 14, POUNCE_EVERY = 110, CRUMBLE_DELAY = 40, REKNIT = 400, CRUMBLE_MAX = 60;
    private record Crumble(BlockPos at, int when) {}
    private final List<Crumble> pending = new ArrayList<>();
    private final Mech.Ledger broken = new Mech.Ledger();
    private final List<Integer> reknitAt = new ArrayList<>();
    private final List<BlockPos> reknitPos = new ArrayList<>();
    @Nullable private Vec3 mark;
    private int tell = -1, airborne = -1, nextPounce = 80;

    public EdgewalkerGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.EDGEWALKER); }

    @Override protected boolean mobile() { return tell < 0 && airborne < 0; }
    @Override protected int meleeCooldown() { return 30; }

    @Override
    protected void tickMechanic() {
        if (ageInFight == 1) shout("The Edgewalker answers for the Cut. No trick to this one: watch for the gold claw-mark and be somewhere else when it lands. Bridges crumble behind you.");
        if (tell >= 0) tickTell(); else if (airborne >= 0) tickFlight(); else if (--nextPounce <= 0) startPounce();
        tickBridges();
        if (tickCount % 40 == 0 && Mech.horiz(position(), origin()) > ARENA_R + 6) leapTo(origin().add(0, 1, 0));     // never leaves the shards
    }

    @Override protected void onPhase(int phase) { shout(phase == 3 ? "The Edgewalker bares every claw — it pounces without pause!" : "The Edgewalker quickens."); }
    private int pounceInterval() { return Math.max(50, POUNCE_EVERY - phase() * 20); }

    /** Pick the most exposed player (furthest from any other player and from the boss) and mark the landing spot. */
    private void startPounce() {
        ServerPlayer best = null; double bd = -1;
        for (ServerPlayer p : party()) {
            if (!p.isAlive() || Mech.horiz(p.position(), origin()) > ARENA_R + 10) continue;
            double d = p.distanceToSqr(this); for (ServerPlayer q : party()) if (q != p) d = Math.min(d, p.distanceToSqr(q) * 2);
            if (d > bd) { bd = d; best = p; }
        }
        if (best == null) { nextPounce = 40; return; }
        Vec3 land = Mech.standOn(level(), best.getX(), best.getZ(), (int) origin().y - 2, (int) origin().y + 22);
        mark = land != null ? land : best.position(); tell = 0; getNavigation().stop(); setTarget(best);
        sound(SoundEvents.PHANTOM_SWOOP, 2F, 0.6F);
    }

    private void tickTell() {
        tell++;
        if (mark == null) { tell = -1; return; }
        ring(Mech.GOLD, mark, 3.5, 20, mark.y + 0.15); ring(Mech.GOLD, mark, 1.5, 8, mark.y + 0.15);
        if (tell == 4) Mech.line(serverLevel(), Mech.GOLD, mark.add(-2, 0.2, -2), mark.add(2, 0.2, 2), 8);
        if (tell >= TELL) { tell = -1; leapTo(mark); }
    }

    /** Ballistic hop to a point: ~1 s in the air, then the slam. */
    private void leapTo(Vec3 to) {
        Vec3 from = position(); double t = 18;
        Vec3 d = to.subtract(from);
        double vx = d.x / t * 1.05, vz = d.z / t * 1.05, vy = d.y / t + 0.04 * t * 1.15;
        setDeltaMovement(vx, Math.max(0.3, Math.min(1.6, vy)), vz); hurtMarked = true;
        airborne = 0; getNavigation().stop(); playClip(CLIP_ATTACK);
        sound(SoundEvents.ENDER_DRAGON_FLAP, 1.5F, 1.2F);
    }

    private void tickFlight() {
        airborne++;
        if (tickCount % 2 == 0) particles(ParticleTypes.CLOUD, position(), 3, 0.8, 0.02);
        if ((onGround() && airborne > 6) || airborne > 50) {
            airborne = -1; nextPounce = pounceInterval(); Vec3 at = position();
            Mech.thud(serverLevel(), at); areaDamage(at, 4.5, 12, 1.4); ring(ParticleTypes.SWEEP_ATTACK, at, 3, 10, at.y + 0.5);
            mark = null; playClip(CLIP_IDLE);
        }
    }

    /** Thin deepslate under a player with void two below = a bridge; it goes 2 s later and comes back after 20 s. */
    private void tickBridges() {
        if (arena() == null) return;
        if (tickCount % 5 == 0) for (ServerPlayer p : party()) {
            BlockPos on = p.getOnPos();
            if (!p.onGround() || !level().getBlockState(on).is(Blocks.DEEPSLATE) || !level().getBlockState(on.below(2)).isAir() || !level().getBlockState(on.below(3)).isAir()) continue;
            if (broken.has(on) || pending.stream().anyMatch(c -> c.at.equals(on)) || pending.size() > CRUMBLE_MAX) continue;
            pending.add(new Crumble(on, tickCount + CRUMBLE_DELAY));
            serverLevel().playSound(null, on, SoundEvents.DEEPSLATE_BREAK, net.minecraft.sounds.SoundSource.BLOCKS, 1.2F, 0.5F);
        }
        for (int i = pending.size() - 1; i >= 0; i--) {
            Crumble c = pending.get(i);
            if (tickCount % 4 == 0) serverLevel().sendParticles(ParticleTypes.CRIT, c.at.getX() + 0.5, c.at.getY() + 1.1, c.at.getZ() + 0.5, 4, 0.5, 0.1, 0.5, 0.01);
            if (tickCount < c.when) continue;
            pending.remove(i);
            for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) {          // the 3-wide span goes block by block
                BlockPos b = c.at.offset(dx, 0, dz);
                if (!level().getBlockState(b).is(Blocks.DEEPSLATE) || !level().getBlockState(b.below(2)).isAir()) continue;
                broken.clear(level(), b); reknitPos.add(b); reknitAt.add(tickCount + REKNIT);
                serverLevel().sendParticles(new net.minecraft.core.particles.BlockParticleOption(ParticleTypes.BLOCK, Blocks.DEEPSLATE.defaultBlockState()), b.getX() + 0.5, b.getY(), b.getZ() + 0.5, 12, 0.4, 0.2, 0.4, 0.05);
            }
            serverLevel().playSound(null, c.at, SoundEvents.DEEPSLATE_FALL, net.minecraft.sounds.SoundSource.BLOCKS, 1.5F, 0.4F);
        }
        while (!reknitAt.isEmpty() && reknitAt.get(0) <= tickCount) {
            BlockPos b = reknitPos.remove(0); reknitAt.remove(0);
            if (level().getBlockState(b).isAir()) level().setBlock(b, Blocks.DEEPSLATE.defaultBlockState(), 3);
            broken.forget(b);
        }
    }

    @Override protected void onDefeated() { super.onDefeated(); broken.restoreAll(level()); pending.clear(); reknitAt.clear(); reknitPos.clear(); }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        broken.save(tag, "Broken");
    }
    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        broken.load(tag, "Broken", level());
    }
}
