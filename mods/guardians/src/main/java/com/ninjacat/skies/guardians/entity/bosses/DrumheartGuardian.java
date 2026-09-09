package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Spark · the Drumheart — ON THE BEAT. A 120 BPM four-beat loop (+10 BPM per phase). Hammers on r 17 slam in
 * turn on beats 1–3 and all together on beat 4; the boss is vulnerable only for 0.6 s after beat 4. Standing on a
 * beat pad (r 14, in front of each hammer) on the downbeat charges a spark: the next hit lands ×3. On beat 4 the
 * four diagonal lava channels rise to floor level for 1 s.
 */
public class DrumheartGuardian extends GuardianEntity {
    private static final int HAMMER_R = 17, PAD_R = 14, OPEN_TICKS = 12, SPARK_TICKS = 120, LAVA_TICKS = 20;
    private final Map<UUID, Integer> spark = new HashMap<>();
    private final List<BlockPos> lava = new ArrayList<>();
    private double beatClock = 0; private int beat = 0, open = 0, lavaTimer = 0;

    public DrumheartGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.DRUMHEART); }

    @Override protected boolean mobile() { return false; }
    @Override protected String immuneMessage() { return "The Drumheart only opens on its fourth beat. Strike on the downbeat."; }
    private double bpm() { return 120 + 10 * phase(); }

    @Override
    public boolean hurt(DamageSource src, float amount) {
        if (!isImmune() && src.getEntity() instanceof ServerPlayer p && spark.getOrDefault(p.getUUID(), 0) > tickCount) {
            spark.remove(p.getUUID()); amount *= 3;
            p.displayClientMessage(NinjacatText.gold("Spark strike! ×3"), true); sound(SoundEvents.LIGHTNING_BOLT_IMPACT, 1.2F, 1.4F);
            Mech.burst(serverLevel(), ParticleTypes.ELECTRIC_SPARK, position().add(0, kind.height * 0.5, 0), 40, 3);
        }
        return super.hurt(src, amount);
    }

    @Override
    protected void tickMechanic() {
        if (ageInFight == 1) shout("The Drumheart answers for the Cut. Listen: three beats, then the downbeat. It opens only on the fourth. Stand on an amber pad as the fourth beat lands to charge a spark, and mind the hammers and the lava lines.");
        Vec3 o = origin();
        beatClock += 1; double interval = 1200.0 / bpm();
        if (beatClock >= interval) { beatClock -= interval; beat = beat % 4 + 1; onBeat(o); }
        else if (beatClock >= interval - 8 && tickCount % 2 == 0) warnNext(o);
        if (open > 0) open--;
        setImmune(open <= 0);
        if (lavaTimer > 0 && --lavaTimer == 0) drainLava();
        if (tickCount % 10 == 0) for (int k = 0; k < 8; k++) ring(Mech.GOLD, Mech.polar(o, PAD_R, Math.PI / 4 * k, o.y), 1.2, 6, o.y + 0.1);
        spark.entrySet().removeIf(e -> e.getValue() < tickCount);
    }

    @Override protected void onPhase(int phase) { shout("The Drumheart quickens — " + (int) bpm() + " beats a minute."); sound(SoundEvents.NOTE_BLOCK_BASEDRUM.value(), 3F, 0.5F); }

    private boolean slams(int k, int b) { return b == 4 || k % 3 == b - 1; }

    /** Amber flashes on the hammers about to fall. */
    private void warnNext(Vec3 o) {
        int nb = beat % 4 + 1;
        for (int k = 0; k < 8; k++) if (slams(k, nb)) { Vec3 h = Mech.polar(o, HAMMER_R, Math.PI / 4 * k, o.y + 0.2); ring(Mech.RED, h, 2.5, 10, h.y); }
        if (nb == 4) for (int d = 0; d < 4; d++) Mech.line(serverLevel(), ParticleTypes.FLAME, Mech.polar(o, 4, Math.PI / 4 + Math.PI / 2 * d, o.y + 0.3), Mech.polar(o, 22, Math.PI / 4 + Math.PI / 2 * d, o.y + 0.3), 12);
    }

    private void onBeat(Vec3 o) {
        sound(beat == 4 ? SoundEvents.NOTE_BLOCK_BASEDRUM.value() : SoundEvents.NOTE_BLOCK_SNARE.value(), 3F, beat == 4 ? 0.5F : 1.0F);
        for (int k = 0; k < 8; k++) if (slams(k, beat)) {
            Vec3 h = Mech.polar(o, HAMMER_R, Math.PI / 4 * k, o.y);
            areaDamage(h, 2.8, 8, 0.9); Mech.soundAt(serverLevel(), h, SoundEvents.ANVIL_LAND, 1.2F, 0.6F);
            serverLevel().sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, h.x, h.y + 0.5, h.z, 8, 1, 0.2, 1, 0.02);
        }
        if (beat != 4) return;
        // the downbeat: the boss opens, pads charge sparks, the lava lines rise
        open = OPEN_TICKS; Mech.burst(serverLevel(), ParticleTypes.ELECTRIC_SPARK, position().add(0, kind.height * 0.6, 0), 30, 4);
        for (ServerPlayer p : party()) for (int k = 0; k < 8; k++) if (Mech.horiz(p.position(), Mech.polar(o, PAD_R, Math.PI / 4 * k, o.y)) <= 1.6 && Math.abs(p.getY() - o.y) < 2.5) {
            spark.put(p.getUUID(), tickCount + SPARK_TICKS); p.displayClientMessage(NinjacatText.gold("Spark charged — hit it on the next open beat!"), true);
            serverLevel().sendParticles(ParticleTypes.ELECTRIC_SPARK, p.getX(), p.getY() + 1, p.getZ(), 20, 0.5, 0.8, 0.5, 0.1); break;
        }
        if (arena() != null) raiseLava(o);
    }

    private void raiseLava(Vec3 o) {
        lava.clear();
        for (int d = 0; d < 4; d++) for (int r = 4; r <= 22; r++) {
            BlockPos p = BlockPos.containing(Mech.polar(o, r, Math.PI / 4 + Math.PI / 2 * d, o.y));
            if (level().getBlockState(p).isAir()) { level().setBlock(p, Blocks.LAVA.defaultBlockState(), 3); lava.add(p); }
        }
        lavaTimer = LAVA_TICKS; sound(SoundEvents.LAVA_EXTINGUISH, 1.5F, 0.5F);
    }

    private void drainLava() {
        for (BlockPos p : lava) for (BlockPos q : new BlockPos[]{p, p.north(), p.south(), p.east(), p.west(), p.below(), p.below(2)})
            if (level().getBlockState(q).is(Blocks.LAVA) && q.getY() >= origin().y - 2) level().setBlock(q, Blocks.AIR.defaultBlockState(), 3);
        lava.clear();
    }

    @Override protected void onDefeated() { super.onDefeated(); drainLava(); }
}
