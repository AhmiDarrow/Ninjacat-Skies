package com.ninjacat.skies.driftwrecks.registry;

import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.Driftwrecks;
import com.ninjacat.skies.driftwrecks.block.*;
import com.ninjacat.skies.driftwrecks.wreck.WreckCore;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.Map;

public final class DwBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(Driftwrecks.MOD_ID);

    private static BlockBehaviour.Properties wreck() {
        // wreck furniture: sturdy, not movable by pistons, so an unravel always finds it where it was placed
        return BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_CYAN).strength(2.5F, 6.0F).pushReaction(PushReaction.BLOCK);
    }

    public static final DeferredBlock<TetherThreadBlock> TETHER_THREAD = BLOCKS.register("tether_thread",
            () -> new TetherThreadBlock(BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_CYAN).strength(0.6F).sound(SoundType.WOOL)
                    .lightLevel(s -> 4).noOcclusion().isValidSpawn((s, l, p, e) -> false).pushReaction(PushReaction.DESTROY)));
    public static final DeferredBlock<WreckChestBlock> WRECK_CHEST = BLOCKS.register("wreck_chest",
            () -> new WreckChestBlock(wreck().strength(-1.0F, 3600000.0F).sound(SoundType.WOOD).noLootTable()));
    public static final DeferredBlock<FrayedSpawnerBlock> FRAYED_SPAWNER = BLOCKS.register("frayed_spawner",
            () -> new FrayedSpawnerBlock(wreck().strength(5.0F, 6.0F).requiresCorrectToolForDrops().sound(SoundType.METAL)
                    .lightLevel(s -> 7).noOcclusion()));
    public static final DeferredBlock<ThreadPillarBlock> THREAD_PILLAR = BLOCKS.register("thread_pillar",
            () -> new ThreadPillarBlock(wreck().strength(-1.0F, 3600000.0F).sound(SoundType.STONE).noLootTable()
                    .lightLevel(s -> s.getValue(ThreadPillarBlock.LIT) ? 12 : 3)));
    public static final DeferredBlock<ThreadIdolBlock> THREAD_IDOL = BLOCKS.register("thread_idol",
            () -> new ThreadIdolBlock(wreck().strength(-1.0F, 3600000.0F).sound(SoundType.WOOD).noLootTable().noOcclusion().lightLevel(s -> 6)));
    public static final DeferredBlock<ThreadLockBlock> THREAD_LOCK = BLOCKS.register("thread_lock",
            () -> new ThreadLockBlock(wreck().strength(-1.0F, 3600000.0F).sound(SoundType.WOOL).noLootTable().lightLevel(s -> 5)));
    public static final DeferredBlock<RiftTearBlock> RIFT_TEAR = BLOCKS.register("rift_tear",
            () -> new RiftTearBlock(wreck().strength(-1.0F, 3600000.0F).noCollission().noLootTable().lightLevel(s -> 13).sound(SoundType.AMETHYST)));
    public static final DeferredBlock<SalvageCrateBlock> SALVAGE_CRATE = BLOCKS.register("salvage_crate",
            () -> new SalvageCrateBlock(BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2.0F).sound(SoundType.WOOD)));
    public static final DeferredBlock<SalvagersFrameBlock> SALVAGERS_FRAME = BLOCKS.register("salvagers_frame",
            () -> new SalvagersFrameBlock(BlockBehaviour.Properties.of().mapColor(MapColor.WOOD).strength(2.0F).sound(SoundType.WOOD).noOcclusion()));
    public static final DeferredBlock<TrophyPlinthBlock> TROPHY_PLINTH = BLOCKS.register("trophy_plinth",
            () -> new TrophyPlinthBlock(BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(2.0F, 6.0F).sound(SoundType.STONE).noOcclusion()));
    public static final DeferredBlock<KeepsakeBlock> HEART_KEEPSAKE = BLOCKS.register("keepsake_heartwreck",
            () -> new KeepsakeBlock(null, null, keepsakeProps()));

    public static final Map<Strand, Map<WreckCore, DeferredBlock<KeepsakeBlock>>> KEEPSAKES = new EnumMap<>(Strand.class);
    public static final Map<Strand, DeferredBlock<TribeBannerBlock>> BANNERS = new EnumMap<>(Strand.class);

    static {
        for (Strand s : Strand.ALL) {
            Map<WreckCore, DeferredBlock<KeepsakeBlock>> row = new LinkedHashMap<>();
            for (WreckCore c : WreckCore.ALL) {
                row.put(c, BLOCKS.register("keepsake_" + s.id() + "_" + c.id, () -> new KeepsakeBlock(s, c, keepsakeProps())));
            }
            KEEPSAKES.put(s, row);
            BANNERS.put(s, BLOCKS.register("tribe_banner_" + s.id(),
                    () -> new TribeBannerBlock(s, BlockBehaviour.Properties.of().mapColor(MapColor.WOOL).strength(1.0F).sound(SoundType.WOOL).noOcclusion())));
        }
    }

    private static BlockBehaviour.Properties keepsakeProps() {
        return BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BROWN).strength(0.4F).sound(SoundType.DECORATED_POT).noOcclusion()
                .pushReaction(PushReaction.DESTROY).lightLevel(s -> 2);
    }

    public static KeepsakeBlock keepsake(Strand s, WreckCore c) { return KEEPSAKES.get(s).get(c).get(); }

    private DwBlocks() {}
}
