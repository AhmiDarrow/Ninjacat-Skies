package com.ninjacat.skies.driftwrecks.wreck;

import javax.annotation.Nullable;

/** Tier comes from tensioned Strands, never item count or playtime. Lifetime counts Clowder online time only. */
public enum WreckTier {
    RAFT("raft", "Raft", 1, 20 * 60 * 20, 15),
    RUIN("ruin", "Ruin", 4, 40 * 60 * 20, 31),
    HOLD("hold", "Hold", 7, 60 * 60 * 20, 48);

    public static final WreckTier[] ALL = values();

    public final String id;
    public final String title;
    /** Strands a Clowder must have tensioned before this tier can drift in. */
    public final int strandsNeeded;
    public final int lifetimeTicks;
    /** Largest horizontal footprint of any plan at this tier. */
    public final int maxSize;

    WreckTier(String id, String title, int strandsNeeded, int lifetimeTicks, int maxSize) {
        this.id = id; this.title = title; this.strandsNeeded = strandsNeeded; this.lifetimeTicks = lifetimeTicks; this.maxSize = maxSize;
    }

    public int level() { return ordinal() + 1; }

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
