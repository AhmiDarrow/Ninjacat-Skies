package com.ninjacat.skies.guardians.entity.bosses;

import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.animal.Bee;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CampfireBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import net.minecraft.util.Mth;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Predicate;

/**
 * Swarm · the Hivemind — QUEEN AND DRONES. The tower is fragile but hides its royal chamber: it is immune until
 * all six drone cells in the wall are smoked. Every wave each open cell pours drones (angry bees). A lit campfire
 * placed at a drone cell seals it for 30 s (then the smoke gutters out and the fire must be relit); sealing all
 * six exposes the chamber for 10 s. Comb cells rise and fall by a block every 5 s, reshaping cover.
 */
public class HivemindGuardian extends GuardianEntity {
    private static final int CELLS = 6, CELL_R = 34, WAVE = 400, SEAL_TICKS = 600, EXPOSE = 200;
    private static final double DRONE_R = 28, DRONE_JITTER = 0.5;
    private final int[] sealedUntil = new int[CELLS];
    private final BlockPos[] fire = new BlockPos[CELLS];
    private final Mech.Ledger comb = new Mech.Ledger();
    private final List<BlockPos> raised = new ArrayList<>();
    private int exposed = 0; private boolean armed = true;

    public HivemindGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.HIVEMIND); }

    @Override protected boolean mobile() { return false; }
    @Override protected MutableComponent immuneMessage() { return Component.translatable("message.guardians.hivemind.royal_chamber_shut_smoke_all"); }
    /** Drone cell k: arena_factory puts the six at 30° + 60°k on the wall (r 33); the plan mirrors y into -z. */
    private Vec3 cell(int k) { Vec3 o = origin(); return Mech.polar(o, CELL_R, cellAngle(k), o.y); }
    private static double cellAngle(int k) { return -(Math.PI / 3 * k + Math.PI / 6); }

    /**
     * Where cell k's drones come out: open air in front of the cell. The cell itself (r 34) sits inside the solid
     * amber wall (r 31-35, y 1-4), so drones spawned there suffocated. Tries r 28 inward to r 26 on the cell's axis
     * and stands on the highest solid block of that column (a wax ledge, honey pillar or risen comb lifts the spawn
     * onto it), taking the first spot whose whole jittered spawn volume is free. {@code solid} tests absolute block
     * positions. GuardianGameTests#hivemindDroneMouthsOpen checks every mouth against the shipped arena plan.
     */
    public static Vec3 droneMouth(Vec3 o, int k, Predicate<BlockPos> solid) {
        Vec3 first = null;
        int base = Mth.floor(o.y);
        for (double r = DRONE_R; r >= DRONE_R - 2; r -= 0.5) {
            Vec3 p = Mech.polar(o, r, cellAngle(k), o.y);
            int bx = Mth.floor(p.x), bz = Mth.floor(p.z), feet = base - 1;
            for (int y = base + 5; y >= base - 2; y--) if (solid.test(new BlockPos(bx, y, bz))) { feet = y + 1; break; }
            Vec3 at = new Vec3(p.x, feet, p.z);
            if (first == null) first = at;
            if (droneRoom(at, solid)) return at;
        }
        return first;      // players walled the mouth in: the drones still come
    }
    /** Every block a drone (0.7 wide, 0.6 tall) can touch when it spawns at {@code at} with the wave jitter is free. */
    public static boolean droneRoom(Vec3 at, Predicate<BlockPos> solid) {
        double w = DRONE_JITTER + 0.35;
        int y0 = Mth.floor(at.y);
        for (int x = Mth.floor(at.x - w); x <= Mth.floor(at.x + w); x++)
            for (int z = Mth.floor(at.z - w); z <= Mth.floor(at.z + w); z++)
                for (int y = y0; y <= y0 + 1; y++) if (solid.test(new BlockPos(x, y, z))) return false;
        return true;
    }
    private Vec3 droneMouth(int k) { Level l = level(); return droneMouth(origin(), k, p -> !l.getBlockState(p).getCollisionShape(l, p).isEmpty()); }
    private int droneCap() { return 6 + 3 * partySize(); }

    @Override
    protected void tickMechanic() {
        if (ageInFight == 1) shout("message.guardians.hivemind.hivemind_answers_for_cut_queen");
        Vec3 o = origin();
        if (tickCount % 10 == 0) tickSeals();
        if (arena() == null && exposed <= 0 && ageInFight % 400 == 60) { exposed = EXPOSE; shout("message.guardians.hivemind.royal_chamber_gapes_open_own"); }   // no wall cells to smoke (a shade, or /summon)
        if (exposed > 0) exposed--;
        setImmune(exposed <= 0);
        if (ageInFight % WAVE == 60) wave();
        if (arena() != null && ageInFight % 100 == 50) shiftCells(o);
        if (tickCount % 8 == 0) for (int k = 0; k < CELLS; k++) { Vec3 c = cell(k); boolean s = sealedUntil[k] > tickCount; Mech.column(serverLevel(), s ? ParticleTypes.CAMPFIRE_SIGNAL_SMOKE : Mech.GOLD, c.add(0, 1, 0), 4, 4); }
    }

    @Override protected void onPhase(int phase) { shout(phase == 3 ? "message.guardians.hivemind.hivemind_shrieks_every_cell_empties" : "message.guardians.hivemind.comb_hums_louder_more_drones"); if (phase == 3) wave(); }

    /** A campfire (lit) within 3.5 blocks of a cell mouth seals it; after 30 s the smoke gutters and the fire goes out. */
    private void tickSeals() {
        int sealed = 0;
        int newly = -1;   // the cell smoked this tick; its line is said after the loop so the count is the true total
        for (int k = 0; k < CELLS; k++) {
            if (sealedUntil[k] > tickCount) {
                sealed++;
                if (fire[k] != null && !isLitCampfire(level().getBlockState(fire[k]))) sealedUntil[k] = 0;      // fire removed → cell open again
                continue;
            }
            if (fire[k] != null) { BlockState s = level().getBlockState(fire[k]); if (isLitCampfire(s)) level().setBlock(fire[k], s.setValue(CampfireBlock.LIT, false), 3); fire[k] = null; Mech.burst(serverLevel(), ParticleTypes.LARGE_SMOKE, cell(k).add(0, 1, 0), 10, 1); }
            BlockPos f = findCampfire(cell(k));
            if (f != null) { fire[k] = f; sealedUntil[k] = tickCount + SEAL_TICKS; sealed++; newly = k; Mech.soundAt(serverLevel(), cell(k), SoundEvents.FIRE_EXTINGUISH, 1.5F, 0.6F); }
        }
        if (newly >= 0) say("message.guardians.hivemind.cell_smoked", sealed, CELLS);
        if (sealed == CELLS) { if (armed) { armed = false; exposed = EXPOSE; shout("message.guardians.hivemind.all_six_cells_are_smoked"); sound(SoundEvents.BEEHIVE_SHEAR, 2F, 0.5F); Mech.burst(serverLevel(), ParticleTypes.FALLING_HONEY, position().add(0, kind.height * 0.4, 0), 40, 3); } }
        else armed = true;
    }
    private static boolean isLitCampfire(BlockState s) { return (s.is(Blocks.CAMPFIRE) || s.is(Blocks.SOUL_CAMPFIRE)) && s.getValue(CampfireBlock.LIT); }
    @Nullable
    private BlockPos findCampfire(Vec3 c) {
        BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
        for (int dx = -3; dx <= 3; dx++) for (int dz = -3; dz <= 3; dz++) for (int dy = -1; dy <= 6; dy++) { m.set(Math.floor(c.x) + dx, c.y + dy, Math.floor(c.z) + dz); if (isLitCampfire(level().getBlockState(m))) return m.immutable(); }
        return null;
    }

    /** Each open cell pours drones until the cap; drones are angry bees. */
    private void wave() {
        int alive = Mech.countMinions(this), per = 1 + (partySize() + 1) / 2 + (phase() == 3 ? 1 : 0);
        for (int k = 0; k < CELLS; k++) {
            if (sealedUntil[k] > tickCount) continue;
            Vec3 c = droneMouth(k);
            for (int i = 0; i < per && alive < droneCap(); i++, alive++) {
                Bee b = Mech.spawn(this, EntityType.BEE, c.add((random.nextDouble() * 2 - 1) * DRONE_JITTER, random.nextDouble() * 0.4, (random.nextDouble() * 2 - 1) * DRONE_JITTER), "message.guardians.minion.drone", 12, 3);
                if (b == null) continue;
                ServerPlayer t = Mech.randomPlayer(this);
                if (t != null) { b.setPersistentAngerTarget(t.getUUID()); b.setRemainingPersistentAngerTime(2400); b.setTarget(t); }
            }
            Mech.burst(serverLevel(), ParticleTypes.FALLING_HONEY, c.add(0, 1, 0), 8, 1);
        }
        sound(SoundEvents.BEE_LOOP_AGGRESSIVE, 2F, 0.6F); say("message.guardians.hivemind.cells_pour_drones");
    }

    /** One comb cell rises (honeycomb on top) or one that rose falls back. Bounded to a block per 5 s. */
    private void shiftCells(Vec3 o) {
        if (!raised.isEmpty() && chance(0.5)) { BlockPos p = raised.remove(random.nextInt(raised.size())); if (level().getBlockState(p).is(Blocks.HONEYCOMB_BLOCK)) level().setBlock(p, Blocks.AIR.defaultBlockState(), 3); comb.forget(p); serverLevel().playSound(null, p, SoundEvents.HONEY_BLOCK_BREAK, net.minecraft.sounds.SoundSource.BLOCKS, 1F, 0.7F); return; }
        for (int tries = 0; tries < 6; tries++) {
            Vec3 at = Mech.polar(o, 4 + random.nextDouble() * 26, random.nextDouble() * Math.PI * 2, o.y);
            BlockPos g = Mech.ground(level(), at.x, at.z, (int) o.y - 2, (int) o.y + 3);
            if (g == null) continue; BlockState s = level().getBlockState(g);
            if (!(s.is(Blocks.HONEYCOMB_BLOCK) || s.is(Blocks.ORANGE_TERRACOTTA) || s.is(Blocks.BROWN_TERRACOTTA))) continue;
            boolean occupied = false; for (ServerPlayer p : party()) if (p.blockPosition().equals(g.above()) || p.getOnPos().equals(g)) occupied = true;
            if (occupied) continue;
            comb.set(level(), g.above(), Blocks.HONEYCOMB_BLOCK.defaultBlockState()); raised.add(g.above());
            serverLevel().playSound(null, g, SoundEvents.HONEY_BLOCK_PLACE, net.minecraft.sounds.SoundSource.BLOCKS, 1F, 0.7F); return;
        }
    }

    @Override protected void onDefeated() { super.onDefeated(); Mech.discardMinions(this); comb.restoreAll(level()); raised.clear(); }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        comb.save(tag, "Comb");
    }
    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        comb.load(tag, "Comb", level());
    }
}
