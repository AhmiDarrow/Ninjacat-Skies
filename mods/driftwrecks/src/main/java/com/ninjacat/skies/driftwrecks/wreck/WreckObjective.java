package com.ninjacat.skies.driftwrecks.wreck;

import javax.annotation.Nullable;

/** What "done" means on a wreck. Looting without finishing still gives the ordinary chests. */
public enum WreckObjective {
    SALVAGE("salvage", "Salvage", "Open the wreck's heart chest.", 35, WreckTier.RAFT),
    CLEAR("clear", "Clear", "Break every frayed spawner.", 25, WreckTier.RAFT),
    RETHREAD("rethread", "Re-thread", "Light the thread pillars in the order the idol shows.", 20, WreckTier.RAFT),
    ESCORT("escort", "Escort", "Walk the Steward echo to your tether.", 10, WreckTier.RUIN),
    HOLD("hold", "Hold", "Hold the seam through three waves.", 10, WreckTier.RUIN);

    public static final WreckObjective[] ALL = values();

    public final String id;
    public final String title;
    public final String brief;
    public final int weight;
    public final WreckTier minTier;

    WreckObjective(String id, String title, String brief, int weight, WreckTier minTier) {
        this.id = id; this.title = title; this.brief = brief; this.weight = weight; this.minTier = minTier;
    }

    @Nullable
    public static WreckObjective byId(String id) {
        for (WreckObjective o : ALL) if (o.id.equals(id)) return o;
        return null;
    }
}
