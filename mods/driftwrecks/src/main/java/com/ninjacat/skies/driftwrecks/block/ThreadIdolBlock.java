package com.ninjacat.skies.driftwrecks.block;

import com.mojang.serialization.MapCodec;
import com.ninjacat.skies.driftwrecks.wreck.DriftManager;
import com.ninjacat.skies.driftwrecks.wreck.Wreck;
import com.ninjacat.skies.driftwrecks.wreck.WreckObjectives;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** The thread-wound idol: touch it and the pillars flare in the order to re-thread them. Watch, then act. */
public class ThreadIdolBlock extends Block {
    public static final MapCodec<ThreadIdolBlock> CODEC = simpleCodec(ThreadIdolBlock::new);
    private static final VoxelShape SHAPE = Block.box(4, 0, 4, 12, 15, 12);

    public ThreadIdolBlock(Properties props) { super(props); }

    @Override protected MapCodec<? extends Block> codec() { return CODEC; }
    @Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return SHAPE; }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (level.isClientSide) return InteractionResult.SUCCESS;
        if (level instanceof ServerLevel sl && player instanceof ServerPlayer sp) {
            Wreck w = DriftManager.get(sl.getServer()).at(pos, 0);
            if (w != null && w.phase == Wreck.Phase.ACTIVE) WreckObjectives.showOrder(sl, w, sp);
        }
        return InteractionResult.CONSUME;
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource rng) {
        if (rng.nextInt(4) == 0) level.addParticle(ParticleTypes.GLOW, pos.getX() + 0.5 + (rng.nextDouble() - 0.5) * 0.6, pos.getY() + 1.0, pos.getZ() + 0.5 + (rng.nextDouble() - 0.5) * 0.6, 0, 0.02, 0);
    }
}
