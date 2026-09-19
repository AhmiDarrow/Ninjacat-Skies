package com.ninjacat.skies.driftwrecks.wreck;

import javax.annotation.Nullable;

/** The layout of a wreck. Each core has one plan per tier (data/driftwrecks/wreck/&lt;core&gt;_&lt;tier&gt;.ncga). */
public enum WreckCore {
    SHRINE("shrine", "Shrine", "The shrine-tenders kept the best offering under the stone they knelt on."),
    WATCHTOWER("watchtower", "Watchtower", "Three landings up, the watch kept a room nobody climbed to."),
    LIBRARY("library", "Library", "One shelf in every library was never meant to be read."),
    FORGE("forge", "Forge", "The forge-keepers kept their best work where the hammer fell."),
    GARDEN("garden", "Garden", "The gardeners buried what they loved under the water they gave it."),
    VAULT("vault", "Vault", "A vault with one wall is a door. A vault with two is a promise.");

    public static final WreckCore[] ALL = values();

    public final String id;
    public final String title;
    /** The Codex hint page line; points at the hidden room without naming it. */
    public final String hint;

    WreckCore(String id, String title, String hint) { this.id = id; this.title = title; this.hint = hint; }

    public int bit() { return 1 << ordinal(); }

    @Nullable
    public static WreckCore byId(String id) {
        for (WreckCore c : ALL) if (c.id.equals(id)) return c;
        return null;
    }
}
