package com.ninjacat.skies.core.event;

import com.ninjacat.skies.core.NinjacatSkies;
import com.ninjacat.skies.core.config.SkiesConfig;
import com.ninjacat.skies.core.item.ModItems;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.portal.DimensionTransition;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;

public final class SkyboundEvents {
    private static final String ROOT = NinjacatSkies.MOD_ID;
    private static final String FLAG_JOINED = "received_skybound_kit";
    private static final String LIVES_KEY = "skybound_lives";
    private static final String LIVES_INIT = "skybound_lives_init";

    @SubscribeEvent
    public void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }

        CompoundTag persistent = player.getPersistentData();
        CompoundTag data = persistent.getCompound(ROOT);

        ensureLivesInitialized(player, data);

        if (data.getBoolean(FLAG_JOINED)) {
            persistent.put(ROOT, data);
            return;
        }

        if (SkiesConfig.GIVE_CODEX_ON_JOIN.get()) {
            giveOrDrop(player, new ItemStack(ModItems.WHISKER_CODEX.get()));
        }

        // Soft deps — Clowder Hall jars ship with the pack; registry miss is fine solo.
        giveOptional(player, "clowderhall:island_charter", 1);
        giveOptional(player, "clowderhall:hub_key", 1);

        String preset = SkiesConfig.DIFFICULTY_PRESET.get().toLowerCase();
        switch (preset) {
            case "easy" -> {
                giveOrDrop(player, new ItemStack(Items.BREAD, 8));
                giveOrDrop(player, new ItemStack(Items.OAK_SAPLING, 2));
                giveOrDrop(player, new ItemStack(Items.BONE_MEAL, 8));
                giveOrDrop(player, new ItemStack(ModItems.FRAYED_THREAD.get(), 4));
            }
            case "hard" -> {
                // Sparse: Codex + Charter/Hub Key. Island template carries the rest.
            }
            default -> {
                giveOrDrop(player, new ItemStack(Items.BREAD, 4));
                giveOrDrop(player, new ItemStack(Items.OAK_SAPLING, 1));
                // Enough Thread to unravel → string → first Void Yarn without softlock.
                giveOrDrop(player, new ItemStack(ModItems.FRAYED_THREAD.get(), 6));
            }
        }

        data.putBoolean(FLAG_JOINED, true);
        persistent.put(ROOT, data);

        player.displayClientMessage(NinjacatText.teal("Skybound. The Loom is cut. Start with Soil."), true);
        player.displayClientMessage(
                NinjacatText.gold("Island Charter in hand — Dock: Create Team. Pad chests restore kits after claim."),
                false
        );
    }

    @SubscribeEvent
    public void onDeath(LivingDeathEvent event) {
        if (!SkiesConfig.HARDCORE_LIVES_ENABLED.get()) {
            return;
        }
        if (!(event.getEntity() instanceof ServerPlayer player) || event.isCanceled()) {
            return;
        }

        CompoundTag data = player.getPersistentData().getCompound(ROOT);
        ensureLivesInitialized(player, data);
        int lives = data.getInt(LIVES_KEY);
        if (lives <= 0) {
            return;
        }

        lives -= 1;
        data.putInt(LIVES_KEY, lives);
        player.getPersistentData().put(ROOT, data);
        // Spectator applied on respawn — death-time gamemode is overwritten by vanilla respawn.
    }

    @SubscribeEvent
    public void onRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (!SkiesConfig.HARDCORE_LIVES_ENABLED.get()) {
            return;
        }
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        CompoundTag data = player.getPersistentData().getCompound(ROOT);
        ensureLivesInitialized(player, data);
        int lives = data.getInt(LIVES_KEY);
        if (lives <= 0) {
            player.setGameMode(GameType.SPECTATOR);
            player.displayClientMessage(
                    NinjacatText.gold("Last life spent. Spectator — /clowder revive (self), mate /clowder revive <you>, or op /skybound revive."),
                    false
            );
        } else {
            player.displayClientMessage(
                    NinjacatText.teal("Skybound lives remaining: " + lives),
                    false
            );
        }
    }

    private static void ensureLivesInitialized(ServerPlayer player, CompoundTag data) {
        if (!SkiesConfig.HARDCORE_LIVES_ENABLED.get() || data.getBoolean(LIVES_INIT)) {
            return;
        }
        data.putInt(LIVES_KEY, SkiesConfig.STARTING_LIVES.get());
        data.putBoolean(LIVES_INIT, true);
        player.displayClientMessage(
                NinjacatText.gold("Soft hardcore on — starting lives: " + SkiesConfig.STARTING_LIVES.get()),
                false
        );
    }

    /** Restores starting lives. Caller must check config. */
    public static int resetLives(ServerPlayer player) {
        CompoundTag data = player.getPersistentData().getCompound(ROOT);
        int lives = SkiesConfig.STARTING_LIVES.get();
        data.putInt(LIVES_KEY, lives);
        data.putBoolean(LIVES_INIT, true);
        player.getPersistentData().put(ROOT, data);
        return lives;
    }

    /**
     * Full soft-hardcore revive: reset lives, seat at respawn/Dock, Survival.
     * @return restored life count, or -1 if lives are disabled
     */
    public static int revivePlayer(ServerPlayer player) {
        if (!SkiesConfig.HARDCORE_LIVES_ENABLED.get()) {
            return -1;
        }
        int lives = resetLives(player);
        seatAtRespawnOrDock(player);
        if (player.isSpectator()) {
            player.setGameMode(GameType.SURVIVAL);
        }
        player.displayClientMessage(NinjacatText.gold("Skybound revive — lives restored."), false);
        return lives;
    }

    public static void seatAtRespawnOrDock(ServerPlayer player) {
        BlockPos respawn = player.getRespawnPosition();
        ServerLevel level = null;
        double x = 0;
        double y = 0;
        double z = 0;
        if (respawn != null) {
            level = player.server.getLevel(player.getRespawnDimension());
            x = respawn.getX() + 0.5;
            y = respawn.getY();
            z = respawn.getZ() + 0.5;
        }
        if (level == null) {
            level = player.server.overworld();
            BlockPos spawn = level.getSharedSpawnPos();
            x = spawn.getX() + 0.5;
            y = spawn.getY();
            z = spawn.getZ() + 0.5;
        }
        player.changeDimension(new DimensionTransition(
                level,
                new Vec3(x, y, z),
                Vec3.ZERO,
                player.getYRot(),
                player.getXRot(),
                DimensionTransition.DO_NOTHING
        ));
    }

    private static void giveOptional(ServerPlayer player, String id, int count) {
        Item item = BuiltInRegistries.ITEM.getOptional(ResourceLocation.parse(id)).orElse(null);
        if (item != null && item != Items.AIR) {
            giveOrDrop(player, new ItemStack(item, count));
        }
    }

    private static void giveOrDrop(ServerPlayer player, ItemStack stack) {
        if (!player.addItem(stack)) {
            player.drop(stack, false);
        }
    }
}
