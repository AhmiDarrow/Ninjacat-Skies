package com.ninjacat.skies.lib.plan;

import net.minecraft.core.BlockPos;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;

/**
 * A voxel block plan in the NCGA format written by the art pipeline (arena_factory.py, wreck_factory.py):
 * magic 'NCGA', version, a palette of string keys, then (x, y, z, key index) per block. Whatever follows the
 * blocks is format-specific (arena pads and gate, wreck markers) and is left in {@link #trailer} for the caller.
 * Keys are palette names, not block ids: each consumer maps them to BlockStates its own way.
 */
public final class BlockPlan {
    public static final int MAGIC = 0x4147434E;   // 'NCGA' little-endian

    public final int version;
    public final String[] keys;
    public final short[] xyz;       // packed triples
    public final byte[] key;
    /** Positioned just past the block list; little-endian. */
    public final ByteBuffer trailer;

    private BlockPlan(int version, String[] keys, short[] xyz, byte[] key, ByteBuffer trailer) {
        this.version = version; this.keys = keys; this.xyz = xyz; this.key = key; this.trailer = trailer;
    }

    public int size() { return key.length; }
    public int x(int i) { return xyz[i * 3]; }
    public int y(int i) { return xyz[i * 3 + 1]; }
    public int z(int i) { return xyz[i * 3 + 2]; }
    public BlockPos pos(int i) { return new BlockPos(xyz[i * 3], xyz[i * 3 + 1], xyz[i * 3 + 2]); }
    public String keyOf(int i) { return keys[key[i] & 0xFF]; }

    public static BlockPlan read(byte[] bytes) throws IOException {
        try {
            return parse(bytes);
        } catch (java.nio.BufferUnderflowException e) {
            throw new IOException("truncated plan", e);
        }
    }

    private static BlockPlan parse(byte[] bytes) throws IOException {
        ByteBuffer b = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);
        if (b.remaining() < 10 || b.getInt() != MAGIC) throw new IOException("bad magic");
        int version = b.getInt();
        int nk = b.getShort() & 0xFFFF;
        if (nk > 256) throw new IOException("palette too large: " + nk);
        String[] keys = new String[nk];
        for (int i = 0; i < nk; i++) keys[i] = readString(b);
        int n = b.getInt();
        if (n < 0 || (long) n * 7 > b.remaining()) throw new IOException("bad block count: " + n);
        short[] xyz = new short[n * 3];
        byte[] key = new byte[n];
        for (int i = 0; i < n; i++) {
            xyz[i * 3] = b.getShort(); xyz[i * 3 + 1] = b.getShort(); xyz[i * 3 + 2] = b.getShort();
            key[i] = b.get();
            if ((key[i] & 0xFF) >= nk) throw new IOException("bad palette index " + (key[i] & 0xFF) + " of " + nk);
        }
        return new BlockPlan(version, keys, xyz, key, b.slice().order(ByteOrder.LITTLE_ENDIAN));
    }

    /** A u16-length-prefixed UTF-8 string, the palette encoding; trailers may reuse it. */
    public static String readString(ByteBuffer b) {
        int n = b.getShort() & 0xFFFF;
        byte[] s = new byte[n];
        b.get(s);
        return new String(s, StandardCharsets.UTF_8);
    }
}
