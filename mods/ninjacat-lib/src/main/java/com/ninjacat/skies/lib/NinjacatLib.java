package com.ninjacat.skies.lib;

import com.mojang.logging.LogUtils;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import org.slf4j.Logger;

@Mod(NinjacatLib.MOD_ID)
public final class NinjacatLib {
    public static final String MOD_ID = "ninjacatlib";
    public static final Logger LOGGER = LogUtils.getLogger();

    public NinjacatLib(IEventBus modBus) {
        modBus.addListener(this::onCommonSetup);
    }

    private void onCommonSetup(FMLCommonSetupEvent event) {
        LOGGER.info("Ninjacat Lib ready");
    }
}
