package com.ninjacat.skies.voidloom.block;

import com.mojang.serialization.MapCodec;
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

/** Tension Barrel: pour water, drop in dirt (or string and pearls), come back for what settled. */
public class TensionBarrelBlock extends BaseEntityBlock {
    @Override protected boolean hasAnalogOutputSignal(BlockState state) { return true; }
    @Override protected int getAnalogOutputSignal(BlockState state, Level level, BlockPos pos) {
        if (!(level.getBlockEntity(pos) instanceof TensionBarrelBlockEntity be)) return 0;
        var inventory = be.handler();
        float fullness = 0; boolean occupied = false;
        for (int i=1; i<inventory.getSlots(); i++) {
            ItemStack stack = inventory.getStackInSlot(i);
            if (!stack.isEmpty()) { occupied = true; fullness += (float)stack.getCount()/stack.getMaxStackSize(); }
        }
        return occupied ? 1 + (int)(14 * fullness / (inventory.getSlots()-1)) : 0;
    }
    public static final MapCodec<TensionBarrelBlock> CODEC = simpleCodec(TensionBarrelBlock::new);

    public TensionBarrelBlock(Properties properties) {
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
        return new TensionBarrelBlockEntity(pos, state);
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        return level.isClientSide ? null : createTickerHelper(type, ModBlockEntities.TENSION_BARREL.get(), TensionBarrelBlockEntity::serverTick);
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (level.hasNeighborSignal(pos)) {
            if (!level.isClientSide) player.displayClientMessage(Component.literal("Paused by redstone."), true);
            return ItemInteractionResult.CONSUME;
        }
        if (!(level.getBlockEntity(pos) instanceof TensionBarrelBlockEntity be) || stack.isEmpty()) {
            return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        }
        if (!TensionBarrelBlockEntity.isAcceptedInput(stack)) {
            // Not an input: let the empty-hand interaction (collect output / status) run instead of swallowing the click.
            return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        }
        if (level.isClientSide) {
            return ItemInteractionResult.SUCCESS;
        }

        if (TensionBarrelBlockEntity.isWaterCarrier(stack)) {
            ItemStack empty = be.pourWater(stack);
            if (empty.isEmpty()) {
                player.displayClientMessage(Component.translatable("message.voidloom.tension.water_full"), true);
                return ItemInteractionResult.CONSUME;
            }
            if (!player.getAbilities().instabuild) {
                stack.shrink(1);
                give(level, pos, player, empty);
            }
            level.playSound(null, pos, SoundEvents.BUCKET_EMPTY, SoundSource.BLOCKS, 0.7F, 1.0F);
            player.displayClientMessage(Component.translatable("message.voidloom.tension.water_added", be.getWater()), true);
            return ItemInteractionResult.CONSUME;
        }

        int taken = be.insertDry(stack, false);
        if (taken <= 0) {
            player.displayClientMessage(Component.translatable("message.voidloom.tension.full"), true);
            return ItemInteractionResult.CONSUME;
        }
        if (!player.getAbilities().instabuild) {
            stack.shrink(taken);
        }
        level.playSound(null, pos, SoundEvents.BARREL_CLOSE, SoundSource.BLOCKS, 0.5F, 1.2F);
        player.displayClientMessage(Component.translatable("message.voidloom.tension.input_added", taken), true);
        return ItemInteractionResult.CONSUME;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (level.hasNeighborSignal(pos)) {
            if (!level.isClientSide) player.displayClientMessage(Component.literal("Paused by redstone."), true);
            return InteractionResult.CONSUME;
        }
        if (!(level.getBlockEntity(pos) instanceof TensionBarrelBlockEntity be)) {
            return InteractionResult.PASS;
        }
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }
        if (be.hasOutput()) {
            for (ItemStack out : be.takeAllOutput()) {
                give(level, pos, player, out);
            }
            level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.4F, 1.0F);
            player.displayClientMessage(Component.translatable("message.voidloom.tension.collected"), true);
            return InteractionResult.CONSUME;
        }
        if (player.isShiftKeyDown()) {
            var pulled = be.takeDryInputs();
            if (!pulled.isEmpty()) {
                for (ItemStack s : pulled) {
                    give(level, pos, player, s);
                }
                level.playSound(null, pos, SoundEvents.BARREL_OPEN, SoundSource.BLOCKS, 0.4F, 1.0F);
                player.displayClientMessage(Component.translatable("message.voidloom.tension.removed"), true);
                return InteractionResult.CONSUME;
            }
        }
        be.tellStatus(player);
        return InteractionResult.CONSUME;
    }

    private static void give(Level level, BlockPos pos, Player player, ItemStack stack) {
        if (!stack.isEmpty() && !player.getInventory().add(stack)) {
            Containers.dropItemStack(level, pos.getX() + 0.5, pos.getY() + 1.0, pos.getZ() + 0.5, stack);
        }
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean movedByPiston) {
        if (!state.is(newState.getBlock()) && level.getBlockEntity(pos) instanceof TensionBarrelBlockEntity be) {
            be.dropAll(level, pos);
        }
        super.onRemove(state, level, pos, newState, movedByPiston);
    }
}
