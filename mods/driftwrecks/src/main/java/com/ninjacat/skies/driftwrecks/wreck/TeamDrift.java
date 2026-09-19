package com.ninjacat.skies.driftwrecks.wreck;

import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.Strand;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.util.RandomSource;

import javax.annotation.Nullable;

/**
 * A Clowder's Driftwreck state, stored next to Loom Tension in the team's data (one source of truth per team):
 * Drift pressure, lure cooldown and bias, the Wreck Atlas, stamps, hint pages read, Keepsakes found, the Heartwreck.
 */
public final class TeamDrift {
    public static final String ROOT = "driftwrecks";
    private final Clowder clowder;
    private final CompoundTag tag;

    private TeamDrift(Clowder clowder) {
        this.clowder = clowder;
        CompoundTag data = clowder.data();
        if (!data.contains(ROOT)) data.put(ROOT, new CompoundTag());
        this.tag = data.getCompound(ROOT);
    }

    public static TeamDrift of(Clowder c) { return new TeamDrift(c); }

    public Clowder clowder() { return clowder; }
    public void dirty() { clowder.markDirty(); }

    // ---------------------------------------------------------------- pressure
    public int pressure() { return tag.getInt("pressure"); }
    public void setPressure(int ticks) { tag.putInt("pressure", Math.max(0, ticks)); }

    /** Ticks of online time to fill; rolled fresh after each arrival. */
    public int target(RandomSource rng, int minMinutes, int maxMinutes) {
        int t = tag.getInt("target");
        if (t <= 0) {
            int lo = Math.min(minMinutes, maxMinutes), hi = Math.max(minMinutes, maxMinutes);
            t = (lo + rng.nextInt(hi - lo + 1)) * 60 * 20;
            tag.putInt("target", t);
        }
        return t;
    }
    public void resetCycle() { tag.putInt("pressure", 0); tag.remove("target"); }
    public void fill() { tag.putInt("pressure", Integer.MAX_VALUE / 2); }

    public long lureReadyAt() { return tag.getLong("lureReady"); }
    public void setLureReadyAt(long gameTime) { tag.putLong("lureReady", gameTime); }

    /** Strand the next wreck leans toward (a Strand-bead Lure), or null. */
    @Nullable
    public Strand lureStrand() { return tag.contains("lureStrand") ? Strand.byId(tag.getString("lureStrand")) : null; }
    public void setLureStrand(@Nullable Strand s) { if (s == null) tag.remove("lureStrand"); else tag.putString("lureStrand", s.id()); }

    /** A Wreck-map scroll was read: the next arrival is a core not yet in the Atlas for its skin. */
    public boolean scrollPending() { return tag.getBoolean("scroll"); }
    public void setScrollPending(boolean b) { tag.putBoolean("scroll", b); }

    // ---------------------------------------------------------------- atlas
    /** Cores filled for a Strand column, as {@link WreckCore#bit()} flags. */
    public int column(Strand s) { return tag.getCompound("atlas").getInt(s.id()); }
    public boolean hasCell(Strand s, WreckCore c) { return (column(s) & c.bit()) != 0; }
    /** Returns true if the cell is new. */
    public boolean fillCell(Strand s, WreckCore c) {
        CompoundTag atlas = tag.getCompound("atlas");
        int bits = atlas.getInt(s.id());
        if ((bits & c.bit()) != 0) return false;
        atlas.putInt(s.id(), bits | c.bit());
        tag.put("atlas", atlas);
        return true;
    }
    public int cellCount() {
        int n = 0;
        for (Strand s : Strand.ALL) n += Integer.bitCount(column(s));
        return n;
    }
    public boolean columnComplete(Strand s) { return Integer.bitCount(column(s)) == WreckCore.ALL.length; }
    public boolean rowComplete(WreckCore c) {
        for (Strand s : Strand.ALL) if (!hasCell(s, c)) return false;
        return true;
    }

    public int modifierStamps() { return tag.getInt("modStamps"); }
    public boolean stampModifier(WreckModifier m) {
        int b = modifierStamps();
        if ((b & m.bit()) != 0) return false;
        tag.putInt("modStamps", b | m.bit());
        return true;
    }
    public boolean allModifierStamps() { return Integer.bitCount(modifierStamps()) == WreckModifier.ALL.length; }

    public int remnantStamps() { return tag.getInt("remnants"); }
    public boolean stampRemnant(Strand s) {
        int b = remnantStamps();
        if ((b & s.bit()) != 0) return false;
        tag.putInt("remnants", b | s.bit());
        return true;
    }
    public boolean allRemnantStamps() { return Integer.bitCount(remnantStamps()) == Strand.ALL.length; }

    /** Hint pages read, as core bits. A read hint (or a completed row) opens that core's hidden room. */
    public boolean hintRead(WreckCore c) { return (tag.getInt("hints") & c.bit()) != 0; }
    public boolean readHint(WreckCore c) {
        int b = tag.getInt("hints");
        if ((b & c.bit()) != 0) return false;
        tag.putInt("hints", b | c.bit());
        return true;
    }
    public boolean hiddenRoomOpen(WreckCore c) { return hintRead(c) || rowComplete(c); }

    /** Keepsakes this Clowder has found (bit = strand * 6 + core). */
    public boolean hasKeepsake(Strand s, WreckCore c) { return (tag.getLong("keepsakes") & (1L << keepsakeIndex(s, c))) != 0; }
    public boolean findKeepsake(Strand s, WreckCore c) {
        long b = tag.getLong("keepsakes"), bit = 1L << keepsakeIndex(s, c);
        if ((b & bit) != 0) return false;
        tag.putLong("keepsakes", b | bit);
        return true;
    }
    public static int keepsakeIndex(Strand s, WreckCore c) { return s.ordinal() * WreckCore.ALL.length + c.ordinal(); }
    public boolean heartKeepsake() { return tag.getBoolean("heartKeepsake"); }
    public void setHeartKeepsake() { tag.putBoolean("heartKeepsake", true); }

    /** 0 not earned, 1 earned (arrives next), 2 arrived, 3 finished. Once per Clowder. */
    public int heartwreck() { return tag.getInt("heartwreck"); }
    public void setHeartwreck(int state) { tag.putInt("heartwreck", state); }

    // ---------------------------------------------------------------- perks
    public float lifetimeBonus() { return allModifierStamps() ? 1.25F : 1.0F; }
    public boolean halfPriceLure(Strand s) { return columnComplete(s); }
    public boolean halfPriceKeys() { return allRemnantStamps(); }

    public int counter(String key) { return tag.getCompound("counts").getInt(key); }
    public void count(String key) {
        CompoundTag c = tag.getCompound("counts");
        c.putInt(key, c.getInt(key) + 1);
        tag.put("counts", c);
    }

    /** A copy of the raw tag, for the Atlas sync payload. */
    public CompoundTag snapshot() { return tag.copy(); }
}
