package com.ninjacat.skies.lib.plan;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.TicketType;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Places or removes a large set of blocks a slice at a time, so a 25k-block structure never lands in one tick.
 * Chunks under the work are held by a region ticket while the queue runs; tickets are not saved, so a queue loaded
 * after a restart simply takes them again on its first step. States are palette-compressed for saving.
 *
 * <p>A removal step only clears a position that still holds the recorded block (any state of it: a lit pillar or a
 * turned chest still counts), so blocks a player placed in the meantime survive.
 */
public final class BuildQueue {
    public static final TicketType<Long> TICKET = TicketType.create("ninjacatlib_build", Long::compareTo);

    public enum Mode { PLACE, REMOVE }

    private final Mode mode;
    private final long ticketKey;
    private final List<BlockState> palette = new ArrayList<>();
    private int[] ops = new int[0];     // x, y, z, paletteIndex
    private int count, cursor;
    private final Set<Long> ticketed = new HashSet<>();

    public BuildQueue(Mode mode, long ticketKey) { this.mode = mode; this.ticketKey = ticketKey; }

    public Mode mode() { return mode; }
    public boolean done() { return cursor >= count; }
    public int size() { return count; }
    public int cursor() { return cursor; }
    /** 0..1 progress, for spectacle timing. */
    public float progress() { return count == 0 ? 1F : (float) cursor / count; }

    public void add(BlockPos pos, BlockState state) {
        int idx = palette.indexOf(state);
        if (idx < 0) { palette.add(state); idx = palette.size() - 1; }
        if ((count + 1) * 4 > ops.length) ops = java.util.Arrays.copyOf(ops, Math.max(64, ops.length * 2));
        int o = count * 4;
        ops[o] = pos.getX(); ops[o + 1] = pos.getY(); ops[o + 2] = pos.getZ(); ops[o + 3] = idx;
        count++;
    }

    public BlockPos posAt(int i) { int o = i * 4; return new BlockPos(ops[o], ops[o + 1], ops[o + 2]); }
    public BlockState stateAt(int i) { return palette.get(ops[i * 4 + 3]); }

    /**
     * Run up to {@code budget} operations. Returns the number done. Place uses flags 2|16 (no neighbour shape
     * updates, clients told); remove uses the same, then the caller may do a final lighting-safe pass if needed.
     */
    public int step(ServerLevel level, int budget) {
        int done = 0;
        BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
        while (cursor < count && done < budget) {
            int o = cursor * 4;
            m.set(ops[o], ops[o + 1], ops[o + 2]);
            hold(level, m);
            BlockState want = palette.get(ops[o + 3]);
            if (mode == Mode.PLACE) {
                level.setBlock(m, want, 2 | 16);
            } else if (level.getBlockState(m).is(want.getBlock())) {
                level.setBlock(m, Blocks.AIR.defaultBlockState(), 2 | 16);
            }
            cursor++;
            done++;
        }
        if (done()) release(level);
        return done;
    }

    private void hold(ServerLevel level, BlockPos p) {
        ChunkPos c = new ChunkPos(p);
        if (ticketed.add(c.toLong())) level.getChunkSource().addRegionTicket(TICKET, c, 1, ticketKey);
    }

    /** Drop every chunk ticket this queue took. Safe to call more than once. */
    public void release(ServerLevel level) {
        for (long l : ticketed) level.getChunkSource().removeRegionTicket(TICKET, new ChunkPos(l), 1, ticketKey);
        ticketed.clear();
    }

    // ------------------------------------------------------------------ persistence

    public CompoundTag save() {
        CompoundTag t = new CompoundTag();
        t.putString("mode", mode.name());
        t.putLong("key", ticketKey);
        t.putInt("cursor", cursor);
        ListTag pal = new ListTag();
        for (BlockState s : palette) pal.add(NbtUtils.writeBlockState(s));
        t.put("palette", pal);
        t.putIntArray("ops", java.util.Arrays.copyOf(ops, count * 4));
        return t;
    }

    public static BuildQueue load(CompoundTag t, HolderLookup.Provider regs) {
        Mode mode;
        try { mode = Mode.valueOf(t.getString("mode")); } catch (IllegalArgumentException e) { mode = Mode.PLACE; }
        BuildQueue q = new BuildQueue(mode, t.getLong("key"));
        var blocks = regs.lookupOrThrow(Registries.BLOCK);
        for (Tag s : t.getList("palette", Tag.TAG_COMPOUND)) q.palette.add(NbtUtils.readBlockState(blocks, (CompoundTag) s));
        q.ops = t.getIntArray("ops");
        q.count = q.ops.length / 4;
        q.cursor = Math.min(t.getInt("cursor"), q.count);
        return q;
    }
}
