package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.animal.Bee;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CampfireBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;

/**
 * Swarm · the Hivemind — QUEEN AND DRONES. The tower is fragile but hides its royal chamber: it is immune until
 * all six drone cells in the wall are smoked. Every wave each open cell pours drones (angry bees). A lit campfire
 * placed at a drone cell seals it for 30 s (then the smoke gutters out and the fire must be relit); sealing all
 * six exposes the chamber for 10 s. Comb cells rise and fall by a block every 5 s, reshaping cover.
 */
public class HivemindGuardian extends GuardianEntity {
    private static final int CELLS = 6, CELL_R = 34, WAVE = 400, SEAL_TICKS = 600, EXPOSE = 200;
    private final int[] sealedUntil = new int[CELLS];
    private final BlockPos[] fire = new BlockPos[CELLS];
    private final Mech.Ledger comb = new Mech.Ledger();
    private final List<BlockPos> raised = new ArrayList<>();
    private int exposed = 0; private boolean armed = true;

    public HivemindGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.HIVEMIND); }

    @Override protected boolean mobile() { return false; }
    @Override protected String immuneMessage() { return "The royal chamber is shut. Smoke all six drone cells with lit campfires."; }
    /** Drone cell k: arena_factory puts the six at 30° + 60°k on the wall (r 33); the plan mirrors y into -z. */
    private Vec3 cell(int k) { Vec3 o = origin(); return Mech.polar(o, CELL_R, -(Math.PI / 3 * k + Math.PI / 6), o.y); }
    private int droneCap() { return 6 + 3 * partySize(); }

    @Override
    protected void tickMechanic() {
        if (ageInFight == 1) shout("The Hivemind answers for the Cut. The queen is soft, but her six drone cells in the wall never stop pouring. Set a lit campfire at a cell to smoke it shut; smoke all six and the royal chamber opens.");
        Vec3 o = origin();
        if (tickCount % 10 == 0) tickSeals();
        if (arena() == null && exposed <= 0 && ageInFight % 400 == 60) { exposed = EXPOSE; shout("The royal chamber gapes open on its own — strike the queen!"); }   // no wall cells to smoke (a shade, or /summon)
        if (exposed > 0) exposed--;
        setImmune(exposed <= 0);
        if (ageInFight % WAVE == 60) wave();
        if (arena() != null && ageInFight % 100 == 50) shiftCells(o);
        if (tickCount % 8 == 0) for (int k = 0; k < CELLS; k++) { Vec3 c = cell(k); boolean s = sealedUntil[k] > tickCount; Mech.column(serverLevel(), s ? ParticleTypes.CAMPFIRE_SIGNAL_SMOKE : Mech.GOLD, c.add(0, 1, 0), 4, 4); }
    }

    @Override protected void onPhase(int phase) { shout(phase == 3 ? "The Hivemind shrieks — every cell empties at once!" : "The comb hums louder. More drones."); if (phase == 3) wave(); }

    /** A campfire (lit) within 3.5 blocks of a cell mouth seals it; after 30 s the smoke gutters and the fire goes out. */
    private void tickSeals() {
        int sealed = 0;
        for (int k = 0; k < CELLS; k++) {
            if (sealedUntil[k] > tickCount) {
                sealed++;
                if (fire[k] != null && !isLitCampfire(level().getBlockState(fire[k]))) sealedUntil[k] = 0;      // fire removed → cell open again
                continue;
            }
            if (fire[k] != null) { BlockState s = level().getBlockState(fire[k]); if (isLitCampfire(s)) level().setBlock(fire[k], s.setValue(CampfireBlock.LIT, false), 3); fire[k] = null; Mech.burst(serverLevel(), ParticleTypes.LARGE_SMOKE, cell(k).add(0, 1, 0), 10, 1); }
            BlockPos f = findCampfire(cell(k));
            if (f != null) { fire[k] = f; sealedUntil[k] = tickCount + SEAL_TICKS; sealed++; say("A drone cell is smoked shut (" + sealed + "/" + CELLS + ")."); Mech.soundAt(serverLevel(), cell(k), SoundEvents.FIRE_EXTINGUISH, 1.5F, 0.6F); }
        }
        if (sealed == CELLS) { if (armed) { armed = false; exposed = EXPOSE; shout("All six cells are smoked — the royal chamber opens! Strike the queen!"); sound(SoundEvents.BEEHIVE_SHEAR, 2F, 0.5F); Mech.burst(serverLevel(), ParticleTypes.FALLING_HONEY, position().add(0, kind.height * 0.4, 0), 40, 3); } }
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
            Vec3 c = cell(k);
            for (int i = 0; i < per && alive < droneCap(); i++, alive++) {
                Bee b = Mech.spawn(this, EntityType.BEE, c.add(random.nextDouble() * 2 - 1, 2 + random.nextDouble(), random.nextDouble() * 2 - 1), "Drone", 12, 3);
                if (b == null) continue;
                ServerPlayer t = Mech.randomPlayer(this);
                if (t != null) { b.setPersistentAngerTarget(t.getUUID()); b.setRemainingPersistentAngerTime(2400); b.setTarget(t); }
            }
            Mech.burst(serverLevel(), ParticleTypes.FALLING_HONEY, c.add(0, 2, 0), 8, 1);
        }
        sound(SoundEvents.BEE_LOOP_AGGRESSIVE, 2F, 0.6F); say("The cells pour drones!");
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
}
