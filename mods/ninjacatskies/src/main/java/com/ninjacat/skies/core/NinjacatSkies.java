package com.ninjacat.skies.core;

import com.mojang.logging.LogUtils;
import com.ninjacat.skies.core.config.SkiesConfig;
import com.ninjacat.skies.core.item.ModItems;
import com.ninjacat.skies.core.item.ModCreativeTabs;
import com.ninjacat.skies.core.command.SkyboundCommands;
import com.ninjacat.skies.core.event.SkyboundEvents;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import org.slf4j.Logger;

@Mod(NinjacatSkies.MOD_ID)
public final class NinjacatSkies {
    public static final String MOD_ID = "ninjacatskies";
    public static final Logger LOGGER = LogUtils.getLogger();

    public NinjacatSkies(IEventBus modBus, ModContainer container) {
        ModItems.ITEMS.register(modBus);
        ModCreativeTabs.TABS.register(modBus);
        modBus.addListener(this::onCommonSetup);

        NeoForge.EVENT_BUS.register(new SkyboundEvents());
        NeoForge.EVENT_BUS.addListener(this::onRegisterCommands);

        container.registerConfig(ModConfig.Type.COMMON, SkiesConfig.SPEC);
    }

    private void onRegisterCommands(RegisterCommandsEvent event) {
        SkyboundCommands.register(event.getDispatcher());
    }

    private void onCommonSetup(FMLCommonSetupEvent event) {
        LOGGER.info("Whisker Codex bound — Ninjacat Skies core online");
    }
}
