package com.ninjacat.skies.driftwrecks.wreck;

import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.lib.plan.BuildQueue;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.LongTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.world.phys.AABB;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/**
 * One active Driftwreck: what was rolled, where it sits, how long it has held, and every block it placed so the
 * unravel can take back exactly those (and nothing a player built).
 */
public final class Wreck {
    public enum Phase { BUILDING, ACTIVE, UNRAVELING, DONE }

    public final int id;
    public final UUID team;
    public final String planId;
    public final WreckCore core;       // null for the Heartwreck
    public final WreckTier tier;
    public final Strand skin;
    public final WreckModifier modifier;
    public final WreckObjective objective;
    public final boolean heartwreck;
    public final BlockPos origin;
    public final boolean hiddenRoom;

    public Phase phase = Phase.BUILDING;
    public int age;                 // online ticks lived (after building)
    public int lifetime;            // online ticks it may hold
    public int warned;              // highest warning sent: 0, 50, 80, 95
    public boolean objectiveDone;
    /** Finished while no owner was online: paid out once one is. */
    public boolean pendingComplete;
    public boolean announced;
    public int minX, minY, minZ, maxX, maxY, maxZ;

    /** Build queue while building; afterwards the same ops, kept for the template-only removal. */
    public BuildQueue placed;
    @Nullable public BuildQueue removal;
    public int crumbleCursor;       // index into the placed ops, from the rim inward
    public final List<BlockPos> tether = new ArrayList<>();
    @Nullable public BlockPos tetherStart;
    public final Set<UUID> mobs = new LinkedHashSet<>();
    public final Set<UUID> visitors = new LinkedHashSet<>();

    // objective state
    public int[] pillarOrder = new int[0];
    public int pillarStep;
    public int spawnersLeft;
    @Nullable public UUID echo;
    public int holdWave;            // 0 not started, 1..3 running, 4 held
    public int holdTicks;
    public boolean riftOpened;
    public long lastPenalty;        // game time of the last mob a wrong pillar cost (transient)

    public Wreck(int id, UUID team, String planId, @Nullable WreckCore core, WreckTier tier, Strand skin, WreckModifier modifier,
                 WreckObjective objective, boolean heartwreck, BlockPos origin, boolean hiddenRoom) {
        this.id = id; this.team = team; this.planId = planId; this.core = core; this.tier = tier; this.skin = skin;
        this.modifier = modifier; this.objective = objective; this.heartwreck = heartwreck; this.origin = origin; this.hiddenRoom = hiddenRoom;
    }

    public AABB box() { return new AABB(minX, minY, minZ, maxX + 1, maxY + 1, maxZ + 1); }
    public BlockPos center() { return new BlockPos((minX + maxX) / 2, origin.getY() + 1, (minZ + maxZ) / 2); }
    public float lifeFraction() { return lifetime <= 0 ? 0 : Math.min(1F, (float) age / lifetime); }
    public boolean contains(BlockPos p, int margin) {
        return p.getX() >= minX - margin && p.getX() <= maxX + margin && p.getZ() >= minZ - margin && p.getZ() <= maxZ + margin
                && p.getY() >= minY - margin && p.getY() <= maxY + margin;
    }

    /** Horizontal distance from a point to the wreck's box or any tether block. */
    public double reach(double x, double z) {
        double dx = Math.max(0, Math.max(minX - x, x - (maxX + 1)));
        double dz = Math.max(0, Math.max(minZ - z, z - (maxZ + 1)));
        double best = Math.sqrt(dx * dx + dz * dz);
        for (int i = 0; i < tether.size(); i += 4) {
            BlockPos t = tether.get(i);
            best = Math.min(best, Math.hypot(t.getX() + 0.5 - x, t.getZ() + 0.5 - z));
        }
        return best;
    }

    // ------------------------------------------------------------------ persistence
    public CompoundTag save() {
        CompoundTag t = new CompoundTag();
        t.putInt("id", id); t.putUUID("team", team); t.putString("plan", planId);
        if (core != null) t.putString("core", core.id);
        t.putString("tier", tier.id); t.putString("skin", skin.id()); t.putString("modifier", modifier.id);
        t.putString("objective", objective.id); t.putBoolean("heart", heartwreck); t.put("origin", NbtUtils.writeBlockPos(origin));
        t.putBoolean("hidden", hiddenRoom);
        t.putString("phase", phase.name()); t.putInt("age", age); t.putInt("lifetime", lifetime); t.putInt("warned", warned);
        t.putBoolean("done", objectiveDone); t.putBoolean("pending", pendingComplete); t.putBoolean("announced", announced);
        t.putIntArray("box", new int[]{minX, minY, minZ, maxX, maxY, maxZ});
        if (placed != null) t.put("placed", placed.save());
        if (removal != null) t.put("removal", removal.save());
        t.putInt("crumble", crumbleCursor);
        ListTag tl = new ListTag(); for (BlockPos p : tether) tl.add(LongTag.valueOf(p.asLong())); t.put("tether", tl);
        if (tetherStart != null) t.putLong("tetherStart", tetherStart.asLong());
        ListTag ml = new ListTag(); for (UUID u : mobs) ml.add(NbtUtils.createUUID(u)); t.put("mobs", ml);
        ListTag vl = new ListTag(); for (UUID u : visitors) vl.add(NbtUtils.createUUID(u)); t.put("visitors", vl);
        t.putIntArray("pillars", pillarOrder); t.putInt("pillarStep", pillarStep); t.putInt("spawners", spawnersLeft);
        if (echo != null) t.putUUID("echo", echo);
        t.putInt("holdWave", holdWave); t.putInt("holdTicks", holdTicks); t.putBoolean("rift", riftOpened);
        return t;
    }

    @Nullable
    public static Wreck load(CompoundTag t, HolderLookup.Provider regs) {
        WreckTier tier = WreckTier.byId(t.getString("tier"));
        Strand skin = Strand.byId(t.getString("skin"));
        WreckModifier mod = WreckModifier.byId(t.getString("modifier"));
        WreckObjective obj = WreckObjective.byId(t.getString("objective"));
        if (tier == null || skin == null || mod == null || obj == null || !t.hasUUID("team")) return null;
        BlockPos origin = NbtUtils.readBlockPos(t, "origin").orElse(BlockPos.ZERO);
        Wreck w = new Wreck(t.getInt("id"), t.getUUID("team"), t.getString("plan"), WreckCore.byId(t.getString("core")), tier, skin, mod, obj,
                t.getBoolean("heart"), origin, t.getBoolean("hidden"));
        try { w.phase = Phase.valueOf(t.getString("phase")); } catch (IllegalArgumentException e) { w.phase = Phase.ACTIVE; }
        w.age = t.getInt("age"); w.lifetime = t.getInt("lifetime"); w.warned = t.getInt("warned");
        w.objectiveDone = t.getBoolean("done"); w.pendingComplete = t.getBoolean("pending"); w.announced = t.getBoolean("announced");
        int[] b = t.getIntArray("box");
        if (b.length == 6) { w.minX = b[0]; w.minY = b[1]; w.minZ = b[2]; w.maxX = b[3]; w.maxY = b[4]; w.maxZ = b[5]; }
        if (t.contains("placed")) w.placed = BuildQueue.load(t.getCompound("placed"), regs);
        if (t.contains("removal")) w.removal = BuildQueue.load(t.getCompound("removal"), regs);
        w.crumbleCursor = t.getInt("crumble");
        for (Tag x : t.getList("tether", Tag.TAG_LONG)) w.tether.add(BlockPos.of(((LongTag) x).getAsLong()));
        if (t.contains("tetherStart")) w.tetherStart = BlockPos.of(t.getLong("tetherStart"));
        for (Tag x : t.getList("mobs", Tag.TAG_INT_ARRAY)) w.mobs.add(NbtUtils.loadUUID(x));
        for (Tag x : t.getList("visitors", Tag.TAG_INT_ARRAY)) w.visitors.add(NbtUtils.loadUUID(x));
        w.pillarOrder = t.getIntArray("pillars"); w.pillarStep = t.getInt("pillarStep"); w.spawnersLeft = t.getInt("spawners");
        if (t.hasUUID("echo")) w.echo = t.getUUID("echo");
        w.holdWave = t.getInt("holdWave"); w.holdTicks = t.getInt("holdTicks"); w.riftOpened = t.getBoolean("rift");
        return w;
    }
}
