package com.ninjacat.skies.guardians.arena;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.Guardians;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.state.BlockState;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/**
 * The block plan of one arena (data/guardians/arena/<id>.ncga, written by arena_factory.py). Coordinates are
 * relative to the arena origin (boss spawn, floor top = y 0). Blocks are stored as (x, y, z, palette key).
 */
public final class ArenaData {
    public record Gate(BlockPos pos, boolean alongX, int height, int width) {}

    public final GuardianKind kind;
    public final String[] keys;
    public final BlockState[] states;
    public final short[] xyz;       // packed triples
    public final byte[] key;
    public final List<BlockPos> pads;
    public final BlockPos totem;
    public final Gate gate;
    public final int radius;

    private ArenaData(GuardianKind kind, String[] keys, short[] xyz, byte[] key, List<BlockPos> pads, BlockPos totem, Gate gate, int radius) {
        this.kind = kind; this.keys = keys; this.xyz = xyz; this.key = key; this.pads = pads; this.totem = totem; this.gate = gate; this.radius = radius;
        this.states = new BlockState[keys.length];
        for (int i = 0; i < keys.length; i++) states[i] = Palette.state(keys[i]);
    }

    public int size() { return key.length; }
    public BlockPos pos(int i) { return new BlockPos(xyz[i*3], xyz[i*3+1], xyz[i*3+2]); }
    public BlockState state(int i) { return states[key[i] & 0xFF]; }

    private static final Map<GuardianKind, ArenaData> CACHE = new EnumMap<>(GuardianKind.class);

    public static ArenaData get(MinecraftServer server, GuardianKind kind) {
        ArenaData d = CACHE.get(kind);
        if (d != null) return d;
        try (InputStream in = server.getResourceManager().getResourceOrThrow(kind.arenaFile()).open()) {
            d = read(kind, in.readAllBytes());
        } catch (IOException e) {
            throw new IllegalStateException("Missing arena plan " + kind.arenaFile(), e);
        }
        CACHE.put(kind, d);
        return d;
    }
    public static void clearCache() { CACHE.clear(); }

    static ArenaData read(GuardianKind kind, byte[] bytes) throws IOException {
        ByteBuffer b = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);
        if (b.getInt() != 0x4147434E) throw new IOException("bad magic");          // 'NCGA' little-endian
        int version = b.getInt(); int nk = b.getShort() & 0xFFFF;
        String[] keys = new String[nk];
        for (int i = 0; i < nk; i++) { int n = b.getShort() & 0xFFFF; byte[] s = new byte[n]; b.get(s); keys[i] = new String(s, java.nio.charset.StandardCharsets.UTF_8); }
        int n = b.getInt(); short[] xyz = new short[n*3]; byte[] key = new byte[n];
        for (int i = 0; i < n; i++) { xyz[i*3] = b.getShort(); xyz[i*3+1] = b.getShort(); xyz[i*3+2] = b.getShort(); key[i] = b.get(); }
        int np = b.get() & 0xFF; List<BlockPos> pads = new ArrayList<>();
        for (int i = 0; i < np; i++) pads.add(new BlockPos(b.getShort(), b.getShort(), b.getShort()));
        BlockPos totem = new BlockPos(b.getShort(), b.getShort(), b.getShort());
        Gate gate = new Gate(new BlockPos(b.getShort(), b.getShort(), b.getShort()), b.get() == 1, b.get() & 0xFF, b.get() & 0xFF);
        int radius = b.getShort();
        return new ArenaData(kind, keys, xyz, key, pads, totem, gate, radius);
    }

    /** Palette keys of the art pipeline -> real blocks. Modded blocks fall back to vanilla when absent. */
    public static final class Palette {
        private Palette() {}
        public static BlockState state(String key) {
            return switch (key) {
                case "dirt" -> Blocks.DIRT.defaultBlockState();
                case "rooted" -> Blocks.ROOTED_DIRT.defaultBlockState();
                case "mud" -> Blocks.MUD.defaultBlockState();
                case "moss" -> Blocks.MOSS_BLOCK.defaultBlockState();
                case "grass" -> Blocks.GRASS_BLOCK.defaultBlockState();
                case "stone" -> Blocks.STONE.defaultBlockState();
                case "cobble" -> Blocks.COBBLESTONE.defaultBlockState();
                case "deepslate" -> Blocks.DEEPSLATE.defaultBlockState();
                case "blackstone" -> Blocks.BLACKSTONE.defaultBlockState();
                case "tuff" -> Blocks.TUFF.defaultBlockState();
                case "gravel" -> Blocks.GRAVEL.defaultBlockState();
                case "basalt" -> Blocks.SMOOTH_BASALT.defaultBlockState();
                case "obsidian" -> Blocks.OBSIDIAN.defaultBlockState();
                case "endstone" -> Blocks.END_STONE.defaultBlockState();
                case "purpur" -> Blocks.PURPUR_BLOCK.defaultBlockState();
                case "oak" -> Blocks.OAK_LOG.defaultBlockState();
                case "darkoak" -> Blocks.DARK_OAK_LOG.defaultBlockState();
                case "spruce" -> Blocks.SPRUCE_PLANKS.defaultBlockState();
                case "planks" -> Blocks.OAK_PLANKS.defaultBlockState();
                case "log" -> Blocks.SPRUCE_LOG.defaultBlockState();
                case "copper" -> Blocks.COPPER_BLOCK.defaultBlockState();
                case "oxcopper" -> Blocks.OXIDIZED_COPPER.defaultBlockState();
                case "brass" -> modded("create:brass_block", Blocks.RAW_GOLD_BLOCK);
                case "iron" -> Blocks.IRON_BLOCK.defaultBlockState();
                case "gold" -> Blocks.OCHRE_FROGLIGHT.defaultBlockState();
                case "wax" -> Blocks.HONEYCOMB_BLOCK.defaultBlockState();
                case "comb" -> Blocks.ORANGE_TERRACOTTA.defaultBlockState();
                case "darkwax" -> Blocks.BROWN_TERRACOTTA.defaultBlockState();
                case "hedge" -> Blocks.OAK_LEAVES.defaultBlockState().setValue(LeavesBlock.PERSISTENT, true);
                case "leaves" -> Blocks.AZALEA_LEAVES.defaultBlockState().setValue(LeavesBlock.PERSISTENT, true);
                case "wool" -> Blocks.WHITE_WOOL.defaultBlockState();
                case "redwool" -> Blocks.RED_WOOL.defaultBlockState();
                case "rope" -> Blocks.OAK_FENCE.defaultBlockState();
                case "amethyst" -> Blocks.AMETHYST_BLOCK.defaultBlockState();
                case "prismarine" -> Blocks.PRISMARINE.defaultBlockState();
                case "sand" -> Blocks.SAND.defaultBlockState();
                case "glass" -> Blocks.GLASS.defaultBlockState();
                case "snow" -> Blocks.SNOW_BLOCK.defaultBlockState();
                case "lava" -> Blocks.LAVA.defaultBlockState();
                case "honey" -> Blocks.HONEY_BLOCK.defaultBlockState();
                case "teal" -> Blocks.VERDANT_FROGLIGHT.defaultBlockState();
                case "seam" -> Blocks.OCHRE_FROGLIGHT.defaultBlockState();
                case "void" -> Blocks.PEARLESCENT_FROGLIGHT.defaultBlockState();
                case "amber" -> Blocks.SHROOMLIGHT.defaultBlockState();
                case "violet" -> Blocks.CRYING_OBSIDIAN.defaultBlockState();
                case "white" -> Blocks.SEA_LANTERN.defaultBlockState();
                case "ember" -> Blocks.MAGMA_BLOCK.defaultBlockState();
                case "soul" -> Blocks.SOUL_LANTERN.defaultBlockState();
                default -> Blocks.STONE.defaultBlockState();
            };
        }
        private static BlockState modded(String id, Block fallback) {
            ResourceLocation rl = ResourceLocation.tryParse(id);
            if (rl != null) { Block b = BuiltInRegistries.BLOCK.get(rl); if (b != Blocks.AIR) return b.defaultBlockState(); }
            return fallback.defaultBlockState();
        }
    }
}
