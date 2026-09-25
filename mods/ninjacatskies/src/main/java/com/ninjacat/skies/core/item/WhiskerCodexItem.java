package com.ninjacat.skies.core.item;

import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.core.tension.Strand;
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
import net.neoforged.fml.ModList;

import java.util.List;

/**
 * The damaged assigner. Right-click always opens the campaign book (Modonomicon). FTB Quests stays on grave (`).
 * Without the book mod, it still offers a practical next-step hint.
 */
public class WhiskerCodexItem extends Item {
    private static final boolean MODONOMICON = ModList.get().isLoaded("modonomicon");
    private static final boolean QUESTS = ModList.get().isLoaded("ftbquests");

    public WhiskerCodexItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(player instanceof ServerPlayer sp)) {
            return InteractionResultHolder.sidedSuccess(stack, true);
        }
        if (MODONOMICON && CodexBookHook.open(sp)) {
            return InteractionResultHolder.sidedSuccess(stack, false);
        }
        nudge(sp);
        return InteractionResultHolder.sidedSuccess(stack, false);
    }

    private static void nudge(ServerPlayer player) {
        int bits = LoomTension.strandBits(player);
        Strand next = null;
        for (Strand s : Strand.ALL) {
            if ((bits & s.bit()) == 0) {
                next = s;
                break;
            }
        }
        if (next == null) {
            player.sendSystemMessage(NinjacatText.goldKey("message.ninjacatskies.codex.all_answer"));
            return;
        }
        int seated = Integer.bitCount(bits);
        player.sendSystemMessage(NinjacatText.tealKey("message.ninjacatskies.codex.thins"));
        player.sendSystemMessage(NinjacatText.goldKey("message.ninjacatskies.codex.nudge." + next.id()));
        if (seated > 0) {
            player.sendSystemMessage(NinjacatText.tealKey("message.ninjacatskies.codex.progress", seated));
        } else {
            player.sendSystemMessage(NinjacatText.tealKey("message.ninjacatskies.codex.start"));
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(NinjacatText.tealKey("tooltip.ninjacatskies.codex.damaged"));
        tooltip.add(Component.translatable(MODONOMICON ? "tooltip.ninjacatskies.codex.book" : QUESTS ? "tooltip.ninjacatskies.codex.quests" : "tooltip.ninjacatskies.codex.nudge")
                .withStyle(s -> s.withColor(0x8A8580)));
    }
}
