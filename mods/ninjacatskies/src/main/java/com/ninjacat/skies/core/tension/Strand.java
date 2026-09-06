package com.ninjacat.skies.core.tension;

import net.minecraft.resources.ResourceLocation;

import javax.annotation.Nullable;

/**
 * The nine Strands of the Loom. Order is canon (Wake → Reweave); bit index is used for team flags.
 * Steward lines are the tribes speaking from the cut — two per Strand, always ending on a verb.
 */
public enum Strand {
    SOIL("soil", "Pad-keepers", 0x6B8E3A, 0.70F,
            "Soil answers. Pad-keepers banked hearth-warmth in dirt this thin, and it held.",
            "Claim the pad. Cache what grows. Wake slowly; the void is patient."),
    STONE("stone", "Grit-singers", 0x8A8580, 0.80F,
            "Stone hums under the mesh. Grit-singers named every shard by its echo.",
            "Shatter grit. Knot yarn. Recover what the cut scattered."),
    SPROUT("sprout", "Rootbinders", 0x5AAF5A, 0.90F,
            "Sprout takes hold. Rootbinders grew living anchors where pads would have drifted.",
            "Feed the Clowder before you feed the forge. Root, then wander."),
    CLAW("claw", "Edge-walkers", 0x8C8C96, 1.00F,
            "Claw finds the rim. Edge-walkers kept footholds past the last fence post.",
            "Kit up. Step off the pad on purpose, never by accident."),
    SPARK("spark", "Drumhearts", 0xD4A84B, 1.10F,
            "Spark wakes a pulse. Drumhearts kept the beat under the whole sky.",
            "Strike a drum and listen before you wire anything."),
    CLOCK("clock", "Pattern-weavers", 0xC87A3A, 1.20F,
            "Clock repeats. Pattern-weavers sang a factory the way you'd sing a round.",
            "One cog, then the same cog again. Let the pattern carry the work."),
    SWARM("swarm", "Colony-keepers", 0xE6C478, 1.30F,
            "Swarm thickens. Colony-keepers tended hives that hummed in the Loom's own key.",
            "Keep something alive that keeps something else alive. That is industry."),
    SIGIL("sigil", "Seal-carvers", 0x8A5FB8, 1.45F,
            "Sigil bites. Seal-carvers pressed spirit into matter and made it stay.",
            "Carve carefully. A seal is a promise the world has to keep."),
    SPINDLE("spindle", "Loom-stitchers", 0x3D7A7A, 1.60F,
            "Spindle draws taut. Loom-stitchers cut the gate-paths and always meant to come back.",
            "Stitch the cut. Then go and see what the March kept for you.");

    public static final Strand[] ALL = values();
    public static final Strand[] BRAID = {CLOCK, SWARM, SPARK};

    private final String id;
    private final String tribe;
    private final int color;
    private final float chimePitch;
    private final String lineA;
    private final String lineB;

    Strand(String id, String tribe, int color, float chimePitch, String lineA, String lineB) {
        this.id = id;
        this.tribe = tribe;
        this.color = color;
        this.chimePitch = chimePitch;
        this.lineA = lineA;
        this.lineB = lineB;
    }

    public String id() {
        return id;
    }

    public String tribe() {
        return tribe;
    }

    public int color() {
        return color;
    }

    public float chimePitch() {
        return chimePitch;
    }

    public String lineA() {
        return lineA;
    }

    public String lineB() {
        return lineB;
    }

    public int bit() {
        return 1 << ordinal();
    }

    public String title() {
        return Character.toUpperCase(id.charAt(0)) + id.substring(1);
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
