package com.ninjacat.skies.core.verification;

import com.ninjacat.skies.core.compat.JerMobTooltipGuard;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("ninjacatskies")
@PrefixGameTestTemplate(false)
public class JerCompatGameTests {
    @GameTest(template = "empty")
    public static void jerTooltipGuardSkipsEmptySlots(GameTestHelper h) {
        h.assertTrue(JerMobTooltipGuard.shouldSkip(2, "3"), "index 3 is past 2 drops");
        h.assertTrue(!JerMobTooltipGuard.shouldSkip(2, "0"), "index 0 is a real drop");
        h.assertTrue(!JerMobTooltipGuard.shouldSkip(2, "1"), "index 1 is a real drop");
        h.assertTrue(JerMobTooltipGuard.shouldSkip(0, "0"), "no drops means skip");
        h.assertTrue(JerMobTooltipGuard.shouldSkip(2, "nope"), "non-numeric slot name");
        h.assertTrue(!JerMobTooltipGuard.shouldSkip(2, null), "null slot name is treated as index 0");
        h.assertTrue(!JerMobTooltipGuard.shouldSkip(2, ""), "empty slot name is treated as index 0");
        h.succeed();
    }
}
