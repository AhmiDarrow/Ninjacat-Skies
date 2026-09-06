package com.ninjacat.skies.voidloom;

import com.mojang.logging.LogUtils;
import com.ninjacat.skies.voidloom.block.ModBlockEntities;
import com.ninjacat.skies.voidloom.block.ModBlocks;
import com.ninjacat.skies.voidloom.item.ModCreativeTabs;
import com.ninjacat.skies.voidloom.item.ModItems;
import com.ninjacat.skies.voidloom.sound.ModSounds;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
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
        ModSounds.SOUNDS.register(modBus);
        modBus.addListener(this::onCommonSetup);
        modBus.addListener(this::onRegisterCapabilities);
    }

    /** Hoppers and pipes: grit in the top of a Loomframe, scraps out the sides; same for the Barrel. */
    private void onRegisterCapabilities(RegisterCapabilitiesEvent event) {
        event.registerBlockEntity(Capabilities.ItemHandler.BLOCK, ModBlockEntities.LOOMFRAME.get(), (be, side) -> be.handler());
        event.registerBlockEntity(Capabilities.ItemHandler.BLOCK, ModBlockEntities.TENSION_BARREL.get(), (be, side) -> be.handler());
    }

    private void onCommonSetup(FMLCommonSetupEvent event) {
        LOGGER.info("Voidloom spindles ready");
    }
}
