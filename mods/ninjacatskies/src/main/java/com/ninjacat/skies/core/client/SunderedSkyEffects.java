package com.ninjacat.skies.core.client;

import com.ninjacat.skies.core.config.SkiesConfig;
import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.DimensionSpecialEffects;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.client.event.RegisterDimensionSpecialEffectsEvent;
import org.joml.Matrix4f;

public final class SunderedSkyEffects extends DimensionSpecialEffects {
    public SunderedSkyEffects() {
        super(Float.NaN, true, SkyType.NORMAL, false, false);
    }

    public static void register(RegisterDimensionSpecialEffectsEvent event) {
        event.register(ResourceLocation.withDefaultNamespace("overworld"), new SunderedSkyEffects());
    }

    @Override
    public Vec3 getBrightnessDependentFogColor(Vec3 color, float brightness) {
        float heal = com.ninjacat.skies.core.sky.SunderedSkyMath.heal(ClientTension.seated(), ClientTension.rewoven());
        return color.multiply(
                0.18 + brightness * 0.62 + heal * 0.08,
                0.14 + brightness * 0.58 + heal * 0.14,
                0.16 + brightness * 0.55 + heal * 0.10);
    }

    @Override
    public boolean isFoggyAt(int x, int y) {
        return false;
    }

    @Override
    public float[] getSunriseColor(float time, float partial) {
        float[] base = super.getSunriseColor(time, partial);
        if (base == null) {
            return null;
        }
        return new float[] { 0.72F, 0.42F, 0.28F, base[3] * 0.7F };
    }

    @Override
    public boolean renderSky(ClientLevel level, int ticks, float partialTick, Matrix4f modelViewMatrix, Camera camera, Matrix4f projectionMatrix, boolean isFoggy, Runnable setupFog) {
        if (!SkiesConfig.SUNDERED_SKY.get()) {
            return false;
        }
        return SunderedSkyRenderer.draw(level, partialTick, modelViewMatrix, camera, isFoggy, setupFog);
    }
}
