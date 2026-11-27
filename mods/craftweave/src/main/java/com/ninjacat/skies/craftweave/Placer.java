package com.ninjacat.skies.craftweave;

import net.minecraft.recipebook.ServerPlaceRecipe;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.StackedContents;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.RecipeBookMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingInput;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.crafting.RecipeHolder;

import java.util.ArrayList;
import java.util.List;

/**
 * Lays a recipe out on a table from the player's pack: the recipe book's own placement (it returns what is on the
 * grid, finds each ingredient, fills the slots), without the book's rule that the recipe be unlocked first. A
 * bookmark, or a quantity that outruns the grid, needs the ingredients pulled in whether or not the book knows it.
 */
public final class Placer extends ServerPlaceRecipe<CraftingInput, CraftingRecipe> {
    @SuppressWarnings("unchecked")
    public Placer(AbstractContainerMenu menu) {
        super((RecipeBookMenu<CraftingInput, CraftingRecipe>) menu);
    }

    /** Place one set (or as many as will fit with {@code all}). False when the pack and grid cannot make it. */
    public boolean place(ServerPlayer player, RecipeHolder<CraftingRecipe> recipe, boolean all) {
        this.inventory = player.getInventory();
        stackedContents.clear();
        inventory.fillStackedContents(stackedContents);
        menu.fillCraftSlotsStackedContents(stackedContents);
        if (!stackedContents.canCraft(recipe.value(), null)) return false;
        // placing clears the grid first, and vanilla's clear throws whatever the pack cannot take onto the ground
        if (!menu.recipeMatches(recipe) && !gridFits(player)) return false;
        handleRecipeClicked(recipe, all);
        inventory.setChanged();
        return true;
    }

    /** Whether everything on the grid fits back into the pack at once. */
    private boolean gridFits(ServerPlayer player) {
        List<ItemStack> pack = new ArrayList<>();
        for (ItemStack s : player.getInventory().items) pack.add(s.copy());
        for (int slot = 1; slot <= 9; slot++) {
            ItemStack rest = menu.getSlot(slot).getItem().copy();
            for (ItemStack into : pack) {
                if (rest.isEmpty()) break;
                if (into.isEmpty() || !ItemStack.isSameItemSameComponents(into, rest)) continue;
                int move = Math.max(0, Math.min(rest.getCount(), into.getMaxStackSize() - into.getCount()));
                into.grow(move);
                rest.shrink(move);
            }
            if (rest.isEmpty()) continue;
            int free = -1;
            for (int i = 0; i < pack.size() && free < 0; i++) if (pack.get(i).isEmpty()) free = i;
            if (free < 0) return false;
            pack.set(free, rest);
        }
        return true;
    }

    /** Everything on the grid back into the pack. If it does not all fit, it all stays on the grid. */
    public void clear(ServerPlayer player) {
        this.inventory = player.getInventory();
        if (!gridFits(player)) return;
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
