package com.ninjacat.skies.core.event;

import com.ninjacat.skies.core.NinjacatSkies;
import com.ninjacat.skies.core.config.SkiesConfig;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.GameRules;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;

/** Vanilla already counts sleepers per dimension; Core only sets how many it needs. */
public final class SleepRule {
    @SubscribeEvent
    public void onServerStarted(ServerStartedEvent event) {
        apply(event.getServer());
    }

    public static void apply(MinecraftServer server) {
        int percent = SkiesConfig.SLEEP_PERCENTAGE.get();
        if (percent < 0) return;
        GameRules.IntegerValue rule = server.getGameRules().getRule(GameRules.RULE_PLAYERS_SLEEPING_PERCENTAGE);
        if (rule.get() == percent) return;
        rule.set(percent, server);
        NinjacatSkies.LOGGER.info("playersSleepingPercentage set to {}", percent);
    }
}
