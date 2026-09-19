package com.ninjacat.skies.driftwrecks.rift;

import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.Driftwrecks;
import com.ninjacat.skies.driftwrecks.entity.RemnantEntity;
import com.ninjacat.skies.driftwrecks.item.DriftlureItem;
import com.ninjacat.skies.driftwrecks.registry.DwItems;
import com.ninjacat.skies.driftwrecks.registry.DwRegistries;
import com.ninjacat.skies.driftwrecks.wreck.DriftManager;
import com.ninjacat.skies.driftwrecks.wreck.StrandSkin;
import com.ninjacat.skies.driftwrecks.wreck.TeamDrift;
import com.ninjacat.skies.driftwrecks.wreck.Wreck;
import com.ninjacat.skies.driftwrecks.wreck.WreckCore;
import com.ninjacat.skies.driftwrecks.wreck.WreckRewards;
import com.ninjacat.skies.driftwrecks.wreck.WreckTier;
import com.ninjacat.skies.guardians.arena.ArenaManager;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.*;

/**
 * Sealed rifts: a Weft Key opens a Tier 3 wreck's tear and pulls the Clowder members within 8 blocks into a small
 * chamber in the Guardians' arena dimension. Slots use the same 4096 grid on the negative X side, so they never meet a
 * guardian arena. Win: a guaranteed Keepsake of the Strand, a rare roll, the Remnant stamp. Lose: back to the wreck.
 */
public final class RiftManager extends SavedData {
    public static final int SPACING = 4096, FLOOR_Y = 120, RADIUS = 12, PULL = 8, END_DELAY = 80;
    private static final String RETURN = "driftwrecks_rift_return";

    public static final class Rift {
        int slot, wreck, ticks, emptyTicks;
        UUID team;
        Strand strand;
        BlockPos origin;
        final List<UUID> party = new ArrayList<>();
        @Nullable UUID remnant;
        int state;   // 0 fight, 1 won, 2 lost

        CompoundTag save() {
            CompoundTag t = new CompoundTag();
            t.putInt("slot", slot); t.putInt("wreck", wreck); t.putInt("ticks", ticks); t.putInt("state", state);
            t.putUUID("team", team); t.putString("strand", strand.id()); t.put("origin", NbtUtils.writeBlockPos(origin));
            ListTag l = new ListTag(); for (UUID u : party) l.add(NbtUtils.createUUID(u)); t.put("party", l);
            if (remnant != null) t.putUUID("remnant", remnant);
            return t;
        }

        static Rift load(CompoundTag t) {
            Rift r = new Rift();
            r.slot = t.getInt("slot"); r.wreck = t.getInt("wreck"); r.ticks = t.getInt("ticks"); r.state = t.getInt("state");
            r.team = t.getUUID("team"); r.strand = Optional.ofNullable(Strand.byId(t.getString("strand"))).orElse(Strand.SOIL);
            r.origin = NbtUtils.readBlockPos(t, "origin").orElse(BlockPos.ZERO);
            for (Tag x : t.getList("party", Tag.TAG_INT_ARRAY)) r.party.add(NbtUtils.loadUUID(x));
            if (t.hasUUID("remnant")) r.remnant = t.getUUID("remnant");
            return r;
        }
    }

    private final Map<Integer, Rift> rifts = new TreeMap<>();
    private boolean ticketsRestored;

    public static RiftManager get(MinecraftServer server) {
        return server.overworld().getDataStorage().computeIfAbsent(new Factory<>(RiftManager::new, RiftManager::load), "driftwrecks_rifts");
    }

    public Collection<Rift> rifts() { return rifts.values(); }

    // ------------------------------------------------------------------ opening

    public static void open(ServerLevel level, BlockPos tear, ServerPlayer opener, ItemStack key) {
        MinecraftServer server = level.getServer();
        DriftManager dm = DriftManager.get(server);
        Wreck w = dm.at(tear, 0);
        if (w == null || w.phase != Wreck.Phase.ACTIVE || w.tier != WreckTier.HOLD) { opener.displayClientMessage(NinjacatText.teal("The tear does not answer."), true); return; }
        if (w.riftOpened) { opener.displayClientMessage(NinjacatText.teal("This rift has already been walked."), true); return; }
        Strand ks = DriftlureItem.strandOf(key);
        if (ks != w.skin) { opener.displayClientMessage(NinjacatText.teal("The key is cut for another Strand. This rift wants " + w.skin.title() + "."), true); return; }
        ServerLevel arena = ArenaManager.arenaLevel(server);
        if (arena == null) { opener.displayClientMessage(NinjacatText.teal("The rift has nowhere to open (arena dimension missing)."), true); return; }
        RiftManager rm = get(server);
        Rift r = new Rift();
        int slot = 0; while (rm.rifts.containsKey(slot)) slot++;
        r.slot = slot; r.wreck = w.id; r.team = w.team; r.strand = w.skin;
        boolean fallback = arena == server.overworld();
        r.origin = new BlockPos(-(slot + 1) * SPACING, FLOOR_Y, fallback ? -200000 : 0);
        forceChunks(arena, r.origin, true);
        build(arena, r.origin, r.strand);

        List<ServerPlayer> party = new ArrayList<>();
        Optional<Clowder> c = LoomTension.clowderById(server, w.team);
        if (c.isPresent()) for (ServerPlayer m : c.get().onlineMembers())
            if (!m.isSpectator() && m.level() == level && m.blockPosition().closerThan(tear, PULL)) party.add(m);
        if (!party.contains(opener)) party.add(opener);
        for (int i = 0; i < party.size(); i++) {
            ServerPlayer p = party.get(i);
            r.party.add(p.getUUID());
            storeReturn(p);
            double a = Math.PI * 2 * i / party.size();
            teleport(p, arena, r.origin.getX() + 0.5 + Math.cos(a) * 9, r.origin.getY(), r.origin.getZ() + 0.5 + Math.sin(a) * 9);
            p.sendSystemMessage(NinjacatText.teal("The rift folds shut behind you. Something small and frayed wears the shape of a Guardian."));
            WreckRewards.award(p, "rift");
        }
        RemnantEntity rem = DwRegistries.REMNANT.get().create(arena);
        if (rem != null) {
            rem.moveTo(r.origin.getX() + 0.5, r.origin.getY(), r.origin.getZ() + 0.5, 180, 0);
            rem.finalizeSpawn(arena, arena.getCurrentDifficultyAt(r.origin), MobSpawnType.EVENT, null);
            rem.setup(r.strand, slot, r.origin, party.size());
            arena.addFreshEntity(rem);
            r.remnant = rem.getUUID();
        }
        if (!opener.getAbilities().instabuild) key.shrink(1);
        w.riftOpened = true;
        dm.markDirty();
        rm.rifts.put(slot, r);
        rm.setDirty();
        level.playSound(null, tear, DwRegistries.sound("rift.open"), SoundSource.AMBIENT, 2.0F, 1.0F);
        arena.playSound(null, r.origin, DwRegistries.sound("rift.open"), SoundSource.AMBIENT, 2.0F, 0.8F);
    }

    /** The chamber: a round floor of the Strand's skin on a keel, a low rim, a teal seam round the top. */
    static void build(ServerLevel level, BlockPos o, Strand s) {
        clear(level, o);
        BlockState floor = StrandSkin.resolve(s, "floor"), wall = StrandSkin.resolve(s, "wall"), keel = StrandSkin.resolve(s, "keel"), trim = StrandSkin.resolve(s, "trim");
        for (int x = -RADIUS; x <= RADIUS; x++) for (int z = -RADIUS; z <= RADIUS; z++) {
            double d = Math.sqrt(x * x + z * z);
            if (d > RADIUS + 0.5) continue;
            BlockPos p = o.offset(x, -1, z);
            level.setBlock(p, d > RADIUS - 0.5 ? trim : floor, 2);
            level.setBlock(p.below(), keel, 2);
            if (d > RADIUS - 2.5) level.setBlock(p.below(2), keel, 2);
            if (d > RADIUS - 0.5) {
                for (int y = 0; y < 3; y++) level.setBlock(p.above(1 + y), wall, 2);
                level.setBlock(p.above(4), (x + z) % 3 == 0 ? StrandSkin.seam2() : StrandSkin.seam(), 2);
            }
        }
        for (int i = 0; i < 6; i++) {
            double a = Math.PI / 3 * i;
            BlockPos l = o.offset((int) Math.round(Math.cos(a) * (RADIUS - 2)), 0, (int) Math.round(Math.sin(a) * (RADIUS - 2)));
            level.setBlock(l, Blocks.LANTERN.defaultBlockState(), 2);
        }
    }

    static void clear(ServerLevel level, BlockPos o) {
        for (BlockPos p : BlockPos.betweenClosed(o.offset(-RADIUS - 1, -4, -RADIUS - 1), o.offset(RADIUS + 1, 8, RADIUS + 1)))
            if (!level.getBlockState(p).isAir()) level.setBlock(p, Blocks.AIR.defaultBlockState(), 2 | 16);
        AABB box = new AABB(o).inflate(RADIUS + 8, 16, RADIUS + 8);
        for (Entity e : level.getEntities((Entity) null, box, e -> !(e instanceof Player))) e.discard();
    }

    private static void forceChunks(ServerLevel level, BlockPos o, boolean on) {
        ChunkPos c = new ChunkPos(o);
        for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) level.setChunkForced(c.x + dx, c.z + dz, on);
    }

    // ------------------------------------------------------------------ ticking

    public void tick(MinecraftServer server) {
        if (rifts.isEmpty()) return;
        ServerLevel arena = ArenaManager.arenaLevel(server);
        if (arena == null) return;
        if (!ticketsRestored) { ticketsRestored = true; for (Rift r : rifts.values()) forceChunks(arena, r.origin, true); }
        List<Integer> done = new ArrayList<>();
        for (Rift r : rifts.values()) {
            r.ticks++;
            List<ServerPlayer> inside = new ArrayList<>();
            for (UUID u : r.party) {
                ServerPlayer p = server.getPlayerList().getPlayer(u);
                if (p == null || p.isSpectator() || !p.isAlive()) continue;
                if (p.level() != arena) continue;
                double dx = p.getX() - r.origin.getX() - 0.5, dz = p.getZ() - r.origin.getZ() - 0.5;
                if (Math.abs(dx) > SPACING / 4.0 || Math.abs(dz) > SPACING / 4.0) continue;
                inside.add(p);
                if (Math.sqrt(dx * dx + dz * dz) > RADIUS + 3 || p.getY() < r.origin.getY() - 8) {
                    teleport(p, arena, r.origin.getX() + 0.5 + 6, r.origin.getY(), r.origin.getZ() + 0.5);
                    p.hurt(p.damageSources().fellOutOfWorld(), Math.min(6F, Math.max(0, p.getHealth() - 1)));
                    p.displayClientMessage(NinjacatText.teal("The rift folds you back in."), true);
                }
            }
            if (r.state == 0) {
                if (inside.isEmpty() && r.ticks > 100) { if (++r.emptyTicks > 100) lose(server, r); }
                else r.emptyTicks = 0;
            } else if (r.ticks > END_DELAY) {
                for (UUID u : r.party) { ServerPlayer p = server.getPlayerList().getPlayer(u); if (p != null) returnHome(p); }
                clear(arena, r.origin);
                forceChunks(arena, r.origin, false);
                done.add(r.slot);
            }
        }
        for (int s : done) rifts.remove(s);
        if (!done.isEmpty()) setDirty();
    }

    private void lose(MinecraftServer server, Rift r) {
        r.state = 2; r.ticks = 0; setDirty();
        for (UUID u : r.party) { ServerPlayer p = server.getPlayerList().getPlayer(u); if (p != null) p.sendSystemMessage(NinjacatText.teal("The rift lets go of you. The Remnant stays frayed.")); }
        ServerLevel arena = ArenaManager.arenaLevel(server);
        if (arena != null && r.remnant != null) { Entity e = arena.getEntity(r.remnant); if (e != null) e.discard(); }
    }

    public static void onRemnantDeath(ServerLevel level, int slot) {
        MinecraftServer server = level.getServer();
        RiftManager rm = get(server);
        Rift r = rm.rifts.get(slot);
        if (r == null || r.state != 0) return;
        r.state = 1; r.ticks = 0; rm.setDirty();
        Optional<Clowder> c = LoomTension.clowderById(server, r.team);
        TeamDrift team = c.map(TeamDrift::of).orElse(null);
        boolean stamp = team != null && team.stampRemnant(r.strand);
        for (UUID u : r.party) {
            ServerPlayer p = server.getPlayerList().getPlayer(u);
            if (p == null) continue;
            // a guaranteed Keepsake of this Strand: one the Clowder lacks, else any
            if (team != null) {
                List<WreckCore> missing = new ArrayList<>();
                for (WreckCore core : WreckCore.ALL) if (!team.hasKeepsake(r.strand, core)) missing.add(core);
                WreckCore core = missing.isEmpty() ? WreckCore.ALL[level.random.nextInt(WreckCore.ALL.length)] : missing.get(level.random.nextInt(missing.size()));
                WreckRewards.giveKeepsake(team, r.strand, core, p);
            }
            for (ItemStack s : rareRoll(level, p)) LoomTension.giveOrDrop(p, s);
            LoomTension.giveOrDrop(p, new ItemStack(DwItems.RIFT_SHARD.get()));
            p.sendSystemMessage(NinjacatText.gold("The Remnant comes apart into clean thread. The " + r.strand.tribe() + " would have called that mending."));
            WreckRewards.award(p, "remnant");
        }
        if (team != null) {
            if (stamp && team.allRemnantStamps()) c.get().onlineMembers().forEach(p -> {
                WreckRewards.award(p, "remnants");
                p.sendSystemMessage(NinjacatText.gold("Every Remnant mended. Weft Keys cost you half now."));
            });
            team.dirty();
            WreckRewards.syncAll(c.get());
        }
    }

    private static List<ItemStack> rareRoll(ServerLevel level, ServerPlayer p) {
        SimpleContainer box = new SimpleContainer(27);
        var table = level.getServer().reloadableRegistries().getLootTable(ResourceKey.create(Registries.LOOT_TABLE, ResourceLocation.fromNamespaceAndPath(Driftwrecks.MOD_ID, "chests/rift")));
        table.fill(box, new LootParams.Builder(level).withParameter(LootContextParams.ORIGIN, p.position()).withLuck(p.getLuck()).create(LootContextParamSets.CHEST), level.random.nextLong());
        List<ItemStack> out = new ArrayList<>();
        for (int i = 0; i < 27; i++) if (!box.getItem(i).isEmpty()) out.add(box.getItem(i));
        return out;
    }

    // ------------------------------------------------------------------ return points

    private static void storeReturn(ServerPlayer p) {
        CompoundTag persisted = p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        CompoundTag ret = new CompoundTag();
        ret.putString("dim", p.level().dimension().location().toString());
        ret.putDouble("x", p.getX()); ret.putDouble("y", p.getY()); ret.putDouble("z", p.getZ());
        persisted.put(RETURN, ret);
        p.getPersistentData().put(Player.PERSISTED_NBT_TAG, persisted);
    }

    /** Back to where the player stood when the rift opened (the wreck), or their Tension Post if it has gone. */
    public static void returnHome(ServerPlayer p) {
        CompoundTag persisted = p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        CompoundTag ret = persisted.getCompound(RETURN);
        persisted.remove(RETURN);
        p.getPersistentData().put(Player.PERSISTED_NBT_TAG, persisted);
        ServerLevel target = p.server.overworld();
        Vec3 at = null;
        if (!ret.isEmpty()) {
            ResourceLocation dim = ResourceLocation.tryParse(ret.getString("dim"));
            ServerLevel l = dim == null ? null : p.server.getLevel(ResourceKey.create(Registries.DIMENSION, dim));
            if (l != null) { target = l; at = new Vec3(ret.getDouble("x"), ret.getDouble("y"), ret.getDouble("z")); }
        }
        if (at == null || !target.getBlockState(BlockPos.containing(at).below()).isSolid()) {
            BlockPos home = LoomTension.clowderOf(p).map(LoomTension::postOf).filter(g -> g.dimension().equals(Level.OVERWORLD)).map(g -> g.pos().above()).orElse(target.getSharedSpawnPos());
            target = p.server.overworld();
            at = Vec3.atBottomCenterOf(home);
        }
        teleport(p, target, at.x, at.y, at.z);
    }

    public static boolean hasReturn(ServerPlayer p) { return p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).contains(RETURN); }

    /** Log in inside a finished rift (or with a stale return point): go home. */
    public void onLogin(ServerPlayer p) {
        if (!hasReturn(p)) return;
        for (Rift r : rifts.values()) if (r.party.contains(p.getUUID()) && r.state == 0) return;
        returnHome(p);
    }

    private static void teleport(ServerPlayer p, ServerLevel level, double x, double y, double z) {
        if (p.isPassenger()) p.stopRiding();
        if (p instanceof net.neoforged.neoforge.common.util.FakePlayer) p.moveTo(x, y, z, p.getYRot(), 0);
        else p.teleportTo(level, x, y, z, p.getYRot(), 0);
        p.setDeltaMovement(Vec3.ZERO);
        p.fallDistance = 0;
    }

    // ------------------------------------------------------------------ saved data

    public RiftManager() {}

    public static RiftManager load(CompoundTag tag, HolderLookup.Provider regs) {
        RiftManager m = new RiftManager();
        for (Tag t : tag.getList("rifts", Tag.TAG_COMPOUND)) { Rift r = Rift.load((CompoundTag) t); m.rifts.put(r.slot, r); }
        return m;
    }

    @Override
    public CompoundTag save(CompoundTag tag, HolderLookup.Provider regs) {
        ListTag l = new ListTag();
        for (Rift r : rifts.values()) l.add(r.save());
        tag.put("rifts", l);
        return tag;
    }
}
