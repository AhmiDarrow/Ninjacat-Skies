package com.ninjacat.skies.core.block;

import com.ninjacat.skies.core.NinjacatSkies;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITY_TYPES =
            DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, NinjacatSkies.MOD_ID);

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<TensionPostBlockEntity>> TENSION_POST =
            BLOCK_ENTITY_TYPES.register(
                    "tension_post",
                    () -> BlockEntityType.Builder.of(TensionPostBlockEntity::new, ModBlocks.TENSION_POST.get()).build(null)
            );

    private ModBlockEntities() {}
}
