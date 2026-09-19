package com.ninjacat.skies.driftwrecks.item;

import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.driftwrecks.wreck.TeamDrift;
import com.ninjacat.skies.driftwrecks.wreck.WreckRewards;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/** The Wreck Atlas: the Clowder's grid of every Strand x core, stamps and perks. Opens a client screen. */
public class WreckAtlasItem extends Item {
    public WreckAtlasItem(Properties props) { super(props); }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack s = player.getItemInHand(hand);
        if (level.isClientSide) {
            com.ninjacat.skies.driftwrecks.client.ClientHooks.openAtlas();
        } else if (player instanceof ServerPlayer sp) {
            WreckRewards.award(sp, "atlas");
            LoomTension.clowderOf(sp).ifPresent(c -> WreckRewards.sync(sp, TeamDrift.of(c)));
        }
        return InteractionResultHolder.sidedSuccess(s, level.isClientSide);
    }
}
