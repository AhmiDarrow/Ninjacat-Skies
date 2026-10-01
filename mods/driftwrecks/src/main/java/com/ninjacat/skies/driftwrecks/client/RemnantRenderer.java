package com.ninjacat.skies.driftwrecks.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.Driftwrecks;
import com.ninjacat.skies.driftwrecks.entity.RemnantEntity;
import com.ninjacat.skies.guardians.client.GuardianModel;
import com.ninjacat.skies.guardians.client.MeshPose;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

/**
 * Draws a Remnant from its own baked mesh (assets/driftwrecks/remnant/&lt;strand&gt;.ncgb), never a Guardian's: the
 * same skinning and emissive pass the Guardians use. While the Remnant is closed (immune) it sheds teal motes.
 */
public class RemnantRenderer extends EntityRenderer<RemnantEntity> {
    private final MeshPose mesh = new MeshPose();

    public RemnantRenderer(EntityRendererProvider.Context ctx) { super(ctx); shadowRadius = 1.2F; }

    private static ResourceLocation rl(String p) { return ResourceLocation.fromNamespaceAndPath(Driftwrecks.MOD_ID, p); }

    /** Each Strand's mesh, texture and emission map, built once rather than three new ids every frame. */
    private static final ResourceLocation[] MESH = new ResourceLocation[Strand.ALL.length], TEXTURE = new ResourceLocation[Strand.ALL.length],
            EMIT = new ResourceLocation[Strand.ALL.length];

    static {
        for (Strand s : Strand.ALL) {
            MESH[s.ordinal()] = rl("remnant/" + s.id() + ".ncgb");
            TEXTURE[s.ordinal()] = rl("textures/remnant/" + s.id() + ".png");
            EMIT[s.ordinal()] = rl("textures/remnant/" + s.id() + "_emit.png");
        }
    }

    @Override
    public ResourceLocation getTextureLocation(RemnantEntity e) { return TEXTURE[e.strand().ordinal()]; }

    @Override
    public void render(RemnantEntity e, float yaw, float partial, PoseStack ps, MultiBufferSource buf, int light) {
        GuardianModel m = GuardianModel.load(MESH[e.strand().ordinal()]);
        if (m != null && m.clips.length > 0) {
            GuardianModel.Clip clip = m.clip(e.clip());
            if (clip == null) clip = m.clips[0];
            if (clip.frames > 0 && clip.bones > 0) {
                float time = ((float) (e.level().getGameTime() - e.clipStart()) + partial) / 20F;
                float f = time * clip.fps;
                if (clip.loops()) f = ((f % clip.frames) + clip.frames) % clip.frames; else f = Mth.clamp(f, 0, clip.frames - 1.001F);
                int f0 = (int) f, f1 = clip.loops() ? (f0 + 1) % clip.frames : Math.min(f0 + 1, clip.frames - 1);
                mesh.pose(clip, f0, f1, f - f0);
                ps.pushPose();
                ps.mulPose(Axis.YP.rotationDegrees(-Mth.rotLerp(partial, e.yBodyRotO, e.yBodyRot)));
                mesh.draw(m, ps.last(), buf, getTextureLocation(e), EMIT[e.strand().ordinal()], light, OverlayTexture.pack(0, e.hurtTime > 0));
                ps.popPose();
            }
        }
        super.render(e, yaw, partial, ps, buf, light);
    }
}
