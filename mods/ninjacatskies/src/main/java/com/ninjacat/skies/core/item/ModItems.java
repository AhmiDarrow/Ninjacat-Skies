package com.ninjacat.skies.core.item;

import com.ninjacat.skies.core.NinjacatSkies;
import com.ninjacat.skies.core.block.ModBlocks;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(NinjacatSkies.MOD_ID);

    public static final DeferredItem<WhiskerCodexItem> WHISKER_CODEX = ITEMS.register(
            "whisker_codex",
            () -> new WhiskerCodexItem(new Item.Properties().stacksTo(1))
    );

    public static final DeferredItem<Item> FRAYED_THREAD = ITEMS.registerSimpleItem(
            "frayed_thread",
            new Item.Properties()
    );

    public static final DeferredItem<StewardCacheItem> SMALL_STEWARD_CACHE = ITEMS.register(
            "small_steward_cache", () -> new StewardCacheItem("small"));
    public static final DeferredItem<StewardCacheItem> MEDIUM_STEWARD_CACHE = ITEMS.register(
            "medium_steward_cache", () -> new StewardCacheItem("medium"));
    public static final DeferredItem<StewardCacheItem> LARGE_STEWARD_CACHE = ITEMS.register(
            "large_steward_cache", () -> new StewardCacheItem("large"));

    public static final DeferredItem<CodexPageItem> CODEX_PAGE = ITEMS.register(
            "codex_page",
            () -> new CodexPageItem(new Item.Properties().stacksTo(16))
    );

    // Tokens are quest proof: earned once per Strand, seated at a Tension Post, never crafted or consumed by recipes.
    private static Item.Properties tokenProps() {
        return new Item.Properties().stacksTo(16);
    }

    public static final DeferredItem<StrandTokenItem> STRAND_TOKEN_SOIL = ITEMS.register(
            "strand_token_soil",
            () -> new StrandTokenItem("soil", tokenProps())
    );

    public static final DeferredItem<StrandTokenItem> STRAND_TOKEN_STONE = ITEMS.register(
            "strand_token_stone",
            () -> new StrandTokenItem("stone", tokenProps())
    );

    public static final DeferredItem<StrandTokenItem> STRAND_TOKEN_SPROUT = ITEMS.register(
            "strand_token_sprout",
            () -> new StrandTokenItem("sprout", tokenProps())
    );

    public static final DeferredItem<StrandTokenItem> STRAND_TOKEN_CLAW = ITEMS.register(
            "strand_token_claw",
            () -> new StrandTokenItem("claw", tokenProps())
    );

    public static final DeferredItem<StrandTokenItem> STRAND_TOKEN_SPARK = ITEMS.register(
            "strand_token_spark",
            () -> new StrandTokenItem("spark", tokenProps())
    );

    public static final DeferredItem<StrandTokenItem> STRAND_TOKEN_CLOCK = ITEMS.register(
            "strand_token_clock",
            () -> new StrandTokenItem("clock", tokenProps())
    );

    public static final DeferredItem<StrandTokenItem> STRAND_TOKEN_SWARM = ITEMS.register(
            "strand_token_swarm",
            () -> new StrandTokenItem("swarm", tokenProps())
    );

    public static final DeferredItem<StrandTokenItem> STRAND_TOKEN_SIGIL = ITEMS.register(
            "strand_token_sigil",
            () -> new StrandTokenItem("sigil", tokenProps())
    );

    public static final DeferredItem<StrandTokenItem> STRAND_TOKEN_SPINDLE = ITEMS.register(
            "strand_token_spindle",
            () -> new StrandTokenItem("spindle", tokenProps())
    );

    /** End trophy, spun at a Tension Post from nine seated Strands and a March stone; seat it to Reweave. */
    public static final DeferredItem<Item> SPINDLE_LOOM_FRAGMENT = ITEMS.registerSimpleItem(
            "spindle_loom_fragment",
            new Item.Properties().stacksTo(1).fireResistant()
    );

    /**
     * The lives piece. Four stitch into a Thread of Return: the pack's repeatable answer to a spent pool,
     * bought from the Spark stall or cut from a Rift Shard. Rare on purpose, never a drop.
     */
    public static final DeferredItem<Item> THREAD_SHARD = ITEMS.register(
            "thread_shard",
            () -> new Item(new Item.Properties().stacksTo(16).rarity(Rarity.RARE))
    );

    /** Spend it for one shared Clowder life. Repeatable, unlike the six quest milestones. */
    public static final DeferredItem<ThreadOfReturnItem> THREAD_OF_RETURN = ITEMS.register(
            "thread_of_return",
            () -> new ThreadOfReturnItem(new Item.Properties().stacksTo(4).rarity(Rarity.EPIC).fireResistant())
    );

    /** The Clowder's monument. */
    public static final DeferredItem<BlockItem> TENSION_POST = ITEMS.registerSimpleBlockItem("tension_post", ModBlocks.TENSION_POST);

    /** Loom Braid glue — 16 Strand Filaments spun at a Tension Post. */
    public static final DeferredItem<Item> BRAID_CORD = ITEMS.registerSimpleItem(
            "braid_cord",
            new Item.Properties().stacksTo(16)
    );

    /**
     * The pack's only way to the End: eat it to go, eat the half that is left to come back.
     * Expensive on purpose (five pearls, two bones, two blaze powder) and not a shortcut to anything else.
     */
    public static final DeferredItem<EndAppleItem> END_APPLE = ITEMS.register(
            "end_apple",
            () -> new EndAppleItem(false, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)
                    .food(new FoodProperties.Builder().nutrition(4).saturationModifier(0.3F).alwaysEdible().build()))
    );

    /** Bite two. Carries nothing itself: the way back is stored on the player, so dying in the End keeps it. */
    public static final DeferredItem<EndAppleItem> BITTEN_END_APPLE = ITEMS.register(
            "bitten_end_apple",
            () -> new EndAppleItem(true, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)
                    .food(new FoodProperties.Builder().nutrition(4).saturationModifier(0.3F).alwaysEdible().build()))
    );

    /** Soft check against an item that may belong to another mod. */
    public static boolean is(ItemStack stack, String id) {
        Item item = BuiltInRegistries.ITEM.getOptional(ResourceLocation.parse(id)).orElse(null);
        return item != null && stack.is(item);
    }

    private ModItems() {}
}
