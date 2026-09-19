package com.ninjacat.skies.driftwrecks.wreck;

import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.driftwrecks.block.TetherThreadBlock;
import com.ninjacat.skies.driftwrecks.registry.DwBlocks;
import com.ninjacat.skies.driftwrecks.registry.DwRegistries;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Half;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/**
 * Tether Spool bridges and the thread catch. A bridge is rasterised from the player's feet to the nearest dock on
 * the wreck in half-block steps (so it climbs without jumps), laid a few blocks per tick, and registered to the
 * wreck so it unravels with it. Existing blocks are skipped, never replaced.
 */
public final class Tether {
    public static final int MAX_LENGTH = 400, PER_TICK = 4, AIM_DEGREES = 30, CATCH_RADIUS = 24;
    private static final List<Lay> LAYING = new ArrayList<>();

    private record Lay(int wreck, Deque<BlockPos> todo, Deque<BlockState> states) {}

    private Tether() {}

    public static boolean lay(ServerPlayer p) {
        MinecraftServer server = p.server;
        ServerLevel level = DriftManager.level(server);
        if (p.level() != level) { p.displayClientMessage(NinjacatText.teal("Wrecks drift in the Skies. The spool finds nothing to catch here."), true); return false; }
        DriftManager m = DriftManager.get(server);
        Wreck w = LoomTension.clowderOf(p).map(c -> m.byTeam(c.id())).orElse(null);
        if (w == null || w.phase != Wreck.Phase.ACTIVE) { p.displayClientMessage(NinjacatText.teal("No wreck is caught on your weft."), true); return false; }
        BlockPos dock = nearestDock(server, w, p.position());
        Vec3 target = Vec3.atBottomCenterOf(dock).add(0, 1, 0);   // surface of the deck block
        Vec3 look = p.getLookAngle();
        Vec3 dir = target.subtract(p.position());
        double lookAng = Math.toDegrees(Math.atan2(look.z, look.x)), dirAng = Math.toDegrees(Math.atan2(dir.z, dir.x));
        double diff = Math.abs(((lookAng - dirAng) % 360 + 540) % 360 - 180);
        if (diff > AIM_DEGREES) { p.displayClientMessage(NinjacatText.teal("Face the wreck, then throw the thread."), true); return false; }
        double horiz = Math.hypot(dir.x, dir.z);
        if (horiz > MAX_LENGTH) { p.displayClientMessage(NinjacatText.teal("Too far. A spool holds " + MAX_LENGTH + " blocks of thread."), true); return false; }
        if (!p.onGround()) { p.displayClientMessage(NinjacatText.teal("Plant your feet first."), true); return false; }
        if (w.contains(p.blockPosition(), 16)) { p.displayClientMessage(NinjacatText.teal("Throw the thread from your own ground, not from the wreck."), true); return false; }

        List<BlockPos> path = new ArrayList<>();
        List<BlockState> states = new ArrayList<>();
        raster(p.position(), target, path, states);
        Deque<BlockPos> todo = new ArrayDeque<>();
        Deque<BlockState> st = new ArrayDeque<>();
        for (int i = 0; i < path.size(); i++) {
            BlockPos b = path.get(i);
            if (w.contains(b, 0) && !level.getBlockState(b).isAir()) continue;
            if (!level.getBlockState(b).isAir()) continue;
            todo.add(b); st.add(states.get(i));
        }
        if (todo.isEmpty()) { p.displayClientMessage(NinjacatText.teal("The way is already bridged."), true); return false; }
        LAYING.add(new Lay(w.id, todo, st));
        w.tetherStart = p.blockPosition();
        m.markDirty();
        WreckRewards.award(p, "cross");
        p.displayClientMessage(NinjacatText.gold("The thread runs out ahead of you."), true);
        return true;
    }

    /** Surface heights rounded to half blocks: an integer surface is a top half below it, x.5 a bottom half. */
    static void raster(Vec3 from, Vec3 to, List<BlockPos> path, List<BlockState> states) {
        double dx = to.x - from.x, dz = to.z - from.z, dist = Math.hypot(dx, dz);
        int n = (int) Math.ceil(dist * 2);
        BlockState bottom = DwBlocks.TETHER_THREAD.get().defaultBlockState();
        BlockState top = bottom.setValue(TetherThreadBlock.HALF, Half.TOP);
        BlockPos last = null;
        for (int i = 1; i <= n; i++) {
            double t = (double) i / n;
            double x = from.x + dx * t, z = from.z + dz * t;
            double s = Math.round((from.y + (to.y - from.y) * t) * 2) / 2.0;
            boolean whole = Math.abs(s - Math.floor(s)) < 1e-6;
            int y = whole ? (int) s - 1 : (int) Math.floor(s);
            BlockPos b = BlockPos.containing(x, y, z);
            if (b.equals(last)) continue;
            if (last != null && last.getX() != b.getX() && last.getZ() != b.getZ()) {
                // no diagonal gaps: fill the corner so the walk is continuous
                BlockPos corner = new BlockPos(b.getX(), b.getY(), last.getZ());
                path.add(corner); states.add(whole ? top : bottom);
            }
            path.add(b); states.add(whole ? top : bottom);
            last = b;
        }
    }

    @Nullable
    static BlockPos nearestDock(MinecraftServer server, Wreck w, Vec3 from) {
        WreckPlan plan = WreckPlan.get(server, w.planId);
        BlockPos best = null;
        double bd = Double.MAX_VALUE;
        for (WreckPlan.Marker mk : plan.markers("dock")) {
            BlockPos p = w.origin.offset(mk.pos());
            double d = p.distToCenterSqr(from);
            if (d < bd) { bd = d; best = p; }
        }
        return best == null ? w.origin : best;
    }

    /** Called every server tick: lay queued bridge blocks, a few at a time, with a tick sound. */
    public static void tick(MinecraftServer server) {
        if (LAYING.isEmpty()) return;
        ServerLevel level = DriftManager.level(server);
        DriftManager m = DriftManager.get(server);
        LAYING.removeIf(lay -> {
            Wreck w = m.byId(lay.wreck);
            if (w == null || w.phase != Wreck.Phase.ACTIVE) return true;
            for (int i = 0; i < PER_TICK && !lay.todo.isEmpty(); i++) {
                BlockPos b = lay.todo.poll();
                BlockState s = lay.states.poll();
                if (!level.getBlockState(b).isAir()) continue;
                level.setBlock(b, s, 3);
                w.tether.add(b);
                if (i == 0) level.playSound(null, b, DwRegistries.sound("tether.lay"), SoundSource.BLOCKS, 0.5F, 0.9F + level.random.nextFloat() * 0.2F);
            }
            m.markDirty();
            return lay.todo.isEmpty();
        });
    }

    /**
     * The thread catch: a Clowder member falling into the void near their wreck or its tether is pulled back onto
     * the nearest tether block (or the wreck's dock) with 3 hearts of damage. The void is the scenery, not the
     * punishment. Fires long before Forgiving Void would.
     */
    public static void checkCatch(ServerPlayer p) {
        if (p.isSpectator() || p.getAbilities().flying || p.isCreative() || p.fallDistance < 12) return;
        ServerLevel level = DriftManager.level(p.server);
        if (p.level() != level) return;
        DriftManager m = DriftManager.get(p.server);
        Wreck w = LoomTension.clowderOf(p).map(c -> m.byTeam(c.id())).orElse(null);
        if (w == null || w.phase != Wreck.Phase.ACTIVE) return;
        int floor = w.minY;
        for (BlockPos t : w.tether) floor = Math.min(floor, t.getY());
        if (p.getY() > floor - 16) return;
        if (w.reach(p.getX(), p.getZ()) > CATCH_RADIUS) return;
        BlockPos to = null;
        double bd = Double.MAX_VALUE;
        for (BlockPos t : w.tether) {
            if (!level.getBlockState(t).is(DwBlocks.TETHER_THREAD.get())) continue;
            double d = Math.hypot(t.getX() + 0.5 - p.getX(), t.getZ() + 0.5 - p.getZ());
            if (d < bd) { bd = d; to = t; }
        }
        double y;
        if (to == null) {
            to = nearestDock(p.server, w, p.position());
            y = to.getY() + 1;
        } else {
            y = to.getY() + (level.getBlockState(to).getValue(TetherThreadBlock.HALF) == Half.TOP ? 1.0 : 0.5);
        }
        if (p.isPassenger()) p.stopRiding();
        if (p instanceof net.neoforged.neoforge.common.util.FakePlayer) p.moveTo(to.getX() + 0.5, y, to.getZ() + 0.5, p.getYRot(), p.getXRot());
        else p.teleportTo(level, to.getX() + 0.5, y, to.getZ() + 0.5, p.getYRot(), p.getXRot());
        p.setDeltaMovement(Vec3.ZERO);
        p.fallDistance = 0;
        p.hurt(p.damageSources().fellOutOfWorld(), Math.min(6F, Math.max(0, p.getHealth() - 1)));
        level.playSound(null, to, DwRegistries.sound("tether.catch"), SoundSource.PLAYERS, 1.0F, 1.0F);
        p.displayClientMessage(NinjacatText.teal("The thread catches you. It will not always be there."), true);
    }

    /** Server stopping: lay whatever is still queued at once, so a restart never leaves half a bridge. */
    public static void flush(MinecraftServer server) {
        ServerLevel level = DriftManager.level(server);
        DriftManager m = DriftManager.get(server);
        for (Lay lay : LAYING) {
            Wreck w = m.byId(lay.wreck);
            if (w == null) continue;
            while (!lay.todo.isEmpty()) {
                BlockPos b = lay.todo.poll();
                BlockState s = lay.states.poll();
                if (level.getBlockState(b).isAir()) { level.setBlock(b, s, 3); w.tether.add(b); }
            }
        }
        LAYING.clear();
        m.markDirty();
    }

    public static void clear() { LAYING.clear(); }
}
