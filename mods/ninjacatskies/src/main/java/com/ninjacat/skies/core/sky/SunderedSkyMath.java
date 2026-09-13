package com.ninjacat.skies.core.sky;

/** Pure sundered-sky numbers: the Cut in the Loom, healing as Tension rises. */
public final class SunderedSkyMath {
    private SunderedSkyMath() {}

    /** 1 at noon, 0 at midnight. */
    public static float dayness(long dayTime, float partial) {
        double time = (Math.floorMod(dayTime, 24000) + Math.clamp(partial, 0F, 1F)) / 24000.0;
        return (float) Math.clamp((Math.sin(time * Math.PI * 2) + 0.2) / 1.15, 0, 1);
    }

    /** 0 = fully sundered, 1 = rewoven. */
    public static float heal(int seatedStrands, boolean rewoven) {
        float t = Math.clamp(seatedStrands / 9.0F, 0F, 1F);
        if (rewoven) {
            t = 1F;
        }
        return t;
    }

    /** Angular half-width of the Cut. Wide when the Loom is torn, a seam when rewoven. */
    public static float cutHalfWidth(float heal) {
        return lerp(heal, 0.22F, 0.035F);
    }

    public static float[] zenith(float dayness, float heal, float rain) {
        float r = lerp(dayness, 0.04F, 0.22F);
        float g = lerp(dayness, 0.05F, 0.28F);
        float b = lerp(dayness, 0.08F, 0.32F);
        r = lerp(heal, r, lerp(dayness, 0.06F, 0.20F));
        g = lerp(heal, g, lerp(dayness, 0.10F, 0.42F));
        b = lerp(heal, b, lerp(dayness, 0.14F, 0.48F));
        return dim(r, g, b, rain);
    }

    public static float[] horizon(float dayness, float heal, float rain) {
        float r = lerp(dayness, 0.16F, 0.55F);
        float g = lerp(dayness, 0.10F, 0.38F);
        float b = lerp(dayness, 0.08F, 0.22F);
        r = lerp(heal, r, lerp(dayness, 0.22F, 0.48F));
        g = lerp(heal, g, lerp(dayness, 0.18F, 0.56F));
        b = lerp(heal, b, lerp(dayness, 0.16F, 0.44F));
        return dim(r, g, b, rain);
    }

    public static float[] nadir(float dayness, float heal, float rain) {
        float r = lerp(heal, 0.03F, 0.06F);
        float g = lerp(heal, 0.02F, 0.08F);
        float b = lerp(heal, 0.04F, 0.12F);
        r += dayness * 0.02F;
        return dim(r, g, b, rain);
    }

    public static float[] cutCore(float heal) {
        float a = lerp(heal, 0.92F, 0.55F);
        return new float[] { 0.02F, 0.02F, 0.04F, a };
    }

    public static float[] cutGold(float heal, float dayness) {
        float a = lerp(heal, 0.85F, 0.40F);
        float r = lerp(dayness, 0.78F, 0.92F);
        float g = lerp(dayness, 0.52F, 0.72F);
        float b = lerp(heal, 0.18F, 0.42F);
        return new float[] { r, g, b, a };
    }

    public static float sunAlpha(float dayness, float rain) {
        return dayness * (1F - Math.clamp(rain, 0F, 1F) * 0.65F);
    }

    public static float moonAlpha(float dayness, float rain) {
        return (1F - dayness) * (1F - Math.clamp(rain, 0F, 1F) * 0.45F);
    }

    /** Distance of a unit sky direction to the Cut plane. */
    public static float cutDistance(float x, float y, float z) {
        // Plane facing roughly NW–SE so pads look into the seam.
        float nx = 0.62F, ny = 0.18F, nz = 0.76F;
        return Math.abs(x * nx + y * ny + z * nz);
    }

    private static float[] dim(float r, float g, float b, float rain) {
        float d = 1F - Math.clamp(rain, 0F, 1F) * 0.4F;
        return new float[] { r * d, g * d, b * d };
    }

    private static float lerp(float t, float a, float b) {
        return a + Math.clamp(t, 0F, 1F) * (b - a);
    }
}
