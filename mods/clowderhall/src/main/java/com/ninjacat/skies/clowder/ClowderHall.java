package com.ninjacat.skies.clowder;

import com.mojang.logging.LogUtils;
import com.ninjacat.skies.clowder.command.ClowderCommands;
import com.ninjacat.skies.clowder.item.ModCreativeTabs;
import com.ninjacat.skies.clowder.item.ModItems;
import com.ninjacat.skies.clowder.team.ClowderSync;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import org.slf4j.Logger;

@Mod(ClowderHall.MOD_ID)
public final class ClowderHall {
    public static final String MOD_ID = "clowderhall";
    public static final Logger LOGGER = LogUtils.getLogger();

    public ClowderHall(IEventBus modBus) {
        ModItems.ITEMS.register(modBus);
        ModCreativeTabs.TABS.register(modBus);
        modBus.addListener(this::onCommonSetup);
        NeoForge.EVENT_BUS.addListener(this::onRegisterCommands);
        ClowderSync.register(NeoForge.EVENT_BUS);
    }

    private void onCommonSetup(FMLCommonSetupEvent event) {
        // Datapack dimension clowderhall:clowder_hall auto-loads on NeoForge 1.21.1.
        LOGGER.info("Clowder Hall doors unlatched — hub dimension ready");
    }

    private void onRegisterCommands(RegisterCommandsEvent event) {
        ClowderCommands.register(event.getDispatcher());
    }
}
