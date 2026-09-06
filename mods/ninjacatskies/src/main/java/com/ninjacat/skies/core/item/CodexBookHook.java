package com.ninjacat.skies.core.item;

import com.klikli_dev.modonomicon.networking.OpenBookOnClientMessage;
import com.ninjacat.skies.core.NinjacatSkies;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.PacketDistributor;

/** Opens the Whisker Codex book. Only touched when Modonomicon is loaded — never reference directly. */
final class CodexBookHook {
    static final ResourceLocation BOOK = ResourceLocation.fromNamespaceAndPath(NinjacatSkies.MOD_ID, "whisker_codex");

    private CodexBookHook() {}

    static boolean open(ServerPlayer player) {
        try {
            PacketDistributor.sendToPlayer(player, new OpenBookOnClientMessage(BOOK));
            return true;
        } catch (Throwable t) {
            NinjacatSkies.LOGGER.warn("Could not open the Whisker Codex book", t);
            return false;
        }
    }
}
