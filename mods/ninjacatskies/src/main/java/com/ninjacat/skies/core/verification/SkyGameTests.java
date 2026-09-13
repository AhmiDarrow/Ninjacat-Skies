package com.ninjacat.skies.core.verification;

import com.ninjacat.skies.core.sky.SunderedSkyMath;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("ninjacatskies")
@PrefixGameTestTemplate(false)
public class SkyGameTests {
    @GameTest(template = "empty")
    public static void sunderedSkyHealsAndKeepsTheCut(GameTestHelper h) {
        h.assertTrue(SunderedSkyMath.dayness(6000, 0) > 0.9F, "Day sky peaks at noon");
        h.assertTrue(SunderedSkyMath.dayness(18000, 0) < 0.1F, "Night sky rests at midnight");
        float torn = SunderedSkyMath.cutHalfWidth(SunderedSkyMath.heal(0, false));
        float seated = SunderedSkyMath.cutHalfWidth(SunderedSkyMath.heal(9, false));
        float done = SunderedSkyMath.cutHalfWidth(SunderedSkyMath.heal(9, true));
        h.assertTrue(torn > seated && seated >= done, "The Cut thins as Strands seat and closes when rewoven");
        h.assertTrue(SunderedSkyMath.heal(0, false) == 0F && SunderedSkyMath.heal(0, true) == 1F, "Rewoven pads are fully healed");
        float[] gold = SunderedSkyMath.cutGold(0, 1);
        h.assertTrue(gold[0] > gold[2], "The Cut reads gold, not teal");
        h.assertTrue(SunderedSkyMath.cutDistance(-0.76F, 0F, 0.62F) < 0.05F, "A point on the Cut plane sits in the seam");
        h.succeed();
    }
}
