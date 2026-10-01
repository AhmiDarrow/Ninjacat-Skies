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
        if (p.isSpectator()) return List.of();
        // Runs for every player every tick; most wear nothing, so nothing is allocated until a relic turns up.
        Found found = new Found();
        if (CURIOS) { try { CuriosBridge.collect(p, found); } catch (Throwable ignored) {} }
        found.add(p.getOffhandItem());
        for (int i = 0; i < 9; i++) found.add(p.getInventory().getItem(i));
        return found.out == null ? List.of() : found.out;
    }

    /** The first stack of each relic kind, in the order offered. */
    private static final class Found {
        List<ItemStack> out;

        void add(ItemStack s) {
            if (!(s.getItem() instanceof RelicItem)) return;
            if (out == null) out = new ArrayList<>(2);
            for (ItemStack o : out) if (o.getItem() == s.getItem()) return;
            out.add(s);
        }
    }

    public static boolean wearing(ServerPlayer p, RelicItem item) {
        for (ItemStack s : worn(p)) if (s.getItem() == item) return true;
        return false;
    }

    /** Only touched when Curios is loaded. */
    private static final class CuriosBridge {
        static void collect(ServerPlayer p, Found out) {
            var inv = top.theillusivec4.curios.api.CuriosApi.getCuriosInventory(p).orElse(null);
            if (inv == null) return;
            for (var handler : inv.getCurios().values()) {
                var stacks = handler.getStacks();
                for (int i = 0; i < stacks.getSlots(); i++) out.add(stacks.getStackInSlot(i));
            }
        }
    }
}
