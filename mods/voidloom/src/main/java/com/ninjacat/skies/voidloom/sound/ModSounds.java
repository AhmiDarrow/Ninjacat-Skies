package com.ninjacat.skies.voidloom.sound;

import com.ninjacat.skies.voidloom.Voidloom;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(Registries.SOUND_EVENT, Voidloom.MOD_ID);

    /** Shuttle clack as the Loomframe works a piece of grit. */
    public static final DeferredHolder<SoundEvent, SoundEvent> LOOMFRAME_SIFT = register("loomframe_sift");
    /** Wet wooden thunk as the Tension Barrel finishes a piece. */
    public static final DeferredHolder<SoundEvent, SoundEvent> BARREL_SETTLE = register("barrel_settle");

    private static DeferredHolder<SoundEvent, SoundEvent> register(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(ResourceLocation.fromNamespaceAndPath(Voidloom.MOD_ID, name)));
    }

    private ModSounds() {}
}
