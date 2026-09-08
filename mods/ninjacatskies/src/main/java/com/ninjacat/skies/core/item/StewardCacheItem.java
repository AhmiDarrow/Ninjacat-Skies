package com.ninjacat.skies.core.item;

import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import java.util.List;

/** Sealed provisions left by the Nine Tribes. Only the server rolls or spends a cache. */
public final class StewardCacheItem extends Item {
    private final String tier;
    public StewardCacheItem(String tier) {
        super(new Properties().stacksTo(64));
        this.tier = tier;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack held = player.getItemInHand(hand);
        if (!(level instanceof ServerLevel server)) return InteractionResultHolder.success(held);
        if (player.getCooldowns().isOnCooldown(this)) return InteractionResultHolder.fail(held);
        var table = server.getServer().reloadableRegistries().getLootTable(ResourceKey.create(
                Registries.LOOT_TABLE, ResourceLocation.fromNamespaceAndPath("ninjacatskies", "provisions/" + tier)));
        var params = new LootParams.Builder(server)
                .withParameter(LootContextParams.ORIGIN, player.position())
                .withParameter(LootContextParams.THIS_ENTITY, player)
                .create(LootContextParamSets.GIFT);
        // A disabled/missing datapack table must not destroy the player's sealed reward.
        var loot = table.getRandomItems(params);
        if (loot.stream().allMatch(ItemStack::isEmpty)) {
            player.displayClientMessage(Component.translatable("message.ninjacatskies.cache_empty"), true);
            return InteractionResultHolder.fail(held);
        }
        held.consume(1, player);
        for (ItemStack stack : loot) {
            if (!player.getInventory().add(stack) && !stack.isEmpty()) player.drop(stack, false);
        }
        player.getCooldowns().addCooldown(this, 12);
        level.playSound(null, player.blockPosition(), SoundEvents.BUNDLE_DROP_CONTENTS, SoundSource.PLAYERS, 0.6F, 1.0F);
        return InteractionResultHolder.consume(held);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> lines, TooltipFlag flag) {
        lines.add(Component.translatable("tooltip.ninjacatskies.cache_lore").withStyle(ChatFormatting.DARK_AQUA));
        lines.add(Component.translatable("tooltip.ninjacatskies.cache_" + tier).withStyle(ChatFormatting.GRAY));
        lines.add(Component.translatable("tooltip.ninjacatskies.cache_open").withStyle(ChatFormatting.GRAY));
        lines.add(Component.translatable("tooltip.ninjacatskies.cache_combine").withStyle(ChatFormatting.GOLD));
    }
}
