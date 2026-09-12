package com.ninjacat.skies.guardians.entity.bosses;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Blocks;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

/** Mechanic block ledgers survive a save/reload so a mid-fight restart can put the arena back. */
@GameTestHolder("guardians")
@PrefixGameTestTemplate(false)
public class LedgerGameTests {
    @GameTest(template = "empty")
    public static void ledgerRoundTrip(GameTestHelper h) {
        ServerLevel level = h.getLevel();
        BlockPos p = h.absolutePos(new BlockPos(2, 2, 2));
        level.setBlock(p, Blocks.STONE.defaultBlockState(), 3);
        Mech.Ledger led = new Mech.Ledger();
        led.set(level, p, Blocks.DIRT.defaultBlockState());
        h.assertTrue(level.getBlockState(p).is(Blocks.DIRT), "ledger overwrote the block");
        CompoundTag tag = new CompoundTag();
        led.save(tag, "L");
        Mech.Ledger loaded = new Mech.Ledger();
        loaded.load(tag, "L", level);
        h.assertTrue(loaded.has(p), "position remembered after NBT");
        loaded.restoreAll(level);
        h.assertTrue(level.getBlockState(p).is(Blocks.STONE), "original state restored");
        h.succeed();
    }
}
