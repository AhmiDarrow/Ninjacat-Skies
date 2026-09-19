package com.ninjacat.skies.driftwrecks.wreck;

import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.Driftwrecks;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.Half;
import net.minecraft.world.level.block.state.properties.SlabType;

import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;

/**
 * A Strand's block palette. Wreck plans name <b>roles</b> (wall, floor, trim, seam...), and the rolled skin turns each
 * role into a block, so one layout reads as nine different cultures. Every skin shares the teal/gold frayed seam.
 *
 * <p>Plan keys:
 * <ul>
 *   <li>a role name: {@code keel keel2 floor wall wall2 trim beam roof accent light glass growth soil metal fence}</li>
 *   <li>{@code stair_<n|e|s|w>} and {@code stair_<n|e|s|w>_top}, {@code slab}, {@code slab_top}: the skin's stair/slab</li>
 *   <li>{@code seam}, {@code seam2}: the shared teal and gold glow of the cut</li>
 *   <li>{@code mc:<block state>}: a literal block, same in every skin (anvils, lecterns, water)</li>
 *   <li>{@code h_<key>}: hidden-room block; when the room is closed it becomes the plan's fill role instead</li>
 * </ul>
 */
public final class StrandSkin {
    private static final Map<Strand, Map<String, BlockState>> SKINS = new EnumMap<>(Strand.class);
    private static final Map<String, BlockState> LITERALS = new HashMap<>();

    private StrandSkin() {}

    public static BlockState seam() { return Blocks.VERDANT_FROGLIGHT.defaultBlockState(); }
    public static BlockState seam2() { return Blocks.OCHRE_FROGLIGHT.defaultBlockState(); }

    /** The block for a plan key under this skin. Unknown roles fall back to the skin's wall. */
    public static BlockState resolve(Strand skin, String key) {
        if (key.startsWith("mc:")) return literal(key.substring(3));
        if (key.equals("seam")) return seam();
        if (key.equals("seam2")) return seam2();
        Map<String, BlockState> s = skin(skin);
        if (key.startsWith("stair_")) return stair(s.get("stair"), key.substring(6));
        if (key.equals("slab")) return slab(s.get("slab"), SlabType.BOTTOM);
        if (key.equals("slab_top")) return slab(s.get("slab"), SlabType.TOP);
        BlockState st = s.get(key);
        return st != null ? st : s.get("wall");
    }

    private static BlockState stair(BlockState base, String dir) {
        if (base == null || !base.hasProperty(StairBlock.FACING)) return base == null ? Blocks.STONE_BRICK_STAIRS.defaultBlockState() : base;
        boolean top = dir.endsWith("_top");
        Direction face = switch (dir.charAt(0)) { case 'n' -> Direction.NORTH; case 'e' -> Direction.EAST; case 'w' -> Direction.WEST; default -> Direction.SOUTH; };
        return base.setValue(StairBlock.FACING, face).setValue(StairBlock.HALF, top ? Half.TOP : Half.BOTTOM);
    }

    private static BlockState slab(BlockState base, SlabType type) {
        if (base == null || !base.hasProperty(SlabBlock.TYPE)) return base == null ? Blocks.STONE_BRICK_SLAB.defaultBlockState() : base;
        return base.setValue(SlabBlock.TYPE, type);
    }

    private static BlockState literal(String spec) {
        return LITERALS.computeIfAbsent(spec, k -> {
            try {
                return BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK.asLookup(), k, false).blockState();
            } catch (Exception e) {
                Driftwrecks.LOGGER.warn("Wreck plan names an unknown block '{}'", k);
                return Blocks.STONE.defaultBlockState();
            }
        });
    }

    private static Map<String, BlockState> skin(Strand s) {
        return SKINS.computeIfAbsent(s, StrandSkin::build);
    }

    private static Map<String, BlockState> build(Strand s) {
        Map<String, BlockState> m = new HashMap<>();
        switch (s) {
            case SOIL -> put(m, Blocks.ROOTED_DIRT, Blocks.COARSE_DIRT, Blocks.PACKED_MUD, Blocks.MUD_BRICKS, Blocks.DARK_OAK_PLANKS,
                    Blocks.STRIPPED_DARK_OAK_LOG, Blocks.DARK_OAK_LOG, Blocks.DARK_OAK_PLANKS, Blocks.MOSS_BLOCK, Blocks.LANTERN,
                    Blocks.MOSS_CARPET, Blocks.ROOTED_DIRT, Blocks.COPPER_BLOCK, Blocks.DARK_OAK_FENCE, Blocks.MUD_BRICK_STAIRS, Blocks.MUD_BRICK_SLAB);
            case STONE -> put(m, Blocks.TUFF, Blocks.COBBLED_DEEPSLATE, Blocks.POLISHED_DEEPSLATE, Blocks.DEEPSLATE_BRICKS, Blocks.COBBLESTONE,
                    Blocks.CHISELED_DEEPSLATE, modded("create:brass_casing", Blocks.CUT_COPPER), Blocks.DEEPSLATE_TILES, modded("create:brass_block", Blocks.RAW_GOLD_BLOCK), Blocks.LANTERN,
                    Blocks.GRAVEL, Blocks.GRAVEL, modded("create:brass_block", Blocks.RAW_GOLD_BLOCK), Blocks.COBBLESTONE_WALL, Blocks.DEEPSLATE_BRICK_STAIRS, Blocks.DEEPSLATE_BRICK_SLAB);
            case SPROUT -> put(m, Blocks.DIRT, Blocks.ROOTED_DIRT, Blocks.MOSS_BLOCK, Blocks.MOSSY_STONE_BRICKS, Blocks.DARK_OAK_PLANKS,
                    Blocks.DARK_OAK_LOG, Blocks.DARK_OAK_LOG, Blocks.MOSSY_COBBLESTONE, Blocks.FLOWERING_AZALEA_LEAVES, Blocks.LANTERN,
                    Blocks.MOSS_CARPET, Blocks.GRASS_BLOCK, Blocks.OXIDIZED_COPPER, Blocks.DARK_OAK_FENCE, Blocks.MOSSY_STONE_BRICK_STAIRS, Blocks.MOSSY_STONE_BRICK_SLAB);
            case CLAW -> put(m, Blocks.BLACKSTONE, Blocks.BASALT, Blocks.POLISHED_BLACKSTONE, Blocks.DEEPSLATE_TILES, Blocks.POLISHED_BLACKSTONE_BRICKS,
                    Blocks.GILDED_BLACKSTONE, Blocks.POLISHED_BASALT, Blocks.DEEPSLATE_TILES, Blocks.GOLD_BLOCK, Blocks.LANTERN,
                    Blocks.GRAVEL, Blocks.BLACKSTONE, Blocks.GOLD_BLOCK, Blocks.POLISHED_BLACKSTONE_WALL, Blocks.POLISHED_BLACKSTONE_BRICK_STAIRS, Blocks.POLISHED_BLACKSTONE_BRICK_SLAB);
            case SPARK -> put(m, Blocks.BASALT, Blocks.SMOOTH_BASALT, Blocks.CUT_COPPER, Blocks.POLISHED_BASALT, Blocks.COPPER_BLOCK,
                    Blocks.CHISELED_COPPER, Blocks.IRON_BLOCK, Blocks.WEATHERED_CUT_COPPER, Blocks.IRON_BLOCK, Blocks.LANTERN,
                    Blocks.GRAVEL, Blocks.SMOOTH_BASALT, Blocks.IRON_BLOCK, Blocks.IRON_BARS, Blocks.CUT_COPPER_STAIRS, Blocks.CUT_COPPER_SLAB);
            case CLOCK -> put(m, Blocks.BLACKSTONE, Blocks.COBBLED_DEEPSLATE, Blocks.DARK_OAK_PLANKS, Blocks.POLISHED_BLACKSTONE_BRICKS, Blocks.DARK_OAK_PLANKS,
                    modded("create:brass_casing", Blocks.CUT_COPPER), Blocks.DARK_OAK_LOG, Blocks.OXIDIZED_CUT_COPPER, modded("create:brass_block", Blocks.RAW_GOLD_BLOCK), Blocks.LANTERN,
                    Blocks.GRAVEL, Blocks.COBBLED_DEEPSLATE, Blocks.COPPER_BLOCK, Blocks.DARK_OAK_FENCE, Blocks.DARK_OAK_STAIRS, Blocks.DARK_OAK_SLAB);
            case SWARM -> put(m, Blocks.PACKED_MUD, Blocks.DIRT, Blocks.OAK_PLANKS, Blocks.HONEYCOMB_BLOCK, Blocks.ORANGE_TERRACOTTA,
                    Blocks.BROWN_TERRACOTTA, Blocks.OAK_LOG, Blocks.OAK_PLANKS, Blocks.YELLOW_TERRACOTTA, Blocks.LANTERN,
                    Blocks.MOSS_CARPET, Blocks.DIRT, Blocks.HONEYCOMB_BLOCK, Blocks.OAK_FENCE, Blocks.OAK_STAIRS, Blocks.OAK_SLAB);
            case SIGIL -> put(m, Blocks.DEEPSLATE, Blocks.COBBLED_DEEPSLATE, Blocks.POLISHED_DEEPSLATE, Blocks.DEEPSLATE_BRICKS, Blocks.PURPUR_BLOCK,
                    Blocks.PURPUR_PILLAR, Blocks.PURPUR_PILLAR, Blocks.DEEPSLATE_TILES, Blocks.AMETHYST_BLOCK, Blocks.LANTERN,
                    Blocks.AMETHYST_CLUSTER, Blocks.CALCITE, Blocks.GOLD_BLOCK, Blocks.DEEPSLATE_BRICK_WALL, Blocks.PURPUR_STAIRS, Blocks.PURPUR_SLAB);
            case SPINDLE -> put(m, Blocks.DEEPSLATE, Blocks.TUFF, Blocks.SPRUCE_PLANKS, Blocks.STRIPPED_SPRUCE_LOG, Blocks.DARK_OAK_PLANKS,
                    Blocks.PURPUR_PILLAR, Blocks.SPRUCE_LOG, Blocks.WARPED_PLANKS, Blocks.CYAN_TERRACOTTA, Blocks.LANTERN,
                    Blocks.MOSS_CARPET, Blocks.TUFF, Blocks.GOLD_BLOCK, Blocks.SPRUCE_FENCE, Blocks.SPRUCE_STAIRS, Blocks.SPRUCE_SLAB);
        }
        m.put("glass", Blocks.TINTED_GLASS.defaultBlockState());
        m.computeIfPresent("accent", (k, v) -> v.hasProperty(LeavesBlock.PERSISTENT) ? v.setValue(LeavesBlock.PERSISTENT, true) : v);
        m.computeIfPresent("growth", (k, v) -> v.hasProperty(BlockStateProperties.WATERLOGGED) ? v.setValue(BlockStateProperties.WATERLOGGED, false) : v);
        return m;
    }

    private static void put(Map<String, BlockState> m, Object keel, Object keel2, Object floor, Object wall, Object wall2, Object trim, Object beam,
                            Object roof, Object accent, Object light, Object growth, Object soil, Object metal, Object fence, Object stair, Object slab) {
        m.put("keel", st(keel)); m.put("keel2", st(keel2)); m.put("floor", st(floor)); m.put("wall", st(wall)); m.put("wall2", st(wall2));
        m.put("trim", st(trim)); m.put("beam", st(beam)); m.put("roof", st(roof)); m.put("accent", st(accent)); m.put("light", st(light));
        m.put("growth", st(growth)); m.put("soil", st(soil)); m.put("metal", st(metal)); m.put("fence", st(fence));
        m.put("stair", st(stair)); m.put("slab", st(slab));
    }

    private static BlockState st(Object o) { return o instanceof BlockState b ? b : ((Block) o).defaultBlockState(); }

    private static BlockState modded(String id, Block fallback) {
        ResourceLocation rl = ResourceLocation.tryParse(id);
        if (rl != null) { Block b = BuiltInRegistries.BLOCK.get(rl); if (b != Blocks.AIR) return b.defaultBlockState(); }
        return fallback.defaultBlockState();
    }
}
