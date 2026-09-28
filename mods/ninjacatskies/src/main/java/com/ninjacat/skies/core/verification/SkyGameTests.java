package com.ninjacat.skies.core.verification;

import com.ninjacat.skies.core.sky.FrayMath;
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

    @GameTest(template = "empty")
    public static void theFrayGathersAndLights(GameTestHelper h) {
        h.assertTrue(FrayMath.strandAlpha(0, 0F) == 1F && FrayMath.strandAlpha(FrayMath.STRANDS - 1, 0F) == 1F,
                "Every thread hangs while nothing is rewoven");
        h.assertTrue(FrayMath.strandAlpha(1, 0.5F) == 1F && FrayMath.strandAlpha(FrayMath.STRANDS - 1, 0.5F) == 0F,
                "Threads gather one at a time, outermost first");
        h.assertTrue(FrayMath.strandAlpha(0, 1F) == 1F && FrayMath.strandAlpha(1, 1F) == 0F,
                "Only the spine remains at full Reweave");
        h.assertTrue(!FrayMath.lit(0.95F) && FrayMath.lit(1F), "The thread lights only when the whole server has rewoven");
        h.assertTrue(FrayMath.glow(0.9F) == 0F && FrayMath.glow(1F) == 1F, "The glow ramps in over the last few percent");
        h.assertTrue(FrayMath.halfWidth(1, 0F) > FrayMath.halfWidth(1, 1F), "Threads thin as the server reweaves");
        float open = FrayMath.cutHalfWidth(1F, 0F), half = FrayMath.cutHalfWidth(1F, 0.5F), closed = FrayMath.cutHalfWidth(1F, 1F);
        h.assertTrue(open > half && half > closed && closed == 0F, "The dark cut narrows and is gone when rewoven");
        h.assertTrue(FrayMath.heightFade(0F) == 1F && FrayMath.heightFade(FrayMath.DOCK) == 1F && FrayMath.heightFade(1F) == 0F,
                "The cut is solid from its root in the void past the gate-path and frays out at the top");
        float[] low = new float[2], high = new float[2];
        FrayMath.offset(3, 0.1F, 0F, 0F, low);
        FrayMath.offset(3, 1F, 0F, 0F, high);
        h.assertTrue(Math.hypot(high[0], high[1]) > Math.hypot(low[0], low[1]), "Threads gather at the root and splay as they climb");
        h.assertTrue(FrayMath.BELOW > 64 + 66 && FrayMath.DOCK > 0.5F, "The root sits below the bottom of the world");
        h.assertTrue(FrayMath.distanceFade(100) == 1F && FrayMath.distanceFade(7000) == 0F, "A far pad sees a faint line, then nothing");
        h.succeed();
    }
}
