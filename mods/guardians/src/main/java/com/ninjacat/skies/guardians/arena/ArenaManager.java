package com.ninjacat.skies.guardians.arena;

import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.Guardians;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import com.ninjacat.skies.guardians.entity.ModEntities;
import com.ninjacat.skies.guardians.item.ModItems;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.core.HolderLookup;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.portal.DimensionTransition;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.*;

/**
 * Runs the totem -> arena -> return loop. One arena dimension; each fight gets its own slot 4096 blocks apart,
 * rebuilt from the arena's block plan on every summon and cleared on the next reuse. Saved with the overworld.
 */
public final class ArenaManager extends SavedData {
    public static final ResourceKey<Level> ARENA_LEVEL = ResourceKey.create(Registries.DIMENSION, ResourceLocation.fromNamespaceAndPath(Guardians.MOD_ID, "arena"));
    private static final int SLOT_SPACING = 4096, FLOOR_Y = 120, FENCE_MARGIN = 6, RETURN_DELAY = 120, EMPTY_STAGE_TICKS = 20 * 60 * 5;
    private static final String PERSIST_ROOT = Guardians.MOD_ID, RETURN_TAG = "arena_return";

    private final Map<Integer, ArenaInstance> active = new TreeMap<>();
    private final Map<Integer, String> lastKind = new HashMap<>();      // slot -> plan to clear before reuse
    private final Map<UUID, String> pendingRelics = new HashMap<>();    // offline win: kind id delivered on login
    private boolean ticketsRestored;

    public static ArenaManager get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(new Factory<>(ArenaManager::new, ArenaManager::load), "guardians_arenas");
    }

    @Nullable public ArenaInstance instance(int slot) { return active.get(slot); }
    public Collection<ArenaInstance> instances() { return active.values(); }
    @Nullable
    public ArenaInstance instanceOf(Player p) {
        for (ArenaInstance a : active.values()) if (a.party.contains(p.getUUID())) return a;
        return null;
    }

    // ------------------------------------------------------------------ summon
    /** Called by the Frayed Totem. Returns a failure message, or null when the fight started. */
    @Nullable
    public String summon(ServerPlayer summoner, GuardianKind kind) {
        MinecraftServer server = summoner.server;
        if (summoner.isSpectator()) return "A spent life cannot call a guardian.";
        if (inArena(summoner)) return "You are already answering for the Cut.";
        if (instanceOf(summoner) != null) return "Your Clowder is already in an arena.";
        ServerLevel arena = arenaLevel(server);
        if (arena == null) return "The arena is not woven into this world (dimension missing).";
        Optional<Clowder> clowder = LoomTension.clowderOf(summoner);
        if (kind.tier == GuardianKind.Tier.INSANE && (clowder.isEmpty() || !LoomTension.isRewoven(clowder.get())))
            return "That door only opens after the Reweave.";
        if (kind.strand != null && (clowder.isEmpty() || !LoomTension.isSeated(clowder.get(), kind.strand)))
            return "Seat the " + kind.strand.title() + " Strand at your Tension Post first — " + kind.title + " only answers for a Strand that is held.";
        if (kind.strand == null && kind.tier == GuardianKind.Tier.EASY) {
            com.ninjacat.skies.core.tension.Strand need = kind == GuardianKind.LINTGOLEM
                    ? com.ninjacat.skies.core.tension.Strand.SOIL
                    : com.ninjacat.skies.core.tension.Strand.CLAW;
            if (clowder.isEmpty() || !LoomTension.isSeated(clowder.get(), need))
                return "Seat the " + need.title() + " Strand at your Tension Post first — " + kind.title + " only answers for a Strand that is held.";
        }
        // the party: Clowder members online and within 32 blocks of the summoner (they hear the totem)
        List<ServerPlayer> party = new ArrayList<>(); party.add(summoner);
        clowder.ifPresent(c -> { for (ServerPlayer m : c.onlineMembers()) if (m != summoner && m.level() == summoner.level() && m.distanceTo(summoner) < 32 && !m.isSpectator() && instanceOf(m) == null) party.add(m); });
        int slot = 0; while (active.containsKey(slot)) slot++;
        ArenaData data = ArenaData.get(server, kind);
        BlockPos origin = new BlockPos(slot * SLOT_SPACING + (arena.dimension().equals(ARENA_LEVEL) ? 0 : TEST_OFFSET), FLOOR_Y, arena.dimension().equals(ARENA_LEVEL) ? 0 : TEST_OFFSET);
        forceChunks(arena, origin, data.radius + 16, true);
        clearSlot(arena, slot, origin);
        build(arena, data, origin);
        ArenaInstance inst = new ArenaInstance(slot, kind, origin, data.radius);
        inst.clowderId = clowder.map(Clowder::id).orElse(null);
        for (ServerPlayer p : party) inst.party.add(p.getUUID());
        active.put(slot, inst); lastKind.put(slot, kind.id); setDirty();
        // pull the party in
        for (int i = 0; i < party.size(); i++) {
            ServerPlayer p = party.get(i);
            storeReturnPoint(p);
            BlockPos pad = data.pads.isEmpty() ? BlockPos.ZERO : data.pads.get(i % data.pads.size());
            teleportToPad(p, arena, origin, pad);
            p.sendSystemMessage(NinjacatText.gold("The Frayed Totem calls ").append(NinjacatText.teal(kind.title)).append(NinjacatText.gold(" to answer for the Cut.")));
            p.displayClientMessage(NinjacatText.teal("Prove worthiness. Fall, and the totem is spent."), true);
        }
        // the guardian
        GuardianEntity boss = ModEntities.create(kind, arena);
        if (boss != null) {
            boss.moveTo(origin.getX() + 0.5, origin.getY(), origin.getZ() + 0.5, 180, 0);
            boss.bindArena(slot, inst.clowderId);
            double scale = 0.6 + 0.4 * party.size();
            boss.getAttribute(Attributes.MAX_HEALTH).setBaseValue(kind.baseHealth * scale); boss.setHealth(boss.getMaxHealth());
            boss.finalizeSpawn(arena, arena.getCurrentDifficultyAt(origin), MobSpawnType.EVENT, null);
            arena.addFreshEntity(boss); inst.boss = boss.getUUID();
            arena.playSound(null, origin, SoundEvents.WITHER_SPAWN, SoundSource.HOSTILE, 3.0F, 0.6F);
        } else {
            wipe(server, inst, "The guardian did not answer. The totem is spent.");   // no boss would mean a stage that never ends
        }
        setDirty();
        return null;
    }

    /** The arena dimension; the game-test server has no datapack dimensions, so tests fall back to a far corner of the overworld. */
    @Nullable
    public static ServerLevel arenaLevel(MinecraftServer server) {
        ServerLevel l = server.getLevel(ARENA_LEVEL);
        if (l == null && TEST_FALLBACK) return server.overworld();
        return l;
    }
    private static final boolean TEST_FALLBACK = Boolean.getBoolean("guardians.arenaFallbackOverworld");
    private static final int TEST_OFFSET = 200000;
    public static boolean inArena(ServerPlayer p) {
        if (p.level().dimension().equals(ARENA_LEVEL)) return inGuardianSlots(p.getX());   // Driftwreck rifts share the dimension at X < 0
        return TEST_FALLBACK && p.getX() > TEST_OFFSET - 4096;
    }
    /** Guardian slots sit at X = slot * 4096 ≥ 0; Driftwreck rift chambers at X = -4096·n. */
    public static boolean inGuardianSlots(double x) { return x > -SLOT_SPACING / 2.0; }
    public static boolean inGuardianSlots(Level level, BlockPos pos) {
        return level.dimension().equals(ARENA_LEVEL) && inGuardianSlots(pos.getX());
    }
    private static int slotAt(int x) { return Math.floorDiv(x + SLOT_SPACING / 2, SLOT_SPACING); }

    // ------------------------------------------------------------------ player blocks and drops
    private final Map<Integer, Set<Long>> placed = new HashMap<>();   // slot -> player-placed positions, cleared before reuse
    private static final String DEATH_STASH = "death_stash";

    /** A player set a block on a stage: remember it so the next fight in that slot does not inherit it. */
    public void onPlayerPlaced(BlockPos pos) {
        if (placed.computeIfAbsent(slotAt(pos.getX()), k -> new HashSet<>()).add(pos.asLong())) setDirty();
    }

    /** Dying on a stage: the slot is torn down before you can walk back, so the drops wait for you at home. */
    public static boolean stashDeathDrops(ServerPlayer p, Collection<net.minecraft.world.entity.item.ItemEntity> drops) {
        if (!inArena(p) || drops.isEmpty()) return false;
        CompoundTag persisted = p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        CompoundTag root = persisted.getCompound(PERSIST_ROOT);
        ListTag stash = root.getList(DEATH_STASH, Tag.TAG_COMPOUND);
        for (var e : drops) if (!e.getItem().isEmpty()) stash.add(e.getItem().save(p.registryAccess()));
        root.put(DEATH_STASH, stash); persisted.put(PERSIST_ROOT, root); p.getPersistentData().put(Player.PERSISTED_NBT_TAG, persisted);
        return true;
    }

    private static void returnDeathDrops(ServerPlayer p) {
        if (p.isDeadOrDying() || inArena(p)) return;
        CompoundTag persisted = p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        CompoundTag root = persisted.getCompound(PERSIST_ROOT);
        ListTag stash = root.getList(DEATH_STASH, Tag.TAG_COMPOUND);
        if (stash.isEmpty()) return;
        root.remove(DEATH_STASH); persisted.put(PERSIST_ROOT, root); p.getPersistentData().put(Player.PERSISTED_NBT_TAG, persisted);
        for (int i = 0; i < stash.size(); i++)
            ItemStack.parse(p.registryAccess(), stash.getCompound(i)).ifPresent(s -> LoomTension.giveOrDrop(p, s));
        p.displayClientMessage(NinjacatText.teal("What you dropped on the stage came home with you."), true);
    }

    private void build(ServerLevel level, ArenaData data, BlockPos origin) {
        BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
        for (int i = 0; i < data.size(); i++) {
            BlockPos p = data.pos(i); m.set(origin.getX() + p.getX(), origin.getY() + p.getY(), origin.getZ() + p.getZ());
            level.setBlock(m, data.state(i), 2 | 16);
        }
        // the return gate is sealed until the fight ends: fill the sheet with barrier blocks
        setGate(level, data, origin, true);
    }

    private void setGate(ServerLevel level, ArenaData data, BlockPos origin, boolean sealed) {
        ArenaData.Gate g = data.gate; BlockPos base = origin.offset(g.pos());
        for (int s = -(g.width()/2) + 1; s < g.width()/2; s++)
            for (int y = 0; y < g.height(); y++) {
                BlockPos p = g.alongX() ? base.offset(s, y, 0) : base.offset(0, y, s);
                level.setBlock(p, sealed ? Blocks.BARRIER.defaultBlockState() : Blocks.AIR.defaultBlockState(), 3);
            }
    }

    private void clearSlot(ServerLevel level, int slot, BlockPos origin) {
        Set<Long> mine = placed.remove(slot);
        if (mine != null) { for (long l : mine) level.setBlock(BlockPos.of(l), Blocks.AIR.defaultBlockState(), 2 | 16); setDirty(); }
        String prev = lastKind.get(slot); if (prev == null) return;
        GuardianKind k = GuardianKind.byId(prev); if (k == null) return;
        ArenaData old = ArenaData.get(level.getServer(), k);
        BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
        for (int i = 0; i < old.size(); i++) { BlockPos p = old.pos(i); m.set(origin.getX() + p.getX(), origin.getY() + p.getY(), origin.getZ() + p.getZ()); level.setBlock(m, Blocks.AIR.defaultBlockState(), 2 | 16); }
        AABB box = new AABB(origin).inflate(old.radius + 40, 120, old.radius + 40);
        for (Entity e : level.getEntities((Entity) null, box, e -> !(e instanceof Player))) e.discard();
    }

    private static void forceChunks(ServerLevel level, BlockPos origin, int radius, boolean on) {
        ChunkPos c = new ChunkPos(origin); int r = radius / 16 + 1;
        for (int dx = -r; dx <= r; dx++) for (int dz = -r; dz <= r; dz++) level.setChunkForced(c.x + dx, c.z + dz, on);
    }

    // ------------------------------------------------------------------ teleports
    private static void dismount(ServerPlayer p) {
        if (p.isPassenger()) p.stopRiding();
        if (p.isVehicle()) p.ejectPassengers();
    }

    private static void teleportToPad(ServerPlayer p, ServerLevel arena, BlockPos origin, BlockPos pad) {
        double x = origin.getX() + pad.getX() + 0.5, y = origin.getY() + pad.getY() + 0.1, z = origin.getZ() + pad.getZ() + 0.5;
        Vec3 stand = snapToStand(arena, x, y, z);
        if (stand != null) { x = stand.x; y = stand.y; z = stand.z; }
        float yaw = (float) Math.toDegrees(Math.atan2(-(origin.getX() + 0.5 - x), origin.getZ() + 0.5 - z));
        dismount(p);
        if (p instanceof net.neoforged.neoforge.common.util.FakePlayer) p.moveTo(x, y, z, yaw, 0);   // fake players have no connection to teleport through
        else p.teleportTo(arena, x, y, z, yaw, 0);
        p.setDeltaMovement(Vec3.ZERO); p.fallDistance = 0;
    }

    private static void storeReturnPoint(ServerPlayer p) {
        CompoundTag persisted = p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        CompoundTag root = persisted.getCompound(PERSIST_ROOT); CompoundTag ret = new CompoundTag();
        ret.putString("dim", p.level().dimension().location().toString()); ret.putDouble("x", p.getX()); ret.putDouble("y", p.getY()); ret.putDouble("z", p.getZ());
        ret.putFloat("yaw", p.getYRot()); ret.putFloat("pitch", p.getXRot()); root.put(RETURN_TAG, ret);
        persisted.put(PERSIST_ROOT, root); p.getPersistentData().put(Player.PERSISTED_NBT_TAG, persisted);
    }

    /** Send a player home to where they used the totem (or spawn). */
    public static void returnHome(ServerPlayer p) {
        CompoundTag root = p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).getCompound(PERSIST_ROOT);
        ServerLevel target = null; Vec3 at = null; float yaw = 0, pitch = 0;
        if (root.contains(RETURN_TAG)) {
            CompoundTag r = root.getCompound(RETURN_TAG); ResourceLocation dim = ResourceLocation.tryParse(r.getString("dim"));
            if (dim != null) target = p.server.getLevel(ResourceKey.create(Registries.DIMENSION, dim));
            at = new Vec3(r.getDouble("x"), r.getDouble("y"), r.getDouble("z")); yaw = r.getFloat("yaw"); pitch = r.getFloat("pitch");
        }
        if (target == null || target.dimension().equals(ARENA_LEVEL) || (TEST_FALLBACK && at != null && at.x > TEST_OFFSET - 4096)) { target = p.server.overworld(); BlockPos s = target.getSharedSpawnPos(); at = Vec3.atBottomCenterOf(s.above()); }
        Vec3 stand = snapToStand(target, at.x, at.y, at.z);
        if (stand == null) {
            BlockPos respawn = p.getRespawnPosition();
            ServerLevel pad = respawn == null ? null : p.server.getLevel(p.getRespawnDimension());
            if (pad != null && !pad.dimension().equals(ARENA_LEVEL)) {
                stand = snapToStand(pad, respawn.getX() + 0.5, respawn.getY() + 1, respawn.getZ() + 0.5);
                if (stand != null) target = pad;
            }
        }
        if (stand == null) {
            target = p.server.overworld();
            BlockPos s = target.getSharedSpawnPos();
            stand = snapToStand(target, s.getX() + 0.5, s.getY() + 1, s.getZ() + 0.5);
            if (stand == null) stand = Vec3.atBottomCenterOf(s.above());
        }
        at = stand;
        dismount(p);
        if (p instanceof net.neoforged.neoforge.common.util.FakePlayer) p.moveTo(at.x, at.y, at.z, yaw, pitch);
        else p.teleportTo(target, at.x, at.y, at.z, yaw, pitch);
        p.setDeltaMovement(Vec3.ZERO); p.fallDistance = 0;
    }

    private static Vec3 snapToStand(ServerLevel level, double x, double y, double z) {
        for (int dy = 0; dy <= 24; dy++) {
            if (safeToStand(level, x, y - dy, z)) return new Vec3(x, y - dy, z);
            if (dy > 0 && safeToStand(level, x, y + dy, z)) return new Vec3(x, y + dy, z);
        }
        return null;
    }

    private static boolean safeToStand(ServerLevel level, double x, double y, double z) {
        BlockPos feet = BlockPos.containing(x, y, z);
        var atFeet = level.getBlockState(feet);
        if (!atFeet.getCollisionShape(level, feet).isEmpty() && atFeet.isCollisionShapeFullBlock(level, feet)) return false;
        boolean footing = !atFeet.getCollisionShape(level, feet).isEmpty()
                || level.getBlockState(feet.below()).blocksMotion()
                || !level.getBlockState(feet.below()).getCollisionShape(level, feet.below()).isEmpty();
        if (!footing) return false;
        BlockPos head = feet.above();
        return !level.getBlockState(head).isSuffocating(level, head)
                && !level.getBlockState(head.above()).isSuffocating(level, head.above());
    }

    // ------------------------------------------------------------------ ticking
    public void tick(MinecraftServer server) {
        if (active.isEmpty()) return;
        ServerLevel arena = arenaLevel(server); if (arena == null) return;
        if (!ticketsRestored) {
            ticketsRestored = true;
            for (ArenaInstance inst : active.values())
                if (inst.state == ArenaInstance.State.FIGHT)
                    forceChunks(arena, inst.originPos, inst.radius + 16, true);
        }
        List<Integer> done = new ArrayList<>();
        for (ArenaInstance inst : active.values()) {
            inst.age++; inst.stateTicks++;
            List<ServerPlayer> inside = inst.onlinePlayers();
            ArenaData data = ArenaData.get(server, inst.kind);
            // fence: nobody falls into the void or wanders off the stage
            for (ServerPlayer p : inside) {
                double dx = p.getX() - (inst.originPos.getX() + 0.5), dz = p.getZ() - (inst.originPos.getZ() + 0.5);
                boolean out = Math.max(Math.abs(dx), Math.abs(dz)) > inst.radius + FENCE_MARGIN || p.getY() < inst.originPos.getY() - 14;
                if (out) {
                    int idx = Math.max(0, inst.party.indexOf(p.getUUID()));
                    BlockPos pad = data.pads.isEmpty() ? BlockPos.ZERO : data.pads.get(idx % data.pads.size());
                    double x = inst.originPos.getX() + pad.getX() + 0.5, y = inst.originPos.getY() + pad.getY() + 0.1, z = inst.originPos.getZ() + pad.getZ() + 0.5;
                    Vec3 stand = snapToStand(arena, x, y, z);
                    if (stand != null) { x = stand.x; y = stand.y; z = stand.z; }
                    dismount(p);
                    p.teleportTo(arena, x, y, z, p.getYRot(), p.getXRot());
                    p.setDeltaMovement(Vec3.ZERO); p.fallDistance = 0;
                    float dmg = inst.kind == GuardianKind.EDGEWALKER || inst.kind.tier == GuardianKind.Tier.INSANE ? 12 : 6;
                    p.hurt(p.damageSources().fellOutOfWorld(), Math.min(dmg, Math.max(0, p.getHealth() - 1)));
                    p.displayClientMessage(NinjacatText.teal("The Loom pulls you back onto the stage."), true);
                }
            }
            switch (inst.state) {
                case FIGHT -> {
                    inst.emptyTicks = inside.isEmpty() ? inst.emptyTicks + 1 : 0;
                    if (inside.isEmpty() && inst.age > 100 && partyWithdrawn(server, inst)) {
                        // they walked out without /guardians leave — spend the totem
                        wipe(server, inst, "Nobody stands. The totem is spent.");
                    }
                    // one member staying offline must not hold the stage (and 81 forced chunks) forever
                    else if (inst.emptyTicks > EMPTY_STAGE_TICKS) {
                        wipe(server, inst, "The stage stood empty too long. The totem is spent.");
                    }
                    // a full disconnect leaves party UUIDs with no online players: keep the stage until they log back in
                    else if (inst.boss != null && inst.age > 100 && arena.isLoaded(inst.originPos) && arena.getEntity(inst.boss) == null && inst.age % 20 == 0) {
                        // boss vanished (killed by /kill or unloaded) — count it as a win only if it actually died via die()
                        wipe(server, inst, "The guardian slipped the weave. The totem is spent.");
                    }
                }
                case WON -> { if (inst.stateTicks > RETURN_DELAY + 60) { sendEveryoneHome(server, inst); done.add(inst.slot); } }
                case WIPED -> { if (inst.stateTicks > RETURN_DELAY) { sendEveryoneHome(server, inst); done.add(inst.slot); } }
            }
        }
        for (int slot : done) {
            ArenaInstance i = active.remove(slot);
            if (i == null) continue;
            // purge while the chunks are still forced: entity sections load asynchronously, so clearSlot on the
            // next summon would miss drops, minions or a stray boss that then wake up inside someone else's fight
            AABB box = new AABB(i.originPos).inflate(i.radius + 40, 120, i.radius + 40);
            for (Entity e : arena.getEntities((Entity) null, box, e -> !(e instanceof Player))) e.discard();
            forceChunks(arena, i.originPos, i.radius + 16, false);
        }
        if (!done.isEmpty()) setDirty();
    }

    private void sendEveryoneHome(MinecraftServer server, ArenaInstance inst) {
        ItemStack relic = inst.state == ArenaInstance.State.WON ? ModItems.relic(inst.kind) : ItemStack.EMPTY;
        List<UUID> grant = !inst.winners.isEmpty() ? new ArrayList<>(inst.winners) : new ArrayList<>(inst.party);
        for (UUID id : grant) {
            ServerPlayer p = server.getPlayerList().getPlayer(id);
            if (p != null && inArena(p)) returnHome(p);
            // Grant after the pad teleport so a full inventory drops at home, not in the arena
            // (clearSlot discards leftover item entities). Spectator leftovers stash until revive.
            if (!relic.isEmpty()) {
                if (p != null) LoomTension.giveOrDrop(p, relic.copy());
                else pendingRelics.put(id, inst.kind.id);
            }
        }
        ServerLevel arena = arenaLevel(server);
        if (arena != null && inst.boss != null) { Entity e = arena.getEntity(inst.boss); if (e instanceof GuardianEntity g) { g.cleanupArena(); g.discard(); } }
    }

    public void wipe(MinecraftServer server, ArenaInstance inst, String line) {
        if (inst.state != ArenaInstance.State.FIGHT) return;
        inst.state = ArenaInstance.State.WIPED; inst.stateTicks = 0; setDirty();
        for (UUID id : inst.party) { ServerPlayer p = server.getPlayerList().getPlayer(id); if (p != null) p.sendSystemMessage(NinjacatText.teal(line)); }
        ServerLevel arena = arenaLevel(server);
        if (arena != null) { ArenaData data = ArenaData.get(server, inst.kind); setGate(arena, data, inst.originPos, false); }
    }

    /** The guardian died: every party member present gets the relic, the win is recorded on the Clowder, the gate opens. */
    public void onWin(ArenaInstance inst, GuardianEntity boss) {
        if (inst.state != ArenaInstance.State.FIGHT) return;
        MinecraftServer server = boss.getServer(); if (server == null) return;
        inst.state = ArenaInstance.State.WON; inst.stateTicks = 0; setDirty();
        ServerLevel arena = arenaLevel(server);
        if (arena != null) setGate(arena, ArenaData.get(server, inst.kind), inst.originPos, false);
        // onlinePlayers() skips spectators. A last-life killing blow spectates before this 8-tick win.
        List<ServerPlayer> present = new ArrayList<>();
        for (UUID id : inst.party) {
            ServerPlayer p = server.getPlayerList().getPlayer(id);
            if (p != null) present.add(p);
        }
        inst.winners.clear();
        inst.winners.addAll(inst.party);
        for (ServerPlayer p : present) {
            p.sendSystemMessage(NinjacatText.gold(inst.kind.title + " answers for the Cut. ").append(NinjacatText.teal("The Strand re-tensions.")));
            p.displayClientMessage(NinjacatText.gold("Worthy. The gate opens; you will be returned shortly."), true);
            p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG); // ensure exists
            recordDefeat(p, inst.kind);
        }
        if (!present.isEmpty()) LoomTension.clowderOf(present.get(0)).ifPresent(c -> {
            CompoundTag d = c.data(); CompoundTag g = d.getCompound(Guardians.MOD_ID);
            ListTag l = g.getList("defeated", Tag.TAG_STRING);
            boolean has = false; for (Tag t : l) if (t.getAsString().equals(inst.kind.id)) has = true;
            if (!has) l.add(net.minecraft.nbt.StringTag.valueOf(inst.kind.id));
            g.put("defeated", l); d.put(Guardians.MOD_ID, g); c.markDirty();
        });
    }

    private static void recordDefeat(ServerPlayer p, GuardianKind kind) {
        CompoundTag persisted = p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        CompoundTag root = persisted.getCompound(PERSIST_ROOT); ListTag l = root.getList("defeated", Tag.TAG_STRING);
        boolean has = false; for (Tag t : l) if (t.getAsString().equals(kind.id)) has = true;
        if (!has) l.add(net.minecraft.nbt.StringTag.valueOf(kind.id));
        root.put("defeated", l); persisted.put(PERSIST_ROOT, root); p.getPersistentData().put(Player.PERSISTED_NBT_TAG, persisted);
        net.minecraft.advancements.AdvancementHolder adv = p.server.getAdvancements().get(ResourceLocation.fromNamespaceAndPath(Guardians.MOD_ID, "defeat/" + kind.id));
        if (adv != null) for (String c : p.getAdvancements().getOrStartProgress(adv).getRemainingCriteria()) p.getAdvancements().award(adv, c);
    }

    public static boolean hasDefeated(ServerPlayer p, GuardianKind kind) {
        ListTag l = p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).getCompound(PERSIST_ROOT).getList("defeated", Tag.TAG_STRING);
        for (Tag t : l) if (t.getAsString().equals(kind.id)) return true;
        return false;
    }

    /** Disconnected members keep the stage. Spectators and pad-side survivors do not. */
    private static boolean partyWithdrawn(MinecraftServer server, ArenaInstance inst) {
        boolean anyOnline = false;
        for (UUID id : inst.party) {
            ServerPlayer p = server.getPlayerList().getPlayer(id);
            if (p == null) return false;
            anyOnline = true;
            if (p.isAlive() && !p.isSpectator() && inArena(p)) return false;
        }
        return anyOnline;
    }

    /** A player who logs in inside the arena dimension with no running fight is sent home. */
    public void onLogin(ServerPlayer p) {
        ArenaInstance inst = instanceOf(p);
        // a disconnect mid-fight puts you back on your pad; a death does not (respawn routes here too)
        if (inst != null && inst.state == ArenaInstance.State.FIGHT && !inArena(p) && !inst.fallen.contains(p.getUUID())) {
            if (p.isSpectator()) { returnHome(p); return; }
            ServerLevel arena = arenaLevel(p.server);
            if (arena != null) {
                ArenaData data = ArenaData.get(p.server, inst.kind);
                int idx = Math.max(0, inst.party.indexOf(p.getUUID()));
                BlockPos pad = data.pads.isEmpty() ? BlockPos.ZERO : data.pads.get(idx % data.pads.size());
                teleportToPad(p, arena, inst.originPos, pad);
            }
            return;
        }
        // a Driftwreck rift shares this dimension; its own manager brings those players home
        boolean inRift = p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).contains("driftwrecks_rift_return");
        if (inArena(p) && inst == null && !inRift) returnHome(p);
        returnDeathDrops(p);
        String pendingKind = pendingRelics.remove(p.getUUID());
        if (pendingKind != null) {
            GuardianKind k = GuardianKind.byId(pendingKind);
            if (k != null) {
                ItemStack relic = ModItems.relic(k);
                if (!relic.isEmpty()) LoomTension.giveOrDrop(p, relic);
            }
            setDirty();
        }
    }
    /** Dying in the arena takes you out of the fight (respawn happens at home). */
    public void onDeath(ServerPlayer p) {
        ArenaInstance a = instanceOf(p); if (a == null) return;
        if (a.state == ArenaInstance.State.FIGHT && a.fallen.add(p.getUUID())) setDirty();
        for (ServerPlayer o : a.onlinePlayers()) if (o != p) o.sendSystemMessage(NinjacatText.teal(p.getName().getString() + " has fallen."));
        if (a.onlinePlayers().isEmpty()) wipe(p.server, a, "Nobody stands. The totem is spent.");
    }
    public void leave(ServerPlayer p) {
        ArenaInstance a = instanceOf(p); if (a == null) return;
        if (a.state == ArenaInstance.State.WON) {
            ItemStack relic = ModItems.relic(a.kind);
            if (!relic.isEmpty()) LoomTension.giveOrDrop(p, relic);
            a.winners.remove(p.getUUID());
            a.party.remove(p.getUUID());
            returnHome(p);
            setDirty();
            return;
        }
        a.party.remove(p.getUUID()); returnHome(p); setDirty();
        if (a.onlinePlayers().isEmpty()) wipe(p.server, a, "The Clowder withdrew. The totem is spent.");
    }

    // ------------------------------------------------------------------ saved data
    public ArenaManager() {}
    public static ArenaManager load(CompoundTag tag, HolderLookup.Provider regs) {
        ArenaManager m = new ArenaManager();
        for (Tag t : tag.getList("Active", Tag.TAG_COMPOUND)) { ArenaInstance a = ArenaInstance.load((CompoundTag) t); if (a != null) m.active.put(a.slot, a); }
        CompoundTag lk = tag.getCompound("LastKind"); for (String k : lk.getAllKeys()) m.lastKind.put(Integer.parseInt(k), lk.getString(k));
        CompoundTag pr = tag.getCompound("PendingRelics");
        for (String k : pr.getAllKeys()) {
            try { m.pendingRelics.put(UUID.fromString(k), pr.getString(k)); } catch (IllegalArgumentException ignored) {}
        }
        CompoundTag pl = tag.getCompound("Placed");
        for (String k : pl.getAllKeys()) {
            Set<Long> s = new HashSet<>(); for (long l : pl.getLongArray(k)) s.add(l);
            try { m.placed.put(Integer.parseInt(k), s); } catch (NumberFormatException ignored) {}
        }
        return m;
    }
    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider regs) {
        ListTag l = new ListTag(); for (ArenaInstance a : active.values()) l.add(a.save()); tag.put("Active", l);
        CompoundTag lk = new CompoundTag(); for (var e : lastKind.entrySet()) lk.putString(String.valueOf(e.getKey()), e.getValue()); tag.put("LastKind", lk);
        CompoundTag pr = new CompoundTag(); for (var e : pendingRelics.entrySet()) pr.putString(e.getKey().toString(), e.getValue()); tag.put("PendingRelics", pr);
        CompoundTag pl = new CompoundTag();
        for (var e : placed.entrySet()) pl.putLongArray(String.valueOf(e.getKey()), e.getValue().stream().mapToLong(Long::longValue).toArray());
        tag.put("Placed", pl);
        return tag;
    }
}
