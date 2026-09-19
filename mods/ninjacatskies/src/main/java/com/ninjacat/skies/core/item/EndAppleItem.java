package com.ninjacat.skies.core.item;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import net.minecraft.network.chat.TextColor;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.feature.EndPlatformFeature;
import net.minecraft.world.level.portal.DimensionTransition;
import net.minecraft.world.phys.Vec3;

/**
 * Two bites: the whole apple sends the eater to the End, the bitten half brings them back to where they
 * stood. The pack's only route there — twelve portal frames are not a pad craft.
 */
public class EndAppleItem extends Item {
    private static final String ROOT = "ninjacatskies";
    private static final String RETURN_TAG = "end_apple_return";
    private static final int TEAL = 0x59D9C9;
    private static final int GOLD = 0xE8C05A;
    private final boolean bitten;

    public EndAppleItem(boolean bitten, Properties properties) {
        super(properties);
        this.bitten = bitten;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        // The whole apple calls the End from outside it; in the End it would strand the eater with no way home.
        if (!bitten && level.dimension() == Level.END) {
            if (!level.isClientSide) player.displayClientMessage(msg("message.ninjacatskies.end_apple.already_there", TEAL), true);
            return InteractionResultHolder.fail(player.getItemInHand(hand));
        }
        return super.use(level, player, hand);
    }

    @Override
    public ItemStack finishUsingItem(ItemStack stack, Level level, LivingEntity entity) {
        // Eat first: super handles nutrition, effects and the single-player stack shrink.
        ItemStack rest = super.finishUsingItem(stack, level, entity);
        if (level.isClientSide || !(entity instanceof ServerPlayer player)) return rest;
        if (bitten) {
            returnHome(player);
            return rest;
        }
        ServerLevel end = player.server.getLevel(Level.END);
        if (end == null) {
            player.displayClientMessage(msg("message.ninjacatskies.end_apple.no_end", TEAL), true);
            return rest; // Whole apple is spent either way; without the End there is nowhere to send them.
        }
        storeReturnPoint(player);
        dismount(player);
        // Vanilla's own arrival: an obsidian pad under the spawn point, facing west like an End portal.
        BlockPos platform = ServerLevel.END_SPAWN_POINT;
        EndPlatformFeature.createEndPlatform(end, platform.below(), true);
        player.changeDimension(new DimensionTransition(
                end,
                Vec3.atBottomCenterOf(platform),
                Vec3.ZERO,
                net.minecraft.core.Direction.WEST.toYRot(),
                0.0F,
                DimensionTransition.DO_NOTHING
        ));
        player.level().playSound(null, player.blockPosition(), SoundEvents.PORTAL_TRAVEL, SoundSource.PLAYERS, 0.4F, 1.4F);
        player.displayClientMessage(msg("message.ninjacatskies.end_apple.away", GOLD), true);
        // The bite that is left is the way back. Creative keeps its whole apple.
        return player.getAbilities().instabuild ? rest : new ItemStack(ModItems.BITTEN_END_APPLE.get());
    }

    /** Back to the stored point, or the world spawn when the apple changed hands or the dimension is gone. */
    private void returnHome(ServerPlayer player) {
        CompoundTag ret = player.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).getCompound(ROOT).getCompound(RETURN_TAG);
        ServerLevel level = null;
        double x = 0, y = 0, z = 0;
        float yaw = 0, pitch = 0;
        if (ret.contains("dim")) {
            ResourceLocation id = ResourceLocation.tryParse(ret.getString("dim"));
            if (id != null) level = player.server.getLevel(ResourceKey.create(net.minecraft.core.registries.Registries.DIMENSION, id));
            x = ret.getDouble("x");
            y = ret.getDouble("y");
            z = ret.getDouble("z");
            yaw = ret.getFloat("yaw");
            pitch = ret.getFloat("pitch");
        }
        if (level == null) {
            level = player.server.getLevel(Level.OVERWORLD);
            if (level == null) {
                player.displayClientMessage(msg("message.ninjacatskies.end_apple.no_way_back", TEAL), true);
                return;
            }
            BlockPos spawn = level.getSharedSpawnPos();
            x = spawn.getX() + 0.5;
            y = spawn.getY();
            z = spawn.getZ() + 0.5;
            yaw = level.getSharedSpawnAngle();
            pitch = 0;
        }
        dismount(player);
        player.changeDimension(new DimensionTransition(level, new Vec3(x, y, z), Vec3.ZERO, yaw, pitch, DimensionTransition.DO_NOTHING));
        player.level().playSound(null, player.blockPosition(), SoundEvents.PORTAL_TRAVEL, SoundSource.PLAYERS, 0.4F, 1.6F);
        player.displayClientMessage(msg("message.ninjacatskies.end_apple.home", GOLD), true);
        clearReturnPoint(player);
    }

    private static void storeReturnPoint(ServerPlayer player) {
        CompoundTag persisted = player.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        CompoundTag root = persisted.getCompound(ROOT);
        CompoundTag ret = new CompoundTag();
        ret.putString("dim", player.level().dimension().location().toString());
        ret.putDouble("x", player.getX());
        ret.putDouble("y", player.getY());
        ret.putDouble("z", player.getZ());
        ret.putFloat("yaw", player.getYRot());
        ret.putFloat("pitch", player.getXRot());
        root.put(RETURN_TAG, ret);
        // PlayerPersisted survives death, so dying in the End does not lose the way back.
        persisted.put(ROOT, root);
        player.getPersistentData().put(Player.PERSISTED_NBT_TAG, persisted);
    }

    private static void clearReturnPoint(ServerPlayer player) {
        CompoundTag persisted = player.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        CompoundTag root = persisted.getCompound(ROOT);
        root.remove(RETURN_TAG);
        persisted.put(ROOT, root);
        player.getPersistentData().put(Player.PERSISTED_NBT_TAG, persisted);
    }

    /** changeDimension keeps a rider listed as its vehicle's passenger in the other level, which freezes them. */
    private static void dismount(ServerPlayer player) {
        if (player.isPassenger()) player.stopRiding();
        if (player.isVehicle()) player.ejectPassengers();
    }

    private static Component msg(String key, int rgb) {
        return Component.translatable(key).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(rgb)));
    }
}
