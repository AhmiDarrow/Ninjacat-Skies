package com.ninjacat.skies.core.client;

import com.ninjacat.skies.core.config.SkiesConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.util.Mth;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.client.event.ViewportEvent;

/**
 * Warms the horizon a little per seated Strand — meant to be noticed on a screenshot, not on a loading screen.
 * Client only; registered from the mod constructor behind a dist check.
 */
public final class SkyTint {
    @SubscribeEvent
    public void onFogColor(ViewportEvent.ComputeFogColor event) {
        if (!SkiesConfig.SKY_TINT.get()) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || !mc.level.dimensionType().hasSkyLight()) {
            return;
        }
        float t = (ClientTension.seated() + (ClientTension.rewoven() ? 1 : 0)) / 10.0F;
        if (t <= 0.0F) {
            return;
        }
        float blend = 0.14F * t;
        // Lantern gold by day, teal at dusk.
        float day = mc.level.getSkyDarken(1.0F) > 0.5F ? 1.0F : 0.0F;
        float tr = Mth.lerp(day, 0.24F, 0.83F);
        float tg = Mth.lerp(day, 0.48F, 0.66F);
        float tb = Mth.lerp(day, 0.48F, 0.29F);
        event.setRed(Mth.lerp(blend, event.getRed(), tr));
        event.setGreen(Mth.lerp(blend, event.getGreen(), tg));
        event.setBlue(Mth.lerp(blend, event.getBlue(), tb));
    }
}
