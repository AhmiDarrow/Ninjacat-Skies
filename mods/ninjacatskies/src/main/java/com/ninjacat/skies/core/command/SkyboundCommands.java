package com.ninjacat.skies.core.command;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.ninjacat.skies.core.event.SkyboundEvents;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.server.level.ServerPlayer;

public final class SkyboundCommands {
    private SkyboundCommands() {}

    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(
                Commands.literal("skybound")
                        .then(Commands.literal("revive")
                                .requires(source -> source.hasPermission(2))
                                .executes(SkyboundCommands::reviveSelf)
                                .then(Commands.argument("player", EntityArgument.player())
                                        .executes(SkyboundCommands::reviveOther)))
        );
    }

    private static int reviveSelf(CommandContext<CommandSourceStack> ctx) {
        if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
            ctx.getSource().sendFailure(NinjacatText.gold("Players only."));
            return 0;
        }
        return revive(ctx.getSource(), player);
    }

    private static int reviveOther(CommandContext<CommandSourceStack> ctx) throws CommandSyntaxException {
        ServerPlayer target = EntityArgument.getPlayer(ctx, "player");
        return revive(ctx.getSource(), target);
    }

    private static int revive(CommandSourceStack source, ServerPlayer player) {
        int lives = SkyboundEvents.revivePlayer(player);
        if (lives < 0) {
            source.sendFailure(NinjacatText.gold("Soft hardcore lives are disabled in config."));
            return 0;
        }
        source.sendSuccess(
                () -> NinjacatText.teal("Revived " + player.getGameProfile().getName() + " — lives: " + lives),
                true
        );
        return 1;
    }
}
