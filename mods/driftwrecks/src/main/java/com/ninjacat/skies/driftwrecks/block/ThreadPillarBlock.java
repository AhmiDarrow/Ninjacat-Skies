package com.ninjacat.skies.driftwrecks.block;

import com.mojang.serialization.MapCodec;
import com.ninjacat.skies.driftwrecks.wreck.DriftManager;
import com.ninjacat.skies.driftwrecks.wreck.Wreck;
import com.ninjacat.skies.driftwrecks.wreck.WreckObjectives;
import com.ninjacat.skies.driftwrecks.wreck.WreckPlan;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/** Re-thread: light the pillars in the order the idol shows. INDEX only tints the thread; order lives on the wreck. */
public class ThreadPillarBlock extends Block {
    public static final MapCodec<ThreadPillarBlock> CODEC = simpleCodec(ThreadPillarBlock::new);
    public static final BooleanProperty LIT = BooleanProperty.create("lit");
    public static final IntegerProperty INDEX = IntegerProperty.create("index", 0, 4);
    private static final VoxelShape SHAPE = Block.box(3, 0, 3, 13, 16, 13);

    public ThreadPillarBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(LIT, false).setValue(INDEX, 0));
    }

    @Override protected MapCodec<? extends Block> codec() { return CODEC; }
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(LIT, INDEX); }
    @Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return SHAPE; }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (level.isClientSide) return InteractionResult.SUCCESS;
        if (!(level instanceof ServerLevel sl) || !(player instanceof ServerPlayer sp) || state.getValue(LIT)) return InteractionResult.CONSUME;
        DriftManager m = DriftManager.get(sl.getServer());
        Wreck w = m.at(pos, 0);
        if (w == null || w.phase != Wreck.Phase.ACTIVE) return InteractionResult.CONSUME;
        int index = markerIndex(sl, w, pos);
        if (index >= 0) WreckObjectives.touchPillar(m, sl, w, index, pos, sp);
        return InteractionResult.CONSUME;
    }

    /** The plan marker index at this position (pillar data, or the Heartwreck district's Strand ordinal). */
    public static int markerIndex(ServerLevel level, Wreck w, BlockPos pos) {
        BlockPos rel = pos.subtract(w.origin);
        for (WreckPlan.Marker mk : w.markers(w.heartwreck ? "district" : "pillar")) if (mk.pos().equals(rel)) return mk.data();
        return -1;
    }
}
