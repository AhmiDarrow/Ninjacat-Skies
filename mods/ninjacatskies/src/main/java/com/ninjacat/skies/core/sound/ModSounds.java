package com.ninjacat.skies.core.sound;

import com.ninjacat.skies.core.NinjacatSkies;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(Registries.SOUND_EVENT, NinjacatSkies.MOD_ID);

    /** Loom-shuttle-and-bell stinger; pitched per Strand. */
    public static final DeferredHolder<SoundEvent, SoundEvent> STRAND_CHIME = register("strand_chime");
    /** Wooden knock as a token seats in the Post. */
    public static final DeferredHolder<SoundEvent, SoundEvent> POST_SEAT = register("post_seat");
    /** Low looped hum near a Post with Strands seated. */
    public static final DeferredHolder<SoundEvent, SoundEvent> LOOM_HUM = register("loom_hum");
    /** The Reweave. */
    public static final DeferredHolder<SoundEvent, SoundEvent> REWEAVE = register("reweave");
    /** Codex page turn. */
    public static final DeferredHolder<SoundEvent, SoundEvent> PAGE = register("page");

    private static DeferredHolder<SoundEvent, SoundEvent> register(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(ResourceLocation.fromNamespaceAndPath(NinjacatSkies.MOD_ID, name)));
    }

    private ModSounds() {}
}
