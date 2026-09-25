package com.ninjacat.skies.driftwrecks.item;

import com.ninjacat.skies.driftwrecks.registry.DwComponents;
import com.ninjacat.skies.driftwrecks.registry.DwItems;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.ItemContainerContents;
import net.minecraft.world.level.Level;

import java.util.List;

/** What a member left on an unravelled wreck, tied up and sent home. Right-click to unpack. */
public class SalvageBundleItem extends Item {
    public SalvageBundleItem(Properties props) { super(props); }

    public static ItemStack of(List<ItemStack> items, String owner) {
        ItemStack b = new ItemStack(DwItems.SALVAGE_BUNDLE.get());
        b.set(DataComponents.CONTAINER, ItemContainerContents.fromItems(items.subList(0, Math.min(items.size(), 256))));
        b.set(DwComponents.OWNER.get(), owner);
        return b;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack b = player.getItemInHand(hand);
        if (level.isClientSide) return InteractionResultHolder.success(b);
        ItemContainerContents c = b.getOrDefault(DataComponents.CONTAINER, ItemContainerContents.EMPTY);
        c.nonEmptyItemsCopy().forEach(s -> { if (!player.addItem(s)) player.drop(s, false); });
        level.playSound(null, player.blockPosition(), SoundEvents.BUNDLE_DROP_CONTENTS, SoundSource.PLAYERS, 1.0F, 1.0F);
        b.shrink(1);
        return InteractionResultHolder.consume(b);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> tip, TooltipFlag flag) {
        String owner = stack.get(DwComponents.OWNER.get());
        if (owner != null) tip.add(Component.translatable("item.driftwrecks.salvage_bundle.owner",
                owner.isEmpty() ? Component.translatable("item.driftwrecks.salvage_bundle.owner_unknown") : owner).withStyle(st -> st.withColor(0xD4A84B)));
        tip.add(Component.translatable("item.driftwrecks.salvage_bundle.tip").withStyle(st -> st.withColor(0x3D7A7A)));
    }
}
