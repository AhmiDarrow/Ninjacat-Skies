package com.ninjacat.skies.driftwrecks.item;

import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.driftwrecks.registry.DwComponents;
import com.ninjacat.skies.driftwrecks.registry.DwItems;
import com.ninjacat.skies.driftwrecks.wreck.TeamDrift;
import com.ninjacat.skies.driftwrecks.wreck.WreckCore;
import com.ninjacat.skies.driftwrecks.wreck.WreckRewards;
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

import javax.annotation.Nullable;
import java.util.List;

/**
 * A loose Codex page about one kind of place. Reading it files it in the Codex for the whole Clowder, and from then
 * on that core's wrecks drift in with their hidden room open.
 */
public class HintPageItem extends Item {
    public HintPageItem(Properties props) { super(props); }

    public static ItemStack of(WreckCore c) {
        ItemStack s = new ItemStack(DwItems.HINT_PAGE.get());
        s.set(DwComponents.CORE.get(), c.id);
        return s;
    }

    @Nullable
    public static WreckCore coreOf(ItemStack s) {
        String id = s.get(DwComponents.CORE.get());
        return id == null ? null : WreckCore.byId(id);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack s = player.getItemInHand(hand);
        WreckCore core = coreOf(s);
        if (level.isClientSide || core == null) return InteractionResultHolder.sidedSuccess(s, level.isClientSide);
        if (player instanceof ServerPlayer sp) {
            LoomTension.clowderOf(sp).ifPresent(c -> {
                TeamDrift t = TeamDrift.of(c);
                boolean fresh = t.readHint(core);
                t.dirty();
                level.playSound(null, sp.blockPosition(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 1.0F, 1.0F);
                sp.sendSystemMessage(NinjacatText.tealKey(core.hintKey()));
                if (fresh) {
                    for (ServerPlayer m : c.onlineMembers()) {
                        WreckRewards.award(m, "hint/" + core.id);
                        m.sendSystemMessage(NinjacatText.goldKey("message.driftwrecks.hint_page.filed", core.titleInline()));
                    }
                    WreckRewards.syncAll(c);
                    if (!sp.getAbilities().instabuild) s.shrink(1);
                } else {
                    sp.displayClientMessage(NinjacatText.tealKey("message.driftwrecks.hint_page.known"), true);
                }
            });
        }
        return InteractionResultHolder.consume(s);
    }

    @Override
    public Component getName(ItemStack stack) {
        WreckCore c = coreOf(stack);
        return c == null ? super.getName(stack) : Component.translatable("item.driftwrecks.hint_page.named", c.title());
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> tip, TooltipFlag flag) {
        tip.add(Component.translatable("item.driftwrecks.hint_page.tip").withStyle(st -> st.withColor(0x3D7A7A)));
    }
}
