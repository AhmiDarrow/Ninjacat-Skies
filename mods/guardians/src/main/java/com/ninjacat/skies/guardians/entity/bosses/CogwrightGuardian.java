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

import java.util.ArrayList;
import java.util.List;

/**
 * Clock · the Cogwright — PATTERN. Four rings (r 7/14/21/28, 8/12/16/20 tiles) turn, the inner slowest. The boss
 * "winds": tiles light one after another (3 + phase of them); the party then has 12 s to step on them in that
 * order while the rings carry them round. Success opens the chassis for 8 s; failure fires every gear-tower
 * (arc shock, 3 hearts, ring-wide) and it winds again. The pendulum ticks every 10 s and the rings reverse.
 * Rotation is simulated: the lit tile positions and anyone standing on a ring move; the annuli themselves stay put.
 */
public class CogwrightGuardian extends GuardianEntity {
    private static final double[] RADII = {7, 14, 21, 28};
    private static final int[] COUNT = {8, 12, 16, 20}, PERIOD = {60, 45, 30, 20};
    private static final int SOLVE_TICKS = 240, OPEN_TICKS = 160, SHOW_GAP = 14, TOWERS = 6, TOWER_R = 30;
    private enum Stage { IDLE, WIND, SOLVE, OPEN }
    private final Mech.Ledger lit = new Mech.Ledger();
    private final List<int[]> sequence = new ArrayList<>();      // {ring, index}
    private final int[] offset = new int[4];
    private Stage stage = Stage.IDLE; private int stageTicks = 0, progress = 0, dir = 1;

    public CogwrightGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.COGWRIGHT); }

    @Override protected String immuneMessage() { return "The Cogwright's chassis is shut. Step the lit tiles in the order it wound them."; }

    @Override
    protected void tickMechanic() {
        if (ageInFight == 1) { shout("The Cogwright answers for the Cut. It winds a pattern into the rings: watch which tiles light and in what order, then walk them in that order before the escapement runs out. Get it wrong and every gear-tower arcs."); stage = Stage.IDLE; stageTicks = -40; }
        Vec3 o = origin();
        stageTicks++;
        if (ageInFight % 200 == 0) { dir = -dir; sound(SoundEvents.NOTE_BLOCK_BELL.value(), 2F, 0.6F); say("The pendulum swings back — the rings reverse."); }
        for (int r = 0; r < 4; r++) if (ageInFight % PERIOD[r] == 0) offset[r] += dir;
        if (ageInFight % 5 == 0 && arena() != null) pushRiders(o);
        setImmune(stage != Stage.OPEN);
        switch (stage) {
            case IDLE -> { if (stageTicks >= 40) wind(); }
            case WIND -> tickWind(o);
            case SOLVE -> tickSolve(o);
            case OPEN -> { if (stageTicks >= OPEN_TICKS) { say("The chassis snaps shut."); setStage(Stage.IDLE); } }
        }
        if (tickCount % 40 == 0 && arena() != null && Mech.horiz(position(), o) > 31) getNavigation().moveTo(o.x, o.y, o.z, 1.0);
    }

    @Override protected void onPhase(int phase) { shout("The Cogwright re-winds — the pattern grows to " + (3 + phase) + " tiles."); if (stage != Stage.OPEN) setStage(Stage.IDLE); }
    private void setStage(Stage s) { stage = s; stageTicks = 0; }

    // ------------------------------------------------------------------ tiles
    /** Rings shrink to a third when there is no arena (a shade on its ø 22 platform, or /summon). */
    private double ringScale() { return arena() == null ? 0.32 : 1.0; }
    private BlockPos tile(Vec3 o, int ring, int index) {
        double a = Math.PI * 2 * (index + offset[ring]) / COUNT[ring];
        Vec3 at = Mech.polar(o, RADII[ring] * ringScale(), a, o.y);
        BlockPos g = Mech.ground(level(), at.x, at.z, (int) o.y - 2, (int) o.y + 2);
        return g != null ? g : BlockPos.containing(at).below();
    }
    private void light(BlockPos p, net.minecraft.world.level.block.state.BlockState s) { if (!lit.has(p)) lit.set(level(), p, s); else level().setBlock(p, s, 3); }
    private void unlightAll() { lit.restoreAll(level()); }
    /** Keep the sequence tiles lit at their current (rotated) positions: pending = shroomlight, done = sea lantern. */
    private void relight(Vec3 o) {
        unlightAll();
        for (int i = 0; i < sequence.size(); i++) light(tile(o, sequence.get(i)[0], sequence.get(i)[1]), i < progress ? Blocks.SEA_LANTERN.defaultBlockState() : Blocks.SHROOMLIGHT.defaultBlockState());
    }

    private void wind() {
        sequence.clear(); int n = 3 + phase();
        for (int i = 0; i < n; i++) { int r = random.nextInt(4); sequence.add(new int[]{r, random.nextInt(COUNT[r])}); }
        progress = 0; setStage(Stage.WIND); sound(SoundEvents.NOTE_BLOCK_CHIME.value(), 2F, 0.5F);
        say("The Cogwright winds... watch the tiles.");
    }

    private void tickWind(Vec3 o) {
        int step = stageTicks / SHOW_GAP;
        if (stageTicks % SHOW_GAP == 0 && step < sequence.size()) {
            unlightAll(); BlockPos t = tile(o, sequence.get(step)[0], sequence.get(step)[1]);
            light(t, Blocks.OCHRE_FROGLIGHT.defaultBlockState());
            Mech.column(serverLevel(), Mech.GOLD, Vec3.atCenterOf(t).add(0, 0.6, 0), 4, 8);
            Mech.soundAt(serverLevel(), Vec3.atCenterOf(t), SoundEvents.NOTE_BLOCK_PLING.value(), 2F, 0.6F + 0.15F * step);
        }
        if (stageTicks >= SHOW_GAP * sequence.size() + 10) { setStage(Stage.SOLVE); relight(o); shout("Now — walk the tiles in that order. Twelve seconds."); }
    }

    private void tickSolve(Vec3 o) {
        if (stageTicks % 10 == 0) relight(o);
        BlockPos next = tile(o, sequence.get(progress)[0], sequence.get(progress)[1]);
        for (ServerPlayer p : party()) {
            BlockPos on = p.getOnPos();
            if (on.equals(next)) { progress++; Mech.soundAt(serverLevel(), p.position(), SoundEvents.NOTE_BLOCK_PLING.value(), 2F, 0.6F + 0.15F * progress); Mech.burst(serverLevel(), ParticleTypes.HAPPY_VILLAGER, p.position(), 10, 0.6); relight(o); if (progress >= sequence.size()) { succeed(); return; } next = tile(o, sequence.get(progress)[0], sequence.get(progress)[1]); continue; }
            for (int i = progress + 1; i < sequence.size(); i++) if (on.equals(tile(o, sequence.get(i)[0], sequence.get(i)[1]))) { fail("Wrong tile!"); return; }
        }
        if (stageTicks >= SOLVE_TICKS) fail("The escapement ran out!");
        else if (stageTicks % 20 == 0 && stageTicks >= SOLVE_TICKS - 60) sound(SoundEvents.NOTE_BLOCK_HAT.value(), 1.5F, 1.5F);
    }

    private void succeed() {
        unlightAll(); setStage(Stage.OPEN);
        shout("The pattern holds — the Cogwright's chassis opens! Strike!"); sound(SoundEvents.IRON_DOOR_OPEN, 2F, 0.5F);
        Mech.burst(serverLevel(), ParticleTypes.ELECTRIC_SPARK, position().add(0, kind.height * 0.5, 0), 40, 4);
    }

    private void fail(String why) {
        unlightAll(); Vec3 o = origin();
        for (int k = 0; k < TOWERS; k++) Mech.arc(serverLevel(), Mech.polar(o, TOWER_R * ringScale(), Math.PI / 3 * k, o.y));
        areaDamage(o, 40 * ringScale(), 6, 0.2); shout(why + " The gear-towers arc.");
        setStage(Stage.IDLE);
    }

    /** Standing on the outer three rings drifts you with them. */
    private void pushRiders(Vec3 o) {
        for (ServerPlayer p : party()) {
            double r = Mech.horiz(p.position(), o); if (r < 11 || r > 31 || !p.onGround() || Math.abs(p.getY() - o.y) > 3) continue;
            int ring = r < 17.5 ? 1 : r < 24.5 ? 2 : 3;
            double a = Mech.angleOf(o, p.position()) + Math.PI / 2 * dir, sp = 0.09 * 60 / PERIOD[ring] * 0.5;
            p.push(Math.cos(a) * sp, 0, Math.sin(a) * sp); p.hurtMarked = true;
        }
    }

    @Override protected void onDefeated() { super.onDefeated(); unlightAll(); }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        lit.save(tag, "Lit");
    }
    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        lit.load(tag, "Lit", level());
    }
}
