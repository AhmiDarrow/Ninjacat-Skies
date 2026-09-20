package com.ninjacat.skies.core.item;

import com.ninjacat.skies.core.config.SkiesConfig;
import com.ninjacat.skies.core.event.SkyboundEvents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import net.minecraft.network.chat.TextColor;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * Four Thread Shards stitched back into one life. Unlike the six quest milestones this keeps no receipt, so a
 * Clowder can earn it again for as long as it can pay: the Shard price is the limit, not a counter.
 * A Clowder at zero is already spectating and cannot use one — hold a spare before the pool runs out.
 */
public class ThreadOfReturnItem extends Item {
    private static final int TEAL = 0x59D9C9;
    private static final int GREY = 0x8A8580;

    public ThreadOfReturnItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level.isClientSide) return InteractionResultHolder.success(stack);
        if (!(player instanceof ServerPlayer server)) return InteractionResultHolder.pass(stack);
        if (!SkiesConfig.HARDCORE_LIVES_ENABLED.get()) {
            server.displayClientMessage(msg("message.ninjacatskies.thread_of_return.lives_off"), true);
            return InteractionResultHolder.fail(stack);
        }
        // No Clowder means no pool to credit; spending it there would burn the whole craft for nothing.
        if (!SkyboundEvents.spendThreadOfReturn(server)) {
            server.displayClientMessage(msg("message.ninjacatskies.thread_of_return.no_clowder"), true);
            return InteractionResultHolder.fail(stack);
        }
        stack.consume(1, player);
        level.playSound(null, player.blockPosition(), SoundEvents.TOTEM_USE, SoundSource.PLAYERS, 0.7F, 1.4F);
        player.getCooldowns().addCooldown(this, 40);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.ninjacatskies.thread_of_return")
                .withStyle(Style.EMPTY.withColor(TextColor.fromRgb(TEAL))));
        tooltip.add(Component.translatable("tooltip.ninjacatskies.thread_of_return.hint")
                .withStyle(Style.EMPTY.withColor(TextColor.fromRgb(GREY)).withItalic(true)));
    }

    private static Component msg(String key) {
        return Component.translatable(key).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(TEAL)));
    }
}
