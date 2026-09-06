package com.ninjacat.skies.core.config;

import net.neoforged.neoforge.common.ModConfigSpec;

public final class SkiesConfig {
    public static final ModConfigSpec SPEC;

    public static final ModConfigSpec.BooleanValue GIVE_CODEX_ON_JOIN;
    public static final ModConfigSpec.BooleanValue HARDCORE_LIVES_ENABLED;
    public static final ModConfigSpec.IntValue STARTING_LIVES;
    public static final ModConfigSpec.ConfigValue<String> DIFFICULTY_PRESET;

    static {
        ModConfigSpec.Builder builder = new ModConfigSpec.Builder();

        builder.push("skybound");
        GIVE_CODEX_ON_JOIN = builder
                .comment("Give a Whisker Codex the first time a player joins a world.")
                .define("giveCodexOnJoin", true);
        DIFFICULTY_PRESET = builder
                .comment("First-join kit extras only (wiped on pad claim). Real Easy/Normal/Hard = island template.")
                .define("difficultyPreset", "normal");
        builder.pop();

        builder.push("hardcore");
        HARDCORE_LIVES_ENABLED = builder
                .comment("Optional soft hardcore. Default off. /clowder revive (self) or <player> mate. Ops: /skybound revive [player]")
                .define("livesEnabled", false);
        STARTING_LIVES = builder
                .comment("Starting lives when hardcore lives are enabled (also restore count on revive).")
                .defineInRange("startingLives", 3, 1, 99);
        builder.pop();

        SPEC = builder.build();
    }

    private SkiesConfig() {}
}
