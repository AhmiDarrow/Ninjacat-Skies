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
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;

import javax.annotation.Nullable;

/** Mesh pedestal with a tiny pack-native sift flair — not a full Ex Deorum sieve. */
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

    @Override
    protected ItemInteractionResult useItemOn(
            ItemStack stack,
            BlockState state,
            Level level,
            BlockPos pos,
            Player player,
            InteractionHand hand,
            BlockHitResult hit
    ) {
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
                player.displayClientMessage(NinjacatText.teal("Mesh stretched across the Loomframe."), true);
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
            if (be.isOnCooldown(level.getGameTime())) {
                player.displayClientMessage(Component.translatable("message.voidloom.loomframe.cooldown"), true);
                return ItemInteractionResult.CONSUME;
            }
            ItemStack bonus = be.sift(stack, level.getGameTime());
            if (bonus.isEmpty()) {
                return ItemInteractionResult.FAIL;
            }
            if (!player.getAbilities().instabuild) {
                stack.shrink(1);
            }
            if (!player.getInventory().add(bonus)) {
                Containers.dropItemStack(level, pos.getX(), pos.getY() + 1.0, pos.getZ(), bonus);
            }
            level.playSound(null, pos, SoundEvents.SAND_BREAK, SoundSource.BLOCKS, 0.6F, 1.3F);
            player.displayClientMessage(NinjacatText.teal("A scrap shakes loose from the weave."), true);
            return ItemInteractionResult.CONSUME;
        }

        return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof LoomframeBlockEntity be) || !be.hasMesh()) {
            return InteractionResult.PASS;
        }
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        ItemStack mesh = be.takeMesh();
        if (!player.getInventory().add(mesh)) {
            Containers.dropItemStack(level, pos.getX(), pos.getY() + 1.0, pos.getZ(), mesh);
        }
        level.playSound(null, pos, SoundEvents.WOOL_BREAK, SoundSource.BLOCKS, 0.7F, 0.9F);
        player.displayClientMessage(Component.translatable("message.voidloom.loomframe.mesh_removed"), true);
        return InteractionResult.CONSUME;
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean movedByPiston) {
        if (!state.is(newState.getBlock()) && level.getBlockEntity(pos) instanceof LoomframeBlockEntity be && be.hasMesh()) {
            Containers.dropItemStack(level, pos.getX(), pos.getY(), pos.getZ(), be.takeMesh());
        }
        super.onRemove(state, level, pos, newState, movedByPiston);
    }
}
