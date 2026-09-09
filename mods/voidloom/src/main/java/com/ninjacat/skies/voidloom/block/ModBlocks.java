package com.ninjacat.skies.voidloom.block;

import com.ninjacat.skies.voidloom.Voidloom;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(Voidloom.MOD_ID);

    /** Mesh pedestal with a tiny sift flair; Ex Deorum sieves still do the real work. */
    public static final DeferredBlock<LoomframeBlock> LOOMFRAME = BLOCKS.registerBlock(
            "loomframe",
            LoomframeBlock::new,
            BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_BLUE)
                    .strength(2.0F, 3.0F)
                    .sound(SoundType.WOOD)
                    .noOcclusion()
    );

    /** Slow transform barrel: water+dirt→clay, string+ender→void yarn. */
    public static final DeferredBlock<TensionBarrelBlock> TENSION_BARREL = BLOCKS.registerBlock(
            "tension_barrel",
            TensionBarrelBlock::new,
            BlockBehaviour.Properties.of()
                    .mapColor(MapColor.WOOD)
                    .strength(1.5F)
                    .sound(SoundType.WOOD)
                    .noOcclusion()
    );

    private ModBlocks() {}
}
