package com.ninjacat.skies.voidloom.block;

import com.mojang.serialization.MapCodec;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

import javax.annotation.Nullable;

/**
 * Loomframe: stretch a mesh, load grit, and let it work. Hoppers feed the top and pull from the sides.
 * Hand: siftables load in, empty hand takes scraps (then grit, then the mesh when sneaking).
 */
public class LoomframeBlock extends BaseEntityBlock {
    public static final MapCodec<LoomframeBlock> CODEC = simpleCodec(LoomframeBlock::new);

    public LoomframeBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() {
        return CODEC;
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new LoomframeBlockEntity(pos, state);
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        return level.isClientSide ? null : createTickerHelper(type, ModBlockEntities.LOOMFRAME.get(), LoomframeBlockEntity::serverTick);
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof LoomframeBlockEntity be)) {
            return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        }

        if (LoomframeBlockEntity.isMeshItem(stack)) {
            if (level.isClientSide) {
                return ItemInteractionResult.SUCCESS;
            }
            if (be.hasMesh()) {
                player.displayClientMessage(Component.translatable("message.voidloom.loomframe.has_mesh"), true);
                return ItemInteractionResult.CONSUME;
            }
            if (be.tryInsertMesh(stack)) {
                if (!player.getAbilities().instabuild) {
                    stack.shrink(1);
                }
                level.playSound(null, pos, SoundEvents.WOOL_PLACE, SoundSource.BLOCKS, 0.8F, 1.1F);
                player.displayClientMessage(NinjacatText.teal("Mesh stretched across the Loomframe. Load it with grit."), true);
                return ItemInteractionResult.CONSUME;
            }
            return ItemInteractionResult.FAIL;
        }

        if (LoomframeBlockEntity.isSiftable(stack)) {
            if (level.isClientSide) {
                return ItemInteractionResult.SUCCESS;
            }
            if (!be.hasMesh()) {
                player.displayClientMessage(Component.translatable("message.voidloom.loomframe.need_mesh"), true);
                return ItemInteractionResult.CONSUME;
            }
            int taken = be.insertInput(stack, false);
            if (taken <= 0) {
                player.displayClientMessage(Component.translatable("message.voidloom.loomframe.full"), true);
                return ItemInteractionResult.CONSUME;
            }
            if (!player.getAbilities().instabuild) {
                stack.shrink(taken);
            }
            level.playSound(null, pos, SoundEvents.GRAVEL_PLACE, SoundSource.BLOCKS, 0.6F, 1.1F);
            player.displayClientMessage(NinjacatText.teal("Grit on the mesh: " + be.getInput().getCount() + ". The frame will work it."), true);
            return ItemInteractionResult.CONSUME;
        }

        return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof LoomframeBlockEntity be)) {
            return InteractionResult.PASS;
        }
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }

        if (be.hasOutput()) {
            for (ItemStack out : be.takeAllOutput()) {
                give(level, pos, player, out);
            }
            level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.5F, 1.0F);
            player.displayClientMessage(NinjacatText.gold("Scraps shaken loose from the weave."), true);
            return InteractionResult.CONSUME;
        }

        if (player.isShiftKeyDown() && be.hasMesh()) {
            if (!be.getInput().isEmpty()) {
                give(level, pos, player, be.takeInput());
            }
            give(level, pos, player, be.takeMesh());
            level.playSound(null, pos, SoundEvents.WOOL_BREAK, SoundSource.BLOCKS, 0.7F, 0.9F);
            player.displayClientMessage(Component.translatable("message.voidloom.loomframe.mesh_removed"), true);
            return InteractionResult.CONSUME;
        }

        if (!be.getInput().isEmpty()) {
            give(level, pos, player, be.takeInput());
            player.displayClientMessage(NinjacatText.teal("Grit taken back."), true);
            return InteractionResult.CONSUME;
        }

        if (!be.hasMesh()) {
            player.displayClientMessage(Component.translatable("message.voidloom.loomframe.need_mesh"), true);
        } else {
            player.displayClientMessage(Component.translatable("message.voidloom.loomframe.idle"), true);
        }
        return InteractionResult.CONSUME;
    }

    private static void give(Level level, BlockPos pos, Player player, ItemStack stack) {
        if (!stack.isEmpty() && !player.getInventory().add(stack)) {
            Containers.dropItemStack(level, pos.getX() + 0.5, pos.getY() + 1.0, pos.getZ() + 0.5, stack);
        }
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean movedByPiston) {
        if (!state.is(newState.getBlock()) && level.getBlockEntity(pos) instanceof LoomframeBlockEntity be) {
            for (ItemStack s : be.drainForDrop()) {
                Containers.dropItemStack(level, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, s);
            }
        }
        super.onRemove(state, level, pos, newState, movedByPiston);
    }
}
