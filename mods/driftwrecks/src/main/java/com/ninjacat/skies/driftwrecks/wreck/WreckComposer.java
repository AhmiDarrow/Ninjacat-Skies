package com.ninjacat.skies.driftwrecks.wreck;

import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;

import java.util.*;

/**
 * Assembles a wreck from parts, so no two drift in alike: a procedural keel and deck (six deck shapes), the core's
 * signature module (three variants per core and tier, turned to any of four bearings), a handful of shared annex ruins
 * placed and turned at random on the free deck, tethered satellite islets on Ruins and Holds, the frayed seam, rim
 * erosion, and finally the objective markers spread over whatever ground the result offers. Everything follows from
 * one seed. Output is role-keyed (the Strand skin is applied later by {@link WreckBuilder}).
 */
public final class WreckComposer {
    public static final int VARIANTS = 3;
    public static final String[] ANNEXES = {"ruined_wall", "broken_arch", "watch_post", "shed", "well", "statue", "garden_bed", "stair_ruin",
            "tower_stump", "column_field", "market_stall", "gazebo", "obelisk", "lantern_row", "fallen_bell", "cistern", "kiln", "loom_ruin"};
    private static final Set<String> WALKABLE = Set.of("floor", "soil", "keel", "keel2", "accent", "trim", "metal");
    private static final int[] PILLARS = {3, 4, 5}, CHESTS = {2, 4, 6}, SPAWNERS = {1, 2, 4}, MOBS = {4, 6, 8};
    private static final int[] KEEL = {4, 6, 9}, EXTRA = {1, 3, 3}, MIN_R = {6, 11, 16};
    private static final int[] HEIGHT = {12, 24, 40};

    public enum Shape { DISC, OVAL, CRESCENT, TWIN, TERRACED, SHATTERED }

    /** A composed wreck: role-keyed blocks relative to the origin, markers, bounds, and what it was made of. */
    public static final class Layout {
        public final Map<BlockPos, String> blocks = new LinkedHashMap<>();
        public final List<WreckPlan.Marker> markers = new ArrayList<>();
        public String fill = "wall";
        public String description = "";
        public int minX, minY, minZ, maxX, maxY, maxZ;

        void bounds() {
            minX = minY = minZ = Integer.MAX_VALUE; maxX = maxY = maxZ = Integer.MIN_VALUE;
            for (BlockPos p : blocks.keySet()) {
                if ("x_air".equals(blocks.get(p))) continue;
                minX = Math.min(minX, p.getX()); minY = Math.min(minY, p.getY()); minZ = Math.min(minZ, p.getZ());
                maxX = Math.max(maxX, p.getX()); maxY = Math.max(maxY, p.getY()); maxZ = Math.max(maxZ, p.getZ());
            }
        }

        public List<WreckPlan.Marker> markers(String kind) {
            List<WreckPlan.Marker> out = new ArrayList<>();
            for (WreckPlan.Marker m : markers) if (m.kind().equals(kind)) out.add(m);
            return out;
        }

        /** A fixed plan (the Heartwreck) as a layout. */
        public static Layout of(WreckPlan plan) {
            Layout l = new Layout();
            for (int i = 0; i < plan.plan.size(); i++) l.blocks.put(plan.plan.pos(i), plan.plan.keyOf(i));
            l.markers.addAll(plan.markers);
            l.fill = plan.fill;
            l.description = plan.id;
            l.bounds();
            return l;
        }
    }

    private WreckComposer() {}

    public static String corePlan(WreckCore core, WreckTier tier, int variant) { return "core/" + core.id + "_" + tier.id + "_" + variant; }

    public static Layout compose(MinecraftServer server, WreckCore core, WreckTier tier, long seed) {
        Random rng = new Random(seed);
        int t = tier.ordinal();
        int variant = rng.nextInt(VARIANTS);
        // a Ruin may grow around a Raft's core, a Hold around a Ruin's: the room left over fills with annexes and islets
        WreckTier coreTier = switch (tier) {
            case RAFT -> WreckTier.RAFT;
            case RUIN -> rng.nextBoolean() ? WreckTier.RAFT : WreckTier.RUIN;
            case HOLD -> rng.nextFloat() < 0.6F ? WreckTier.RUIN : WreckTier.HOLD;
        };
        WreckPlan cp = WreckPlan.get(server, corePlan(core, coreTier, variant));
        int coreTurn = rng.nextInt(4);
        double coreR = cp.radius();
        int cap = tier.maxSize / 2;
        int minR = MIN_R[t] + rng.nextInt(3);
        int R = (int) Math.min(cap - (t == 0 ? 0 : 2), Math.max(minR, Math.ceil(coreR) + EXTRA[t] + rng.nextInt(2)));
        Shape shape = Shape.values()[rng.nextInt(Shape.values().length)];

        Layout L = new Layout();
        L.fill = cp.fill;
        Map<Long, Integer> top = deck(shape, R, coreR, rng);                 // column -> deck top y
        keel(L, top, R, KEEL[t] + rng.nextInt(2), rng, 0, 0);
        for (Map.Entry<Long, Integer> e : top.entrySet()) {
            int x = BlockPos.getX(e.getKey()), z = BlockPos.getZ(e.getKey());
            for (int y = 0; y <= e.getValue(); y++) L.blocks.put(new BlockPos(x, y, z), rng.nextInt(9) == 0 ? "keel2" : (y == e.getValue() ? "floor" : "keel"));
        }
        Set<BlockPos> reserved = new HashSet<>();
        merge(L, cp, BlockPos.ZERO, coreTurn, reserved);

        // annexes on the free deck
        List<String> names = new ArrayList<>(List.of(ANNEXES));
        Collections.shuffle(names, rng);
        int want = switch (tier) { case RAFT -> rng.nextInt(2); case RUIN -> 2 + rng.nextInt(3); case HOLD -> 4 + rng.nextInt(4); };
        List<double[]> taken = new ArrayList<>();
        taken.add(new double[]{0, 0, coreR + 0.5});
        List<String> placed = new ArrayList<>();
        for (String name : names) {
            if (placed.size() >= want) break;
            WreckPlan ap = WreckPlan.get(server, "annex/" + name);
            double ar = ap.radius();
            for (int attempt = 0; attempt < 40; attempt++) {
                double a = rng.nextDouble() * Math.PI * 2, d = coreR + ar + 1 + rng.nextDouble() * Math.max(0.5, R - coreR - 2 * ar - 1);
                int cx = (int) Math.round(Math.cos(a) * d), cz = (int) Math.round(Math.sin(a) * d);
                if (!fitsOnDeck(top, cx, cz, ar) || overlaps(taken, cx, cz, ar)) continue;
                int y = top.getOrDefault(BlockPos.asLong(cx, 0, cz), 0);
                merge(L, ap, new BlockPos(cx, y, cz), rng.nextInt(4), reserved);
                taken.add(new double[]{cx, cz, ar});
                placed.add(name);
                break;
            }
        }

        // satellite islets, tethered by a plank bridge
        int sats = switch (tier) { case RAFT -> 0; case RUIN -> rng.nextFloat() < 0.5F ? 1 : 0; case HOLD -> rng.nextFloat() < 0.4F ? 2 : 1; };
        for (int i = 0; i < sats; i++) satellite(server, L, top, R, cap, rng, reserved, names, placed);

        seam(L, R, KEEL[t], rng);
        erode(L, reserved, 0.12F + 0.05F * t, rng);
        clampHeight(L, HEIGHT[t]);
        spreadMarkers(L, reserved, tier, top, R, rng);
        if (tier == WreckTier.HOLD && L.markers("rift").isEmpty()) {
            List<BlockPos> ground = new ArrayList<>();
            for (Map.Entry<BlockPos, String> e : L.blocks.entrySet()) if (standable(L, e.getKey().above(), reserved)) ground.add(e.getKey().above());
            ground.sort(Comparator.comparingInt((BlockPos b) -> b.getX()).thenComparingInt(BlockPos::getZ).thenComparingInt(BlockPos::getY));
            if (!ground.isEmpty()) { BlockPos r = ground.get(rng.nextInt(ground.size())); L.markers.add(new WreckPlan.Marker("rift", r, 0)); reserved.add(r); }
        }
        L.bounds();
        L.description = core.id + "_" + coreTier.id + "_" + variant + " " + shape.name().toLowerCase(Locale.ROOT) + " r" + R
                + (placed.isEmpty() ? "" : " + " + String.join(",", placed)) + (sats > 0 ? " + " + sats + " islet" + (sats > 1 ? "s" : "") : "");
        return L;
    }

    // ------------------------------------------------------------------ deck and keel

    private static Map<Long, Integer> deck(Shape shape, int R, double coreR, Random rng) {
        Map<Long, Integer> top = new HashMap<>();
        double a = rng.nextDouble() * Math.PI * 2, ca = Math.cos(a), sa = Math.sin(a);
        double squash = 0.68 + rng.nextDouble() * 0.12;
        for (int x = -R - 1; x <= R + 1; x++) for (int z = -R - 1; z <= R + 1; z++) {
            double d = Math.sqrt(x * x + z * z);
            double u = x * ca + z * sa, v = -x * sa + z * ca;                // shape axes
            boolean in = switch (shape) {
                case DISC, TERRACED -> d * d <= R * R + R * 0.8;
                case OVAL -> (u / R) * (u / R) + (v / (R * squash)) * (v / (R * squash)) <= 1.04;
                case CRESCENT -> d <= R + 0.4 && Math.hypot(u - R * 0.95, v) > R * 0.72;
                case TWIN -> Math.hypot(u + R * 0.42, v) <= R * 0.62 || Math.hypot(u - R * 0.5, v) <= R * 0.52;
                case SHATTERED -> d <= R + 0.4 && !(d > coreR + 2 && Math.abs(Math.sin(Math.atan2(v, u) * 1.5)) < 0.22);
            };
            if (d <= coreR + 1.2) in = true;                                   // the core always stands on ground
            if (!in) continue;
            int y = shape == Shape.TERRACED && u > Math.max(coreR + 1.5, R * 0.35) ? 1 : 0;
            top.put(BlockPos.asLong(x, 0, z), y);
        }
        return top;
    }

    private static void keel(Layout L, Map<Long, Integer> top, int R, int depth, Random rng, int cx, int cz) {
        double[] lump = new double[7];
        for (int i = 0; i < lump.length; i++) lump[i] = rng.nextDouble() * Math.PI * 2;
        for (long k : top.keySet()) {
            int x = BlockPos.getX(k), z = BlockPos.getZ(k);
            double d = Math.hypot(x - cx, z - cz) / Math.max(1, R);
            double ang = Math.atan2(z - cz, x - cx), wob = 0;
            for (int i = 0; i < lump.length; i++) wob += Math.cos(ang * (i + 2) + lump[i]);
            int dd = (int) Math.round(depth * (1 - Math.pow(Math.min(1, d), 1.25)) * (1 + 0.12 * wob / lump.length)) + 1;
            for (int y = 1; y <= dd; y++) L.blocks.putIfAbsent(new BlockPos(x, -y, z), y == 1 ? "soil" : ((x * 7 + z * 13 + y * 5) % 5 == 0 ? "keel2" : "keel"));
            if (d < 0.35 && rng.nextInt(9) == 0) for (int y = dd + 1; y <= dd + 1 + rng.nextInt(3); y++) L.blocks.putIfAbsent(new BlockPos(x, -y, z), "keel");
        }
    }

    private static boolean fitsOnDeck(Map<Long, Integer> top, int cx, int cz, double r) {
        Integer y0 = top.get(BlockPos.asLong(cx, 0, cz));
        if (y0 == null) return false;
        int ri = (int) Math.ceil(r);
        for (int x = -ri; x <= ri; x++) for (int z = -ri; z <= ri; z++) {
            if (x * x + z * z > r * r + 0.5) continue;
            Integer y = top.get(BlockPos.asLong(cx + x, 0, cz + z));
            if (y == null || !y.equals(y0)) return false;
        }
        return true;
    }

    private static boolean overlaps(List<double[]> taken, int cx, int cz, double r) {
        for (double[] o : taken) if (Math.hypot(o[0] - cx, o[1] - cz) < o[2] + r + 1.5) return true;
        return false;
    }

    private static void satellite(MinecraftServer server, Layout L, Map<Long, Integer> mainTop, int R, int cap, Random rng,
                                  Set<BlockPos> reserved, List<String> names, List<String> placed) {
        int r = 3 + rng.nextInt(2);
        int reach = Math.min(cap - r - 1, R + 4 + rng.nextInt(3));
        if (reach <= R + 2) return;
        for (int attempt = 0; attempt < 12; attempt++) {
            double a = rng.nextDouble() * Math.PI * 2;
            int cx = (int) Math.round(Math.cos(a) * reach), cz = (int) Math.round(Math.sin(a) * reach);
            int y0 = rng.nextInt(5) - 2;
            boolean clear = true;
            for (BlockPos p : L.blocks.keySet()) if (Math.hypot(p.getX() - cx, p.getZ() - cz) < r + 2 && Math.abs(p.getY() - y0) < 6) { clear = false; break; }
            if (!clear) continue;
            Map<Long, Integer> top = new HashMap<>();
            for (int x = -r; x <= r; x++) for (int z = -r; z <= r; z++) if (x * x + z * z <= r * r + r * 0.6) top.put(BlockPos.asLong(cx + x, 0, cz + z), 0);
            Map<BlockPos, String> shifted = new LinkedHashMap<>();
            Layout tmp = new Layout();
            keel(tmp, top, r, 3 + rng.nextInt(2), rng, cx, cz);
            for (Map.Entry<BlockPos, String> e : tmp.blocks.entrySet()) shifted.put(e.getKey().above(y0), e.getValue());
            for (long k : top.keySet()) shifted.put(new BlockPos(BlockPos.getX(k), y0, BlockPos.getZ(k)), "floor");
            for (Map.Entry<BlockPos, String> e : shifted.entrySet()) L.blocks.putIfAbsent(e.getKey(), e.getValue());
            // a small annex on the islet, half the time
            if (rng.nextBoolean()) for (String n : names) {
                if (placed.contains(n)) continue;
                WreckPlan ap = WreckPlan.get(server, "annex/" + n);
                if (ap.radius() > r - 0.5) continue;
                merge(L, ap, new BlockPos(cx, y0, cz), rng.nextInt(4), reserved);
                placed.add(n);
                break;
            }
            // plank bridge from the main deck's edge toward the islet
            double ux = Math.cos(a), uz = Math.sin(a);
            int from = R - 1, to = reach - r + 1;
            for (int s = from; s <= to; s++) {
                int x = (int) Math.round(ux * s), z = (int) Math.round(uz * s);
                int yMain = mainTop.getOrDefault(BlockPos.asLong(x, 0, z), 0);
                double f = (double) (s - from) / Math.max(1, to - from);
                int y = (int) Math.round(yMain + (y0 - yMain) * f);
                L.blocks.putIfAbsent(new BlockPos(x, y, z), "floor");
                if (s % 3 == 0) {
                    L.blocks.putIfAbsent(new BlockPos(x + (int) Math.round(-uz), y + 1, z + (int) Math.round(ux)), "fence");
                    L.blocks.putIfAbsent(new BlockPos(x - (int) Math.round(-uz), y + 1, z - (int) Math.round(ux)), "fence");
                }
            }
            return;
        }
    }

    // ------------------------------------------------------------------ modules

    /** Rotate a module a quarter turn at a time into the layout; carved air cuts the rock beneath. */
    private static void merge(Layout L, WreckPlan plan, BlockPos at, int turns, Set<BlockPos> reserved) {
        for (int i = 0; i < plan.plan.size(); i++) {
            BlockPos p = at.offset(rotate(plan.plan.pos(i), turns));
            L.blocks.put(p, rotateKey(plan.plan.keyOf(i), turns));
        }
        for (WreckPlan.Marker m : plan.markers) {
            BlockPos p = at.offset(rotate(m.pos(), turns));
            L.markers.add(new WreckPlan.Marker(m.kind(), p, m.data()));
            reserved.add(p);
        }
    }

    static BlockPos rotate(BlockPos p, int turns) {
        int x = p.getX(), z = p.getZ();
        for (int i = 0; i < (turns & 3); i++) { int nx = -z; z = x; x = nx; }
        return new BlockPos(x, p.getY(), z);
    }

    private static final String[] DIRS = {"north", "east", "south", "west"};

    /** Turn directional keys with their module: stair_n/e/s/w and facing=/axis= in literal block states. */
    static String rotateKey(String key, int turns) {
        turns &= 3;
        if (turns == 0) return key;
        String prefix = "";
        if (key.startsWith("h_")) { prefix = "h_"; key = key.substring(2); }
        if (key.startsWith("stair_")) {
            String dir = key.substring(6, 7), rest = key.substring(7);
            int i = "nesw".indexOf(dir);
            if (i >= 0) return prefix + "stair_" + "nesw".charAt((i + turns) & 3) + rest;
        }
        if (key.startsWith("mc:") && key.contains("[")) {
            for (int i = 0; i < 4; i++) {
                String f = "facing=" + DIRS[i];
                if (key.contains(f)) { key = key.replace(f, "facing=" + DIRS[(i + turns) & 3]); break; }
            }
            if ((turns & 1) == 1) {
                if (key.contains("axis=x")) key = key.replace("axis=x", "axis=z");
                else if (key.contains("axis=z")) key = key.replace("axis=z", "axis=x");
            }
        }
        return prefix + key;
    }

    // ------------------------------------------------------------------ seam, erosion, height

    private static void seam(Layout L, int R, int depth, Random rng) {
        double a = rng.nextDouble() * Math.PI * 2;
        for (int d = 0; d < depth + 2; d++) {
            double rr = R * (1 - Math.pow((double) d / Math.max(1, depth + 2), 1.25));
            double jitter = (rng.nextDouble() - 0.5) * 0.5;
            for (int w = -1; w <= 1; w++) {
                double ang = a + jitter + w * 0.08;
                BlockPos p = new BlockPos((int) Math.round(Math.cos(ang) * rr), -1 - d, (int) Math.round(Math.sin(ang) * rr));
                if (L.blocks.containsKey(p) && !"x_air".equals(L.blocks.get(p))) L.blocks.put(p, (d + w) % 3 != 0 ? "seam" : "seam2");
            }
        }
        for (int i = 0; i < 4; i++) {
            double ang = a + (i - 1.5) * 0.15;
            int x = (int) Math.round(Math.cos(ang) * R), z = (int) Math.round(Math.sin(ang) * R);
            for (int d = 1; d <= 1 + rng.nextInt(3); d++) L.blocks.putIfAbsent(new BlockPos(x, -d, z), i % 2 == 0 ? "mc:cyan_wool" : "mc:yellow_wool");
        }
    }

    private static void erode(Layout L, Set<BlockPos> reserved, float prob, Random rng) {
        List<BlockPos> drop = new ArrayList<>();
        for (Map.Entry<BlockPos, String> e : L.blocks.entrySet()) {
            BlockPos p = e.getKey();
            String k = e.getValue();
            if (p.getY() < 1 || k.startsWith("mc:") || k.startsWith("h_") || k.startsWith("seam") || k.equals("x_air")) continue;
            if (reserved.contains(p.above())) continue;
            int exposed = 0;
            for (int[] d : new int[][]{{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) if (!solid(L, p.offset(d[0], 0, d[1]))) exposed++;
            if (exposed >= 2 && !solid(L, p.above()) && rng.nextFloat() < prob) drop.add(p);
        }
        for (BlockPos p : drop) L.blocks.remove(p);
    }

    private static boolean solid(Layout L, BlockPos p) {
        String k = L.blocks.get(p);
        return k != null && !k.equals("x_air");
    }

    private static void clampHeight(Layout L, int limit) {
        int top = Integer.MIN_VALUE;
        for (Map.Entry<BlockPos, String> e : L.blocks.entrySet()) if (!"x_air".equals(e.getValue())) top = Math.max(top, e.getKey().getY());
        int floor = top - limit + 1;
        L.blocks.keySet().removeIf(p -> p.getY() < floor);
    }

    // ------------------------------------------------------------------ markers

    private static boolean standable(Layout L, BlockPos p, Set<BlockPos> reserved) {
        String below = L.blocks.get(p.below());
        return below != null && WALKABLE.contains(below) && !solid(L, p) && !solid(L, p.above()) && !reserved.contains(p)
                && !"x_air".equals(below);
    }

    private static void spreadMarkers(Layout L, Set<BlockPos> reserved, WreckTier tier, Map<Long, Integer> top, int R, Random rng) {
        int t = tier.ordinal();
        List<BlockPos> cells = new ArrayList<>();
        for (Map.Entry<BlockPos, String> e : L.blocks.entrySet()) {
            BlockPos up = e.getKey().above();
            if (standable(L, up, reserved)) cells.add(up);
        }
        cells.sort(Comparator.comparingInt((BlockPos p) -> p.getX()).thenComparingInt(BlockPos::getY).thenComparingInt(BlockPos::getZ));
        spread(L, reserved, "pillar", PILLARS[t], cells, rng, 4, true);
        int chests = (int) L.markers.stream().filter(m -> m.kind().equals("chest") && m.data() == 0).count();
        spread(L, reserved, "chest", Math.max(0, CHESTS[t] - 1 - chests), cells, rng, 4, false);
        spread(L, reserved, "spawner", SPAWNERS[t], cells, rng, 5, false);
        int mobs = (int) L.markers.stream().filter(m -> m.kind().equals("mob")).count();
        spread(L, reserved, "mob", Math.max(2, MOBS[t] - mobs), cells, rng, 3, false);
        if (L.markers("echo").isEmpty()) spread(L, reserved, "echo", 1, cells, rng, 2, false);
        if (L.markers("center").isEmpty()) {
            BlockPos best = null;
            for (BlockPos c : cells) if (!reserved.contains(c) && (best == null || c.distSqr(BlockPos.ZERO) < best.distSqr(BlockPos.ZERO))) best = c;
            if (best != null) { L.markers.add(new WreckPlan.Marker("center", best, 0)); reserved.add(best); }
        }
        // tether landings: the deck edge at the four bearings
        int[][] dirs = {{0, -1}, {1, 0}, {0, 1}, {-1, 0}};
        for (int i = 0; i < 4; i++) {
            for (int rr = R + 2; rr > 0; rr--) {
                int x = dirs[i][0] * rr, z = dirs[i][1] * rr;
                Integer y = top.get(BlockPos.asLong(x, 0, z));
                if (y == null) continue;
                BlockPos p = new BlockPos(x, y, z);
                if (solid(L, p) && !solid(L, p.above())) { L.markers.add(new WreckPlan.Marker("dock", p, i)); break; }
            }
        }
    }

    private static void spread(Layout L, Set<BlockPos> reserved, String kind, int n, List<BlockPos> cells, Random rng, int gap, boolean indexed) {
        if (n <= 0 || cells.isEmpty()) return;
        Map<Integer, List<BlockPos>> buckets = new TreeMap<>();
        for (BlockPos c : cells) {
            double ang = (Math.atan2(c.getZ(), c.getX()) + Math.PI * 2) % (Math.PI * 2);
            buckets.computeIfAbsent((int) (ang / (Math.PI * 2) * Math.max(1, n) * 2), k -> new ArrayList<>()).add(c);
        }
        List<Integer> order = new ArrayList<>(buckets.keySet());
        Collections.shuffle(order, rng);
        int placed = 0;
        for (int round = 0; round < 2 && placed < n; round++) {
            for (int b : order) {
                if (placed >= n) break;
                List<BlockPos> opts = new ArrayList<>();
                for (BlockPos c : round == 0 ? buckets.get(b) : cells)
                    if (!reserved.contains(c) && farFromMarkers(L, c, round == 0 ? gap : 2)) opts.add(c);
                if (opts.isEmpty()) continue;
                BlockPos c = opts.get(rng.nextInt(opts.size()));
                L.markers.add(new WreckPlan.Marker(kind, c, indexed ? placed : 0));
                reserved.add(c);
                placed++;
                if (round == 1) break;
            }
        }
    }

    private static boolean farFromMarkers(Layout L, BlockPos c, int gap) {
        for (WreckPlan.Marker m : L.markers) {
            BlockPos p = m.pos();
            if (Math.abs(p.getX() - c.getX()) + Math.abs(p.getY() - c.getY()) + Math.abs(p.getZ() - c.getZ()) < gap) return false;
        }
        return true;
    }
}
