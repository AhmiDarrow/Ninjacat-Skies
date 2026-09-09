package com.ninjacat.skies.guardians.item;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.arena.ArenaManager;
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
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * A Frayed Totem calls one Snapped Guardian. Use it anywhere outside an arena: your Clowder mates within 32 blocks
 * come with you; the totem is consumed when the fight starts (win or lose). One item per guardian.
 */
public class FrayedTotemItem extends Item {
    public final GuardianKind kind;

    public FrayedTotemItem(GuardianKind kind) {
        super(new Item.Properties().stacksTo(1).rarity(kind.tier == GuardianKind.Tier.INSANE ? Rarity.EPIC : Rarity.RARE));
        this.kind = kind;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(player instanceof ServerPlayer sp)) return InteractionResultHolder.sidedSuccess(stack, true);
        String fail = ArenaManager.get(sp.server).summon(sp, kind);
        if (fail != null) {
            sp.displayClientMessage(NinjacatText.teal(fail), true);
            level.playSound(null, sp.blockPosition(), SoundEvents.NOTE_BLOCK_BASS.value(), SoundSource.PLAYERS, 0.8F, 0.5F);
            return InteractionResultHolder.fail(stack);
        }
        if (!sp.getAbilities().instabuild) stack.shrink(1);
        return InteractionResultHolder.consume(stack);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> tip, TooltipFlag flag) {
        tip.add(NinjacatText.gold("Calls " + kind.title + " to the arena."));
        tip.add(NinjacatText.teal("Clowder mates within 32 blocks answer with you."));
        if (kind.tier == GuardianKind.Tier.INSANE) tip.add(NinjacatText.teal("Only after the Reweave."));
        tip.add(Component.literal("Spent when the fight begins.").withStyle(net.minecraft.ChatFormatting.GRAY));
    }
}
