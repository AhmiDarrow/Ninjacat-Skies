package com.ninjacat.skies.driftwrecks.item;

import com.ninjacat.skies.core.tension.Strand;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

/** Opens a Tier 3 wreck's sealed rift of its Strand. Consumed on use. */
public class WeftKeyItem extends Item {
    public WeftKeyItem(Properties props) { super(props); }

    @Override
    public Component getName(ItemStack stack) {
        Strand s = DriftlureItem.strandOf(stack);
        return s == null ? super.getName(stack) : Component.translatable("item.driftwrecks.weft_key.named", s.title());
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> tip, TooltipFlag flag) {
        tip.add(Component.translatable("item.driftwrecks.weft_key.tip").withStyle(st -> st.withColor(0x3D7A7A)));
    }
}
