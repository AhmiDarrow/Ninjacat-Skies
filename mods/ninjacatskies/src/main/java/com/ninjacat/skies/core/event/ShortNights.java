package com.ninjacat.skies.core.event;

import com.ninjacat.skies.core.config.SkiesConfig;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.tick.LevelTickEvent;

/**
 * Under the Sundered sky's two suns the Overworld's night is short: from dusk (13000) to dawn (23000) the clock
 * runs at double speed, so night takes half as long as day. Only while the daylight cycle runs. The client
 * mirrors the step ({@code client.ClientShortNights}) so the sky moves smoothly between the server's time updates.
 */
public final class ShortNights {
    public static final long DUSK = 13000, DAWN = 23000;

    public static boolean night(long dayTime) {
        long d = Math.floorMod(dayTime, 24000L);
        return d >= DUSK && d < DAWN;
    }

    @SubscribeEvent
    public void onLevelTick(LevelTickEvent.Post event) {
        if (!(event.getLevel() instanceof ServerLevel level) || level.dimension() != Level.OVERWORLD) return;
        if (!SkiesConfig.SHORT_NIGHTS.get() || !level.getGameRules().getBoolean(GameRules.RULE_DAYLIGHT)) return;
        if (night(level.getDayTime())) level.setDayTime(level.getDayTime() + 1);
    }
}
