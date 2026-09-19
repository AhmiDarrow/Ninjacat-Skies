package com.ninjacat.skies.driftwrecks;

import net.neoforged.neoforge.common.ModConfigSpec;

/** driftwrecks-server.toml: switches and pacing for server owners. */
public final class DriftConfig {
    public static final ModConfigSpec SPEC;
    public static final ModConfigSpec.BooleanValue ENABLED;
    public static final ModConfigSpec.IntValue PRESSURE_MIN_MINUTES;
    public static final ModConfigSpec.IntValue PRESSURE_MAX_MINUTES;
    public static final ModConfigSpec.IntValue LURE_COOLDOWN_MINUTES;
    public static final ModConfigSpec.IntValue BLOCKS_PER_TICK;
    public static final ModConfigSpec.IntValue MIN_DISTANCE;
    public static final ModConfigSpec.IntValue MAX_DISTANCE;
    public static final ModConfigSpec.IntValue NEIGHBOUR_DISTANCE;
    public static final ModConfigSpec.DoubleValue LIFETIME_MULTIPLIER;
    public static final ModConfigSpec.BooleanValue FINISH_UNLOADED;

    static {
        ModConfigSpec.Builder b = new ModConfigSpec.Builder();
        b.push("driftwrecks");
        ENABLED = b.comment("Turn Driftwrecks on. Turning it off unravels active wrecks cleanly on the next tick.").define("enabled", true);
        PRESSURE_MIN_MINUTES = b.comment("Drift pressure fills in this many minutes of Clowder online time, at least...").defineInRange("pressureMinMinutes", 90, 1, 1440);
        PRESSURE_MAX_MINUTES = b.comment("...and at most (a new random target each cycle).").defineInRange("pressureMaxMinutes", 120, 1, 1440);
        LURE_COOLDOWN_MINUTES = b.comment("Minutes a Clowder waits between Driftlures.").defineInRange("lureCooldownMinutes", 30, 0, 1440);
        BLOCKS_PER_TICK = b.comment("Most blocks a wreck places or removes per server tick.").defineInRange("blocksPerTick", 2000, 50, 20000);
        MIN_DISTANCE = b.comment("Closest a wreck arrives to the Tension Post, in blocks.").defineInRange("minDistance", 160, 48, 2000);
        MAX_DISTANCE = b.comment("Farthest a wreck arrives from the Tension Post, in blocks.").defineInRange("maxDistance", 320, 64, 2000);
        NEIGHBOUR_DISTANCE = b.comment("A wreck never lands closer than this to another Clowder's Tension Post (half the island spacing).").defineInRange("neighbourDistance", 2048, 0, 100000);
        LIFETIME_MULTIPLIER = b.comment("Scales every wreck's lifetime.").defineInRange("lifetimeMultiplier", 1.0, 0.1, 10.0);
        FINISH_UNLOADED = b.comment("Load a wreck's chunks briefly to finish unravelling it at expiry, instead of waiting for them to load.").define("finishUnloaded", true);
        b.pop();
        SPEC = b.build();
    }

    private DriftConfig() {}
}
