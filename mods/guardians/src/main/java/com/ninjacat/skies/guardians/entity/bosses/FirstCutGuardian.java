package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;

/**
 * Insane · the First Cut — THE SEVERANCE. The 32-tall blade severs: every 20 s it raises the blade (1.5 s red
 * line tell) and cuts a 2-wide line across the main shard (r 42); the floor along it falls into the void for 15 s.
 * The Cut itself — the gold seam (ochre froglight) crossing the floor — gives Speed III to anyone standing on it,
 * but every 8 s the boss's beam runs the seam (1 s gold tell, 4 hearts to anyone on it).
 * Phase 1: world-shards collide — crush zones (1.5 s ring, 8 hearts, end-stone rubble). Phase 2: void tears pull —
 * levitation lines across the floor. Phase 3: the shard splits along the Cut and the halves drift apart (the gap
 * widens by a block a side every 10 s). No immunity: it is a damage race against a floor that keeps disappearing.
 * Simplified vs ARENAS.md: the 20 orbiting shards do not drift (crossing a gap is a jump, not a bridge); the split
 * is at 25 % (the phase hook) rather than 20 %.
 */
public class FirstCutGuardian extends GuardianEntity {
    private static final int SHARD_R = 42, SEVER_EVERY = 400, SEVER_TELL = 30, GAP_LIFE = 300, BEAM_EVERY = 160, BEAM_TELL = 20, CRUSH_EVERY = 240, CRUSH_TELL = 30, PULL_EVERY = 200, PULL_TELL = 20, MAX_SPLIT = 4, BOSS_KEEP = 7;
    private static final Vec3 SEAM_DIR = new Vec3(160, 0, -29).normalize();     // the Cut runs ~ (-75,-14) -> (85,15) in arena_factory; the plan mirrors y into -z
    private final Mech.Ledger gap = new Mech.Ledger(), split = new Mech.Ledger();
    private final List<BlockPos> rubble = new ArrayList<>(); private final List<Integer> rubbleBorn = new ArrayList<>();
    private final List<BlockPos> splitQueue = new ArrayList<>();
    private int severTell = -1, gapTimer = 0, beamTell = -1, crushTell = -1, pullTell = -1, splitHalf = 0, widenClock = 0;
    @Nullable private Vec3 severAt, severDir, crushAt, pullDir;

    public FirstCutGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.FIRSTCUT); }

    @Override protected boolean mobile() { return false; }
    @Override protected int meleeCooldown() { return 44; }

    @Override
    protected void tickMechanic() {
        if (ageInFight == 1) shout("The First Cut answers for nothing — it made the Cut. When it raises the blade, the red line is where the floor stops existing. The gold seam is fast, and the seam is where its beam runs.");
        Vec3 o = origin();
        if (severTell >= 0) tickSever(o); else if (ageInFight % SEVER_EVERY == 100) startSever(o);
        if (gapTimer > 0 && --gapTimer == 0) { gap.restoreAll(level()); sound(SoundEvents.DEEPSLATE_PLACE, 2F, 0.4F); }
        if (beamTell >= 0) tickBeam(o); else if (ageInFight % BEAM_EVERY == 0) { beamTell = 0; say("The beam gathers along the seam."); sound(SoundEvents.BEACON_POWER_SELECT, 2F, 0.5F); }
        if (tickCount % 10 == 0) seamSpeed();
        if (phase() >= 1) { if (crushTell >= 0) tickCrush(); else if (ageInFight % CRUSH_EVERY == 0) startCrush(o); }
        if (phase() >= 2) { if (pullTell >= 0) tickPull(o); else if (ageInFight % PULL_EVERY == 50) { pullDir = Mech.polar(Vec3.ZERO, 1, random.nextDouble() * Math.PI, 0); pullTell = 0; say("The void tears pull..."); sound(SoundEvents.ENDERMAN_STARE, 2F, 0.5F); } }
        if (phase() >= 3) tickSplit(o);
        if (tickCount % 20 == 5) rotRubble();
    }

    @Override
    protected void onPhase(int phase) {
        Vec3 o = origin();
        if (phase == 1) shout("The world-shards begin to collide with the floor. Red rings are crush zones.");
        if (phase == 2) shout("The void tears open — teal lines lift whoever stands on them.");
        if (phase == 3) {
            // the boss steps off the seam, then the shard splits along it
            Vec3 perp = new Vec3(-SEAM_DIR.z, 0, SEAM_DIR.x).scale(random.nextBoolean() ? 11 : -11);
            Vec3 to = o.add(perp); teleportTo(to.x, o.y, to.z);
            gap.restoreAll(level()); gapTimer = 0;                       // the two ledgers never overlap
            splitHalf = 1; widenClock = 0; queueSplit(o);
            shout("The main shard splits along the Cut! The halves drift apart — jump while you still can.");
            sound(SoundEvents.ENDER_DRAGON_GROWL, 3F, 0.4F);
        }
    }

    private boolean onSeam(ServerPlayer p) { return p.onGround() && (level().getBlockState(p.getOnPos()).is(Blocks.OCHRE_FROGLIGHT) || level().getBlockState(p.blockPosition()).is(Blocks.OCHRE_FROGLIGHT)); }
    /** Distance of a point from a line through c with direction d (horizontal). */
    private static double lineDist(Vec3 c, Vec3 d, Vec3 p) { double dx = p.x - c.x, dz = p.z - c.z; return Math.abs(dx * d.z - dz * d.x); }

    // ------------------------------------------------------------------ the sever
    /** A line through a random player's position at a random angle; the blade comes down after 1.5 s. */
    private void startSever(Vec3 o) {
        ServerPlayer p = Mech.randomPlayer(this); if (p == null || arena() == null) return;
        severAt = new Vec3(p.getX(), o.y, p.getZ()); severDir = Mech.polar(Vec3.ZERO, 1, random.nextDouble() * Math.PI, 0); severTell = 0;
        playClip(CLIP_ATTACK); getNavigation().stop();
        say("The First Cut raises the blade..."); sound(SoundEvents.WITHER_SHOOT, 2F, 0.4F);
    }
    private void tickSever(Vec3 o) {
        severTell++;
        if (severAt == null || severDir == null) { severTell = -1; return; }
        if (severTell % 3 == 0) Mech.line(serverLevel(), Mech.RED, severAt.add(severDir.scale(-SHARD_R)).add(0, 0.3, 0), severAt.add(severDir.scale(SHARD_R)).add(0, 0.3, 0), 60);
        if (severTell < SEVER_TELL) return;
        severTell = -1;
        Vec3 perp = new Vec3(-severDir.z, 0, severDir.x);
        for (int t = -SHARD_R; t <= SHARD_R; t++) for (int w = 0; w < 2; w++) {
            Vec3 q = severAt.add(severDir.scale(t)).add(perp.scale(w));
            if (Mech.horiz(q, o) > SHARD_R || Mech.horiz(q, position()) < BOSS_KEEP) continue;
            for (int dy = 0; dy >= -2; dy--) { BlockPos b = BlockPos.containing(q.x, o.y + dy, q.z); if (!level().getBlockState(b).isAir() && !split.has(b) && !splitQueue.contains(b)) gap.clear(level(), b); }
        }
        gapTimer = GAP_LIFE;
        Mech.line(serverLevel(), ParticleTypes.SWEEP_ATTACK, severAt.add(severDir.scale(-SHARD_R)).add(0, 1, 0), severAt.add(severDir.scale(SHARD_R)).add(0, 1, 0), 30);
        sound(SoundEvents.GLASS_BREAK, 3F, 0.3F); sound(SoundEvents.GENERIC_EXPLODE.value(), 2F, 0.5F);
        shout("SEVERED. The floor along the line is gone for fifteen seconds.");
    }

    // ------------------------------------------------------------------ the seam
    private void seamSpeed() { for (ServerPlayer p : party()) if (onSeam(p)) p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 30, 2, false, false, true)); }
    private void tickBeam(Vec3 o) {
        beamTell++;
        if (beamTell % 2 == 0) Mech.line(serverLevel(), Mech.GOLD, o.add(SEAM_DIR.scale(-SHARD_R)).add(0, 0.6, 0), o.add(SEAM_DIR.scale(SHARD_R)).add(0, 0.6, 0), 50);
        if (beamTell < BEAM_TELL) return;
        beamTell = -1;
        Mech.line(serverLevel(), ParticleTypes.END_ROD, o.add(SEAM_DIR.scale(-SHARD_R)).add(0, 1, 0), o.add(SEAM_DIR.scale(SHARD_R)).add(0, 1, 0), 80);
        sound(SoundEvents.BEACON_DEACTIVATE, 3F, 1.4F);
        for (ServerPlayer p : party()) if (onSeam(p) || lineDist(o, SEAM_DIR, p.position()) < 1.2 && Mech.horiz(p.position(), o) < SHARD_R) { p.hurt(damageSources().mobAttack(this), 8); p.displayClientMessage(NinjacatText.teal("The beam runs the seam."), true); }
    }

    // ------------------------------------------------------------------ phase 1: crush zones
    private void startCrush(Vec3 o) {
        ServerPlayer p = Mech.randomPlayer(this); if (p == null) return;
        Vec3 at = Mech.polar(p.position(), random.nextDouble() * 5, random.nextDouble() * Math.PI * 2, o.y);
        if (Mech.horiz(at, o) > SHARD_R - 4) at = o.add(at.subtract(o).normalize().scale(SHARD_R - 6));
        crushAt = at; crushTell = 0; sound(SoundEvents.ANVIL_LAND, 2F, 0.3F);
    }
    private void tickCrush() {
        crushTell++;
        if (crushAt == null) { crushTell = -1; return; }
        ring(Mech.RED, crushAt, 5, 24, crushAt.y + 0.2);
        if (crushTell % 4 == 0) serverLevel().sendParticles(new net.minecraft.core.particles.BlockParticleOption(ParticleTypes.BLOCK, Blocks.END_STONE.defaultBlockState()), crushAt.x, crushAt.y + 14 - crushTell * 0.4, crushAt.z, 6, 2, 1, 2, 0.05);
        if (crushTell < CRUSH_TELL) return;
        crushTell = -1;
        Mech.thud(serverLevel(), crushAt); areaDamage(crushAt, 5.5, 16, 1.2);
        for (int i = 0; i < 4; i++) { BlockPos b = BlockPos.containing(Mech.polar(crushAt, random.nextDouble() * 3, random.nextDouble() * Math.PI * 2, crushAt.y)); if (level().getBlockState(b).isAir() && !level().getBlockState(b.below()).isAir() && rubble.size() < 40) { placeTemp(b, Blocks.END_STONE.defaultBlockState()); rubble.add(b); rubbleBorn.add(tickCount); } }
        sound(SoundEvents.GENERIC_EXPLODE.value(), 2F, 0.4F);
    }
    private void rotRubble() {
        for (int i = rubble.size() - 1; i >= 0; i--) if (tickCount - rubbleBorn.get(i) > 400) { BlockPos b = rubble.get(i); if (level().getBlockState(b).is(Blocks.END_STONE)) level().setBlock(b, Blocks.AIR.defaultBlockState(), 3); tempBlocks.remove(b); rubble.remove(i); rubbleBorn.remove(i); }
    }

    // ------------------------------------------------------------------ phase 2: levitation lines
    private void tickPull(Vec3 o) {
        pullTell++;
        if (pullDir == null) { pullTell = -1; return; }
        if (pullTell % 2 == 0) Mech.line(serverLevel(), Mech.TEAL, o.add(pullDir.scale(-SHARD_R)).add(0, 0.4, 0), o.add(pullDir.scale(SHARD_R)).add(0, 0.4, 0), 60);
        if (pullTell < PULL_TELL) return;
        pullTell = -1; sound(SoundEvents.ENDERMAN_TELEPORT, 2F, 0.4F);
        for (ServerPlayer p : party()) if (lineDist(o, pullDir, p.position()) < 1.6 && Mech.horiz(p.position(), o) < SHARD_R) {
            p.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 50, 1)); p.hurt(damageSources().mobAttack(this), 4);
            p.displayClientMessage(NinjacatText.teal("A void tear pulls you up!"), true); Mech.column(serverLevel(), Mech.TEAL, p.position(), 6, 10);
        }
    }

    // ------------------------------------------------------------------ phase 3: the split
    /** Queue the strip |perp| < splitHalf along the seam; blocks are removed 120 a tick so the server never stalls. */
    private void queueSplit(Vec3 o) {
        Vec3 perp = new Vec3(-SEAM_DIR.z, 0, SEAM_DIR.x);
        for (int t = -SHARD_R - 2; t <= SHARD_R + 2; t++) for (int w = -splitHalf; w <= splitHalf; w++) {
            Vec3 q = o.add(SEAM_DIR.scale(t)).add(perp.scale(w));
            if (Mech.horiz(q, o) > SHARD_R + 1 || Mech.horiz(q, position()) < BOSS_KEEP) continue;
            for (int dy = 0; dy >= -3; dy--) { BlockPos b = BlockPos.containing(q.x, o.y + dy, q.z); if (!level().getBlockState(b).isAir() && !split.has(b) && !splitQueue.contains(b)) splitQueue.add(b); }
        }
    }
    private void tickSplit(Vec3 o) {
        for (int i = 0; i < 120 && !splitQueue.isEmpty(); i++) { BlockPos b = splitQueue.remove(splitQueue.size() - 1); if (!gap.has(b)) split.clear(level(), b); }
        if (!splitQueue.isEmpty() && tickCount % 5 == 0) sound(SoundEvents.DEEPSLATE_BREAK, 2F, 0.3F);
        if (++widenClock >= 200 && splitHalf < MAX_SPLIT) { widenClock = 0; splitHalf++; queueSplit(o); say("The halves drift further apart."); }
        if (tickCount % 6 == 0) Mech.line(serverLevel(), ParticleTypes.PORTAL, o.add(SEAM_DIR.scale(-SHARD_R)).add(0, -1, 0), o.add(SEAM_DIR.scale(SHARD_R)).add(0, -1, 0), 40);
    }

    @Override
    protected void onDefeated() {
        super.onDefeated();
        gap.restoreAll(level()); split.restoreAll(level()); splitQueue.clear(); rubble.clear(); rubbleBorn.clear(); gapTimer = 0;
    }
}
