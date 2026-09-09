package com.ninjacat.skies.guardians.relic.compat;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.storage.loot.LootContext;
import net.neoforged.fml.ModList;
import thedarkcolour.exdeorum.blockentity.AbstractSieveBlockEntity;
import thedarkcolour.exdeorum.blockentity.CompressedSieveBlockEntity;
import thedarkcolour.exdeorum.blockentity.SieveBlockEntity;
import thedarkcolour.exdeorum.blockentity.logic.SieveLogic;
import thedarkcolour.exdeorum.recipe.RecipeUtil;
import thedarkcolour.exdeorum.recipe.sieve.SieveRecipe;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Grindcore's Grit passive against the real Ex Deorum API: a Grindcore wearer's hand sieves get one extra fortune-style
 * roll. Ex Deorum applies Fortune as "per level, a 30 % chance to add another {@code resultAmount} roll" (SieveLogic.
 * getResultAmount); this class adds exactly one such level, without touching the sieve's private state.
 * <p>
 * How: the right-click that finishes a sieve is not distinguishable from any other from outside, so the relic records
 * the sieve's contents and mesh on every right-click of a sieve by a wearer, and on the wearer's next tick checks whether
 * that sieve has emptied. If it did, the recorded contents just dropped and the bonus roll is made for each matching
 * recipe, spawned through the sieve's own {@link AbstractSieveBlockEntity#handleResultItem} so it pops out like any drop.
 * Only referenced when Ex Deorum is loaded ({@link #present()}), so the class never resolves otherwise.
 */
public final class SieveCompat {
    private SieveCompat() {}

    public static boolean present() { return ModList.get().isLoaded("exdeorum"); }

    private record Pending(ServerLevel level, BlockPos pos, ItemStack contents, ItemStack mesh, boolean compressed, int expires) {}
    private static final Map<UUID, Pending> PENDING = new HashMap<>();

    /** Call from RightClickBlock (before the sieve handles the click). */
    public static void onRightClick(ServerPlayer p, ServerLevel level, BlockPos pos) {
        BlockEntity be = level.getBlockEntity(pos);
        if (!isHandSieve(be) || !(be instanceof AbstractSieveBlockEntity sieve)) return;
        SieveLogic logic = sieve.getLogic();
        ItemStack contents = logic.getContents();
        if (contents.isEmpty()) return;
        PENDING.put(p.getUUID(), new Pending(level, pos.immutable(), contents.copy(), logic.getMesh().copy(), be instanceof CompressedSieveBlockEntity, p.tickCount + 2));
    }

    /** Call from the wearer's tick. */
    public static void tick(ServerPlayer p) {
        Pending pend = PENDING.get(p.getUUID());
        if (pend == null) return;
        if (p.tickCount > pend.expires()) { PENDING.remove(p.getUUID()); return; }
        if (pend.level() != p.serverLevel()) { PENDING.remove(p.getUUID()); return; }
        if (!(pend.level().getBlockEntity(pend.pos()) instanceof AbstractSieveBlockEntity sieve)) { PENDING.remove(p.getUUID()); return; }
        if (!sieve.getLogic().getContents().isEmpty()) return;                 // still sifting; keep watching until it expires
        PENDING.remove(p.getUUID());
        bonusRoll(pend, sieve);
    }

    private static void bonusRoll(Pending pend, AbstractSieveBlockEntity sieve) {
        ServerLevel level = pend.level();
        List<? extends SieveRecipe> recipes = pend.compressed()
                ? RecipeUtil.getCaches(level).getCompressedSieveRecipes(pend.contents().getItem(), pend.mesh())
                : RecipeUtil.getCaches(level).getSieveRecipes(pend.contents().getItem(), pend.mesh());
        if (recipes == null || recipes.isEmpty()) return;
        LootContext ctx = RecipeUtil.emptyLootContext(level);
        boolean any = false;
        for (SieveRecipe r : recipes) {
            if (level.random.nextFloat() >= 0.3F) continue;                    // one fortune level, Ex Deorum's own odds
            int n = r.resultAmount.getInt(ctx);
            if (n <= 0) continue;
            sieve.handleResultItem(r.result.copyWithCount(n), level, level.random);
            any = true;
        }
        if (any) {
            BlockPos pos = pend.pos();
            level.sendParticles(ParticleTypes.CRIT, pos.getX() + 0.5, pos.getY() + 1.0, pos.getZ() + 0.5, 6, 0.3, 0.1, 0.3, 0.05);
            level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, Blocks.GRAVEL.defaultBlockState()), pos.getX() + 0.5, pos.getY() + 0.9, pos.getZ() + 0.5, 8, 0.3, 0.05, 0.3, 0.02);
        }
    }

    /** True for the plain (non-mechanical) sieves the passive applies to. */
    public static boolean isHandSieve(BlockEntity be) { return be instanceof SieveBlockEntity || be instanceof CompressedSieveBlockEntity; }
}
