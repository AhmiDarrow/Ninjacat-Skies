package com.ninjacat.skies.driftwrecks.rift;

import com.mojang.authlib.GameProfile;
import com.ninjacat.skies.guardians.arena.ArenaManager;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.util.FakePlayer;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.UUID;

/** When a rift ends, only the members still in its chamber go back to the wreck; one who died and respawned at home stays home. */
@GameTestHolder("driftwrecks")
@PrefixGameTestTemplate(false)
public class RiftReturnGameTests {
    @GameTest(template = "empty")
    public static void riftEndReturnsOnlyThoseInside(GameTestHelper h) {
        ServerLevel level = h.getLevel();
        ServerLevel arena = ArenaManager.arenaLevel(level.getServer());
        if (arena == null) { h.fail("no arena level"); return; }   // lang-exempt: GameTest assertion message
        BlockPos wreck = h.absolutePos(new BlockPos(2, 2, 2));
        level.setBlock(wreck.below(), Blocks.STONE.defaultBlockState(), 3);
        RiftManager.Rift r = new RiftManager.Rift();
        r.origin = new BlockPos(-RiftManager.SPACING * 9, RiftManager.FLOOR_Y, arena == level.getServer().overworld() ? -200000 : 0);

        FakePlayer inside = FakePlayerFactory.get(level, new GameProfile(UUID.nameUUIDFromBytes("rift-inside".getBytes()), "RiftInside"));
        FakePlayer home = FakePlayerFactory.get(level, new GameProfile(UUID.nameUUIDFromBytes("rift-home".getBytes()), "RiftHome"));
        for (FakePlayer p : new FakePlayer[] {inside, home}) {
            p.moveTo(wreck.getX() + 0.5, wreck.getY(), wreck.getZ() + 0.5, 0, 0);
            RiftManager.storeReturn(p);
        }
        // one is still in the chamber; the other died there and respawned at home, far from the wreck
        inside.setServerLevel(arena);
        inside.moveTo(r.origin.getX() + 0.5, r.origin.getY(), r.origin.getZ() + 0.5, 0, 0);
        BlockPos spawn = h.absolutePos(new BlockPos(0, 2, 0)).offset(40, 0, 40);
        home.moveTo(spawn.getX() + 0.5, spawn.getY(), spawn.getZ() + 0.5, 0, 0);

        RiftManager.endFor(inside, arena, r);
        RiftManager.endFor(home, arena, r);
        h.assertTrue(inside.position().distanceTo(Vec3.atBottomCenterOf(wreck)) < 1.0, "the member in the chamber is back at the wreck");   // lang-exempt: GameTest assertion message
        h.assertTrue(home.position().distanceTo(Vec3.atBottomCenterOf(spawn)) < 1.0, "the member who respawned at home stays home");   // lang-exempt: GameTest assertion message
        h.assertFalse(RiftManager.hasReturn(inside) || RiftManager.hasReturn(home), "both return points are spent");   // lang-exempt: GameTest assertion message
        h.succeed();
    }
}
