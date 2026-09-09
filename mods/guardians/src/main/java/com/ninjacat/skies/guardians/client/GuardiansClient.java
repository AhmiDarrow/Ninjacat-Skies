package com.ninjacat.skies.guardians.client;

import com.ninjacat.skies.guardians.Guardians;
import com.ninjacat.skies.guardians.entity.ModEntities;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.client.event.RegisterClientReloadListenersEvent;

/** Client-only entry point: the custom renderer for every guardian type and the model cache reload. */
@Mod(value = Guardians.MOD_ID, dist = Dist.CLIENT)
public final class GuardiansClient {
    public GuardiansClient(IEventBus modBus) {
        modBus.addListener(this::onRenderers);
        modBus.addListener(this::onReload);
    }

    private void onRenderers(EntityRenderersEvent.RegisterRenderers e) {
        for (var h : ModEntities.TYPES.values()) e.registerEntityRenderer(h.get(), GuardianRenderer::new);
    }

    private void onReload(RegisterClientReloadListenersEvent e) {
        e.registerReloadListener((ResourceManagerReloadListener) (ResourceManager rm) -> GuardianModel.clearCache());
    }
}
