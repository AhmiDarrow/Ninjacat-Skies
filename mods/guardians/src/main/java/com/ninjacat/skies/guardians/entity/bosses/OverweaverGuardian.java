package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import com.ninjacat.skies.guardians.entity.ModEntities;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.UUID;

/**
 * Insane · the Overweaver — THE LOOM ABOVE. The boss is the loom: it stands on the central weave and throws
 * shades of the nine guardians (40 % HP copies running their own fight) onto their strand-platforms (r 74, one per
 * 40°). Killing a shade lights that strand's bridge line and pulls its cathedral thread taut for 25 s; the boss can
 * only be hurt while at least one thread is taut. It throws one shade at a time; at 50 % three at once; at 25 %
 * (the phase hook — ARENAS.md says 20 %) all nine, and the keystone descends: from then on only blows struck from
 * under it (within r 6 of the weave's centre) count. Its own attack is the shuttle: a 1 s gold ring on a player,
 * then 5 hearts in r 4.
 * <p>
 * Shades are NOT bound to the arena: a bound guardian's death makes the base class call ArenaManager.onWin, which
 * would end the fight. Unbound, a shade's origin() is its own platform and its party() is whoever is within 96
 * blocks — exactly the mini-fight we want. A shade that vanishes (void, /kill) counts as killed so nothing soft-locks.
 */
public class OverweaverGuardian extends GuardianEntity {
    private static final GuardianKind[] STRANDS = {GuardianKind.BEDDOWN, GuardianKind.GRINDMAW, GuardianKind.THORNMOTHER, GuardianKind.EDGEWALKER, GuardianKind.DRUMHEART, GuardianKind.COGWRIGHT, GuardianKind.HIVEMIND, GuardianKind.SEALBREAKER, GuardianKind.UNWOVEN};
    private static final int PLATFORM_R = 74, SHADE_R = 66, BRIDGE_IN = 35, BRIDGE_OUT = 64, PILLAR_TOP = 31, KEYSTONE_Y = 64, KEYSTONE_LOW = 9, KEYSTONE_R = 6, TAUT = 500, THROW_EVERY = 400, SHUTTLE_EVERY = 120, SHUTTLE_TELL = 20;
    private final UUID[] shade = new UUID[9];
    private final int[] tautUntil = new int[9];
    private final Mech.Ledger[] lines = new Mech.Ledger[9];
    private int next = 0, nextThrow = 80, shuttleTell = -1; private double keystoneY = KEYSTONE_Y; private boolean keystone = false;
    @Nullable private Vec3 shuttleAt;

    public OverweaverGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.OVERWEAVER); for (int k = 0; k < 9; k++) lines[k] = new Mech.Ledger(); }

    @Override protected boolean mobile() { return false; }
    @Override protected String immuneMessage() { return "No thread is taut. Kill a shade on its strand-platform to pull one tight."; }
    /** Strand k's platform. arena_factory puts it at 90° + 40°k; the plan is that mirrored into Minecraft z, so the angle is negated. */
    private double angle(int k) { return -(Math.PI * 2 * k / 9 + Math.PI / 2); }
    private int tautCount() { int n = 0; for (int t : tautUntil) if (t > tickCount) n++; return n; }
    private int shadeCap() { return (phase() >= 3 ? 9 : phase() >= 2 ? 3 : 1) + Math.max(0, partySize() - 2); }

    /** Under the keystone, only blows from beneath it land. */
    @Override
    public boolean hurt(DamageSource src, float amount) {
        if (keystone && !isImmune() && src.getEntity() instanceof ServerPlayer p && Mech.horiz(p.position(), origin()) > KEYSTONE_R) {
            if (tickCount % 10 == 0) p.displayClientMessage(NinjacatText.teal("The keystone has come down — strike from beneath it."), true);
            return false;
        }
        return super.hurt(src, amount);
    }

    @Override
    protected void tickMechanic() {
        if (ageInFight == 1) shout("The Overweaver answers for the Cut with every guardian you have broken. It throws their shades onto the nine strands; each shade you kill pulls a thread taut for 25 s, and only then can the loom itself be hurt.");
        setImmune(tautCount() == 0);
        if (tickCount % 10 == 0) auditShades();
        if (--nextThrow <= 0) throwShades();
        if (tickCount % 5 == 0) drawThreads();
        if (tickCount % 20 == 0) slacken();
        if (shuttleTell >= 0) tickShuttle(); else if (ageInFight % SHUTTLE_EVERY == 0) startShuttle();
        if (keystone) tickKeystone();
    }

    @Override
    protected void onPhase(int phase) {
        if (phase == 1) shout("The loom quickens.");
        if (phase == 2) { shout("The Overweaver throws three shades at once!"); nextThrow = 1; }
        if (phase == 3) { keystone = true; shout("All nine strands at once — and the keystone descends. When it settles, only blows from beneath it land."); sound(SoundEvents.END_PORTAL_SPAWN, 3F, 0.5F); nextThrow = 1; }
    }

    // ------------------------------------------------------------------ shades
    private int alive() { int n = 0; for (UUID u : shade) if (u != null) n++; return n; }
    /** Throw shades up to the cap: one per cycle normally, everything at once in the later phases. */
    private void throwShades() {
        nextThrow = THROW_EVERY;
        int room = shadeCap() - alive(), thrown = 0;
        for (int tries = 0; tries < 9 && thrown < room; tries++) {
            int k = next; next = (next + 1) % 9;
            if (shade[k] != null || tautUntil[k] > tickCount) continue;        // a strand already fighting, or still taut, waits
            if (spawnShade(k)) thrown++;
            if (phase() < 2) break;                                             // one at a time until 50 %
        }
        if (thrown > 0) { playClip(CLIP_ATTACK); sound(SoundEvents.ENDER_DRAGON_FLAP, 2F, 0.4F); }
    }
    private boolean spawnShade(int k) {
        GuardianKind sk = STRANDS[k];
        GuardianEntity g = ModEntities.create(sk, serverLevel()); if (g == null) return false;
        Vec3 o = origin(), spot = Mech.polar(o, SHADE_R, angle(k), o.y);
        Vec3 at = Mech.standOn(level(), spot.x, spot.z, (int) o.y - 4, (int) o.y + 4); if (at == null) at = spot;
        g.moveTo(at.x, at.y, at.z, (float) Math.toDegrees(angle(k)) + 90, 0);
        g.setCustomName(Component.literal("Shade of " + sk.title)); g.setCustomNameVisible(true);
        g.addTag(Mech.tag(this)); g.addTag("guardians_add"); g.setPersistenceRequired();
        AttributeInstance h = g.getAttribute(Attributes.MAX_HEALTH); if (h != null) { h.setBaseValue(sk.baseHealth * 0.4 * (0.6 + 0.4 * partySize())); g.setHealth(g.getMaxHealth()); }
        g.finalizeSpawn(serverLevel(), serverLevel().getCurrentDifficultyAt(g.blockPosition()), MobSpawnType.MOB_SUMMONED, null);
        serverLevel().addFreshEntity(g); shade[k] = g.getUUID();
        Mech.line(serverLevel(), Mech.VIOLET, position().add(0, kind.height * 0.5, 0), at.add(0, 2, 0), 40); Mech.burst(serverLevel(), ParticleTypes.PORTAL, at.add(0, 2, 0), 40, 2);
        Mech.soundAt(serverLevel(), at, SoundEvents.SHULKER_TELEPORT, 2F, 0.5F);
        say("The Overweaver throws the shade of " + sk.title + " onto its strand.");
        return true;
    }
    /** A shade that is dead, dying (death clip) or simply gone counts as killed: its thread pulls taut. */
    private void auditShades() {
        for (int k = 0; k < 9; k++) {
            if (shade[k] == null) continue;
            Entity e = serverLevel().getEntity(shade[k]);
            if (e instanceof GuardianEntity g && g.isAlive() && g.clip() != CLIP_DEATH) continue;
            shade[k] = null; tautUntil[k] = tickCount + TAUT; lightLine(k);
            shout("The shade of " + STRANDS[k].title + " unravels — its thread pulls taut! The loom can be hurt for 25 s.");
            sound(SoundEvents.NOTE_BLOCK_CHIME.value(), 3F, 0.5F); Mech.burst(serverLevel(), ParticleTypes.END_ROD, position().add(0, kind.height * 0.6, 0), 40, 5);
            if (phase() < 2) nextThrow = Math.min(nextThrow, 100);            // the next shade follows the kill quickly
        }
    }

    // ------------------------------------------------------------------ threads and bridge lines
    /** The oak ridge down the middle of the bridge (r 35–64) glows sea-lantern while the thread is taut. */
    private void lightLine(int k) {
        Vec3 o = origin();
        for (int r = BRIDGE_IN; r <= BRIDGE_OUT; r++) { BlockPos b = BlockPos.containing(Mech.polar(o, r, angle(k), o.y)); if (!level().getBlockState(b).isAir() && !lines[k].has(b)) lines[k].set(level(), b, Blocks.SEA_LANTERN.defaultBlockState()); }
    }
    private void slacken() {
        for (int k = 0; k < 9; k++) if (lines[k].size() > 0 && tautUntil[k] <= tickCount) { lines[k].restoreAll(level()); say("A thread slackens."); }
    }
    private void drawThreads() {
        Vec3 o = origin(), key = new Vec3(o.x, o.y + keystoneY, o.z);
        for (int k = 0; k < 9; k++) if (tautUntil[k] > tickCount) Mech.line(serverLevel(), Mech.GOLD, Mech.polar(o, PLATFORM_R, angle(k), o.y + PILLAR_TOP), key, 30);
    }

    // ------------------------------------------------------------------ the shuttle
    private void startShuttle() {
        ServerPlayer p = nearestParty(); if (p == null || Mech.horiz(p.position(), origin()) > 34) return;
        shuttleAt = p.position(); shuttleTell = 0; sound(SoundEvents.ARROW_SHOOT, 2F, 0.4F);
    }
    private void tickShuttle() {
        shuttleTell++;
        if (shuttleAt == null) { shuttleTell = -1; return; }
        ring(Mech.GOLD, shuttleAt, 4, 18, shuttleAt.y + 0.15);
        if (shuttleTell < SHUTTLE_TELL) return;
        shuttleTell = -1; Mech.thud(serverLevel(), shuttleAt); areaDamage(shuttleAt, 4, 10, 1.1); shuttleAt = null;
    }

    // ------------------------------------------------------------------ the keystone
    private void tickKeystone() {
        Vec3 o = origin();
        if (keystoneY > KEYSTONE_LOW) keystoneY = Math.max(KEYSTONE_LOW, keystoneY - 0.25);
        if (tickCount % 2 == 0) Mech.burst(serverLevel(), Mech.GOLD, new Vec3(o.x, o.y + keystoneY, o.z), 8, 1.2);
        if (tickCount % 5 == 0) ring(Mech.GOLD, o, KEYSTONE_R, 24, o.y + 0.2);
    }

    @Override
    protected void onDefeated() {
        super.onDefeated();
        Mech.discardMinions(this); for (int k = 0; k < 9; k++) { shade[k] = null; lines[k].restoreAll(level()); }
    }
}
