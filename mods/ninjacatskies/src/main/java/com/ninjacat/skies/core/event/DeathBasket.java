package com.ninjacat.skies.core.event;

import com.ninjacat.skies.core.block.ModBlocks;
import com.ninjacat.skies.core.block.YarnBasketBlockEntity;
import com.ninjacat.skies.core.config.SkiesConfig;
import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.living.LivingDropsEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * A player's death drops go into a Yarn Basket instead of scattering. Runs last, after Curios has added
 * its slots and after the Guardians stage has claimed its own deaths, and leaves the arena dimension alone
 * (rift chambers are cleared block by block, which would spill a basket there anyway).
 */
public final class DeathBasket {
    private static final String GROUND = "ninjacatskies_last_ground";
    private static final ResourceLocation ARENA = ResourceLocation.fromNamespaceAndPath("guardians", "arena");
    private static final int REACH = 4;

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onDrops(LivingDropsEvent event) {
        if (event.isCanceled() || !SkiesConfig.YARN_BASKET.get()) return;
        if (!(event.getEntity() instanceof ServerPlayer player) || event.getDrops().isEmpty()) return;
        if (player.level().dimension().location().equals(ARENA)) return;
        List<ItemStack> stacks = new ArrayList<>();
        for (ItemEntity drop : event.getDrops()) if (!drop.getItem().isEmpty()) stacks.add(drop.getItem());
        if (stacks.isEmpty()) return;
        UUID clowder = LoomTension.clowderOf(player).map(Clowder::id).orElse(null);
        Spot spot = spotFor(player);
        if (spot == null) return; // nowhere to put it: vanilla drops are better than nothing
        BlockPos at = stash(spot.level, spot.pos, player.getUUID(), player.getGameProfile().getName(), clowder, stacks);
        if (at == null) return;
        event.setCanceled(true);
        String where = at.getX() + ", " + at.getY() + ", " + at.getZ()
                + (spot.level.dimension() == Level.OVERWORLD ? "" : " in " + spot.level.dimension().location().getPath().replace('_', ' '));
        player.sendSystemMessage(NinjacatText.gold("Your things wait in a Yarn Basket at " + where + "."));
    }

    /** Remember the last block a player stood on, so a fall into the void leaves the basket at the edge. */
    @SubscribeEvent
    public void onTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || player.tickCount % 10 != 0) return;
        if (!player.onGround() || player.isSpectator() || player.level().dimension().location().equals(ARENA)) return;
        CompoundTag tag = new CompoundTag();
        tag.putLong("Pos", player.blockPosition().asLong());
        tag.putString("Dim", player.level().dimension().location().toString());
        player.getPersistentData().put(GROUND, tag);
    }

    private record Spot(ServerLevel level, BlockPos pos) {}

    @Nullable
    private static Spot spotFor(ServerPlayer player) {
        ServerLevel level = player.serverLevel();
        BlockPos died = player.blockPosition();
        if (died.getY() >= level.getMinBuildHeight() && died.getY() < level.getMaxBuildHeight()) return new Spot(level, died);
        // Fell out of the world: where they last stood, else their respawn point, else world spawn.
        CompoundTag ground = player.getPersistentData().getCompound(GROUND);
        if (ground.contains("Pos")) {
            ServerLevel l = player.server.getLevel(ResourceKey.create(Registries.DIMENSION, ResourceLocation.parse(ground.getString("Dim"))));
            if (l != null) return new Spot(l, BlockPos.of(ground.getLong("Pos")));
        }
        if (player.getRespawnPosition() != null) {
            ServerLevel l = player.server.getLevel(player.getRespawnDimension());
            if (l != null) return new Spot(l, player.getRespawnPosition());
        }
        ServerLevel overworld = player.server.overworld();
        return new Spot(overworld, overworld.getSharedSpawnPos());
    }

    /** Place a filled basket at or near {@code want}; null when there is no free block close by. */
    @Nullable
    public static BlockPos stash(ServerLevel level, BlockPos want, UUID owner, String ownerName, @Nullable UUID clowder, List<ItemStack> stacks) {
        BlockPos at = freeNear(level, want);
        if (at == null) return null;
        level.setBlock(at, ModBlocks.YARN_BASKET.get().defaultBlockState(), 3);
        if (!(level.getBlockEntity(at) instanceof YarnBasketBlockEntity basket)) return null;
        basket.fill(owner, ownerName, clowder, stacks);
        return at;
    }

    @Nullable
    private static BlockPos freeNear(ServerLevel level, BlockPos want) {
        int y0 = Math.max(level.getMinBuildHeight(), Math.min(level.getMaxBuildHeight() - 1, want.getY()));
        BlockPos base = new BlockPos(want.getX(), y0, want.getZ());
        for (int r = 0; r <= REACH; r++)
            for (int dy : new int[]{0, 1, -1, 2, 3})
                for (int dx = -r; dx <= r; dx++)
                    for (int dz = -r; dz <= r; dz++) {
                        if (Math.max(Math.abs(dx), Math.abs(dz)) != r) continue;
                        BlockPos p = base.offset(dx, dy, dz);
                        if (p.getY() < level.getMinBuildHeight() || p.getY() >= level.getMaxBuildHeight()) continue;
                        BlockState s = level.getBlockState(p);
                        if ((s.isAir() || s.canBeReplaced()) && level.getBlockEntity(p) == null) return p;
                    }
        return null;
    }
}
