package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Easy · the Tangle — THE KNOTGARDEN. A spider in a hedge maze. It remembers where each player walked and strings
 * the corridor shut three steps behind them with a rope knot (cobweb — cut it with a sword); knots rot after 40 s.
 * It always goes for whoever is alone: its target is the party member furthest from any friend, and a bite on a
 * lonely player is 50 % harder and venomous (Poison 4 s). Too big for the paths, it hops the hedges instead.
 * Phase 1 strings faster; phase 2 spits knots at your feet (0.7 s tell); phase 3 calls knotlings (cave spiders).
 */
public class TangleGuardian extends GuardianEntity {
    private static final int TRAIL = 6, WEB_LIFE = 800, MAX_WEBS = 80, RETARGET = 40, HOP_CD = 50, SPIT_EVERY = 160, SPIT_TELL = 14, ARENA_R = 31, LONELY = 8;
    private final Map<UUID, List<BlockPos>> trails = new HashMap<>();
    private final List<BlockPos> webs = new ArrayList<>(); private final List<Integer> webBorn = new ArrayList<>();
    private int hopCd = 40, airborne = -1, spitTell = -1; @Nullable private Vec3 spitAt;

    public TangleGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.TANGLE); }

    @Override protected SoundEvent hurtSoundOverride() { return SoundEvents.SPIDER_HURT; }
    @Override protected int meleeCooldown() { return 36; }
    @Override protected boolean mobile() { return airborne < 0; }
    /** The bite: venom, and half again as much on someone with no friend within 8 blocks. */
    @Override
    protected void onMeleeHit(LivingEntity t) {
        boolean lonely = t instanceof ServerPlayer p && isLonely(p);
        float dmg = (float) getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE) * (lonely ? 1.5F : 1F);
        t.hurt(damageSources().mobAttack(this), dmg);
        t.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 0));
        if (t instanceof ServerPlayer p) p.displayClientMessage(NinjacatText.teal(lonely ? "Alone in a dead end — the Tangle's venom bites deep." : "The Tangle's venom seeps in."), true);
        sound(SoundEvents.SPIDER_AMBIENT, 1.5F, 0.6F);
    }

    @Override
    protected void tickMechanic() {
        if (ageInFight == 1) shout("The Tangle answers for the Cut. It strings the paths shut behind you — cut the knots — and it hunts whoever wanders off alone. Stay together.");
        if (tickCount % (phase() >= 1 ? 20 : 30) == 0) trailAndString();
        if (tickCount % 20 == 10) rotWebs();
        if (tickCount % RETARGET == 0) retarget();
        if (airborne >= 0) tickHop(); else if (--hopCd <= 0) tryHop();
        if (phase() >= 2) tickSpit();
        if (phase() >= 3 && ageInFight % 300 == 0) knotlings();
    }

    @Override protected void onPhase(int phase) { shout(phase == 1 ? "The Tangle spins faster." : phase == 2 ? "The Tangle spits knots — watch the line at your feet." : "The Tangle calls its knotlings!"); sound(SoundEvents.SPIDER_AMBIENT, 2F, 0.4F); }

    // ------------------------------------------------------------------ rope knots
    /** Remember the last few floor positions of every player; string the block three steps back if it sits in a hedge corridor. */
    private void trailAndString() {
        for (ServerPlayer p : party()) {
            if (!p.onGround()) continue;
            List<BlockPos> t = trails.computeIfAbsent(p.getUUID(), k -> new ArrayList<>());
            BlockPos here = p.blockPosition();
            if (!t.isEmpty() && t.get(t.size() - 1).distSqr(here) < 4) continue;
            t.add(here); while (t.size() > TRAIL) t.remove(0);
            if (t.size() >= 4) { BlockPos back = t.get(t.size() - 4); if (here.distSqr(back) >= 9) string(back); }
        }
    }
    private boolean inCorridor(BlockPos p) {
        int hedge = 0; for (Direction d : Direction.Plane.HORIZONTAL) if (level().getBlockState(p.relative(d)).is(BlockTags.LEAVES) || level().getBlockState(p.relative(d, 2)).is(BlockTags.LEAVES)) hedge++;
        return hedge >= 1;
    }
    private void string(BlockPos p) {
        if (webs.size() >= MAX_WEBS || !level().getBlockState(p).isAir() || !level().getBlockState(p.below()).isSolidRender(level(), p.below()) || !inCorridor(p)) return;
        if (Mech.horiz(Vec3.atCenterOf(p), origin()) > ARENA_R) return;
        for (ServerPlayer q : party()) if (q.distanceToSqr(Vec3.atCenterOf(p)) < 2.5 * 2.5) return;      // never on top of someone
        placeTemp(p, Blocks.COBWEB.defaultBlockState()); webs.add(p); webBorn.add(tickCount);
        serverLevel().playSound(null, p, SoundEvents.WOOL_PLACE, net.minecraft.sounds.SoundSource.HOSTILE, 1F, 0.5F);
        serverLevel().sendParticles(ParticleTypes.WHITE_ASH, p.getX() + 0.5, p.getY() + 0.5, p.getZ() + 0.5, 12, 0.3, 0.3, 0.3, 0.02);
    }
    /** Knots the party cut are forgotten; old ones rot away. */
    private void rotWebs() {
        for (int i = webs.size() - 1; i >= 0; i--) {
            BlockPos p = webs.get(i);
            boolean gone = !level().getBlockState(p).is(Blocks.COBWEB);
            if (gone || tickCount - webBorn.get(i) > WEB_LIFE) { if (!gone) level().setBlock(p, Blocks.AIR.defaultBlockState(), 3); tempBlocks.remove(p); webs.remove(i); webBorn.remove(i); }
        }
    }

    // ------------------------------------------------------------------ hunting
    private boolean isLonely(ServerPlayer p) { for (ServerPlayer q : party()) if (q != p && q.isAlive() && q.distanceTo(p) < LONELY) return false; return true; }
    /** The loneliest player (largest distance to the nearest friend), closest as tiebreak, becomes the prey. */
    private void retarget() {
        ServerPlayer best = null; double bs = -1;
        for (ServerPlayer p : party()) {
            if (!p.isAlive()) continue;
            double near = 64; for (ServerPlayer q : party()) if (q != p && q.isAlive()) near = Math.min(near, p.distanceTo(q));
            double score = near * 4 - p.distanceTo(this);
            if (score > bs) { bs = score; best = p; }
        }
        if (best != null && best != getTarget()) { setTarget(best); if (isLonely(best)) best.displayClientMessage(NinjacatText.teal("The Tangle has caught your scent — you are alone."), true); }
    }
    /** A 7-wide spider does not fit the paths: when the target is out of reach and the path is stuck, it hops the hedge. */
    private void tryHop() {
        LivingEntity t = getTarget(); if (t == null) { hopCd = 20; return; }
        double d = Mech.horiz(position(), t.position());
        if (d <= meleeReach() || (getNavigation().isInProgress() && !getNavigation().isStuck() && d < 6)) { hopCd = 20; return; }
        Vec3 dir = t.position().subtract(position()); dir = new Vec3(dir.x, 0, dir.z);
        double len = Math.min(14, dir.length()); if (len < 1) { hopCd = 20; return; }
        dir = dir.normalize().scale(len / 16.0);
        setDeltaMovement(dir.x, 0.62, dir.z); hurtMarked = true; airborne = 0; hopCd = HOP_CD; getNavigation().stop();
        sound(SoundEvents.SPIDER_STEP, 1.5F, 0.5F); Mech.burst(serverLevel(), ParticleTypes.WHITE_ASH, position(), 10, 1.5);
    }
    private void tickHop() { airborne++; if ((onGround() && airborne > 5) || airborne > 40) { airborne = -1; getNavigation().stop(); } }

    // ------------------------------------------------------------------ spit (phase 2+)
    private void tickSpit() {
        if (spitTell < 0) {
            if (ageInFight % SPIT_EVERY != 0) return;
            LivingEntity t = getTarget(); if (t == null) return;
            spitAt = t.position(); spitTell = 0; sound(SoundEvents.LLAMA_SPIT, 1.5F, 0.5F);
            return;
        }
        spitTell++;
        if (spitAt == null) { spitTell = -1; return; }
        if (spitTell % 2 == 0) Mech.line(serverLevel(), ParticleTypes.WHITE_ASH, getEyePosition(), spitAt.add(0, 0.5, 0), 16);
        ring(Mech.TEAL, spitAt, 1.5, 8, spitAt.y + 0.1);
        if (spitTell < SPIT_TELL) return;
        spitTell = -1;
        BlockPos at = BlockPos.containing(spitAt);
        if (webs.size() < MAX_WEBS && level().getBlockState(at).isAir()) { placeTemp(at, Blocks.COBWEB.defaultBlockState()); webs.add(at); webBorn.add(tickCount); }
        areaDamage(spitAt, 1.8, 3, 0); Mech.burst(serverLevel(), ParticleTypes.WHITE_ASH, spitAt.add(0, 0.5, 0), 20, 0.8);
    }

    // ------------------------------------------------------------------ knotlings (phase 3)
    private void knotlings() {
        int cap = 1 + partySize();
        if (Mech.countMinions(this) >= cap) return;
        for (int i = 0; i < 2 && Mech.countMinions(this) < cap; i++) {
            Vec3 at = Mech.polar(position(), 2.5, random.nextDouble() * Math.PI * 2, getY());
            Mech.spawn(this, EntityType.CAVE_SPIDER, at, "Knotling", 8, 2);
        }
        say("Knotlings skitter out of the hedge!"); sound(SoundEvents.SPIDER_AMBIENT, 1.5F, 1.4F);
    }

    @Override protected void onDefeated() { super.onDefeated(); Mech.discardMinions(this); webs.clear(); webBorn.clear(); trails.clear(); }
}
