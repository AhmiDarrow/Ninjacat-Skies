package com.ninjacat.skies.driftwrecks.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.ninjacat.skies.driftwrecks.block.TrophyPlinthBlockEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;

/** Six Keepsakes turning slowly in a ring above the plinth. */
public class PlinthRenderer implements BlockEntityRenderer<TrophyPlinthBlockEntity> {
    public PlinthRenderer(BlockEntityRendererProvider.Context ctx) {}

    @Override
    public void render(TrophyPlinthBlockEntity be, float partial, PoseStack ps, MultiBufferSource buf, int light, int overlay) {
        float spin = be.getLevel() == null ? 0 : (be.getLevel().getGameTime() + partial) * 0.6F;
        for (int i = 0; i < TrophyPlinthBlockEntity.SLOTS; i++) {
            ItemStack s = be.slot(i);
            if (s.isEmpty()) continue;
            double a = Math.PI * 2 * i / TrophyPlinthBlockEntity.SLOTS;
            ps.pushPose();
            ps.translate(0.5 + Math.cos(a) * 0.3, 0.95, 0.5 + Math.sin(a) * 0.3);
            ps.mulPose(Axis.YP.rotationDegrees(spin + i * 60));
            ps.scale(0.35F, 0.35F, 0.35F);
            Minecraft.getInstance().getItemRenderer().renderStatic(s, ItemDisplayContext.FIXED, light, overlay, ps, buf, be.getLevel(), 0);
            ps.popPose();
        }
    }
}
