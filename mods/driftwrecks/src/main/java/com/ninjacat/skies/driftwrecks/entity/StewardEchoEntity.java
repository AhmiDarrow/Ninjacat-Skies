package com.ninjacat.skies.driftwrecks.entity;

import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.driftwrecks.wreck.DriftManager;
import com.ninjacat.skies.driftwrecks.wreck.Wreck;
import com.ninjacat.skies.driftwrecks.wreck.WreckObjectives;
import net.minecraft.core.GlobalPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

import javax.annotation.Nullable;
import java.util.EnumSet;
import java.util.Optional;

/**
 * A lost Steward echo: a quiet, translucent cat that follows the nearest member of the wreck's Clowder. Walk it
 * across your tether to your pad and it settles (Escort done). Left alone too long, or dropped into the void, it
 * fades; the chests are still yours.
 */
public class StewardEchoEntity extends PathfinderMob {
    private static final int ABANDON_TICKS = 20 * 120;
    private int wreckId = -1;
    private int alone;

    public StewardEchoEntity(EntityType<? extends StewardEchoEntity> type, Level level) {
        super(type, level);
        setPersistenceRequired();
    }

    public static AttributeSupplier.Builder createAttributes() {
        return PathfinderMob.createMobAttributes().add(Attributes.MAX_HEALTH, 20.0).add(Attributes.MOVEMENT_SPEED, 0.32).add(Attributes.FOLLOW_RANGE, 32.0);
    }

    public void bind(int wreck) { this.wreckId = wreck; }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(1, new FollowClowderGoal(this));
        goalSelector.addGoal(2, new LookAtPlayerGoal(this, Player.class, 8.0F));
        goalSelector.addGoal(3, new RandomLookAroundGoal(this));
    }

    @Nullable
    Wreck wreck() {
        if (!(level() instanceof ServerLevel sl)) return null;
        return DriftManager.get(sl.getServer()).byId(wreckId);
    }

    @Nullable
    ServerPlayer nearestMember(double range) {
        Wreck w = wreck();
        if (w == null || !(level() instanceof ServerLevel sl)) return null;
        Optional<Clowder> c = LoomTension.clowderById(sl.getServer(), w.team);
        ServerPlayer best = null;
        double bd = range * range;
        if (c.isPresent()) for (ServerPlayer p : c.get().onlineMembers()) {
            if (p.level() != level() || p.isSpectator()) continue;
            double d = p.distanceToSqr(this);
            if (d < bd) { bd = d; best = p; }
        }
        return best;
    }

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) {
            if (random.nextInt(6) == 0) level().addParticle(ParticleTypes.GLOW, getRandomX(0.5), getY() + 0.4, getRandomZ(0.5), 0, 0.02, 0);
            return;
        }
        if (tickCount % 10 != 0) return;
        ServerLevel sl = (ServerLevel) level();
        DriftManager m = DriftManager.get(sl.getServer());
        Wreck w = wreck();
        if (w == null || w.phase != Wreck.Phase.ACTIVE) { discard(); return; }
        if (getY() < w.minY - 30) { WreckObjectives.echoLost(m, sl, w); fade(); return; }
        // home: at the tether's pad end or beside the Tension Post
        boolean home = w.tetherStart != null && w.tetherStart.closerToCenterThan(position(), 4);
        if (!home) {
            GlobalPos post = LoomTension.clowderById(sl.getServer(), w.team).map(LoomTension::postOf).orElse(null);
            home = post != null && post.dimension().equals(sl.dimension()) && post.pos().closerToCenterThan(position(), 8);
        }
        if (home) { WreckObjectives.echoHome(m, sl, w); fade(); return; }
        if (nearestMember(32) == null) {
            alone += 10;
            if (alone >= ABANDON_TICKS) { WreckObjectives.echoLost(m, sl, w); fade(); }
        } else alone = 0;
    }

    private void fade() {
        if (level() instanceof ServerLevel sl) sl.sendParticles(ParticleTypes.GLOW, getX(), getY() + 0.4, getZ(), 30, 0.3, 0.4, 0.3, 0.05);
        discard();
    }

    @Override
    public boolean isInvulnerableTo(DamageSource src) {
        // players cannot hurt the echo; the void and mobs can
        return src.getEntity() instanceof Player || super.isInvulnerableTo(src);
    }

    @Override
    public void die(DamageSource src) {
        if (level() instanceof ServerLevel sl) {
            Wreck w = wreck();
            if (w != null) WreckObjectives.echoLost(DriftManager.get(sl.getServer()), sl, w);
        }
        super.die(src);
    }

    @Override public boolean removeWhenFarAway(double d) { return false; }
    @Override protected SoundEvent getAmbientSound() { return random.nextInt(4) == 0 ? SoundEvents.CAT_PURR : null; }
    @Override protected SoundEvent getHurtSound(DamageSource src) { return SoundEvents.CAT_HURT; }
    @Override protected SoundEvent getDeathSound() { return SoundEvents.CAT_DEATH; }
    @Override protected float getSoundVolume() { return 0.4F; }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("Wreck", wreckId); tag.putInt("Alone", alone);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        wreckId = tag.getInt("Wreck"); alone = tag.getInt("Alone");
    }

    /** Pad after the nearest Clowder member, keeping 2-3 blocks behind. */
    static final class FollowClowderGoal extends Goal {
        private final StewardEchoEntity echo;
        @Nullable private ServerPlayer target;
        private int repath;

        FollowClowderGoal(StewardEchoEntity echo) { this.echo = echo; setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK)); }

        @Override public boolean canUse() {
            target = echo.nearestMember(20);
            return target != null && target.distanceToSqr(echo) > 9;
        }
        @Override public boolean canContinueToUse() { return target != null && target.isAlive() && target.distanceToSqr(echo) > 4 && target.distanceToSqr(echo) < 900; }
        @Override public void start() { repath = 0; }
        @Override public void stop() { target = null; echo.getNavigation().stop(); }
        @Override public void tick() {
            if (target == null) return;
            echo.getLookControl().setLookAt(target, 10F, echo.getMaxHeadXRot());
            if (--repath <= 0) { repath = 10; echo.getNavigation().moveTo(target, 1.1); }
        }
    }
}
