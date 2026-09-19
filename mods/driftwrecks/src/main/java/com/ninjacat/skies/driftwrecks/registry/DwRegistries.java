package com.ninjacat.skies.driftwrecks.registry;

import com.ninjacat.skies.driftwrecks.Driftwrecks;
import com.ninjacat.skies.driftwrecks.block.FrayedSpawnerBlockEntity;
import com.ninjacat.skies.driftwrecks.block.SalvageCrateBlockEntity;
import com.ninjacat.skies.driftwrecks.block.TrophyPlinthBlockEntity;
import com.ninjacat.skies.driftwrecks.block.WreckChestBlockEntity;
import com.ninjacat.skies.driftwrecks.entity.RemnantEntity;
import com.ninjacat.skies.driftwrecks.entity.StewardEchoEntity;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.LinkedHashMap;
import java.util.Map;

/** Block entities, entities and sounds. */
public final class DwRegistries {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES = DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, Driftwrecks.MOD_ID);
    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(Registries.ENTITY_TYPE, Driftwrecks.MOD_ID);
    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(Registries.SOUND_EVENT, Driftwrecks.MOD_ID);

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<WreckChestBlockEntity>> WRECK_CHEST = BLOCK_ENTITIES.register("wreck_chest",
            () -> BlockEntityType.Builder.of(WreckChestBlockEntity::new, DwBlocks.WRECK_CHEST.get()).build(null));
    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<FrayedSpawnerBlockEntity>> FRAYED_SPAWNER = BLOCK_ENTITIES.register("frayed_spawner",
            () -> BlockEntityType.Builder.of(FrayedSpawnerBlockEntity::new, DwBlocks.FRAYED_SPAWNER.get()).build(null));
    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<SalvageCrateBlockEntity>> SALVAGE_CRATE = BLOCK_ENTITIES.register("salvage_crate",
            () -> BlockEntityType.Builder.of(SalvageCrateBlockEntity::new, DwBlocks.SALVAGE_CRATE.get()).build(null));
    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<TrophyPlinthBlockEntity>> TROPHY_PLINTH = BLOCK_ENTITIES.register("trophy_plinth",
            () -> BlockEntityType.Builder.of(TrophyPlinthBlockEntity::new, DwBlocks.TROPHY_PLINTH.get()).build(null));

    public static final DeferredHolder<EntityType<?>, EntityType<StewardEchoEntity>> STEWARD_ECHO = ENTITIES.register("steward_echo",
            () -> EntityType.Builder.of(StewardEchoEntity::new, MobCategory.MISC).sized(0.6F, 0.7F).clientTrackingRange(10).build("steward_echo"));
    public static final DeferredHolder<EntityType<?>, EntityType<RemnantEntity>> REMNANT = ENTITIES.register("remnant",
            () -> EntityType.Builder.of(RemnantEntity::new, MobCategory.MONSTER).sized(2.2F, 4.5F).clientTrackingRange(12).fireImmune().build("remnant"));

    public static final Map<String, DeferredHolder<SoundEvent, SoundEvent>> SOUND = new LinkedHashMap<>();
    static {
        for (String s : new String[]{"driftwreck.arrive", "driftwreck.creak", "driftwreck.crumble", "driftwreck.warn_final", "driftwreck.unravel",
                "tether.lay", "tether.catch", "rift.open", "keepsake.found", "atlas.page", "driftwreck.whisper"}) {
            SOUND.put(s, SOUNDS.register(s, () -> SoundEvent.createVariableRangeEvent(ResourceLocation.fromNamespaceAndPath(Driftwrecks.MOD_ID, s))));
        }
    }

    public static SoundEvent sound(String id) { return SOUND.get(id).get(); }

    public static void attributes(EntityAttributeCreationEvent e) {
        e.put(STEWARD_ECHO.get(), StewardEchoEntity.createAttributes().build());
        e.put(REMNANT.get(), RemnantEntity.createAttributes().build());
    }

    private DwRegistries() {}
}
