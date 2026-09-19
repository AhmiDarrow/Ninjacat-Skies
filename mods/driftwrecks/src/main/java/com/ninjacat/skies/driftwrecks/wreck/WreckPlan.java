package com.ninjacat.skies.driftwrecks.wreck;

import com.ninjacat.skies.driftwrecks.Driftwrecks;
import com.ninjacat.skies.lib.plan.BlockPlan;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;

import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * One wreck layout: a role-keyed {@link BlockPlan} from tools/wreck_factory.py plus its markers. Coordinates are
 * relative to the origin: x/z centred on the wreck, y 0 = the main deck.
 *
 * <p>Trailer (after the blocks): fill role (string), u16 marker count, then per marker: kind (string), x y z
 * (shorts), data (u8). Marker kinds are listed in {@link Marker}.
 */
public final class WreckPlan {
    /**
     * chest (data 0 plain, 1 heart chest, 2 hidden room), spawner, pillar (data = index), idol (shows the pillar
     * order), echo (Steward echo start), center (Hold objective), dock (tether landing), rift (Tier 3 tear),
     * mob (ambient mob spot), district (Heartwreck pillar, data = Strand ordinal)
     */
    public record Marker(String kind, BlockPos pos, int data) {}

    public final String id;
    public final BlockPlan plan;
    public final String fill;
    public final List<Marker> markers;
    public final int minX, minY, minZ, maxX, maxY, maxZ;

    private WreckPlan(String id, BlockPlan plan, String fill, List<Marker> markers) {
        this.id = id; this.plan = plan; this.fill = fill; this.markers = markers;
        int x0 = 0, y0 = 0, z0 = 0, x1 = 0, y1 = 0, z1 = 0;
        for (int i = 0; i < plan.size(); i++) {
            x0 = Math.min(x0, plan.x(i)); y0 = Math.min(y0, plan.y(i)); z0 = Math.min(z0, plan.z(i));
            x1 = Math.max(x1, plan.x(i)); y1 = Math.max(y1, plan.y(i)); z1 = Math.max(z1, plan.z(i));
        }
        minX = x0; minY = y0; minZ = z0; maxX = x1; maxY = y1; maxZ = z1;
    }

    public List<Marker> markers(String kind) {
        List<Marker> out = new ArrayList<>();
        for (Marker m : markers) if (m.kind.equals(kind)) out.add(m);
        return out;
    }

    public static String planId(WreckCore core, WreckTier tier) { return core.id + "_" + tier.id; }

    private static final Map<String, WreckPlan> CACHE = new HashMap<>();

    public static WreckPlan get(MinecraftServer server, String id) {
        WreckPlan p = CACHE.get(id);
        if (p != null) return p;
        ResourceLocation rl = ResourceLocation.fromNamespaceAndPath(Driftwrecks.MOD_ID, "wreck/" + id + ".ncga");
        try (InputStream in = server.getResourceManager().getResourceOrThrow(rl).open()) {
            p = read(id, in.readAllBytes());
        } catch (IOException e) {
            throw new IllegalStateException("Missing wreck plan " + rl, e);
        }
        CACHE.put(id, p);
        return p;
    }

    public static void clearCache() { CACHE.clear(); }

    static WreckPlan read(String id, byte[] bytes) throws IOException {
        BlockPlan plan = BlockPlan.read(bytes);
        ByteBuffer b = plan.trailer;
        String fill = BlockPlan.readString(b);
        int n = b.getShort() & 0xFFFF;
        List<Marker> markers = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            String kind = BlockPlan.readString(b);
            BlockPos pos = new BlockPos(b.getShort(), b.getShort(), b.getShort());
            markers.add(new Marker(kind, pos, b.get() & 0xFF));
        }
        return new WreckPlan(id, plan, fill, List.copyOf(markers));
    }
}
