package com.ninjacat.skies.driftwrecks.wreck;

import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;

import javax.annotation.Nullable;

/**
 * What "done" means on a wreck. Looting without finishing still gives the ordinary chests.
 * Name and one-line brief: wreck.driftwrecks.objective.&lt;id&gt;.title / .brief.
 */
public enum WreckObjective {
    SALVAGE("salvage", 35, WreckTier.RAFT),
    CLEAR("clear", 25, WreckTier.RAFT),
    RETHREAD("rethread", 20, WreckTier.RAFT),
    ESCORT("escort", 10, WreckTier.RUIN),
    HOLD("hold", 10, WreckTier.RUIN);

    public static final WreckObjective[] ALL = values();

    public final String id;
    public final int weight;
    public final WreckTier minTier;

    WreckObjective(String id, int weight, WreckTier minTier) {
        this.id = id; this.weight = weight; this.minTier = minTier;
    }

    /** The objective's name ("Re-thread"). */
    public MutableComponent title() { return Component.translatable("wreck.driftwrecks.objective." + id + ".title"); }

    /** What to do, as one sentence. */
    public MutableComponent brief() { return Component.translatable("wreck.driftwrecks.objective." + id + ".brief"); }

    @Nullable
    public static WreckObjective byId(String id) {
        for (WreckObjective o : ALL) if (o.id.equals(id)) return o;
        return null;
    }
}
