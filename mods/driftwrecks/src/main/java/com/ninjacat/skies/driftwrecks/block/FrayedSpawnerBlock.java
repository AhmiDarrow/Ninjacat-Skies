package com.ninjacat.skies.driftwrecks.block;

import com.mojang.serialization.MapCodec;
import com.ninjacat.skies.driftwrecks.registry.DwRegistries;
import com.ninjacat.skies.driftwrecks.wreck.DriftManager;
import com.ninjacat.skies.driftwrecks.wreck.Wreck;
import com.ninjacat.skies.driftwrecks.wreck.WreckObjectives;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;

import javax.annotation.Nullable;

/** A tear that keeps coughing up the old world's strays. Breaking it pays Weft and a Frayed Core (loot table). */
public class FrayedSpawnerBlock extends BaseEntityBlock {
    public static final MapCodec<FrayedSpawnerBlock> CODEC = simpleCodec(FrayedSpawnerBlock::new);

    public FrayedSpawnerBlock(Properties props) { super(props); }

    @Override protected MapCodec<? extends BaseEntityBlock> codec() { return CODEC; }
    @Override protected RenderShape getRenderShape(BlockState state) { return RenderShape.MODEL; }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new FrayedSpawnerBlockEntity(pos, state); }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        return level.isClientSide ? null : createTickerHelper(type, DwRegistries.FRAYED_SPAWNER.get(), FrayedSpawnerBlockEntity::serverTick);
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState now, boolean moving) {
        if (!level.isClientSide && !now.is(state.getBlock()) && level instanceof ServerLevel sl) {
            DriftManager m = DriftManager.get(sl.getServer());
            Wreck w = m.at(pos, 0);
            if (w != null && w.phase == Wreck.Phase.ACTIVE) WreckObjectives.spawnerBroken(m, sl, w);
        }
        super.onRemove(state, level, pos, now, moving);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource rng) {
        if (rng.nextInt(3) == 0) level.addParticle(ParticleTypes.ASH, pos.getX() + rng.nextDouble(), pos.getY() + 1.0, pos.getZ() + rng.nextDouble(), 0, 0.02, 0);
        if (rng.nextInt(5) == 0) level.addParticle(ParticleTypes.GLOW, pos.getX() + rng.nextDouble(), pos.getY() + rng.nextDouble(), pos.getZ() + rng.nextDouble(), 0, 0.01, 0);
    }
}
