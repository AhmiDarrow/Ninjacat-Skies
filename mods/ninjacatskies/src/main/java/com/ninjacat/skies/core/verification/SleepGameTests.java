package com.ninjacat.skies.core.verification;

import com.ninjacat.skies.core.config.SkiesConfig;
import com.ninjacat.skies.core.event.SleepRule;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.players.SleepStatus;
import net.minecraft.world.level.GameRules;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@GameTestHolder("ninjacatskies")
@PrefixGameTestTemplate(false)
public class SleepGameTests {
    @GameTest(template = "empty")
    public static void aQuarterOfTheDimensionPassesTheNight(GameTestHelper h) {
        var server = h.getLevel().getServer();
        SleepRule.apply(server);
        int percent = server.getGameRules().getInt(GameRules.RULE_PLAYERS_SLEEPING_PERCENTAGE);
        h.assertTrue(percent == SkiesConfig.SLEEP_PERCENTAGE.get() && percent == 25, "Core sets the sleep rule to 25%, got " + percent);

        h.assertTrue(enough(h, 4, 1, percent), "One of four sleeping passes the night");
        h.assertFalse(enough(h, 5, 1, percent), "One of five is short: 25% of five rounds up to two");
        h.assertTrue(enough(h, 5, 2, percent), "Two of five sleeping passes the night");
        h.assertTrue(enough(h, 1, 1, percent), "A lone player still sleeps the night away");
        h.succeed();
    }

    private static boolean enough(GameTestHelper h, int online, int sleeping, int percent) {
        List<ServerPlayer> players = new ArrayList<>();
        for (int i = 0; i < online; i++) {
            ServerPlayer p = FakePlayerFactory.get(h.getLevel(), new com.mojang.authlib.GameProfile(UUID.randomUUID(), "sleeper" + i));
            if (i < sleeping) p.setSleepingPos(h.absolutePos(new net.minecraft.core.BlockPos(1, 2, 1)));
            else p.clearSleepingPos();
            players.add(p);
        }
        SleepStatus status = new SleepStatus();
        status.update(players);
        boolean result = status.areEnoughSleeping(percent);
        players.forEach(ServerPlayer::clearSleepingPos);
        return result;
    }
}
