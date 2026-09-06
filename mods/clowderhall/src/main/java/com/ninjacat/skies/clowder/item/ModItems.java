package com.ninjacat.skies.clowder.item;

import com.ninjacat.skies.clowder.ClowderHall;
import net.minecraft.world.item.BannerPatternItem;
import net.minecraft.world.item.Item;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(ClowderHall.MOD_ID);

    public static final DeferredItem<IslandCharterItem> ISLAND_CHARTER = ITEMS.register(
            "island_charter",
            () -> new IslandCharterItem(new Item.Properties().stacksTo(1))
    );

    public static final DeferredItem<HubKeyItem> HUB_KEY = ITEMS.register(
            "hub_key",
            () -> new HubKeyItem(new Item.Properties().stacksTo(1))
    );

    public static final DeferredItem<BannerPatternItem> STRAND_BANNER_PATTERN = ITEMS.register(
            "strand_banner_pattern",
            () -> new BannerPatternItem(
                    ModBannerPatterns.PATTERN_ITEM_STRAND,
                    new Item.Properties().stacksTo(1)
            )
    );

    private ModItems() {}
}
