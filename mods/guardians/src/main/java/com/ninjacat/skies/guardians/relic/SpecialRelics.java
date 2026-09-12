package com.ninjacat.skies.guardians.relic;

import com.ninjacat.skies.core.event.SkyboundEvents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.damagesource.DamageContainer;
import net.neoforged.neoforge.event.entity.living.LivingDamageEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;

/** The two easy relics (Lintwisp, Knotcharm) and the two insane ones (Shard of the First Cut, Overweaver's Shuttle). */
final class SpecialRelics {
    private SpecialRelics() {}

    // ================================================================== Lintwisp (Lint Golem)
    static RelicPower lintwisp() {
        return new BaseRelic("Lintwisp", "Soft: immune to cactus, berry-bush and thorn-hedge damage.",
                "Puff: a harmless cloud of lint that blinds every mob within 5 blocks for 4 s.", 400) { // 20 s
            @Override public void onWearerHurt(ServerPlayer p, ItemStack s, LivingIncomingDamageEvent e) { RelicUtil.contactImmune(e); }
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                for (LivingEntity m : RelicUtil.mobsAround(p, 5)) RelicUtil.effect(m, MobEffects.BLINDNESS, 80, 0); // 4 s
                RelicUtil.burst(p.serverLevel(), ParticleTypes.POOF, p.position().add(0, 1, 0), 40, 2.0, 0.05);
                RelicUtil.burst(p.serverLevel(), ParticleTypes.CLOUD, p.position().add(0, 1, 0), 20, 1.5, 0.02);
                RelicUtil.sound(p, SoundEvents.PANDA_SNEEZE, 1.2F, 1.1F);
                return true;
            }
        };
    }

    // ================================================================== Knotcharm (Tangle)
    static RelicPower knotcharm() {
        return new BaseRelic("Knotcharm", "Sure-footed: no slowdown on soul sand or honey, a burst of speed through cobwebs and powder snow, never freezes.",
                "Tangle: throw a knot up to 12 blocks; the first mob hit is rooted for 4 s (it can still attack).", 600) { // 30 s
            @Override public void onWorn(ServerPlayer p, boolean worn) {
                RelicUtil.modifier(p, Attributes.MOVEMENT_EFFICIENCY, "knotcharm_footing", 1.0, AttributeModifier.Operation.ADD_VALUE, worn);
            }
            @Override public void tickWorn(ServerPlayer p, ItemStack s) {
                RelicUtil.modifier(p, Attributes.MOVEMENT_EFFICIENCY, "knotcharm_footing", 1.0, AttributeModifier.Operation.ADD_VALUE, true);
                BlockState in = p.getInBlockState();
                if (in.is(Blocks.COBWEB) || in.is(Blocks.POWDER_SNOW)) RelicUtil.effect(p, MobEffects.MOVEMENT_SPEED, 20, 2); // Speed III compensates the stuck multiplier
                if (p.getTicksFrozen() > 0) p.setTicksFrozen(0);
            }
            @Override public void onWearerHurt(ServerPlayer p, ItemStack s, LivingIncomingDamageEvent e) {
                if (e.getSource().is(DamageTypeTags.IS_FREEZING)) e.setCanceled(true);
            }
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                Vec3 start = p.getEyePosition(), end = start.add(p.getLookAngle().scale(12));
                AABB box = p.getBoundingBox().expandTowards(p.getLookAngle().scale(12)).inflate(1.0);
                EntityHitResult hit = ProjectileUtil.getEntityHitResult(p.level(), p, start, end, box,
                        ent -> ent instanceof LivingEntity && !(ent instanceof Player) && !(ent instanceof com.ninjacat.skies.guardians.entity.GuardianEntity) && !(ent instanceof net.minecraft.world.entity.TamableAnimal t && t.isTame()) && !ent.getTags().contains(RelicUtil.BEE_TAG) && ent.isAlive() && !ent.isSpectator());
                if (hit == null || !(hit.getEntity() instanceof LivingEntity target)) { RelicUtil.note(p, "The knot finds nothing."); return false; }
                RelicUtil.root(target, 80);                                        // 4 s
                ServerLevel l = p.serverLevel();
                RelicUtil.line(l, RelicUtil.GOLD, start.add(0, -0.3, 0), target.position().add(0, target.getBbHeight() * 0.5, 0), 16);
                RelicUtil.ring(l, RelicUtil.GOLD, target.position().add(0, target.getBbHeight() * 0.5, 0), target.getBbWidth() * 0.8, 12);
                RelicUtil.sound(target, SoundEvents.LEASH_KNOT_PLACE, 1.0F, 0.7F);
                return true;
            }
        };
    }

    // ================================================================== Shard of the First Cut
    static RelicPower firstCut() {
        return new BaseRelic("Shard of the First Cut", "Severed: your melee hits ignore 30 % of armour and cut through Guardian ward phases for 25 % damage.",
                "The Cut: slash a 6-block line ahead; every mob in it takes 12 hearts of true damage and boss projectiles in it are cut apart.", 2400) { // 120 s
            // "ignore 30 % of armour" is registered in RelicEvents.onIncoming (the target's LivingIncomingDamageEvent): by the time
            // LivingDamageEvent.Pre fires, the armour reduction has already been taken and a modifier added there is never run.
            // Ward-phase bypass lives in RelicTimers.onAttack (the boss cancels inside hurt(), before any damage event).
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                ServerLevel l = p.serverLevel();
                Vec3 eye = p.getEyePosition(), look = p.getLookAngle();
                int hit = 0;
                for (Entity ent : l.getEntities(p, p.getBoundingBox().inflate(7.5), ent -> ent.isAlive() && !(ent instanceof Player))) {
                    Vec3 rel = ent.position().add(0, ent.getBbHeight() * 0.5, 0).subtract(eye);
                    double along = rel.dot(look);
                    if (along < 0 || along > 6.5) continue;
                    if (rel.subtract(look.scale(along)).length() > 1.5 + ent.getBbWidth() * 0.5) continue;
                    if (ent instanceof LivingEntity le && !le.getTags().contains(RelicUtil.BEE_TAG)) {
                        le.hurt(p.damageSources().indirectMagic(p, p), 24.0F);     // 12 hearts, bypasses armour
                        RelicUtil.burst(l, ParticleTypes.SCULK_SOUL, le, 10, 0.4, 0.05);
                        hit++;
                    } else if (ent instanceof Projectile pr && !(pr.getOwner() instanceof Player)) {
                        RelicUtil.burst(l, RelicUtil.TEAL, pr, 8, 0.2, 0.0);
                        pr.discard();
                    }
                }
                Vec3 a = eye.add(look.scale(0.5)), b = eye.add(look.scale(6.5));
                RelicUtil.line(l, ParticleTypes.SWEEP_ATTACK, a, b, 6);
                RelicUtil.line(l, RelicUtil.GOLD, a, b, 24);
                RelicUtil.line(l, ParticleTypes.SCULK_SOUL, a.add(0, -0.3, 0), b.add(0, -0.3, 0), 12);
                RelicUtil.sound(p, SoundEvents.GLASS_BREAK, 1.2F, 0.6F);
                RelicUtil.sound(p, SoundEvents.BEACON_DEACTIVATE, 1.0F, 0.5F);
                if (hit > 0) RelicUtil.note(p, "The cut takes " + hit + ".");
                return true;
            }
        };
    }

    // ================================================================== Overweaver's Shuttle
    private static final String REWEAVE_KEY = "reweave_until", REWEAVE_REVIVE = "reweave_revive_left";

    static RelicPower overweaverShuttle() {
        return new BaseRelic("Overweaver's Shuttle",
                "Nine Strands: knockback -30 %, Thorns, Haste I, magic -10 %, bees ignore you, safe falls to 8 blocks, sure-footed, thorn-proof.",
                "Reweave: for 10 s every Clowder-mate within 16 blocks shares your buffs and takes 20 % less damage; a downed mate in range is revived at half health, once.", 3600) { // 180 s
            private void attributes(ServerPlayer p, boolean on) {
                RelicUtil.modifier(p, Attributes.KNOCKBACK_RESISTANCE, "shuttle_anchor", 0.3, AttributeModifier.Operation.ADD_VALUE, on);
                RelicUtil.modifier(p, Attributes.SAFE_FALL_DISTANCE, "shuttle_landing", 5.0, AttributeModifier.Operation.ADD_VALUE, on); // 3 -> 8
                RelicUtil.modifier(p, Attributes.MOVEMENT_EFFICIENCY, "shuttle_footing", 0.5, AttributeModifier.Operation.ADD_VALUE, on);
            }
            @Override public void onWorn(ServerPlayer p, boolean worn) { attributes(p, worn); }
            @Override public void onWearerHurt(ServerPlayer p, ItemStack s, LivingIncomingDamageEvent e) {
                RelicUtil.contactImmune(e);
                RelicUtil.beeImmune(e);
                if (e.isCanceled()) return;
                RelicUtil.magicReduce(e, 0.9F);
                RelicUtil.thorns(p, e, 2.0F);
            }
            @Override public void tickWorn(ServerPlayer p, ItemStack s) {
                attributes(p, true);
                RelicUtil.passive(p, MobEffects.DIG_SPEED, 0);                     // Haste I
                RelicUtil.calmBees(p);
                if (!RelicUtil.until(p, REWEAVE_KEY)) return;
                ServerLevel l = p.serverLevel();
                RelicUtil.setUntil(p, RelicTimers.REWEAVE_GUARD_KEY, 25);
                var mates = RelicUtil.mates(p, 16);
                boolean pulse = p.tickCount % 20 == 0;
                int i = 0;
                for (ServerPlayer m : mates) {
                    if (m.isSpectator()) { tryRevive(p, m); continue; }
                    RelicUtil.setUntil(m, RelicTimers.REWEAVE_GUARD_KEY, 25);
                    if (pulse) {
                        for (MobEffectInstance eff : p.getActiveEffects()) {
                            if (!eff.getEffect().value().isBeneficial()) continue;
                            m.addEffect(new MobEffectInstance(eff.getEffect(), eff.isInfiniteDuration() ? 60 : Math.min(eff.getDuration(), 60), eff.getAmplifier(), true, false, false));
                        }
                    }
                    if (p.tickCount % 10 == 0) RelicUtil.line(l, (i++ % 2 == 0) ? RelicUtil.TEAL : RelicUtil.GOLD, p.position().add(0, 1.2, 0), m.position().add(0, 1.2, 0), 12);
                }
            }
            /** "Downed" in this pack = the shared-lives pool is spent and the mate sits in spectator with the exhausted flag. */
            private void tryRevive(ServerPlayer p, ServerPlayer m) {
                var t = RelicUtil.tag(p);
                if (t.getInt(REWEAVE_REVIVE) <= 0 || !m.getPersistentData().getBoolean("skybound_exhausted")) return;
                t.putInt(REWEAVE_REVIVE, 0);
                if (SkyboundEvents.restoreOneLife(m) < 0) return;
                ServerPlayer wearer = p;
                RelicTimers.later(p, 2, () -> {
                    if (m.isSpectator()) return;
                    m.teleportTo(wearer.serverLevel(), wearer.getX(), wearer.getY(), wearer.getZ(), m.getYRot(), m.getXRot());
                    m.setHealth(m.getMaxHealth() * 0.5F);
                    RelicUtil.burst(wearer.serverLevel(), ParticleTypes.TOTEM_OF_UNDYING, m, 40, 0.8, 0.3);
                    RelicUtil.sound(m, SoundEvents.TOTEM_USE, 1.0F, 1.2F);
                });
            }
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                RelicUtil.setUntil(p, REWEAVE_KEY, 200);                           // 10 s
                RelicUtil.tag(p).putInt(REWEAVE_REVIVE, 1);
                ServerLevel l = p.serverLevel();
                int i = 0;
                for (ServerPlayer m : RelicUtil.mates(p, 16)) RelicUtil.line(l, (i++ % 2 == 0) ? RelicUtil.TEAL : RelicUtil.GOLD, p.position().add(0, 1.2, 0), m.position().add(0, 1.2, 0), 20);
                RelicUtil.ring(l, RelicUtil.GOLD, p.position().add(0, 0.2, 0), 1.5, 18);
                RelicUtil.sound(p, SoundEvents.UI_LOOM_TAKE_RESULT, 1.2F, 0.8F);
                RelicTimers.later(p, 6, () -> RelicUtil.sound(p, SoundEvents.BELL_RESONATE, 0.8F, 1.3F));
                return true;
            }
        };
    }
}
