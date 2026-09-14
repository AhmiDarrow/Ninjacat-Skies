package com.ninjacat.skies.core.client;

import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.material.FogType;
import org.joml.Matrix4f;
import com.ninjacat.skies.core.sky.SunderedSkyMath;

/** High-definition celestial loom, with continuous day/night transitions. */
public final class SunderedSkyRenderer {
    private static final ResourceLocation[] LAYERS = {
        ResourceLocation.fromNamespaceAndPath("ninjacatskies", "textures/sky/sundered_night.png"),
        ResourceLocation.fromNamespaceAndPath("ninjacatskies", "textures/sky/sundered_day.png"),
        ResourceLocation.fromNamespaceAndPath("ninjacatskies", "textures/sky/march_night.png"),
        ResourceLocation.fromNamespaceAndPath("ninjacatskies", "textures/sky/march_day.png")
    };
    private SunderedSkyRenderer() {}
    public static boolean draw(ClientLevel level, float partial, Matrix4f modelView, Camera camera, boolean foggy, Runnable setupFog) {
        setupFog.run();
        if (foggy || camera.getFluidInCamera() != FogType.NONE) return true;
        float day = SunderedSkyMath.dayness(level.getDayTime(), partial);
        float heal = SunderedSkyMath.heal(ClientTension.seated(), ClientTension.rewoven());
        float[] weights = {(1-day)*(1-heal), day*(1-heal), (1-day)*heal, day*heal};
        PanoramicSky.draw(level, partial, modelView, LAYERS, weights);
        return true;
    }
}
