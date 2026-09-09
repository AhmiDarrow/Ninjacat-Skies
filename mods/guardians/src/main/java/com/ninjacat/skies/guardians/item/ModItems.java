package com.ninjacat.skies.guardians.item;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.Guardians;
import com.ninjacat.skies.guardians.relic.Relics;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.EnumMap;
import java.util.Map;

public final class ModItems {
    private ModItems() {}
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(Guardians.MOD_ID);
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Guardians.MOD_ID);

    public static final Map<GuardianKind, DeferredItem<FrayedTotemItem>> TOTEMS = new EnumMap<>(GuardianKind.class);
    public static final Map<GuardianKind, DeferredItem<RelicItem>> RELICS = new EnumMap<>(GuardianKind.class);

    static {
        for (GuardianKind k : GuardianKind.values()) {
            TOTEMS.put(k, ITEMS.register(k.totemId(), () -> new FrayedTotemItem(k)));
            RELICS.put(k, ITEMS.register(k.relicItemId(), () -> new RelicItem(k, Relics.power(k))));
        }
    }

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> TAB = TABS.register("guardians", () -> CreativeModeTab.builder()
            .title(Component.literal("Snapped Guardians"))
            .icon(() -> new ItemStack(RELICS.get(GuardianKind.UNWOVEN).get()))
            .displayItems((params, out) -> {
                for (GuardianKind k : GuardianKind.values()) out.accept(TOTEMS.get(k).get());
                for (GuardianKind k : GuardianKind.values()) out.accept(RELICS.get(k).get());
            }).build());

    public static ItemStack relic(GuardianKind k) { DeferredItem<RelicItem> r = RELICS.get(k); return r == null ? ItemStack.EMPTY : new ItemStack(r.get()); }
    public static Item totem(GuardianKind k) { return TOTEMS.get(k).get(); }
}
