package com.ninjacat.skies.driftwrecks;

import com.mojang.logging.LogUtils;
import com.ninjacat.skies.driftwrecks.network.AtlasSyncPayload;
import com.ninjacat.skies.driftwrecks.registry.DwBlocks;
import com.ninjacat.skies.driftwrecks.registry.DwComponents;
import com.ninjacat.skies.driftwrecks.registry.DwItems;
import com.ninjacat.skies.driftwrecks.registry.DwRegistries;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import org.slf4j.Logger;

/**
 * Driftwrecks: pieces of the old world that drift up to a Clowder's pad, hold for a while, then unravel. Repeatable
 * side content; nothing in the main line needs it.
 */
@Mod(Driftwrecks.MOD_ID)
public final class Driftwrecks {
    public static final String MOD_ID = "driftwrecks";
    public static final Logger LOGGER = LogUtils.getLogger();

    public Driftwrecks(IEventBus modBus, ModContainer container) {
        DwBlocks.BLOCKS.register(modBus);
        DwItems.ITEMS.register(modBus);
        DwItems.TABS.register(modBus);
        DwComponents.COMPONENTS.register(modBus);
        DwRegistries.BLOCK_ENTITIES.register(modBus);
        DwRegistries.ENTITIES.register(modBus);
        DwRegistries.SOUNDS.register(modBus);
        modBus.addListener(DwRegistries::attributes);
        modBus.addListener(this::onPayloads);
        NeoForge.EVENT_BUS.register(new DriftEvents());
        if (FMLEnvironment.dist.isClient()) com.ninjacat.skies.driftwrecks.client.DriftClient.init(modBus);
        container.registerConfig(ModConfig.Type.SERVER, DriftConfig.SPEC);
        LOGGER.info("Driftwrecks: the old world is drifting");
    }

    private void onPayloads(RegisterPayloadHandlersEvent e) {
        e.registrar("1").optional().playToClient(AtlasSyncPayload.TYPE, AtlasSyncPayload.STREAM_CODEC,
                (payload, ctx) -> ctx.enqueueWork(() -> com.ninjacat.skies.driftwrecks.client.ClientAtlas.set(payload.data())));
    }
}
