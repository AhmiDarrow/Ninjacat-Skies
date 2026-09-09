package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

/**
 * Stone · the Grindmaw — ROUTE THE GRIT. Immune while its maw is closed. The four sieve chutes drop a block of
 * sieve grit (gravel) every 15 s; place it on the grindstone ring (r 14–21) and the ring carries it round one
 * block per 2 s. When the grit reaches the maw mark (a gold-lit point on the pit's inner edge) it is swallowed
 * and jams the maw open for 12 s. The ring pushes anyone standing on it; the pit itself is a slow, grinding hazard.
 * The ring reverses direction each phase. Rotation is simulated (blocks carried, players pushed) — the annulus itself is static.
 */
public class GrindmawGuardian extends GuardianEntity {
    private static final int RING_IN = 14, RING_OUT = 21, PIT = 9, CHUTE_R = 23, DROP_EVERY = 300, OPEN_TICKS = 240, STEP = 40;
    private int openTimer = 0, dir = 1;
    private double mouthAngle = Math.PI / 2;

    public GrindmawGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.GRINDMAW); }

    @Override protected String immuneMessage() { return "The Grindmaw's maw is shut. Ride sieve grit round the grindstone into its mouth."; }
    @Override protected boolean mobile() { return false; }   // it squats in its own grit pit
    @Override protected double meleeReach() { return kind.width * 0.75 + 4.5; }

    @Override
    protected void tickMechanic() {
        if (ageInFight == 1) { shout("The Grindmaw answers for the Cut. Its maw only opens for its own grit: take a chute's grit block, set it on the grindstone ring and let the ring carry it into the gold-lit mouth."); }
        Vec3 o = origin();
        if (arena() != null && ageInFight % DROP_EVERY == 40) dropGrit(o);
        if (arena() == null && openTimer <= 0 && ageInFight % 400 == 60) jamOpen();        // no chutes to route grit from (a shade, or /summon): the maw jams on a timer
        if (ageInFight % STEP == 0) { carryGrit(o); }
        pushRiders(o);
        tickMouth(o);
        if (openTimer > 0 && --openTimer == 0) { say("The maw grinds shut again."); sound(SoundEvents.IRON_TRAPDOOR_CLOSE, 1.5F, 0.5F); }
        setImmune(openTimer <= 0);
    }

    @Override
    protected void onPhase(int phase) {
        dir = -dir; mouthAngle = mouthAngle + Math.PI / 2 * (random.nextBoolean() ? 1 : -1);
        shout("The grindstone reverses! The maw turns to " + compass(mouthAngle) + ".");
        sound(SoundEvents.GRINDSTONE_USE, 2F, 0.4F);
    }

    /** One gravel item falls from each of the four sieve chutes. */
    private void dropGrit(Vec3 o) {
        for (int i = 0; i < 4; i++) {
            Vec3 at = Mech.polar(o, CHUTE_R, Math.PI / 2 * i, o.y + 6);
            ItemStack grit = new ItemStack(Items.GRAVEL); grit.set(net.minecraft.core.component.DataComponents.CUSTOM_NAME, Component.literal("Sieve Grit"));
            ItemEntity e = new ItemEntity(level(), at.x, at.y, at.z, grit); e.setDeltaMovement(0, -0.2, 0); e.setUnlimitedLifetime(); e.addTag(Mech.tag(this));
            serverLevel().addFreshEntity(e);
            Mech.burst(serverLevel(), ParticleTypes.CLOUD, at, 8, 0.6);
        }
        say("The sieve chutes pour fresh grit."); sound(SoundEvents.GRAVEL_FALL, 1.5F, 0.8F);
    }

    /** Every 2 s each gravel block on the ring advances one block tangentially; on the maw mark it is eaten. */
    private final java.util.Set<BlockPos> planGrit = new java.util.HashSet<>();
    private boolean planGritScanned = false;
    private void carryGrit(Vec3 o) {
        List<BlockPos> found = new ArrayList<>();
        if (!planGritScanned) {                                                   // gravel the arena plan itself put on the ring
            planGritScanned = true;
            BlockPos.MutableBlockPos q = new BlockPos.MutableBlockPos();
            for (int x = -RING_OUT; x <= RING_OUT; x++) for (int z = -RING_OUT; z <= RING_OUT; z++) { int r2 = x * x + z * z; if (r2 < RING_IN * RING_IN || r2 > RING_OUT * RING_OUT) continue; for (int y = 0; y <= 2; y++) { q.set((int) Math.floor(o.x) + x, (int) o.y + y, (int) Math.floor(o.z) + z); if (level().getBlockState(q).is(Blocks.GRAVEL)) planGrit.add(q.immutable()); } }
        }
        BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
        for (int x = -RING_OUT; x <= RING_OUT; x++) for (int z = -RING_OUT; z <= RING_OUT; z++) {
            int r2 = x * x + z * z; if (r2 < RING_IN * RING_IN || r2 > RING_OUT * RING_OUT) continue;
            for (int y = 0; y <= 2; y++) { m.set((int) Math.floor(o.x) + x, (int) o.y + y, (int) Math.floor(o.z) + z); if (level().getBlockState(m).is(Blocks.GRAVEL)) found.add(m.immutable()); }
        }
        for (BlockPos p : found) {
            Vec3 c = Vec3.atCenterOf(p); double r = Mech.horiz(c, o), a = Mech.angleOf(o, c);
            BlockPos np = p;
            for (int k = 1; k <= 3 && np.equals(p); k++) np = BlockPos.containing(Mech.polar(o, r, a + dir * k * 0.8 / r, c.y));
            level().setBlock(p, Blocks.AIR.defaultBlockState(), 3);
            if (level().getBlockState(np).isAir()) { level().setBlock(np, Blocks.GRAVEL.defaultBlockState(), 3); serverLevel().playSound(null, np, SoundEvents.GRAVEL_STEP, net.minecraft.sounds.SoundSource.BLOCKS, 1F, 0.6F); }
            if (planGrit.contains(p) || planGrit.contains(np)) { planGrit.remove(p); planGrit.add(np); continue; }   // the quarry's own rubble rides the ring but feeds nothing
            double da = Math.abs(Math.atan2(Math.sin(Mech.angleOf(o, Vec3.atCenterOf(np)) - mouthAngle), Math.cos(Mech.angleOf(o, Vec3.atCenterOf(np)) - mouthAngle)));
            if (da <= 2.5 / RING_IN) { level().setBlock(np, Blocks.AIR.defaultBlockState(), 3); jamOpen(); }
        }
    }

    private void jamOpen() {
        openTimer = OPEN_TICKS;
        shout("Grit in the gears! The Grindmaw's maw is jammed open — strike now!");
        sound(SoundEvents.IRON_TRAPDOOR_OPEN, 2F, 0.4F); Mech.burst(serverLevel(), ParticleTypes.CRIT, position().add(0, 4, 0), 40, 3);
    }

    /** Gold sparks mark the maw; the pit grinds anyone who stays in it. */
    private void tickMouth(Vec3 o) {
        Vec3 mouth = Mech.polar(o, RING_IN, mouthAngle, o.y + 0.5);
        if (tickCount % 4 == 0) { Mech.column(serverLevel(), Mech.GOLD, mouth, 3, 6); ring(Mech.GOLD, mouth, 2.5, 8, o.y + 0.2); }
        if (tickCount % 60 == 0) for (ServerPlayer p : party()) if (Mech.horiz(p.position(), o) < PIT && p.getY() < o.y + 0.5) {
            p.hurt(damageSources().mobAttack(this), 2); p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 0));
            p.displayClientMessage(com.ninjacat.skies.lib.NinjacatText.teal("The grit pit grinds at you."), true);
        }
    }

    /** Standing on the ring moves you with it. */
    private void pushRiders(Vec3 o) {
        if (tickCount % 5 != 0) return;
        for (ServerPlayer p : party()) {
            double r = Mech.horiz(p.position(), o);
            if (r < RING_IN - 0.5 || r > RING_OUT + 0.5 || !p.onGround() || p.getY() > o.y + 3) continue;
            double a = Mech.angleOf(o, p.position()) + Math.PI / 2 * dir;
            p.push(Math.cos(a) * 0.12, 0, Math.sin(a) * 0.12); p.hurtMarked = true;
        }
    }

    private static String compass(double a) { double d = Math.toDegrees(a) % 360; if (d < 0) d += 360; return d < 45 || d >= 315 ? "the east" : d < 135 ? "the south" : d < 225 ? "the west" : "the north"; }

    @Override protected void onDefeated() { super.onDefeated(); Mech.discardMinions(this); }
}
