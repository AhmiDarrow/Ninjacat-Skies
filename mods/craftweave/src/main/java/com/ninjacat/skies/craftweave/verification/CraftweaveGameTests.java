package com.ninjacat.skies.craftweave.verification;

import com.ninjacat.skies.craftweave.CraftTables;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.NonNullList;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.CraftingBookCategory;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.ShapelessRecipe;
import net.minecraft.world.level.block.Blocks;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

/** Craftweave at a real crafting table: a typed quantity, and two recipes that share a grid. */
@GameTestHolder("craftweave")
@PrefixGameTestTemplate(false)
public final class CraftweaveGameTests {
    private CraftweaveGameTests() {}

    @SuppressWarnings({"removal", "deprecation"})
    private static ServerPlayer player(GameTestHelper h) {
        return h.makeMockServerPlayerInLevel();
    }

    private static CraftingMenu table(GameTestHelper h, ServerPlayer player) {
        BlockPos pos = new BlockPos(1, 2, 1);
        h.setBlock(pos, Blocks.CRAFTING_TABLE);
        CraftingMenu menu = new CraftingMenu(1, player.getInventory(), ContainerLevelAccess.create(h.getLevel(), h.absolutePos(pos)));
        player.containerMenu = menu;
        CraftTables.owned(menu, player);
        return menu;
    }

    @GameTest(template = "empty")
    public static void aTypedQuantityCraftsThatMany(GameTestHelper h) {
        ServerPlayer player = player(h);
        try {
            CraftingMenu menu = table(h, player);
            h.assertTrue(CraftTables.isTable(menu), "The vanilla crafting table is a Craftweave table");
            menu.getSlot(5).set(new ItemStack(Items.OAK_PLANKS, 12));
            menu.slotsChanged(menu.getSlot(5).container);
            h.assertTrue(menu.getSlot(0).getItem().is(Items.OAK_BUTTON), "One plank makes a button");
            int made = CraftTables.craft(player, 5);
            h.assertTrue(made == 5, "Five were asked for and five were made, got " + made);
            h.assertTrue(player.getInventory().countItem(Items.OAK_BUTTON) == 5, "They went into the pack");
            h.assertTrue(menu.getSlot(5).getItem().getCount() == 7, "Five planks were used, seven are left");
            int rest = CraftTables.craft(player, 64);
            h.assertTrue(rest == 7 && menu.getSlot(5).getItem().isEmpty(), "Asking for more than the grid holds makes what it can, got " + rest);
            h.succeed();
        } finally {
            h.getLevel().getServer().getPlayerList().remove(player);
        }
    }

    @GameTest(template = "empty")
    public static void conflictingRecipesCycleAndTheChoiceIsKept(GameTestHelper h) {
        var manager = h.getLevel().getRecipeManager();
        List<RecipeHolder<?>> original = new ArrayList<>(manager.getRecipes());
        ServerPlayer player = player(h);
        try {
            // two recipes that both take a single dirt: a conflict the table cannot settle by itself
            List<RecipeHolder<?>> with = new ArrayList<>(original);
            with.add(new RecipeHolder<>(ResourceLocation.fromNamespaceAndPath("craftweave", "test_dirt_stick"),
                    new ShapelessRecipe("", CraftingBookCategory.MISC, new ItemStack(Items.STICK), NonNullList.of(Ingredient.EMPTY, Ingredient.of(Items.DIRT)))));
            with.add(new RecipeHolder<>(ResourceLocation.fromNamespaceAndPath("craftweave", "test_dirt_string"),
                    new ShapelessRecipe("", CraftingBookCategory.MISC, new ItemStack(Items.STRING), NonNullList.of(Ingredient.EMPTY, Ingredient.of(Items.DIRT)))));
            manager.replaceRecipes(with);
            CraftingMenu menu = table(h, player);
            menu.getSlot(5).set(new ItemStack(Items.DIRT, 4));
            menu.slotsChanged(menu.getSlot(5).container);
            var matches = CraftTables.matches(h.getLevel(), CraftTables.input(menu));
            h.assertTrue(matches.size() == 2, "Both recipes match the grid, got " + matches.size());
            var first = menu.getSlot(0).getItem().getItem();
            CraftTables.cycle(player, 1);
            var second = menu.getSlot(0).getItem().getItem();
            h.assertTrue(first != second && (second == Items.STICK || second == Items.STRING), "Cycling shows the other recipe, got " + second);
            // clear the grid and put the dirt back: the pick holds
            menu.getSlot(5).set(ItemStack.EMPTY);
            menu.slotsChanged(menu.getSlot(5).container);
            menu.getSlot(5).set(new ItemStack(Items.DIRT, 4));
            menu.slotsChanged(menu.getSlot(5).container);
            h.assertTrue(menu.getSlot(0).getItem().is(second), "The table remembers the pick, got " + menu.getSlot(0).getItem());
            int made = CraftTables.craft(player, 2);
            h.assertTrue(made == 2 && player.getInventory().countItem(second) == 2, "The picked recipe is the one crafted");
            CraftTables.cycle(player, -1);
            h.assertTrue(menu.getSlot(0).getItem().is(first), "Cycling back returns to the first");
            h.succeed();
        } finally {
            manager.replaceRecipes(original);
            h.getLevel().getServer().getPlayerList().remove(player);
        }
    }

    @GameTest(template = "empty")
    public static void aQuantityRefillsTheGridFromThePack(GameTestHelper h) {
        ServerPlayer player = player(h);
        try {
            CraftingMenu menu = table(h, player);
            player.getInventory().add(new ItemStack(Items.OAK_PLANKS, 20));
            menu.getSlot(5).set(new ItemStack(Items.OAK_PLANKS, 1));
            menu.slotsChanged(menu.getSlot(5).container);
            int made = CraftTables.craft(player, 10);
            h.assertTrue(made == 10, "Ten buttons from one plank on the grid and twenty in the pack, got " + made);
            h.assertTrue(player.getInventory().countItem(Items.OAK_BUTTON) == 10, "The buttons are in the pack");
            int planksLeft = player.getInventory().countItem(Items.OAK_PLANKS);
            for (int i = 1; i <= 9; i++) planksLeft += menu.getSlot(i).getItem().is(Items.OAK_PLANKS) ? menu.getSlot(i).getItem().getCount() : 0;
            h.assertTrue(planksLeft == 11, "Ten of the twenty-one planks were used, got " + planksLeft + " left");
            h.succeed();
        } finally {
            h.getLevel().getServer().getPlayerList().remove(player);
        }
    }

    @GameTest(template = "empty")
    public static void aBookmarkLaysOutARecipeFromThePackAndClearPutsItBack(GameTestHelper h) {
        ServerPlayer player = player(h);
        try {
            CraftingMenu menu = table(h, player);
            player.getInventory().add(new ItemStack(Items.COBBLESTONE, 16));
            var furnace = ResourceLocation.withDefaultNamespace("furnace");
            h.assertFalse(player.getRecipeBook().contains(furnace), "The test player has not unlocked the furnace");
            h.assertTrue(CraftTables.place(player, furnace, false), "The bookmark lays the furnace out anyway");
            int stones = 0;
            for (int i = 1; i <= 9; i++) if (menu.getSlot(i).getItem().is(Items.COBBLESTONE)) stones += menu.getSlot(i).getItem().getCount();
            h.assertTrue(stones == 8 && menu.getSlot(0).getItem().is(Items.FURNACE), "Eight cobblestone in a ring and a furnace offered, got " + stones);
            h.assertTrue(player.getInventory().countItem(Items.COBBLESTONE) == 8, "They came out of the pack");
            CraftTables.clear(player);
            boolean empty = true;
            for (int i = 1; i <= 9; i++) empty &= menu.getSlot(i).getItem().isEmpty();
            h.assertTrue(empty && player.getInventory().countItem(Items.COBBLESTONE) == 16, "Clear puts all sixteen back in the pack");
            h.assertFalse(CraftTables.place(player, ResourceLocation.withDefaultNamespace("diamond_block"), false), "Without the diamonds nothing is laid out");
            h.succeed();
        } finally {
            h.getLevel().getServer().getPlayerList().remove(player);
        }
    }
}
