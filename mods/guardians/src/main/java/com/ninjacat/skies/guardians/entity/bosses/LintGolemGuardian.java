package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Snowball;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Easy · the Lint Golem — THE DOCK DUSTBIN. A zero-risk tutorial fight. The golem throws lint balls (0 damage,
 * Blindness 2 s), staggers when it is hit and then scurries to the far side of the washing line to lob more.
 * Stomping the red rug (the rug is a red-wool patch south of the line) makes it sneeze: 2.5 s of stagger and
 * double damage. Its fists are lint-soft — the melee is a shove for 0 damage. Phase 2 throws two balls a volley;
 * phase 3 adds a lint puff (Blindness in r 5 after a 1 s tell). Nothing here can hurt a player.
 */
public class LintGolemGuardian extends GuardianEntity {
    private static final int SNEEZE = 50, SNEEZE_CD = 200, FLEE = 70, PUFF_EVERY = 200, PUFF_TELL = 20, LINE_HALF = 9, MAX_BALLS = 8;
    private record Ball(Snowball ball, UUID target) {}
    private final List<Ball> balls = new ArrayList<>();
    private int stagger = 0, sneezeCd = 0, flee = 0, nextThrow = 60, puffTell = -1;
    @Nullable private Vec3 hideSpot;

    public LintGolemGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.LINTGOLEM); }

    @Override protected boolean mobile() { return stagger <= 0 && flee <= 0; }
    @Override protected int meleeCooldown() { return 40; }
    @Override protected SoundEvent hurtSoundOverride() { return SoundEvents.WOOL_HIT; }
    /** A shove, never a wound. */
    @Override
    protected void onMeleeHit(LivingEntity t) {
        Vec3 push = t.position().subtract(position()).normalize().scale(0.8); t.push(push.x, 0.3, push.z); t.hurtMarked = true;
        Mech.burst(serverLevel(), ParticleTypes.CLOUD, t.position().add(0, 1, 0), 8, 0.5); sound(SoundEvents.WOOL_PLACE, 1.5F, 0.6F);
    }
    /** Sneezing = double damage: the rug is the "damage window" this fight teaches. */
    @Override public boolean hurt(DamageSource src, float amount) { return super.hurt(src, sneezeCd > SNEEZE_CD - SNEEZE ? amount * 2 : amount); }
    /** Staggers when hit, then scurries behind the washing. */
    @Override
    protected void onDamagedBy(LivingEntity by, float amount) {
        if (stagger > 0) return;
        stagger = 12; flee = FLEE; getNavigation().stop();
        Vec3 away = position().subtract(by.position()).normalize().scale(0.4); setDeltaMovement(away.x, 0.2, away.z); hurtMarked = true;
        Mech.burst(serverLevel(), ParticleTypes.CLOUD, position().add(0, kind.height * 0.5, 0), 12, 1.2);
    }

    @Override
    protected void tickMechanic() {
        if (ageInFight == 1) shout("The Lint Golem answers for the Cut... sort of. It throws lint, it hides behind the washing, and it cannot hurt you. Stomp the red rug to make it sneeze, then hit it while it reels.");
        if (sneezeCd > 0) sneezeCd--;
        tickBalls();
        if (stagger > 0) { stagger--; getNavigation().stop(); if (tickCount % 4 == 0) particles(ParticleTypes.CLOUD, position().add(0, kind.height * 0.7, 0), 3, 0.8, 0.02); return; }
        if (flee > 0) tickFlee();
        if (tickCount % 20 == 0 && sneezeCd == 0) checkRug();
        if (--nextThrow <= 0) throwLint();
        if (phase() >= 3) tickPuff();
    }

    @Override
    protected void onPhase(int phase) {
        shout(phase == 1 ? "The Lint Golem sheds a little. It throws faster." : phase == 2 ? "The Lint Golem throws with both hands!" : "The Lint Golem is coming apart in tufts — mind the puff!");
        Mech.burst(serverLevel(), ParticleTypes.CLOUD, position().add(0, kind.height * 0.5, 0), 30, 2);
    }

    // ------------------------------------------------------------------ lint balls
    /** A snowball dressed as wool; when it lands next to a player it puts lint in their eyes. */
    private void throwLint() {
        nextThrow = Math.max(25, 50 - 8 * phase());
        int volley = phase() >= 2 ? 2 : 1;
        List<ServerPlayer> ps = party(); if (ps.isEmpty()) return;
        for (int i = 0; i < volley && balls.size() < MAX_BALLS; i++) {
            ServerPlayer t = ps.get((tickCount + i) % ps.size());
            if (!t.isAlive() || t.distanceTo(this) > 40) continue;
            Snowball b = new Snowball(level(), this);
            b.setItem(new ItemStack(Items.WHITE_WOOL));
            double dx = t.getX() - b.getX(), dy = t.getEyeY() - 0.6 - b.getY(), dz = t.getZ() - b.getZ();
            double dist = Math.sqrt(dx * dx + dz * dz);
            b.shoot(dx, dy + dist * 0.18, dz, 1.3F, 3F);
            serverLevel().addFreshEntity(b); balls.add(new Ball(b, t.getUUID()));
        }
        playClip(CLIP_ATTACK); sound(SoundEvents.SNOWBALL_THROW, 1.2F, 0.7F);
    }

    private void tickBalls() {
        for (int i = balls.size() - 1; i >= 0; i--) {
            Ball b = balls.get(i);
            if (b.ball.isAlive() && b.ball.tickCount < 100) continue;
            balls.remove(i);
            Vec3 at = b.ball.position();
            for (ServerPlayer p : party()) if (p.isAlive() && p.distanceToSqr(at) < 2.5 * 2.5) {
                p.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 40, 0));
                p.displayClientMessage(NinjacatText.teal("Lint in your eyes!"), true);
                serverLevel().sendParticles(ParticleTypes.CLOUD, p.getX(), p.getEyeY(), p.getZ(), 10, 0.4, 0.3, 0.4, 0.02);
            }
        }
    }

    // ------------------------------------------------------------------ hiding and sneezing
    /** The washing line runs east–west through the origin: hide on whichever side the party is not. */
    private void tickFlee() {
        flee--;
        if (flee % 10 == 0 || hideSpot == null) {
            Vec3 o = origin(); double sx = 0, sz = 0; int n = 0;
            for (ServerPlayer p : party()) { sx += p.getX(); sz += p.getZ(); n++; }
            if (n == 0) { flee = 0; return; }
            double mx = Math.max(o.x - LINE_HALF, Math.min(o.x + LINE_HALF, sx / n)), side = sz / n >= o.z ? -4.5 : 4.5;
            hideSpot = new Vec3(mx, o.y, o.z + side);
            getNavigation().moveTo(hideSpot.x, hideSpot.y, hideSpot.z, 1.25);
        }
        playClip(CLIP_WALK);
        if (hideSpot != null && Mech.horiz(position(), hideSpot) < 1.5) { flee = 0; getNavigation().stop(); }
    }

    /** Anyone standing on the red rug beats the dust out of it — the golem sneezes and staggers. */
    private void checkRug() {
        for (ServerPlayer p : party()) {
            if (!p.onGround() || !level().getBlockState(p.getOnPos()).is(Blocks.RED_WOOL) || p.distanceTo(this) > 24) continue;
            stagger = SNEEZE; sneezeCd = SNEEZE_CD; flee = 0; getNavigation().stop();
            Vec3 c = position().add(0, kind.height * 0.8, 0);
            Mech.burst(serverLevel(), ParticleTypes.CLOUD, c, 40, 1.5); Mech.burst(serverLevel(), ParticleTypes.SNEEZE, c, 20, 1);
            sound(SoundEvents.PANDA_SNEEZE, 2F, 0.6F);
            shout(p.getName().getString() + " beats the rug — the Lint Golem sneezes and reels! Hit it now (double damage).");
            return;
        }
    }

    /** Phase 3: a lint puff — a 1 s tell ring, then Blindness to everyone within r 5. Still 0 damage. */
    private void tickPuff() {
        if (puffTell < 0) { if (ageInFight % PUFF_EVERY == 0) { puffTell = 0; say("The Lint Golem swells up..."); sound(SoundEvents.PUFFER_FISH_BLOW_UP, 1.5F, 0.6F); } return; }
        puffTell++;
        ring(ParticleTypes.CLOUD, position(), 5, 20, getY() + 0.3);
        if (puffTell < PUFF_TELL) return;
        puffTell = -1; Mech.burst(serverLevel(), ParticleTypes.CLOUD, position().add(0, 2, 0), 80, 3); sound(SoundEvents.PUFFER_FISH_BLOW_OUT, 2F, 0.5F);
        for (ServerPlayer p : party()) if (p.distanceTo(this) <= 5.5) { p.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 50, 0)); p.displayClientMessage(NinjacatText.teal("Lint everywhere!"), true); }
    }

    @Override protected void onDefeated() { super.onDefeated(); for (Ball b : balls) b.ball.discard(); balls.clear(); }
}
