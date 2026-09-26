package com.ninjacat.skies.craftweave;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.WeakHashMap;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.RecipeBookMenu;
import net.minecraft.world.inventory.RecipeBookType;
import net.minecraft.world.inventory.ResultContainer;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingInput;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.Level;

/**
 * What Craftweave knows about a crafting table: which menus count (a 3x3 crafting grid with a recipe book: the vanilla
 * table, the Tribal Bench, most modded tables), every recipe the grid matches in a fixed order, and which of them each
 * player picked the last time those recipes met. The server makes the result from that pick; the client only draws.
 */
public final class CraftTables {
    /** Recipes a player chose when they met another recipe on the same grid, most recent last. */
    private static final Map<UUID, LinkedHashSet<ResourceLocation>> PICKS = new ConcurrentHashMap<>();
    /** Which player each open crafting menu belongs to (menus built without a player reference, like the bench's). */
    private static final Map<AbstractContainerMenu, ServerPlayer> OWNERS = java.util.Collections.synchronizedMap(new WeakHashMap<>());
    /** Most crafts one request may make: a full inventory's worth. */
    public static final int MAX_ITEMS = 36 * 64;

    private CraftTables() {}

    public static boolean isTable(AbstractContainerMenu menu) {
        return menu instanceof RecipeBookMenu<?, ?> book && book.getRecipeBookType() == RecipeBookType.CRAFTING
                && book.getGridWidth() == 3 && book.getGridHeight() == 3 && book.getResultSlotIndex() == 0 && book.slots.size() > 9;
    }

    public static void owned(AbstractContainerMenu menu, ServerPlayer player) {
        OWNERS.put(menu, player);
    }

    public static ServerPlayer owner(AbstractContainerMenu menu) {
        return OWNERS.get(menu);
    }

    /** The grid's nine places as a crafting input: menu slots 1 to 9, as vanilla and the recipe book lay them out. */
    public static CraftingInput input(AbstractContainerMenu menu) {
        List<ItemStack> items = new ArrayList<>(9);
        for (int i = 1; i <= 9; i++) items.add(menu.getSlot(i).getItem());
        return CraftingInput.of(3, 3, items);
    }

    /** Every crafting recipe the input matches, in the order of their ids (the same on both sides). */
    public static List<RecipeHolder<CraftingRecipe>> matches(Level level, CraftingInput input) {
        if (input.isEmpty()) return List.of();
        List<RecipeHolder<CraftingRecipe>> out = new ArrayList<>(level.getRecipeManager().getRecipesFor(RecipeType.CRAFTING, input, level));
        out.sort(Comparator.comparing(holder -> holder.id().toString()));
        return out;
    }

    /** The recipe a player gets from these matches: their latest pick among them, else the table's own choice. */
    public static RecipeHolder<CraftingRecipe> chosen(Player player, List<RecipeHolder<CraftingRecipe>> matches) {
        Set<ResourceLocation> picks = PICKS.get(player.getUUID());
        if (picks != null) {
            List<ResourceLocation> order = new ArrayList<>(picks);
            for (int i = order.size() - 1; i >= 0; i--)
                for (RecipeHolder<CraftingRecipe> holder : matches) if (holder.id().equals(order.get(i))) return holder;
        }
        return null;
    }

    /** Remember that the player chose this recipe over the others it met. */
    public static void pick(Player player, RecipeHolder<CraftingRecipe> recipe, List<RecipeHolder<CraftingRecipe>> among) {
        LinkedHashSet<ResourceLocation> picks = PICKS.computeIfAbsent(player.getUUID(), id -> new LinkedHashSet<>());
        for (RecipeHolder<CraftingRecipe> other : among) picks.remove(other.id());
        picks.add(recipe.id());
        while (picks.size() > 256) picks.remove(picks.iterator().next());
    }

    public static void forget(UUID player) {
        PICKS.remove(player);
    }

    /**
     * After the table has made its own result: if this player picked a different one of the matching recipes, put
     * that one's output in the result slot instead.
     */
    public static void applyPick(AbstractContainerMenu menu, Player player) {
        if (!(player instanceof ServerPlayer server) || !isTable(menu)) return;
        List<RecipeHolder<CraftingRecipe>> matches = matches(server.level(), input(menu));
        if (matches.size() < 2) return;
        RecipeHolder<CraftingRecipe> pick = chosen(server, matches);
        if (pick == null) return;
        Slot result = menu.getSlot(0);
        ItemStack output = pick.value().assemble(input(menu), server.level().registryAccess());
        if (ItemStack.isSameItemSameComponents(output, result.getItem()) && output.getCount() == result.getItem().getCount()) return;
        if (result.container instanceof ResultContainer container) container.setRecipeUsed(pick);
        result.set(output);
        menu.broadcastChanges();
    }

    /** Step to the next (or previous) matching recipe and remember it. */
    public static void cycle(ServerPlayer player, int direction) {
        AbstractContainerMenu menu = player.containerMenu;
        if (!isTable(menu)) return;
        List<RecipeHolder<CraftingRecipe>> matches = matches(player.level(), input(menu));
        if (matches.size() < 2) return;
        int current = index(player.level(), menu, matches);
        RecipeHolder<CraftingRecipe> next = matches.get(Math.floorMod(current + (direction < 0 ? -1 : 1), matches.size()));
        pick(player, next, matches);
        applyPick(menu, player);
    }

    /** Which of the matches the result slot is showing now (0 when none is recognisable). */
    public static int index(Level level, AbstractContainerMenu menu, List<RecipeHolder<CraftingRecipe>> matches) {
        ItemStack shown = menu.getSlot(0).getItem();
        CraftingInput input = input(menu);
        for (int i = 0; i < matches.size(); i++) {
            ItemStack output = matches.get(i).value().assemble(input, level.registryAccess());
            if (ItemStack.isSameItemSameComponents(output, shown)) return i;
        }
        return 0;
    }

    /** The recipe the result slot is showing, or null when the grid makes nothing. */
    public static RecipeHolder<CraftingRecipe> showing(Level level, AbstractContainerMenu menu) {
        if (menu.getSlot(0).getItem().isEmpty()) return null;
        List<RecipeHolder<CraftingRecipe>> matches = matches(level, input(menu));
        return matches.isEmpty() ? null : matches.get(index(level, menu, matches));
    }

    /**
     * Craft until {@code wanted} items have come off the table. Each craft is the table's own shift-click, so every
     * table's rules (remainders, achievements, the Tribal Bench's shared grid) still apply; when the grid runs dry the
     * same recipe is laid out again from the pack, until the pack runs dry too. Returns how many items were made.
     */
    public static int craft(ServerPlayer player, int wanted) {
        AbstractContainerMenu menu = player.containerMenu;
        if (!isTable(menu) || wanted <= 0) return 0;
        wanted = Math.min(wanted, MAX_ITEMS);
        RecipeHolder<CraftingRecipe> recipe = showing(player.level(), menu);
        if (recipe == null) return 0;
        Placer placer = new Placer(menu);
        int made = 0;
        while (made < wanted) {
            if (menu.getSlot(0).getItem().isEmpty()) {
                // the grid is spent: lay the same recipe out again from the pack, and keep to it if others match too
                if (!placer.place(player, recipe, true)) break;
                List<RecipeHolder<CraftingRecipe>> matches = matches(player.level(), input(menu));
                if (matches.size() > 1) pick(player, recipe, matches);
                applyPick(menu, player);
                if (menu.getSlot(0).getItem().isEmpty()) break;
            }
            ItemStack moved = menu.quickMoveStack(player, 0);
            if (moved.isEmpty()) break;          // the pack is full
            made += moved.getCount();
            applyPick(menu, player);
        }
        menu.broadcastChanges();
        return made;
    }

    /** Everything on the grid back into the pack. */
    public static void clear(ServerPlayer player) {
        AbstractContainerMenu menu = player.containerMenu;
        if (!isTable(menu)) return;
        new Placer(menu).clear(player);
        menu.broadcastChanges();
    }

    /**
     * Lay a bookmarked recipe out on the grid from the pack (one set, or as many as fit with {@code all}), whether or
     * not the recipe book has it unlocked. Returns false when the pack cannot make it.
     */
    public static boolean place(ServerPlayer player, ResourceLocation id, boolean all) {
        AbstractContainerMenu menu = player.containerMenu;
        if (!isTable(menu)) return false;
        var holder = player.level().getRecipeManager().byKey(id).orElse(null);
        if (holder == null || !(holder.value() instanceof CraftingRecipe)) return false;
        @SuppressWarnings("unchecked") RecipeHolder<CraftingRecipe> recipe = (RecipeHolder<CraftingRecipe>) holder;
        if (!recipe.value().canCraftInDimensions(3, 3)) return false;
        boolean placed = new Placer(menu).place(player, recipe, all);
        if (placed) {
            List<RecipeHolder<CraftingRecipe>> matches = matches(player.level(), input(menu));
            if (matches.size() > 1) pick(player, recipe, matches);
            applyPick(menu, player);
        }
        menu.broadcastChanges();
        return placed;
    }

    /** How many items of this recipe the pack and grid can make together. */
    public static int canMake(Player player, AbstractContainerMenu menu, RecipeHolder<CraftingRecipe> recipe) {
        int per = Math.max(1, recipe.value().getResultItem(player.level().registryAccess()).getCount());
        return Placer.craftable(player, menu, recipe) * per;
    }
}
