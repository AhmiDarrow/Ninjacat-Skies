package com.ninjacat.skies.core.config;

import net.neoforged.neoforge.common.ModConfigSpec;

public final class SkiesConfig {
    public static final ModConfigSpec SPEC;

    public static final ModConfigSpec.BooleanValue GIVE_CODEX_ON_JOIN;
    public static final ModConfigSpec.BooleanValue HARDCORE_LIVES_ENABLED;
    public static final ModConfigSpec.IntValue STARTING_LIVES;
    public static final ModConfigSpec.ConfigValue<String> DIFFICULTY_PRESET;
    public static final ModConfigSpec.BooleanValue FRAY_ENABLED;
    public static final ModConfigSpec.IntValue FRAY_X;
    public static final ModConfigSpec.IntValue FRAY_Y;
    public static final ModConfigSpec.IntValue FRAY_Z;
    public static final ModConfigSpec.BooleanValue SKY_TINT;
    public static final ModConfigSpec.BooleanValue SUNDERED_SKY;
    public static final ModConfigSpec.IntValue SLEEP_PERCENTAGE;
    public static final ModConfigSpec.BooleanValue YARN_BASKET;
    public static final ModConfigSpec.BooleanValue SNEAK_DISMOUNTS;

    static {
        ModConfigSpec.Builder builder = new ModConfigSpec.Builder();

        builder.push("skybound");
        GIVE_CODEX_ON_JOIN = builder
                .comment("Give a Whisker Codex the first time a player joins a world.")   // lang-exempt: config file comment for server operators
                .define("giveCodexOnJoin", true);
        DIFFICULTY_PRESET = builder
                .comment("First-join kit extras only (wiped on pad claim). Real Easy/Normal/Hard = island template.")   // lang-exempt: config file comment for server operators
                .define("difficultyPreset", "normal");
        builder.pop();

        builder.push("loom");
        FRAY_ENABLED = builder
                .comment("Show the Fray: a slow dark column over the Dock that thins as Clowders seat Strands.")   // lang-exempt: config file comment for server operators
                .define("frayEnabled", true);
        FRAY_X = builder.comment("Fray column X (overworld).").defineInRange("frayX", 0, -30000000, 30000000);   // lang-exempt: config file comment for server operators
        FRAY_Y = builder.comment("Fray column base Y.").defineInRange("frayY", 66, -64, 320);   // lang-exempt: config file comment for server operators
        FRAY_Z = builder.comment("Fray column Z (overworld).").defineInRange("frayZ", 0, -30000000, 30000000);   // lang-exempt: config file comment for server operators
        SKY_TINT = builder
                .comment("Client: warm the horizon a little as your Clowder's Loom Tension rises.")   // lang-exempt: config file comment for server operators
                .define("skyTint", true);
        SUNDERED_SKY = builder
                .comment("Client: replace the Overworld sky with the sundered Loom (gold Cut, void tears). Disable for shader packs that draw their own sky.")   // lang-exempt: config file comment for server operators
                .define("sunderedSky", true);
        builder.pop();

        builder.push("hardcore");
        HARDCORE_LIVES_ENABLED = builder
                .comment("Shared Clowder lives. Every survival death spends one team life. Rare quest rewards add lives; operator /skybound revive restores the team.")   // lang-exempt: config file comment for server operators
                .define("livesEnabled", true);
        STARTING_LIVES = builder
                .comment("Lives contributed once by each member to the shared team pool; operator revive restores this count times current members.")   // lang-exempt: config file comment for server operators
                .defineInRange("startingLives", 3, 1, 99);
        YARN_BASKET = builder
                .comment("On death, gather a player's dropped items into a Yarn Basket where they fell (or where they last stood, after a fall into the void). Only the owner, their Clowder or a creative player can open it.")   // lang-exempt: config file comment for server operators
                .define("yarnBasket", true);
        builder.pop();

        builder.push("sleep");
        SLEEP_PERCENTAGE = builder
                .comment("Share of a dimension's online players who must sleep to pass the night there. Written to the playersSleepingPercentage gamerule on every server start. -1 leaves the gamerule alone.")   // lang-exempt: config file comment for server operators
                .defineInRange("playersSleepingPercentage", 25, -1, 100);
        builder.pop();

        builder.push("controls");
        SNEAK_DISMOUNTS = builder
                .comment("Vanilla sneak-to-dismount. Off: sneak only steers what you ride (a chocobo descends) and the Dismount key (Caps Lock by default) gets you off.")   // lang-exempt: config file comment for server operators
                .define("sneakDismounts", false);
        builder.pop();

        SPEC = builder.build();
    }

    private SkiesConfig() {}
}
