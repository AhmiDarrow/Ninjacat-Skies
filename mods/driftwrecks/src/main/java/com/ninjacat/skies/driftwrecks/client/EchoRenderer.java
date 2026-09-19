package com.ninjacat.skies.driftwrecks.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.ninjacat.skies.driftwrecks.Driftwrecks;
import com.ninjacat.skies.driftwrecks.entity.StewardEchoEntity;
import net.minecraft.client.model.OcelotModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.FastColor;
import net.minecraft.util.Mth;

/** A quiet translucent cat in teal thread: the vanilla cat body, drawn see-through with its own texture. */
public class EchoRenderer extends EntityRenderer<StewardEchoEntity> {
    private static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath(Driftwrecks.MOD_ID, "textures/entity/steward_echo.png");
    private final OcelotModel<StewardEchoEntity> model;

    public EchoRenderer(EntityRendererProvider.Context ctx) {
        super(ctx);
        model = new OcelotModel<>(ctx.bakeLayer(ModelLayers.CAT));
        model.young = false;   // only LivingEntityRenderer resets this; left true it draws a kitten
        shadowRadius = 0.2F;
    }

    @Override public ResourceLocation getTextureLocation(StewardEchoEntity e) { return TEXTURE; }

    @Override
    public void render(StewardEchoEntity e, float yaw, float partial, PoseStack ps, MultiBufferSource buf, int light) {
        ps.pushPose();
        float body = Mth.rotLerp(partial, e.yBodyRotO, e.yBodyRot);
        ps.translate(0, 1.5 + Mth.sin((e.tickCount + partial) * 0.1F) * 0.04F, 0);
        ps.mulPose(Axis.YP.rotationDegrees(180 - body));
        ps.scale(-0.8F, -0.8F, 0.8F);
        float walk = e.walkAnimation.position(partial), speed = Math.min(1F, e.walkAnimation.speed(partial));
        float head = Mth.rotLerp(partial, e.yHeadRotO, e.yHeadRot) - body;
        model.prepareMobModel(e, walk, speed, partial);
        model.setupAnim(e, walk, speed, e.tickCount + partial, head, Mth.lerp(partial, e.xRotO, e.getXRot()));
        int alpha = 150 + (int) (Mth.sin((e.tickCount + partial) * 0.07F) * 30);
        model.renderToBuffer(ps, buf.getBuffer(RenderType.entityTranslucent(TEXTURE)), 0xF000F0, OverlayTexture.NO_OVERLAY, FastColor.ARGB32.color(alpha, 255, 255, 255));
        ps.popPose();
        super.render(e, yaw, partial, ps, buf, light);
    }
}
