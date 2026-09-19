package com.ninjacat.skies.driftwrecks.registry;

import com.mojang.serialization.Codec;
import com.ninjacat.skies.driftwrecks.Driftwrecks;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.codec.ByteBufCodecs;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/** Item data: which Strand a lure/key/banner is for, which core a hint page names. */
public final class DwComponents {
    public static final DeferredRegister.DataComponents COMPONENTS = DeferredRegister.createDataComponents(Registries.DATA_COMPONENT_TYPE, Driftwrecks.MOD_ID);

    public static final DeferredHolder<DataComponentType<?>, DataComponentType<String>> STRAND = COMPONENTS.registerComponentType("strand",
            b -> b.persistent(Codec.STRING).networkSynchronized(ByteBufCodecs.STRING_UTF8));
    public static final DeferredHolder<DataComponentType<?>, DataComponentType<String>> CORE = COMPONENTS.registerComponentType("core",
            b -> b.persistent(Codec.STRING).networkSynchronized(ByteBufCodecs.STRING_UTF8));
    /** A Salvage Bundle's owner name, shown in its tooltip. */
    public static final DeferredHolder<DataComponentType<?>, DataComponentType<String>> OWNER = COMPONENTS.registerComponentType("owner",
            b -> b.persistent(Codec.STRING).networkSynchronized(ByteBufCodecs.STRING_UTF8));

    private DwComponents() {}
}
