package com.ninjacat.skies.voidloom.compat;

import net.minecraft.core.registries.Registries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.loot.LootContext;
import thedarkcolour.exdeorum.recipe.RecipeUtil;
import thedarkcolour.exdeorum.recipe.sieve.SieveRecipe;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Same recipe list as an Ex Deorum hand sieve, then {@link LoomframeYield#AUTOMATED} so the
 * hopper machine is a little worse than clicking a sieve. Fortune on the mesh still applies first.
 * Loaded only after {@code ModList.isLoaded("exdeorum")}.
 */
public final class ExDeorumSieveBridge {
    private static Set<Item> siftable;
    private static Object recipesKey;

    private ExDeorumSieveBridge() {}

    public static boolean isSiftable(Level level, ItemStack stack) {
        if (stack.isEmpty()) return false;
        var manager = level.getRecipeManager();
        if (siftable == null || recipesKey != manager) {
            recipesKey = manager;
            siftable = new HashSet<>();
            for (var holder : manager.getAllRecipesFor(thedarkcolour.exdeorum.registry.ERecipeTypes.SIEVE.get())) {
                for (ItemStack example : holder.value().ingredient.getItems()) {
                    siftable.add(example.getItem());
                }
            }
        }
        return siftable.contains(stack.getItem());
    }

    public static boolean hasRecipes(Level level, ItemStack mesh, ItemStack input) {
        if (mesh.isEmpty() || input.isEmpty()) return false;
        return !RecipeUtil.getCaches(level).getSieveRecipes(mesh.getItem(), input).isEmpty();
    }

    public static List<ItemStack> roll(ServerLevel level, ItemStack mesh, ItemStack input, RandomSource rand) {
        List<ItemStack> out = new ArrayList<>();
        List<SieveRecipe> recipes = RecipeUtil.getCaches(level).getSieveRecipes(mesh.getItem(), input);
        if (recipes.isEmpty()) return out;
        LootContext ctx = RecipeUtil.emptyLootContext(level);
        int fortune = fortune(level, mesh);
        for (SieveRecipe recipe : recipes) {
            int n = recipe.resultAmount.getInt(ctx);
            for (int i = 0; i < fortune; i++) {
                if (rand.nextFloat() < 0.3F) n += recipe.resultAmount.getInt(ctx);
            }
            n = LoomframeYield.scale(n, rand);
            if (n <= 0) continue;
            ItemStack result = recipe.result;
            while (n > 0) {
                int take = Math.min(n, result.getMaxStackSize());
                out.add(result.copyWithCount(take));
                n -= take;
            }
        }
        return out;
    }

    private static int fortune(ServerLevel level, ItemStack mesh) {
        return level.registryAccess().lookup(Registries.ENCHANTMENT)
                .flatMap(reg -> reg.get(Enchantments.FORTUNE))
                .map(mesh::getEnchantmentLevel)
                .orElse(0);
    }
}
