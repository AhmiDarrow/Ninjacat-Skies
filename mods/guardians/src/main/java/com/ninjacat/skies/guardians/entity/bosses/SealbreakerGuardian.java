package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

/**
 * Sigil · the Sealbreaker — READ THE ROOM. Nine glyph pillars stand on r 24; three carry active wards (teal),
 * shown as ward-glass at the pillar's foot. The dais pegs in the centre light in an order — dispel (break) the
 * ward-glass in that order. Wrong order re-arms all wards and the ward-glass fires a 3-heart arc. Three correct
 * dispels expose the boss for 12 s. Phase 2 shuffles the runes; phase 3 adds a decoy ward that is never in the order.
 * The peg order replays every 30 s so a party that missed it can watch again.
 */
public class SealbreakerGuardian extends GuardianEntity {
    private static final int PILLARS = 9, PILLAR_R = 24, GLYPH_R = 21, PEG_R = 4, OPEN_TICKS = 240, REPLAY = 600, PEG_GAP = 24;
    private final List<Integer> order = new ArrayList<>();       // pillar indices, in dispel order
    private final List<Integer> active = new ArrayList<>();      // order + decoy
    private final BlockPos[] glyph = new BlockPos[PILLARS];
    private int progress = 0, open = 0, replayClock = 0, decoy = -1;

    public SealbreakerGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.SEALBREAKER); }

    @Override protected String immuneMessage() { return "The Sealbreaker hides behind its wards. Watch the dais pegs and dispel the wards in that order."; }
    /** Pillar k stands at 90° + 40°k in arena_factory; the plan mirrors Blender y into Minecraft -z, hence the negated angle. */
    private static double pillarAngle(int k) { return -(Math.PI * 2 * k / PILLARS + Math.PI / 2); }
    private Vec3 pillar(int k) { Vec3 o = origin(); return Mech.polar(o, PILLAR_R, pillarAngle(k), o.y); }
    private Vec3 peg(int k) { Vec3 o = origin(); return Mech.polar(o, PEG_R, pillarAngle(k), o.y + 1.2); }

    @Override
    protected void tickMechanic() {
        if (arena() == null) {                                          // a shade (or /summon): no glyph pillars to ward — it drops its guard every 20 s
            if (open > 0) open--; else if (ageInFight % 400 == 60) { open = OPEN_TICKS; shout("The Sealbreaker's wards flicker — it is exposed for twelve seconds!"); sound(SoundEvents.BEACON_DEACTIVATE, 2F, 0.5F); }
            setImmune(open <= 0); return;
        }
        if (ageInFight == 1) { shout("The Sealbreaker answers for the Cut. Three wards hold it: teal-lit ward-glass at the foot of three pillars. Don't rush them — the dais pegs light the order. Dispel the glass in that order; break the wrong one and the whole circle bites."); arm(true); }
        if (open > 0) { open--; if (open == 0) { say("The wards re-knit."); arm(true); } }
        setImmune(open <= 0);
        if (open <= 0) {
            if (tickCount % 5 == 0) checkGlyphs();
            replayClock++;
            if (replayClock >= REPLAY) replayClock = 0;
            if (replayClock < PEG_GAP * order.size() && replayClock % PEG_GAP == 0) showPeg(replayClock / PEG_GAP);
            if (tickCount % 6 == 0) for (int k : active) Mech.column(serverLevel(), Mech.TEAL, pillar(k).add(0, 3, 0), 6, 6);
        }
        if (tickCount % 40 == 0 && Mech.horiz(position(), origin()) > 20) getNavigation().moveTo(origin().x, origin().y, origin().z, 1.0);
    }

    @Override
    protected void onPhase(int phase) {
        if (open > 0) return;
        shout(phase == 3 ? "The Sealbreaker raises a fourth ward — a decoy. Only three are written on the dais." : "The runes shuffle! Watch the dais again.");
        arm(true);
    }

    /** Choose the active pillars and their order, place the ward-glass, start the peg replay. */
    private void arm(boolean reshuffle) {
        clearGlyphs();
        if (reshuffle || order.isEmpty()) {
            List<Integer> pool = new ArrayList<>(); for (int k = 0; k < PILLARS; k++) pool.add(k);
            java.util.Collections.shuffle(pool, new java.util.Random(random.nextLong()));
            order.clear(); for (int i = 0; i < 3; i++) order.add(pool.get(i));
            decoy = phase() >= 3 ? pool.get(3) : -1;
        }
        active.clear(); active.addAll(order); if (decoy >= 0) active.add(decoy);
        for (int k : active) {
            Vec3 at = Mech.polar(origin(), GLYPH_R, pillarAngle(k), origin().y);
            BlockPos g = Mech.ground(level(), at.x, at.z, (int) origin().y - 2, (int) origin().y + 3);
            BlockPos p = g != null ? g.above() : BlockPos.containing(at);
            placeTemp(p, Blocks.TINTED_GLASS.defaultBlockState()); glyph[k] = p;
        }
        progress = 0; replayClock = 0;
        sound(SoundEvents.BEACON_ACTIVATE, 2F, 0.6F);
    }
    private void clearGlyphs() {
        for (int k = 0; k < PILLARS; k++) if (glyph[k] != null) { if (level().getBlockState(glyph[k]).is(Blocks.TINTED_GLASS)) level().setBlock(glyph[k], Blocks.AIR.defaultBlockState(), 3); tempBlocks.remove(glyph[k]); glyph[k] = null; }
    }

    private void showPeg(int i) {
        Vec3 p = peg(order.get(i));
        Mech.burst(serverLevel(), ParticleTypes.END_ROD, p, 20, 0.3); Mech.line(serverLevel(), Mech.GOLD, p, pillar(order.get(i)).add(0, 4, 0), 24);
        Mech.soundAt(serverLevel(), p, SoundEvents.AMETHYST_BLOCK_CHIME, 2F, 0.7F + 0.2F * i);
    }

    /** Ward-glass that disappeared was dispelled: right one advances, any other re-arms the circle. */
    private void checkGlyphs() {
        for (int k : new ArrayList<>(active)) {
            if (glyph[k] == null || level().getBlockState(glyph[k]).is(Blocks.TINTED_GLASS)) continue;
            tempBlocks.remove(glyph[k]); glyph[k] = null;
            if (order.get(progress) == k) {
                progress++; active.remove(Integer.valueOf(k));
                Mech.burst(serverLevel(), ParticleTypes.SOUL_FIRE_FLAME, pillar(k).add(0, 2, 0), 30, 1); sound(SoundEvents.RESPAWN_ANCHOR_DEPLETE.value(), 2F, 1.2F);
                say("Ward " + progress + " of 3 dispelled.");
                if (progress >= 3) { open = OPEN_TICKS; clearGlyphs(); active.clear(); shout("The wards fall — the Sealbreaker is exposed! Twelve seconds."); sound(SoundEvents.BEACON_DEACTIVATE, 2F, 0.5F); }
            } else {
                for (int j : active) Mech.arc(serverLevel(), pillar(j));
                areaDamage(origin(), 40, 6, 0.3); shout("Wrong ward! The circle bites and every ward re-arms.");
                sound(SoundEvents.ELDER_GUARDIAN_CURSE, 2F, 0.8F); arm(false);
            }
            return;
        }
    }

    @Override protected void onDefeated() { super.onDefeated(); clearGlyphs(); }
}
