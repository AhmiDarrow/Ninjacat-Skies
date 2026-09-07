package com.ninjacat.skies.core;

import com.mojang.logging.LogUtils;
import com.ninjacat.skies.core.block.ModBlockEntities;
import com.ninjacat.skies.core.block.ModBlocks;
import com.ninjacat.skies.core.client.ClientTension;
import com.ninjacat.skies.core.client.SkyTint;
import com.ninjacat.skies.core.command.SkyboundCommands;
import com.ninjacat.skies.core.config.SkiesConfig;
import com.ninjacat.skies.core.event.SkyboundEvents;
import com.ninjacat.skies.core.item.ModCreativeTabs;
import com.ninjacat.skies.core.item.ModItems;
import com.ninjacat.skies.core.network.TensionSyncPayload;
import com.ninjacat.skies.core.sound.ModSounds;
import com.ninjacat.skies.core.tension.TensionEffects;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.registration.PayloadRegistrar;
import org.slf4j.Logger;

@Mod(NinjacatSkies.MOD_ID)
public final class NinjacatSkies {
    public static final String MOD_ID = "ninjacatskies";
    public static final Logger LOGGER = LogUtils.getLogger();

    public NinjacatSkies(IEventBus modBus, ModContainer container) {
        ModBlocks.BLOCKS.register(modBus);
        ModBlockEntities.BLOCK_ENTITY_TYPES.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModCreativeTabs.TABS.register(modBus);
        ModSounds.SOUNDS.register(modBus);
        modBus.addListener(this::onCommonSetup);
        modBus.addListener(this::onRegisterPayloads);

        NeoForge.EVENT_BUS.register(new SkyboundEvents());
        NeoForge.EVENT_BUS.register(new TensionEffects());
        NeoForge.EVENT_BUS.addListener(this::onRegisterCommands);
        if (FMLEnvironment.dist.isClient()) {
            NeoForge.EVENT_BUS.register(new SkyTint());
            NeoForge.EVENT_BUS.register(new com.ninjacat.skies.core.client.PackKeybindings());
            if (Boolean.getBoolean("ninjacatskies.uiVerification")) NeoForge.EVENT_BUS.register(new com.ninjacat.skies.core.client.UiVerification());
        }

        container.registerConfig(ModConfig.Type.COMMON, SkiesConfig.SPEC);
    }

    private void onRegisterPayloads(RegisterPayloadHandlersEvent event) {
        PayloadRegistrar registrar = event.registrar("1");
        registrar.playToClient(TensionSyncPayload.TYPE, TensionSyncPayload.STREAM_CODEC, ClientTension::handle);
    }

    private void onRegisterCommands(RegisterCommandsEvent event) {
        SkyboundCommands.register(event.getDispatcher());
    }

    private void onCommonSetup(FMLCommonSetupEvent event) {
        LOGGER.info("Whisker Codex bound — Ninjacat Skies core online");
    }
}
