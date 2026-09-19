package com.ninjacat.skies.driftwrecks.block;

import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.Half;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * One step of a tether bridge: a half-height weave of thread, bottom or top half, so a rising bridge climbs in
 * half-block steps a player walks without jumping. Glows faintly; mobs never spawn on it. Unravels with its wreck.
 */
public class TetherThreadBlock extends Block {
    public static final MapCodec<TetherThreadBlock> CODEC = simpleCodec(TetherThreadBlock::new);
    public static final EnumProperty<Half> HALF = BlockStateProperties.HALF;
    private static final VoxelShape BOTTOM = Block.box(0, 0, 0, 16, 8, 16), TOP = Block.box(0, 8, 0, 16, 16, 16);

    public TetherThreadBlock(BlockBehaviour.Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(HALF, Half.BOTTOM));
    }

    @Override protected MapCodec<? extends Block> codec() { return CODEC; }
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> b) { b.add(HALF); }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return state.getValue(HALF) == Half.TOP ? TOP : BOTTOM;
    }

    @Override
    protected boolean useShapeForLightOcclusion(BlockState state) { return true; }
}
