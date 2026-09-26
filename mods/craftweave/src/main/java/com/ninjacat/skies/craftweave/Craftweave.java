package com.ninjacat.skies.craftweave;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerContainerEvent;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;

/**
 * Craftweave: a better crafting table. When several recipes share a grid, a button beside the result cycles between
 * them (and the choice is remembered); a small box under the result crafts a typed number of items in one click; and
 * a few favourite recipes wait on a tab at the side of the table. Nothing appears unless it has something to do.
 */
@Mod(Craftweave.MOD_ID)
public final class Craftweave {
    public static final String MOD_ID = "craftweave";

    public Craftweave(IEventBus modBus) {
        modBus.addListener(Craftweave::payloads);
        NeoForge.EVENT_BUS.addListener((PlayerContainerEvent.Open event) -> {
            if (event.getEntity() instanceof ServerPlayer player && CraftTables.isTable(event.getContainer())) {
                CraftTables.owned(event.getContainer(), player);
                CraftTables.applyPick(event.getContainer(), player);
            }
        });
        NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.event.RegisterCommandsEvent event) -> com.ninjacat.skies.craftweave.verification.SelfTest.register(event.getDispatcher()));
        if (FMLEnvironment.dist.isClient()) com.ninjacat.skies.craftweave.client.CraftweaveClient.init(modBus);
    }

    private static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MOD_ID, path);
    }

    /** Client to server: show the next (+1) or previous (-1) of the recipes that match the grid. */
    public record Cycle(int containerId, int direction) implements CustomPacketPayload {
        public static final Type<Cycle> TYPE = new Type<>(id("cycle"));
        public static final StreamCodec<FriendlyByteBuf, Cycle> STREAM_CODEC = CustomPacketPayload.codec(
                (v, b) -> { b.writeVarInt(v.containerId); b.writeByte(v.direction); }, b -> new Cycle(b.readVarInt(), b.readByte()));
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** Client to server: craft this many items from the grid, into the pack. */
    public record Craft(int containerId, int count) implements CustomPacketPayload {
        public static final Type<Craft> TYPE = new Type<>(id("craft"));
        public static final StreamCodec<FriendlyByteBuf, Craft> STREAM_CODEC = CustomPacketPayload.codec(
                (v, b) -> { b.writeVarInt(v.containerId); b.writeVarInt(v.count); }, b -> new Craft(b.readVarInt(), b.readVarInt()));
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** Client to server: lay this (bookmarked) recipe out on the grid from the pack. */
    public record Place(int containerId, ResourceLocation recipe, boolean all) implements CustomPacketPayload {
        public static final Type<Place> TYPE = new Type<>(id("place"));
        public static final StreamCodec<FriendlyByteBuf, Place> STREAM_CODEC = CustomPacketPayload.codec(
                (v, b) -> { b.writeVarInt(v.containerId); b.writeResourceLocation(v.recipe); b.writeBoolean(v.all); },
                b -> new Place(b.readVarInt(), b.readResourceLocation(), b.readBoolean()));
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    /** Client to server: put everything on the grid back into the pack. */
    public record Clear(int containerId) implements CustomPacketPayload {
        public static final Type<Clear> TYPE = new Type<>(id("clear"));
        public static final StreamCodec<FriendlyByteBuf, Clear> STREAM_CODEC = CustomPacketPayload.codec(
                (v, b) -> b.writeVarInt(v.containerId), b -> new Clear(b.readVarInt()));
        @Override public Type<? extends CustomPacketPayload> type() { return TYPE; }
    }

    private static void payloads(RegisterPayloadHandlersEvent event) {
        var registrar = event.registrar("1").optional();
        registrar.playToServer(Cycle.TYPE, Cycle.STREAM_CODEC, (payload, context) -> {
            if (context.player() instanceof ServerPlayer player && player.containerMenu.containerId == payload.containerId())
                CraftTables.cycle(player, payload.direction());
        });
        registrar.playToServer(Place.TYPE, Place.STREAM_CODEC, (payload, context) -> {
            if (context.player() instanceof ServerPlayer player && player.containerMenu.containerId == payload.containerId() && !player.isSpectator())
                CraftTables.place(player, payload.recipe(), payload.all());
        });
        registrar.playToServer(Clear.TYPE, Clear.STREAM_CODEC, (payload, context) -> {
            if (context.player() instanceof ServerPlayer player && player.containerMenu.containerId == payload.containerId() && !player.isSpectator())
                CraftTables.clear(player);
        });
        registrar.playToServer(Craft.TYPE, Craft.STREAM_CODEC, (payload, context) -> {
            if (context.player() instanceof ServerPlayer player && player.containerMenu.containerId == payload.containerId() && !player.isSpectator())
                CraftTables.craft(player, payload.count());
        });
    }
}
