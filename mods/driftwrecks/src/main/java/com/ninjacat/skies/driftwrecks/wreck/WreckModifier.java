package com.ninjacat.skies.driftwrecks.wreck;

import javax.annotation.Nullable;

/** Conditions on a wreck. Weights from the spec; Burning and Unstable only from Tier 2. */
public enum WreckModifier {
    UNMARKED("unmarked", "Unmarked", 40, WreckTier.RAFT, 1.0F),
    OVERGROWN("overgrown", "Overgrown", 15, WreckTier.RAFT, 1.0F),
    FROZEN("frozen", "Frozen", 15, WreckTier.RAFT, 1.0F),
    HAUNTED("haunted", "Haunted", 15, WreckTier.RAFT, 1.0F),
    BURNING("burning", "Burning", 10, WreckTier.RUIN, 0.75F),
    UNSTABLE("unstable", "Unstable", 5, WreckTier.RUIN, 0.5F);

    public static final WreckModifier[] ALL = values();

    public final String id;
    public final String title;
    public final int weight;
    public final WreckTier minTier;
    public final float lifetime;

    WreckModifier(String id, String title, int weight, WreckTier minTier, float lifetime) {
        this.id = id; this.title = title; this.weight = weight; this.minTier = minTier; this.lifetime = lifetime;
    }

    public int bit() { return 1 << ordinal(); }

    @Nullable
    public static WreckModifier byId(String id) {
        for (WreckModifier m : ALL) if (m.id.equals(id)) return m;
        return null;
    }
}
