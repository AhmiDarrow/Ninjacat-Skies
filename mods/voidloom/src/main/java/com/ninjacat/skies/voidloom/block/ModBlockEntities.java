package com.ninjacat.skies.voidloom.block;

import com.ninjacat.skies.voidloom.Voidloom;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITY_TYPES =
            DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, Voidloom.MOD_ID);

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<LoomframeBlockEntity>> LOOMFRAME =
            BLOCK_ENTITY_TYPES.register(
                    "loomframe",
                    () -> BlockEntityType.Builder.of(LoomframeBlockEntity::new, ModBlocks.LOOMFRAME.get()).build(null)
            );

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<TensionBarrelBlockEntity>> TENSION_BARREL =
            BLOCK_ENTITY_TYPES.register(
                    "tension_barrel",
                    () -> BlockEntityType.Builder.of(TensionBarrelBlockEntity::new, ModBlocks.TENSION_BARREL.get()).build(null)
            );

    private ModBlockEntities() {}
}
