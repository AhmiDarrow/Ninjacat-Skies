package com.ninjacat.skies.driftwrecks.verification;

import com.ninjacat.skies.core.block.ModBlocks;
import com.ninjacat.skies.core.block.TensionPostBlock;
import com.ninjacat.skies.core.item.ModItems;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.core.tension.Strand;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

/**
 * The Braid Cord is priced in Strand Filaments and gated on nothing else. It used to want two of
 * Clock / Swarm / Spark seated, which put the Thread of Return most of the way through the pack.
 *
 * These live in driftwrecks because it is the module that loads voidloom and the Core together,
 * so the Strand Filament and the Tension Post both exist at test time.
 */
@GameTestHolder("driftwrecks")
@PrefixGameTestTemplate(false)
public class BraidGameTests {

    /** Right-clicks the Post at (2,1,2) with what the player is holding. */
    private static void useOnPost(GameTestHelper h, net.minecraft.server.level.ServerPlayer player, BlockPos post) {
        BlockPos absolute = h.absolutePos(post);
        h.getLevel().getBlockState(absolute).useItemOn(
                player.getItemInHand(InteractionHand.MAIN_HAND), h.getLevel(), player, InteractionHand.MAIN_HAND,
                new BlockHitResult(Vec3.atCenterOf(absolute), Direction.UP, absolute, false));
    }

    /** A player with no login event behind it: a mock server player syncs Loom Tension and cannot. */
    private static net.neoforged.neoforge.common.util.FakePlayer braider(GameTestHelper h) {
        var player = new net.neoforged.neoforge.common.util.FakePlayer(h.getLevel(),
                new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(), "braid-test"));
        player.setGameMode(GameType.SURVIVAL);
        player.getAbilities().instabuild = false;
        return player;
    }

    private static int filaments(net.minecraft.server.level.ServerPlayer player) {
        var filament = LoomTension.itemOrNull("voidloom:strand_filament");
        int n = 0;
        for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
            ItemStack s = player.getInventory().getItem(i);
            if (filament != null && s.is(filament)) n += s.getCount();
        }
        return n;
    }

    private static int braids(net.minecraft.server.level.ServerPlayer player) {
        int n = 0;
        for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
            ItemStack s = player.getInventory().getItem(i);
            if (s.is(ModItems.BRAID_CORD.get())) n += s.getCount();
        }
        return n;
    }

    @GameTest(template = "empty")
    public static void sixteenFilamentsMakeOneCordWithNoStrandSeated(GameTestHelper h) {
        BlockPos post = new BlockPos(2, 1, 2);
        h.setBlock(post, ModBlocks.TENSION_POST.get());
        var player = braider(h);

        var clowder = LoomTension.clowderOf(player).orElseThrow();
        h.assertTrue(LoomTension.strandBits(clowder) == 0, "This Clowder has seated nothing");

        ItemStack filaments = new ItemStack(LoomTension.itemOrNull("voidloom:strand_filament"), 16);
        player.setItemInHand(InteractionHand.MAIN_HAND, filaments);
        useOnPost(h, player, post);

        h.assertTrue(braids(player) == 1, "Sixteen filaments at the Post give one Braid Cord");
        // The cord lands in the hand slot the filaments just emptied, so count what is left instead.
        h.assertTrue(filaments(player) == 0, "and all sixteen are spent");
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void fifteenFilamentsBuyNothingAndAreNotEaten(GameTestHelper h) {
        BlockPos post = new BlockPos(2, 1, 2);
        h.setBlock(post, ModBlocks.TENSION_POST.get());
        var player = braider(h);

        ItemStack filaments = new ItemStack(LoomTension.itemOrNull("voidloom:strand_filament"),
                TensionPostBlock.BRAID_FILAMENTS - 1);
        player.setItemInHand(InteractionHand.MAIN_HAND, filaments);
        useOnPost(h, player, post);

        h.assertTrue(braids(player) == 0, "Short of the price, no cord");
        h.assertTrue(filaments(player) == TensionPostBlock.BRAID_FILAMENTS - 1,
                "and a refused braid keeps every filament");
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void seatingIsStillTheOnlyWayStrandsAreRecorded(GameTestHelper h) {
        BlockPos post = new BlockPos(2, 1, 2);
        h.setBlock(post, ModBlocks.TENSION_POST.get());
        var player = braider(h);

        ItemStack filaments = new ItemStack(LoomTension.itemOrNull("voidloom:strand_filament"), 64);
        player.setItemInHand(InteractionHand.MAIN_HAND, filaments);
        useOnPost(h, player, post);

        var clowder = LoomTension.clowderOf(player).orElseThrow();
        h.assertTrue(LoomTension.strandBits(clowder) == 0, "Braiding seats nothing");
        for (Strand s : Strand.ALL) {
            h.assertTrue(!LoomTension.isSeated(clowder, s), s.title() + " is not seated by a braid");
        }
        h.succeed();
    }
}
