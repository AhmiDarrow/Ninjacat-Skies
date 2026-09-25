package com.ninjacat.skies.driftwrecks.block;

import com.mojang.serialization.MapCodec;
import com.ninjacat.skies.driftwrecks.registry.DwItems;
import com.ninjacat.skies.driftwrecks.rift.RiftManager;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.joml.Vector3f;

/** The sealed rift on a Tier 3 wreck's lowest floor. A Weft Key of the wreck's Strand opens it. */
public class RiftTearBlock extends Block {
    public static final MapCodec<RiftTearBlock> CODEC = simpleCodec(RiftTearBlock::new);
    private static final VoxelShape SHAPE = Block.box(2, 0, 2, 14, 16, 14);

    public RiftTearBlock(Properties props) { super(props); }

    @Override protected MapCodec<? extends Block> codec() { return CODEC; }
    @Override protected VoxelShape getShape(BlockState s, BlockGetter l, BlockPos p, CollisionContext c) { return SHAPE; }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (!stack.is(DwItems.WEFT_KEY.get())) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        if (level.isClientSide) return ItemInteractionResult.SUCCESS;
        if (level instanceof ServerLevel sl && player instanceof ServerPlayer sp) RiftManager.open(sl, pos, sp, stack);
        return ItemInteractionResult.CONSUME;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!level.isClientSide) player.displayClientMessage(NinjacatText.tealKey("message.driftwrecks.rift.tear_sealed"), true);
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource rng) {
        for (int i = 0; i < 3; i++) {
            level.addParticle(new DustParticleOptions(new Vector3f(0.24F, 0.85F, 0.8F), 1.2F),
                    pos.getX() + 0.3 + rng.nextDouble() * 0.4, pos.getY() + rng.nextDouble() * 1.8, pos.getZ() + 0.3 + rng.nextDouble() * 0.4, 0, 0.02, 0);
        }
        if (rng.nextInt(3) == 0) level.addParticle(ParticleTypes.REVERSE_PORTAL, pos.getX() + 0.5, pos.getY() + 1.0, pos.getZ() + 0.5, 0, 0.05, 0);
    }
}
