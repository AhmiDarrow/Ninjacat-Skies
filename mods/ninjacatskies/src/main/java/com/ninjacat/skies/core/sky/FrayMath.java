package com.ninjacat.skies.core.sky;

/**
 * Pure numbers for the Fray: the cut at Loom's End, past the broken end of the gate-path. It comes up out of the
 * bottom of the void, far below the world, rises past the town and frays on into the sky: nine loose threads
 * gathered at their root in the deep and splaying as they climb. They gather one by one as the server reweaves,
 * until only the spine is left, and that turns to lit thread once every Clowder online has closed theirs. Positions
 * along the cut are t in 0..1: 0 the root in the void, DOCK the ground the cut passes, 1 the top in the sky. No client
 * classes, so the GameTests can read it.
 */
public final class FrayMath {
    /** Threads in the cut: the spine plus one per Strand still open. */
    public static final int STRANDS = 9;
    /** How far below the ground the cut is rooted: through the bottom of the world and on into the void, in blocks. */
    public static final float BELOW = 260F;
    /** How far above the ground the cut frays into the sky, in blocks. */
    public static final float ABOVE = 200F;
    /** The whole cut, root to top, in blocks. */
    public static final float SPAN = BELOW + ABOVE;
    /** Where the ground (the gate-path's level) sits along the cut, 0 root .. 1 top. */
    public static final float DOCK = BELOW / SPAN;
    /** Segments a thread is drawn in, root to top. */
    public static final int SEGMENTS = 48;

    private FrayMath() {}

    /** 1 = the cut is fully open, 0 = every Clowder online has rewoven. */
    public static float torn(float progress) {
        return 1F - clamp(progress);
    }

    /** Server truth: the lit thread appears only once the server has fully rewoven. */
    public static boolean lit(float progress) {
        return progress >= 0.999F;
    }

    /** 0 dark, 1 lit; ramps over the last few percent so an eased client value turns the spine gold smoothly. */
    public static float glow(float progress) {
        float g = clamp((clamp(progress) - 0.95F) / 0.05F);
        return g * g * (3F - 2F * g);
    }

    /**
     * How much of thread k hangs in the sky. The spine (0) always does; the others fade out one at a time, outermost
     * first, as the server closes its Strands.
     */
    public static float strandAlpha(int k, float progress) {
        if (k <= 0) {
            return 1F;
        }
        return clamp(torn(progress) * (STRANDS - 1) - (k - 1));
    }

    /**
     * Horizontal offset (dx, dz) of thread k at t along the cut (0 root in the void, 1 top), in blocks. Threads are
     * gathered at the root and splay outward and sideways as they climb past the town into the sky, more so the
     * more torn the sky is; everything sways slowly.
     */
    public static void offset(int k, float t, float seconds, float progress, float[] out) {
        float torn = torn(progress);
        float splay = (float) Math.pow(t, 1.5) * (1.5F + 16F * torn) * (k == 0 ? 0.15F : 1F);
        double phi = k * (Math.PI * 2 / STRANDS) + seconds * 0.05 * (k % 2 == 0 ? 1 : -1);
        float sway = (0.6F + 3.0F * torn) * t;
        out[0] = (float) (Math.cos(phi) * splay + Math.sin(t * 9.0 + seconds * 0.6 + k * 1.7) * sway);
        out[1] = (float) (Math.sin(phi) * splay + Math.cos(t * 7.0 + seconds * 0.45 + k * 2.3) * sway);
    }

    /** Half-width of a thread in blocks: heavy while torn, a single thread when the sky holds. */
    public static float halfWidth(int k, float progress) {
        return (k == 0 ? 0.34F : 0.28F) + 0.32F * torn(progress);
    }

    /** Half-width of the dark cut behind the threads, wider as it climbs; gone once rewoven. */
    public static float cutHalfWidth(float t, float progress) {
        return torn(progress) * (2.0F + 4.0F * t);
    }

    /** Alpha along the cut: solid from its root in the void, fraying out into the sky at the top. */
    public static float heightFade(float t) {
        return t < 0.8F ? 1F : clamp((1F - t) / 0.2F);
    }

    /** Fades with horizontal distance from the Dock, so a far pad sees a faint line and never a hard pixel. */
    public static float distanceFade(double horizontal) {
        return clamp((float) ((6000.0 - horizontal) / 3000.0));
    }

    /** The lit thread breathes. */
    public static float pulse(float seconds) {
        return 0.8F + 0.2F * (float) Math.sin(seconds * 1.6);
    }

    private static float clamp(float v) {
        return Math.clamp(v, 0F, 1F);
    }
}
