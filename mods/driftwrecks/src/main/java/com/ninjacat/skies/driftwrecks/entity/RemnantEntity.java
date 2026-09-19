package com.ninjacat.skies.driftwrecks.entity;

import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.rift.RiftManager;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.LongTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.Bee;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SweetBerryBushBlock;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;

/**
 * A Remnant: a frayed echo of a Strand's Guardian, a quarter of its size, keeping one mechanic from that fight.
 * Bury (Soil), grit (Stone), prune (Sprout), pounce (Claw), beat (Spark), pattern (Clock), drones (Swarm),
 * wards (Sigil); the Spindle's echo quotes pounce, then the beat. It lives in a rift chamber and is tied to it.
 */
public class RemnantEntity extends Monster {
    public static final int CLIP_IDLE = 0, CLIP_WALK = 1, CLIP_ATTACK = 2, CLIP_DEATH = 3;
    private static final EntityDataAccessor<Integer> STRAND = SynchedEntityData.defineId(RemnantEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> CLIP = SynchedEntityData.defineId(RemnantEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> OPEN = SynchedEntityData.defineId(RemnantEntity.class, EntityDataSerializers.BOOLEAN);
    private static final DustParticleOptions TEAL = new DustParticleOptions(new Vector3f(0.24F, 0.85F, 0.8F), 1.6F);
    private static final DustParticleOptions GOLD = new DustParticleOptions(new Vector3f(0.95F, 0.75F, 0.25F), 1.6F);

    private final ServerBossEvent bar = new ServerBossEvent(Component.literal("Remnant"), BossEvent.BossBarColor.BLUE, BossEvent.BossBarOverlay.NOTCHED_10);
    private int riftSlot = -1;
    private BlockPos home = BlockPos.ZERO;
    private long clipStart;
    private int timer, openTicks, phaseStep;
    private boolean charged;
    @Nullable private Vec3 mark;
    private int markTicks;
    private final List<BlockPos> props = new ArrayList<>();   // ward glass, lit tiles, drone cells, the root core
    private int propStep, lastBushes, prunedSince;

    public RemnantEntity(EntityType<? extends RemnantEntity> type, Level level) {
        super(type, level);
        xpReward = 60;
        setPersistenceRequired();
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MAX_HEALTH, 160).add(Attributes.ATTACK_DAMAGE, 8).add(Attributes.ARMOR, 6)
                .add(Attributes.MOVEMENT_SPEED, 0.27).add(Attributes.KNOCKBACK_RESISTANCE, 0.9).add(Attributes.FOLLOW_RANGE, 32);
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder b) {
        super.defineSynchedData(b);
        b.define(STRAND, 0); b.define(CLIP, CLIP_IDLE); b.define(OPEN, false);
    }

    public Strand strand() { return Strand.ALL[Math.floorMod(entityData.get(STRAND), Strand.ALL.length)]; }
    public int clip() { return entityData.get(CLIP); }
    public long clipStart() { return clipStart; }
    public boolean isOpen() { return entityData.get(OPEN); }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        super.onSyncedDataUpdated(key);
        if (CLIP.equals(key)) clipStart = level().getGameTime();
    }

    private void setClip(int c) { if (clip() != c) { entityData.set(CLIP, c); clipStart = level().getGameTime(); } }

    public void setup(Strand s, int slot, BlockPos home, int party) {
        entityData.set(STRAND, s.ordinal());
        this.riftSlot = slot; this.home = home;
        double hp = 160 * (0.6 + 0.4 * Math.max(1, party));
        getAttribute(Attributes.MAX_HEALTH).setBaseValue(hp);
        setHealth((float) hp);
        styleBar(s);
        entityData.set(OPEN, !immuneByDefault());
    }

    private void styleBar(Strand s) {
        bar.setName(Component.translatable("entity.driftwrecks.remnant." + s.id()));
        bar.setColor(switch (s) { case SOIL, SPROUT -> BossEvent.BossBarColor.GREEN; case SPARK, SWARM, CLOCK -> BossEvent.BossBarColor.YELLOW; case SIGIL -> BossEvent.BossBarColor.PURPLE; default -> BossEvent.BossBarColor.BLUE; });
    }

    @Override
    protected void registerGoals() {
        goalSelector.addGoal(0, new FloatGoal(this));
        goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.0, true) {
            @Override public boolean canUse() { return strand() != Strand.SPROUT && super.canUse(); }
        });
        goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 16F));
        targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Player.class, true));
    }

    // ------------------------------------------------------------------ vulnerability

    private boolean immuneByDefault() {
        return switch (strand()) { case SOIL, STONE, SPARK, CLOCK, SWARM, SIGIL -> true; default -> false; };
    }

    private void open(int ticks, String line) {
        openTicks = ticks;
        entityData.set(OPEN, true);
        say(line);
        playSound(SoundEvents.ZOMBIE_BREAK_WOODEN_DOOR, 1.5F, 0.6F);
    }

    @Override
    public boolean hurt(DamageSource src, float amount) {
        if (level().isClientSide) return false;
        if (src.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY)) return super.hurt(src, amount);
        if (!isOpen()) {
            if (src.getEntity() instanceof Player && tickCount % 4 == 0) playSound(SoundEvents.SHIELD_BLOCK, 1.0F, 0.6F);
            return false;
        }
        if (charged && src.getEntity() instanceof Player) { amount *= 3; charged = false; }
        if (strand() == Strand.SPROUT && openTicks > 0) amount *= 2;
        return super.hurt(src, amount);
    }

    // ------------------------------------------------------------------ tick

    @Override
    public void tick() {
        super.tick();
        // while closed (immune) it sheds teal motes
        if (level().isClientSide && !isOpen() && tickCount % 3 == 0)
            level().addParticle(ParticleTypes.GLOW, getRandomX(0.8), getY() + getBbHeight() * random.nextFloat(), getRandomZ(0.8), 0, 0.02, 0);
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        ServerLevel sl = (ServerLevel) level();
        bar.setProgress(getHealth() / getMaxHealth());
        setClip(getDeltaMovement().horizontalDistanceSqr() > 1e-4 ? CLIP_WALK : getTarget() != null && distanceToSqr(getTarget()) < 12 ? CLIP_ATTACK : CLIP_IDLE);
        if (openTicks > 0 && --openTicks == 0 && immuneByDefault()) { entityData.set(OPEN, false); say("It closes again."); }
        if (home.distToCenterSqr(position()) > 12 * 12) { teleportTo(home.getX() + 0.5, home.getY(), home.getZ() + 0.5); getNavigation().stop(); }
        timer++;
        switch (strand()) {
            case SOIL -> bury(sl);
            case STONE -> grit(sl);
            case SPROUT -> prune(sl);
            case CLAW -> pounce(sl, 100);
            case SPARK -> beat(sl);
            case CLOCK -> pattern(sl);
            case SWARM -> drones(sl);
            case SIGIL -> wards(sl);
            case SPINDLE -> { if (getHealth() > getMaxHealth() / 2) pounce(sl, 80); else beat(sl); }
        }
    }

    /** Soil: slam, then a root core glows under one of four seams; break it to end the burial. */
    private void bury(ServerLevel sl) {
        if (props.isEmpty() && !isOpen() && timer > 60) {
            slam(sl, 5, 6);
            int k = random.nextInt(4);
            BlockPos seam = home.offset(new int[]{7, -7, 0, 0}[k], -1, new int[]{0, 0, 7, -7}[k]);
            sl.setBlock(seam, Blocks.VERDANT_FROGLIGHT.defaultBlockState(), 3);
            sl.setBlock(seam.above(), Blocks.ROOTED_DIRT.defaultBlockState(), 3);
            props.add(seam);
            say("It buries itself. A root-seam glows—dig.");
        }
        if (!props.isEmpty()) {
            BlockPos core = props.get(0);
            sl.sendParticles(TEAL, core.getX() + 0.5, core.getY() + 2.2, core.getZ() + 0.5, 3, 0.2, 0.4, 0.2, 0);
            if (!sl.getBlockState(core).is(Blocks.VERDANT_FROGLIGHT)) { props.clear(); timer = 0; open(160, "The root core breaks. It is exposed!"); }
        }
    }

    /** Stone: grit falls; a gravel stack dropped beside it jams the maw open. */
    private void grit(ServerLevel sl) {
        if (timer % 200 == 0) {
            Player p = sl.getNearestPlayer(this, 24);
            Vec3 at = p != null ? p.position().add(0, 3, 0) : position().add(4, 3, 0);
            ItemEntity grit = new ItemEntity(sl, at.x, at.y, at.z, new ItemStack(Items.GRAVEL));
            grit.setPickUpDelay(10);
            sl.addFreshEntity(grit);
            say("Grit falls from the seam. Feed it to the maw.");
        }
        if (!isOpen() && timer % 10 == 0) {
            List<ItemEntity> near = sl.getEntitiesOfClass(ItemEntity.class, getBoundingBox().inflate(1.5), e -> e.getItem().is(Items.GRAVEL));
            if (!near.isEmpty()) { near.get(0).getItem().shrink(1); if (near.get(0).getItem().isEmpty()) near.get(0).discard(); open(160, "Grit jams the maw open!"); }
        }
    }

    /** Sprout: never strikes; seeds thorns. Overgrowth heals it; cutting five hedges stuns it. */
    private void prune(ServerLevel sl) {
        if (timer % 120 == 0) {
            Player p = sl.getNearestPlayer(this, 24);
            if (p != null) {
                BlockPos at = BlockPos.containing(p.getX() + random.nextInt(5) - 2, home.getY(), p.getZ() + random.nextInt(5) - 2);
                if (sl.getBlockState(at).isAir() && sl.getBlockState(at.below()).isSolid()) sl.setBlock(at, Blocks.SWEET_BERRY_BUSH.defaultBlockState().setValue(SweetBerryBushBlock.AGE, 3), 3);
            }
        }
        if (timer % 20 == 0) {
            int bushes = 0;
            for (BlockPos b : BlockPos.betweenClosed(home.offset(-11, 0, -11), home.offset(11, 1, 11))) if (sl.getBlockState(b).is(Blocks.SWEET_BERRY_BUSH)) bushes++;
            if (bushes < lastBushes) prunedSince += lastBushes - bushes;
            lastBushes = bushes;
            if (bushes >= 6 && timer % 200 == 0) { heal(getMaxHealth() * 0.05F); say("The thicket feeds it."); }
            if (prunedSince >= 5) { prunedSince = 0; openTicks = 80; getNavigation().stop(); say("Pruned back—it reels!"); }
        }
    }

    /** Claw: a gold claw-mark, 0.7 s, then the pounce lands there. */
    private void pounce(ServerLevel sl, int every) {
        if (mark == null && timer % every == 0) {
            Player p = getTarget() instanceof Player t ? t : sl.getNearestPlayer(this, 24);
            if (p != null) { mark = p.position(); markTicks = 0; }
        }
        if (mark != null) {
            markTicks++;
            ring(sl, GOLD, mark, 3, 16);
            if (markTicks >= 14) {
                teleportTo(mark.x, mark.y, mark.z);
                slam(sl, 3, 8);
                mark = null;
            }
        }
    }

    /** Spark: a four-beat loop; open only just after beat four; the downbeat sends a shockwave. */
    private void beat(ServerLevel sl) {
        int b = (timer / 10) % 4;
        if (timer % 10 == 0) {
            sl.playSound(null, blockPosition(), SoundEvents.NOTE_BLOCK_BASEDRUM.value(), SoundSource.HOSTILE, 2.0F, b == 3 ? 0.5F : 0.8F);
            if (b == 3) { slam(sl, 4, 4); openTicks = 12; entityData.set(OPEN, true); }
        }
        if (strand() == Strand.SPINDLE && openTicks == 0 && !isOpen()) entityData.set(OPEN, true);
    }

    /** Clock: three tiles light in order; step on them in that order within 12 s to open the chassis. */
    private void pattern(ServerLevel sl) {
        if (props.isEmpty() && !isOpen() && timer > 40) {
            List<Integer> pick = new ArrayList<>(List.of(0, 1, 2, 3, 4, 5, 6, 7));
            java.util.Collections.shuffle(pick, new java.util.Random(random.nextLong()));
            for (int i = 0; i < 3; i++) {
                double a = Math.PI / 4 * pick.get(i);
                props.add(home.offset((int) Math.round(Math.cos(a) * 6), -1, (int) Math.round(Math.sin(a) * 6)));
            }
            propStep = 0; timer = 0;
            for (int i = 0; i < props.size(); i++) {
                BlockPos t = props.get(i);
                int delay = i * 20;
                com.ninjacat.skies.driftwrecks.Later.run(sl.getServer(), delay, () -> {
                    sl.setBlock(t, Blocks.OCHRE_FROGLIGHT.defaultBlockState(), 3);
                    sl.playSound(null, t, SoundEvents.NOTE_BLOCK_CHIME.value(), SoundSource.HOSTILE, 1.5F, 1.0F);
                });
            }
            say("It winds. Watch, then step.");
        }
        if (props.isEmpty()) return;
        BlockPos want = props.get(propStep);
        for (ServerPlayer p : sl.getEntitiesOfClass(ServerPlayer.class, new AABB(home).inflate(12))) {
            if (p.blockPosition().below().equals(want) && timer > 60) {
                sl.setBlock(want, floor(sl), 3);
                propStep++;
                sl.playSound(null, want, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 1.2F, 0.8F + 0.2F * propStep);
                if (propStep >= props.size()) { props.clear(); open(160, "The pattern holds. The chassis opens!"); }
                return;
            }
        }
        if (timer > 60 + 240) {
            for (BlockPos t : props) sl.setBlock(t, floor(sl), 3);
            props.clear();
            for (ServerPlayer p : sl.getEntitiesOfClass(ServerPlayer.class, new AABB(home).inflate(12))) p.hurt(damageSources().magic(), 6);
            say("Out of pattern. The gears bite.");
            timer = 0;
        }
    }

    /** Swarm: immune until its three drone cells are broken; open cells pour drones. */
    private void drones(ServerLevel sl) {
        if (props.isEmpty() && !isOpen()) {
            for (int i = 0; i < 3; i++) {
                double a = Math.PI * 2 / 3 * i + 0.4;
                BlockPos c = home.offset((int) Math.round(Math.cos(a) * 10), 1, (int) Math.round(Math.sin(a) * 10));
                sl.setBlock(c, Blocks.BEE_NEST.defaultBlockState(), 3);
                props.add(c);
            }
            say("Drone cells knit into the walls. Break them.");
        }
        if (props.isEmpty()) return;
        props.removeIf(c -> !sl.getBlockState(c).is(Blocks.BEE_NEST));
        if (props.isEmpty()) { open(200, "The last cell falls. The queen is bare!"); return; }
        if (timer % 160 == 0) {
            int bees = sl.getEntitiesOfClass(Bee.class, new AABB(home).inflate(14)).size();
            for (BlockPos c : props) if (bees++ < 6) {
                Bee bee = EntityType.BEE.create(sl);
                if (bee == null) continue;
                bee.moveTo(c.getX() + 0.5, c.getY() + 1, c.getZ() + 0.5, 0, 0);
                Player p = sl.getNearestPlayer(this, 24);
                if (p != null) { bee.setRemainingPersistentAngerTime(400); bee.setPersistentAngerTarget(p.getUUID()); bee.setTarget(p); }
                bee.finalizeSpawn(sl, sl.getCurrentDifficultyAt(c), MobSpawnType.EVENT, null);
                sl.addFreshEntity(bee);
            }
        }
    }

    /** Sigil: three ward-glass seals, shown in order; break them in that order to expose it. */
    private void wards(ServerLevel sl) {
        if (props.isEmpty() && !isOpen()) {
            for (int i = 0; i < 3; i++) {
                double a = Math.PI * 2 / 5 * (i * 2 % 5) + 0.3;
                BlockPos g = home.offset((int) Math.round(Math.cos(a) * 8), 0, (int) Math.round(Math.sin(a) * 8));
                sl.setBlock(g, Blocks.PURPLE_STAINED_GLASS.defaultBlockState(), 3);
                props.add(g);
            }
            java.util.Collections.shuffle(props, new java.util.Random(random.nextLong()));
            propStep = 0; timer = 0;
        }
        if (props.isEmpty()) return;
        if (timer % 300 == 1) for (int i = 0; i < props.size(); i++) {
            BlockPos g = props.get(i);
            int delay = i * 20;
            com.ninjacat.skies.driftwrecks.Later.run(sl.getServer(), delay, () -> {
                sl.sendParticles(TEAL, g.getX() + 0.5, g.getY() + 1.5, g.getZ() + 0.5, 30, 0.2, 0.8, 0.2, 0);
                sl.playSound(null, g, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.HOSTILE, 1.5F, 0.7F);
            });
        }
        for (int i = propStep; i < props.size(); i++) {
            BlockPos g = props.get(i);
            if (sl.getBlockState(g).is(Blocks.PURPLE_STAINED_GLASS)) continue;
            if (i == propStep) {
                propStep++;
                if (propStep >= props.size()) { props.clear(); open(200, "The last ward breaks. It stands exposed!"); }
            } else {
                for (BlockPos r : props) sl.setBlock(r, Blocks.PURPLE_STAINED_GLASS.defaultBlockState(), 3);
                propStep = 0;
                for (ServerPlayer p : sl.getEntitiesOfClass(ServerPlayer.class, new AABB(home).inflate(12))) p.hurt(damageSources().magic(), 4);
                say("Wrong seal. The wards re-arm.");
            }
            return;
        }
    }

    // ------------------------------------------------------------------ helpers

    private net.minecraft.world.level.block.state.BlockState floor(ServerLevel sl) {
        return com.ninjacat.skies.driftwrecks.wreck.StrandSkin.resolve(strand(), "floor");
    }

    private void slam(ServerLevel sl, double r, float dmg) {
        sl.sendParticles(ParticleTypes.EXPLOSION, getX(), getY() + 0.2, getZ(), 3, r / 3, 0.1, r / 3, 0);
        sl.playSound(null, blockPosition(), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.HOSTILE, 1.4F, 0.6F);
        for (ServerPlayer p : sl.getEntitiesOfClass(ServerPlayer.class, getBoundingBox().inflate(r, 2, r))) {
            p.hurt(damageSources().mobAttack(this), dmg);
            Vec3 k = p.position().subtract(position()).normalize().scale(0.8);
            p.push(k.x, 0.4, k.z);
            p.hurtMarked = true;
        }
    }

    private static void ring(ServerLevel sl, DustParticleOptions o, Vec3 c, double r, int n) {
        for (int i = 0; i < n; i++) {
            double a = Math.PI * 2 * i / n;
            sl.sendParticles(o, c.x + Math.cos(a) * r, c.y + 0.15, c.z + Math.sin(a) * r, 1, 0, 0, 0, 0);
        }
    }

    private void say(String line) {
        if (level() instanceof ServerLevel sl)
            for (ServerPlayer p : sl.getEntitiesOfClass(ServerPlayer.class, new AABB(home).inflate(16))) p.displayClientMessage(com.ninjacat.skies.lib.NinjacatText.teal(line), true);
    }

    @Override public void startSeenByPlayer(ServerPlayer p) { super.startSeenByPlayer(p); bar.addPlayer(p); }
    @Override public void stopSeenByPlayer(ServerPlayer p) { super.stopSeenByPlayer(p); bar.removePlayer(p); }
    @Override public boolean removeWhenFarAway(double d) { return false; }
    @Override public boolean canChangeDimensions(Level from, Level to) { return false; }

    @Override
    public void die(DamageSource src) {
        super.die(src);
        if (level() instanceof ServerLevel sl) {
            for (BlockPos p : props) if (!sl.getBlockState(p).isAir()) sl.setBlock(p, floor(sl), 3);
            props.clear();
            RiftManager.onRemnantDeath(sl, riftSlot);
        }
        setClip(CLIP_DEATH);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("Strand", entityData.get(STRAND)); tag.putInt("Rift", riftSlot); tag.putLong("Home", home.asLong());
        tag.putInt("Timer", timer); tag.putInt("Open", openTicks); tag.putInt("Step", propStep);
        ListTag l = new ListTag(); for (BlockPos p : props) l.add(LongTag.valueOf(p.asLong())); tag.put("Props", l);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        entityData.set(STRAND, tag.getInt("Strand")); riftSlot = tag.getInt("Rift"); home = BlockPos.of(tag.getLong("Home"));
        timer = tag.getInt("Timer"); openTicks = tag.getInt("Open"); propStep = tag.getInt("Step");
        props.clear(); for (Tag t : tag.getList("Props", Tag.TAG_LONG)) props.add(BlockPos.of(((LongTag) t).getAsLong()));
        entityData.set(OPEN, !immuneByDefault() || openTicks > 0);
        styleBar(strand());                                  // a reloaded Remnant keeps its own name and colour
        if (hasCustomName()) bar.setName(getDisplayName());
    }

    public int riftSlot() { return riftSlot; }
}
