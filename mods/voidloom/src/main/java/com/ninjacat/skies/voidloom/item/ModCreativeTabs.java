package com.ninjacat.skies.voidloom.item;

import com.ninjacat.skies.voidloom.Voidloom;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Voidloom.MOD_ID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN = TABS.register("main", () ->
            CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.voidloom"))
                    .withTabsBefore(CreativeModeTabs.SPAWN_EGGS)
                    .icon(() -> ModItems.VOID_YARN.get().getDefaultInstance())
                    .displayItems((params, out) -> {
                        out.accept(ModItems.VOID_YARN.get());
                        out.accept(ModItems.BINDING_KNOT.get());
                        out.accept(ModItems.THREAD_MESH_STRING.get());
                        out.accept(ModItems.THREAD_MESH_FLINT.get());
                        out.accept(ModItems.THREAD_MESH_IRON.get());
                        out.accept(ModItems.LOOM_LINT.get());
                        out.accept(ModItems.STRAND_FILAMENT.get());
                        out.accept(ModItems.SPINDLE_HAMMER.get());
                        out.accept(ModItems.SPINDLE_CROOK.get());
                        out.accept(ModItems.LOOMFRAME.get());
                        out.accept(ModItems.TENSION_BARREL.get());
                    })
                    .build()
    );

    private ModCreativeTabs() {}
}
