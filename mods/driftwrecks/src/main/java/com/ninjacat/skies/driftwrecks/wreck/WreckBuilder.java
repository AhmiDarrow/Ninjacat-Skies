package com.ninjacat.skies.driftwrecks.wreck;

import com.ninjacat.skies.driftwrecks.block.ThreadPillarBlock;
import com.ninjacat.skies.driftwrecks.registry.DwBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.LanternBlock;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.SnowLayerBlock;
import net.minecraft.world.level.block.VineBlock;
import net.minecraft.world.level.block.state.BlockState;

import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Turns a role-keyed plan into real blocks for one wreck: Strand skin, hidden room open or sealed, the modifier's
 * dressing, then the furniture its objective needs at the plan's markers. Output is relative to the origin, in
 * build order (keel first).
 */
public final class WreckBuilder {
    private WreckBuilder() {}

    public static Map<BlockPos, BlockState> build(WreckComposer.Layout layout, Wreck w, RandomSource rng) {
        Map<BlockPos, BlockState> out = new LinkedHashMap<>();
        Map<BlockPos, String> roles = new LinkedHashMap<>();
        // bottom up, so the arrival builds from the keel
        List<Map.Entry<BlockPos, String>> sorted = new java.util.ArrayList<>(layout.blocks.entrySet());
        sorted.sort(java.util.Comparator.comparingInt((Map.Entry<BlockPos, String> e) -> e.getKey().getY()));
        for (Map.Entry<BlockPos, String> e : sorted) {
            String key = e.getValue();
            BlockPos p = e.getKey();
            if (key.equals("x_air")) continue;
            if (key.startsWith("h_")) {
                if (w.hiddenRoom) {
                    String inner = key.substring(2);
                    if (inner.equals("air") || inner.equals("x_air")) continue;
                    key = inner;
                } else {
                    key = layout.fill;
                }
            }
            out.put(p, StrandSkin.resolve(w.skin, key));
            roles.put(p, key);
        }
        Set<BlockPos> reserved = new HashSet<>();
        for (WreckPlan.Marker m : layout.markers) reserved.add(m.pos());
        dress(out, roles, reserved, w, rng);
        furnish(out, layout.markers, w, rng);
        return out;
    }

    // ------------------------------------------------------------------ modifiers
    private static void dress(Map<BlockPos, BlockState> out, Map<BlockPos, String> roles, Set<BlockPos> reserved, Wreck w, RandomSource rng) {
        if (w.modifier == WreckModifier.UNMARKED || w.modifier == WreckModifier.UNSTABLE) return;
        Map<BlockPos, BlockState> add = new LinkedHashMap<>();
        for (Map.Entry<BlockPos, BlockState> e : out.entrySet()) {
            BlockPos p = e.getKey();
            BlockState st = e.getValue();
            String role = roles.getOrDefault(p, "");
            BlockPos up = p.above();
            boolean top = !out.containsKey(up) && !reserved.contains(up) && st.isSolid();
            boolean deck = role.equals("floor") || role.equals("soil") || role.equals("keel") || role.equals("accent");
            switch (w.modifier) {
                case OVERGROWN -> {
                    if (top && rng.nextFloat() < 0.35F) add.put(up, Blocks.MOSS_CARPET.defaultBlockState());
                    else if (top && deck && rng.nextFloat() < 0.06F) add.put(up, rng.nextBoolean() ? Blocks.AZALEA.defaultBlockState() : Blocks.FLOWERING_AZALEA.defaultBlockState());
                    if (role.equals("roof") && rng.nextFloat() < 0.25F) e.setValue(Blocks.AZALEA_LEAVES.defaultBlockState().setValue(LeavesBlock.PERSISTENT, true));
                    if (st.isSolid() && p.getY() >= 1 && rng.nextFloat() < 0.10F) vine(out, add, p, rng);
                }
                case FROZEN -> {
                    if (st.is(Blocks.WATER)) e.setValue(Blocks.PACKED_ICE.defaultBlockState());
                    else if (top && deck && p.getY() == 0 && rng.nextFloat() < 0.03F) e.setValue(Blocks.POWDER_SNOW.defaultBlockState());
                    else if (top && rng.nextFloat() < 0.45F) add.put(up, Blocks.SNOW.defaultBlockState().setValue(SnowLayerBlock.LAYERS, 1 + rng.nextInt(2)));
                    if (role.equals("growth")) e.setValue(Blocks.SNOW_BLOCK.defaultBlockState());
                }
                case HAUNTED -> {
                    if (st.getBlock() instanceof LanternBlock) {
                        e.setValue(rng.nextFloat() < 0.5F ? Blocks.AIR.defaultBlockState()
                                : Blocks.SOUL_LANTERN.defaultBlockState().setValue(LanternBlock.HANGING, st.getValue(LanternBlock.HANGING)));
                    }
                    if (top && p.getY() >= 0 && rng.nextFloat() < 0.04F) add.put(up, Blocks.COBWEB.defaultBlockState());
                    if (top && deck && rng.nextFloat() < 0.03F) add.put(up, Blocks.SOUL_TORCH.defaultBlockState());
                }
                case BURNING -> {
                    if (top && deck && rng.nextFloat() < 0.06F) e.setValue(Blocks.MAGMA_BLOCK.defaultBlockState());
                    else if (top && deck && rng.nextFloat() < 0.015F) { e.setValue(Blocks.NETHERRACK.defaultBlockState()); add.put(up, Blocks.FIRE.defaultBlockState()); }
                    if (st.is(Blocks.WATER)) e.setValue(Blocks.AIR.defaultBlockState());
                }
                default -> {}
            }
        }
        for (Map.Entry<BlockPos, BlockState> a : add.entrySet()) out.putIfAbsent(a.getKey(), a.getValue());
        out.values().removeIf(BlockState::isAir);
    }

    private static void vine(Map<BlockPos, BlockState> out, Map<BlockPos, BlockState> add, BlockPos wall, RandomSource rng) {
        Direction d = Direction.Plane.HORIZONTAL.getRandomDirection(rng);
        BlockPos at = wall.relative(d);
        if (out.containsKey(at)) return;
        BlockState vine = Blocks.VINE.defaultBlockState().setValue(VineBlock.getPropertyForFace(d.getOpposite()), true);
        int len = 1 + rng.nextInt(3);
        for (int i = 0; i < len; i++) {
            BlockPos v = at.below(i);
            if (out.containsKey(v) || !out.containsKey(wall.below(i))) break;
            add.putIfAbsent(v, vine);
        }
    }

    // ------------------------------------------------------------------ furniture
    private static void furnish(Map<BlockPos, BlockState> out, List<WreckPlan.Marker> markers, Wreck w, RandomSource rng) {
        boolean spawners = w.objective == WreckObjective.CLEAR || w.tier != WreckTier.RAFT;
        for (WreckPlan.Marker m : markers) {
            BlockPos p = m.pos();
            switch (m.kind()) {
                case "chest" -> {
                    if (m.data() == 2 && !w.hiddenRoom) break;
                    Direction face = Direction.getNearest(-p.getX(), 0, -p.getZ());
                    if (face.getAxis() == Direction.Axis.Y) face = Direction.SOUTH;
                    out.put(p, DwBlocks.WRECK_CHEST.get().defaultBlockState().setValue(HorizontalDirectionalBlock.FACING, face));
                }
                case "spawner" -> { if (spawners) out.put(p, DwBlocks.FRAYED_SPAWNER.get().defaultBlockState()); }
                case "pillar" -> {
                    if (w.objective == WreckObjective.RETHREAD)
                        out.put(p, DwBlocks.THREAD_PILLAR.get().defaultBlockState().setValue(ThreadPillarBlock.INDEX, Math.min(m.data(), 4)));
                }
                case "idol" -> { if (w.objective == WreckObjective.RETHREAD || w.heartwreck) out.put(p, DwBlocks.THREAD_IDOL.get().defaultBlockState()); }
                case "district" -> out.put(p, DwBlocks.THREAD_PILLAR.get().defaultBlockState().setValue(ThreadPillarBlock.INDEX, Math.min(m.data() % 5, 4)));
                case "rift" -> { if (w.tier == WreckTier.HOLD) out.put(p, DwBlocks.RIFT_TEAR.get().defaultBlockState()); }
                case "lock" -> out.put(p, DwBlocks.THREAD_LOCK.get().defaultBlockState());
                default -> {}
            }
        }
    }

    /** Chest facing helper for tests. */
    static boolean isChest(BlockState s) { return s.getBlock() instanceof ChestBlock || s.is(DwBlocks.WRECK_CHEST.get()); }
}
