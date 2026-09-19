package com.ninjacat.skies.driftwrecks.client;

import com.ninjacat.skies.driftwrecks.Driftwrecks;
import com.ninjacat.skies.driftwrecks.registry.DwItems;
import com.ninjacat.skies.driftwrecks.registry.DwRegistries;
import net.minecraft.client.renderer.item.CompassItemPropertyFunction;
import net.minecraft.client.renderer.item.ItemProperties;
import net.minecraft.core.component.DataComponents;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.component.LodestoneTracker;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

/** Client wiring: renderers, the Drift Needle's angle. Only loaded on the physical client. */
public final class DriftClient {
    private DriftClient() {}

    public static void init(IEventBus modBus) {
        modBus.addListener(DriftClient::renderers);
        modBus.addListener(DriftClient::setup);
    }

    private static void renderers(EntityRenderersEvent.RegisterRenderers e) {
        e.registerEntityRenderer(DwRegistries.STEWARD_ECHO.get(), EchoRenderer::new);
        e.registerEntityRenderer(DwRegistries.REMNANT.get(), RemnantRenderer::new);
        e.registerBlockEntityRenderer(DwRegistries.TROPHY_PLINTH.get(), PlinthRenderer::new);
    }

    private static void setup(FMLClientSetupEvent e) {
        e.enqueueWork(() -> ItemProperties.register(DwItems.DRIFT_NEEDLE.get(), ResourceLocation.withDefaultNamespace("angle"),
                new CompassItemPropertyFunction((level, stack, entity) -> {
                    LodestoneTracker t = stack.get(DataComponents.LODESTONE_TRACKER);
                    return t == null ? null : t.target().orElse(null);
                })));
        Driftwrecks.LOGGER.debug("Driftwrecks client ready");
    }
}
