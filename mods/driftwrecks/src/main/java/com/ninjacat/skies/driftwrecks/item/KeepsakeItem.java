package com.ninjacat.skies.driftwrecks.item;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.block.Block;

import java.util.List;

/** A Keepsake as an item: its one-line inscription in Steward voice. */
public class KeepsakeItem extends BlockItem {
    public KeepsakeItem(Block block, Properties props) { super(block, props); }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> tip, TooltipFlag flag) {
        String path = BuiltInRegistries.BLOCK.getKey(getBlock()).getPath();
        tip.add(Component.translatable("block.driftwrecks." + path + ".inscription").withStyle(st -> st.withItalic(true).withColor(0x3D7A7A)));
    }
}
