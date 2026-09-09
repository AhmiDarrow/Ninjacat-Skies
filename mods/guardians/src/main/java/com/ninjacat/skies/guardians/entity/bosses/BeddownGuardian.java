package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;

/**
 * Soil · the Beddown — BURY. Every quarter of HP the colossus slams and a 3-deep dirt layer floods the pit and
 * first tier; it is immune inside it. One of the seven root-seams lights up: dig to it and break the glowing
 * root core to end the immunity, and the layer sinks back into the rim. Rising dirt lifts players, never buries them.
 */
public class BeddownGuardian extends GuardianEntity {
    private static final int FILL_RADIUS = 15, LAYER = 3, PER_TICK = 160, SEAMS = 7;
    private final Mech.Ledger layer = new Mech.Ledger();
    private final List<BlockPos> fillQueue = new ArrayList<>();
    @Nullable private BlockPos core;
    private int slamTimer = -1, buryTicks = 0, sinking = 0;

    public BeddownGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.BEDDOWN); }

    @Override protected String immuneMessage() { return "The Beddown sleeps under the soil. Dig to the glowing seam and break its root core."; }
    @Override protected boolean mobile() { return core == null && slamTimer < 0; }

    @Override
    protected void tickMechanic() {
        if (ageInFight == 1) shout("The Beddown answers for the Cut. When it slams and the soil rises, dig for the seam that glows.");
        if (slamTimer >= 0) tickSlam();
        if (!fillQueue.isEmpty()) tickFill();
        if (core != null) tickBuried();
        if (sinking > 0) { sinking = layer.restore(level(), PER_TICK); if (sinking == 0) sound(SoundEvents.GRAVEL_BREAK, 1.2F, 0.6F); }
    }

    @Override
    protected void onPhase(int phase) {
        if (core != null || slamTimer >= 0) return;
        slamTimer = 0; getNavigation().stop(); playClip(CLIP_ATTACK);
        say("The Beddown rears up... the ground is coming.");
    }

    /** 0.9 s telegraph then the slam: 3 hearts + knockback in r 8, and the burial starts. */
    private void tickSlam() {
        slamTimer++;
        Vec3 o = position();
        if (slamTimer < 18) { ring(ParticleTypes.CRIT, o, 8, 24, o.y + 0.3); if (slamTimer % 6 == 0) sound(SoundEvents.RAVAGER_STUNNED, 1.5F, 0.5F); return; }
        Mech.thud(serverLevel(), o); areaDamage(o, 9, 6, 0.8); sound(SoundEvents.GENERIC_EXPLODE.value(), 2F, 0.5F);
        slamTimer = -1; startBurial();
    }

    private void startBurial() {
        Vec3 o = origin();
        if (arena() == null) { say("(no arena — the soil stays still)"); return; }
        // pick the seam that surfaces this time and plant the core on the pit floor before the dirt covers it
        double a = Math.PI * 2 * random.nextInt(SEAMS) / SEAMS;
        core = BlockPos.containing(Mech.polar(o, 6, a, o.y));
        if (!serverLevel().getBlockState(core).isAir()) core = BlockPos.containing(o.x, o.y, o.z).offset(3, 0, 3);
        layer.set(level(), core, Blocks.SHROOMLIGHT.defaultBlockState());
        // queue the columns: 3 dirt on top of whatever ground each column has (pit floor y0, tier 1 y+2)
        fillQueue.clear();
        for (int x = -FILL_RADIUS; x <= FILL_RADIUS; x++) for (int z = -FILL_RADIUS; z <= FILL_RADIUS; z++) {
            if (x * x + z * z > FILL_RADIUS * FILL_RADIUS) continue;
            BlockPos g = Mech.ground(level(), o.x + x, o.z + z, (int) o.y - 4, (int) o.y + 4);
            if (g == null) continue;
            for (int i = 1; i <= LAYER; i++) { BlockPos p = g.above(i); if (level().getBlockState(p).isAir()) fillQueue.add(p); }
        }
        java.util.Collections.shuffle(fillQueue, new java.util.Random(random.nextLong()));
        setImmune(true); buryTicks = 0;
        shout("The soil floods the pit. Find the seam that glows and break the root core!");
    }

    private void tickFill() {
        BlockState dirt = Blocks.DIRT.defaultBlockState();
        int n = Math.min(PER_TICK, fillQueue.size());
        for (int i = 0; i < n; i++) { BlockPos p = fillQueue.remove(fillQueue.size() - 1); if (level().getBlockState(p).isAir()) layer.set(level(), p, dirt); }
        if (tickCount % 4 == 0) sound(SoundEvents.ROOTED_DIRT_PLACE, 1.5F, 0.7F);
        // rising dirt lifts anyone standing in it rather than trapping them
        for (ServerPlayer p : party()) {
            if (Mech.horiz(p.position(), origin()) > FILL_RADIUS + 1) continue;
            BlockPos feet = p.blockPosition();
            if (!level().getBlockState(feet).isAir() || !level().getBlockState(feet.above()).isAir()) {
                int y = feet.getY(); while (y < feet.getY() + 6 && !level().getBlockState(new BlockPos(feet.getX(), y, feet.getZ())).isAir()) y++;
                p.teleportTo(serverLevel(), p.getX(), y + 0.1, p.getZ(), p.getYRot(), p.getXRot());
            }
        }
    }

    private void tickBuried() {
        buryTicks++;
        // the lit seam: a column of teal flame above the core so the party can find where to dig
        Vec3 c = Vec3.atCenterOf(core);
        if (tickCount % 2 == 0) Mech.column(serverLevel(), ParticleTypes.SOUL_FIRE_FLAME, c.add(0, 0.5, 0), 6, 6);
        if (tickCount % 20 == 0) Mech.burst(serverLevel(), Mech.TEAL, c.add(0, LAYER + 1.5, 0), 12, 1.2);
        boolean broken = !serverLevel().getBlockState(core).is(Blocks.SHROOMLIGHT);
        if (broken || buryTicks > 20 * 90) {                       // 90 s safety valve so a stuck party is never soft-locked
            if (broken) shout("The root core cracks. The Beddown heaves up through the soil!"); else say("The soil settles on its own...");
            sound(SoundEvents.WITHER_BREAK_BLOCK, 1.5F, 0.6F); Mech.burst(serverLevel(), ParticleTypes.EXPLOSION, c, 3, 1);
            core = null; fillQueue.clear(); setImmune(false); sinking = Math.max(1, layer.size());
        }
    }

    @Override
    protected void onDefeated() {
        super.onDefeated();
        layer.restoreAll(level()); fillQueue.clear(); core = null; sinking = 0;
    }
}
