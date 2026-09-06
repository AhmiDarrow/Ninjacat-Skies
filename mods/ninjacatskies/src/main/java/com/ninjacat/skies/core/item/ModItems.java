package com.ninjacat.skies.core.item;

import com.ninjacat.skies.core.NinjacatSkies;
import net.minecraft.world.item.Item;
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

    public static final DeferredItem<Item> CODEX_PAGE = ITEMS.registerSimpleItem(
            "codex_page",
            new Item.Properties().stacksTo(16)
    );

    // Stack >1 so braid crafts do not soft-brick the Spindle trophy (needs all nine).
    private static Item.Properties tokenProps() {
        return new Item.Properties().stacksTo(16);
    }

    public static final DeferredItem<Item> STRAND_TOKEN_SOIL = ITEMS.registerSimpleItem(
            "strand_token_soil",
            tokenProps()
    );

    public static final DeferredItem<Item> STRAND_TOKEN_STONE = ITEMS.registerSimpleItem(
            "strand_token_stone",
            tokenProps()
    );

    public static final DeferredItem<Item> STRAND_TOKEN_SPROUT = ITEMS.registerSimpleItem(
            "strand_token_sprout",
            tokenProps()
    );

    public static final DeferredItem<Item> STRAND_TOKEN_CLAW = ITEMS.registerSimpleItem(
            "strand_token_claw",
            tokenProps()
    );

    public static final DeferredItem<Item> STRAND_TOKEN_SPARK = ITEMS.registerSimpleItem(
            "strand_token_spark",
            tokenProps()
    );

    public static final DeferredItem<Item> STRAND_TOKEN_CLOCK = ITEMS.registerSimpleItem(
            "strand_token_clock",
            tokenProps()
    );

    public static final DeferredItem<Item> STRAND_TOKEN_SWARM = ITEMS.registerSimpleItem(
            "strand_token_swarm",
            tokenProps()
    );

    public static final DeferredItem<Item> STRAND_TOKEN_SIGIL = ITEMS.registerSimpleItem(
            "strand_token_sigil",
            tokenProps()
    );

    public static final DeferredItem<Item> STRAND_TOKEN_SPINDLE = ITEMS.registerSimpleItem(
            "strand_token_spindle",
            tokenProps()
    );

    /** End-game trophy; craft gated by all nine Strand tokens. */
    public static final DeferredItem<Item> SPINDLE_LOOM_FRAGMENT = ITEMS.registerSimpleItem(
            "spindle_loom_fragment",
            new Item.Properties().stacksTo(1).fireResistant()
    );

    /** Mid/late Loom Braid glue — any two of Clock/Swarm/Spark strand tokens. */
    public static final DeferredItem<Item> BRAID_CORD = ITEMS.registerSimpleItem(
            "braid_cord",
            new Item.Properties().stacksTo(16)
    );

    private ModItems() {}
}
