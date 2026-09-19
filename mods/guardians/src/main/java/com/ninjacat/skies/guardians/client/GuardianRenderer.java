package com.ninjacat.skies.guardians.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import net.minecraft.client.renderer.MultiBufferSource;
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
    /** flip if the bosses turn out to face away from their targets in-game (export axis convention) */
    private static final float FACING = Boolean.getBoolean("guardians.flipFacing") ? 180F : 0F;

    private final MeshPose mesh = new MeshPose();

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
        mesh.pose(clip, f0, f1, t);

        ps.pushPose();
        float bodyYaw = Mth.rotLerp(partial, e.yBodyRotO, e.yBodyRot);
        ps.mulPose(Axis.YP.rotationDegrees(FACING - bodyYaw));
        if (e.deathTime > 0 || e.clip() == GuardianEntity.CLIP_DEATH) { /* the death clip carries the collapse; no vanilla tilt */ }
        PoseStack.Pose pose = ps.last();
        boolean hurt = e.hurtTime > 0;
        int overlay = OverlayTexture.pack(0, hurt);
        mesh.draw(m, pose, buf, e.kind.texture(), e.kind.emissive(), light, overlay);
        ps.popPose();
        super.render(e, yaw, partial, ps, buf, light);
    }

}
