package com.ninjacat.skies.guardians.relic.compat;

import cy.jdkdigital.productivebees.common.block.entity.AdvancedBeehiveBlockEntity;
import cy.jdkdigital.productivebees.common.block.entity.AdvancedBeehiveBlockEntityAbstract;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.neoforged.fml.ModList;

/**
 * Hivecall's Keeper passive against the real Productive Bees API. Productive Bees hives (and nests) tick through the
 * public static {@code tick(level, pos, state, be)} of their block entity; giving one of them an extra tick every ten
 * ticks is exactly "ticks 10 % faster" — bees in the hive finish their work sooner and the hive's own timers run
 * ahead — without touching any private field. Only referenced when Productive Bees is loaded ({@link #present()}).
 */
public final class HiveCompat {
    private HiveCompat() {}

    public static boolean present() { return ModList.get().isLoaded("productivebees"); }

    /** @return true if the block entity was a Productive Bees hive and got its extra tick. */
    public static boolean extraTick(ServerLevel level, BlockPos pos, BlockEntity be) {
        if (be instanceof AdvancedBeehiveBlockEntity hive) { AdvancedBeehiveBlockEntity.tick(level, pos, hive.getBlockState(), hive); return true; }
        if (be instanceof AdvancedBeehiveBlockEntityAbstract hive) { AdvancedBeehiveBlockEntityAbstract.tick(level, pos, hive.getBlockState(), hive); return true; }
        return false;
    }
}
