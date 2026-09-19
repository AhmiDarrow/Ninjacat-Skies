package com.ninjacat.skies.driftwrecks.block;

import com.mojang.serialization.MapCodec;
import com.ninjacat.skies.driftwrecks.registry.DwBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.PressurePlateBlock;
import net.minecraft.world.level.block.state.BlockState;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashSet;
import java.util.Set;

/**
 * The Vault's thread lock: a woven curtain across the door. It unravels when every pressure plate in front of the
 * door is held down at once (two players, or a player and a dropped stack on the wooden plate).
 */
public class ThreadLockBlock extends Block {
    public static final MapCodec<ThreadLockBlock> CODEC = simpleCodec(ThreadLockBlock::new);
    private static final int CHECK = 10, REACH = 3;

    public ThreadLockBlock(Properties props) { super(props); }

    @Override protected MapCodec<? extends Block> codec() { return CODEC; }

    @Override
    protected void onPlace(BlockState state, Level level, BlockPos pos, BlockState old, boolean moving) {
        if (!level.isClientSide) level.scheduleTick(pos, this, CHECK);
    }

    @Override
    protected void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource rng) {
        int plates = 0, pressed = 0;
        for (BlockPos p : BlockPos.betweenClosed(pos.offset(-REACH, -REACH, -REACH), pos.offset(REACH, REACH, REACH))) {
            BlockState s = level.getBlockState(p);
            if (s.getBlock() instanceof PressurePlateBlock) {
                plates++;
                if (s.getValue(PressurePlateBlock.POWERED)) pressed++;
            }
        }
        if (plates >= 2 && pressed == plates) {
            unravel(level, pos);
            return;
        }
        level.scheduleTick(pos, this, CHECK);
    }

    private static void unravel(ServerLevel level, BlockPos start) {
        Deque<BlockPos> todo = new ArrayDeque<>();
        Set<BlockPos> seen = new HashSet<>();
        todo.add(start);
        int removed = 0;                                   // the cap counts lock blocks, not the air around them
        while (!todo.isEmpty() && removed < 256) {
            BlockPos p = todo.poll();
            if (!seen.add(p) || !level.getBlockState(p).is(DwBlocks.THREAD_LOCK.get())) continue;
            level.removeBlock(p, false); removed++;
            level.sendParticles(ParticleTypes.GLOW, p.getX() + 0.5, p.getY() + 0.5, p.getZ() + 0.5, 6, 0.3, 0.3, 0.3, 0.02);
            for (var d : net.minecraft.core.Direction.values()) todo.add(p.relative(d));
        }
        level.playSound(null, start, SoundEvents.WOOL_BREAK, SoundSource.BLOCKS, 1.5F, 0.6F);
        level.playSound(null, start, SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.BLOCKS, 1.0F, 1.2F);
    }
}
