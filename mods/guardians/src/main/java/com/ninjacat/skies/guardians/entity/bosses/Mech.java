package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.entity.GuardianEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderGetter;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;

/**
 * Plain-Java helpers shared by the thirteen fights: vanilla-mob minions tagged to their boss, ground probing,
 * particle lines and a {@link Ledger} that remembers arena blocks a mechanic swapped so they can be put back.
 * Nothing here is an entity or a registry object.
 */
final class Mech {
    private Mech() {}

    static final String TAG_PREFIX = "guardians_minion:";
    static final DustParticleOptions GOLD = new DustParticleOptions(new Vector3f(0.83F, 0.66F, 0.29F), 1.4F);
    static final DustParticleOptions TEAL = new DustParticleOptions(new Vector3f(0.24F, 0.48F, 0.48F), 1.4F);
    static final DustParticleOptions VIOLET = new DustParticleOptions(new Vector3f(0.54F, 0.37F, 0.72F), 1.4F);
    static final DustParticleOptions RED = new DustParticleOptions(new Vector3f(0.9F, 0.2F, 0.15F), 1.6F);

    static String tag(GuardianEntity boss) { return TAG_PREFIX + boss.getUUID(); }
    static ServerLevel level(GuardianEntity boss) { return (ServerLevel) boss.level(); }

    // ------------------------------------------------------------------ minions
    /** Spawn a vanilla mob as a boss helper: named, re-statted, tagged so {@link #discardMinions} can clean it up. */
    @Nullable
    static <T extends Mob> T spawn(GuardianEntity boss, EntityType<T> type, Vec3 at, String name, double hp, double dmg) {
        ServerLevel sl = level(boss);
        T m = type.create(sl);
        if (m == null) return null;
        m.moveTo(at.x, at.y, at.z, boss.getRandom().nextFloat() * 360F, 0);
        m.setCustomName(net.minecraft.network.chat.Component.literal(name));
        m.setCustomNameVisible(false);
        m.setPersistenceRequired();
        m.addTag(tag(boss));
        m.finalizeSpawn(sl, sl.getCurrentDifficultyAt(m.blockPosition()), MobSpawnType.MOB_SUMMONED, null);
        AttributeInstance h = m.getAttribute(Attributes.MAX_HEALTH); if (h != null && hp > 0) { h.setBaseValue(hp); m.setHealth((float) hp); }
        AttributeInstance a = m.getAttribute(Attributes.ATTACK_DAMAGE); if (a != null && dmg > 0) a.setBaseValue(dmg);
        AttributeInstance f = m.getAttribute(Attributes.FOLLOW_RANGE); if (f != null) f.setBaseValue(64);
        ServerPlayer t = boss.nearestParty(); if (t != null) m.setTarget(t);
        sl.addFreshEntity(m);
        return m;
    }
    static List<Entity> minions(GuardianEntity boss) { return minions(boss, e -> true); }
    static List<Entity> minions(GuardianEntity boss, Predicate<Entity> filter) {
        String tag = tag(boss); Vec3 o = boss.origin();
        AABB box = new AABB(o.x - 200, o.y - 80, o.z - 200, o.x + 200, o.y + 120, o.z + 200);
        return level(boss).getEntitiesOfClass(Entity.class, box, e -> e.isAlive() && e.getTags().contains(tag) && filter.test(e));
    }
    static int countMinions(GuardianEntity boss) { return minions(boss).size(); }
    static void discardMinions(GuardianEntity boss) { for (Entity e : minions(boss)) e.discard(); }

    // ------------------------------------------------------------------ geometry
    /** Top solid block with two air blocks above it in the column (x, z), scanning yHi → yLo. Null if none. */
    @Nullable
    static BlockPos ground(Level level, double x, double z, int yLo, int yHi) {
        BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
        int bx = (int) Math.floor(x), bz = (int) Math.floor(z);
        for (int y = yHi; y >= yLo; y--) {
            m.set(bx, y, bz);
            BlockState s = level.getBlockState(m);
            if (!s.isAir() && !s.liquid() && s.isSolidRender(level, m) && level.getBlockState(m.above()).isAir() && level.getBlockState(m.above(2)).isAir()) return m.immutable();
        }
        return null;
    }
    /** Standing position (feet) on top of {@link #ground}, or null. */
    @Nullable
    static Vec3 standOn(Level level, double x, double z, int yLo, int yHi) {
        BlockPos g = ground(level, x, z, yLo, yHi);
        return g == null ? null : new Vec3(Math.floor(x) + 0.5, g.getY() + 1, Math.floor(z) + 0.5);
    }
    static Vec3 polar(Vec3 c, double r, double angle, double y) { return new Vec3(c.x + Math.cos(angle) * r, y, c.z + Math.sin(angle) * r); }
    static double horiz(Vec3 a, Vec3 b) { double dx = a.x - b.x, dz = a.z - b.z; return Math.sqrt(dx * dx + dz * dz); }
    static double angleOf(Vec3 c, Vec3 p) { return Math.atan2(p.z - c.z, p.x - c.x); }

    // ------------------------------------------------------------------ fx
    static void line(ServerLevel sl, ParticleOptions p, Vec3 a, Vec3 b, int n) {
        for (int i = 0; i <= n; i++) { double t = (double) i / n; sl.sendParticles(p, a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t, 1, 0, 0, 0, 0); }
    }
    static void column(ServerLevel sl, ParticleOptions p, Vec3 base, double h, int n) { line(sl, p, base, base.add(0, h, 0), n); }
    static void burst(ServerLevel sl, ParticleOptions p, Vec3 at, int n, double spread) { sl.sendParticles(p, at.x, at.y, at.z, n, spread, spread * 0.5, spread, 0.02); }
    /** A visual-only lightning strike (no fire, no damage) — used for gear arcs and ward flashes. */
    static void arc(ServerLevel sl, Vec3 at) {
        LightningBolt b = EntityType.LIGHTNING_BOLT.create(sl);
        if (b == null) return;
        b.moveTo(at); b.setVisualOnly(true); sl.addFreshEntity(b);
    }
    static void soundAt(ServerLevel sl, Vec3 at, net.minecraft.sounds.SoundEvent s, float vol, float pitch) { sl.playSound(null, at.x, at.y, at.z, s, SoundSource.HOSTILE, vol, pitch); }
    static void thud(ServerLevel sl, Vec3 at) { soundAt(sl, at, SoundEvents.GENERIC_EXPLODE.value(), 1.2F, 0.7F); sl.sendParticles(ParticleTypes.EXPLOSION, at.x, at.y + 0.5, at.z, 1, 0, 0, 0, 0); }

    // ------------------------------------------------------------------ players
    static boolean standingOn(ServerPlayer p, BlockPos pos) { return p.getOnPos().equals(pos) || p.blockPosition().below().equals(pos); }
    @Nullable
    static ServerPlayer randomPlayer(GuardianEntity boss) {
        List<ServerPlayer> ps = new ArrayList<>(); for (ServerPlayer p : boss.party()) if (p.isAlive()) ps.add(p);
        return ps.isEmpty() ? null : ps.get(boss.getRandom().nextInt(ps.size()));
    }

    // ------------------------------------------------------------------ block ledger
    /** Remembers the original state of every arena block a mechanic overwrote so it can be restored (in batches). */
    static final class Ledger {
        private final Map<BlockPos, BlockState> saved = new LinkedHashMap<>();
        int size() { return saved.size(); }
        boolean has(BlockPos p) { return saved.containsKey(p); }
        /** Overwrite pos with state, remembering the first original. */
        void set(Level level, BlockPos pos, BlockState state) {
            if (!level.isLoaded(pos)) return;
            saved.putIfAbsent(pos.immutable(), level.getBlockState(pos));
            level.setBlock(pos, state, 3);
        }
        void clear(Level level, BlockPos pos) { set(level, pos, Blocks.AIR.defaultBlockState()); }
        /** Stop tracking a position (the mechanic put it back itself). */
        void forget(BlockPos pos) { saved.remove(pos); }
        /** Put back up to n blocks; returns how many remain. */
        int restore(Level level, int n) {
            var it = saved.entrySet().iterator();
            while (it.hasNext() && n-- > 0) { var e = it.next(); if (level.isLoaded(e.getKey())) level.setBlock(e.getKey(), e.getValue(), 3); it.remove(); }
            return saved.size();
        }
        void restoreAll(Level level) { restore(level, Integer.MAX_VALUE); }
        Iterable<BlockPos> positions() { return saved.keySet(); }
        void save(CompoundTag tag, String key) {
            ListTag list = new ListTag();
            for (var e : saved.entrySet()) {
                CompoundTag t = new CompoundTag();
                t.putInt("x", e.getKey().getX()); t.putInt("y", e.getKey().getY()); t.putInt("z", e.getKey().getZ());
                t.put("s", NbtUtils.writeBlockState(e.getValue()));
                list.add(t);
            }
            tag.put(key, list);
        }
        void load(CompoundTag tag, String key, Level level) {
            saved.clear();
            if (level == null || !tag.contains(key)) return;
            HolderGetter<net.minecraft.world.level.block.Block> lookup = level.holderLookup(Registries.BLOCK);
            for (Tag raw : tag.getList(key, Tag.TAG_COMPOUND)) {
                CompoundTag t = (CompoundTag) raw;
                BlockPos p = new BlockPos(t.getInt("x"), t.getInt("y"), t.getInt("z"));
                saved.put(p, NbtUtils.readBlockState(lookup, t.getCompound("s")));
            }
        }
    }
}
