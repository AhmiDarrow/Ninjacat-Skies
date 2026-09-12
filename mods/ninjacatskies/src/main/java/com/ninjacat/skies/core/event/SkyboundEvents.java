package com.ninjacat.skies.core.event;

import com.ninjacat.skies.core.NinjacatSkies;
import com.ninjacat.skies.core.config.SkiesConfig;
import com.ninjacat.skies.core.item.ModItems;
import com.ninjacat.skies.core.tension.ClowderLives;
import com.ninjacat.skies.core.tension.LoomTension;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
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
    private static final String EXHAUSTED = "skybound_exhausted";

    @SubscribeEvent
    public void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }

        CompoundTag persistent = player.getPersistentData();
        CompoundTag data = persistent.getCompound(ROOT);

        if (data.getBoolean(FLAG_JOINED)) {
            persistent.put(ROOT, data);
            enforceLives(player);
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
        enforceLives(player);

        player.displayClientMessage(NinjacatText.teal("Skybound. The Loom is cut. Start with Soil."), true);
        player.displayClientMessage(
                NinjacatText.gold("Island Charter in hand — Dock: Create Team. Pad chests restore kits after claim."),
                false
        );
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onDeath(LivingDeathEvent event) {
        if (!SkiesConfig.HARDCORE_LIVES_ENABLED.get() || event.isCanceled()
                || !(event.getEntity() instanceof ServerPlayer player)
                || player.isCreative() || player.isSpectator()) return;
        LoomTension.clowderOf(player).ifPresent(team -> {
            int lives = ClowderLives.spend(team, SkiesConfig.STARTING_LIVES.get());
            for (ServerPlayer member : team.onlineMembers()) {
                member.sendSystemMessage(NinjacatText.gold(player.getGameProfile().getName()
                        + " fell. Clowder lives remaining: " + lives));
                // The dying member's mode is applied after vanilla respawn.
                if (member != player) enforceLives(member);
            }
        });
    }

    @SubscribeEvent
    public void onRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) enforceLives(player);
    }

    @SubscribeEvent
    public void onClone(PlayerEvent.Clone event) {
        // NeoForge does not retain arbitrary persistent tags through player cloning.
        event.getEntity().getPersistentData().put(ROOT,
                event.getOriginal().getPersistentData().getCompound(ROOT).copy());
        event.getEntity().getPersistentData().putBoolean(EXHAUSTED,
                event.getOriginal().getPersistentData().getBoolean(EXHAUSTED));
    }

    @SubscribeEvent
    public void onTick(PlayerTickEvent.Post event) {
        if (event.getEntity() instanceof ServerPlayer player && player.tickCount % 20 == 0
                && player.isAlive()) enforceLives(player);
    }

    public static int remainingLives(ServerPlayer player) {
        return LoomTension.clowderOf(player)
                .map(team -> ClowderLives.remaining(team, SkiesConfig.STARTING_LIVES.get())).orElse(0);
    }

    private static void enforceLives(ServerPlayer player) {
        if (!SkiesConfig.HARDCORE_LIVES_ENABLED.get()) {
            // lives switched off: nobody stays a spectator for a pool that no longer counts
            if (player.getPersistentData().getBoolean(EXHAUSTED)) { player.getPersistentData().remove(EXHAUSTED); if (player.isSpectator()) { seatAtRespawnOrDock(player); player.setGameMode(GameType.SURVIVAL); } }
            return;
        }
        int lives = remainingLives(player);
        boolean teamDown = LoomTension.clowderOf(player).map(t -> ClowderLives.isExhausted(t, player.getUUID())).orElse(false);
        if ((lives == 0 || teamDown) && !player.isCreative()) {
            if (!player.isSpectator()) {
                player.getPersistentData().putBoolean(EXHAUSTED, true);
                player.setGameMode(GameType.SPECTATOR);
                player.sendSystemMessage(NinjacatText.gold(
                        "Your Clowder has spent its last life. A rare life reward or an operator revive can restore the pool."));
            }
        } else if (lives > 0 && !teamDown && player.getPersistentData().getBoolean(EXHAUSTED)) {
            player.getPersistentData().remove(EXHAUSTED);
            if (player.isSpectator()) {
                seatAtRespawnOrDock(player);
                player.setGameMode(GameType.SURVIVAL);
            }
        }
    }

    public static boolean awardLife(ServerPlayer player, String milestone) {
        if (!SkiesConfig.HARDCORE_LIVES_ENABLED.get()) return false;
        return LoomTension.clowderOf(player).map(team -> {
            if (!ClowderLives.award(team, SkiesConfig.STARTING_LIVES.get(), milestone)) return false;
            for (ServerPlayer member : team.onlineMembers()) {
                enforceLives(member);
                member.sendSystemMessage(NinjacatText.gold("A Thread of Return: +1 shared Clowder life. Remaining: "
                        + ClowderLives.remaining(team, SkiesConfig.STARTING_LIVES.get())));
            }
            return true;
        }).orElse(false);
    }

    public static int resetLives(ServerPlayer player) {
        return LoomTension.clowderOf(player)
                .map(team -> ClowderLives.reset(team, SkiesConfig.STARTING_LIVES.get())).orElse(0);
    }

    /** Restore the team's pool; offline exhausted members recover on their next login. */
    public static int revivePlayer(ServerPlayer player) {
        if (!SkiesConfig.HARDCORE_LIVES_ENABLED.get()) return -1;
        int lives = resetLives(player);
        player.getPersistentData().remove(EXHAUSTED);
        LoomTension.clowderOf(player).ifPresent(team -> {
            for (ServerPlayer member : team.onlineMembers()) {
                member.getPersistentData().remove(EXHAUSTED);
                enforceLives(member);
            }
        });
        player.sendSystemMessage(NinjacatText.gold("Clowder revive — shared lives restored: " + lives));
        return lives;
    }

    /** Overweaver shuttle: +1 shared life and stand this mate back up. Other exhausted mates stay down. */
    public static int restoreOneLife(ServerPlayer player) {
        if (!SkiesConfig.HARDCORE_LIVES_ENABLED.get()) return -1;
        return LoomTension.clowderOf(player).map(team -> {
            int lives = ClowderLives.restoreOne(team, player.getUUID(), SkiesConfig.STARTING_LIVES.get());
            player.getPersistentData().remove(EXHAUSTED);
            enforceLives(player);
            return lives;
        }).orElse(-1);
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
