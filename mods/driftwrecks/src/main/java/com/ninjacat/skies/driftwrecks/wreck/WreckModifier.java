package com.ninjacat.skies.driftwrecks.wreck;

import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;

import javax.annotation.Nullable;

/** Conditions on a wreck. Weights from the spec; Burning and Unstable only from Tier 2. Names: wreck.driftwrecks.modifier.&lt;id&gt;. */
public enum WreckModifier {
    UNMARKED("unmarked", 40, WreckTier.RAFT, 1.0F),
    OVERGROWN("overgrown", 15, WreckTier.RAFT, 1.0F),
    FROZEN("frozen", 15, WreckTier.RAFT, 1.0F),
    HAUNTED("haunted", 15, WreckTier.RAFT, 1.0F),
    BURNING("burning", 10, WreckTier.RUIN, 0.75F),
    UNSTABLE("unstable", 5, WreckTier.RUIN, 0.5F);

    public static final WreckModifier[] ALL = values();

    public final String id;
    public final int weight;
    public final WreckTier minTier;
    public final float lifetime;

    WreckModifier(String id, int weight, WreckTier minTier, float lifetime) {
        this.id = id; this.weight = weight; this.minTier = minTier; this.lifetime = lifetime;
    }

    public int bit() { return 1 << ordinal(); }

    /** The modifier's name ("Haunted"). */
    public MutableComponent title() { return Component.translatable("wreck.driftwrecks.modifier." + id + ".title"); }

    /** A label short enough for an Atlas stamp cell. */
    public MutableComponent shortTitle() { return Component.translatable("wreck.driftwrecks.modifier." + id + ".short"); }

    @Nullable
    public static WreckModifier byId(String id) {
        for (WreckModifier m : ALL) if (m.id.equals(id)) return m;
        return null;
    }
}
