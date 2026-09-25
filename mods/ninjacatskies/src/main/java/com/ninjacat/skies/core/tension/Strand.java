package com.ninjacat.skies.core.tension;

import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.resources.ResourceLocation;

import javax.annotation.Nullable;

/**
 * The nine Strands of the Loom. Order is canon (Wake → Reweave); bit index is used for team flags.
 * Steward lines are the tribes speaking from the cut — two per Strand, always ending on a verb; the text lives
 * in the lang file under message.ninjacatskies.strand.<id>.line_a / line_b. The Strand's name and its tribe's name are
 * lang keys too (strand.ninjacatskies.<id>.title / .tribe).
 */
public enum Strand {
    SOIL("soil", "Pad-keepers", 0x6B8E3A, 0.70F),
    STONE("stone", "Grit-singers", 0x8A8580, 0.80F),
    SPROUT("sprout", "Rootbinders", 0x5AAF5A, 0.90F),
    CLAW("claw", "Edge-walkers", 0x8C8C96, 1.00F),
    SPARK("spark", "Drumhearts", 0xD4A84B, 1.10F),
    CLOCK("clock", "Pattern-weavers", 0xC87A3A, 1.20F),
    SWARM("swarm", "Colony-keepers", 0xE6C478, 1.30F),
    SIGIL("sigil", "Seal-carvers", 0x8A5FB8, 1.45F),
    SPINDLE("spindle", "Loom-stitchers", 0x3D7A7A, 1.60F);

    public static final Strand[] ALL = values();

    private final String id;
    /** The tribe's English name as it was written into Codex page names before they were translatable; matching only. */
    private final String legacyTribe;
    private final int color;
    private final float chimePitch;

    Strand(String id, String legacyTribe, int color, float chimePitch) {
        this.id = id;
        this.legacyTribe = legacyTribe;
        this.color = color;
        this.chimePitch = chimePitch;
    }

    public String id() {
        return id;
    }

    public String tribeKey() {
        return "strand.ninjacatskies." + id + ".tribe";
    }

    /** The tribe that kept this Strand ("Pad-keepers"). */
    public MutableComponent tribe() {
        return Component.translatable(tribeKey());
    }

    /** True if a Codex page name written before translation (English tribe string) names this Strand's tribe. */
    public boolean legacyTribeIn(String text) {
        return text.contains(legacyTribe);
    }

    public int color() {
        return color;
    }

    public float chimePitch() {
        return chimePitch;
    }

    public String lineAKey() {
        return "message.ninjacatskies.strand." + id + ".line_a";
    }

    public String lineBKey() {
        return "message.ninjacatskies.strand." + id + ".line_b";
    }

    public int bit() {
        return 1 << ordinal();
    }

    public String titleKey() {
        return "strand.ninjacatskies." + id + ".title";
    }

    /** The Strand's name ("Soil"). */
    public MutableComponent title() {
        return Component.translatable(titleKey());
    }

    public ResourceLocation tokenId() {
        return ResourceLocation.fromNamespaceAndPath("ninjacatskies", "strand_token_" + id);
    }

    public ResourceLocation advancementId() {
        return ResourceLocation.fromNamespaceAndPath("ninjacatskies", "strand/" + id);
    }

    public boolean isBraid() {
        return this == CLOCK || this == SWARM || this == SPARK;
    }

    @Nullable
    public static Strand byId(String id) {
        for (Strand s : ALL) {
            if (s.id.equals(id)) {
                return s;
            }
        }
        return null;
    }

    @Nullable
    public static Strand byToken(ResourceLocation itemId) {
        if (!"ninjacatskies".equals(itemId.getNamespace()) || !itemId.getPath().startsWith("strand_token_")) {
            return null;
        }
        return byId(itemId.getPath().substring("strand_token_".length()));
    }
}
