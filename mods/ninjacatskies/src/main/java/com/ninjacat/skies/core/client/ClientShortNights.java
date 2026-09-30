package com.ninjacat.skies.core.client;

import com.ninjacat.skies.core.event.ShortNights;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.world.level.Level;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.tick.LevelTickEvent;

/** The client's half of {@link ShortNights}: steps the night clock with the server so the suns and moons never jump. */
public final class ClientShortNights {
    private long last = Long.MIN_VALUE;

    @SubscribeEvent
    public void onLevelTick(LevelTickEvent.Post event) {
        if (!(event.getLevel() instanceof ClientLevel level) || level.dimension() != Level.OVERWORLD) return;
        long now = level.getDayTime();
        // the client cannot read the daylight gamerule; a clock that moved since last tick is running
        // the server's shortNights setting (synced on login and config reload), not this client's own config
        if (ClientServerRules.shortNights() && last != Long.MIN_VALUE && now > last && ShortNights.night(now)) {
            now += 1;
            level.setDayTime(now);
        }
        last = now;
    }
}
