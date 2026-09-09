package com.ninjacat.skies.guardians.item;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.relic.RelicPower;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * A Woven Relic: trophy + one on-theme power (see WOVEN_RELICS.md). Passives apply while the relic is worn
 * (hotbar, off-hand or a Curios slot — see {@link com.ninjacat.skies.guardians.relic.RelicSlots}); the active
 * fires on right-click and shows its cooldown on the item. The power itself lives in a {@link RelicPower}.
 */
public class RelicItem extends Item {
    public final GuardianKind kind;
    public final RelicPower power;

    public RelicItem(GuardianKind kind, RelicPower power) {
        super(new Item.Properties().stacksTo(1).fireResistant().rarity(kind.tier == GuardianKind.Tier.INSANE || kind == GuardianKind.UNWOVEN ? Rarity.EPIC : Rarity.RARE));
        this.kind = kind; this.power = power;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(player instanceof ServerPlayer sp)) return InteractionResultHolder.sidedSuccess(stack, true);
        if (sp.getCooldowns().isOnCooldown(this)) return InteractionResultHolder.fail(stack);
        if (power.activate(sp, stack)) {
            sp.getCooldowns().addCooldown(this, power.cooldownTicks());
            return InteractionResultHolder.consume(stack);
        }
        return InteractionResultHolder.fail(stack);
    }

    @Override
    public boolean isFoil(ItemStack stack) { return false; }

    /** Relics are keystones, never reagents: crafting with one hands it back (the insane totems need Loomthread). */
    @Override public boolean hasCraftingRemainingItem(ItemStack stack) { return true; }
    @Override public ItemStack getCraftingRemainingItem(ItemStack stack) { return stack.copy(); }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> tip, TooltipFlag flag) {
        tip.add(NinjacatText.gold(power.title()));
        tip.add(NinjacatText.teal("Passive: ").append(Component.literal(power.passiveText()).withStyle(ChatFormatting.GRAY)));
        tip.add(NinjacatText.teal("Right-click: ").append(Component.literal(power.activeText()).withStyle(ChatFormatting.GRAY)));
        tip.add(Component.literal("Cooldown " + (power.cooldownTicks()/20) + " s · won from " + kind.title).withStyle(ChatFormatting.DARK_GRAY));
    }
}
