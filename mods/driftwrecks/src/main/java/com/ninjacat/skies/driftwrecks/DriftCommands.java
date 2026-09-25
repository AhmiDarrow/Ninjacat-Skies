package com.ninjacat.skies.driftwrecks;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.wreck.*;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.server.level.ServerPlayer;

import java.util.Optional;

/**
 * /driftwreck list | summon [core] [skin] [modifier] [objective] [tier] | heartwreck | unravel &lt;id&gt; |
 * pressure &lt;player&gt; &lt;ticks&gt; | atlas &lt;player&gt; fill — testing and server admin.
 */
public final class DriftCommands {
    private DriftCommands() {}

    public static void register(CommandDispatcher<CommandSourceStack> d) {
        d.register(Commands.literal("driftwreck").requires(s -> s.hasPermission(2))
                .then(Commands.literal("list").executes(DriftCommands::list))
                .then(Commands.literal("summon").executes(c -> summon(c, null, null, null, null, null))
                        .then(Commands.argument("core", StringArgumentType.word()).executes(c -> summon(c, arg(c, "core"), null, null, null, null))
                                .then(Commands.argument("skin", StringArgumentType.word()).executes(c -> summon(c, arg(c, "core"), arg(c, "skin"), null, null, null))
                                        .then(Commands.argument("modifier", StringArgumentType.word()).executes(c -> summon(c, arg(c, "core"), arg(c, "skin"), arg(c, "modifier"), null, null))
                                                .then(Commands.argument("objective", StringArgumentType.word()).executes(c -> summon(c, arg(c, "core"), arg(c, "skin"), arg(c, "modifier"), arg(c, "objective"), null))
                                                        .then(Commands.argument("tier", StringArgumentType.word()).executes(c -> summon(c, arg(c, "core"), arg(c, "skin"), arg(c, "modifier"), arg(c, "objective"), arg(c, "tier")))))))))
                .then(Commands.literal("heartwreck").executes(DriftCommands::heart))
                .then(Commands.literal("unravel").then(Commands.argument("id", IntegerArgumentType.integer(1)).executes(DriftCommands::unravel)))
                .then(Commands.literal("expire").then(Commands.argument("id", IntegerArgumentType.integer(1)).executes(DriftCommands::expire)))
                .then(Commands.literal("pressure").then(Commands.argument("player", EntityArgument.player())
                        .then(Commands.argument("ticks", IntegerArgumentType.integer(0)).executes(DriftCommands::pressure))))
                .then(Commands.literal("atlas").then(Commands.argument("player", EntityArgument.player())
                        .then(Commands.literal("fill").executes(DriftCommands::atlasFill)))));
    }

    private static String arg(CommandContext<CommandSourceStack> c, String n) { return StringArgumentType.getString(c, n); }

    private static int list(CommandContext<CommandSourceStack> c) {
        DriftManager m = DriftManager.get(c.getSource().getServer());
        c.getSource().sendSuccess(() -> NinjacatText.goldKey("message.driftwrecks.command.list_header", m.size()), false);
        for (Wreck w : m.wrecks()) c.getSource().sendSuccess(() -> NinjacatText.teal("#" + w.id + " " + w.planId + " " + w.skin.id() + " " + w.modifier.id + " " + w.objective.id // lang-exempt: operator debug dump of wreck ids and ticks
                + " " + w.phase + " " + w.age / 20 + "/" + w.lifetime / 20 + "s at " + w.center().toShortString() + (w.objectiveDone ? " (done)" : "")), false);
        return m.size();
    }

    private static int summon(CommandContext<CommandSourceStack> c, String core, String skin, String mod, String obj, String tier) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer p = c.getSource().getPlayerOrException();
        Optional<Clowder> cl = LoomTension.clowderOf(p);
        if (cl.isEmpty()) return 0;
        DriftManager m = DriftManager.get(p.server);
        Wreck old = m.byTeam(cl.get().id());
        if (old != null) { c.getSource().sendFailure(NinjacatText.tealKey("message.driftwrecks.command.already_has", old.id, old.id)); return 0; }
        DriftManager.Roll r = new DriftManager.Roll(core == null ? null : WreckCore.byId(core), skin == null ? null : Strand.byId(skin),
                mod == null ? null : WreckModifier.byId(mod), obj == null ? null : WreckObjective.byId(obj), tier == null ? null : WreckTier.byId(tier), false,
                LoomTension.postOf(cl.get()) == null ? p.blockPosition().offset(40, 0, 0) : null);
        if (r.tier() == null && LoomTension.strandBits(cl.get()) == 0) r = new DriftManager.Roll(r.core(), r.skin(), r.modifier(), r.objective(), WreckTier.RAFT, false, r.origin());
        Wreck w = m.arrive(p.server, cl.get(), r);
        if (w == null) { c.getSource().sendFailure(NinjacatText.tealKey("message.driftwrecks.command.no_land")); return 0; }
        c.getSource().sendSuccess(() -> NinjacatText.goldKey("message.driftwrecks.command.spawned", w.id, w.center().toShortString()), true);
        return w.id;
    }

    private static int heart(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer p = c.getSource().getPlayerOrException();
        Optional<Clowder> cl = LoomTension.clowderOf(p);
        if (cl.isEmpty()) return 0;
        Wreck w = DriftManager.get(p.server).arrive(p.server, cl.get(), new DriftManager.Roll(null, Strand.SPINDLE, null, null, null, true,
                LoomTension.postOf(cl.get()) == null ? p.blockPosition().offset(60, 0, 0) : null));
        if (w == null) { c.getSource().sendFailure(NinjacatText.tealKey("message.driftwrecks.command.heart_no_land")); return 0; }
        c.getSource().sendSuccess(() -> NinjacatText.goldKey("message.driftwrecks.command.heart_spawned", w.center().toShortString()), true);
        return 1;
    }

    private static int unravel(CommandContext<CommandSourceStack> c) {
        DriftManager m = DriftManager.get(c.getSource().getServer());
        Wreck w = m.byId(IntegerArgumentType.getInteger(c, "id"));
        if (w == null) { c.getSource().sendFailure(NinjacatText.tealKey("message.driftwrecks.command.no_such_wreck")); return 0; }
        m.beginUnravel(DriftManager.level(c.getSource().getServer()), w, false);
        c.getSource().sendSuccess(() -> NinjacatText.goldKey("message.driftwrecks.command.unravelling", w.id), true);
        return 1;
    }

    /** Jump a wreck's clock to its last moments, for testing the warnings and the crumble. */
    private static int expire(CommandContext<CommandSourceStack> c) {
        Wreck w = DriftManager.get(c.getSource().getServer()).byId(IntegerArgumentType.getInteger(c, "id"));
        if (w == null) return 0;
        w.age = Math.max(w.age, (int) (w.lifetime * 0.94F));
        DriftManager.get(c.getSource().getServer()).markDirty();
        return 1;
    }

    private static int pressure(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer p = EntityArgument.getPlayer(c, "player");
        int ticks = IntegerArgumentType.getInteger(c, "ticks");
        LoomTension.clowderOf(p).ifPresent(cl -> { TeamDrift t = TeamDrift.of(cl); t.setPressure(ticks); t.dirty(); });
        c.getSource().sendSuccess(() -> NinjacatText.goldKey("message.driftwrecks.command.pressure_set", ticks), true);
        return 1;
    }

    private static int atlasFill(CommandContext<CommandSourceStack> c) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer p = EntityArgument.getPlayer(c, "player");
        LoomTension.clowderOf(p).ifPresent(cl -> {
            TeamDrift t = TeamDrift.of(cl);
            for (Strand s : Strand.ALL) for (WreckCore core : WreckCore.ALL) t.fillCell(s, core);
            for (WreckModifier mo : WreckModifier.ALL) t.stampModifier(mo);
            if (t.heartwreck() == 0) t.setHeartwreck(1);
            t.dirty();
            WreckRewards.syncAll(cl);
            for (ServerPlayer m : cl.onlineMembers()) WreckRewards.onJoin(m);
        });
        return 1;
    }
}
