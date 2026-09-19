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

    @GameTest(template = "empty")
    public static void plansLoadAndSkinsResolve(GameTestHelper h) {
        var server = h.getLevel().getServer();
        for (WreckCore c : WreckCore.ALL) for (WreckTier t : WreckTier.ALL) {
            WreckPlan p = WreckPlan.get(server, WreckPlan.planId(c, t));
            int w = p.maxX - p.minX + 1, d = p.maxZ - p.minZ + 1, hgt = p.maxY - p.minY + 1;
            if (w > t.maxSize || d > t.maxSize) h.fail(p.id + " footprint " + w + "x" + d);
            if (p.plan.size() < 200) h.fail(p.id + " too few blocks");
            for (String need : new String[]{"chest", "idol", "pillar", "spawner", "dock", "echo", "center", "mob"})
                if (p.markers(need).isEmpty()) h.fail(p.id + " has no " + need + " marker");
            if (t == WreckTier.HOLD && p.markers("rift").isEmpty()) h.fail(p.id + " has no rift");
            if (hgt > 40) h.fail(p.id + " too tall");
            for (String key : p.plan.keys) for (Strand s : Strand.ALL) {
                String k = key.startsWith("h_") ? key.substring(2) : key;
                if (k.equals("air")) continue;
                if (StrandSkin.resolve(s, k).isAir()) h.fail(p.id + " key " + key + " resolves to air in " + s.id());
            }
        }
        WreckPlan heart = WreckPlan.get(server, "heartwreck");
        if (heart.markers("district").size() != 9) h.fail("heartwreck needs nine districts");
        h.succeed();
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
            WreckPlan plan = WreckPlan.get(level.getServer(), active.planId);
            WreckChestBlockEntity chest = null;
            for (WreckPlan.Marker m : plan.markers("chest"))
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
            WreckPlan plan = WreckPlan.get(level.getServer(), active.planId);
            for (WreckPlan.Marker m : plan.markers("chest"))
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
            WreckPlan plan = WreckPlan.get(level.getServer(), active.planId);
            for (WreckPlan.Marker mk : plan.markers("spawner")) {
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
