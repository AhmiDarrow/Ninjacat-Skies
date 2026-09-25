package com.ninjacat.skies.driftwrecks.wreck;

import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;

import javax.annotation.Nullable;

/** Tier comes from tensioned Strands, never item count or playtime. Lifetime counts Clowder online time only. */
public enum WreckTier {
    RAFT("raft", 1, 20 * 60 * 20, 19),
    RUIN("ruin", 4, 40 * 60 * 20, 35),
    HOLD("hold", 7, 60 * 60 * 20, 53);

    public static final WreckTier[] ALL = values();

    public final String id;
    /** Strands a Clowder must have tensioned before this tier can drift in. */
    public final int strandsNeeded;
    public final int lifetimeTicks;
    /** Largest horizontal footprint of a composed wreck at this tier (core, annexes and islets). */
    public final int maxSize;

    WreckTier(String id, int strandsNeeded, int lifetimeTicks, int maxSize) {
        this.id = id; this.strandsNeeded = strandsNeeded; this.lifetimeTicks = lifetimeTicks; this.maxSize = maxSize;
    }

    public int level() { return ordinal() + 1; }

    /** The tier's name ("Raft"); wreck.driftwrecks.tier.<id>.title. */
    public MutableComponent title() { return Component.translatable("wreck.driftwrecks.tier." + id + ".title"); }

    @Nullable
    public static WreckTier byId(String id) {
        for (WreckTier t : ALL) if (t.id.equals(id)) return t;
        return null;
    }

    /** Highest tier this many tensioned Strands opens, or null before Soil. */
    @Nullable
    public static WreckTier highestFor(int strands) {
        WreckTier best = null;
        for (WreckTier t : ALL) if (strands >= t.strandsNeeded) best = t;
        return best;
    }
}
