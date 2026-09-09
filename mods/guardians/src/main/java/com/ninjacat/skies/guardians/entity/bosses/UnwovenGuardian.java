package com.ninjacat.skies.guardians.entity.bosses;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.animal.Bee;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ScaffoldingBlock;
import net.minecraft.world.level.block.SweetBerryBushBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;

/**
 * Spindle · the Unwoven — FINALE. Five phases (100/80/60/40/20 % HP). Each of the first four quotes two of the
 * eight gate mechanics for 30 s apiece (bury, grit, prune, pounce, beat, pattern, drones, wards — reduced forms)
 * and then a heddle bar drops, unravelling three warp strips into one-block thread bridges. At 20 % the true form:
 * the boss rises to the top beam, warp threads (scaffolding) become the only way up, and it lashes at climbers.
 */
public class UnwovenGuardian extends GuardianEntity {
    private enum Quote { BURY, GRIT, PRUNE, POUNCE, BEAT, PATTERN, DRONES, WARDS }
    private static final int QUOTE_TICKS = 600, STRIPS = 23, HALF_W = 31, BEAM_Y = 28;
    private static final BlockState HEDGE = Blocks.SWEET_BERRY_BUSH.defaultBlockState().setValue(SweetBerryBushBlock.AGE, 2);
    private final Mech.Ledger floor = new Mech.Ledger(), lit = new Mech.Ledger();
    private final List<Integer> dropped = new ArrayList<>();
    private final List<BlockPos> marks = new ArrayList<>();       // core / gravel / tiles / wards used by the running quote
    private final List<Integer> order = new ArrayList<>();
    private int stage = 0, quoteIndex = 0, quoteTicks = 0, heddle = -1, progress = 0, beat = 0;
    private boolean solved = false, trueForm = false;
    @Nullable private Quote quote; @Nullable private Vec3 mark; private int markTicks = 0;
    private Quote[] pair = new Quote[2];

    public UnwovenGuardian(EntityType<? extends GuardianEntity> type, Level level) { super(type, level, GuardianKind.UNWOVEN); }

    @Override protected boolean mobile() { return false; }
    @Override protected int meleeCooldown() { return trueForm ? 30 : 50; }
    @Override
    protected String immuneMessage() {
        if (quote == null) return super.immuneMessage();
        return switch (quote) {
            case BURY -> "Buried. Dig to the glowing core and break it.";
            case GRIT -> "Its maw is shut. Place gravel at its feet.";
            case BEAT -> "It opens only on its fourth beat.";
            case PATTERN -> "Walk the lit tiles in the order they lit.";
            case WARDS -> "Dispel the ward-glass in the order the lights showed.";
            default -> super.immuneMessage();
        };
    }

    // ------------------------------------------------------------------ phase driver
    private int stageFor(float f) { return f > 0.8F ? 1 : f > 0.6F ? 2 : f > 0.4F ? 3 : f > 0.2F ? 4 : 5; }

    @Override
    protected void tickMechanic() {
        if (ageInFight == 1) shout("The Unwoven answers for the Cut — and it remembers every guardian you broke. Each phase it quotes two of them; then a heddle bar drops and the loom floor unravels beneath you.");
        int s = stageFor(getHealth() / getMaxHealth());
        if (s != stage) { stage = s; enterStage(); }
        if (heddle >= 0) tickHeddle();
        if (trueForm) { tickTrueForm(); return; }
        if (quote != null) {
            quoteTicks++;
            tickQuote();
            if (quoteTicks >= QUOTE_TICKS) endQuote();
        } else if (quoteIndex < 2 && heddle < 0) startQuote(pair[quoteIndex]);
        else if (quoteIndex >= 2 && heddle < 0 && !dropped.contains(-stage)) { dropped.add(-stage); heddle = 0; }   // one heddle drop per stage (negative ids mark stages)
    }

    private void enterStage() {
        if (stage >= 5) { trueForm(); return; }
        endQuote();
        List<Quote> pool = new ArrayList<>(List.of(Quote.values())); java.util.Collections.shuffle(pool, new java.util.Random(random.nextLong()));
        pair = new Quote[]{pool.get(0), pool.get(1)}; quoteIndex = 0;
        if (stage > 1) shout("The Unwoven frays further. It remembers " + pretty(pair[0]) + " and " + pretty(pair[1]) + ".");
        else shout("It begins with " + pretty(pair[0]) + ", then " + pretty(pair[1]) + ".");
    }
    private static String pretty(Quote q) { return switch (q) { case BURY -> "the Beddown"; case GRIT -> "the Grindmaw"; case PRUNE -> "the Thornmother"; case POUNCE -> "the Edgewalker"; case BEAT -> "the Drumheart"; case PATTERN -> "the Cogwright"; case DRONES -> "the Hivemind"; case WARDS -> "the Sealbreaker"; }; }

    // ------------------------------------------------------------------ quotes
    private void startQuote(Quote q) {
        quote = q; quoteTicks = 0; progress = 0; solved = false; beat = 0; marks.clear(); order.clear();
        Vec3 o = origin();
        switch (q) {
            case BURY -> {
                double a = random.nextDouble() * Math.PI * 2; BlockPos core = BlockPos.containing(Mech.polar(o, 6, a, o.y));
                placeTemp(core, Blocks.SHROOMLIGHT.defaultBlockState()); marks.add(core);
                for (int x = -8; x <= 8; x++) for (int z = -8; z <= 8; z++) { int r2 = x * x + z * z; if (r2 < 16 || r2 > 64) continue; for (int y = 0; y < 3; y++) placeTemp(BlockPos.containing(o.x + x, o.y + y, o.z + z), Blocks.DIRT.defaultBlockState()); }
                for (ServerPlayer p : party()) { double r = Mech.horiz(p.position(), o); if (r >= 3.5 && r <= 8.9 && p.getY() < o.y + 3) p.teleportTo(serverLevel(), p.getX(), o.y + 3.1, p.getZ(), p.getYRot(), p.getXRot()); }   // the heave lifts, never traps
                say("Soil heaves around the Unwoven — dig to the glowing core.");
            }
            case GRIT -> { for (int k = 0; k < 4; k++) { Vec3 at = Mech.polar(o, 10, Math.PI / 2 * k, o.y + 3); serverLevel().addFreshEntity(new net.minecraft.world.entity.item.ItemEntity(level(), at.x, at.y, at.z, new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.GRAVEL))); } say("Grit rattles down — place gravel at its feet to jam the maw."); }
            case PRUNE -> say("Thorns creep in — cut them or it drinks from them.");
            case POUNCE -> say("It lashes like the Edgewalker — leave the gold mark.");
            case BEAT -> say("It beats like the Drumheart — strike on the fourth.");
            case PATTERN -> { List<Integer> pool = new ArrayList<>(); for (int i = 0; i < 12; i++) pool.add(i); java.util.Collections.shuffle(pool, new java.util.Random(random.nextLong())); for (int i = 0; i < 3; i++) order.add(pool.get(i)); for (int i : order) marks.add(tileAt(o, i)); say("Tiles light like the Cogwright's — walk them in order."); }
            case WARDS -> {
                List<Integer> pool = new ArrayList<>(); for (int i = 0; i < 6; i++) pool.add(i); java.util.Collections.shuffle(pool, new java.util.Random(random.nextLong()));
                for (int i = 0; i < 3; i++) { order.add(pool.get(i)); BlockPos g = wardAt(o, pool.get(i)); placeTemp(g, Blocks.TINTED_GLASS.defaultBlockState()); marks.add(g); }
                say("Wards rise like the Sealbreaker's — watch the lights, then break the glass in that order.");
            }
            case DRONES -> say("The comb hums — drones!");
        }
    }
    private BlockPos tileAt(Vec3 o, int i) { Vec3 at = Mech.polar(o, arena() == null ? 7 : 10, Math.PI * 2 * i / 12, o.y); BlockPos g = Mech.ground(level(), at.x, at.z, (int) o.y - 2, (int) o.y + 2); return g != null ? g : BlockPos.containing(at).below(); }
    private BlockPos wardAt(Vec3 o, int i) { Vec3 at = Mech.polar(o, arena() == null ? 8 : 12, Math.PI * 2 * i / 6, o.y); BlockPos g = Mech.ground(level(), at.x, at.z, (int) o.y - 2, (int) o.y + 2); return g != null ? g.above() : BlockPos.containing(at); }

    private void tickQuote() {
        Vec3 o = origin(); boolean immune = false;
        switch (quote) {
            case BURY -> { BlockPos core = marks.get(0); immune = level().getBlockState(core).is(Blocks.SHROOMLIGHT); if (immune && tickCount % 3 == 0) Mech.column(serverLevel(), ParticleTypes.SOUL_FIRE_FLAME, Vec3.atCenterOf(core).add(0, 0.5, 0), 5, 5); if (!immune && !solved) { solved = true; shout("The core cracks — it is open!"); } }
            case GRIT -> { if (!solved && tickCount % 20 == 0) { BlockPos g = gravelNear(o); if (g != null) { level().setBlock(g, Blocks.AIR.defaultBlockState(), 3); solved = true; shout("Grit in the gears — the maw jams open!"); sound(SoundEvents.IRON_TRAPDOOR_OPEN, 2F, 0.4F); } } immune = !solved; }
            case PRUNE -> { if (quoteTicks % 60 == 0) seedThorns(); int n = 0; for (BlockPos p : marks) if (level().getBlockState(p).is(Blocks.SWEET_BERRY_BUSH)) n++; if (n >= 6 && quoteTicks % 40 == 0) { heal(getMaxHealth() * 0.01F); Mech.burst(serverLevel(), ParticleTypes.HEART, position().add(0, 6, 0), 6, 2); } thornDamage(); }
            case POUNCE -> { if (mark == null && quoteTicks % 60 == 0) { ServerPlayer p = Mech.randomPlayer(this); if (p != null) { mark = p.position(); markTicks = 0; sound(SoundEvents.PHANTOM_SWOOP, 2F, 0.7F); } } tickMark(3.5, 10); }
            case BEAT -> { int t = quoteTicks % 40; if (t == 0) { beat = beat % 4 + 1; sound(beat == 4 ? SoundEvents.NOTE_BLOCK_BASEDRUM.value() : SoundEvents.NOTE_BLOCK_SNARE.value(), 3F, beat == 4 ? 0.5F : 1F); if (beat == 4) { ServerPlayer p = nearestParty(); if (p != null) { mark = p.position(); markTicks = 0; } } } tickMark(3, 8); immune = !(beat == 4 && t < 12); }
            case PATTERN -> {
                if (quoteTicks <= 45) { if (quoteTicks % 15 == 1) { lit.restoreAll(level()); BlockPos t = marks.get(quoteTicks / 15); lit.set(level(), t, Blocks.OCHRE_FROGLIGHT.defaultBlockState()); Mech.soundAt(serverLevel(), Vec3.atCenterOf(t), SoundEvents.NOTE_BLOCK_PLING.value(), 2F, 0.6F + 0.2F * (quoteTicks / 15)); } }
                else if (!solved) { if (quoteTicks == 46) { lit.restoreAll(level()); for (BlockPos t : marks) lit.set(level(), t, Blocks.SHROOMLIGHT.defaultBlockState()); }
                    for (ServerPlayer p : party()) { BlockPos on = p.getOnPos(); if (on.equals(marks.get(progress))) { progress++; lit.set(level(), on, Blocks.SEA_LANTERN.defaultBlockState()); Mech.soundAt(serverLevel(), p.position(), SoundEvents.NOTE_BLOCK_PLING.value(), 2F, 0.6F + 0.2F * progress); if (progress >= 3) { solved = true; lit.restoreAll(level()); shout("The pattern holds — it opens!"); } break; } for (int i = progress + 1; i < 3; i++) if (on.equals(marks.get(i))) { progress = 0; areaDamage(o, 40, 6, 0.2); shout("Wrong tile! The gears arc — the pattern is lost."); lit.restoreAll(level()); quoteTicks = QUOTE_TICKS; break; } }
                    if (quoteTicks > 46 + 240) { areaDamage(o, 40, 6, 0.2); shout("Too slow — the gears arc."); quoteTicks = QUOTE_TICKS; } }
                immune = !solved;
            }
            case WARDS -> {
                if ((quoteTicks - 1) % 200 < 60 && (quoteTicks - 1) % 20 == 0) { int i = ((quoteTicks - 1) % 200) / 20; Vec3 w = Vec3.atCenterOf(marks.get(i)); Mech.column(serverLevel(), Mech.GOLD, w, 6, 8); Mech.soundAt(serverLevel(), w, SoundEvents.AMETHYST_BLOCK_CHIME, 2F, 0.7F + 0.2F * i); }
                if (!solved && tickCount % 5 == 0) for (int i = 0; i < 3; i++) { BlockPos w = marks.get(i); if (level().getBlockState(w).is(Blocks.TINTED_GLASS) || tempBlocks.contains(w) == false) continue;
                    tempBlocks.remove(w);
                    if (i == progress) { progress++; sound(SoundEvents.RESPAWN_ANCHOR_DEPLETE.value(), 2F, 1.2F); if (progress >= 3) { solved = true; shout("The wards fall — it is exposed!"); } }
                    else { areaDamage(o, 40, 6, 0.3); shout("Wrong ward! They re-arm."); progress = 0; for (BlockPos g : marks) placeTemp(g, Blocks.TINTED_GLASS.defaultBlockState()); }
                    break; }
                immune = !solved;
            }
            case DRONES -> { if (quoteTicks % 200 == 1 && Mech.countMinions(this) < 4 + 3 * partySize()) for (int i = 0; i < 2 + partySize(); i++) { Bee b = Mech.spawn(this, EntityType.BEE, Mech.polar(o, 12, random.nextDouble() * Math.PI * 2, o.y + 3), "Drone", 12, 3); ServerPlayer p = Mech.randomPlayer(this); if (b != null && p != null) { b.setPersistentAngerTarget(p.getUUID()); b.setRemainingPersistentAngerTime(2400); b.setTarget(p); } } }
        }
        setImmune(immune);
    }

    /** Gold claw-mark: 0.7 s telegraph, then the slam. */
    private void tickMark(double r, float dmg) {
        if (mark == null) return;
        markTicks++;
        ring(Mech.GOLD, mark, r, 16, mark.y + 0.15);
        if (markTicks >= 14) { Mech.thud(serverLevel(), mark); areaDamage(mark, r, dmg, 1.0); mark = null; }
    }
    @Nullable
    private BlockPos gravelNear(Vec3 o) {
        BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
        for (int x = -6; x <= 6; x++) for (int z = -6; z <= 6; z++) for (int y = 0; y <= 2; y++) { m.set(Math.floor(o.x) + x, o.y + y, Math.floor(o.z) + z); if (level().getBlockState(m).is(Blocks.GRAVEL)) return m.immutable(); }
        return null;
    }
    private void seedThorns() {
        for (int i = 0; i < 2 + partySize() / 2; i++) {
            ServerPlayer p = Mech.randomPlayer(this); if (p == null) return;
            Vec3 at = Mech.polar(p.position(), 2 + random.nextDouble() * 4, random.nextDouble() * Math.PI * 2, p.getY());
            BlockPos g = Mech.ground(level(), at.x, at.z, (int) p.getY() - 3, (int) p.getY() + 3);
            if (g != null && HEDGE.canSurvive(level(), g.above()) && marks.size() < 60) { placeTemp(g.above(), HEDGE); marks.add(g.above()); }
        }
    }
    private void thornDamage() {
        if (tickCount % 20 != 0) return;
        for (ServerPlayer p : party()) if (level().getBlockState(p.blockPosition()).is(Blocks.SWEET_BERRY_BUSH)) p.hurt(damageSources().mobAttack(this), 2);
    }

    private void endQuote() {
        if (quote == null) return;
        if (quote == Quote.BURY || quote == Quote.PRUNE || quote == Quote.WARDS || quote == Quote.PATTERN) { for (BlockPos p : marks) if (tempBlocks.remove(p)) level().setBlock(p, Blocks.AIR.defaultBlockState(), 3); revertTempBlocks(); }
        lit.restoreAll(level()); marks.clear(); mark = null; quote = null; quoteIndex++; setImmune(false);
    }

    // ------------------------------------------------------------------ heddle drop
    /** A 1 s telegraph, then three warp strips lose one of their two plank rows — one-block thread bridges. */
    private void tickHeddle() {
        if (arena() == null) { heddle = -1; return; }
        Vec3 o = origin(); heddle++;
        if (heddle == 1) { shout("A heddle bar drops — the warp unravels!"); sound(SoundEvents.ANVIL_LAND, 3F, 0.4F); }
        if (heddle < 20) { if (heddle % 4 == 0) for (int i = 0; i < 3; i++) Mech.line(serverLevel(), Mech.RED, new Vec3(o.x - HALF_W, o.y + 0.2, o.z - STRIPS + 2 * ((heddle + i * 7) % STRIPS) + 0.5), new Vec3(o.x + HALF_W, o.y + 0.2, o.z - STRIPS + 2 * ((heddle + i * 7) % STRIPS) + 0.5), 20); return; }
        int done = 0;
        for (int tries = 0; tries < 40 && done < 3; tries++) {
            int i = random.nextInt(STRIPS); if (i == 11 || i == 12 || dropped.contains(i)) continue;      // the two strips under the boss stay
            dropped.add(i); done++;
            // the strip is whichever of the two rows actually carries planks; it unravels into a thread of single blocks (every fourth stays)
            int z0 = (int) Math.floor(o.z) - STRIPS + 2 * i, z = z0;
            int n0 = 0, n1 = 0; for (int x = -HALF_W; x <= HALF_W; x++) { if (!level().getBlockState(new BlockPos((int) Math.floor(o.x) + x, (int) o.y - 1, z0)).isAir()) n0++; if (!level().getBlockState(new BlockPos((int) Math.floor(o.x) + x, (int) o.y - 1, z0 + 1)).isAir()) n1++; }
            if (n1 > n0) z = z0 + 1;
            for (int x = -HALF_W; x <= HALF_W; x++) { if (Math.floorMod(x, 4) == 0) continue; BlockPos p = new BlockPos((int) Math.floor(o.x) + x, (int) o.y - 1, z); if (!level().getBlockState(p).isAir()) floor.clear(level(), p); }
            serverLevel().sendParticles(ParticleTypes.CLOUD, o.x, o.y, z + 0.5, 30, HALF_W, 0.3, 0.3, 0.02);
        }
        sound(SoundEvents.WOOD_BREAK, 3F, 0.4F); heddle = -1;
    }

    // ------------------------------------------------------------------ true form
    private void trueForm() {
        endQuote(); trueForm = true; Vec3 o = origin();
        Vec3 beam = Mech.standOn(level(), o.x, o.z, (int) o.y + 20, (int) o.y + 34);
        if (beam == null) { for (int x = -3; x <= 3; x++) for (int z = -3; z <= 3; z++) placeTemp(BlockPos.containing(o.x + x, o.y + BEAM_Y - 1, o.z + z), Blocks.SPRUCE_PLANKS.defaultBlockState()); beam = new Vec3(o.x, o.y + BEAM_Y, o.z); }
        BlockState thread = Blocks.SCAFFOLDING.defaultBlockState().setValue(ScaffoldingBlock.DISTANCE, 0);
        for (int k = 0; k < 4; k++) {
            Vec3 base = Mech.polar(o, 9, Math.PI / 4 + Math.PI / 2 * k, o.y);
            BlockPos foot = BlockPos.containing(base.x, o.y - 1, base.z);
            if (level().getBlockState(foot).isAir()) placeTemp(foot, Blocks.SPRUCE_PLANKS.defaultBlockState());   // a thread needs a footing, or the scaffolding falls
            for (int y = 0; y < beam.y - o.y; y++) placeTemp(BlockPos.containing(base.x, o.y + y, base.z), thread);
        }
        teleportTo(beam.x, beam.y, beam.z); setImmune(false);
        shout("The Unwoven unravels into its true form and climbs to the top beam. The warp threads pull taut — climb them and finish it on the beam!");
        sound(SoundEvents.ENDER_DRAGON_GROWL, 3F, 0.5F);
    }
    private void tickTrueForm() {
        if (mark == null && tickCount % 80 == 0) { ServerPlayer p = Mech.randomPlayer(this); if (p != null) { mark = p.position(); markTicks = 0; sound(SoundEvents.PHANTOM_SWOOP, 2F, 0.5F); } }
        tickMark(3.5, 12);
        if (tickCount % 10 == 0) Mech.burst(serverLevel(), Mech.TEAL, position().add(0, kind.height * 0.5, 0), 6, 4);
    }

    @Override protected void onDefeated() { super.onDefeated(); Mech.discardMinions(this); floor.restoreAll(level()); lit.restoreAll(level()); }
}
