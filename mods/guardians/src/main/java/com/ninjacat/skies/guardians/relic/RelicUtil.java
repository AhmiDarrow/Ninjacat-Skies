package com.ninjacat.skies.guardians.relic;

import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.guardians.Guardians;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Bee;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import org.joml.Vector3f;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;

/** Small server-side helpers shared by the relic powers: persistent flags, effects, particles, sounds, Clowder lookups. */
final class RelicUtil {
    private RelicUtil() {}

    static final String TAG = "guardians";
    /** Scoreboard tag on bees summoned by Hivecall. */
    static final String BEE_TAG = "guardians_relic_bee";
    static final DustParticleOptions TEAL = new DustParticleOptions(new Vector3f(0.24F, 0.48F, 0.48F), 1.0F);
    static final DustParticleOptions GOLD = new DustParticleOptions(new Vector3f(0.83F, 0.66F, 0.29F), 1.0F);

    // ------------------------------------------------------------------ persistent flags (survive death/relog)

    static CompoundTag tag(ServerPlayer p) {
        CompoundTag root = p.getPersistentData();
        CompoundTag persisted = root.getCompound(Player.PERSISTED_NBT_TAG);
        if (!root.contains(Player.PERSISTED_NBT_TAG)) root.put(Player.PERSISTED_NBT_TAG, persisted);
        CompoundTag g = persisted.getCompound(TAG);
        if (!persisted.contains(TAG)) persisted.put(TAG, g);
        return g;
    }

    static long now(ServerPlayer p) { return p.server.getTickCount(); }
    /** True while the timed flag {@code key} is still running. */
    static boolean until(ServerPlayer p, String key) { return tag(p).getLong(key) > now(p); }
    static void setUntil(ServerPlayer p, String key, int ticks) { tag(p).putLong(key, now(p) + ticks); }
    static void clear(ServerPlayer p, String key) { tag(p).remove(key); }

    // ------------------------------------------------------------------ attributes

    static ResourceLocation id(String path) { return ResourceLocation.fromNamespaceAndPath(Guardians.MOD_ID, path); }

    /** Adds (or removes) a transient attribute modifier with a fixed id. Safe to call every tick. */
    static void modifier(LivingEntity e, Holder<Attribute> attr, String id, double amount, AttributeModifier.Operation op, boolean on) {
        AttributeInstance inst = e.getAttribute(attr);
        if (inst == null) return;
        ResourceLocation rl = id(id);
        if (!on) { inst.removeModifier(rl); return; }
        if (!inst.hasModifier(rl)) inst.addTransientModifier(new AttributeModifier(rl, amount, op));
    }

    /** Rooted: movement speed x0, jump strength 0 for {@code ticks} (plus a Slowness visual). Can still attack. */
    static void root(LivingEntity e, int ticks) {
        RelicTimers.timedModifier(e, Attributes.MOVEMENT_SPEED, id("root_speed"), -1.0, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL, ticks);
        RelicTimers.timedModifier(e, Attributes.JUMP_STRENGTH, id("root_jump"), -1.0, AttributeModifier.Operation.ADD_VALUE, ticks);
        effect(e, MobEffects.MOVEMENT_SLOWDOWN, ticks, 4);
    }

    static void unroot(LivingEntity e) {
        RelicTimers.endModifier(e, Attributes.MOVEMENT_SPEED, id("root_speed"));
        RelicTimers.endModifier(e, Attributes.JUMP_STRENGTH, id("root_jump"));
        e.removeEffect(MobEffects.MOVEMENT_SLOWDOWN);
    }

    // ------------------------------------------------------------------ effects

    /** Ambient, particle-less effect (vanilla only upgrades if this is stronger/longer than what is already there). */
    static void effect(LivingEntity e, Holder<MobEffect> eff, int ticks, int amp) {
        e.addEffect(new MobEffectInstance(eff, ticks, amp, true, false, false));
    }

    /** A "while worn" effect: call from tickWorn; re-applied every 10 ticks with a 50-tick tail so it fades when unequipped. */
    static void passive(ServerPlayer p, Holder<MobEffect> eff, int amp) {
        if (p.tickCount % 10 == 0) effect(p, eff, 50, amp);
    }

    // ------------------------------------------------------------------ shared passive hooks (used by several relics)

    /** Thorns: a direct melee attacker takes {@code dmg} back. Skips thorns-on-thorns loops and projectiles. */
    static void thorns(ServerPlayer p, LivingIncomingDamageEvent e, float dmg) {
        DamageSource src = e.getSource();
        if (src.is(DamageTypes.THORNS) || src.is(DamageTypeTags.IS_PROJECTILE)) return;
        if (src.getEntity() instanceof LivingEntity a && src.getDirectEntity() == a && a != p && a.isAlive()) {
            a.hurt(p.damageSources().thorns(p), dmg);
        }
    }

    /** Immunity to cactus / sweet-berry-bush (= thorn hedge) contact damage. */
    static void contactImmune(LivingIncomingDamageEvent e) {
        if (e.getSource().is(DamageTypes.CACTUS) || e.getSource().is(DamageTypes.SWEET_BERRY_BUSH)) e.setCanceled(true);
    }

    /** Magic-ish damage (potions, wither, dragon breath, Ars spells by type name) scaled by {@code factor}. */
    static void magicReduce(LivingIncomingDamageEvent e, float factor) {
        DamageSource src = e.getSource();
        String path = src.typeHolder().unwrapKey().map(k -> k.location().getPath()).orElse("");
        boolean magic = src.is(DamageTypeTags.WITCH_RESISTANT_TO) || src.is(DamageTypes.WITHER) || src.is(DamageTypes.DRAGON_BREATH)
                || path.contains("magic") || path.contains("spell") || path.contains("potion") || path.contains("wither");
        if (magic) e.setAmount(e.getAmount() * factor);
    }

    /** Bees never hurt the wearer. */
    static void beeImmune(LivingIncomingDamageEvent e) {
        if (e.getSource().getEntity() instanceof Bee) e.setCanceled(true);
    }

    /** Calm any bee that has decided the wearer is the problem (call every 20 ticks). */
    static void calmBees(ServerPlayer p) {
        if (p.tickCount % 20 != 0) return;
        for (Bee b : p.serverLevel().getEntitiesOfClass(Bee.class, p.getBoundingBox().inflate(8))) {
            if (b.getTarget() == p || p.getUUID().equals(b.getPersistentAngerTarget())) {
                b.setTarget(null); b.setPersistentAngerTarget(null); b.setRemainingPersistentAngerTime(0);
            }
        }
    }

    // ------------------------------------------------------------------ Clowder

    /** Online Clowder-mates (not the player) in the same level within {@code r} blocks. */
    static List<ServerPlayer> mates(ServerPlayer p, double r) {
        List<ServerPlayer> out = new ArrayList<>();
        LoomTension.clowderOf(p).ifPresent(c -> {
            for (ServerPlayer m : c.onlineMembers()) {
                if (m != p && m.level() == p.level() && m.isAlive() && m.distanceToSqr(p) <= r * r) out.add(m);
            }
        });
        return out;
    }

    static boolean isMate(ServerPlayer p, Entity other) {
        if (other == p) return true;
        if (!(other instanceof ServerPlayer sp)) return false;
        return LoomTension.clowderOf(p).map(c -> c.onlineMembers().contains(sp)).orElse(false);
    }

    /** The mate the player is looking at (within {@code r} blocks, ~18° cone), or null. */
    @Nullable
    static ServerPlayer lookedMate(ServerPlayer p, double r) {
        Vec3 eye = p.getEyePosition(), look = p.getLookAngle();
        ServerPlayer best = null; double bestDot = 0.95;
        for (ServerPlayer m : mates(p, r)) {
            double dot = look.dot(m.getEyePosition().subtract(eye).normalize());
            if (dot > bestDot) { bestDot = dot; best = m; }
        }
        return best;
    }

    /** Hostile-able living things near the player: no players, no tamed pets, no relic bees. */
    static List<LivingEntity> mobsAround(ServerPlayer p, double r) {
        return p.serverLevel().getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(r), e ->
                e != p && !(e instanceof Player) && e.isAlive() && e.distanceToSqr(p) <= r * r
                        && !e.getTags().contains(BEE_TAG) && !(e instanceof TamableAnimal t && t.isTame()));
    }

    // ------------------------------------------------------------------ presentation

    static void sound(ServerPlayer p, SoundEvent s, float volume, float pitch) {
        p.level().playSound(null, p.getX(), p.getY(), p.getZ(), s, SoundSource.PLAYERS, volume, pitch);
    }

    static void sound(Entity at, SoundEvent s, float volume, float pitch) {
        at.level().playSound(null, at.getX(), at.getY(), at.getZ(), s, SoundSource.PLAYERS, volume, pitch);
    }

    static void burst(ServerLevel l, ParticleOptions t, Vec3 at, int n, double spread, double speed) {
        l.sendParticles(t, at.x, at.y, at.z, n, spread, spread, spread, speed);
    }

    static void burst(ServerLevel l, ParticleOptions t, Entity at, int n, double spread, double speed) {
        burst(l, t, at.position().add(0, at.getBbHeight() * 0.5, 0), n, spread, speed);
    }

    /** Horizontal ring of {@code n} particles at radius {@code r}. */
    static void ring(ServerLevel l, ParticleOptions t, Vec3 c, double r, int n) {
        for (int i = 0; i < n; i++) {
            double a = Math.PI * 2 * i / n;
            l.sendParticles(t, c.x + Math.cos(a) * r, c.y, c.z + Math.sin(a) * r, 1, 0, 0, 0, 0);
        }
    }

    static void line(ServerLevel l, ParticleOptions t, Vec3 a, Vec3 b, int n) {
        for (int i = 0; i <= n; i++) {
            Vec3 at = a.lerp(b, (double) i / n);
            l.sendParticles(t, at.x, at.y, at.z, 1, 0, 0, 0, 0);
        }
    }

    static void note(ServerPlayer p, String text) { p.displayClientMessage(NinjacatText.teal(text), true); }
}
