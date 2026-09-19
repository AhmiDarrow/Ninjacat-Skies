package com.ninjacat.skies.driftwrecks.wreck;

import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.DriftConfig;
import com.ninjacat.skies.driftwrecks.Driftwrecks;
import com.ninjacat.skies.driftwrecks.block.FrayedSpawnerBlockEntity;
import com.ninjacat.skies.driftwrecks.block.SalvageCrateBlockEntity;
import com.ninjacat.skies.driftwrecks.block.ThreadPillarBlock;
import com.ninjacat.skies.driftwrecks.block.WreckChestBlockEntity;
import com.ninjacat.skies.driftwrecks.entity.StewardEchoEntity;
import com.ninjacat.skies.driftwrecks.registry.DwBlocks;
import com.ninjacat.skies.driftwrecks.registry.DwItems;
import com.ninjacat.skies.driftwrecks.registry.DwRegistries;
import com.ninjacat.skies.lib.NinjacatText;
import com.ninjacat.skies.lib.plan.BuildQueue;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.GlobalPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.HoverEvent;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.item.FallingBlockEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.*;

/**
 * Runs every Driftwreck: Drift pressure, arrival and building, online-time lifetime, warnings, crumble, objectives
 * and the unravel. Saved with the overworld; wrecks live in the overworld (the Skies).
 */
public final class DriftManager extends SavedData {
    public static final String MOB_TAG = "driftwrecks_wreck";
    private static final int SLOW = 20;             // bookkeeping cadence (ticks)
    private static final int BUILD_TICKS = 100;     // arrival spectacle: ~5 s
    private static final int UNRAVEL_TICKS = 60;    // unravel spectacle: ~3 s

    private final Map<Integer, Wreck> wrecks = new TreeMap<>();
    private int nextId = 1;
    private final RandomSource rng = RandomSource.create();

    public static DriftManager get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(new Factory<>(DriftManager::new, DriftManager::load), "driftwrecks");
    }

    public Collection<Wreck> wrecks() { return wrecks.values(); }
    @Nullable public Wreck byId(int id) { return wrecks.get(id); }

    @Nullable
    public Wreck byTeam(UUID team) {
        for (Wreck w : wrecks.values()) if (w.team.equals(team) && w.phase != Wreck.Phase.DONE) return w;
        return null;
    }

    @Nullable
    public Wreck at(BlockPos p, int margin) {
        for (Wreck w : wrecks.values()) if (w.phase != Wreck.Phase.DONE && w.contains(p, margin)) return w;
        return null;
    }

    public static ServerLevel level(MinecraftServer server) { return server.overworld(); }

    // ================================================================== tick

    public void tick(MinecraftServer server) {
        ServerLevel level = level(server);
        boolean enabled = DriftConfig.ENABLED.get();
        boolean slow = server.getTickCount() % SLOW == 0;
        List<Integer> finished = new ArrayList<>();
        for (Wreck w : wrecks.values()) {
            switch (w.phase) {
                case BUILDING -> stepBuild(level, w);
                case ACTIVE -> {
                    if (!enabled) { beginUnravel(level, w, false); break; }
                    if (slow) tickActive(level, w);
                    WreckObjectives.tick(this, level, w);
                }
                case UNRAVELING -> { if (stepUnravel(level, w)) finished.add(w.id); }
                case DONE -> finished.add(w.id);
            }
        }
        for (int id : finished) wrecks.remove(id);
        if (!finished.isEmpty()) setDirty();
        if (slow && enabled) tickPressure(server, level);
    }

    private void tickPressure(MinecraftServer server, ServerLevel level) {
        List<Clowder> all = LoomTension.allClowders(server);
        for (Clowder c : all) {
            if (c.onlineMembers().isEmpty()) continue;
            if (!LoomTension.isSeated(c, Strand.SOIL)) continue;
            if (byTeam(c.id()) != null) continue;
            if (LoomTension.postOf(c) == null) continue;
            TeamDrift t = TeamDrift.of(c);
            int target = t.target(rng, DriftConfig.PRESSURE_MIN_MINUTES.get(), DriftConfig.PRESSURE_MAX_MINUTES.get());
            int p = t.pressure() + SLOW;
            t.setPressure(p);
            t.dirty();
            if (p >= target) {
                Wreck w = arrive(server, c, null);
                if (w != null) { t.resetCycle(); t.dirty(); }
            }
        }
    }

    // ================================================================== arrival

    /** A fixed roll (admin summon, tests). Any null field is rolled. */
    public record Roll(@Nullable WreckCore core, @Nullable Strand skin, @Nullable WreckModifier modifier,
                       @Nullable WreckObjective objective, @Nullable WreckTier tier, boolean heartwreck, @Nullable BlockPos origin) {
        public static Roll random() { return new Roll(null, null, null, null, null, false, null); }
    }

    /** Roll and start building a wreck for this Clowder. Returns null if no spot was found or rules forbid it. */
    @Nullable
    public Wreck arrive(MinecraftServer server, Clowder c, @Nullable Roll fixed) {
        if (byTeam(c.id()) != null) return null;
        ServerLevel level = level(server);
        GlobalPos post = LoomTension.postOf(c);
        Roll r = fixed == null ? Roll.random() : fixed;
        if (post == null && r.origin() == null) return null;
        TeamDrift team = TeamDrift.of(c);
        int seated = Integer.bitCount(LoomTension.strandBits(c));
        List<Strand> open = new ArrayList<>();
        for (Strand s : Strand.ALL) if (LoomTension.isSeated(c, s)) open.add(s);
        if (open.isEmpty()) open.add(Strand.SOIL);

        boolean heart = r.heartwreck() || (fixed == null && team.heartwreck() == 1);
        WreckTier tier = r.tier() != null ? r.tier() : heart ? WreckTier.HOLD : rollTier(seated);
        if (tier == null) return null;
        Strand skin = r.skin() != null ? r.skin() : rollSkin(team, open);
        WreckCore core = heart ? null : r.core() != null ? r.core() : rollCore(team, skin);
        WreckModifier mod = heart ? WreckModifier.UNMARKED : r.modifier() != null ? r.modifier() : rollModifier(tier);
        WreckObjective obj = heart ? WreckObjective.RETHREAD : r.objective() != null ? r.objective() : rollObjective(tier);
        String planId = heart ? "heartwreck" : WreckPlan.planId(core, tier);
        WreckPlan plan;
        try { plan = WreckPlan.get(server, planId); } catch (IllegalStateException e) { Driftwrecks.LOGGER.error("{}", e.getMessage()); return null; }

        BlockPos origin = r.origin();
        if (origin == null) {
            origin = Placement.find(level, post.pos(), plan, rng, c.id(), wrecks.values(), LoomTension.allClowders(server));
            if (origin == null) {
                Driftwrecks.LOGGER.info("No clear sky for {}'s driftwreck this cycle", c.name().getString());
                return null;
            }
        }
        boolean hidden = core != null && team.hiddenRoomOpen(core);
        Wreck w = new Wreck(nextId++, c.id(), planId, core, tier, skin, mod, obj, heart, origin, hidden);
        w.minX = origin.getX() + plan.minX; w.minY = origin.getY() + plan.minY; w.minZ = origin.getZ() + plan.minZ;
        w.maxX = origin.getX() + plan.maxX; w.maxY = origin.getY() + plan.maxY; w.maxZ = origin.getZ() + plan.maxZ;
        float life = tier.lifetimeTicks * mod.lifetime * team.lifetimeBonus() * DriftConfig.LIFETIME_MULTIPLIER.get().floatValue();
        w.lifetime = Math.max(20 * 60, Math.round(life));
        if (heart) { team.setHeartwreck(2); team.dirty(); }
        if (fixed == null) {
            if (team.lureStrand() != null) team.setLureStrand(null);
            if (team.scrollPending()) team.setScrollPending(false);
            team.dirty();
        }

        BuildQueue q = new BuildQueue(BuildQueue.Mode.PLACE, w.id);
        for (Map.Entry<BlockPos, BlockState> e : WreckBuilder.build(plan, w, rng).entrySet()) q.add(origin.offset(e.getKey()), e.getValue());
        w.placed = q;
        wrecks.put(w.id, w);
        setDirty();
        level.playSound(null, w.center(), DwRegistries.sound("driftwreck.arrive"), SoundSource.AMBIENT, 6.0F, 0.9F);
        Driftwrecks.LOGGER.info("Driftwreck {} ({} {} {} {} {}) drifting to {} for {}", w.id, planId, skin.id(), mod.id, obj.id,
                hidden ? "hidden" : "sealed", origin.toShortString(), c.name().getString());
        return w;
    }

    @Nullable
    private WreckTier rollTier(int seated) {
        WreckTier top = WreckTier.highestFor(seated);
        if (top == null) return null;
        int roll = rng.nextInt(100);
        return switch (top) {
            case RAFT -> WreckTier.RAFT;
            case RUIN -> roll < 40 ? WreckTier.RAFT : WreckTier.RUIN;
            case HOLD -> roll < 15 ? WreckTier.RAFT : roll < 50 ? WreckTier.RUIN : WreckTier.HOLD;
        };
    }

    private Strand rollSkin(TeamDrift team, List<Strand> open) {
        Strand lure = team.lureStrand();
        if (lure != null && open.contains(lure) && rng.nextFloat() < 0.6F) return lure;
        // completed columns lean a little harder toward their skin (+10%)
        float total = 0;
        float[] w = new float[open.size()];
        for (int i = 0; i < open.size(); i++) { w[i] = team.columnComplete(open.get(i)) ? 1.1F : 1.0F; total += w[i]; }
        float x = rng.nextFloat() * total;
        for (int i = 0; i < open.size(); i++) { x -= w[i]; if (x <= 0) return open.get(i); }
        return open.get(open.size() - 1);
    }

    private WreckCore rollCore(TeamDrift team, Strand skin) {
        if (team.scrollPending()) {
            List<WreckCore> missing = new ArrayList<>();
            for (WreckCore c : WreckCore.ALL) if (!team.hasCell(skin, c)) missing.add(c);
            if (!missing.isEmpty()) return missing.get(rng.nextInt(missing.size()));
        }
        return WreckCore.ALL[rng.nextInt(WreckCore.ALL.length)];
    }

    private WreckModifier rollModifier(WreckTier tier) {
        int total = 0;
        for (WreckModifier m : WreckModifier.ALL) if (tier.ordinal() >= m.minTier.ordinal()) total += m.weight;
        int x = rng.nextInt(total);
        for (WreckModifier m : WreckModifier.ALL) {
            if (tier.ordinal() < m.minTier.ordinal()) continue;
            x -= m.weight;
            if (x < 0) return m;
        }
        return WreckModifier.UNMARKED;
    }

    private WreckObjective rollObjective(WreckTier tier) {
        int total = 0;
        for (WreckObjective o : WreckObjective.ALL) if (tier.ordinal() >= o.minTier.ordinal()) total += o.weight;
        int x = rng.nextInt(total);
        for (WreckObjective o : WreckObjective.ALL) {
            if (tier.ordinal() < o.minTier.ordinal()) continue;
            x -= o.weight;
            if (x < 0) return o;
        }
        return WreckObjective.SALVAGE;
    }

    // ================================================================== building

    private void stepBuild(ServerLevel level, Wreck w) {
        BuildQueue q = w.placed;
        if (q == null) { w.phase = Wreck.Phase.DONE; return; }
        int budget = Math.min(DriftConfig.BLOCKS_PER_TICK.get(), Math.max(20, (q.size() + BUILD_TICKS - 1) / BUILD_TICKS));
        int from = q.cursor();
        q.step(level, budget);
        // drifting-in particles on the layer just laid
        for (int i = 0; i < 6 && q.size() > 0; i++) {
            int idx = Math.min(q.size() - 1, from + rng.nextInt(Math.max(1, q.cursor() - from + 1)));
            BlockPos p = q.posAt(idx);
            level.sendParticles(ParticleTypes.ASH, p.getX() + 0.5, p.getY() + 0.5, p.getZ() + 0.5, 4, 0.8, 0.8, 0.8, 0.02);
            level.sendParticles(ParticleTypes.GLOW, p.getX() + 0.5, p.getY() + 0.5, p.getZ() + 0.5, 1, 0.5, 0.5, 0.5, 0.01);
        }
        if (q.done()) finishBuild(level, w);
        setDirty();
    }

    private void finishBuild(ServerLevel level, Wreck w) {
        MinecraftServer server = level.getServer();
        WreckPlan plan = WreckPlan.get(server, w.planId);
        List<Integer> pillars = new ArrayList<>();
        for (WreckPlan.Marker m : plan.markers) {
            BlockPos p = w.origin.offset(m.pos());
            BlockEntity be = level.getBlockEntity(p);
            if (be instanceof WreckChestBlockEntity chest) chest.setup(w, m.data() == 1, m.data() == 2);
            if (be instanceof FrayedSpawnerBlockEntity sp) { sp.setup(w, rng); w.spawnersLeft++; }
            if (m.kind().equals("pillar") && level.getBlockState(p).is(DwBlocks.THREAD_PILLAR.get())) pillars.add(m.data());
            if (m.kind().equals("district") && w.heartwreck) pillars.add(100 + m.data());
        }
        if (w.heartwreck) {
            pillars.clear();
            for (int i = 0; i < 9; i++) pillars.add(i);
            w.pillarOrder = pillars.stream().mapToInt(Integer::intValue).toArray();
        } else if (!pillars.isEmpty()) {
            Collections.shuffle(pillars, new Random(rng.nextLong()));
            w.pillarOrder = pillars.stream().mapToInt(Integer::intValue).toArray();
        }
        spawnMobs(level, w, plan);
        if (w.objective == WreckObjective.ESCORT) {
            for (WreckPlan.Marker m : plan.markers("echo")) {
                StewardEchoEntity echo = DwRegistries.STEWARD_ECHO.get().create(level);
                if (echo == null) break;
                BlockPos p = w.origin.offset(m.pos());
                echo.moveTo(p.getX() + 0.5, p.getY(), p.getZ() + 0.5, rng.nextFloat() * 360, 0);
                echo.bind(w.id);
                level.addFreshEntity(echo);
                w.echo = echo.getUUID();
                break;
            }
        }
        w.phase = Wreck.Phase.ACTIVE;
        if (w.modifier == WreckModifier.UNSTABLE) w.crumbleCursor = 0;
        announceArrival(server, w);
        setDirty();
    }

    private void spawnMobs(ServerLevel level, Wreck w, WreckPlan plan) {
        List<WreckPlan.Marker> spots = plan.markers("mob");
        if (spots.isEmpty()) return;
        int online = LoomTension.clowderById(level.getServer(), w.team).map(c -> c.onlineMembers().size()).orElse(1);
        float scale = partyScale(online);
        int base = w.heartwreck ? 0 : switch (w.tier) { case RAFT -> 2; case RUIN -> 4; case HOLD -> 6; };
        int n = Math.round(base * scale);
        for (int i = 0; i < n; i++) {
            WreckPlan.Marker m = spots.get(i % spots.size());
            EntityType<?> type = mobFor(w, i);
            Entity e = type.create(level);
            if (!(e instanceof Mob mob)) continue;
            BlockPos p = w.origin.offset(m.pos());
            mob.moveTo(p.getX() + 0.5, p.getY(), p.getZ() + 0.5, rng.nextFloat() * 360, 0);
            mob.finalizeSpawn(level, level.getCurrentDifficultyAt(p), MobSpawnType.EVENT, null);
            tagMob(w, mob);
            level.addFreshEntity(mob);
        }
        if (w.modifier == WreckModifier.OVERGROWN) {
            for (int i = 0; i < 2; i++) {
                Entity bee = EntityType.BEE.create(level);
                if (bee == null) continue;
                BlockPos p = w.origin.offset(spots.get(i % spots.size()).pos()).above();
                bee.moveTo(p.getX() + 0.5, p.getY(), p.getZ() + 0.5, 0, 0);
                if (bee instanceof Mob m) tagMob(w, m);
                level.addFreshEntity(bee);
            }
        }
    }

    public void tagMob(Wreck w, Mob mob) {
        mob.setPersistenceRequired();
        mob.getPersistentData().putInt(MOB_TAG, w.id);
        w.mobs.add(mob.getUUID());
        setDirty();
    }

    public static float partyScale(int online) {
        return switch (Math.max(1, Math.min(4, online))) { case 1 -> 1F; case 2 -> 1.5F; case 3 -> 2F; default -> 2.5F; };
    }

    public EntityType<?> mobFor(Wreck w, int i) {
        switch (w.modifier) {
            case FROZEN -> { if (i % 2 == 0) return EntityType.STRAY; }
            case HAUNTED -> { if (i % 3 == 0 && w.tier != WreckTier.RAFT) return EntityType.VEX; if (i % 2 == 0) return EntityType.ZOMBIE; }
            case BURNING -> { if (i % 3 == 0 && w.tier != WreckTier.RAFT) return EntityType.BLAZE; }
            default -> {}
        }
        return switch (i % 4) { case 0 -> EntityType.ZOMBIE; case 1 -> EntityType.SKELETON; case 2 -> EntityType.SPIDER; default -> w.tier == WreckTier.RAFT ? EntityType.ZOMBIE : EntityType.WITCH; };
    }

    private void announceArrival(MinecraftServer server, Wreck w) {
        Optional<Clowder> c = LoomTension.clowderById(server, w.team);
        if (c.isEmpty()) return;
        BlockPos at = w.center();
        String what = w.heartwreck ? "The Heartwreck" : "A " + w.skin.tribe() + " " + w.core.title.toLowerCase(Locale.ROOT);
        String waypoint = "xaero-waypoint:Driftwreck:D:" + at.getX() + ":" + at.getY() + ":" + at.getZ() + ":11:false:0:Internal-overworld-waypoints";
        for (ServerPlayer p : c.get().onlineMembers()) {
            p.sendSystemMessage(NinjacatText.teal(w.heartwreck
                    ? "Every tribe's thread pulls the same way at once. Something enormous is caught on your weft."
                    : "Something old is caught on your weft. It will not hold for long—go."));
            p.sendSystemMessage(NinjacatText.gold(what + " (" + w.tier.title + ", " + w.modifier.title + "): " + w.objective.brief));
            p.sendSystemMessage(Component.literal(waypoint).withStyle(s -> s.withColor(ChatFormatting.DARK_GRAY)
                    .withClickEvent(new ClickEvent(ClickEvent.Action.COPY_TO_CLIPBOARD, at.getX() + " " + at.getY() + " " + at.getZ()))
                    .withHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, Component.literal("Driftwreck at " + at.toShortString())))));
            WreckRewards.award(p, "root");
        }
        w.announced = true;
    }

    // ================================================================== lifetime

    private void tickActive(ServerLevel level, Wreck w) {
        MinecraftServer server = level.getServer();
        Optional<Clowder> c = LoomTension.clowderById(server, w.team);
        boolean online = c.isPresent() && !c.get().onlineMembers().isEmpty();
        if (!online) return;                              // an offline Clowder never loses a wreck
        if (w.heartwreck && w.visitors.isEmpty()) return; // no timer until someone sets foot on it
        w.age += SLOW;
        setDirty();
        float f = w.lifeFraction();
        if (w.warned < 50 && f >= 0.5F) warn(level, c.get(), w, 50, "The weft creaks.");
        if (w.warned < 80 && f >= 0.8F) warn(level, c.get(), w, 80, "It is slipping.");
        if (w.warned < 95 && f >= 0.95F) warn(level, c.get(), w, 95, "Let go, or be taken with it.");
        if (w.warned >= 50 && server.getTickCount() % 100 == 0)
            level.playSound(null, w.center(), DwRegistries.sound("driftwreck.creak"), SoundSource.AMBIENT, 0.4F + w.lifeFraction(), 0.8F);
        if (w.modifier == WreckModifier.HAUNTED && server.getTickCount() % 200 == 0)
            level.playSound(null, w.center(), DwRegistries.sound("driftwreck.whisper"), SoundSource.AMBIENT, 0.6F, 0.7F + rng.nextFloat() * 0.3F);
        boolean crumbling = w.warned >= 80 || w.modifier == WreckModifier.UNSTABLE;
        if (crumbling && server.getTickCount() % 40 == 0) crumble(level, w);
        if (w.warned >= 95) for (BlockPos t : w.tether) if (rng.nextInt(12) == 0)
            level.sendParticles(ParticleTypes.GLOW, t.getX() + 0.5, t.getY() + 0.6, t.getZ() + 0.5, 1, 0.2, 0.1, 0.2, 0.0);
        if (w.age >= w.lifetime) beginUnravel(level, w, true);
    }

    private void warn(ServerLevel level, Clowder c, Wreck w, int at, String line) {
        w.warned = at;
        for (ServerPlayer p : c.onlineMembers()) {
            p.sendSystemMessage(NinjacatText.teal(line));
            if (at == 95) p.playNotifySound(DwRegistries.sound("driftwreck.warn_final"), SoundSource.AMBIENT, 1.0F, 1.0F);
        }
    }

    /** One rim block lets go: the outermost template block still standing falls away into the void. */
    private void crumble(ServerLevel level, Wreck w) {
        BuildQueue q = w.placed;
        if (q == null) return;
        BlockPos c = w.center();
        // walk from the end of a far-first ordering, computed lazily as a sort of indices by distance
        int[] order = rimOrder(w);
        while (w.crumbleCursor < order.length) {
            int i = order[w.crumbleCursor++];
            BlockPos p = q.posAt(i);
            BlockState want = q.stateAt(i);
            BlockState now = level.getBlockState(p);
            if (!now.is(want.getBlock()) || level.getBlockEntity(p) != null || p.getY() < w.origin.getY()) continue;
            if (!level.getBlockState(p.below()).isAir()) continue;   // only overhangs drop; the core stays walkable longest
            FallingBlockEntity.fall(level, p, now);
            level.playSound(null, p, DwRegistries.sound("driftwreck.crumble"), SoundSource.BLOCKS, 0.6F, 0.9F + rng.nextFloat() * 0.2F);
            setDirty();
            return;
        }
    }

    private final Map<Integer, int[]> rimCache = new HashMap<>();
    private int[] rimOrder(Wreck w) {
        return rimCache.computeIfAbsent(w.id, k -> {
            BuildQueue q = w.placed;
            BlockPos c = w.center();
            Integer[] idx = new Integer[q.size()];
            for (int i = 0; i < idx.length; i++) idx[i] = i;
            Arrays.sort(idx, Comparator.comparingDouble((Integer i) -> -q.posAt(i).distSqr(new BlockPos(c.getX(), q.posAt(i).getY(), c.getZ()))));
            int[] out = new int[idx.length];
            for (int i = 0; i < idx.length; i++) out[i] = idx[i];
            return out;
        });
    }

    // ================================================================== objectives

    /** The objective is met: completion bonus, Atlas cell, stamps and the lifetime extension for Hold. */
    public void completeObjective(ServerLevel level, Wreck w) {
        if (w.objectiveDone) return;
        w.objectiveDone = true;
        if (w.objective == WreckObjective.HOLD) w.lifetime += w.lifetime / 2;
        setDirty();
        WreckRewards.complete(this, level, w);
    }

    // ================================================================== unravel

    /** Expiry (or feature off, or admin): lift players home, bundle unlooted chests, clear mobs, then undo the blocks. */
    public void beginUnravel(ServerLevel level, Wreck w, boolean expired) {
        if (w.phase == Wreck.Phase.UNRAVELING || w.phase == Wreck.Phase.DONE) return;
        MinecraftServer server = level.getServer();
        Optional<Clowder> c = LoomTension.clowderById(server, w.team);
        BlockPos home = homeFor(server, w);
        // 1. nobody falls
        for (ServerPlayer p : level.players()) {
            if (p.isSpectator()) continue;
            boolean onIt = w.contains(p.blockPosition(), 3) || nearTether(w, p.position(), 3);
            if (!onIt) continue;
            if (p.isPassenger()) p.stopRiding();
            if (p instanceof net.neoforged.neoforge.common.util.FakePlayer) p.moveTo(home.getX() + 0.5, home.getY(), home.getZ() + 0.5, p.getYRot(), p.getXRot());
            else p.teleportTo(level, home.getX() + 0.5, home.getY(), home.getZ() + 0.5, p.getYRot(), p.getXRot());
            p.setDeltaMovement(Vec3.ZERO); p.fallDistance = 0;
            p.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 120, 0, false, false, true));
            p.playNotifySound(DwRegistries.sound("driftwreck.unravel"), SoundSource.AMBIENT, 1.0F, 1.0F);
            p.displayClientMessage(NinjacatText.teal("The thread snaps. You are home."), true);
        }
        // 2. what players earned is not lost
        if (w.placed != null) {
            Collection<UUID> members = c.map(Clowder::memberIds).orElse(List.of(w.team));
            Map<UUID, List<ItemStack>> bundles = new HashMap<>();
            WreckPlan plan = null;
            try { plan = WreckPlan.get(server, w.planId); } catch (IllegalStateException ignored) {}
            if (plan != null) for (WreckPlan.Marker m : plan.markers("chest")) {
                BlockPos p = w.origin.offset(m.pos());
                level.getChunkAt(p);
                if (level.getBlockEntity(p) instanceof WreckChestBlockEntity chest) {
                    for (UUID u : members) bundles.computeIfAbsent(u, k -> new ArrayList<>()).addAll(chest.salvageFor(level, u));
                }
            }
            deliverBundles(level, w, c.orElse(null), bundles);
        }
        // 3. wreck mobs leave with it
        for (UUID u : w.mobs) { Entity e = level.getEntity(u); if (e != null) e.discard(); }
        if (w.echo != null) { Entity e = level.getEntity(w.echo); if (e != null) e.discard(); }
        // 4-5. template blocks and the tether, only where they are still what we placed
        BuildQueue removal = new BuildQueue(BuildQueue.Mode.REMOVE, w.id);
        if (w.placed != null) {
            w.placed.release(level);
            for (int i = w.placed.size() - 1; i >= 0; i--) removal.add(w.placed.posAt(i), w.placed.stateAt(i));   // top down
        }
        BlockState thread = DwBlocks.TETHER_THREAD.get().defaultBlockState();
        for (int i = w.tether.size() - 1; i >= 0; i--) removal.add(w.tether.get(i), thread);
        w.removal = removal;
        w.phase = Wreck.Phase.UNRAVELING;
        rimCache.remove(w.id);
        level.playSound(null, w.center(), DwRegistries.sound("driftwreck.unravel"), SoundSource.AMBIENT, 5.0F, 1.0F);
        if (expired) c.ifPresent(cl -> { for (ServerPlayer p : cl.onlineMembers()) p.sendSystemMessage(NinjacatText.teal("The driftwreck unravels back into the void.")); });
        setDirty();
    }

    private boolean stepUnravel(ServerLevel level, Wreck w) {
        BuildQueue q = w.removal;
        if (q == null || q.done()) { if (q != null) q.release(level); w.phase = Wreck.Phase.DONE; return true; }
        if (!DriftConfig.FINISH_UNLOADED.get() && !level.isLoaded(w.center())) return false;
        int budget = Math.min(DriftConfig.BLOCKS_PER_TICK.get(), Math.max(20, (q.size() + UNRAVEL_TICKS - 1) / UNRAVEL_TICKS));
        int from = q.cursor();
        q.step(level, budget);
        for (int i = 0; i < 8 && q.cursor() > from; i++) {
            BlockPos p = q.posAt(from + rng.nextInt(q.cursor() - from));
            level.sendParticles(ParticleTypes.END_ROD, p.getX() + 0.5, p.getY() + 0.5, p.getZ() + 0.5, 1, 0.3, 0.3, 0.3, 0.05);
            level.sendParticles(ParticleTypes.GLOW, p.getX() + 0.5, p.getY() + 0.8, p.getZ() + 0.5, 1, 0.2, 0.6, 0.2, 0.02);
        }
        setDirty();
        if (q.done()) { q.release(level); w.phase = Wreck.Phase.DONE; return true; }
        return false;
    }

    public static boolean nearTether(Wreck w, Vec3 pos, double r) {
        for (BlockPos t : w.tether) if (t.distToCenterSqr(pos) <= r * r) return true;
        return false;
    }

    /** Where a Clowder member stands after the unravel: beside their Tension Post, or world spawn. */
    public static BlockPos homeFor(MinecraftServer server, Wreck w) {
        Optional<Clowder> c = LoomTension.clowderById(server, w.team);
        GlobalPos post = c.map(LoomTension::postOf).orElse(null);
        ServerLevel level = level(server);
        BlockPos base = post != null && post.dimension().equals(level.dimension()) ? post.pos() : level.getSharedSpawnPos();
        for (int r = 1; r <= 4; r++)
            for (BlockPos p : BlockPos.betweenClosed(base.offset(-r, -1, -r), base.offset(r, 2, r)))
                if (standable(level, p)) return p.immutable();
        return base.above();
    }

    private static boolean standable(ServerLevel level, BlockPos feet) {
        return level.getBlockState(feet.below()).isSolid() && level.getBlockState(feet).isAir() && level.getBlockState(feet.above()).isAir();
    }

    private void deliverBundles(ServerLevel level, Wreck w, @Nullable Clowder c, Map<UUID, List<ItemStack>> bundles) {
        MinecraftServer server = level.getServer();
        GlobalPos post = c == null ? null : LoomTension.postOf(c);
        SalvageCrateBlockEntity crate = post == null ? null : SalvageCrateBlockEntity.near(server, post);
        BlockPos drop = homeFor(server, w);
        for (Map.Entry<UUID, List<ItemStack>> e : bundles.entrySet()) {
            List<ItemStack> items = e.getValue();
            items.removeIf(ItemStack::isEmpty);
            if (items.isEmpty()) continue;
            String name = Optional.ofNullable(server.getProfileCache()).flatMap(pc -> pc.get(e.getKey())).map(com.mojang.authlib.GameProfile::getName).orElse("a Clowder member");
            ItemStack bundle = com.ninjacat.skies.driftwrecks.item.SalvageBundleItem.of(items, name);
            if (crate != null && crate.insert(bundle)) continue;
            net.minecraft.world.entity.item.ItemEntity ie = new net.minecraft.world.entity.item.ItemEntity(level, drop.getX() + 0.5, drop.getY() + 0.5, drop.getZ() + 0.5, bundle);
            ie.setUnlimitedLifetime();
            level.addFreshEntity(ie);
        }
    }

    // ================================================================== admin

    public void unravelAll(ServerLevel level) {
        for (Wreck w : wrecks.values()) beginUnravel(level, w, false);
    }

    // ================================================================== saved data

    public DriftManager() {}

    public static DriftManager load(CompoundTag tag, HolderLookup.Provider regs) {
        DriftManager m = new DriftManager();
        m.nextId = Math.max(1, tag.getInt("nextId"));
        for (Tag t : tag.getList("wrecks", Tag.TAG_COMPOUND)) {
            Wreck w = Wreck.load((CompoundTag) t, regs);
            if (w != null) { m.wrecks.put(w.id, w); m.nextId = Math.max(m.nextId, w.id + 1); }
        }
        return m;
    }

    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider regs) {
        tag.putInt("nextId", nextId);
        ListTag l = new ListTag();
        for (Wreck w : wrecks.values()) l.add(w.save());
        tag.put("wrecks", l);
        return tag;
    }

    public RandomSource random() { return rng; }

    /** Pillar block at a plan index, for objectives. */
    @Nullable
    public static BlockPos pillarPos(MinecraftServer server, Wreck w, int index) {
        WreckPlan plan = WreckPlan.get(server, w.planId);
        String kind = w.heartwreck ? "district" : "pillar";
        for (WreckPlan.Marker m : plan.markers(kind)) if (m.data() == index) return w.origin.offset(m.pos());
        return null;
    }

    static boolean isPillar(BlockState s) { return s.getBlock() instanceof ThreadPillarBlock; }

    public void give(ServerPlayer p, ItemStack s) { LoomTension.giveOrDrop(p, s); }
    public ItemStack weft(int n) { return new ItemStack(DwItems.SALVAGED_WEFT.get(), n); }
    public void markDirty() { setDirty(); }
    public int size() { return wrecks.size(); }
    public void forget(int id) { wrecks.remove(id); rimCache.remove(id); setDirty(); }
    public static boolean isWreckMob(Entity e) { return e.getPersistentData().contains(MOB_TAG); }
}
