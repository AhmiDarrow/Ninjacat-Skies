package com.ninjacat.skies.clowder.item;

import com.ninjacat.skies.clowder.ClowderHall;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.block.entity.BannerPattern;

/** Banner pattern tag wired to {@code BannerPatternItem} + datapack pattern. */
public final class ModBannerPatterns {
    public static final TagKey<BannerPattern> PATTERN_ITEM_STRAND = TagKey.create(
            Registries.BANNER_PATTERN,
            ResourceLocation.fromNamespaceAndPath(ClowderHall.MOD_ID, "pattern_item/strand")
    );

    private ModBannerPatterns() {}
}
