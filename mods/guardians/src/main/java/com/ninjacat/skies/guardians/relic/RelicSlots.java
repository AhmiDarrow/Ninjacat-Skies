package com.ninjacat.skies.guardians.relic;

import com.ninjacat.skies.guardians.item.RelicItem;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.neoforged.fml.ModList;

import java.util.ArrayList;
import java.util.List;

/**
 * Where a relic counts as "worn": off-hand, any hotbar slot, or a Curios slot when Curios is present.
 * (Hotbar counts so the relics work without a Curios slot type being configured; the pack ships a "relic" slot.)
 */
public final class RelicSlots {
    private RelicSlots() {}
    private static final boolean CURIOS = ModList.get().isLoaded("curios");

    /** The relics in effect: one stack per relic kind (a second copy of the same relic adds nothing), Curios slot first, then off-hand, then hotbar. */
    public static List<ItemStack> worn(ServerPlayer p) {
        List<ItemStack> found = new ArrayList<>();
        if (CURIOS) { try { CuriosBridge.collect(p, found); } catch (Throwable ignored) {} }
        ItemStack off = p.getOffhandItem(); if (off.getItem() instanceof RelicItem) found.add(off);
        for (int i = 0; i < 9; i++) { ItemStack s = p.getInventory().getItem(i); if (s.getItem() instanceof RelicItem) found.add(s); }
        List<ItemStack> out = new ArrayList<>();
        outer: for (ItemStack s : found) { for (ItemStack o : out) if (o.getItem() == s.getItem()) continue outer; out.add(s); }
        return out;
    }

    public static boolean wearing(ServerPlayer p, RelicItem item) {
        for (ItemStack s : worn(p)) if (s.getItem() == item) return true;
        return false;
    }

    /** Only touched when Curios is loaded. */
    private static final class CuriosBridge {
        static void collect(ServerPlayer p, List<ItemStack> out) {
            top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(p).ifPresent(inv -> {
                for (var entry : inv.getCurios().entrySet()) {
                    var stacks = entry.getValue().getStacks();
                    for (int i = 0; i < stacks.getSlots(); i++) { ItemStack s = stacks.getStackInSlot(i); if (s.getItem() instanceof RelicItem) out.add(s); }
                }
            });
        }
    }
}
