package com.ninjacat.skies.clowder;

import com.mojang.logging.LogUtils;
import com.ninjacat.skies.clowder.command.ClowderCommands;
import com.ninjacat.skies.clowder.item.ModCreativeTabs;
import com.ninjacat.skies.clowder.item.ModItems;
import com.ninjacat.skies.clowder.team.ClowderSync;
import com.ninjacat.skies.clowder.world.ModDimensions;
import net.minecraft.server.level.ServerLevel;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.player.PlayerSetSpawnEvent;
import net.neoforged.neoforge.event.tick.LevelTickEvent;
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
        NeoForge.EVENT_BUS.addListener(this::onSetSpawn);
        NeoForge.EVENT_BUS.addListener(this::onLevelTick);
        ClowderSync.register(NeoForge.EVENT_BUS);
    }

    /** Hall beds are for rest, not a new pad spawn — Charter sneak-use seals the island. */
    private void onSetSpawn(PlayerSetSpawnEvent event) {
        if (event.getEntity().level().dimension().equals(ModDimensions.CLOWDER_HALL) && !event.isForced()) {
            event.setCanceled(true);
        }
    }

    /**
     * The Hall never spawns anything by itself: its ground is the void biome, which lists no mobs, and every creature
     * there is seated by the town plan or brought in by a player. Natural spawning would still try a dozen spots per
     * chunk every tick and find nothing, so it is switched off for this level. The server turns it back on whenever
     * it sets the spawn flags (startup, difficulty changes), so the Hall turns it off again before each of its ticks:
     * two field writes. Eggs, commands, breeding and the town plan do not use these flags.
     */
    private void onLevelTick(LevelTickEvent.Pre event) {
        if (event.getLevel() instanceof ServerLevel level && level.dimension().equals(ModDimensions.CLOWDER_HALL)) {
            level.setSpawnSettings(false, false);
        }
    }

    private void onCommonSetup(FMLCommonSetupEvent event) {
        // Datapack dimension clowderhall:clowder_hall auto-loads on NeoForge 1.21.1.
        LOGGER.info("Clowder Hall doors unlatched — hub dimension ready");
    }

    private void onRegisterCommands(RegisterCommandsEvent event) {
        ClowderCommands.register(event.getDispatcher());
    }
}
