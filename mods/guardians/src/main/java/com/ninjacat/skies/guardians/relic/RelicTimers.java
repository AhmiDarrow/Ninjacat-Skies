package com.ninjacat.skies.guardians.relic;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import com.ninjacat.skies.guardians.item.RelicItem;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Bee;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SweetBerryBushBlock;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.event.server.ServerStoppingEvent;
import net.neoforged.neoforge.event.entity.player.AttackEntityEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

import javax.annotation.Nullable;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.WeakHashMap;

/**
 * Server-side timers and the few static hooks the relics need outside the per-wearer {@link RelicPower} callbacks:
 * stun expiry, timed attribute modifiers, thorn hedges, relic bees, position trail (Cogloop), the Sealmark ward
 * (which can sit on a non-wearer), the Reweave damage share and the First Cut ward-phase bypass.
 * Registered on the NeoForge bus from {@link Relics}' static initialiser. All times are server tick counts.
 */
final class RelicTimers {
    private RelicTimers() {}

    private record Task(long at, Runnable run) {}
    private record Mod(LivingEntity entity, Holder<Attribute> attr, ResourceLocation id) {}
    private record Hedge(ServerLevel level, BlockPos pos) {}
    private record BeeInfo(UUID owner, long expiry) {}
    private record Snap(ResourceKey<Level> dim, Vec3 pos) {}

    private static final List<Task> TASKS = new ArrayList<>();
    private static final Map<Mob, Long> STUNNED = Collections.synchronizedMap(new WeakHashMap<>());
    private static final Map<Mod, Long> MODS = new HashMap<>();
    private static final Map<Hedge, Long> HEDGES = new LinkedHashMap<>();
    private static final Map<Bee, BeeInfo> BEES = Collections.synchronizedMap(new WeakHashMap<>());
    private static final Map<UUID, ArrayDeque<Snap>> TRAIL = new HashMap<>();
    private static final int TRAIL_TICKS = 60; // Cogloop blinks back 3 s

    static final String STUN_TAG = "guardians_stun_until", BEE_EXPIRY_TAG = "guardians_bee_expiry";
    static final String BEE_OWNER_TAG = "guardians_bee_owner";
    static final String WARD_KEY = "ward_until";
    static final String REWEAVE_GUARD_KEY = "reweave_guard_until";

    private static long now;

    /** Player ticks run before {@link ServerTickEvent.Post}, so {@link #now} can still be 0 on the first login tick. */
    private static long clock(LivingEntity e) {
        MinecraftServer server = e.getServer();
        return server != null ? RelicUtil.now(server) : now;
    }

    private static long clock(ServerLevel level) {
        MinecraftServer server = level.getServer();
        return server != null ? RelicUtil.now(server) : now;
    }

    // ------------------------------------------------------------------ scheduling

    static void later(ServerPlayer p, int delay, Runnable r) { TASKS.add(new Task(RelicUtil.now(p) + delay, r)); }

    /** Mobs lose AI for {@code ticks}; Guardians are never stunned (their fight logic is not goal-based). */
    static void stun(LivingEntity e, int ticks) {
        if (!(e instanceof Mob m) || e instanceof GuardianEntity) return;
        long until = clock(e) + ticks;
        if (!m.isNoAi()) m.setNoAi(true);
        else if (!STUNNED.containsKey(m)) return; // was NoAI before us: leave it alone
        STUNNED.merge(m, until, Math::max);
        m.getPersistentData().putLong(STUN_TAG, STUNNED.get(m));                     // survives unload/restart: restored in onJoin
    }

    static void timedModifier(LivingEntity e, Holder<Attribute> attr, ResourceLocation id, double amount, AttributeModifier.Operation op, int ticks) {
        AttributeInstance inst = e.getAttribute(attr);
        if (inst == null) return;
        inst.addOrUpdateTransientModifier(new AttributeModifier(id, amount, op));
        MODS.merge(new Mod(e, attr, id), clock(e) + ticks, Math::max);
    }

    static void endModifier(LivingEntity e, Holder<Attribute> attr, ResourceLocation id) {
        AttributeInstance inst = e.getAttribute(attr);
        if (inst != null) inst.removeModifier(id);
        MODS.remove(new Mod(e, attr, id));
    }

    /** Places a thorn hedge (sweet berry bush, age 1) that is removed after {@code ticks}. */
    static void hedge(ServerLevel level, BlockPos pos, int ticks) {
        level.setBlock(pos, Blocks.SWEET_BERRY_BUSH.defaultBlockState().setValue(SweetBerryBushBlock.AGE, 1), 3);   // age 1: thorns, no berries to pick
        HEDGES.put(new Hedge(level, pos.immutable()), clock(level) + ticks);
    }

    private static void unhedge(Hedge h) {
        if (h.level.getServer() == null || h.level.getServer().isStopped()) return;
        if (h.level.getBlockState(h.pos).is(Blocks.SWEET_BERRY_BUSH)) h.level.removeBlock(h.pos, false);
    }

    /** The owner walking into their own hedge breaks it. */
    static void trampleHedges(ServerPlayer p) {
        if (HEDGES.isEmpty()) return;
        Iterator<Hedge> it = HEDGES.keySet().iterator();
        while (it.hasNext()) {
            Hedge h = it.next();
            if (h.level == p.level() && p.getBoundingBox().inflate(0.05).intersects(new net.minecraft.world.phys.AABB(h.pos))) { unhedge(h); it.remove(); }
        }
    }

    static void bee(Bee b, UUID owner, int ticks) {
        long until = clock(b) + ticks;
        BEES.put(b, new BeeInfo(owner, until));
        b.getPersistentData().putLong(BEE_EXPIRY_TAG, until);
        b.getPersistentData().putUUID(BEE_OWNER_TAG, owner);
    }

    /** A relic bee or a stunned mob that comes back from disk (chunk reload, restart) is settled here rather than left as it was saved. */
    @SubscribeEvent
    static void onJoin(EntityJoinLevelEvent e) {
        if (e.getLevel().isClientSide) return;
        if (e.loadedFromDisk() && e.getEntity() instanceof Bee b && b.getTags().contains(RelicUtil.BEE_TAG) && !BEES.containsKey(b)) {
            long until = b.getPersistentData().getLong(BEE_EXPIRY_TAG);
            UUID owner = b.getPersistentData().hasUUID(BEE_OWNER_TAG) ? b.getPersistentData().getUUID(BEE_OWNER_TAG) : null;
            if (owner != null && until > clock(b)) {
                BEES.put(b, new BeeInfo(owner, until));
            } else {
                try { popBee(b); } catch (Exception ignored) {}
                e.setCanceled(true);
            }
            return;
        }
        if (e.getEntity() instanceof Mob m && m.getPersistentData().contains(STUN_TAG) && !STUNNED.containsKey(m)) {
            long until = m.getPersistentData().getLong(STUN_TAG);
            if (until > clock(m)) {
                if (!m.isNoAi()) m.setNoAi(true);
                STUNNED.put(m, until);
            } else {
                m.setNoAi(false);
                m.getPersistentData().remove(STUN_TAG);
            }
        }
    }

    /** Pop swarm honey while the world can still spawn items. ServerStopped is too late (isStopped, no drops). */
    @SubscribeEvent
    static void onServerStopping(ServerStoppingEvent e) {
        synchronized (BEES) {
            for (Bee b : new ArrayList<>(BEES.keySet())) {
                try { popBee(b); } catch (Exception ignored) {}
            }
            BEES.clear();
        }
    }

    /** A closed world takes its relic state with it (single-player exits, /stop): nothing from it may fire into the next one. */
    @SubscribeEvent
    static void onServerStopped(ServerStoppedEvent e) {
        for (Hedge h : new ArrayList<>(HEDGES.keySet())) try { unhedge(h); } catch (Exception ignored) {}
        TASKS.clear(); STUNNED.clear(); MODS.clear(); HEDGES.clear(); BEES.clear(); TRAIL.clear();
        if (RelicUtil.EXDEORUM) com.ninjacat.skies.guardians.relic.compat.SieveCompat.clearAll();
    }

    static List<Bee> beesOf(ServerPlayer owner) {
        List<Bee> out = new ArrayList<>();
        synchronized (BEES) {
            for (var e : BEES.entrySet()) {
                Bee b = e.getKey();
                if (b != null && e.getValue().owner.equals(owner.getUUID()) && b.isAlive()) out.add(b);
            }
        }
        return out;
    }

    private static void popBee(Bee b) {
        ServerLevel l;
        try {
            l = b.level() instanceof ServerLevel sl ? sl : null;
        } catch (IllegalStateException e) {
            return;
        }
        if (l == null || l.getServer() == null || l.getServer().isStopped()) return;
        l.addFreshEntity(new ItemEntity(l, b.getX(), b.getY(), b.getZ(), new ItemStack(Items.HONEY_BOTTLE)));
        RelicUtil.burst(l, ParticleTypes.FALLING_HONEY, new Vec3(b.getX(), b.getY(), b.getZ()), 6, 0.3, 0.02);
        if (b.isAlive()) b.discard();
    }

    static void recordTrail(ServerPlayer p) {
        ArrayDeque<Snap> d = TRAIL.computeIfAbsent(p.getUUID(), k -> new ArrayDeque<>());
        d.addLast(new Snap(p.level().dimension(), p.position()));
        while (d.size() > TRAIL_TICKS) d.pollFirst();
    }

    static void clearTrail(ServerPlayer p) { TRAIL.remove(p.getUUID()); }

    /** Where the player stood ~3 s ago in their current dimension, or null. */
    @Nullable
    static Vec3 trailBack(ServerPlayer p) {
        ArrayDeque<Snap> d = TRAIL.get(p.getUUID());
        if (d == null || d.isEmpty()) return null;
        Snap s = d.peekFirst();
        return s.dim.equals(p.level().dimension()) ? s.pos : null;
    }

    // ------------------------------------------------------------------ tick

    @SubscribeEvent
    static void onTick(ServerTickEvent.Post e) {
        MinecraftServer server = e.getServer();
        now = RelicUtil.now(server);

        if (!TASKS.isEmpty()) {
            List<Task> due = new ArrayList<>();
            TASKS.removeIf(t -> { if (t.at <= now) { due.add(t); return true; } return false; });
            for (Task t : due) { try { t.run.run(); } catch (Exception ignored) {} }
        }
        synchronized (STUNNED) {
            STUNNED.entrySet().removeIf(en -> {
                Mob m = en.getKey();
                if (m == null || m.isRemoved() || !m.isAlive()) return true;
                if (en.getValue() > now) return false;
                m.setNoAi(false); m.getPersistentData().remove(STUN_TAG); return true;
            });
        }
        MODS.entrySet().removeIf(en -> {
            if (en.getValue() > now && en.getKey().entity.isAlive()) return false;
            AttributeInstance inst = en.getKey().entity.getAttribute(en.getKey().attr);
            if (inst != null) inst.removeModifier(en.getKey().id);
            return true;
        });
        HEDGES.entrySet().removeIf(en -> {
            if (en.getValue() > now) return false;
            try { unhedge(en.getKey()); } catch (Exception ignored) {}
            return true;
        });
        synchronized (BEES) {
            BEES.entrySet().removeIf(en -> {
                Bee b = en.getKey();
                if (b == null) return true;
                if (b.isRemoved() && b.getRemovalReason() != null && !b.getRemovalReason().shouldDestroy()) return true;   // chunk unload: NBT keeps owner/expiry, onJoin restores or pops
                if (b.isRemoved() || !b.isAlive() || en.getValue().expiry <= now) {
                    try { popBee(b); } catch (Exception ignored) {}
                    return true;
                }
                return false;
            });
        }
    }

    // ------------------------------------------------------------------ static damage hooks

    @SubscribeEvent
    static void onIncoming(LivingIncomingDamageEvent e) {
        // Relic bee stings: Poison I for 2 s on whatever they sting.
        if (e.getSource().getEntity() instanceof Bee b && b.getTags().contains(RelicUtil.BEE_TAG)) {
            if (e.getEntity() instanceof Player) { e.setCanceled(true); return; }               // relic bees never sting people
            RelicUtil.effect(e.getEntity(), MobEffects.POISON, 40, 0);
        }
        if (!(e.getEntity() instanceof ServerPlayer p) || p.isSpectator()) return;
        if (e.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)) return;
        // Sealmark ward: the next hit of >= 3 hearts (6.0) is negated, once. May sit on a non-wearer (cast on a mate).
        if (RelicUtil.until(p, WARD_KEY) && e.getAmount() >= 6.0F) {
            RelicUtil.clear(p, WARD_KEY);
            e.setCanceled(true);
            RelicUtil.sound(p, SoundEvents.GLASS_BREAK, 1.0F, 0.8F);
            RelicUtil.burst(p.serverLevel(), ParticleTypes.END_ROD, p, 24, 0.6, 0.15);
            RelicUtil.note(p, "The ward shatters.");
            return;
        }
        // Overweaver's Reweave: everyone inside takes 20 % less.
        if (RelicUtil.until(p, REWEAVE_GUARD_KEY)) e.setAmount(e.getAmount() * 0.8F);
    }

    /**
     * Shard of the First Cut, "Severed": Guardians cancel damage inside {@code hurt()} during ward phases, so the damage
     * event never fires. Instead we take 25 % of the wearer's attack damage straight off the boss's health here.
     * Never drops a Guardian below 1 HP — its own fight logic still finishes it.
     */
    @SubscribeEvent
    static void onAttack(AttackEntityEvent e) {
        if (!(e.getEntity() instanceof ServerPlayer p) || p.isSpectator() || !(e.getTarget() instanceof GuardianEntity g)) return;
        if (!g.isImmune() || !g.isAlive() || g.getHealth() <= 1.0F) return;
        if (p.getAttackStrengthScale(0.5F) < 0.9F) return;
        boolean severed = false;
        for (ItemStack s : RelicSlots.worn(p)) if (((RelicItem) s.getItem()).kind == GuardianKind.FIRSTCUT) { severed = true; break; }
        if (!severed) return;
        float dmg = (float) (p.getAttributeValue(Attributes.ATTACK_DAMAGE) * 0.25);
        g.setHealth(Math.max(1.0F, g.getHealth() - dmg));
        RelicUtil.burst((ServerLevel) g.level(), ParticleTypes.SCULK_SOUL, g, 8, 0.5, 0.05);
        RelicUtil.burst((ServerLevel) g.level(), RelicUtil.GOLD, g, 8, 0.6, 0.0);
        RelicUtil.sound(g, SoundEvents.GLASS_BREAK, 0.6F, 1.6F);
    }
}
