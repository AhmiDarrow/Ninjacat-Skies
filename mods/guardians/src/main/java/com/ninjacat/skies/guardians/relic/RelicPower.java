package com.ninjacat.skies.guardians.relic;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.event.entity.living.LivingDamageEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;

/**
 * The behaviour of one Woven Relic. Passive hooks are only invoked while the relic is worn (see {@link RelicSlots});
 * they are called from {@link RelicEvents}. Implementations live in {@link Relics}.
 */
public interface RelicPower {
    String title();
    String passiveText();
    String activeText();
    int cooldownTicks();

    /** Right-click. Return true to consume the use and start the cooldown. */
    boolean activate(ServerPlayer player, ItemStack relic);

    /** Every server tick while worn. */
    default void tickWorn(ServerPlayer player, ItemStack relic) {}
    /** The wearer is about to take damage (amount can be changed, or the event cancelled). */
    default void onWearerHurt(ServerPlayer player, ItemStack relic, LivingIncomingDamageEvent e) {}
    /** The wearer dealt melee damage. */
    default void onWearerHit(ServerPlayer player, ItemStack relic, LivingEntity target, LivingDamageEvent.Pre e) {}
    /** Called once when the relic starts being worn (apply attribute modifiers) and once when it stops. */
    default void onWorn(ServerPlayer player, boolean worn) {}
}
