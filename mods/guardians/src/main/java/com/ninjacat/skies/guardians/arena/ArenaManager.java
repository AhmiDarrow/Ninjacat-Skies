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
    private static final int SLOT_SPACING = 4096, FLOOR_Y = 120, FENCE_MARGIN = 6, RETURN_DELAY = 120;
    private static final String PERSIST_ROOT = Guardians.MOD_ID, RETURN_TAG = "arena_return";

    private final Map<Integer, ArenaInstance> active = new TreeMap<>();
    private final Map<Integer, String> lastKind = new HashMap<>();      // slot -> plan to clear before reuse

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
        if (inArena(summoner)) return "You are already answering for the Cut.";
        if (instanceOf(summoner) != null) return "Your Clowder is already in an arena.";
        ServerLevel arena = arenaLevel(server);
        if (arena == null) return "The arena is not woven into this world (dimension missing).";
        Optional<Clowder> clowder = LoomTension.clowderOf(summoner);
        if (kind.tier == GuardianKind.Tier.INSANE && (clowder.isEmpty() || !LoomTension.isRewoven(clowder.get())))
            return "That door only opens after the Reweave.";
        if (kind.strand != null && (clowder.isEmpty() || !LoomTension.isSeated(clowder.get(), kind.strand)))
            return "Seat the " + kind.strand.title() + " Strand at your Tension Post first — " + kind.title + " only answers for a Strand that is held.";
        // the party: Clowder members online and within 32 blocks of the summoner (they hear the totem)
        List<ServerPlayer> party = new ArrayList<>(); party.add(summoner);
        clowder.ifPresent(c -> { for (ServerPlayer m : c.onlineMembers()) if (m != summoner && m.level() == summoner.level() && m.distanceTo(summoner) < 32 && !m.isSpectator()) party.add(m); });
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
        if (p.level().dimension().equals(ARENA_LEVEL)) return true;
        return TEST_FALLBACK && p.getX() > TEST_OFFSET - 4096;
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
    private static void teleportToPad(ServerPlayer p, ServerLevel arena, BlockPos origin, BlockPos pad) {
        double x = origin.getX() + pad.getX() + 0.5, y = origin.getY() + pad.getY() + 0.1, z = origin.getZ() + pad.getZ() + 0.5;
        float yaw = (float) Math.toDegrees(Math.atan2(-(origin.getX() + 0.5 - x), origin.getZ() + 0.5 - z));
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
        if (p instanceof net.neoforged.neoforge.common.util.FakePlayer) p.moveTo(at.x, at.y, at.z, yaw, pitch);
        else p.teleportTo(target, at.x, at.y, at.z, yaw, pitch);
        p.setDeltaMovement(Vec3.ZERO); p.fallDistance = 0;
    }

    // ------------------------------------------------------------------ ticking
    public void tick(MinecraftServer server) {
        if (active.isEmpty()) return;
        ServerLevel arena = arenaLevel(server); if (arena == null) return;
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
                    p.teleportTo(arena, inst.originPos.getX() + pad.getX() + 0.5, inst.originPos.getY() + pad.getY() + 0.1, inst.originPos.getZ() + pad.getZ() + 0.5, p.getYRot(), p.getXRot());
                    p.setDeltaMovement(Vec3.ZERO); p.fallDistance = 0;
                    float dmg = inst.kind == GuardianKind.EDGEWALKER || inst.kind.tier == GuardianKind.Tier.INSANE ? 12 : 6;
                    p.hurt(p.damageSources().fellOutOfWorld(), dmg);
                    p.displayClientMessage(NinjacatText.teal("The Loom pulls you back onto the stage."), true);
                }
            }
            switch (inst.state) {
                case FIGHT -> {
                    if (inside.isEmpty() && inst.age > 100) { wipe(server, inst, "Nobody stands. The totem is spent."); }
                    else if (inst.boss != null && inst.age > 100 && arena.getEntity(inst.boss) == null && inst.age % 20 == 0) {
                        // boss vanished (killed by /kill or unloaded) — count it as a win only if it actually died via die()
                        wipe(server, inst, "The guardian slipped the weave. The totem is spent.");
                    }
                }
                case WON -> { if (inst.stateTicks > RETURN_DELAY + 60) { sendEveryoneHome(server, inst); done.add(inst.slot); } }
                case WIPED -> { if (inst.stateTicks > RETURN_DELAY) { sendEveryoneHome(server, inst); done.add(inst.slot); } }
            }
        }
        for (int slot : done) { ArenaInstance i = active.remove(slot); if (i != null) forceChunks(arena, i.originPos, i.radius + 16, false); }
        if (!done.isEmpty()) setDirty();
    }

    private void sendEveryoneHome(MinecraftServer server, ArenaInstance inst) {
        for (UUID id : inst.party) {
            ServerPlayer p = server.getPlayerList().getPlayer(id);
            if (p != null && inArena(p)) returnHome(p);
        }
        ServerLevel arena = arenaLevel(server);
        if (arena != null && inst.boss != null) { Entity e = arena.getEntity(inst.boss); if (e instanceof GuardianEntity g) { g.revertTempBlocks(); g.discard(); } }
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
        List<ServerPlayer> present = inst.onlinePlayers();
        for (ServerPlayer p : present) {
            ItemStack relic = ModItems.relic(inst.kind);
            if (!relic.isEmpty()) LoomTension.giveOrDrop(p, relic);
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

    /** A player who logs in inside the arena dimension with no running fight is sent home. */
    public void onLogin(ServerPlayer p) {
        if (inArena(p) && instanceOf(p) == null) returnHome(p);
    }
    /** Dying in the arena takes you out of the fight (respawn happens at home). */
    public void onDeath(ServerPlayer p) {
        ArenaInstance a = instanceOf(p); if (a == null) return;
        for (ServerPlayer o : a.onlinePlayers()) if (o != p) o.sendSystemMessage(NinjacatText.teal(p.getName().getString() + " has fallen."));
    }
    public void leave(ServerPlayer p) {
        ArenaInstance a = instanceOf(p); if (a == null) return;
        a.party.remove(p.getUUID()); returnHome(p); setDirty();
        if (a.onlinePlayers().isEmpty()) wipe(p.server, a, "The Clowder withdrew. The totem is spent.");
    }

    // ------------------------------------------------------------------ saved data
    public ArenaManager() {}
    public static ArenaManager load(CompoundTag tag, HolderLookup.Provider regs) {
        ArenaManager m = new ArenaManager();
        for (Tag t : tag.getList("Active", Tag.TAG_COMPOUND)) { ArenaInstance a = ArenaInstance.load((CompoundTag) t); if (a != null) m.active.put(a.slot, a); }
        CompoundTag lk = tag.getCompound("LastKind"); for (String k : lk.getAllKeys()) m.lastKind.put(Integer.parseInt(k), lk.getString(k));
        return m;
    }
    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider regs) {
        ListTag l = new ListTag(); for (ArenaInstance a : active.values()) l.add(a.save()); tag.put("Active", l);
        CompoundTag lk = new CompoundTag(); for (var e : lastKind.entrySet()) lk.putString(String.valueOf(e.getKey()), e.getValue()); tag.put("LastKind", lk);
        return tag;
    }
}
