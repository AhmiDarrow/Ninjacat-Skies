package com.ninjacat.skies.core.verification;

import com.mojang.authlib.GameProfile;
import com.ninjacat.skies.core.block.ModBlocks;
import com.ninjacat.skies.core.block.YarnBasketBlockEntity;
import com.ninjacat.skies.core.event.DeathBasket;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameType;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.neoforged.neoforge.event.entity.living.LivingDropsEvent;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@GameTestHolder("ninjacatskies")
@PrefixGameTestTemplate(false)
public class BasketGameTests {
    @GameTest(template = "empty")
    public static void aDeathFillsABasketInsteadOfScattering(GameTestHelper h) {
        var player = FakePlayerFactory.get(h.getLevel(), new GameProfile(UUID.randomUUID(), "basket-owner"));
        BlockPos at = h.absolutePos(new BlockPos(1, 2, 1));
        player.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5);
        var event = new LivingDropsEvent(player, h.getLevel().damageSources().generic(), drops(h, at), true);
        NeoForge.EVENT_BUS.post(event);
        h.assertTrue(event.isCanceled(), "The drops were taken into a basket");
        h.assertTrue(h.getLevel().getBlockState(at).is(ModBlocks.YARN_BASKET.get()), "The basket sits where the player died");
        var basket = (YarnBasketBlockEntity) h.getLevel().getBlockEntity(at);
        h.assertTrue(basket != null && basket.items().size() == 2 && player.getUUID().equals(basket.owner()), "It holds both stacks and knows its owner");
        h.getLevel().removeBlock(at, false);
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void aFallIntoTheVoidLeavesTheBasketWhereTheyLastStood(GameTestHelper h) {
        var player = FakePlayerFactory.get(h.getLevel(), new GameProfile(UUID.randomUUID(), "void-faller"));
        BlockPos ground = h.absolutePos(new BlockPos(2, 2, 2));
        CompoundTag tag = new CompoundTag();
        tag.putLong("Pos", ground.asLong());
        tag.putString("Dim", h.getLevel().dimension().location().toString());
        player.getPersistentData().put("ninjacatskies_last_ground", tag);
        player.moveTo(ground.getX() + 0.5, h.getLevel().getMinBuildHeight() - 40, ground.getZ() + 0.5);
        var event = new LivingDropsEvent(player, h.getLevel().damageSources().fellOutOfWorld(), drops(h, ground), false);
        NeoForge.EVENT_BUS.post(event);
        h.assertTrue(event.isCanceled() && h.getLevel().getBlockState(ground).is(ModBlocks.YARN_BASKET.get()), "The basket waits at the last solid footing");
        h.getLevel().removeBlock(ground, false);
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void breakingSpillsEverythingAndStrangersCannot(GameTestHelper h) {
        var owner = h.makeMockPlayer(GameType.SURVIVAL);
        var stranger = h.makeMockPlayer(GameType.SURVIVAL);
        BlockPos at = DeathBasket.stash(h.getLevel(), h.absolutePos(new BlockPos(1, 2, 1)), owner.getUUID(), "owner", null,
                List.of(new ItemStack(Items.DIAMOND, 3), new ItemStack(Items.OAK_LOG, 20)));
        h.assertTrue(at != null, "A basket was placed");
        var state = h.getLevel().getBlockState(at);
        h.assertTrue(state.getDestroyProgress(stranger, h.getLevel(), at) == 0.0F, "A stranger cannot break someone else's basket");
        h.assertTrue(state.getDestroyProgress(owner, h.getLevel(), at) > 0.0F, "The owner can");
        h.getLevel().destroyBlock(at, false);
        int diamonds = 0, logs = 0;
        for (ItemEntity e : h.getLevel().getEntitiesOfClass(ItemEntity.class, new AABB(at).inflate(2))) {
            if (e.getItem().is(Items.DIAMOND)) diamonds += e.getItem().getCount();
            if (e.getItem().is(Items.OAK_LOG)) logs += e.getItem().getCount();
            e.discard();
        }
        h.assertTrue(diamonds == 3 && logs == 20, "Breaking spills every item: " + diamonds + " diamonds, " + logs + " logs");
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void theOwnerGathersItAllBackWithARightClick(GameTestHelper h) {
        var owner = h.makeMockPlayer(GameType.SURVIVAL);
        BlockPos at = DeathBasket.stash(h.getLevel(), h.absolutePos(new BlockPos(1, 2, 1)), owner.getUUID(), "owner", null,
                List.of(new ItemStack(Items.IRON_INGOT, 7)));
        h.assertTrue(at != null, "A basket was placed");
        h.getLevel().getBlockState(at).useWithoutItem(h.getLevel(), owner, new BlockHitResult(Vec3.atCenterOf(at), net.minecraft.core.Direction.UP, at, false));
        h.assertTrue(h.getLevel().getBlockState(at).isAir(), "The basket is gone");
        h.assertTrue(owner.getInventory().countItem(Items.IRON_INGOT) == 7, "Everything went back into the inventory");
        h.succeed();
    }

    private static List<ItemEntity> drops(GameTestHelper h, BlockPos at) {
        List<ItemEntity> out = new ArrayList<>();
        out.add(new ItemEntity(h.getLevel(), at.getX(), at.getY(), at.getZ(), new ItemStack(Items.DIAMOND_PICKAXE)));
        out.add(new ItemEntity(h.getLevel(), at.getX(), at.getY(), at.getZ(), new ItemStack(Items.COBBLESTONE, 40)));
        return out;
    }
}
