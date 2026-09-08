package com.ninjacat.skies.core.item;

import com.ninjacat.skies.core.NinjacatSkies;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, NinjacatSkies.MOD_ID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN = TABS.register("main", () ->
            CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.ninjacatskies"))
                    .withTabsBefore(CreativeModeTabs.SPAWN_EGGS)
                    .icon(() -> ModItems.WHISKER_CODEX.get().getDefaultInstance())
                    .displayItems((params, out) -> {
                        out.accept(ModItems.WHISKER_CODEX.get());
                        out.accept(ModItems.FRAYED_THREAD.get());
                        out.accept(ModItems.SMALL_STEWARD_CACHE.get());
                        out.accept(ModItems.MEDIUM_STEWARD_CACHE.get());
                        out.accept(ModItems.LARGE_STEWARD_CACHE.get());
                        out.accept(ModItems.CODEX_PAGE.get());
                        out.accept(ModItems.STRAND_TOKEN_SOIL.get());
                        out.accept(ModItems.STRAND_TOKEN_STONE.get());
                        out.accept(ModItems.STRAND_TOKEN_SPROUT.get());
                        out.accept(ModItems.STRAND_TOKEN_CLAW.get());
                        out.accept(ModItems.STRAND_TOKEN_SPARK.get());
                        out.accept(ModItems.STRAND_TOKEN_CLOCK.get());
                        out.accept(ModItems.STRAND_TOKEN_SWARM.get());
                        out.accept(ModItems.STRAND_TOKEN_SIGIL.get());
                        out.accept(ModItems.STRAND_TOKEN_SPINDLE.get());
                        out.accept(ModItems.BRAID_CORD.get());
                        out.accept(ModItems.SPINDLE_LOOM_FRAGMENT.get());
                        out.accept(ModItems.TENSION_POST.get());
                    })
                    .build()
    );

    private ModCreativeTabs() {}
}
