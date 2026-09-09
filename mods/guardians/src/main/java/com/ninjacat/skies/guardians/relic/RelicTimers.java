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
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SweetBerryBushBlock;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.AttackEntityEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

import javax.annotation.Nullable;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

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
    private static final Map<Mob, Long> STUNNED = new HashMap<>();
    private static final Map<Mod, Long> MODS = new HashMap<>();
    private static final Map<Hedge, Long> HEDGES = new LinkedHashMap<>();
    private static final Map<Bee, BeeInfo> BEES = new HashMap<>();
    private static final Map<UUID, ArrayDeque<Snap>> TRAIL = new HashMap<>();
    private static final int TRAIL_TICKS = 60; // Cogloop blinks back 3 s

    static final String WARD_KEY = "ward_until";
    static final String REWEAVE_GUARD_KEY = "reweave_guard_until";

    private static long now;

    // ------------------------------------------------------------------ scheduling

    static void later(ServerPlayer p, int delay, Runnable r) { TASKS.add(new Task(RelicUtil.now(p) + delay, r)); }

    /** Mobs lose AI for {@code ticks}; Guardians are never stunned (their fight logic is not goal-based). */
    static void stun(LivingEntity e, int ticks) {
        if (!(e instanceof Mob m) || e instanceof GuardianEntity) return;
        long until = now + ticks;
        if (!m.isNoAi()) m.setNoAi(true);
        else if (!STUNNED.containsKey(m)) return; // was NoAI before us: leave it alone
        STUNNED.merge(m, until, Math::max);
    }

    static void timedModifier(LivingEntity e, Holder<Attribute> attr, ResourceLocation id, double amount, AttributeModifier.Operation op, int ticks) {
        AttributeInstance inst = e.getAttribute(attr);
        if (inst == null) return;
        inst.addOrUpdateTransientModifier(new AttributeModifier(id, amount, op));
        MODS.merge(new Mod(e, attr, id), now + ticks, Math::max);
    }

    static void endModifier(LivingEntity e, Holder<Attribute> attr, ResourceLocation id) {
        AttributeInstance inst = e.getAttribute(attr);
        if (inst != null) inst.removeModifier(id);
        MODS.remove(new Mod(e, attr, id));
    }

    /** Places a thorn hedge (sweet berry bush, age 3) that is removed after {@code ticks}. */
    static void hedge(ServerLevel level, BlockPos pos, int ticks) {
        level.setBlock(pos, Blocks.SWEET_BERRY_BUSH.defaultBlockState().setValue(SweetBerryBushBlock.AGE, 3), 3);
        HEDGES.put(new Hedge(level, pos.immutable()), now + ticks);
    }

    private static void unhedge(Hedge h) {
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

    static void bee(Bee b, UUID owner, int ticks) { BEES.put(b, new BeeInfo(owner, now + ticks)); }

    static List<Bee> beesOf(ServerPlayer owner) {
        List<Bee> out = new ArrayList<>();
        for (var e : BEES.entrySet()) if (e.getValue().owner.equals(owner.getUUID()) && e.getKey().isAlive()) out.add(e.getKey());
        return out;
    }

    private static void popBee(Bee b) {
        ServerLevel l = (ServerLevel) b.level();
        l.addFreshEntity(new ItemEntity(l, b.getX(), b.getY(), b.getZ(), new ItemStack(Items.HONEY_BOTTLE)));
        RelicUtil.burst(l, ParticleTypes.FALLING_HONEY, b, 6, 0.3, 0.02);
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
        now = server.getTickCount();

        if (!TASKS.isEmpty()) {
            List<Task> due = new ArrayList<>();
            TASKS.removeIf(t -> { if (t.at <= now) { due.add(t); return true; } return false; });
            for (Task t : due) { try { t.run.run(); } catch (Exception ignored) {} }
        }
        STUNNED.entrySet().removeIf(en -> {
            Mob m = en.getKey();
            if (!m.isAlive()) return true;
            if (en.getValue() > now) return false;
            m.setNoAi(false); return true;
        });
        MODS.entrySet().removeIf(en -> {
            if (en.getValue() > now && en.getKey().entity.isAlive()) return false;
            AttributeInstance inst = en.getKey().entity.getAttribute(en.getKey().attr);
            if (inst != null) inst.removeModifier(en.getKey().id);
            return true;
        });
        HEDGES.entrySet().removeIf(en -> { if (en.getValue() > now) return false; unhedge(en.getKey()); return true; });
        BEES.entrySet().removeIf(en -> {
            Bee b = en.getKey();
            if (b.isRemoved() || !b.isAlive() || en.getValue().expiry <= now) { popBee(b); return true; }
            return false;
        });
    }

    // ------------------------------------------------------------------ static damage hooks

    @SubscribeEvent
    static void onIncoming(LivingIncomingDamageEvent e) {
        // Relic bee stings: Poison I for 2 s on whatever they sting.
        if (e.getSource().getEntity() instanceof Bee b && b.getTags().contains(RelicUtil.BEE_TAG)) {
            RelicUtil.effect(e.getEntity(), MobEffects.POISON, 40, 0);
        }
        if (!(e.getEntity() instanceof ServerPlayer p)) return;
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
        if (!(e.getEntity() instanceof ServerPlayer p) || !(e.getTarget() instanceof GuardianEntity g)) return;
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
