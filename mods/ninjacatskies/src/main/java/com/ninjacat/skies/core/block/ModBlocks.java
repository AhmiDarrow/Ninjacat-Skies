package com.ninjacat.skies.core.block;

import com.ninjacat.skies.core.NinjacatSkies;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(NinjacatSkies.MOD_ID);

    /** The Clowder's monument: seat Strand tokens, spin Braid Cord and the Fragment, feel the hum. */
    public static final DeferredBlock<TensionPostBlock> TENSION_POST = BLOCKS.registerBlock(
            "tension_post",
            TensionPostBlock::new,
            BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_BLUE)
                    .strength(2.5F, 6.0F)
                    .sound(SoundType.WOOD)
                    .noOcclusion()
                    .lightLevel(TensionPostBlock::lightFor)
    );

    private ModBlocks() {}
}
