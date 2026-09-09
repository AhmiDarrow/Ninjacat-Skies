package com.ninjacat.skies.guardians.relic;

import com.ninjacat.skies.guardians.item.RelicItem;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.living.LivingDamageEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** Routes player events to the powers of the relics the player is wearing. */
public final class RelicEvents {
    private final Map<UUID, Set<RelicItem>> lastWorn = new HashMap<>();

    @SubscribeEvent
    public void onTick(PlayerTickEvent.Post e) {
        if (!(e.getEntity() instanceof ServerPlayer p)) return;
        Set<RelicItem> now = new HashSet<>();
        for (ItemStack s : RelicSlots.worn(p)) {
            RelicItem r = (RelicItem) s.getItem(); now.add(r);
            r.power.tickWorn(p, s);
        }
        Set<RelicItem> before = lastWorn.getOrDefault(p.getUUID(), Set.of());
        for (RelicItem r : now) if (!before.contains(r)) r.power.onWorn(p, true);
        for (RelicItem r : before) if (!now.contains(r)) r.power.onWorn(p, false);
        if (now.isEmpty()) lastWorn.remove(p.getUUID()); else lastWorn.put(p.getUUID(), now);
    }

    @SubscribeEvent
    public void onIncoming(LivingIncomingDamageEvent e) {
        if (!(e.getEntity() instanceof ServerPlayer p)) return;
        for (ItemStack s : RelicSlots.worn(p)) { ((RelicItem) s.getItem()).power.onWearerHurt(p, s, e); if (e.isCanceled()) return; }
    }

    @SubscribeEvent
    public void onUseBlock(PlayerInteractEvent.RightClickBlock e) {
        if (!(e.getEntity() instanceof ServerPlayer p)) return;
        for (ItemStack s : RelicSlots.worn(p)) ((RelicItem) s.getItem()).power.onWearerUseBlock(p, s, e.getPos());
    }

    @SubscribeEvent
    public void onDamage(LivingDamageEvent.Pre e) {
        if (!(e.getSource().getEntity() instanceof ServerPlayer p)) return;
        for (ItemStack s : RelicSlots.worn(p)) ((RelicItem) s.getItem()).power.onWearerHit(p, s, e.getEntity(), e);
    }
}
