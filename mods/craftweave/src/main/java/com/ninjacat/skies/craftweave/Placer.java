package com.ninjacat.skies.craftweave;

import net.minecraft.recipebook.ServerPlaceRecipe;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.StackedContents;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.RecipeBookMenu;
import net.minecraft.world.item.crafting.CraftingInput;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.crafting.RecipeHolder;

/**
 * Lays a recipe out on a table from the player's pack: the recipe book's own placement (it returns what is on the
 * grid, finds each ingredient, fills the slots), without the book's rule that the recipe be unlocked first. A
 * bookmark, or a quantity that outruns the grid, needs the ingredients pulled in whether or not the book knows it.
 */
final class Placer extends ServerPlaceRecipe<CraftingInput, CraftingRecipe> {
    @SuppressWarnings("unchecked")
    Placer(AbstractContainerMenu menu) {
        super((RecipeBookMenu<CraftingInput, CraftingRecipe>) menu);
    }

    /** Place one set (or as many as will fit with {@code all}). False when the pack and grid cannot make it. */
    boolean place(ServerPlayer player, RecipeHolder<CraftingRecipe> recipe, boolean all) {
        this.inventory = player.getInventory();
        stackedContents.clear();
        inventory.fillStackedContents(stackedContents);
        menu.fillCraftSlotsStackedContents(stackedContents);
        if (!stackedContents.canCraft(recipe.value(), null)) return false;
        handleRecipeClicked(recipe, all);
        inventory.setChanged();
        return true;
    }

    /** Everything on the grid back into the pack (what will not fit stays on the grid). */
    void clear(ServerPlayer player) {
        this.inventory = player.getInventory();
        clearGrid();
        inventory.setChanged();
    }

    /** How many times the recipe can be made from the pack and the grid together. */
    static int craftable(net.minecraft.world.entity.player.Player player, AbstractContainerMenu menu, RecipeHolder<CraftingRecipe> recipe) {
        StackedContents contents = new StackedContents();
        player.getInventory().fillStackedContents(contents);
        if (menu instanceof RecipeBookMenu<?, ?> book) book.fillCraftSlotsStackedContents(contents);
        return contents.getBiggestCraftableStack(recipe, Integer.MAX_VALUE, null);
    }
}
