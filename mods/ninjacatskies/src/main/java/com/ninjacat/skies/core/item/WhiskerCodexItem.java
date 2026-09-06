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
 * The damaged assigner. Right-click opens the Codex book (Modonomicon); sneak-right-click asks it
 * for the next practical step. It never lectures; it points.
 */
public class WhiskerCodexItem extends Item {
    private static final boolean MODONOMICON = ModList.get().isLoaded("modonomicon");

    /** What the Codex says the next unseated Strand needs. One line, one verb. */
    private static final String[] NUDGES = {
            "Soil first. Wood, dirt, a bench, a sapling. Claim the pad and let it hold you.",
            "Stone: unravel Thread to string, spin Void Yarn, tie a Binding Knot. Then let the mesh catch grit.",
            "Sprout: a field, a kitchen, a first Inferium row. Feed the Clowder before the forge.",
            "Claw: blueprints, iron on your back, a way off the pad that you chose.",
            "Spark: strike a Drumheart and hold a Pulse before you touch a wire.",
            "Clock: one cog, then the same cog again. Let Create carry the pattern.",
            "Swarm: keep something alive that keeps something else alive. Bees, deep crops.",
            "Sigil: two braid paths make a cord. Then carve seals and ask the stewards' rites.",
            "Spindle: a digital loom, a March stone, and the Post. Stitch the cut.",
    };

    public WhiskerCodexItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(player instanceof ServerPlayer sp)) {
            return InteractionResultHolder.sidedSuccess(stack, true);
        }
        if (!player.isShiftKeyDown() && MODONOMICON && CodexBookHook.open(sp)) {
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
            player.sendSystemMessage(NinjacatText.gold("Every Strand answers. Seat the Fragment and go see the March."));
            return;
        }
        int seated = Integer.bitCount(bits);
        player.sendSystemMessage(NinjacatText.teal("The Codex thins to a point."));
        player.sendSystemMessage(NinjacatText.gold(NUDGES[next.ordinal()]));
        if (seated > 0) {
            player.sendSystemMessage(NinjacatText.teal(seated + " of nine tensioned. Quests in the book; tokens to the Post."));
        } else {
            player.sendSystemMessage(NinjacatText.teal("Open the quest book for the work. Raise a Tension Post when the first token comes."));
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(NinjacatText.teal("Damaged, but it still assigns work."));
        tooltip.add(Component.translatable(MODONOMICON ? "tooltip.ninjacatskies.codex.book" : "tooltip.ninjacatskies.codex.nudge")
                .withStyle(s -> s.withColor(0x8A8580)));
    }
}
