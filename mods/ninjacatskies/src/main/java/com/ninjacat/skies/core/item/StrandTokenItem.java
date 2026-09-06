package com.ninjacat.skies.core.item;

import com.ninjacat.skies.core.tension.Strand;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

/** Proof that a Strand answered. Seat it at a Tension Post; keep any spare as a souvenir. */
public class StrandTokenItem extends Item {
    private final Strand strand;

    public StrandTokenItem(String strandId, Properties properties) {
        super(properties);
        Strand s = Strand.byId(strandId);
        this.strand = s == null ? Strand.SOIL : s;
    }

    public Strand strand() {
        return strand;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal(strand.tribe()).withStyle(s -> s.withColor(strand.color()).withItalic(true)));
        tooltip.add(Component.translatable("tooltip.ninjacatskies.strand_token").withStyle(s -> s.withColor(0x8A8580)));
    }
}
