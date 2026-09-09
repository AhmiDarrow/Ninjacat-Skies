package com.ninjacat.skies.guardians;

import com.ninjacat.skies.core.tension.Strand;
import net.minecraft.resources.ResourceLocation;

import javax.annotation.Nullable;

/**
 * The thirteen Snapped Guardians. Ids match the boss art pipeline: the model file is
 * assets/guardians/guardian/<id>.ncgb (+ <id>.png, <id>_emit.png) and the block plan is data/guardians/arena/<id>.ncga.
 */
public enum GuardianKind {
    // ---- the nine Strand gates (progression order)
    BEDDOWN("beddown", "the Beddown", Strand.SOIL, "rootheart", 12.7F, 10.0F, 320, 12, 0x6B8E3A, Tier.GATE),
    GRINDMAW("grindmaw", "the Grindmaw", Strand.STONE, "grindcore", 12.9F, 9.0F, 380, 14, 0x8A8580, Tier.GATE),
    THORNMOTHER("thornmother", "the Thornmother", Strand.SPROUT, "thornseed", 12.5F, 9.0F, 360, 10, 0x5AAF5A, Tier.GATE),
    EDGEWALKER("edgewalker", "the Edgewalker", Strand.CLAW, "edgestep", 7.5F, 9.0F, 300, 16, 0x8C8C96, Tier.GATE),
    DRUMHEART("drumheart", "the Drumheart", Strand.SPARK, "drumpulse", 13.0F, 9.0F, 420, 15, 0xD4A84B, Tier.GATE),
    COGWRIGHT("cogwright", "the Cogwright", Strand.CLOCK, "cogloop", 9.5F, 12.0F, 440, 14, 0xC87A3A, Tier.GATE),
    HIVEMIND("hivemind", "the Hivemind", Strand.SWARM, "hivecall", 13.0F, 7.0F, 300, 10, 0xE6C478, Tier.GATE),
    SEALBREAKER("sealbreaker", "the Sealbreaker", Strand.SIGIL, "sealmark", 13.5F, 8.0F, 460, 16, 0x8A5FB8, Tier.GATE),
    UNWOVEN("unwoven", "the Unwoven", Strand.SPINDLE, "loomthread", 13.5F, 9.0F, 600, 18, 0x3D7A7A, Tier.GATE),
    // ---- the two easy
    LINTGOLEM("lintgolem", "the Lint Golem", null, "lintwisp", 6.0F, 5.0F, 80, 3, 0xB8B4BC, Tier.EASY),
    TANGLE("tangle", "the Tangle", null, "knotcharm", 7.0F, 10.0F, 160, 8, 0xC9A45C, Tier.EASY),
    // ---- the two insane (locked until after the Reweave)
    FIRSTCUT("firstcut", "the First Cut", null, "firstcut_shard", 32.0F, 16.0F, 1800, 30, 0x2A1838, Tier.INSANE),
    OVERWEAVER("overweaver", "the Overweaver", null, "overweaver_shuttle", 40.0F, 22.0F, 2400, 26, 0x6C4FB0, Tier.INSANE);

    public enum Tier { GATE, EASY, INSANE }

    public final String id;
    public final String title;
    @Nullable public final Strand strand;
    public final String relicId;
    public final float height, width;
    public final int baseHealth, attackDamage, colour;
    public final Tier tier;

    GuardianKind(String id, String title, @Nullable Strand strand, String relicId, float height, float width, int baseHealth, int attackDamage, int colour, Tier tier) {
        this.id = id; this.title = title; this.strand = strand; this.relicId = relicId; this.height = height; this.width = width;
        this.baseHealth = baseHealth; this.attackDamage = attackDamage; this.colour = colour; this.tier = tier;
    }

    public ResourceLocation modelFile() { return ResourceLocation.fromNamespaceAndPath(Guardians.MOD_ID, "guardian/" + id + ".ncgb"); }
    public ResourceLocation texture() { return ResourceLocation.fromNamespaceAndPath(Guardians.MOD_ID, "textures/guardian/" + id + ".png"); }
    public ResourceLocation emissive() { return ResourceLocation.fromNamespaceAndPath(Guardians.MOD_ID, "textures/guardian/" + id + "_emit.png"); }
    public ResourceLocation arenaFile() { return ResourceLocation.fromNamespaceAndPath(Guardians.MOD_ID, "arena/" + id + ".ncga"); }
    public String totemId() { return "frayed_totem_" + id; }
    public String relicItemId() { return "relic_" + relicId; }

    @Nullable
    public static GuardianKind byId(String id) {
        for (GuardianKind k : values()) if (k.id.equals(id)) return k;
        return null;
    }
}
