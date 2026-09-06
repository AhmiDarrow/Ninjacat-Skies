package com.ninjacat.skies.core.item;

import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * Story surface for the pack. Opens guidance; FTB Quests owns the full book UI.
 * Right-click whispers the next practical step rather than a lore dump.
 */
public class WhiskerCodexItem extends Item {
    public WhiskerCodexItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!level.isClientSide && player instanceof ServerPlayer) {
            player.displayClientMessage(
                    NinjacatText.teal("The Codex thins to a point: open your Quest Book (default key) and pull the next Strand."),
                    false
            );
            player.displayClientMessage(
                    NinjacatText.gold("Loom Braid: Wake → Recover → Root → Edge; then Pattern, Colony, Hum as peers; Bind; Reweave."),
                    false
            );
            player.displayClientMessage(
                    NinjacatText.teal("Tribes: Pad-keepers, Grit-singers, Rootbinders, Edge-walkers, Drumhearts,"),
                    false
            );
            player.displayClientMessage(
                    NinjacatText.teal("Pattern-weavers, Colony-keepers, Seal-carvers, Loom-stitchers."),
                    false
            );
            player.displayClientMessage(
                    NinjacatText.gold("Soil first. Stone: Thread→string→yarn → hammer/mesh/barrel → clay → porcelain → sieve → knot."),
                    false
            );
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(NinjacatText.indigo("Damaged, but it still assigns work."));
        tooltip.add(Component.literal("Right-click for a nudge."));
    }
}
