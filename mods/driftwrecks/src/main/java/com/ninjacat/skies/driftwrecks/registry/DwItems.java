package com.ninjacat.skies.driftwrecks.registry;

import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.Driftwrecks;
import com.ninjacat.skies.driftwrecks.item.*;
import com.ninjacat.skies.driftwrecks.wreck.WreckCore;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class DwItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(Driftwrecks.MOD_ID);
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Driftwrecks.MOD_ID);

    public static final DeferredItem<Item> SALVAGED_WEFT = ITEMS.registerSimpleItem("salvaged_weft", new Item.Properties());
    public static final DeferredItem<Item> FRAYED_CORE = ITEMS.registerSimpleItem("frayed_core", new Item.Properties());
    public static final DeferredItem<Item> DRIFTWRECK_SEAL = ITEMS.register("driftwreck_seal", () -> new Item(new Item.Properties().rarity(Rarity.UNCOMMON)));
    public static final DeferredItem<Item> RIFT_SHARD = ITEMS.register("rift_shard", () -> new Item(new Item.Properties().rarity(Rarity.RARE)));
    public static final DeferredItem<DriftNeedleItem> DRIFT_NEEDLE = ITEMS.register("drift_needle", () -> new DriftNeedleItem(new Item.Properties().stacksTo(1)));
    public static final DeferredItem<TetherSpoolItem> TETHER_SPOOL = ITEMS.register("tether_spool", () -> new TetherSpoolItem(new Item.Properties().stacksTo(16)));
    public static final DeferredItem<DriftlureItem> DRIFTLURE = ITEMS.register("driftlure", () -> new DriftlureItem(false, new Item.Properties().stacksTo(16)));
    public static final DeferredItem<DriftlureItem> STRAND_LURE = ITEMS.register("strand_lure", () -> new DriftlureItem(true, new Item.Properties().stacksTo(16)));
    public static final DeferredItem<WeftKeyItem> WEFT_KEY = ITEMS.register("weft_key", () -> new WeftKeyItem(new Item.Properties().stacksTo(8).rarity(Rarity.RARE)));
    public static final DeferredItem<SalvageBundleItem> SALVAGE_BUNDLE = ITEMS.register("salvage_bundle", () -> new SalvageBundleItem(new Item.Properties().stacksTo(1)));
    public static final DeferredItem<WreckAtlasItem> WRECK_ATLAS = ITEMS.register("wreck_atlas", () -> new WreckAtlasItem(new Item.Properties().stacksTo(1)));
    public static final DeferredItem<WreckMapScrollItem> WRECK_MAP_SCROLL = ITEMS.register("wreck_map_scroll", () -> new WreckMapScrollItem(new Item.Properties().stacksTo(16)));
    public static final DeferredItem<HintPageItem> HINT_PAGE = ITEMS.register("hint_page", () -> new HintPageItem(new Item.Properties().stacksTo(16)));

    public static final DeferredItem<BlockItem> SALVAGE_CRATE = ITEMS.registerSimpleBlockItem(DwBlocks.SALVAGE_CRATE);
    public static final DeferredItem<BlockItem> SALVAGERS_FRAME = ITEMS.registerSimpleBlockItem(DwBlocks.SALVAGERS_FRAME);
    public static final DeferredItem<BlockItem> TROPHY_PLINTH = ITEMS.registerSimpleBlockItem(DwBlocks.TROPHY_PLINTH);
    public static final DeferredItem<BlockItem> TETHER_THREAD = ITEMS.registerSimpleBlockItem(DwBlocks.TETHER_THREAD);
    public static final DeferredItem<BlockItem> FRAYED_SPAWNER = ITEMS.registerSimpleBlockItem(DwBlocks.FRAYED_SPAWNER);
    public static final DeferredItem<BlockItem> HEART_KEEPSAKE = ITEMS.register("keepsake_heartwreck",
            () -> new KeepsakeItem(DwBlocks.HEART_KEEPSAKE.get(), new Item.Properties().rarity(Rarity.EPIC)));

    static {
        for (Strand s : Strand.ALL) {
            for (WreckCore c : WreckCore.ALL) {
                var block = DwBlocks.KEEPSAKES.get(s).get(c);
                ITEMS.register(block.getId().getPath(), () -> new KeepsakeItem(block.get(), new Item.Properties().rarity(Rarity.UNCOMMON)));
            }
            var banner = DwBlocks.BANNERS.get(s);
            ITEMS.register(banner.getId().getPath(), () -> new BlockItem(banner.get(), new Item.Properties().rarity(Rarity.RARE)));
        }
    }

    public static ItemStack strandStack(Item item, Strand s) {
        ItemStack st = new ItemStack(item);
        st.set(DwComponents.STRAND.get(), s.id());
        return st;
    }

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> TAB = TABS.register("driftwrecks", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.driftwrecks"))
            .icon(() -> new ItemStack(TETHER_SPOOL.get()))
            .displayItems((params, out) -> {
                for (var e : ITEMS.getEntries()) {
                    Item item = e.get();
                    if (item == STRAND_LURE.get() || item == WEFT_KEY.get()) {
                        for (Strand s : Strand.ALL) out.accept(strandStack(item, s));
                    } else if (item == HINT_PAGE.get()) {
                        for (WreckCore c : WreckCore.ALL) out.accept(HintPageItem.of(c));
                    } else {
                        out.accept(item);
                    }
                }
            }).build());

    private DwItems() {}
}
