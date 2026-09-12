package com.ninjacat.skies.guardians.entity;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.Guardians;
import com.ninjacat.skies.guardians.arena.ArenaInstance;
import com.ninjacat.skies.guardians.arena.ArenaManager;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Base of every Snapped Guardian. Owns the boss bar, the animation clip state the client renderer plays,
 * phase changes, immunity, the melee cycle and the link to its arena. Subclasses implement the fight
 * (see ARENAS.md): {@link #tickMechanic()}, {@link #onPhase(int)}, {@link #onMeleeHit(LivingEntity)}.
 * <p>
 * Clips: 0 idle (loop), 1 walk (loop), 2 attack (one-shot), 3 death (one-shot). Frame lengths are read
 * from the model on the client; the server only tracks which clip started when.
 */
public abstract class GuardianEntity extends Monster {
    public static final int CLIP_IDLE = 0, CLIP_WALK = 1, CLIP_ATTACK = 2, CLIP_DEATH = 3;
    private static final EntityDataAccessor<Integer> CLIP = SynchedEntityData.defineId(GuardianEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> CLIP_START = SynchedEntityData.defineId(GuardianEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> IMMUNE = SynchedEntityData.defineId(GuardianEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> PHASE = SynchedEntityData.defineId(GuardianEntity.class, EntityDataSerializers.INT);
    /** frames of the one-shot clips at 24 fps (attack 40, death 48) expressed in ticks */
    public static final int ATTACK_TICKS = 34, ATTACK_HIT_TICK = 14, DEATH_TICKS = 40;

    public final GuardianKind kind;
    private final ServerBossEvent bossEvent;
    private int lastClang = -100;
    protected int arenaSlot = -1;
    @Nullable protected UUID partyId;
    protected int attackCooldown = 0, attackTimer = -1, deathTimer = -1, ageInFight = 0;
    private int lastPhase = 0;
    protected final List<BlockPos> tempBlocks = new ArrayList<>();

    protected GuardianEntity(EntityType<? extends GuardianEntity> type, Level level, GuardianKind kind) {
        super(type, level);
        this.kind = kind;
        this.bossEvent = new ServerBossEvent(Component.literal(kind.title), kind.tier == GuardianKind.Tier.INSANE ? BossEvent.BossBarColor.PURPLE : BossEvent.BossBarColor.BLUE, BossEvent.BossBarOverlay.NOTCHED_10);
        this.bossEvent.setDarkenScreen(kind.tier == GuardianKind.Tier.INSANE);
        this.setPersistenceRequired();
        this.xpReward = 60;
        this.noCulling = true;
    }

    public static AttributeSupplier.Builder attributes(GuardianKind k) {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, k.baseHealth)
                .add(Attributes.ATTACK_DAMAGE, k.attackDamage)
                .add(Attributes.MOVEMENT_SPEED, k == GuardianKind.EDGEWALKER ? 0.42 : 0.24)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0)
                .add(Attributes.FOLLOW_RANGE, 96.0)
                .add(Attributes.STEP_HEIGHT, 2.0)
                .add(Attributes.ARMOR, 4.0);
    }

    /** A guardian never suffocates in its own stage (the Unwoven stands in its warp curtain, the Edgewalker in tuff). */
    @Override public boolean isInWall() { return false; }
    /** Bosses this size make the walk-node evaluator scan width×height×depth blocks per node; cap the search so a stuck Tangle or a Beddown chasing a kiting player cannot eat the tick. */
    @Override protected PathNavigation createNavigation(Level level) { PathNavigation nav = super.createNavigation(level); nav.setMaxVisitedNodesMultiplier(0.25F); return nav; }

    // ------------------------------------------------------------------ synched state
    @Override
    protected void defineSynchedData(SynchedEntityData.Builder b) {
        super.defineSynchedData(b);
        b.define(CLIP, CLIP_IDLE); b.define(CLIP_START, 0); b.define(IMMUNE, false); b.define(PHASE, 0);
    }
    public int clip() { return entityData.get(CLIP); }
    public int clipStart() { return entityData.get(CLIP_START); }
    public boolean isImmune() { return entityData.get(IMMUNE); }
    public int phase() { return entityData.get(PHASE); }
    public void setImmune(boolean v) { entityData.set(IMMUNE, v); }
    /** Start a clip now; looping clips keep their phase if already playing. */
    public void playClip(int clip) {
        if (clip() == clip && (clip == CLIP_IDLE || clip == CLIP_WALK)) return;
        entityData.set(CLIP, clip); entityData.set(CLIP_START, (int) level().getGameTime());
    }

    // ------------------------------------------------------------------ arena link
    public void bindArena(int slot, @Nullable UUID party) { this.arenaSlot = slot; this.partyId = party; }
    public int arenaSlot() { return arenaSlot; }
    @Nullable public UUID partyId() { return partyId; }
    @Nullable
    public ArenaInstance arena() {
        return level() instanceof ServerLevel sl && arenaSlot >= 0 ? ArenaManager.get(sl.getServer()).instance(arenaSlot) : null;
    }
    /** The players this guardian is fighting: the arena's party if bound, else any survival players nearby. */
    public List<ServerPlayer> party() {
        List<ServerPlayer> out = new ArrayList<>();
        ArenaInstance a = arena();
        if (a != null) { out.addAll(a.onlinePlayers()); return out; }
        if (level() instanceof ServerLevel sl) for (ServerPlayer p : sl.players()) if (!p.isSpectator() && !p.isCreative() && p.distanceTo(this) < 96) out.add(p);
        return out;
    }
    public Vec3 origin() { ArenaInstance a = arena(); return a != null ? a.origin() : position(); }
    public int partySize() { ArenaInstance a = arena(); return a != null ? Math.max(1, a.partySize()) : Math.max(1, party().size()); }

    // ------------------------------------------------------------------ fight hooks
    /** Called every server tick while alive (after the melee cycle). Implement the arena mechanic here. */
    protected abstract void tickMechanic();
    /** Called once when the health-quarter phase changes: 1 = below 75 %, 2 = below 50 %, 3 = below 25 %. */
    protected void onPhase(int phase) {}
    /** Melee connect on a target in reach at the hit frame of the attack clip. */
    protected void onMeleeHit(LivingEntity target) {
        target.hurt(damageSources().mobAttack(this), (float) getAttributeValue(Attributes.ATTACK_DAMAGE));
        Vec3 push = target.position().subtract(position()).normalize().scale(1.2);
        target.push(push.x, 0.45, push.z);
    }
    protected double meleeReach() { return kind.width * 0.75 + 2.5; }
    protected int meleeCooldown() { return 50; }
    /** Whether the guardian walks toward its target between attacks (rooted bosses return false). */
    protected boolean mobile() { return true; }
    protected SoundEvent hurtSoundOverride() { return SoundEvents.STONE_HIT; }

    // ------------------------------------------------------------------ tick
    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) return;
        ServerLevel sl = (ServerLevel) level();
        if (deathTimer >= 0) { tickDying(sl); return; }
        ageInFight++;
        bossEvent.setProgress(getHealth() / getMaxHealth());
        if (showsBossBar()) { for (ServerPlayer p : party()) bossEvent.addPlayer(p); } else if (!bossEvent.getPlayers().isEmpty()) bossEvent.removeAllPlayers();
        int ph = getHealth() <= getMaxHealth()*0.25F ? 3 : getHealth() <= getMaxHealth()*0.5F ? 2 : getHealth() <= getMaxHealth()*0.75F ? 1 : 0;
        if (ph != lastPhase) { lastPhase = ph; entityData.set(PHASE, ph); onPhase(ph); }
        tickMelee(sl);
        tickMechanic();
    }

    protected void tickMelee(ServerLevel sl) {
        LivingEntity t = getTarget();
        if (t == null || !t.isAlive() || t.distanceTo(this) > 96 || (t instanceof Player p && (p.isSpectator() || p.isCreative()))) {
            ServerPlayer near = nearestParty(); setTarget(near); t = near;
        }
        if (attackTimer >= 0) {
            attackTimer++;
            if (attackTimer == ATTACK_HIT_TICK && t != null && distanceTo(t) <= meleeReach() + 1.5) onMeleeHit(t);
            if (attackTimer >= ATTACK_TICKS) { attackTimer = -1; playClip(CLIP_IDLE); }
            getNavigation().stop();
            return;
        }
        if (attackCooldown > 0) attackCooldown--;
        if (t == null) { playClip(CLIP_IDLE); return; }
        getLookControl().setLookAt(t, 30, 30);
        double d = distanceTo(t);
        if (d <= meleeReach()) {
            getNavigation().stop();
            if (attackCooldown == 0) { attackTimer = 0; attackCooldown = meleeCooldown(); playClip(CLIP_ATTACK); playSound(SoundEvents.RAVAGER_ROAR, 1.4F, 0.5F); }
            else playClip(CLIP_IDLE);
        } else if (mobile()) {
            if (tickCount % 10 == 0) getNavigation().moveTo(t, 1.0);
            playClip(getNavigation().isInProgress() || getDeltaMovement().horizontalDistanceSqr() > 0.01 ? CLIP_WALK : CLIP_IDLE);
        } else playClip(CLIP_IDLE);
    }

    @Nullable
    public ServerPlayer nearestParty() {
        ServerPlayer best = null; double bd = Double.MAX_VALUE;
        for (ServerPlayer p : party()) { if (!p.isAlive()) continue; double d = p.distanceToSqr(this); if (d < bd) { bd = d; best = p; } }
        return best;
    }

    // ------------------------------------------------------------------ damage / death
    @Override
    public boolean hurt(DamageSource src, float amount) {
        if (level().isClientSide) return false;
        if (deathTimer >= 0) return false;
        if (src.is(net.minecraft.tags.DamageTypeTags.IS_FALL) || src.is(net.minecraft.tags.DamageTypeTags.IS_DROWNING) || src.is(net.minecraft.tags.DamageTypeTags.IS_FIRE)) return false;
        if (src.is(net.minecraft.tags.DamageTypeTags.IS_FALL) || src.is(net.minecraft.world.damagesource.DamageTypes.IN_WALL) || src.is(net.minecraft.world.damagesource.DamageTypes.CRAMMING)) return false;
        if (isImmune() && !src.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            if (src.getEntity() != null) {                                       // a real blow: tell the striker (throttled) and clang
                if (src.getEntity() instanceof ServerPlayer p && p.tickCount % 10 == 0) p.displayClientMessage(NinjacatText.teal(immuneMessage()), true);
                if (tickCount - lastClang >= 5) { lastClang = tickCount; level().playSound(null, blockPosition(), SoundEvents.SHIELD_BLOCK, SoundSource.HOSTILE, 1.0F, 0.6F); }
            }
            return false;
        }
        boolean ok = super.hurt(src, amount);
        if (ok && src.getEntity() instanceof LivingEntity le) onDamagedBy(le, amount);
        return ok;
    }
    protected String immuneMessage() { return kind.title + " cannot be harmed right now."; }
    protected void onDamagedBy(LivingEntity by, float amount) {}

    @Override
    public void die(DamageSource src) {
        if (deathTimer >= 0) return;
        deathTimer = 0; setHealth(1.0F); setImmune(true);
        playClip(CLIP_DEATH); getNavigation().stop(); setTarget(null);
        level().playSound(null, blockPosition(), SoundEvents.WITHER_DEATH, SoundSource.HOSTILE, 2.0F, 0.55F);
        onDefeated();
    }
    /** Override to clean the arena (revert blocks) — called once at the start of the death clip. */
    protected void onDefeated() { revertTempBlocks(); }
    /** The fight ended without a death (wipe, leave, restart): the same cleanup the death clip would have run. */
    public void cleanupArena() { onDefeated(); }
    private void tickDying(ServerLevel sl) {
        deathTimer++;
        bossEvent.setProgress(0);
        if (deathTimer == 8 && arena() != null && getUUID().equals(arena().boss)) ArenaManager.get(sl.getServer()).onWin(arena(), this);   // shades never end the fight
        if (deathTimer >= DEATH_TICKS + 20) { bossEvent.removeAllPlayers(); remove(RemovalReason.KILLED); }
    }
    @Override protected void tickDeath() {}
    @Override public void remove(RemovalReason r) { bossEvent.removeAllPlayers(); super.remove(r); }
    @Override public void checkDespawn() {}
    @Override public boolean removeWhenFarAway(double d) { return false; }
    @Override public boolean isPushable() { return false; }
    @Override protected void doPush(Entity e) {}
    @Override public boolean canBeLeashed() { return false; }
    @Override public boolean fireImmune() { return true; }
    @Override public boolean canChangeDimensions(Level from, Level to) { return false; }
    @Override protected SoundEvent getHurtSound(DamageSource s) { return hurtSoundOverride(); }
    @Override protected SoundEvent getDeathSound() { return SoundEvents.WITHER_DEATH; }
    @Override public boolean addEffect(MobEffectInstance e, @Nullable Entity src) { return false; }   // no potion cheese
    @Override protected boolean canRide(Entity e) { return false; }
    @Override public boolean isSteppingCarefully() { return false; }
    @Override protected void dropCustomDeathLoot(ServerLevel l, DamageSource s, boolean b) {}     // relics are given by the arena, team-fair

    // ------------------------------------------------------------------ persistence
    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("ArenaSlot", arenaSlot); if (partyId != null) tag.putUUID("Party", partyId);
        tag.putInt("FightAge", ageInFight);
        ListTag temps = new ListTag();
        for (BlockPos p : tempBlocks) {
            CompoundTag c = new CompoundTag();
            c.putInt("x", p.getX()); c.putInt("y", p.getY()); c.putInt("z", p.getZ());
            temps.add(c);
        }
        tag.put("TempBlocks", temps);
    }
    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        arenaSlot = tag.getInt("ArenaSlot"); partyId = tag.hasUUID("Party") ? tag.getUUID("Party") : null; ageInFight = tag.getInt("FightAge");
        tempBlocks.clear();
        for (Tag t : tag.getList("TempBlocks", Tag.TAG_COMPOUND)) {
            CompoundTag c = (CompoundTag) t;
            tempBlocks.add(new BlockPos(c.getInt("x"), c.getInt("y"), c.getInt("z")));
        }
        if (hasCustomName()) bossEvent.setName(getDisplayName());
    }
    @Override public void setCustomName(@Nullable Component name) { super.setCustomName(name); bossEvent.setName(getDisplayName()); }
    /** Additive spawns (the Overweaver's shades, tagged {@code guardians_add}) fight without a boss bar of their own. */
    public boolean showsBossBar() { return !getTags().contains("guardians_add"); }
    @Override public void startSeenByPlayer(ServerPlayer p) { super.startSeenByPlayer(p); if (showsBossBar()) bossEvent.addPlayer(p); }
    @Override public void stopSeenByPlayer(ServerPlayer p) { super.stopSeenByPlayer(p); bossEvent.removePlayer(p); }

    // ------------------------------------------------------------------ helpers for mechanics
    protected ServerLevel serverLevel() { return (ServerLevel) level(); }
    protected void say(String line) { for (ServerPlayer p : party()) p.displayClientMessage(NinjacatText.gold(line), true); }
    protected void shout(String line) { for (ServerPlayer p : party()) p.sendSystemMessage(NinjacatText.teal(line)); }
    protected void particles(ParticleOptions type, Vec3 at, int n, double spread, double speed) { serverLevel().sendParticles(type, at.x, at.y, at.z, n, spread, spread*0.5, spread, speed); }
    protected void ring(ParticleOptions type, Vec3 c, double r, int n, double y) {
        for (int i = 0; i < n; i++) { double a = Math.PI*2*i/n; serverLevel().sendParticles(type, c.x + Math.cos(a)*r, y, c.z + Math.sin(a)*r, 1, 0, 0, 0, 0); }
    }
    /** Damage every party member inside the radius (no self, no immune players). */
    protected void areaDamage(Vec3 c, double r, float amount, double knock) {
        for (ServerPlayer p : party()) {
            if (p.distanceToSqr(c) > r*r || !p.isAlive()) continue;
            p.hurt(damageSources().mobAttack(this), amount);
            if (knock > 0) { Vec3 d = p.position().subtract(c); d = d.lengthSqr() < 1e-4 ? new Vec3(0, 1, 0) : d.normalize(); p.push(d.x*knock, 0.35*knock, d.z*knock); p.hurtMarked = true; }
        }
    }
    protected void sound(SoundEvent s, float vol, float pitch) { level().playSound(null, blockPosition(), s, SoundSource.HOSTILE, vol, pitch); }
    /** Place a block the mechanic owns; it is restored to air when the guardian is defeated or the arena is wiped. */
    protected void placeTemp(BlockPos pos, BlockState state) {
        if (serverLevel().getBlockState(pos).isAir() || tempBlocks.contains(pos)) { serverLevel().setBlock(pos, state, 3); if (!tempBlocks.contains(pos)) tempBlocks.add(pos); }
    }
    public void revertTempBlocks() {
        for (BlockPos p : tempBlocks) if (level().isLoaded(p)) level().setBlock(p, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), 3);
        tempBlocks.clear();
    }
    protected AABB arenaBox(double r, double h) { Vec3 o = origin(); return new AABB(o.x - r, o.y - 2, o.z - r, o.x + r, o.y + h, o.z + r); }
    protected boolean chance(double p) { return random.nextDouble() < p; }
    protected static Vec3 v(BlockPos p) { return Vec3.atCenterOf(p); }
}
