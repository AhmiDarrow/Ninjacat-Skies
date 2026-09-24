package com.ninjacat.skies.core.block;

import com.mojang.serialization.MapCodec;
import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.Objects;

/**
 * Where a player's things wait after they die: a wicker basket of yarn balls. Its owner or their Clowder
 * right-clicks it to take everything back, or breaks it to spill it. Nobody else can do either.
 */
public class YarnBasketBlock extends BaseEntityBlock {
    public static final MapCodec<YarnBasketBlock> CODEC = simpleCodec(YarnBasketBlock::new);
    private static final VoxelShape SHAPE = Block.box(1, 0, 1, 15, 13, 15);

    public YarnBasketBlock(Properties properties) {
        super(properties);
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() { return CODEC; }

    @Override
    protected RenderShape getRenderShape(BlockState state) { return RenderShape.MODEL; }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) { return SHAPE; }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) { return new YarnBasketBlockEntity(pos, state); }

    /** The owner, anyone in the owner's Clowder, or a creative player. */
    public static boolean mayOpen(Player player, YarnBasketBlockEntity basket) {
        if (player.isCreative()) return true;
        if (player.getUUID().equals(basket.owner())) return true;
        if (basket.clowder() == null || !(player instanceof ServerPlayer sp)) return false;
        return LoomTension.clowderOf(sp).map(Clowder::id).map(id -> Objects.equals(id, basket.clowder())).orElse(false);
    }

    @Override
    protected float getDestroyProgress(BlockState state, Player player, BlockGetter level, BlockPos pos) {
        if (level.getBlockEntity(pos) instanceof YarnBasketBlockEntity basket && !mayOpen(player, basket)) return 0.0F;
        return super.getDestroyProgress(state, player, level, pos);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!(level.getBlockEntity(pos) instanceof YarnBasketBlockEntity basket)) return InteractionResult.PASS;
        if (level.isClientSide) return InteractionResult.SUCCESS;
        if (!mayOpen(player, basket)) {
            player.displayClientMessage(NinjacatText.teal(basket.ownerName() + "'s yarn basket. It is not yours to unpick."), true);
            return InteractionResult.CONSUME;
        }
        // Right-click works where breaking is protected (the Dock, the Hall): everything goes straight to the inventory.
        String name = basket.ownerName();
        for (ItemStack s : basket.takeAll()) {
            if (!player.getInventory().add(s) && !s.isEmpty()) player.drop(s, false);
        }
        level.removeBlock(pos, false);
        level.playSound(null, pos, SoundEvents.WOOL_BREAK, SoundSource.BLOCKS, 1.0F, 1.1F);
        player.displayClientMessage(NinjacatText.teal(player.getGameProfile().getName().equals(name)
                ? "You gather up your things." : "You gather up " + name + "'s things."), true);
        return InteractionResult.CONSUME;
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean movedByPiston) {
        // However the basket goes (a break, a command, a mod clearing blocks), nothing inside is lost.
        if (!state.is(newState.getBlock()) && level.getBlockEntity(pos) instanceof YarnBasketBlockEntity basket) {
            for (ItemStack s : basket.takeAll()) Containers.dropItemStack(level, pos.getX(), pos.getY(), pos.getZ(), s);
        }
        super.onRemove(state, level, pos, newState, movedByPiston);
    }
}
