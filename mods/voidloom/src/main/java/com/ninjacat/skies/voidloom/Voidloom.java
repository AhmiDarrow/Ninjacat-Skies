package com.ninjacat.skies.voidloom;

import com.mojang.logging.LogUtils;
import com.ninjacat.skies.voidloom.block.ModBlockEntities;
import com.ninjacat.skies.voidloom.block.ModBlocks;
import com.ninjacat.skies.voidloom.item.ModCreativeTabs;
import com.ninjacat.skies.voidloom.item.ModItems;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import org.slf4j.Logger;

@Mod(Voidloom.MOD_ID)
public final class Voidloom {
    public static final String MOD_ID = "voidloom";
    public static final Logger LOGGER = LogUtils.getLogger();

    public Voidloom(IEventBus modBus) {
        ModBlocks.BLOCKS.register(modBus);
        ModBlockEntities.BLOCK_ENTITY_TYPES.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModCreativeTabs.TABS.register(modBus);
        modBus.addListener(this::onCommonSetup);
    }

    private void onCommonSetup(FMLCommonSetupEvent event) {
        LOGGER.info("Voidloom spindles ready");
    }
}
