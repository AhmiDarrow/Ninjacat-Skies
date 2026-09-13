package com.ninjacat.skies.core.client;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.ninjacat.skies.core.sky.SunderedSkyMath;
import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.world.level.material.FogType;
import org.joml.Matrix4f;

/** Overworld skybox: the Loom was cut. Gold seam, void tears, heals as Tension seats. */
public final class SunderedSkyRenderer {
    private static final float RADIUS = 100F;
    private static final int RINGS = 14;
    private static final int SEGS = 36;

    private SunderedSkyRenderer() {}

    public static boolean draw(ClientLevel level, float partial, Matrix4f modelView, Camera camera, boolean foggy, Runnable setupFog) {
        setupFog.run();
        if (foggy || camera.getFluidInCamera() != FogType.NONE) {
            return true;
        }
        float day = SunderedSkyMath.dayness(level.getDayTime(), partial);
        float rain = level.getRainLevel(partial);
        float heal = SunderedSkyMath.heal(ClientTension.seated(), ClientTension.rewoven());
        float half = SunderedSkyMath.cutHalfWidth(heal);
        float[] zenith = SunderedSkyMath.zenith(day, heal, rain);
        float[] horizon = SunderedSkyMath.horizon(day, heal, rain);
        float[] nadir = SunderedSkyMath.nadir(day, heal, rain);
        float[] gold = SunderedSkyMath.cutGold(heal, day);
        float[] core = SunderedSkyMath.cutCore(heal);
        Matrix4f m = new Matrix4f(modelView);
        m.m30(0).m31(0).m32(0);
        var old = RenderSystem.getShader();
        float[] oldColor = RenderSystem.getShaderColor().clone();
        RenderSystem.depthMask(false);
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        RenderSystem.disableCull();
        RenderSystem.setShader(GameRenderer::getPositionColorShader);
        RenderSystem.setShaderColor(1, 1, 1, 1);
        try {
            var buffer = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
            sphere(buffer, m, zenith, horizon, nadir, half, gold, core);
            tears(buffer, m, 1F - heal, day);
            float cel = level.getTimeOfDay(partial);
            float sunA = SunderedSkyMath.sunAlpha(day, rain);
            if (sunA > 0.02F) {
                splitDisc(buffer, m, cel, sunA, heal);
            }
            float moonA = SunderedSkyMath.moonAlpha(day, rain);
            if (moonA > 0.02F) {
                splitDisc(buffer, m, cel + 0.5F, moonA * 0.75F, heal);
            }
            BufferUploader.drawWithShader(buffer.buildOrThrow());
        } finally {
            RenderSystem.depthMask(true);
            RenderSystem.enableCull();
            RenderSystem.disableBlend();
            RenderSystem.setShaderColor(oldColor[0], oldColor[1], oldColor[2], oldColor[3]);
            if (old != null) {
                RenderSystem.setShader(() -> old);
            }
        }
        return true;
    }

    private static void sphere(com.mojang.blaze3d.vertex.BufferBuilder b, Matrix4f m,
            float[] zenith, float[] horizon, float[] nadir, float half, float[] gold, float[] core) {
        for (int ring = 0; ring < RINGS; ring++) {
            float t0 = ring / (float) RINGS;
            float t1 = (ring + 1) / (float) RINGS;
            float a0 = (float) (t0 * Math.PI);
            float a1 = (float) (t1 * Math.PI);
            float y0 = (float) Math.cos(a0) * RADIUS;
            float y1 = (float) Math.cos(a1) * RADIUS;
            float r0 = (float) Math.sin(a0) * RADIUS;
            float r1 = (float) Math.sin(a1) * RADIUS;
            for (int s = 0; s < SEGS; s++) {
                float u0 = (float) (s * Math.PI * 2 / SEGS);
                float u1 = (float) ((s + 1) * Math.PI * 2 / SEGS);
                float[] c00 = shade(t0, u0, y0, r0, zenith, horizon, nadir, half, gold, core);
                float[] c01 = shade(t0, u1, y0, r0, zenith, horizon, nadir, half, gold, core);
                float[] c11 = shade(t1, u1, y1, r1, zenith, horizon, nadir, half, gold, core);
                float[] c10 = shade(t1, u0, y1, r1, zenith, horizon, nadir, half, gold, core);
                quad(b, m,
                        r0 * (float) Math.cos(u0), y0, r0 * (float) Math.sin(u0), c00,
                        r0 * (float) Math.cos(u1), y0, r0 * (float) Math.sin(u1), c01,
                        r1 * (float) Math.cos(u1), y1, r1 * (float) Math.sin(u1), c11,
                        r1 * (float) Math.cos(u0), y1, r1 * (float) Math.sin(u0), c10);
            }
        }
    }

    private static float[] shade(float t, float u, float y, float rad, float[] zenith, float[] horizon, float[] nadir,
            float half, float[] gold, float[] core) {
        float x = rad * (float) Math.cos(u);
        float z = rad * (float) Math.sin(u);
        float inv = 1F / RADIUS;
        float dist = SunderedSkyMath.cutDistance(x * inv, y * inv, z * inv);
        float[] base = t <= 0.5F ? lerp3(t * 2F, zenith, horizon) : lerp3((t - 0.5F) * 2F, horizon, nadir);
        if (dist < half * 0.45F) {
            return core;
        }
        if (dist < half) {
            float k = (dist - half * 0.45F) / (half * 0.55F);
            return lerp4(k, core, gold);
        }
        if (dist < half * 1.8F) {
            float k = (dist - half) / (half * 0.8F);
            return new float[] {
                    gold[0] + (base[0] - gold[0]) * k,
                    gold[1] + (base[1] - gold[1]) * k,
                    gold[2] + (base[2] - gold[2]) * k,
                    1F
            };
        }
        return new float[] { base[0], base[1], base[2], 1F };
    }

    private static void tears(com.mojang.blaze3d.vertex.BufferBuilder b, Matrix4f m, float sunder, float day) {
        if (sunder < 0.08F) {
            return;
        }
        float a = sunder * (0.35F + (1F - day) * 0.25F);
        float[] c = { 0.04F, 0.07F, 0.10F, a };
        for (int i = 0; i < 7; i++) {
            float u = (float) (i * 0.93 + 0.4);
            float v = (float) ((i * 1.7) % 1.2 - 0.2);
            float y = v * RADIUS;
            float r = (float) Math.sqrt(Math.max(1, RADIUS * RADIUS - y * y));
            float cx = (float) Math.cos(u) * r * 0.72F;
            float cz = (float) Math.sin(u) * r * 0.72F;
            float s = 4.5F + i * 0.4F;
            quad(b, m,
                    cx - s, y - s * 1.6F, cz, c,
                    cx + s, y - s * 1.6F, cz, c,
                    cx + s * 0.3F, y + s * 1.8F, cz, c,
                    cx - s * 0.3F, y + s * 1.8F, cz, c);
        }
    }

    private static void splitDisc(com.mojang.blaze3d.vertex.BufferBuilder b, Matrix4f m, float celestial, float alpha, float heal) {
        float ang = celestial * (float) Math.PI * 2;
        float cy = (float) Math.cos(ang) * 80F;
        float cz = (float) Math.sin(ang) * 80F;
        float split = (1F - heal) * 3.2F;
        float[] warm = { 0.92F, 0.70F, 0.32F, alpha };
        float[] cool = { 0.55F, 0.72F, 0.78F, alpha * 0.85F };
        quad(b, m, -10F - split, cy - 2F, cz, warm, -split, cy - 2F, cz, warm, -split, cy + 2F, cz, warm, -10F - split, cy + 2F, cz, warm);
        quad(b, m, split, cy - 2.2F, cz + 1.2F, cool, 10F + split, cy - 2.2F, cz + 1.2F, cool, 10F + split, cy + 1.8F, cz + 1.2F, cool, split, cy + 1.8F, cz + 1.2F, cool);
    }

    private static float[] lerp3(float t, float[] a, float[] b) {
        t = Math.clamp(t, 0F, 1F);
        return new float[] { a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t };
    }

    private static float[] lerp4(float t, float[] a, float[] b) {
        t = Math.clamp(t, 0F, 1F);
        return new float[] {
                a[0] + (b[0] - a[0]) * t,
                a[1] + (b[1] - a[1]) * t,
                a[2] + (b[2] - a[2]) * t,
                a[3] + (b[3] - a[3]) * t
        };
    }

    private static void quad(com.mojang.blaze3d.vertex.BufferBuilder b, Matrix4f m,
            float x0, float y0, float z0, float[] c0,
            float x1, float y1, float z1, float[] c1,
            float x2, float y2, float z2, float[] c2,
            float x3, float y3, float z3, float[] c3) {
        vert(b, m, x0, y0, z0, c0);
        vert(b, m, x1, y1, z1, c1);
        vert(b, m, x2, y2, z2, c2);
        vert(b, m, x3, y3, z3, c3);
    }

    private static void vert(com.mojang.blaze3d.vertex.BufferBuilder b, Matrix4f m, float x, float y, float z, float[] c) {
        float a = c.length > 3 ? c[3] : 1F;
        b.addVertex(m, x, y, z).setColor(c[0], c[1], c[2], a);
    }
}
