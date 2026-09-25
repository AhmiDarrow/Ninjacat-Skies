package com.ninjacat.skies.driftwrecks.item;

import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.driftwrecks.wreck.TeamDrift;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/** Read it: the next wreck to arrive is a core not yet in your Atlas for its skin. */
public class WreckMapScrollItem extends Item {
    public WreckMapScrollItem(Properties props) { super(props); }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack s = player.getItemInHand(hand);
        if (level.isClientSide) return InteractionResultHolder.success(s);
        if (player instanceof ServerPlayer sp) {
            LoomTension.clowderOf(sp).ifPresent(c -> {
                TeamDrift t = TeamDrift.of(c);
                if (t.scrollPending()) { sp.displayClientMessage(NinjacatText.tealKey("message.driftwrecks.map_scroll.pending"), true); return; }
                t.setScrollPending(true); t.dirty();
                level.playSound(null, sp.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1.0F, 0.8F);
                sp.sendSystemMessage(NinjacatText.tealKey("message.driftwrecks.map_scroll.read"));
                if (!sp.getAbilities().instabuild) s.shrink(1);
            });
        }
        return InteractionResultHolder.consume(s);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> tip, TooltipFlag flag) {
        tip.add(Component.translatable("item.driftwrecks.wreck_map_scroll.tip").withStyle(st -> st.withColor(0x3D7A7A)));
    }
}
