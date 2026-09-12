package com.ninjacat.skies.voidloom.compat;

import net.minecraft.util.RandomSource;

/** Automated Loomframe keeps this fraction of an Ex Deorum hand-sieve roll. */
public final class LoomframeYield {
    public static final float AUTOMATED = 0.8F;

    private LoomframeYield() {}

    public static int scale(int sieveCount, RandomSource rand) {
        return scale(sieveCount, AUTOMATED, rand);
    }

    public static int scale(int sieveCount, float keep, RandomSource rand) {
        if (sieveCount <= 0) return 0;
        int n = 0;
        for (int i = 0; i < sieveCount; i++) {
            if (rand.nextFloat() < keep) n++;
        }
        return n;
    }
}
