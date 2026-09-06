package com.ninjacat.skies.voidloom.block;

import com.ninjacat.skies.voidloom.item.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.Clearable;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

import javax.annotation.Nullable;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Slow item transform station (no GUI).
 * <ul>
 *   <li>Water bucket (iron or porcelain) + dirt → clay ball; empty bucket returned to nearest player, ~10s</li>
 *   <li>String + ender pearl → void yarn, ~8s</li>
 * </ul>
 */
public class TensionBarrelBlockEntity extends BlockEntity implements Clearable {
    public static final int CLAY_TIME = 200;
    public static final int YARN_TIME = 160;
    private static final ResourceLocation PORCELAIN_WATER =
            ResourceLocation.parse("exdeorum:porcelain_water_bucket");
    private static final ResourceLocation PORCELAIN_BUCKET =
            ResourceLocation.parse("exdeorum:porcelain_bucket");

    private ItemStack slotA = ItemStack.EMPTY;
    private ItemStack slotB = ItemStack.EMPTY;
    private ItemStack output = ItemStack.EMPTY;
    private int progress;
    private int progressTotal;
    @Nullable
    private UUID lastUser;

    public TensionBarrelBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.TENSION_BARREL.get(), pos, state);
    }

    public ItemStack getSlotA() {
        return slotA;
    }

    public ItemStack getSlotB() {
        return slotB;
    }

    public ItemStack getOutput() {
        return output;
    }

    public int getProgress() {
        return progress;
    }

    public int getProgressTotal() {
        return progressTotal;
    }

    public void rememberUser(Player player) {
        lastUser = player.getUUID();
    }

    public static boolean isAcceptedInput(ItemStack stack) {
        return isWaterCarrier(stack)
                || stack.is(Items.DIRT)
                || stack.is(Items.COARSE_DIRT)
                || stack.is(Items.STRING)
                || stack.is(Items.ENDER_PEARL);
    }

    public boolean tryInsert(ItemStack stack) {
        if (!output.isEmpty() || !isAcceptedInput(stack)) {
            return false;
        }
        ItemStack one = stack.copyWithCount(1);
        if (slotA.isEmpty()) {
            slotA = one;
            recomputeRecipe();
            sync();
            return true;
        }
        if (slotB.isEmpty() && !ItemStack.isSameItemSameComponents(slotA, one)) {
            if (isDirt(slotA) && isDirt(one)) {
                return false;
            }
            slotB = one;
            recomputeRecipe();
            sync();
            return true;
        }
        return false;
    }

    public ItemStack takeOutput() {
        if (output.isEmpty()) {
            return ItemStack.EMPTY;
        }
        ItemStack out = output;
        output = ItemStack.EMPTY;
        recomputeRecipe();
        sync();
        return out;
    }

    public ItemStack takeLastInput() {
        if (!slotB.isEmpty()) {
            ItemStack out = slotB;
            slotB = ItemStack.EMPTY;
            progress = 0;
            recomputeRecipe();
            sync();
            return out;
        }
        if (!slotA.isEmpty()) {
            ItemStack out = slotA;
            slotA = ItemStack.EMPTY;
            progress = 0;
            recomputeRecipe();
            sync();
            return out;
        }
        return ItemStack.EMPTY;
    }

    private void sync() {
        setChanged();
        if (level != null && !level.isClientSide) {
            level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
        }
    }

    private void recomputeRecipe() {
        Recipe recipe = matchRecipe();
        if (recipe == null) {
            progress = 0;
            progressTotal = 0;
            return;
        }
        if (progressTotal != recipe.time) {
            progress = 0;
            progressTotal = recipe.time;
        }
    }

    private Recipe matchRecipe() {
        if (slotA.isEmpty() || slotB.isEmpty() || !output.isEmpty()) {
            return null;
        }
        if (isWaterCarrier(slotA) && isDirt(slotB) || isWaterCarrier(slotB) && isDirt(slotA)) {
            return Recipe.CLAY;
        }
        if (isString(slotA) && isEnder(slotB) || isString(slotB) && isEnder(slotA)) {
            return Recipe.YARN;
        }
        return null;
    }

    private static boolean isWaterCarrier(ItemStack stack) {
        if (stack.is(Items.WATER_BUCKET)) {
            return true;
        }
        return BuiltInRegistries.ITEM.getOptional(PORCELAIN_WATER).filter(stack::is).isPresent();
    }

    private static Optional<Item> porcelainEmpty() {
        return BuiltInRegistries.ITEM.getOptional(PORCELAIN_BUCKET);
    }

    private static boolean isDirt(ItemStack stack) {
        return stack.is(Items.DIRT) || stack.is(Items.COARSE_DIRT);
    }

    private static boolean isString(ItemStack stack) {
        return stack.is(Items.STRING);
    }

    private static boolean isEnder(ItemStack stack) {
        return stack.is(Items.ENDER_PEARL);
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, TensionBarrelBlockEntity be) {
        Recipe recipe = be.matchRecipe();
        if (recipe == null) {
            if (be.progress != 0) {
                be.progress = 0;
                be.progressTotal = 0;
                be.setChanged();
            }
            return;
        }
        be.progressTotal = recipe.time;
        be.progress++;
        if (be.progress >= recipe.time) {
            be.finishRecipe(recipe);
        }
        be.setChanged();
    }

    private void finishRecipe(Recipe recipe) {
        progress = 0;
        progressTotal = 0;
        switch (recipe) {
            case CLAY -> {
                boolean porcelain = isPorcelainWater(slotA) || isPorcelainWater(slotB);
                slotA = ItemStack.EMPTY;
                slotB = ItemStack.EMPTY;
                output = new ItemStack(Items.CLAY_BALL);
                ItemStack empty = porcelain
                        ? porcelainEmpty().map(ItemStack::new).orElseGet(() -> new ItemStack(Items.BUCKET))
                        : new ItemStack(Items.BUCKET);
                returnEmptyBucket(empty);
            }
            case YARN -> {
                slotA = ItemStack.EMPTY;
                slotB = ItemStack.EMPTY;
                output = new ItemStack(ModItems.VOID_YARN.get());
            }
        }
        sync();
    }

    private static boolean isPorcelainWater(ItemStack stack) {
        return BuiltInRegistries.ITEM.getOptional(PORCELAIN_WATER).filter(stack::is).isPresent();
    }

    private void returnEmptyBucket(ItemStack empty) {
        if (level == null || level.isClientSide || empty.isEmpty()) {
            return;
        }
        Player target = null;
        if (lastUser != null) {
            target = level.getPlayerByUUID(lastUser);
        }
        if (target == null) {
            List<ServerPlayer> near = level.getEntitiesOfClass(
                    ServerPlayer.class,
                    new AABB(worldPosition).inflate(6.0)
            );
            if (!near.isEmpty()) {
                target = near.get(0);
            }
        }
        if (target != null) {
            if (!target.getInventory().add(empty)) {
                target.drop(empty, false);
            }
            target.displayClientMessage(Component.translatable("message.voidloom.tension.bucket_ejected"), true);
            return;
        }
        // Fallback: center of the block so the bucket does not fall off a pad corner.
        net.minecraft.world.Containers.dropItemStack(
                level,
                worldPosition.getX() + 0.5,
                worldPosition.getY() + 1.0,
                worldPosition.getZ() + 0.5,
                empty
        );
    }

    public void tellStatus(Player player) {
        if (!output.isEmpty()) {
            player.displayClientMessage(Component.translatable("message.voidloom.tension.ready"), true);
            return;
        }
        if (progressTotal > 0) {
            int pct = Math.min(100, (progress * 100) / progressTotal);
            player.displayClientMessage(Component.translatable("message.voidloom.tension.progress", pct), true);
            return;
        }
        if (slotA.isEmpty() && slotB.isEmpty()) {
            player.displayClientMessage(Component.translatable("message.voidloom.tension.empty"), true);
        } else {
            player.displayClientMessage(Component.translatable("message.voidloom.tension.waiting"), true);
        }
    }

    @Override
    public void clearContent() {
        slotA = ItemStack.EMPTY;
        slotB = ItemStack.EMPTY;
        output = ItemStack.EMPTY;
        progress = 0;
        progressTotal = 0;
        sync();
    }

    public void dropAll(Level level, BlockPos pos) {
        drop(level, pos, slotA);
        drop(level, pos, slotB);
        drop(level, pos, output);
        clearContent();
    }

    private static void drop(Level level, BlockPos pos, ItemStack stack) {
        if (!stack.isEmpty()) {
            net.minecraft.world.Containers.dropItemStack(
                    level,
                    pos.getX() + 0.5,
                    pos.getY() + 0.5,
                    pos.getZ() + 0.5,
                    stack.copy()
            );
        }
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        slotA = readStack(tag, "SlotA", registries);
        slotB = readStack(tag, "SlotB", registries);
        output = readStack(tag, "Output", registries);
        progress = tag.getInt("Progress");
        progressTotal = tag.getInt("ProgressTotal");
        if (tag.hasUUID("LastUser")) {
            lastUser = tag.getUUID("LastUser");
        }
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        writeStack(tag, "SlotA", slotA, registries);
        writeStack(tag, "SlotB", slotB, registries);
        writeStack(tag, "Output", output, registries);
        tag.putInt("Progress", progress);
        tag.putInt("ProgressTotal", progressTotal);
        if (lastUser != null) {
            tag.putUUID("LastUser", lastUser);
        }
    }

    private static ItemStack readStack(CompoundTag tag, String key, HolderLookup.Provider registries) {
        if (tag.contains(key)) {
            return ItemStack.parse(registries, tag.getCompound(key)).orElse(ItemStack.EMPTY);
        }
        return ItemStack.EMPTY;
    }

    private static void writeStack(CompoundTag tag, String key, ItemStack stack, HolderLookup.Provider registries) {
        if (!stack.isEmpty()) {
            tag.put(key, stack.save(registries));
        }
    }

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider registries) {
        return saveWithoutMetadata(registries);
    }

    @Nullable
    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }

    private enum Recipe {
        CLAY(CLAY_TIME),
        YARN(YARN_TIME);

        final int time;

        Recipe(int time) {
            this.time = time;
        }
    }
}
