package com.ninjacat.skies.core.verification;

import com.ninjacat.skies.core.event.DismountRequests;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.entity.EntityType;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("ninjacatskies")
@PrefixGameTestTemplate(false)
public class DismountGameTests {
    @GameTest(template = "empty")
    public static void sneakSteersAndOnlyTheDismountKeyGetsYouOff(GameTestHelper h) {
        var pig = h.spawn(EntityType.PIG, new BlockPos(1, 2, 1));
        var rider = h.makeMockServerPlayerInLevel();
        BlockPos at = h.absolutePos(new BlockPos(1, 2, 1));
        rider.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5);
        h.assertTrue(rider.startRiding(pig, true), "The rider mounts");

        rider.setShiftKeyDown(true);
        rider.rideTick();
        h.assertTrue(rider.isPassenger(), "Holding sneak no longer dismounts");
        rider.setShiftKeyDown(false);

        DismountRequests.request(rider);
        rider.rideTick();
        h.assertFalse(rider.isPassenger(), "The Dismount key gets the rider off");
        h.assertFalse(rider.isShiftKeyDown(), "The one-tick sneak used for the dismount is released");

        h.assertTrue(rider.startRiding(pig, true), "The rider mounts again");
        rider.rideTick();
        h.assertTrue(rider.isPassenger(), "A used request does not linger");
        rider.stopRiding();
        pig.discard();
        rider.discard();
        h.succeed();
    }
}
