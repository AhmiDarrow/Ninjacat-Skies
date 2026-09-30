package com.ninjacat.skies.core.verification;

import com.ninjacat.skies.core.event.ShortNights;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.level.GameRules;
import net.neoforged.neoforge.event.tick.LevelTickEvent;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("ninjacatskies")
@PrefixGameTestTemplate(false)
public class ShortNightGameTests {
    @GameTest(template = "empty")
    public static void nightsRunAtDoubleSpeedOnlyAtNight(GameTestHelper h) {
        var level = h.getLevel();
        var rule = level.getGameRules().getRule(GameRules.RULE_DAYLIGHT);
        boolean ruleWas = rule.get();
        long timeWas = level.getDayTime();
        var nights = new ShortNights();
        try {
            rule.set(true, level.getServer());
            level.setDayTime(24000L * 3 + 14000);
            nights.onLevelTick(new LevelTickEvent.Post(() -> true, level));
            h.assertTrue(level.getDayTime() == 24000L * 3 + 14001, "At night the clock takes an extra step each tick");
            level.setDayTime(24000L * 3 + 6000);
            nights.onLevelTick(new LevelTickEvent.Post(() -> true, level));
            h.assertTrue(level.getDayTime() == 24000L * 3 + 6000, "By day the clock is left alone");
            level.setDayTime(24000L * 3 + 23500);
            nights.onLevelTick(new LevelTickEvent.Post(() -> true, level));
            h.assertTrue(level.getDayTime() == 24000L * 3 + 23500, "Dawn (23000 on) runs at the normal pace");
            rule.set(false, level.getServer());
            level.setDayTime(24000L * 3 + 14000);
            nights.onLevelTick(new LevelTickEvent.Post(() -> true, level));
            h.assertTrue(level.getDayTime() == 24000L * 3 + 14000, "A stopped daylight cycle stays stopped");
            h.assertTrue(ShortNights.night(13000) && ShortNights.night(22999) && !ShortNights.night(23000) && !ShortNights.night(12999),
                    "Night is dusk 13000 to dawn 23000");
        } finally {
            rule.set(ruleWas, level.getServer());
            level.setDayTime(timeWas);
        }
        h.succeed();
    }

    /** The client steps its clock by the server's shortNights (and hides the dismount hint by its sneakDismounts), not its own config. */
    @GameTest(template = "empty")
    public static void serverRulesReachTheClient(GameTestHelper h) {
        var now = com.ninjacat.skies.core.network.ServerRulesPayload.current();
        h.assertTrue(now.shortNights() == com.ninjacat.skies.core.config.SkiesConfig.SHORT_NIGHTS.get()
                && now.sneakDismounts() == com.ninjacat.skies.core.config.SkiesConfig.SNEAK_DISMOUNTS.get(), "The payload carries the server's config");
        for (boolean nights : new boolean[] {true, false}) for (boolean sneak : new boolean[] {true, false}) {
            var sent = new com.ninjacat.skies.core.network.ServerRulesPayload(nights, sneak);
            io.netty.buffer.ByteBuf buf = io.netty.buffer.Unpooled.buffer();
            com.ninjacat.skies.core.network.ServerRulesPayload.STREAM_CODEC.encode(buf, sent);
            var got = com.ninjacat.skies.core.network.ServerRulesPayload.STREAM_CODEC.decode(buf);
            h.assertTrue(sent.equals(got), "The payload survives the wire: " + sent);
            com.ninjacat.skies.core.client.ClientServerRules.apply(got);
            h.assertTrue(com.ninjacat.skies.core.client.ClientServerRules.shortNights() == nights
                    && com.ninjacat.skies.core.client.ClientServerRules.sneakDismounts() == sneak, "The client takes the server's rules");
        }
        com.ninjacat.skies.core.client.ClientServerRules.reset();
        h.assertTrue(!com.ninjacat.skies.core.client.ClientServerRules.shortNights() && com.ninjacat.skies.core.client.ClientServerRules.sneakDismounts(),
                "Off a server the client assumes vanilla");
        h.succeed();
    }
}
