package com.ninjacat.skies.core.compat;

/**
 * JER 1.6.0.17 names every mob-loot grid cell {@code "0".."n"} and attaches
 * {@code MobTooltip} even to empty cells. Hovering cell {@code i} then does
 * {@code drops.get(i)} and crashes when the mob has fewer drops than cells.
 */
public final class JerMobTooltipGuard {
    private JerMobTooltipGuard() {}

    public static boolean shouldSkip(int dropCount, String slotName) {
        int index;
        try {
            index = Integer.parseInt(slotName == null || slotName.isEmpty() ? "0" : slotName);
        } catch (NumberFormatException ignored) {
            return true;
        }
        return index < 0 || index >= dropCount;
    }
}
