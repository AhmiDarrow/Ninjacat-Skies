package com.ninjacat.skies.core.item;

import com.ninjacat.skies.core.NinjacatSkies;
import com.ninjacat.skies.core.block.ModBlocks;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
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

    /** The Clowder's monument. */
    public static final DeferredItem<BlockItem> TENSION_POST = ITEMS.registerSimpleBlockItem("tension_post", ModBlocks.TENSION_POST);

    /** Mid/late Loom Braid glue — any two of Clock/Swarm/Spark strand tokens. */
    public static final DeferredItem<Item> BRAID_CORD = ITEMS.registerSimpleItem(
            "braid_cord",
            new Item.Properties().stacksTo(16)
    );

    /** Soft check against an item that may belong to another mod. */
    public static boolean is(ItemStack stack, String id) {
        Item item = BuiltInRegistries.ITEM.getOptional(ResourceLocation.parse(id)).orElse(null);
        return item != null && stack.is(item);
    }

    private ModItems() {}
}
