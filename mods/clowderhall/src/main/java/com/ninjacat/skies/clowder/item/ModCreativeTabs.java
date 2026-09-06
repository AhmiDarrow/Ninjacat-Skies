package com.ninjacat.skies.clowder.item;

import com.ninjacat.skies.clowder.ClowderHall;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ClowderHall.MOD_ID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN = TABS.register("main", () ->
            CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.clowderhall"))
                    .withTabsBefore(CreativeModeTabs.SPAWN_EGGS)
                    .icon(() -> ModItems.ISLAND_CHARTER.get().getDefaultInstance())
                    .displayItems((params, out) -> {
                        out.accept(ModItems.ISLAND_CHARTER.get());
                        out.accept(ModItems.HUB_KEY.get());
                        out.accept(ModItems.STRAND_BANNER_PATTERN.get());
                    })
                    .build()
    );

    private ModCreativeTabs() {}
}
