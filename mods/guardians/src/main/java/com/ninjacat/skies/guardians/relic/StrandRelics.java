package com.ninjacat.skies.guardians.relic;

import com.ninjacat.skies.core.tension.LoomTension;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Bee;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.event.entity.living.LivingDamageEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;

/** The nine Strand relics (WOVEN_RELICS.md). All numbers are in comments next to their use. */
final class StrandRelics {
    private StrandRelics() {}

    // ================================================================== Rootheart (Soil)
    private static final String ROOT_KEY = "root_until";

    static RelicPower rootheart() {
        return new BaseRelic("Rootheart", "Anchored: knockback taken -60 %.",
                "Root Down: root yourself for 5 s with 8 hearts of absorption, no fall damage, and Slowness II on anything that hits you. Sneak to cancel.", 600) { // 30 s
            @Override public void onWorn(ServerPlayer p, boolean worn) {
                RelicUtil.modifier(p, Attributes.KNOCKBACK_RESISTANCE, "rootheart_anchor", 0.6, AttributeModifier.Operation.ADD_VALUE, worn);
                if (!worn && RelicUtil.until(p, ROOT_KEY)) { RelicUtil.clear(p, ROOT_KEY); RelicUtil.unroot(p); }
            }
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                RelicUtil.setUntil(p, ROOT_KEY, 100);                      // 5 s
                RelicUtil.effect(p, MobEffects.ABSORPTION, 100, 3);        // amp 3 = 16 HP = 8 hearts
                RelicUtil.root(p, 100);
                ServerLevel l = p.serverLevel();
                RelicUtil.ring(l, ParticleTypes.COMPOSTER, p.position().add(0, 0.2, 0), 1.2, 16);
                RelicUtil.burst(l, ParticleTypes.GLOW, p.position().add(0, 0.5, 0), 12, 0.6, 0.02);
                RelicUtil.sound(p, SoundEvents.ROOTED_DIRT_BREAK, 1.0F, 0.6F);
                return true;
            }
            @Override public void tickWorn(ServerPlayer p, ItemStack s) {
                RelicUtil.modifier(p, Attributes.KNOCKBACK_RESISTANCE, "rootheart_anchor", 0.6, AttributeModifier.Operation.ADD_VALUE, true);
                if (!RelicUtil.until(p, ROOT_KEY)) return;
                if (p.isShiftKeyDown()) { RelicUtil.clear(p, ROOT_KEY); RelicUtil.unroot(p); return; }
                if (p.tickCount % 5 == 0) RelicUtil.burst(p.serverLevel(), ParticleTypes.GLOW, p.position().add(0, 0.3, 0), 2, 0.5, 0.0);
            }
            @Override public void onWearerHurt(ServerPlayer p, ItemStack s, LivingIncomingDamageEvent e) {
                if (!RelicUtil.until(p, ROOT_KEY)) return;
                if (e.getSource().is(DamageTypeTags.IS_FALL)) { e.setCanceled(true); return; }
                if (e.getSource().getEntity() instanceof LivingEntity a && !(a instanceof Player)) RelicUtil.effect(a, MobEffects.MOVEMENT_SLOWDOWN, 60, 1); // Slowness II 3 s
            }
        };
    }

    // ================================================================== Grindcore (Stone)
    private static final String SHRED_KEY = "shred_until";

    static RelicPower grindcore() {
        return new BaseRelic("Grindcore", "Grit: Haste I while worn and immune to Mining Fatigue.",
                "Shred: your next melee hit within 6 s strips 2 armour from the target for 8 s.", 500) { // 25 s
            @Override public void tickWorn(ServerPlayer p, ItemStack s) {
                RelicUtil.passive(p, MobEffects.DIG_SPEED, 0);                  // Haste I
                if (p.hasEffect(MobEffects.DIG_SLOWDOWN)) p.removeEffect(MobEffects.DIG_SLOWDOWN);
                if (RelicUtil.until(p, SHRED_KEY) && p.tickCount % 4 == 0) RelicUtil.burst(p.serverLevel(), ParticleTypes.CRIT, p.position().add(0, 1.0, 0), 2, 0.4, 0.05);
            }
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                RelicUtil.setUntil(p, SHRED_KEY, 120);                          // 6 s window
                ServerLevel l = p.serverLevel();
                RelicUtil.ring(l, ParticleTypes.CRIT, p.position().add(0, 1.0, 0), 1.0, 12);
                RelicUtil.ring(l, new BlockParticleOption(ParticleTypes.BLOCK, Blocks.STONE.defaultBlockState()), p.position().add(0, 0.8, 0), 0.8, 10);
                RelicUtil.sound(p, SoundEvents.GRINDSTONE_USE, 1.0F, 0.8F);
                return true;
            }
            @Override public void onWearerHit(ServerPlayer p, ItemStack s, LivingEntity target, LivingDamageEvent.Pre e) {
                if (!RelicUtil.until(p, SHRED_KEY)) return;
                RelicUtil.clear(p, SHRED_KEY);
                RelicTimers.timedModifier(target, Attributes.ARMOR, RelicUtil.id("shred_armor"), -2.0, AttributeModifier.Operation.ADD_VALUE, 160); // -2 armour, 8 s
                RelicUtil.burst(p.serverLevel(), ParticleTypes.CRIT, target, 16, 0.5, 0.2);
                RelicUtil.sound(target, SoundEvents.SHIELD_BREAK, 0.8F, 1.2F);
            }
        };
    }

    // ================================================================== Thornseed (Sprout)
    static RelicPower thornseed() {
        return new BaseRelic("Thornseed", "Bramble Skin: attackers take 1 heart; immune to berry-bush and cactus damage.",
                "Bloom: grow a ring of thorn hedge around you for 20 s and give you and mates inside it Regeneration II for 6 s.", 800) { // 40 s
            @Override public void onWearerHurt(ServerPlayer p, ItemStack s, LivingIncomingDamageEvent e) {
                RelicUtil.contactImmune(e);
                RelicUtil.thorns(p, e, 2.0F);                                    // 1 heart
            }
            @Override public void tickWorn(ServerPlayer p, ItemStack s) { RelicTimers.trampleHedges(p); }
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                ServerLevel l = p.serverLevel();
                BlockPos c = p.blockPosition();
                int placed = 0;
                for (int dx = -3; dx <= 3; dx++) for (int dz = -3; dz <= 3; dz++) {
                    double d = Math.sqrt(dx * dx + dz * dz);
                    if (d < 2.2 || d > 3.2) continue;                            // ring ~5 wide, 1 thick
                    for (int dy = 1; dy >= -1; dy--) {
                        BlockPos at = c.offset(dx, dy, dz);
                        if (!l.getBlockState(at).canBeReplaced() || !l.getBlockState(at).getFluidState().isEmpty()) continue;
                        if (!l.getBlockState(at.below()).isFaceSturdy(l, at.below(), net.minecraft.core.Direction.UP)) continue;
                        if (!l.getEntitiesOfClass(LivingEntity.class, new net.minecraft.world.phys.AABB(at)).isEmpty()) break;
                        RelicTimers.hedge(l, at, 400); placed++;                    // 20 s
                        break;
                    }
                }
                RelicUtil.effect(p, MobEffects.REGENERATION, 120, 1);            // Regen II 6 s
                for (ServerPlayer m : RelicUtil.mates(p, 3.5)) RelicUtil.effect(m, MobEffects.REGENERATION, 120, 1);
                RelicUtil.burst(l, ParticleTypes.HAPPY_VILLAGER, p.position().add(0, 1, 0), 30, 2.0, 0.1);
                RelicUtil.ring(l, ParticleTypes.GLOW, p.position().add(0, 0.6, 0), 2.7, 24);
                RelicUtil.sound(p, SoundEvents.SWEET_BERRY_BUSH_BREAK, 1.2F, 0.7F);
                if (placed == 0) RelicUtil.note(p, "No soil for the hedge here, but the sap still runs.");
                return true;
            }
        };
    }

    // ================================================================== Edgestep (Claw)
    private static final String EDGE_CHARGES = "edge_charges", EDGE_RECHARGE = "edge_recharge_at", EDGE_CLEAR = "edge_clear";
    private static final String EDGE_IFRAME = "edge_iframe_until", EDGE_HIT = "edge_hit_until";
    private static final int EDGE_MAX = 2, EDGE_CD = 240;                          // 2 charges, one back every 12 s

    static RelicPower edgestep() {
        return new BaseRelic("Edgestep", "Cat's Landing: no fall damage from 12 blocks or less.",
                "Edgestep: dash 6 blocks the way you look (works in the air), 0.3 s of i-frames, and +50 % damage on a hit right after. Two charges.", EDGE_CD) {
            @Override public void onWorn(ServerPlayer p, boolean worn) {
                RelicUtil.modifier(p, Attributes.SAFE_FALL_DISTANCE, "edgestep_landing", 9.0, AttributeModifier.Operation.ADD_VALUE, worn); // 3 -> 12
            }
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                CompoundTag t = RelicUtil.tag(p);
                int charges = t.contains(EDGE_CHARGES) ? t.getInt(EDGE_CHARGES) : EDGE_MAX;
                if (charges <= 0) return false;
                long now = RelicUtil.now(p);
                if (charges == EDGE_MAX || t.getLong(EDGE_RECHARGE) <= now) t.putLong(EDGE_RECHARGE, now + EDGE_CD);
                t.putInt(EDGE_CHARGES, --charges);
                if (charges > 0) t.putBoolean(EDGE_CLEAR, true);                   // item cooldown only when both are spent
                Vec3 look = p.getLookAngle();
                p.setDeltaMovement(look.scale(1.25));                              // ~6 blocks
                p.hurtMarked = true; p.fallDistance = 0;
                RelicUtil.setUntil(p, EDGE_IFRAME, 6);                             // 0.3 s
                RelicUtil.setUntil(p, EDGE_HIT, 14);
                ServerLevel l = p.serverLevel();
                RelicUtil.burst(l, ParticleTypes.SWEEP_ATTACK, p.position().add(0, 1, 0), 1, 0, 0);
                RelicUtil.line(l, ParticleTypes.END_ROD, p.position().add(0, 1, 0), p.position().add(0, 1, 0).add(look.scale(6)), 12);
                RelicUtil.sound(p, SoundEvents.PLAYER_ATTACK_SWEEP, 1.0F, 1.5F);
                return true;
            }
            @Override public void tickWorn(ServerPlayer p, ItemStack s) {
                RelicUtil.modifier(p, Attributes.SAFE_FALL_DISTANCE, "edgestep_landing", 9.0, AttributeModifier.Operation.ADD_VALUE, true);
                CompoundTag t = RelicUtil.tag(p);
                if (t.getBoolean(EDGE_CLEAR)) { t.remove(EDGE_CLEAR); p.getCooldowns().removeCooldown(s.getItem()); }
                int charges = t.contains(EDGE_CHARGES) ? t.getInt(EDGE_CHARGES) : EDGE_MAX;
                long now = RelicUtil.now(p);
                if (charges < EDGE_MAX && t.getLong(EDGE_RECHARGE) <= now) {
                    t.putInt(EDGE_CHARGES, ++charges); t.putLong(EDGE_RECHARGE, now + EDGE_CD);
                    p.getCooldowns().removeCooldown(s.getItem());
                }
            }
            @Override public void onWearerHurt(ServerPlayer p, ItemStack s, LivingIncomingDamageEvent e) {
                if (RelicUtil.until(p, EDGE_IFRAME) && !e.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)) e.setCanceled(true);
            }
            @Override public void onWearerHit(ServerPlayer p, ItemStack s, LivingEntity target, LivingDamageEvent.Pre e) {
                if (!RelicUtil.until(p, EDGE_HIT)) return;
                RelicUtil.clear(p, EDGE_HIT);
                e.setNewDamage(e.getNewDamage() * 1.5F);                           // +50 %
                RelicUtil.burst(p.serverLevel(), RelicUtil.GOLD, target, 10, 0.4, 0.0);
            }
        };
    }

    // ================================================================== Drumpulse (Spark)
    private static final String DRUM_HITS = "drum_hits";

    static RelicPower drumpulse() {
        return new BaseRelic("Drumpulse", "On the Beat: every 4th hit you land deals +2 hearts.",
                "Downbeat: stun every mob within 7 blocks for 2 s and knock them back.", 700) { // 35 s
            @Override public void onWearerHit(ServerPlayer p, ItemStack s, LivingEntity target, LivingDamageEvent.Pre e) {
                CompoundTag t = RelicUtil.tag(p);
                int hits = t.getInt(DRUM_HITS) + 1;
                if (hits >= 4) {
                    hits = 0;
                    e.setNewDamage(e.getNewDamage() + 4.0F);                       // +2 hearts
                    RelicUtil.sound(target, SoundEvents.NOTE_BLOCK_BASEDRUM.value(), 1.2F, 0.7F);
                    RelicUtil.burst(p.serverLevel(), ParticleTypes.CRIT, target, 10, 0.4, 0.15);
                }
                t.putInt(DRUM_HITS, hits);
            }
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                ServerLevel l = p.serverLevel();
                for (LivingEntity m : RelicUtil.mobsAround(p, 7)) {
                    RelicTimers.stun(m, 40);                                       // 2 s (Guardians exempt)
                    m.knockback(1.5, p.getX() - m.getX(), p.getZ() - m.getZ());
                    m.hurtMarked = true;
                }
                Vec3 c = p.position().add(0, 0.3, 0);
                RelicUtil.ring(l, ParticleTypes.FLAME, c, 2.0, 20);
                RelicTimers.later(p, 4, () -> { RelicUtil.ring(l, ParticleTypes.FLAME, c, 4.5, 36); RelicUtil.ring(l, ParticleTypes.LAVA, c, 4.5, 6); });
                RelicTimers.later(p, 8, () -> { RelicUtil.ring(l, ParticleTypes.FLAME, c, 7.0, 48); RelicUtil.ring(l, ParticleTypes.LAVA, c, 7.0, 8); });
                RelicUtil.sound(p, SoundEvents.NOTE_BLOCK_BASEDRUM.value(), 2.0F, 0.5F);
                RelicUtil.sound(p, SoundEvents.GENERIC_EXPLODE.value(), 0.6F, 0.6F);
                return true;
            }
        };
    }

    // ================================================================== Cogloop (Clock)
    static RelicPower cogloop() {
        return new BaseRelic("Cogloop", "Wound Tight: Haste I while worn.",
                "Rewind: reset the cooldown of every other relic you carry, refill Edgestep, and blink back to where you stood 3 s ago.", 1200) { // 60 s
            @Override public void tickWorn(ServerPlayer p, ItemStack s) {
                RelicUtil.passive(p, MobEffects.DIG_SPEED, 0);                  // Haste I
                RelicTimers.recordTrail(p);
            }
            @Override public void onWorn(ServerPlayer p, boolean worn) { if (!worn) RelicTimers.clearTrail(p); }
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                for (ItemStack other : RelicSlots.worn(p)) {
                    if (other.getItem() != s.getItem()) p.getCooldowns().removeCooldown(other.getItem());
                }
                refillEdgestep(p);
                ServerLevel l = p.serverLevel();
                Vec3 from = p.position();
                Vec3 back = RelicTimers.trailBack(p);
                if (back != null && back.distanceToSqr(from) > 0.25) {
                    RelicUtil.burst(l, ParticleTypes.ENCHANT, from.add(0, 1, 0), 20, 0.5, 0.5);
                    p.teleportTo(l, back.x, back.y, back.z, p.getYRot(), p.getXRot());
                    p.setDeltaMovement(Vec3.ZERO); p.fallDistance = 0;
                    RelicUtil.line(l, RelicUtil.TEAL, from.add(0, 1, 0), back.add(0, 1, 0), 16);
                }
                RelicUtil.burst(l, ParticleTypes.ENCHANT, back == null ? from.add(0, 1, 0) : back.add(0, 1, 0), 30, 0.8, 0.8);
                for (int i : new int[]{0, 3, 5, 6, 7}) RelicTimers.later(p, i, () -> RelicUtil.sound(p, SoundEvents.COMPARATOR_CLICK, 0.8F, 1.6F));
                RelicTimers.later(p, 9, () -> RelicUtil.sound(p, SoundEvents.NOTE_BLOCK_CHIME.value(), 1.0F, 1.2F));
                return true;
            }
        };
    }

    // ================================================================== Hivecall (Swarm)
    static RelicPower hivecall() {
        return new BaseRelic("Hivecall", "Keeper: bees never hurt you.",
                "Call the Swarm: four relic-bees for 20 s that harass whatever you hit (Poison I on sting) and pop into a honey bottle each.", 900) { // 45 s
            @Override public void onWearerHurt(ServerPlayer p, ItemStack s, LivingIncomingDamageEvent e) { RelicUtil.beeImmune(e); }
            @Override public void tickWorn(ServerPlayer p, ItemStack s) { RelicUtil.calmBees(p); }
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                ServerLevel l = p.serverLevel();
                for (int i = 0; i < 4; i++) {
                    Bee b = EntityType.BEE.create(l);
                    if (b == null) continue;
                    double a = Math.PI * 2 * i / 4;
                    b.moveTo(p.getX() + Math.cos(a) * 1.5, p.getY() + 1.5, p.getZ() + Math.sin(a) * 1.5, l.random.nextFloat() * 360F, 0F);
                    b.addTag(RelicUtil.BEE_TAG); b.setPersistenceRequired();
                    l.addFreshEntity(b);
                    RelicTimers.bee(b, p.getUUID(), 400);                          // 20 s
                }
                RelicUtil.burst(l, ParticleTypes.FALLING_HONEY, p.position().add(0, 1.5, 0), 20, 0.8, 0.0);
                RelicUtil.burst(l, ParticleTypes.WAX_ON, p.position().add(0, 1.2, 0), 16, 0.7, 0.1);
                RelicUtil.sound(p, SoundEvents.BEEHIVE_WORK, 1.5F, 0.8F);
                RelicUtil.sound(p, SoundEvents.BEE_LOOP_AGGRESSIVE, 1.0F, 1.0F);
                return true;
            }
            @Override public void onWearerHit(ServerPlayer p, ItemStack s, LivingEntity target, LivingDamageEvent.Pre e) {
                if (target instanceof Player) return;
                for (Bee b : RelicTimers.beesOf(p)) {
                    if (b.level() != p.level() || b.distanceToSqr(p) > 24 * 24) continue;
                    b.setTarget(target); b.setPersistentAngerTarget(target.getUUID()); b.setRemainingPersistentAngerTime(400);
                }
            }
        };
    }

    // ================================================================== Sealmark (Sigil)
    static RelicPower sealmark() {
        return new BaseRelic("Sealmark", "Warded: magic damage taken -20 %.",
                "Sealmark: ward yourself (or the mate you look at, within 8 blocks): the next hit of 3 hearts or more is negated. Lasts 20 s.", 1000) { // 50 s
            @Override public void onWearerHurt(ServerPlayer p, ItemStack s, LivingIncomingDamageEvent e) { RelicUtil.magicReduce(e, 0.8F); }
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                ServerPlayer target = RelicUtil.lookedMate(p, 8);
                if (target == null) target = p;
                RelicUtil.setUntil(target, RelicTimers.WARD_KEY, 400);            // 20 s or until spent
                ServerLevel l = p.serverLevel();
                Vec3 c = target.position().add(0, 1, 0);
                RelicUtil.ring(l, ParticleTypes.END_ROD, c, 1.0, 12);
                RelicUtil.ring(l, RelicUtil.TEAL, c.add(0, 0.6, 0), 0.8, 8);
                RelicUtil.ring(l, RelicUtil.TEAL, c.add(0, -0.6, 0), 0.8, 8);
                RelicUtil.sound(target, SoundEvents.AMETHYST_BLOCK_CHIME, 1.2F, 0.8F);
                if (target != p) { RelicUtil.note(p, "Ward placed on " + target.getGameProfile().getName() + "."); RelicUtil.note(target, p.getGameProfile().getName() + " warded you."); }
                else RelicUtil.note(p, "Ward up.");
                return true;
            }
        };
    }

    // ================================================================== Loomthread (Spindle)
    static RelicPower loomthread() {
        return new BaseRelic("Loomthread", "Re-woven: +1 heart max health per two Strands your Clowder has tensioned (up to +4).",
                "Loomthread: reel every Clowder-mate within 24 blocks to your side and give everyone Resistance I for 5 s.", 1800) { // 90 s
            @Override public void tickWorn(ServerPlayer p, ItemStack s) {
                if (p.tickCount % 20 != 0) return;
                // Loom Tension has no max pool or decay in this pack (it is a count of seated Strands), so the passive scales off it instead.
                int hp = Math.min(8, 2 * (LoomTension.tension(p) / 2));           // +2 HP per 2 Strands, cap +8 (4 hearts)
                var inst = p.getAttribute(Attributes.MAX_HEALTH);
                if (inst != null) inst.addOrUpdateTransientModifier(new AttributeModifier(RelicUtil.id("loomthread_rewoven"), hp, AttributeModifier.Operation.ADD_VALUE));
            }
            @Override public void onWorn(ServerPlayer p, boolean worn) {
                if (!worn) RelicUtil.modifier(p, Attributes.MAX_HEALTH, "loomthread_rewoven", 0, AttributeModifier.Operation.ADD_VALUE, false);
            }
            @Override public boolean activate(ServerPlayer p, ItemStack s) {
                ServerLevel l = p.serverLevel();
                RelicUtil.effect(p, MobEffects.DAMAGE_RESISTANCE, 100, 0);       // Resistance I 5 s
                var mates = RelicUtil.mates(p, 24);
                int i = 0;
                for (ServerPlayer m : mates) {
                    double a = Math.PI * 2 * i++ / Math.max(1, mates.size());
                    Vec3 dest = p.position().add(Math.cos(a) * 1.2, 0, Math.sin(a) * 1.2);
                    RelicUtil.line(l, ParticleTypes.END_ROD, m.position().add(0, 1, 0), p.position().add(0, 1, 0), 24);
                    m.teleportTo(l, dest.x, dest.y, dest.z, m.getYRot(), m.getXRot());
                    m.setDeltaMovement(Vec3.ZERO); m.fallDistance = 0;
                    RelicUtil.effect(m, MobEffects.DAMAGE_RESISTANCE, 100, 0);
                    RelicUtil.note(m, p.getGameProfile().getName() + " reels you in.");
                }
                RelicUtil.burst(l, RelicUtil.TEAL, p.position().add(0, 1, 0), 20, 0.8, 0.0);
                RelicUtil.sound(p, SoundEvents.UI_LOOM_TAKE_RESULT, 1.2F, 0.9F);
                return true;
            }
        };
    }

    /** Edgestep charge refill, shared with Cogloop. */
    static void refillEdgestep(ServerPlayer p) {
        CompoundTag t = RelicUtil.tag(p);
        t.putInt(EDGE_CHARGES, EDGE_MAX); t.remove(EDGE_RECHARGE);
    }
}
