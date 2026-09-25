package com.ninjacat.skies.core.item;

import com.ninjacat.skies.core.sound.ModSounds;
import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.contents.TranslatableContents;
import net.minecraft.server.level.ServerPlayer;
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
 * A page torn from a steward's margin. Right-click to read it. Pages are kept, not spent —
 * nine tribes' worth make a shelf worth having.
 */
public class CodexPageItem extends Item {
    public CodexPageItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(player instanceof ServerPlayer sp)) {
            return InteractionResultHolder.sidedSuccess(stack, true);
        }
        Strand strand = tribeOf(stack);
        int slot = Math.floorMod((int) (level.getGameTime() / 20L) + player.getUUID().hashCode(), 3);

        level.playSound(null, player.blockPosition(), ModSounds.PAGE.get(), SoundSource.PLAYERS, 0.8F, 1.0F);
        sp.sendSystemMessage(Component.translatable("message.ninjacatskies.page.margin", strand.tribe()).withStyle(s -> s.withColor(strand.color()).withItalic(true)));
        sp.sendSystemMessage(NinjacatText.tealKey("message.ninjacatskies.page." + strand.id() + ".note_" + (slot + 1)));
        player.getCooldowns().addCooldown(this, 20);
        return InteractionResultHolder.sidedSuccess(stack, false);
    }

    /** A page named at seat time knows its tribe; a Desk page picks one by where it is in the stack. */
    private static Strand tribeOf(ItemStack stack) {
        Component name = stack.get(DataComponents.CUSTOM_NAME);
        if (name != null) {
            String raw = name.getString();
            // A page named at seat time carries its tribe as a translation argument; read it without a lang lookup.
            // New pages carry the tribe's lang key; pages named before translation carry the English tribe string.
            if (name.getContents() instanceof TranslatableContents tc) {
                for (Object arg : tc.getArgs()) {
                    if (arg instanceof Component c && c.getContents() instanceof TranslatableContents argKey) {
                        for (Strand s : Strand.ALL) {
                            if (s.tribeKey().equals(argKey.getKey())) {
                                return s;
                            }
                        }
                    }
                    raw += " " + (arg instanceof Component c ? c.getString() : String.valueOf(arg));
                }
            }
            for (Strand s : Strand.ALL) {
                if (s.legacyTribeIn(raw)) {
                    return s;
                }
            }
        }
        return Strand.ALL[Math.floorMod(stack.getCount() * 7 + 3, Strand.ALL.length)];
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.ninjacatskies.codex_page").withStyle(s -> s.withColor(0x8A8580)));
    }
}
