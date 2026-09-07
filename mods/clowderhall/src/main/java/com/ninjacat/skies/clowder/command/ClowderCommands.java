package com.ninjacat.skies.clowder.command;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.ninjacat.skies.clowder.util.ClowderTeams;
import com.ninjacat.skies.clowder.world.ModDimensions;
import com.ninjacat.skies.core.event.SkyboundEvents;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import net.minecraft.network.chat.TextColor;
import net.minecraft.server.level.ServerPlayer;

public final class ClowderCommands {
    private ClowderCommands() {}

    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(
                Commands.literal("clowder")
                        .executes(ClowderCommands::help)
                        .then(Commands.literal("help").executes(ClowderCommands::help))
                        .then(Commands.literal("hub").executes(ClowderCommands::hubTeleport))
                        .then(Commands.literal("return").executes(ClowderCommands::returnFromHub))
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

    /** Solo / no-arg path — spectator self-revive for SSP and lone pads. */
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

    private static Component teal(String key) {
        return Component.translatable(key).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(NinjacatText.TEAL)));
    }

    private static Component gold(String key) {
        return Component.translatable(key).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(NinjacatText.GOLD)));
    }
}
