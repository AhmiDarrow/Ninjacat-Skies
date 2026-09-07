package com.ninjacat.skies.voidloom.block;

import net.minecraft.world.item.ItemStack;
import java.util.List;

/** Inserts across all output stacks, returning the amount that did not fit. */
final class OutputStorage {
    private OutputStorage() {}

    static int insert(List<ItemStack> slots, ItemStack incoming, boolean simulate) {
        int remaining = incoming.getCount();
        for (int pass = 0; pass < 2 && remaining > 0; pass++) {
            for (int i = 0; i < slots.size() && remaining > 0; i++) {
                ItemStack slot = slots.get(i);
                if (pass == 0 ? slot.isEmpty() || !ItemStack.isSameItemSameComponents(slot, incoming) : !slot.isEmpty()) continue;
                int moved = Math.min(remaining, Math.max(0, incoming.getMaxStackSize() - slot.getCount()));
                if (!simulate && moved > 0) {
                    if (slot.isEmpty()) slots.set(i, incoming.copyWithCount(moved));
                    else slot.grow(moved);
                }
                remaining -= moved;
            }
        }
        return remaining;
    }
}
