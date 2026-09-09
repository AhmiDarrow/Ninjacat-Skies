package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SweetBerryBushBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * Sprout · the Thornmother — PRUNE. She never strikes. Every 6 s she seeds a thorn hedge (sweet-berry bush,
 * 1 heart/s to anyone inside) that creeps to a neighbouring block every 4 s. If a pruning station's circle stays
 * overgrown for 10 s she heals 10 %. Every 8 hedge blocks the party cuts fires a prune wave: hedge within 6 blocks
 * of every station is cleared and she is stunned 4 s (double damage). Composting is folded into cutting — no custom block.
 */
public class ThornmotherGuardian extends GuardianEntity {
    private static final int SEED_EVERY = 120, SPREAD_EVERY = 80, MAX_HEDGE = 220, STATION_R = 16, CIRCLE = 4, STUN = 80;
    private static final BlockState HEDGE = Blocks.SWEET_BERRY_BUSH.defaultBlockState().setValue(SweetBerryBushBlock.AGE, 2);
    private final List<BlockPos> hedge = new ArrayList<>();
    private final List<Vec3> stations = new ArrayList<>();
    private final int[] overgrown = new int[4];
    private int cut = 0, stun = 0;

    public ThornmotherGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.THORNMOTHER); }

    @Override protected boolean mobile() { return false; }
    @Override protected double meleeReach() { return -1; }      // never attacks directly
    @Override protected void onMeleeHit(LivingEntity t) {}

    @Override
    public boolean hurt(DamageSource src, float amount) { return super.hurt(src, stun > 0 ? amount * 2 : amount); }

    @Override
    protected void tickMechanic() {
        Vec3 o = origin();
        if (ageInFight == 1) {
            for (int i = 0; i < 4; i++) { Vec3 s = Mech.standOn(level(), o.x + Math.cos(Math.PI / 4 + Math.PI / 2 * i) * STATION_R, o.z + Math.sin(Math.PI / 4 + Math.PI / 2 * i) * STATION_R, (int) o.y - 3, (int) o.y + 12); stations.add(s != null ? s : Mech.polar(o, STATION_R, Math.PI / 4 + Math.PI / 2 * i, o.y + 6)); }
            shout("The Thornmother answers for the Cut. She will not strike you — her hedge will. Cut it faster than it creeps, keep the four pruning stations clear, and every eight thorns you cut fire a prune wave that stuns her.");
        }
        if (stun > 0) { stun--; if (tickCount % 3 == 0) Mech.burst(serverLevel(), ParticleTypes.HAPPY_VILLAGER, position().add(0, kind.height * 0.6, 0), 6, 3); }
        else if (ageInFight % SEED_EVERY == 0) seed(o);
        if (ageInFight % SPREAD_EVERY == 10) spread();
        if (tickCount % 20 == 0) { audit(); stations(o); }
        if (tickCount % 20 == 5) thornDamage();
        if (tickCount % 10 == 0) for (Vec3 s : stations) ring(Mech.TEAL, s, CIRCLE, 12, s.y + 0.1);
    }

    @Override protected void onPhase(int phase) { shout(phase == 3 ? "The Thornmother strains — the hedge grows wild!" : "The Thornmother thickens her hedge."); }
    private int seedsPerCycle() { return 1 + phase() / 2 + (partySize() - 1) / 2; }

    /** A seed lands near a random player (or a station) and sprouts. */
    private void seed(Vec3 o) {
        for (int n = 0; n < seedsPerCycle(); n++) {
            Vec3 near = chance(0.3) && !stations.isEmpty() ? stations.get(random.nextInt(stations.size())) : null;
            if (near == null) { ServerPlayer p = Mech.randomPlayer(this); if (p == null) return; near = p.position(); }
            double a = random.nextDouble() * Math.PI * 2, r = 2 + random.nextDouble() * 6;
            Vec3 at = Mech.polar(near, r, a, near.y);
            BlockPos g = Mech.ground(level(), at.x, at.z, (int) near.y - 4, (int) near.y + 4);
            if (g != null && plant(g.above())) { Mech.burst(serverLevel(), ParticleTypes.SPORE_BLOSSOM_AIR, Vec3.atCenterOf(g.above()), 10, 0.6); }
        }
        sound(SoundEvents.AZALEA_LEAVES_PLACE, 1.5F, 0.5F);
    }

    private boolean plant(BlockPos p) {
        if (hedge.size() >= MAX_HEDGE || !level().getBlockState(p).isAir() || !HEDGE.canSurvive(level(), p) || Mech.horiz(Vec3.atCenterOf(p), origin()) > 38) return false;
        for (ServerPlayer pl : party()) if (pl.blockPosition().equals(p) || pl.blockPosition().equals(p.below())) return false;   // never spawn inside someone
        placeTemp(p, HEDGE); hedge.add(p); return true;
    }

    /** Every hedge block tries to creep one block sideways. */
    private void spread() {
        List<BlockPos> snapshot = new ArrayList<>(hedge);
        for (BlockPos p : snapshot) {
            if (!chance(0.6)) continue;
            Direction d = Direction.Plane.HORIZONTAL.getRandomDirection(random);
            BlockPos n = p.relative(d);
            if (!level().getBlockState(n).isAir()) n = n.above(); if (!level().getBlockState(n).isAir()) n = p.relative(d).below();
            plant(n);
        }
    }

    /** Count what the party has cut; every 8 cuts fires the prune wave. */
    private void audit() {
        for (Iterator<BlockPos> it = hedge.iterator(); it.hasNext(); ) { BlockPos p = it.next(); if (!level().getBlockState(p).is(Blocks.SWEET_BERRY_BUSH)) { it.remove(); tempBlocks.remove(p); cut++; } }
        if (cut >= 8) { cut -= 8; pruneWave(); }
    }

    private void pruneWave() {
        int cleared = 0;
        for (Vec3 s : stations) for (Iterator<BlockPos> it = hedge.iterator(); it.hasNext(); ) {
            BlockPos p = it.next(); if (Mech.horiz(Vec3.atCenterOf(p), s) > 6) continue;
            level().setBlock(p, Blocks.AIR.defaultBlockState(), 3); tempBlocks.remove(p); it.remove(); cleared++;
            serverLevel().sendParticles(ParticleTypes.COMPOSTER, p.getX() + 0.5, p.getY() + 0.5, p.getZ() + 0.5, 6, 0.3, 0.3, 0.3, 0.05);
        }
        stun = STUN; getNavigation().stop();
        shout("Prune wave! " + cleared + " thorns wither and the Thornmother reels — strike her now!");
        sound(SoundEvents.COMPOSTER_READY, 2F, 0.7F); sound(SoundEvents.RAVAGER_STUNNED, 2F, 0.6F);
    }

    /** A station overgrown for 10 s heals her 10 %. */
    private void stations(Vec3 o) {
        for (int i = 0; i < stations.size(); i++) {
            boolean over = false; for (BlockPos p : hedge) if (Mech.horiz(Vec3.atCenterOf(p), stations.get(i)) <= CIRCLE) { over = true; break; }
            overgrown[i] = over ? overgrown[i] + 20 : 0;
            if (over && tickCount % 40 == 0) Mech.column(serverLevel(), Mech.RED, stations.get(i), 3, 4);
            if (overgrown[i] >= 200) { overgrown[i] = 0; heal(getMaxHealth() * 0.1F); shout("A pruning station is choked — the Thornmother drinks from it and heals!"); sound(SoundEvents.BONE_MEAL_USE, 2F, 0.5F); Mech.burst(serverLevel(), ParticleTypes.HEART, position().add(0, kind.height * 0.7, 0), 12, 3); }
        }
    }

    private void thornDamage() {
        for (ServerPlayer p : party()) {
            BlockPos at = p.blockPosition();
            if (level().getBlockState(at).is(Blocks.SWEET_BERRY_BUSH) || level().getBlockState(at.above()).is(Blocks.SWEET_BERRY_BUSH)) {
                p.hurt(damageSources().mobAttack(this), 2); p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 30, 1));
            }
        }
    }

    @Override protected void onDefeated() { super.onDefeated(); hedge.clear(); }
}
