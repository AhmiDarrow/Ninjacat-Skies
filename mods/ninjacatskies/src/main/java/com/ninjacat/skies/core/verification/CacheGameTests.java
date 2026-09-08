package com.ninjacat.skies.core.verification;

import com.ninjacat.skies.core.item.ModItems;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.*;
import net.minecraft.world.level.GameType;
import net.neoforged.neoforge.gametest.*;

@GameTestHolder("ninjacatskies")
@PrefixGameTestTemplate(false)
public class CacheGameTests {
    @GameTest(template="empty")
    public static void eachTierOpensAndConsumesExactlyOne(GameTestHelper h) {
        for (var cache : new Item[]{ModItems.SMALL_STEWARD_CACHE.get(), ModItems.MEDIUM_STEWARD_CACHE.get(), ModItems.LARGE_STEWARD_CACHE.get()}) {
            var player = h.makeMockPlayer(GameType.SURVIVAL);
            player.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(cache, 2));
            var result = cache.use(h.getLevel(), player, InteractionHand.MAIN_HAND);
            h.assertTrue(result.getResult().consumesAction(), "Server successfully opens " + cache);
            h.assertTrue(player.getMainHandItem().getCount() == 1, "Exactly one sealed cache consumed");
            h.assertTrue(player.getInventory().items.stream().anyMatch(s -> !s.isEmpty() && !s.is(cache)), "Supplies delivered");
            cache.use(h.getLevel(), player, InteractionHand.MAIN_HAND);
            h.assertTrue(player.getMainHandItem().getCount() == 1, "Cooldown prevents duplicate rapid opening");
        }
        h.succeed();
    }

    @GameTest(template="empty")
    public static void fullInventoryKeepsRemainderAndDropsSupplies(GameTestHelper h) {
        var player = h.makeMockPlayer(GameType.SURVIVAL);
        player.setPos(h.absoluteVec(new net.minecraft.world.phys.Vec3(1, 2, 1)));
        for (int i = 0; i < 36; i++) player.getInventory().setItem(i, new ItemStack(Items.BEDROCK, 64));
        var cache = ModItems.SMALL_STEWARD_CACHE.get();
        player.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(cache, 2));
        cache.use(h.getLevel(), player, InteractionHand.MAIN_HAND);
        h.assertTrue(player.getMainHandItem().getCount() == 1, "Unopened cache remains in full inventory");
        var drops = h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class, player.getBoundingBox().inflate(3));
        h.assertTrue(drops.size() >= 2, "Both supply rolls dropped rather than lost");
        h.succeed();
    }
}
