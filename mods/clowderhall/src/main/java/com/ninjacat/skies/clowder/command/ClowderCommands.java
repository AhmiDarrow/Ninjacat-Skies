package com.ninjacat.skies.clowder.command;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.ninjacat.skies.clowder.team.ClowderSync;
import com.ninjacat.skies.clowder.team.SkyTeams;
import com.ninjacat.skies.clowder.util.ClowderTeams;
import com.ninjacat.skies.clowder.world.ModDimensions;
import com.ninjacat.skies.core.event.SkyboundEvents;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.Style;
import net.minecraft.network.chat.TextColor;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.fml.ModList;

public final class ClowderCommands {
    private ClowderCommands() {}

    private static final boolean SKY = ModList.get().isLoaded("skyblockbuilder");

    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(
                Commands.literal("clowder")
                        .executes(ClowderCommands::help)
                        .then(Commands.literal("help").executes(ClowderCommands::help))
                        .then(Commands.literal("hub").executes(ClowderCommands::hubTeleport))
                        .then(Commands.literal("return").executes(ClowderCommands::returnFromHub))
                        .then(Commands.literal("invite")
                                .then(Commands.argument("player", EntityArgument.player())
                                        .executes(ClowderCommands::invite)))
                        .then(Commands.literal("accept").executes(ClowderCommands::accept))
                        .then(Commands.literal("revive")
                                .requires(source -> source.hasPermission(2))
                                .executes(ClowderCommands::reviveSelf)
                                .then(Commands.argument("player", EntityArgument.player())
                                        .executes(ClowderCommands::reviveMate)))
                        .then(Commands.literal("resetisland")
                                .requires(source -> source.hasPermission(2))
                                .executes(ClowderCommands::resetHint))
        );
    }

    private static int help(CommandContext<CommandSourceStack> ctx) {
        CommandSourceStack source = ctx.getSource();
        source.sendSuccess(() -> teal("command.clowderhall.help.hub"), false);
        source.sendSuccess(() -> teal("command.clowderhall.help.return"), false);
        source.sendSuccess(() -> teal("command.clowderhall.help.invite"), false);
        source.sendSuccess(() -> teal("command.clowderhall.help.revive"), false);
        source.sendSuccess(() -> teal("command.clowderhall.help.resetisland"), false);
        source.sendSuccess(() -> gold("command.clowderhall.help.charter"), false);
        return 1;
    }

    private static int hubTeleport(CommandContext<CommandSourceStack> ctx) {
        if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
            ctx.getSource().sendFailure(teal("command.clowderhall.players_only"));
            return 0;
        }
        return ModDimensions.travelToHub(player) ? 1 : 0;
    }

    private static int returnFromHub(CommandContext<CommandSourceStack> ctx) {
        if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
            ctx.getSource().sendFailure(teal("command.clowderhall.players_only"));
            return 0;
        }
        return ModDimensions.returnFromHub(player) ? 1 : 0;
    }

    /** Invite another player to your Clowder — no operator needed. */
    private static int invite(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        if (!(ctx.getSource().getEntity() instanceof ServerPlayer actor)) {
            ctx.getSource().sendFailure(teal("command.clowderhall.players_only"));
            return 0;
        }
        if (!SKY) {
            ctx.getSource().sendFailure(gold("message.clowderhall.invite_no_skyblock"));
            return 0;
        }
        ServerPlayer target = EntityArgument.getPlayer(ctx, "player");
        return ClowderCommands.doInvite(actor, target) ? 1 : 0;
    }

    /** Shared by the /clowder invite command and the Charter's right-click-on-player. */
    public static boolean doInvite(ServerPlayer actor, ServerPlayer target) {
        if (!SKY) {
            actor.sendSystemMessage(gold("message.clowderhall.invite_no_skyblock"));
            return false;
        }
        int result = SkyTeams.invite(actor.server, actor, target);
        switch (result) {
            case SkyTeams.OK -> {
                actor.sendSystemMessage(teal("message.clowderhall.invite_sent", target.getDisplayName()));
                target.sendSystemMessage(acceptPrompt(actor.getDisplayName()));
                return true;
            }
            case SkyTeams.NO_TEAM -> actor.sendSystemMessage(gold("message.clowderhall.invite_no_team"));
            case SkyTeams.TARGET_TEAM -> actor.sendSystemMessage(gold("message.clowderhall.invite_target_has_team"));
            default -> actor.sendSystemMessage(gold("message.clowderhall.invite_failed"));
        }
        return false;
    }

    /** Accept a pending Clowder invitation — no operator needed. */
    private static int accept(CommandContext<CommandSourceStack> ctx) {
        if (!(ctx.getSource().getEntity() instanceof ServerPlayer actor)) {
            ctx.getSource().sendFailure(teal("command.clowderhall.players_only"));
            return 0;
        }
        if (!SKY) {
            ctx.getSource().sendFailure(gold("message.clowderhall.invite_no_skyblock"));
            return 0;
        }
        int result = SkyTeams.accept(actor.server, actor);
        switch (result) {
            case SkyTeams.OK -> {
                ClowderSync.reconcilePlayer(actor.server, actor.getUUID());
                actor.sendSystemMessage(teal("message.clowderhall.accept_ok"));
                return 1;
            }
            case SkyTeams.NO_TEAM -> ctx.getSource().sendFailure(gold("message.clowderhall.accept_none"));
            case SkyTeams.TARGET_TEAM -> ctx.getSource().sendFailure(gold("message.clowderhall.accept_has_team"));
            default -> ctx.getSource().sendFailure(gold("message.clowderhall.accept_failed"));
        }
        return 0;
    }

    private static int reviveSelf(CommandContext<CommandSourceStack> ctx) {
        if (!(ctx.getSource().getEntity() instanceof ServerPlayer actor)) {
            ctx.getSource().sendFailure(teal("command.clowderhall.players_only"));
            return 0;
        }
        if (!actor.isSpectator()) {
            ctx.getSource().sendFailure(teal("message.clowderhall.revive_self_not_spectator"));
            return 0;
        }
        int lives = SkyboundEvents.revivePlayer(actor);
        if (lives < 0) {
            ctx.getSource().sendFailure(teal("message.clowderhall.revive_disabled"));
            return 0;
        }
        ctx.getSource().sendSuccess(
                () -> NinjacatText.teal("Self-revive complete — lives: " + lives),
                true
        );
        return 1;
    }

    private static int reviveMate(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        if (!(ctx.getSource().getEntity() instanceof ServerPlayer actor)) {
            ctx.getSource().sendFailure(teal("command.clowderhall.players_only"));
            return 0;
        }
        ServerPlayer target = EntityArgument.getPlayer(ctx, "player");
        if (actor.getUUID().equals(target.getUUID())) {
            return reviveSelf(ctx);
        }
        if (!ClowderTeams.sameClowder(actor, target)) {
            ctx.getSource().sendFailure(teal("message.clowderhall.revive_not_mate"));
            return 0;
        }
        if (!target.isSpectator()) {
            ctx.getSource().sendFailure(teal("message.clowderhall.revive_not_spectator"));
            return 0;
        }
        int lives = SkyboundEvents.revivePlayer(target);
        if (lives < 0) {
            ctx.getSource().sendFailure(teal("message.clowderhall.revive_disabled"));
            return 0;
        }
        ctx.getSource().sendSuccess(
                () -> NinjacatText.teal("Revived Clowder mate " + target.getGameProfile().getName() + " — lives: " + lives),
                true
        );
        target.displayClientMessage(
                NinjacatText.gold(actor.getGameProfile().getName() + " pulled you back — Skybound lives restored."),
                false
        );
        return 1;
    }

    private static int resetHint(CommandContext<CommandSourceStack> ctx) {
        CommandSourceStack source = ctx.getSource();
        source.sendSuccess(() -> gold("command.clowderhall.reset.header"), false);
        source.sendSuccess(() -> teal("command.clowderhall.reset.team"), false);
        source.sendSuccess(() -> teal("command.clowderhall.reset.travel"), false);
        source.sendSuccess(() -> teal("command.clowderhall.reset.ops"), false);
        return 1;
    }

    /** Invitation line with a clickable "/clowder accept". */
    private static MutableComponent acceptPrompt(Component inviterName) {
        MutableComponent line = Component.translatable("message.clowderhall.invite_received", inviterName)
                .withStyle(Style.EMPTY.withColor(TextColor.fromRgb(NinjacatText.GOLD)));
        return line.withStyle(s -> s
                .withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND, "/clowder accept"))
                .withUnderlined(true));
    }

    private static Component teal(String key) {
        return Component.translatable(key).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(NinjacatText.TEAL)));
    }

    private static Component teal(String key, Object arg) {
        return Component.translatable(key, arg).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(NinjacatText.TEAL)));
    }

    private static Component gold(String key) {
        return Component.translatable(key).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(NinjacatText.GOLD)));
    }
}
