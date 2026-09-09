package com.ninjacat.skies.guardians.item;

import com.ninjacat.skies.guardians.GuardianKind;
import net.minecraft.advancements.AdvancementHolder;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.event.entity.player.AdvancementEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;

import java.util.ArrayList;
import java.util.List;

/**
 * Frayed Totem recipes are not in anyone's recipe book until the pack says so: a gate guardian's totem appears when
 * its Strand is seated ({@code ninjacatskies:strand/<id>}), the Lint Golem's with Soil, the Tangle's with Claw, and the
 * two insane totems after the Reweave ({@code ninjacatskies:reweave}). The same advancements gate the totem's use in
 * {@link com.ninjacat.skies.guardians.arena.ArenaManager#summon}, so an early craft is never more than a wasted craft.
 * Login re-syncs, so Clowder mates who were offline when the Strand seated still get their pages.
 */
public final class TotemUnlocks {
    private TotemUnlocks() {}

    public static void onAdvancement(AdvancementEvent.AdvancementEarnEvent e) {
        if (!(e.getEntity() instanceof ServerPlayer p)) return;
        award(p, e.getAdvancement().id());
    }

    public static void onLogin(PlayerEvent.PlayerLoggedInEvent e) {
        if (!(e.getEntity() instanceof ServerPlayer p)) return;
        for (GuardianKind k : GuardianKind.values()) {
            AdvancementHolder adv = p.server.getAdvancements().get(k.unlockAdvancement());
            if (adv != null && p.getAdvancements().getOrStartProgress(adv).isDone()) award(p, k.unlockAdvancement());
        }
    }

    private static void award(ServerPlayer p, ResourceLocation earned) {
        List<ResourceLocation> recipes = new ArrayList<>();
        for (GuardianKind k : GuardianKind.values()) if (k.unlockAdvancement().equals(earned)) recipes.add(k.totemRecipeId());
        if (!recipes.isEmpty()) p.awardRecipesByKey(recipes);
    }
}
