package com.ninjacat.skies.guardians.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.ninjacat.skies.guardians.Guardians;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.AABB;

/**
 * Renders a Snapped Guardian straight from its baked mesh: CPU linear-blend skinning of every vertex with the
 * interpolated clip frame, pushed through the entity buffers each frame (the same immediate path vanilla uses).
 * Two passes: lit albedo (texture or vertex colour), then an additive full-bright emissive pass for the cut-seams,
 * eyes and glow parts. No GeckoLib: the approved organic meshes are rendered as authored.
 */
public class GuardianRenderer extends EntityRenderer<GuardianEntity> {
    private static final ResourceLocation WHITE = ResourceLocation.fromNamespaceAndPath(Guardians.MOD_ID, "textures/white.png");
    /** flip if the bosses turn out to face away from their targets in-game (export axis convention) */
    private static final float FACING = Boolean.getBoolean("guardians.flipFacing") ? 180F : 0F;

    private float[] bones = new float[0];
    private float[] skinPos = new float[0], skinNrm = new float[0];

    public GuardianRenderer(EntityRendererProvider.Context ctx) { super(ctx); this.shadowRadius = 2.5F; }

    @Override
    public ResourceLocation getTextureLocation(GuardianEntity e) { return e.kind.texture(); }

    @Override
    public boolean shouldRender(GuardianEntity e, net.minecraft.client.renderer.culling.Frustum frustum, double x, double y, double z) {
        return frustum.isVisible(new AABB(e.getX() - 40, e.getY() - 5, e.getZ() - 40, e.getX() + 40, e.getY() + 60, e.getZ() + 40));
    }

    @Override
    public void render(GuardianEntity e, float yaw, float partial, PoseStack ps, MultiBufferSource buf, int light) {
        GuardianModel m = GuardianModel.get(e.kind);
        if (m == null) { super.render(e, yaw, partial, ps, buf, light); return; }
        if (m.clips.length == 0) { super.render(e, yaw, partial, ps, buf, light); return; }
        GuardianModel.Clip clip = m.clip(e.clip()); if (clip == null) clip = m.clips[0];
        if (clip.frames <= 0 || clip.bones <= 0) { super.render(e, yaw, partial, ps, buf, light); return; }
        // subtract in long first: (gameTime + partial) as a float loses the partial tick after ~9.7 days of world age
        float time = ((float) (e.level().getGameTime() - e.clipStart()) + partial) / 20F;
        float f = time * clip.fps;
        if (clip.loops()) f = ((f % clip.frames) + clip.frames) % clip.frames; else f = Mth.clamp(f, 0, clip.frames - 1.001F);
        int f0 = (int) f, f1 = clip.loops() ? (f0 + 1) % clip.frames : Math.min(f0 + 1, clip.frames - 1); float t = f - f0;
        int nb = clip.bones;
        if (bones.length < nb*12) bones = new float[nb*12];
        for (int i = 0; i < nb*12; i++) bones[i] = Mth.lerp(t, clip.m[f0*nb*12 + i], clip.m[f1*nb*12 + i]);

        ps.pushPose();
        float bodyYaw = Mth.rotLerp(partial, e.yBodyRotO, e.yBodyRot);
        ps.mulPose(Axis.YP.rotationDegrees(FACING - bodyYaw));
        if (e.deathTime > 0 || e.clip() == GuardianEntity.CLIP_DEATH) { /* the death clip carries the collapse; no vanilla tilt */ }
        PoseStack.Pose pose = ps.last();
        boolean hurt = e.hurtTime > 0;
        int overlay = OverlayTexture.pack(0, hurt);
        for (GuardianModel.Part part : m.parts) {
            skin(part);
            ResourceLocation tex = part.textured ? e.kind.texture() : WHITE;
            emit(buf.getBuffer(RenderType.entityCutoutNoCull(tex)), part, pose, light, overlay, false);
            // emissive pass: textured parts use the baked emission map, vertex parts their emit colours
            if (part.textured) emit(buf.getBuffer(RenderType.eyes(e.kind.emissive())), part, pose, 0xF000F0, OverlayTexture.NO_OVERLAY, false);
            else if (hasEmit(part)) emit(buf.getBuffer(RenderType.eyes(WHITE)), part, pose, 0xF000F0, OverlayTexture.NO_OVERLAY, true);
        }
        ps.popPose();
        super.render(e, yaw, partial, ps, buf, light);
    }

    private static boolean hasEmit(GuardianModel.Part p) { for (byte b : p.emit) if (b != 0) return true; return false; }

    private void skin(GuardianModel.Part p) {
        int nv = p.vertexCount;
        if (skinPos.length < nv*3) { skinPos = new float[nv*3]; skinNrm = new float[nv*3]; }
        for (int v = 0; v < nv; v++) {
            float x = p.pos[v*3], y = p.pos[v*3+1], z = p.pos[v*3+2], nx = p.normal[v*3], ny = p.normal[v*3+1], nz = p.normal[v*3+2];
            float px = 0, py = 0, pz = 0, qx = 0, qy = 0, qz = 0;
            for (int k = 0; k < 4; k++) {
                float w = p.weight[v*4+k]; if (w <= 0) continue;
                int o = p.bone[v*4+k] * 12; if (o + 11 >= bones.length) continue;
                px += w*(bones[o]*x + bones[o+1]*y + bones[o+2]*z + bones[o+3]);
                py += w*(bones[o+4]*x + bones[o+5]*y + bones[o+6]*z + bones[o+7]);
                pz += w*(bones[o+8]*x + bones[o+9]*y + bones[o+10]*z + bones[o+11]);
                qx += w*(bones[o]*nx + bones[o+1]*ny + bones[o+2]*nz);
                qy += w*(bones[o+4]*nx + bones[o+5]*ny + bones[o+6]*nz);
                qz += w*(bones[o+8]*nx + bones[o+9]*ny + bones[o+10]*nz);
            }
            float l = Mth.sqrt(qx*qx + qy*qy + qz*qz); if (l < 1e-6F) { qx = 0; qy = 1; qz = 0; } else { qx /= l; qy /= l; qz /= l; }
            skinPos[v*3] = px; skinPos[v*3+1] = py; skinPos[v*3+2] = pz; skinNrm[v*3] = qx; skinNrm[v*3+1] = qy; skinNrm[v*3+2] = qz;
        }
    }

    /** Entity render types are QUADS: every triangle is emitted as a degenerate quad (last vertex repeated). */
    private void emit(VertexConsumer vc, GuardianModel.Part p, PoseStack.Pose pose, int light, int overlay, boolean useEmitColour) {
        for (int i = 0; i < p.triCount*4; i++) {
            int v = p.tri[(i/4)*3 + Math.min(i%4, 2)];
            int r, g, b;
            if (useEmitColour) { r = p.emit[v*3] & 0xFF; g = p.emit[v*3+1] & 0xFF; b = p.emit[v*3+2] & 0xFF; }
            else if (p.textured) { r = g = b = 255; }
            else { r = p.rgb[v*3] & 0xFF; g = p.rgb[v*3+1] & 0xFF; b = p.rgb[v*3+2] & 0xFF; }
            vc.addVertex(pose, skinPos[v*3], skinPos[v*3+1], skinPos[v*3+2])
              .setColor(r, g, b, 255)
              .setUv(p.uv[v*2], p.uv[v*2+1])
              .setOverlay(overlay)
              .setLight(light)
              .setNormal(pose, skinNrm[v*3], skinNrm[v*3+1], skinNrm[v*3+2]);
        }
    }
}
