package com.ninjacat.skies.core.client;

import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.MeshData;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.ninjacat.skies.core.sky.FrayMath;
import com.ninjacat.skies.core.sky.SunderedSkyMath;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.FogRenderer;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.material.FogType;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import org.joml.Matrix4f;
import org.joml.Vector3f;

/**
 * The Fray, drawn on the sky at Loom's End: the cut past the end of the broken gate-path, nine dark threads that
 * gather one by one as the server reweaves, and a single lit thread once every Clowder online has closed theirs. It
 * comes up out of the bottom of the void below the Hall, rises past the gate-path and frays into the sky. It is drawn
 * right after the sky and before the terrain, each point projected onto the sky dome from wherever the camera stands,
 * so it reads from anywhere in the town, and the town's own buildings still hide it. Near the cut it also sheds lint,
 * or lit motes once the sky holds. It only stands in the dimension the server names. Client only.
 */
public final class FrayRenderer {
    /** Radius the threads are projected to; inside the panorama sphere and every far plane. */
    private static final float DOME = 90F;
    /** A thread is never thinner than this half-angle, so it stays a line and not a flicker from far away. */
    private static final float MIN_HALF_ANGLE = 0.0022F;
    private static final float MAX_HALF_ANGLE = 0.5F;
    private static final DustParticleOptions LINT = new DustParticleOptions(new Vector3f(0.16F, 0.17F, 0.28F), 1.4F);
    private static final DustParticleOptions LIT = new DustParticleOptions(new Vector3f(0.83F, 0.66F, 0.29F), 1.0F);

    private final float[] offset = new float[2];
    private final float[] prev = new float[7];   // x y z  sideX sideY sideZ  halfWidth
    private final float[] cur = new float[7];

    // ---------------------------------------------------------------- the cut in the sky

    @SubscribeEvent
    public void onRenderStage(RenderLevelStageEvent event) {
        if (event.getStage() != RenderLevelStageEvent.Stage.AFTER_SKY || !ClientFray.shown()) {
            return;
        }
        Minecraft mc = Minecraft.getInstance();
        if (!ClientFray.standsIn(mc.level) || event.getCamera().getFluidInCamera() != FogType.NONE) {
            return;
        }
        Vec3 cam = event.getCamera().getPosition();
        double bx = ClientFray.x() + 0.5, by = ClientFray.y(), bz = ClientFray.z() + 0.5;
        float far = FrayMath.distanceFade(Math.hypot(bx - cam.x, bz - cam.z));
        if (far <= 0.001F) {
            return;
        }
        float partial = event.getPartialTick().getGameTimeDeltaPartialTick(false);
        float progress = ClientFray.displayed();
        float torn = FrayMath.torn(progress);
        float glow = FrayMath.glow(progress);
        float seconds = (mc.level.getGameTime() + partial) / 20F;
        // The violet rim is what shows the cut against the night; by day the dark threads carry it, so the rim fades.
        float rim = 0.3F + 0.7F * (1F - SunderedSkyMath.dayness(mc.level.getDayTime(), partial));
        Matrix4f matrix = new Matrix4f(event.getModelViewMatrix()).m30(0).m31(0).m32(0);

        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        RenderSystem.depthMask(false);
        RenderSystem.disableCull();
        RenderSystem.setShader(GameRenderer::getPositionColorShader);
        RenderSystem.setShaderColor(1F, 1F, 1F, 1F);
        FogRenderer.setupNoFog();
        try {
            // The dark cut and its loose threads, over the sky.
            BufferBuilder dark = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
            if (torn > 0.001F) {
                ribbon(dark, matrix, cam, bx, by, bz, -1, progress, seconds, 1F, 0.03F, 0.02F, 0.06F, 0.50F * torn * far);
            }
            for (int k = 0; k < FrayMath.STRANDS; k++) {
                float a = FrayMath.strandAlpha(k, progress) * far * (k == 0 ? 1F - glow : 1F);
                if (a < 0.01F) {
                    continue;
                }
                ribbon(dark, matrix, cam, bx, by, bz, k, progress, seconds, 3F, 0.16F, 0.17F, 0.28F, 0.32F * a);
                ribbon(dark, matrix, cam, bx, by, bz, k, progress, seconds, 1F, 0.02F, 0.02F, 0.05F, 0.90F * a);
            }
            draw(dark);
            RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA, GlStateManager.DestFactor.ONE);
            // A faint violet rim along the cut and its threads: the tear has an edge, and it still reads at night.
            if (torn > 0.001F) {
                BufferBuilder rimBuffer = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
                ribbon(rimBuffer, matrix, cam, bx, by, bz, -1, progress, seconds, 1.4F, 0.50F, 0.30F, 0.62F, 0.16F * torn * far * rim);
                for (int k = 0; k < FrayMath.STRANDS; k++) {
                    float a = FrayMath.strandAlpha(k, progress) * far * (k == 0 ? 1F - glow : 1F);
                    if (a < 0.01F) {
                        continue;
                    }
                    ribbon(rimBuffer, matrix, cam, bx, by, bz, k, progress, seconds, 2.0F, 0.42F, 0.26F, 0.55F, 0.22F * a * rim);
                }
                draw(rimBuffer);
            }
            // The lit thread: a gold halo added to the sky, and a gold core laid over it so it stays gold by day.
            if (glow > 0.001F) {
                float a = glow * far * FrayMath.pulse(seconds);
                BufferBuilder halo = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
                ribbon(halo, matrix, cam, bx, by, bz, 0, progress, seconds, 4F, 0.83F, 0.66F, 0.29F, 0.45F * a);
                draw(halo);
                RenderSystem.defaultBlendFunc();
                BufferBuilder lit = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR);
                ribbon(lit, matrix, cam, bx, by, bz, 0, progress, seconds, 1F, 0.98F, 0.80F, 0.38F, 0.92F * a);
                draw(lit);
            }
        } finally {
            RenderSystem.defaultBlendFunc();
            RenderSystem.depthMask(true);
            RenderSystem.enableCull();
            RenderSystem.disableBlend();
            RenderSystem.setShaderColor(1F, 1F, 1F, 1F);
        }
    }

    private static void draw(BufferBuilder buffer) {
        MeshData mesh = buffer.build();
        if (mesh != null) {
            BufferUploader.drawWithShader(mesh);
        }
    }

    /**
     * One thread (k >= 0) or the cut itself (k = -1) as a soft ribbon on the dome: two quads per segment, the edges
     * fully transparent and the centre at the given alpha, so the line has no hard pixel edge at any width.
     */
    private void ribbon(BufferBuilder buffer, Matrix4f matrix, Vec3 cam, double bx, double by, double bz, int k,
                        float progress, float seconds, float widthScale, float r, float g, float b, float alpha) {
        boolean any = false;
        float prevAlpha = 0F;
        for (int i = 0; i <= FrayMath.SEGMENTS; i++) {
            float t = i / (float) FrayMath.SEGMENTS;   // 0 the root in the void, DOCK the Dock, 1 the top
            FrayMath.offset(Math.max(k, 0), t, seconds, progress, offset);
            double wx = bx + offset[0] - cam.x, wy = by - FrayMath.BELOW + t * FrayMath.SPAN - cam.y, wz = bz + offset[1] - cam.z;
            double dist = Math.sqrt(wx * wx + wy * wy + wz * wz);
            if (dist < 0.5) {
                any = false;   // the camera is inside the thread: start again above it
                continue;
            }
            float dx = (float) (wx / dist), dy = (float) (wy / dist), dz = (float) (wz / dist);
            float halfBlocks = (k < 0 ? FrayMath.cutHalfWidth(t, progress) : FrayMath.halfWidth(k, progress)) * widthScale;
            float halfAngle = Math.clamp((float) (halfBlocks / dist), MIN_HALF_ANGLE, MAX_HALF_ANGLE);
            // Sideways on the dome: horizontal and perpendicular to the view direction (straight overhead: east).
            float sx = -dz, sz = dx;
            float sl = (float) Math.sqrt(sx * sx + sz * sz);
            if (sl < 1e-3F) {
                sx = 1F;
                sz = 0F;
            } else {
                sx /= sl;
                sz /= sl;
            }
            cur[0] = dx * DOME;
            cur[1] = dy * DOME;
            cur[2] = dz * DOME;
            cur[3] = sx;
            cur[4] = 0F;
            cur[5] = sz;
            cur[6] = halfAngle * DOME;
            float a = alpha * FrayMath.heightFade(t);
            if (any) {
                // left half, then right half
                for (int side = -1; side <= 1; side += 2) {
                    vertex(buffer, matrix, prev, side, r, g, b, 0F);
                    vertex(buffer, matrix, prev, 0, r, g, b, prevAlpha);
                    vertex(buffer, matrix, cur, 0, r, g, b, a);
                    vertex(buffer, matrix, cur, side, r, g, b, 0F);
                }
            }
            System.arraycopy(cur, 0, prev, 0, 7);
            prevAlpha = a;
            any = true;
        }
    }

    private static void vertex(BufferBuilder buffer, Matrix4f matrix, float[] p, int side, float r, float g, float b, float a) {
        buffer.addVertex(matrix, p[0] + p[3] * p[6] * side, p[1] + p[4] * p[6] * side, p[2] + p[5] * p[6] * side)
                .setColor(r, g, b, a);
    }

    // ---------------------------------------------------------------- lint under the cut

    @SubscribeEvent
    public void onClientTick(ClientTickEvent.Post event) {
        ClientFray.tick();
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.isPaused() || !ClientFray.standsIn(mc.level)) {
            return;
        }
        Vec3 cam = mc.gameRenderer.getMainCamera().getPosition();
        double bx = ClientFray.x() + 0.5, by = ClientFray.y(), bz = ClientFray.z() + 0.5;
        if (Math.hypot(bx - cam.x, bz - cam.z) > 64.0) {
            return;
        }
        float progress = ClientFray.displayed();
        float torn = FrayMath.torn(progress);
        float glow = FrayMath.glow(progress);
        float seconds = mc.level.getGameTime() / 20F;
        RandomSource random = mc.level.random;
        if (torn > 0.02F && random.nextFloat() < 0.5F * torn) {
            // Lint sifting down out of the cut, from whichever thread still hangs.
            int k = random.nextInt(FrayMath.STRANDS);
            if (FrayMath.strandAlpha(k, progress) > random.nextFloat()) {
                float t = FrayMath.DOCK + (random.nextFloat() - 0.3F) * 0.2F;   // around the Dock, mostly above it
                FrayMath.offset(k, t, seconds, progress, offset);
                mc.level.addParticle(random.nextBoolean() ? LINT : ParticleTypes.ASH,
                        bx + offset[0], by - FrayMath.BELOW + t * FrayMath.SPAN, bz + offset[1], 0, -0.02, 0);
            }
        }
        if (glow > 0.5F && random.nextFloat() < 0.3F) {
            // The sky holds: lit motes climb the thread up out of the void.
            float t = FrayMath.DOCK - random.nextFloat() * 0.15F;
            FrayMath.offset(0, t, seconds, progress, offset);
            mc.level.addParticle(random.nextBoolean() ? ParticleTypes.END_ROD : LIT,
                    bx + offset[0], by - FrayMath.BELOW + t * FrayMath.SPAN, bz + offset[1], 0, 0.03, 0);
        }
    }

    @SubscribeEvent
    public void onLogout(ClientPlayerNetworkEvent.LoggingOut event) {
        ClientFray.reset();
        ClientServerRules.reset();
        ClientTension.reset();
    }
}
