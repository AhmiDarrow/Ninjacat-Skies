package com.ninjacat.skies.guardians;

import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.logging.LogUtils;
import com.ninjacat.skies.guardians.arena.ArenaData;
import com.ninjacat.skies.guardians.arena.ArenaManager;
import com.ninjacat.skies.guardians.entity.ModEntities;
import com.ninjacat.skies.guardians.item.ModItems;
import com.ninjacat.skies.guardians.relic.RelicEvents;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.commands.Commands;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.AddReloadListenerEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import org.slf4j.Logger;

@Mod(Guardians.MOD_ID)
public final class Guardians {
    public static final String MOD_ID = "guardians";
    public static final Logger LOGGER = LogUtils.getLogger();

    public Guardians(IEventBus modBus) {
        ModEntities.ENTITIES.register(modBus);
        ModItems.ITEMS.register(modBus);
        ModItems.TABS.register(modBus);
        modBus.addListener(ModEntities::attributes);
        NeoForge.EVENT_BUS.register(new RelicEvents());
        NeoForge.EVENT_BUS.addListener(this::onServerTick);
        NeoForge.EVENT_BUS.addListener(this::onLogin);
        NeoForge.EVENT_BUS.addListener(this::onDeath);
        NeoForge.EVENT_BUS.addListener(this::onCommands);
        NeoForge.EVENT_BUS.addListener((AddReloadListenerEvent e) -> ArenaData.clearCache());
        LOGGER.info("Snapped Guardians: thirteen arenas woven");
    }

    private void onServerTick(ServerTickEvent.Post e) { ArenaManager.get(e.getServer()).tick(e.getServer()); }
    private void onLogin(PlayerEvent.PlayerLoggedInEvent e) { if (e.getEntity() instanceof ServerPlayer p) ArenaManager.get(p.server).onLogin(p); }
    private void onDeath(LivingDeathEvent e) { if (e.getEntity() instanceof ServerPlayer p) ArenaManager.get(p.server).onDeath(p); }

    private void onCommands(RegisterCommandsEvent e) {
        e.getDispatcher().register(Commands.literal("guardians")
                .then(Commands.literal("leave").executes(ctx -> {
                    if (ctx.getSource().getEntity() instanceof ServerPlayer p) { ArenaManager.get(p.server).leave(p); return 1; }
                    return 0;
                }))
                .then(Commands.literal("summon").requires(s -> s.hasPermission(2))
                        .then(Commands.argument("guardian", StringArgumentType.word()).executes(ctx -> {
                            GuardianKind k = GuardianKind.byId(StringArgumentType.getString(ctx, "guardian"));
                            if (k == null || !(ctx.getSource().getEntity() instanceof ServerPlayer p)) { ctx.getSource().sendFailure(NinjacatText.teal("Unknown guardian.")); return 0; }
                            String fail = ArenaManager.get(p.server).summon(p, k);
                            if (fail != null) { ctx.getSource().sendFailure(NinjacatText.teal(fail)); return 0; }
                            return 1;
                        })))
                .then(Commands.literal("status").executes(ctx -> {
                    var m = ArenaManager.get(ctx.getSource().getServer());
                    ctx.getSource().sendSuccess(() -> NinjacatText.gold("Arenas running: " + m.instances().size()), false);
                    for (var a : m.instances()) ctx.getSource().sendSuccess(() -> NinjacatText.teal("slot " + a.slot + " " + a.kind.id + " " + a.state + " party " + a.party.size() + " inside " + a.onlinePlayers().size()), false);
                    return 1;
                })));
    }
}
