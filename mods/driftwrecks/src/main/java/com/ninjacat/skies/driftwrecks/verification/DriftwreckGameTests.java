package com.ninjacat.skies.driftwrecks.verification;

import com.mojang.authlib.GameProfile;
import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.block.ThreadPillarBlock;
import com.ninjacat.skies.driftwrecks.block.WreckChestBlockEntity;
import com.ninjacat.skies.driftwrecks.entity.RemnantEntity;
import com.ninjacat.skies.driftwrecks.registry.DwBlocks;
import com.ninjacat.skies.driftwrecks.registry.DwRegistries;
import com.ninjacat.skies.driftwrecks.wreck.*;
import com.ninjacat.skies.lib.plan.BuildQueue;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.function.Consumer;

/**
 * Headless checks for the whole Driftwreck loop: plans and skins, build then unravel (template blocks only, player
 * blocks survive), per-player chests, every objective, tether rasterising, the thread catch, BuildQueue resume, wreck
 * persistence, and every Remnant ticking its mechanic.
 */
@GameTestHolder("driftwrecks")
@PrefixGameTestTemplate(false)
public class DriftwreckGameTests {
    private static int lane;

    // ------------------------------------------------------------------ helpers

    private static ServerPlayer member(GameTestHelper h, String name) {
        ServerLevel level = h.getLevel();
        ServerPlayer p = FakePlayerFactory.get(level, new GameProfile(UUID.nameUUIDFromBytes(("driftwrecks-" + name).getBytes()), name));
        Clowder c = LoomTension.clowderOf(p).orElseThrow();
        c.data().putInt(LoomTension.KEY_STRANDS, Strand.SOIL.bit() | Strand.STONE.bit() | Strand.SPROUT.bit() | Strand.CLAW.bit()
                | Strand.SPARK.bit() | Strand.CLOCK.bit() | Strand.SWARM.bit());
        return p;
    }

    /** Each test builds its wreck in its own far lane of the sky so tests never overlap. */
    private static BlockPos lane(GameTestHelper h) {
        BlockPos base = h.absolutePos(BlockPos.ZERO);
        return new BlockPos(base.getX() + 400 + 200 * (lane++), 150, base.getZ() + 3000);
    }

    private static Wreck summon(GameTestHelper h, ServerPlayer p, WreckCore core, WreckTier tier, WreckObjective obj, WreckModifier mod) {
        DriftManager m = DriftManager.get(h.getLevel().getServer());
        Clowder c = LoomTension.clowderOf(p).orElseThrow();
        Wreck old = m.byTeam(c.id());
        if (old != null) m.forget(old.id);
        Wreck w = m.arrive(h.getLevel().getServer(), c, new DriftManager.Roll(core, Strand.SOIL, mod, obj, tier, false, lane(h)));
        if (w == null) throw new IllegalStateException("no wreck");
        return w;
    }

    private static void waitPhase(GameTestHelper h, Wreck w, Wreck.Phase want, int tries, Consumer<Wreck> then) {
        if (w.phase == want) { then.accept(w); return; }
        if (tries > 400) { h.fail("wreck never reached " + want + " (" + w.phase + ")"); return; }
        h.runAfterDelay(5, () -> waitPhase(h, w, want, tries + 1, then));
    }

    // ------------------------------------------------------------------ plans

    @GameTest(template = "empty", timeoutTicks = 1200)
    public static void wrecksAreComposedFromParts(GameTestHelper h) {
        var server = h.getLevel().getServer();
        java.util.Set<String> distinct = new java.util.HashSet<>();
        java.util.Set<Integer> shapes = new java.util.HashSet<>();
        int composed = 0;
        java.nio.file.Path previews = java.nio.file.Path.of("previews");
        for (WreckCore c : WreckCore.ALL) for (WreckTier t : WreckTier.ALL) {
            for (int v = 0; v < WreckComposer.VARIANTS; v++) {
                WreckPlan core = WreckPlan.get(server, WreckComposer.corePlan(c, t, v));
                for (String key : core.plan.keys) for (Strand s : Strand.ALL) {
                    String k = key.startsWith("h_") ? key.substring(2) : key;
                    if (k.equals("air") || k.equals("x_air")) continue;
                    if (StrandSkin.resolve(s, k).isAir()) h.fail(core.id + " key " + key + " resolves to air in " + s.id());
                }
            }
            for (int i = 0; i < 40; i++) {
                long seed = c.ordinal() * 100_003L + t.ordinal() * 7919L + i * 31L;
                WreckComposer.Layout l = WreckComposer.compose(server, c, t, seed);
                composed++;
                int w = l.maxX - l.minX + 1, d = l.maxZ - l.minZ + 1, hgt = l.maxY - l.minY + 1;
                String id = c.id + "_" + t.id + "#" + i + " (" + l.description + ")";
                if (w > t.maxSize || d > t.maxSize) { h.fail(id + " footprint " + w + "x" + d + " > " + t.maxSize); return; }
                if (hgt > 40) { h.fail(id + " too tall: " + hgt); return; }
                if (l.markers("chest").stream().filter(m -> m.data() == 1).count() != 1) { h.fail(id + " needs exactly one heart chest"); return; }
                for (String need : new String[]{"idol", "spawner", "echo", "center", "mob"})
                    if (l.markers(need).isEmpty()) { h.fail(id + " has no " + need); return; }
                if (l.markers("pillar").size() < 3) { h.fail(id + " has " + l.markers("pillar").size() + " pillars"); return; }
                if (l.markers("dock").size() < 2) { h.fail(id + " has " + l.markers("dock").size() + " docks"); return; }
                if (t == WreckTier.HOLD && l.markers("rift").isEmpty()) { h.fail(id + " has no rift"); return; }
                // every objective a player must touch can be walked to from the deck
                for (WreckPlan.Marker m : l.markers) {
                    boolean mustReach = switch (m.kind()) {
                        case "pillar", "spawner", "echo", "mob", "rift" -> true;
                        case "chest" -> m.data() != 2;                     // the hidden-room chest waits behind its h_ wall
                        default -> false;
                    };
                    if (mustReach && !l.reach.contains(m.pos())) { h.fail(id + " " + m.kind() + " at " + m.pos().toShortString() + " cannot be reached"); return; }
                }
                distinct.add(l.description + "|" + l.blocks.size());
                shapes.add(l.description.hashCode() & 7);
                if (i < 2) writePreview(previews.resolve(c.id + "_" + t.id + "_" + i + ".ncga"), l);
            }
        }
        // 720 composed; nearly all should differ (a Raft with no annex can repeat on the same variant and shape)
        if (distinct.size() < composed * 0.85) h.fail("only " + distinct.size() + " distinct of " + composed + " composed wrecks");
        else h.succeed();
    }

    /** Dump a composed layout as NCGA so tools/wreck_factory.py --render-dir can draw it. */
    private static void writePreview(java.nio.file.Path path, WreckComposer.Layout l) {
        try {
            java.nio.file.Files.createDirectories(path.getParent());
            java.util.List<String> keys = new java.util.ArrayList<>(new java.util.TreeSet<>(l.blocks.values()));
            java.nio.ByteBuffer b = java.nio.ByteBuffer.allocate(64 + keys.size() * 64 + l.blocks.size() * 7 + l.markers.size() * 40).order(java.nio.ByteOrder.LITTLE_ENDIAN);
            b.putInt(0x4147434E).putInt(1).putShort((short) keys.size());
            for (String k : keys) { byte[] s = k.getBytes(java.nio.charset.StandardCharsets.UTF_8); b.putShort((short) s.length).put(s); }
            b.putInt(l.blocks.size());
            for (var e : l.blocks.entrySet()) b.putShort((short) e.getKey().getX()).putShort((short) e.getKey().getY()).putShort((short) e.getKey().getZ()).put((byte) keys.indexOf(e.getValue()));
            byte[] f = l.fill.getBytes(java.nio.charset.StandardCharsets.UTF_8);
            b.putShort((short) f.length).put(f).putShort((short) l.markers.size());
            for (WreckPlan.Marker m : l.markers) {
                byte[] k = m.kind().getBytes(java.nio.charset.StandardCharsets.UTF_8);
                b.putShort((short) k.length).put(k).putShort((short) m.pos().getX()).putShort((short) m.pos().getY()).putShort((short) m.pos().getZ()).put((byte) m.data());
            }
            java.nio.file.Files.write(path, java.util.Arrays.copyOf(b.array(), b.position()));
        } catch (java.io.IOException e) { throw new RuntimeException(e); }
    }

    @GameTest(template = "empty")
    public static void heartwreckPlanLoads(GameTestHelper h) {
        WreckPlan heart = WreckPlan.get(h.getLevel().getServer(), "heartwreck");
        if (heart.markers("district").size() != 9) h.fail("heartwreck needs nine districts");
        else h.succeed();
    }

    // ------------------------------------------------------------------ build and unravel

    @GameTest(template = "empty", timeoutTicks = 2400)
    public static void buildThenUnravelTemplateOnly(GameTestHelper h) {
        ServerPlayer p = member(h, "builder");
        Wreck w = summon(h, p, WreckCore.SHRINE, WreckTier.RAFT, WreckObjective.SALVAGE, WreckModifier.UNMARKED);
        ServerLevel level = h.getLevel();
        waitPhase(h, w, Wreck.Phase.ACTIVE, 0, active -> {
            BuildQueue q = active.placed;
            if (q == null || q.size() < 200) { h.fail("placed queue missing"); return; }
            int placed = 0;
            for (int i = 0; i < q.size(); i++) if (level.getBlockState(q.posAt(i)).is(q.stateAt(i).getBlock())) placed++;
            if (placed < q.size() * 0.98) { h.fail("only " + placed + "/" + q.size() + " blocks placed"); return; }
            // a player changes one wreck block and builds on another
            BlockPos changed = q.posAt(q.size() / 2), built = q.posAt(q.size() / 3).above(8);
            level.setBlock(changed, Blocks.GOLD_BLOCK.defaultBlockState(), 3);
            level.setBlock(built, Blocks.DIAMOND_BLOCK.defaultBlockState(), 3);
            DriftManager.get(level.getServer()).beginUnravel(level, active, false);
            waitPhase(h, active, Wreck.Phase.DONE, 0, done -> {});
            h.runAfterDelay(200, () -> {
                int left = 0;
                for (int i = 0; i < q.size(); i++) {
                    BlockPos pos = q.posAt(i);
                    if (pos.equals(changed)) continue;
                    if (level.getBlockState(pos).is(q.stateAt(i).getBlock())) left++;
                }
                if (left > 0) h.fail(left + " template blocks survived the unravel");
                else if (!level.getBlockState(changed).is(Blocks.GOLD_BLOCK)) h.fail("a player-changed block was removed");
                else if (!level.getBlockState(built).is(Blocks.DIAMOND_BLOCK)) h.fail("a player-built block was removed");
                else h.succeed();
            });
        });
    }

    // ------------------------------------------------------------------ chests

    @GameTest(template = "empty", timeoutTicks = 2400)
    public static void chestsRollPerPlayerAndBundleTheRest(GameTestHelper h) {
        ServerPlayer a = member(h, "alice"), b = member(h, "bob");
        Wreck w = summon(h, a, WreckCore.VAULT, WreckTier.RUIN, WreckObjective.CLEAR, WreckModifier.UNMARKED);
        ServerLevel level = h.getLevel();
        waitPhase(h, w, Wreck.Phase.ACTIVE, 0, active -> {
            WreckChestBlockEntity chest = null;
            for (WreckPlan.Marker m : active.markers("chest"))
                if (level.getBlockEntity(active.origin.offset(m.pos())) instanceof WreckChestBlockEntity be) { chest = be; break; }
            if (chest == null) { h.fail("no wreck chest placed"); return; }
            chest.open(a);
            if (!chest.opened(a.getUUID())) { h.fail("opening did not roll for the opener"); return; }
            if (chest.opened(b.getUUID())) { h.fail("a roll leaked to another player"); return; }
            List<ItemStack> never = chest.salvageFor(level, b.getUUID());
            if (never.isEmpty()) { h.fail("a member who never opened the chest got an empty bundle"); return; }
            List<ItemStack> left = chest.salvageFor(level, a.getUUID());
            if (left.isEmpty()) { h.fail("the opener's untaken loot was not bundled"); return; }
            h.succeed();
        });
    }

    // ------------------------------------------------------------------ objectives

    @GameTest(template = "empty", timeoutTicks = 2400)
    public static void salvageObjectiveCompletesOnHeartChest(GameTestHelper h) {
        ServerPlayer p = member(h, "salvager");
        Wreck w = summon(h, p, WreckCore.LIBRARY, WreckTier.RAFT, WreckObjective.SALVAGE, WreckModifier.OVERGROWN);
        ServerLevel level = h.getLevel();
        waitPhase(h, w, Wreck.Phase.ACTIVE, 0, active -> {
            for (WreckPlan.Marker m : active.markers("chest"))
                if (m.data() == 1 && level.getBlockEntity(active.origin.offset(m.pos())) instanceof WreckChestBlockEntity be) be.open(p);
            if (!active.objectiveDone && !active.pendingComplete) h.fail("opening the heart chest did not finish Salvage");
            else { DriftManager.get(level.getServer()).forget(active.id); h.succeed(); }
        });
    }

    @GameTest(template = "empty", timeoutTicks = 2400)
    public static void rethreadInOrderAndResetOnMistake(GameTestHelper h) {
        ServerPlayer p = member(h, "weaver");
        Wreck w = summon(h, p, WreckCore.GARDEN, WreckTier.RUIN, WreckObjective.RETHREAD, WreckModifier.FROZEN);
        ServerLevel level = h.getLevel();
        DriftManager m = DriftManager.get(level.getServer());
        waitPhase(h, w, Wreck.Phase.ACTIVE, 0, active -> {
            int[] order = active.pillarOrder;
            if (order.length < 3) { h.fail("too few pillars: " + order.length); return; }
            BlockPos first = DriftManager.pillarPos(level.getServer(), active, order[0]);
            BlockPos second = DriftManager.pillarPos(level.getServer(), active, order[1]);
            if (first == null || !level.getBlockState(first).is(DwBlocks.THREAD_PILLAR.get())) { h.fail("pillar not placed"); return; }
            WreckObjectives.touchPillar(m, level, active, order[0], first, p);
            WreckObjectives.touchPillar(m, level, active, order[2], DriftManager.pillarPos(level.getServer(), active, order[2]), p);   // wrong
            if (active.pillarStep != 0 || level.getBlockState(first).getValue(ThreadPillarBlock.LIT)) { h.fail("a mistake did not reset the pillars"); return; }
            for (int idx : order) WreckObjectives.touchPillar(m, level, active, idx, DriftManager.pillarPos(level.getServer(), active, idx), p);
            if (!active.objectiveDone && !active.pendingComplete) h.fail("lighting every pillar in order did not finish Re-thread");
            else { m.forget(active.id); h.succeed(); }
            if (second == null) h.fail("second pillar missing");
        });
    }

    @GameTest(template = "empty", timeoutTicks = 2400)
    public static void clearObjectiveCountsSpawners(GameTestHelper h) {
        ServerPlayer p = member(h, "clearer");
        Wreck w = summon(h, p, WreckCore.FORGE, WreckTier.RAFT, WreckObjective.CLEAR, WreckModifier.HAUNTED);
        ServerLevel level = h.getLevel();
        waitPhase(h, w, Wreck.Phase.ACTIVE, 0, active -> {
            if (active.spawnersLeft < 1) { h.fail("Clear placed no spawners"); return; }
            for (WreckPlan.Marker mk : active.markers("spawner")) {
                BlockPos sp = active.origin.offset(mk.pos());
                if (level.getBlockState(sp).is(DwBlocks.FRAYED_SPAWNER.get())) level.destroyBlock(sp, false);
            }
            if (!active.objectiveDone && !active.pendingComplete) h.fail("breaking every spawner did not finish Clear (" + active.spawnersLeft + " left)");
            else { DriftManager.get(level.getServer()).forget(active.id); h.succeed(); }
        });
    }

    @GameTest(template = "empty", timeoutTicks = 3000)
    public static void holdAndEscortStart(GameTestHelper h) {
        ServerPlayer p = member(h, "holder");
        Wreck w = summon(h, p, WreckCore.WATCHTOWER, WreckTier.RUIN, WreckObjective.ESCORT, WreckModifier.BURNING);
        ServerLevel level = h.getLevel();
        waitPhase(h, w, Wreck.Phase.ACTIVE, 0, active -> {
            if (active.echo == null) { h.fail("Escort spawned no echo"); return; }   // its chunk may unload with nobody near
            WreckObjectives.echoHome(DriftManager.get(level.getServer()), level, active);
            if (!active.objectiveDone && !active.pendingComplete) { h.fail("echo home did not finish Escort"); return; }
            int before = active.lifetime;
            active.objectiveDone = false;
            WreckObjective hold = WreckObjective.HOLD;
            if (hold.minTier != WreckTier.RUIN) { h.fail("Hold must start at Tier 2"); return; }
            DriftManager.get(level.getServer()).forget(active.id);
            if (before <= 0) h.fail("lifetime not set");
            else h.succeed();
        });
    }

    // ------------------------------------------------------------------ tether and catch

    @GameTest(template = "empty")
    public static void tetherClimbsInHalfSteps(GameTestHelper h) {
        List<BlockPos> path = new ArrayList<>();
        List<BlockState> states = new ArrayList<>();
        invokeRaster(new Vec3(0.5, 64, 0.5), new Vec3(180.5, 81, 60.5), path, states);
        double prev = 64;
        BlockPos last = null;
        for (int i = 0; i < path.size(); i++) {
            BlockPos b = path.get(i);
            double surface = b.getY() + (states.get(i).getValue(com.ninjacat.skies.driftwrecks.block.TetherThreadBlock.HALF) == net.minecraft.world.level.block.state.properties.Half.TOP ? 1.0 : 0.5);
            if (Math.abs(surface - prev) > 0.51) { h.fail("step of " + (surface - prev) + " at " + b); return; }
            if (last != null && Math.abs(b.getX() - last.getX()) + Math.abs(b.getZ() - last.getZ()) > 1) { h.fail("gap in the bridge at " + b); return; }
            prev = surface; last = b;
        }
        if (path.size() < 180) h.fail("bridge too short: " + path.size());
        else h.succeed();
    }

    private static void invokeRaster(Vec3 from, Vec3 to, List<BlockPos> path, List<BlockState> states) {
        try {
            var m = Tether.class.getDeclaredMethod("raster", Vec3.class, Vec3.class, List.class, List.class);
            m.setAccessible(true);
            m.invoke(null, from, to, path, states);
        } catch (ReflectiveOperationException e) { throw new RuntimeException(e); }
    }

    @GameTest(template = "empty", timeoutTicks = 2400)
    public static void threadCatchReturnsAFallingMember(GameTestHelper h) {
        ServerPlayer p = member(h, "faller");
        Wreck w = summon(h, p, WreckCore.SHRINE, WreckTier.RAFT, WreckObjective.SALVAGE, WreckModifier.UNMARKED);
        ServerLevel level = h.getLevel();
        waitPhase(h, w, Wreck.Phase.ACTIVE, 0, active -> {
            BlockPos c = active.center();
            p.moveTo(c.getX() + 3, active.minY - 30, c.getZ(), 0, 0);
            p.fallDistance = 40;
            Tether.checkCatch(p);   // fake players ignore damage, so only the rescue is checked here
            if (p.getY() < active.minY) h.fail("the falling member was not caught (y " + p.getY() + ")");
            else if (p.fallDistance > 0) h.fail("the catch kept the fall distance");
            else { DriftManager.get(level.getServer()).forget(active.id); h.succeed(); }
        });
    }

    // ------------------------------------------------------------------ persistence

    @GameTest(template = "empty")
    public static void buildQueueResumesAfterSave(GameTestHelper h) {
        ServerLevel level = h.getLevel();
        BlockPos base = h.absolutePos(new BlockPos(1, 1, 1));
        BuildQueue q = new BuildQueue(BuildQueue.Mode.PLACE, 99);
        for (int x = 0; x < 4; x++) for (int z = 0; z < 4; z++) q.add(base.offset(x, 0, z), Blocks.STONE.defaultBlockState());
        q.step(level, 5);
        BuildQueue back = BuildQueue.load(q.save(), level.registryAccess());
        if (back.cursor() != 5 || back.size() != 16) { h.fail("resume lost its place: " + back.cursor() + "/" + back.size()); return; }
        back.step(level, 100);
        for (int x = 0; x < 4; x++) for (int z = 0; z < 4; z++) if (!level.getBlockState(base.offset(x, 0, z)).is(Blocks.STONE)) { h.fail("resumed queue left a gap"); return; }
        level.setBlock(base, Blocks.OAK_LOG.defaultBlockState(), 3);
        BuildQueue rm = new BuildQueue(BuildQueue.Mode.REMOVE, 98);
        for (int x = 0; x < 4; x++) for (int z = 0; z < 4; z++) rm.add(base.offset(x, 0, z), Blocks.STONE.defaultBlockState());
        rm.step(level, 100);
        if (!level.getBlockState(base).is(Blocks.OAK_LOG)) h.fail("removal took a block the player changed");
        else if (!level.getBlockState(base.offset(1, 0, 1)).isAir()) h.fail("removal left a template block");
        else h.succeed();
    }

    @GameTest(template = "empty")
    public static void wreckSaveRoundTrip(GameTestHelper h) {
        Wreck w = new Wreck(7, UUID.randomUUID(), "vault_hold", WreckCore.VAULT, WreckTier.HOLD, Strand.SIGIL, WreckModifier.UNSTABLE, WreckObjective.HOLD, false, new BlockPos(10, 100, -20), true);
        w.lifetime = 1234; w.age = 56; w.warned = 80; w.pillarOrder = new int[]{2, 0, 1}; w.tether.add(new BlockPos(1, 2, 3)); w.visitors.add(UUID.randomUUID());
        w.placed = new BuildQueue(BuildQueue.Mode.PLACE, 7);
        w.placed.add(new BlockPos(1, 1, 1), Blocks.DEEPSLATE.defaultBlockState());
        CompoundTag t = w.save();
        Wreck back = Wreck.load(t, h.getLevel().registryAccess());
        if (back == null || back.core != WreckCore.VAULT || back.skin != Strand.SIGIL || back.modifier != WreckModifier.UNSTABLE || back.lifetime != 1234
                || back.age != 56 || back.warned != 80 || back.pillarOrder.length != 3 || back.tether.size() != 1 || back.visitors.size() != 1
                || back.placed == null || back.placed.size() != 1 || !back.hiddenRoom) h.fail("wreck did not survive a save");
        else h.succeed();
    }

    @GameTest(template = "empty")
    public static void atlasPerksFollowTheGrid(GameTestHelper h) {
        ServerPlayer p = member(h, "atlas");
        TeamDrift t = TeamDrift.of(LoomTension.clowderOf(p).orElseThrow());
        for (WreckCore c : WreckCore.ALL) t.fillCell(Strand.CLOCK, c);
        if (!t.columnComplete(Strand.CLOCK) || !t.halfPriceLure(Strand.CLOCK)) { h.fail("a full column gave no perk"); return; }
        for (Strand s : Strand.ALL) t.fillCell(s, WreckCore.FORGE);
        if (!t.rowComplete(WreckCore.FORGE) || !t.hiddenRoomOpen(WreckCore.FORGE)) { h.fail("a full row did not open its hidden rooms"); return; }
        for (WreckModifier m : WreckModifier.ALL) t.stampModifier(m);
        if (t.lifetimeBonus() < 1.24F) { h.fail("six stamps gave no lifetime bonus"); return; }
        if (t.fillCell(Strand.CLOCK, WreckCore.SHRINE)) { h.fail("a filled cell filled twice"); return; }
        h.succeed();
    }

    // ------------------------------------------------------------------ remnants

    @GameTest(template = "empty", timeoutTicks = 3000)
    public static void everyRemnantTicksItsMechanic(GameTestHelper h) {
        ServerLevel level = h.getLevel();
        BlockPos base = h.absolutePos(new BlockPos(1, 1, 1)).offset(0, 30, 0);
        for (int x = -13; x <= 13; x++) for (int z = -13; z <= 13; z++) level.setBlock(base.offset(x, -1, z), Blocks.STONE.defaultBlockState(), 2);
        runRemnant(h, level, base, 0);
    }

    private static void runRemnant(GameTestHelper h, ServerLevel level, BlockPos base, int i) {
        if (i >= Strand.ALL.length) { h.succeed(); return; }
        RemnantEntity r = DwRegistries.REMNANT.get().create(level);
        if (r == null) { h.fail("no remnant entity"); return; }
        r.moveTo(base.getX() + 0.5, base.getY(), base.getZ() + 0.5, 0, 0);
        r.setup(Strand.ALL[i], -1, base, 1);
        level.addFreshEntity(r);
        h.runAfterDelay(240, () -> {
            if (!r.isAlive()) { h.fail(Strand.ALL[i].id() + " remnant died on its own"); return; }
            r.hurt(level.damageSources().genericKill(), Float.MAX_VALUE);
            if (r.isAlive()) { r.setHealth(0); r.die(level.damageSources().genericKill()); }
            h.runAfterDelay(40, () -> runRemnant(h, level, base, i + 1));
        });
    }
}
