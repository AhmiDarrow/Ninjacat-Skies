package com.ninjacat.skies.guardians.relic;

import com.ninjacat.skies.guardians.GuardianKind;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.common.NeoForge;

/**
 * Registry of the thirteen relic powers (see WOVEN_RELICS.md). The Strand relics live in {@link StrandRelics}, the
 * easy and insane ones in {@link SpecialRelics}; shared timers and static hooks in {@link RelicTimers}.
 */
public final class Relics {
    private Relics() {}

    static { NeoForge.EVENT_BUS.register(RelicTimers.class); }

    public static RelicPower power(GuardianKind kind) {
        return switch (kind) {
            case BEDDOWN -> StrandRelics.rootheart();
            case GRINDMAW -> StrandRelics.grindcore();
            case THORNMOTHER -> StrandRelics.thornseed();
            case EDGEWALKER -> StrandRelics.edgestep();
            case DRUMHEART -> StrandRelics.drumpulse();
            case COGWRIGHT -> StrandRelics.cogloop();
            case HIVEMIND -> StrandRelics.hivecall();
            case SEALBREAKER -> StrandRelics.sealmark();
            case UNWOVEN -> StrandRelics.loomthread();
            case LINTGOLEM -> SpecialRelics.lintwisp();
            case TANGLE -> SpecialRelics.knotcharm();
            case FIRSTCUT -> SpecialRelics.firstCut();
            case OVERWEAVER -> SpecialRelics.overweaverShuttle();
        };
    }

    static RelicPower trophy(GuardianKind kind) {
        return new RelicPower() {
            public String title() { return "Woven Relic of " + kind.title; }
            public String passiveText() { return "A trophy from the arena."; }
            public String activeText() { return "Nothing yet."; }
            public int cooldownTicks() { return 20; }
            public boolean activate(ServerPlayer p, ItemStack s) { return false; }
        };
    }
}
