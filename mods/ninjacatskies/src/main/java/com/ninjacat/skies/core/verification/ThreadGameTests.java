package com.ninjacat.skies.core.verification;

import com.ninjacat.skies.core.item.ModItems;
import net.minecraft.core.registries.Registries;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingInput;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.Collections;
import java.util.List;

@GameTestHolder("ninjacatskies")
@PrefixGameTestTemplate(false)
public class ThreadGameTests {
    @GameTest(template = "empty")
    public static void threadPacksNineToOneAndUnpacksAgain(GameTestHelper h) {
        Item thread = ModItems.FRAYED_THREAD.get(), skein = ModItems.THREAD_SKEIN.get(), bolt = ModItems.THREAD_BOLT.get();
        h.assertTrue(craft(h, Collections.nCopies(9, thread), 3).is(skein) && craft(h, Collections.nCopies(9, thread), 3).getCount() == 1, "Nine Frayed Thread wind one Thread Skein");
        h.assertTrue(craft(h, Collections.nCopies(9, skein), 3).is(bolt), "Nine skeins make one Thread Bolt");
        ItemStack unwound = craft(h, List.of(skein), 1);
        h.assertTrue(unwound.is(thread) && unwound.getCount() == 9, "A skein unwinds into nine Thread");
        ItemStack unbolted = craft(h, List.of(bolt), 1);
        h.assertTrue(unbolted.is(skein) && unbolted.getCount() == 9, "A bolt unwinds into nine skeins");
        h.succeed();
    }

    @GameTest(template = "empty", timeoutTicks = 200)
    public static void everyCacheTableLoadsAndCanRollAPieceOfALife(GameTestHelper h) {
        var server = h.getLevel().getServer();
        var player = h.makeMockPlayer(GameType.SURVIVAL);
        for (String tier : new String[]{"small", "medium", "large"}) {
            LootTable table = server.reloadableRegistries().getLootTable(ResourceKey.create(Registries.LOOT_TABLE,
                    ResourceLocation.fromNamespaceAndPath("ninjacatskies", "provisions/" + tier)));
            h.assertTrue(table != LootTable.EMPTY, tier + " cache table parses");
            var params = new LootParams.Builder(h.getLevel())
                    .withParameter(LootContextParams.ORIGIN, player.position())
                    .withParameter(LootContextParams.THIS_ENTITY, player)
                    .create(LootContextParamSets.GIFT);
            boolean shard = false, life = false, chicken = false, cow = false;
            for (int i = 0; i < 20000 && !(shard && life && chicken && cow); i++) {
                for (ItemStack stack : table.getRandomItems(params)) {
                    shard |= stack.is(ModItems.THREAD_SHARD.get());
                    life |= stack.is(ModItems.THREAD_OF_RETURN.get());
                    chicken |= stack.is(net.minecraft.world.item.Items.CHICKEN_SPAWN_EGG);
                    cow |= stack.is(net.minecraft.world.item.Items.COW_SPAWN_EGG);
                    h.assertFalse(stack.getItem() instanceof com.ninjacat.skies.core.item.StewardCacheItem, "A cache never holds a cache");
                }
            }
            h.assertTrue(shard && life, tier + " cache can hold a Thread Shard and a Thread of Return");
            h.assertTrue(chicken && cow, tier + " cache can hold livestock eggs for a pad");
        }
        h.succeed();
    }

    private static ItemStack craft(GameTestHelper h, List<Item> items, int width) {
        List<ItemStack> stacks = items.stream().map(ItemStack::new).toList();
        CraftingInput input = CraftingInput.of(width, stacks.size() / width, stacks);
        return h.getLevel().getRecipeManager().getRecipeFor(RecipeType.CRAFTING, input, h.getLevel())
                .map(r -> r.value().assemble(input, h.getLevel().registryAccess())).orElse(ItemStack.EMPTY);
    }
}
