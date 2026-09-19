package com.ninjacat.skies.driftwrecks;

import com.ninjacat.skies.core.block.TensionPostBlock;
import com.ninjacat.skies.driftwrecks.item.DriftlureItem;
import com.ninjacat.skies.driftwrecks.rift.RiftManager;
import com.ninjacat.skies.driftwrecks.wreck.DriftManager;
import com.ninjacat.skies.driftwrecks.wreck.Tether;
import com.ninjacat.skies.driftwrecks.wreck.WreckPlan;
import com.ninjacat.skies.driftwrecks.wreck.WreckRewards;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.AddReloadListenerEvent;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.server.ServerStoppedEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/** Game-bus hooks: the wreck and rift ticks, the thread catch, lures on the Tension Post, login sync, commands. */
public final class DriftEvents {
    @SubscribeEvent
    public void onServerTick(ServerTickEvent.Post e) {
        DriftManager.get(e.getServer()).tick(e.getServer());
        RiftManager.get(e.getServer()).tick(e.getServer());
        Tether.tick(e.getServer());
    }

    @SubscribeEvent
    public void onPlayerTick(PlayerTickEvent.Post e) {
        if (e.getEntity() instanceof ServerPlayer p && p.tickCount % 2 == 0) Tether.checkCatch(p);
    }

    @SubscribeEvent
    public void onLogin(PlayerEvent.PlayerLoggedInEvent e) {
        if (!(e.getEntity() instanceof ServerPlayer p)) return;
        WreckRewards.onJoin(p);
        RiftManager.get(p.server).onLogin(p);
    }

    @SubscribeEvent
    public void onRespawn(PlayerEvent.PlayerRespawnEvent e) {
        if (e.getEntity() instanceof ServerPlayer p && RiftManager.hasReturn(p)) RiftManager.get(p.server).onLogin(p);
    }

    /** A lure is hung on the Tension Post before the post handles the click. */
    @SubscribeEvent
    public void onUseBlock(PlayerInteractEvent.RightClickBlock e) {
        ItemStack stack = e.getItemStack();
        if (!(stack.getItem() instanceof DriftlureItem lure)) return;
        if (!(e.getLevel().getBlockState(e.getPos()).getBlock() instanceof TensionPostBlock)) return;
        e.setCanceled(true);
        e.setCancellationResult(InteractionResult.SUCCESS);
        if (e.getEntity() instanceof ServerPlayer p && lure.apply(p, stack) && !p.getAbilities().instabuild) stack.shrink(1);
    }

    @SubscribeEvent
    public void onReload(AddReloadListenerEvent e) { WreckPlan.clearCache(); }

    @SubscribeEvent
    public void onStopping(net.neoforged.neoforge.event.server.ServerStoppingEvent e) { Tether.flush(e.getServer()); }

    @SubscribeEvent
    public void onStopped(ServerStoppedEvent e) { Tether.clear(); }

    @SubscribeEvent
    public void onDeath(net.neoforged.neoforge.event.entity.living.LivingDeathEvent e) {
        if (e.getEntity().level() instanceof net.minecraft.server.level.ServerLevel sl && DriftManager.isWreckMob(e.getEntity()))
            DriftManager.get(sl.getServer()).mobGone(e.getEntity());
    }

    @SubscribeEvent
    public void onCommands(RegisterCommandsEvent e) { DriftCommands.register(e.getDispatcher()); }
}
