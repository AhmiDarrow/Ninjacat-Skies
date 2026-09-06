package com.ninjacat.skies.clowder.item;

import com.ninjacat.skies.clowder.world.ModDimensions;
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

/** Cold brass that remembers Clowder Hall. Right-click toggles Hall ↔ pad. */
public class HubKeyItem extends Item {
    public HubKeyItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!level.isClientSide && player instanceof ServerPlayer serverPlayer) {
            if (serverPlayer.level().dimension().equals(ModDimensions.CLOWDER_HALL)) {
                ModDimensions.returnFromHub(serverPlayer);
            } else {
                ModDimensions.travelToHub(serverPlayer);
            }
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.clowderhall.hub_key.desc"));
        tooltip.add(NinjacatText.gold("Right-click: enter Hall — or leave if you are already there."));
    }
}
