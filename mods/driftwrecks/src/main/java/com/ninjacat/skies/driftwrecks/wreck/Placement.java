package com.ninjacat.skies.driftwrecks.wreck;

import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.driftwrecks.DriftConfig;
import net.minecraft.core.BlockPos;
import net.minecraft.core.GlobalPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraft.world.phys.AABB;

import javax.annotation.Nullable;
import java.util.Collection;
import java.util.List;
import java.util.UUID;

/**
 * Where a wreck lands: 160-320 blocks from the Clowder's Tension Post, post Y +-20, random bearing. A spot is
 * rejected if the wreck (plus a 32-block margin) would touch any block, the Dock, another Clowder's pad, another
 * wreck, or the world border. Void chunks are empty sections, so the check is cheap and only real builds and
 * neighbouring islands ever stop it.
 */
public final class Placement {
    public static final int MARGIN = 32, TRIES = 16, DOCK_RADIUS = 256;

    private Placement() {}

    @Nullable
    public static BlockPos find(ServerLevel level, BlockPos post, WreckComposer.Layout plan, RandomSource rng, UUID self, Collection<Wreck> others, List<Clowder> clowders) {
        int min = DriftConfig.MIN_DISTANCE.get(), max = Math.max(min, DriftConfig.MAX_DISTANCE.get());
        for (int attempt = 0; attempt < TRIES; attempt++) {
            double ang = rng.nextDouble() * Math.PI * 2;
            int dist = min + rng.nextInt(max - min + 1);
            int dy = rng.nextInt(41) - 20;
            BlockPos origin = new BlockPos(post.getX() + Mth.floor(Math.cos(ang) * dist), post.getY() + dy, post.getZ() + Mth.floor(Math.sin(ang) * dist));
            if (fits(level, origin, plan, self, others, clowders)) return origin;
        }
        return null;
    }

    public static boolean fits(ServerLevel level, BlockPos origin, WreckComposer.Layout plan, UUID self, Collection<Wreck> others, List<Clowder> clowders) {
        AABB box = new AABB(origin.getX() + plan.minX, origin.getY() + plan.minY, origin.getZ() + plan.minZ,
                origin.getX() + plan.maxX + 1, origin.getY() + plan.maxY + 1, origin.getZ() + plan.maxZ + 1);
        AABB wide = box.inflate(MARGIN);
        if (wide.minY < level.getMinBuildHeight() + 4 || wide.maxY > level.getMaxBuildHeight() - 4) {
            // keep the keel above the void floor and the roof under the build limit; the margin may clip
            if (box.minY < level.getMinBuildHeight() + 4 || box.maxY > level.getMaxBuildHeight() - 4) return false;
        }
        var border = level.getWorldBorder();
        if (!border.isWithinBounds(wide.minX, wide.minZ) || !border.isWithinBounds(wide.maxX, wide.maxZ)) return false;
        BlockPos dock = level.getSharedSpawnPos();
        if (horizontalDistance(wide, dock) < DOCK_RADIUS) return false;
        int neighbour = DriftConfig.NEIGHBOUR_DISTANCE.get();
        for (Clowder c : clowders) {
            if (c.id().equals(self)) continue;
            GlobalPos p = LoomTension.postOf(c);
            if (p != null && p.dimension().equals(level.dimension()) && horizontalDistance(box, p.pos()) < neighbour) return false;
        }
        for (Wreck w : others) if (w.box().inflate(MARGIN).intersects(wide)) return false;
        return empty(level, wide);
    }

    private static double horizontalDistance(AABB box, BlockPos p) {
        double dx = Math.max(0, Math.max(box.minX - p.getX(), p.getX() - box.maxX));
        double dz = Math.max(0, Math.max(box.minZ - p.getZ(), p.getZ() - box.maxZ));
        return Math.sqrt(dx * dx + dz * dz);
    }

    /** True when every block in the box is air. Whole empty sections are skipped without looking inside. */
    static boolean empty(ServerLevel level, AABB box) {
        int x0 = Mth.floor(box.minX), x1 = Mth.floor(box.maxX), z0 = Mth.floor(box.minZ), z1 = Mth.floor(box.maxZ);
        int y0 = Math.max(level.getMinBuildHeight(), Mth.floor(box.minY)), y1 = Math.min(level.getMaxBuildHeight() - 1, Mth.floor(box.maxY));
        BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
        for (int cx = x0 >> 4; cx <= x1 >> 4; cx++) {
            for (int cz = z0 >> 4; cz <= z1 >> 4; cz++) {
                LevelChunk chunk = level.getChunk(cx, cz);
                for (int sy = level.getSectionIndex(y0); sy <= level.getSectionIndex(y1); sy++) {
                    LevelChunkSection section = chunk.getSection(sy);
                    if (section.hasOnlyAir()) continue;
                    int baseY = level.getSectionYFromSectionIndex(sy) << 4;
                    for (int x = Math.max(x0, cx << 4); x <= Math.min(x1, (cx << 4) + 15); x++)
                        for (int z = Math.max(z0, cz << 4); z <= Math.min(z1, (cz << 4) + 15); z++)
                            for (int y = Math.max(y0, baseY); y <= Math.min(y1, baseY + 15); y++)
                                if (!chunk.getBlockState(m.set(x, y, z)).isAir()) return false;
                }
            }
        }
        return true;
    }
}
