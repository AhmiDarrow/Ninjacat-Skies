package com.ninjacat.skies.voidloom.block;

import com.ninjacat.skies.voidloom.item.ModItems;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.Clearable;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

import javax.annotation.Nullable;

/** Single mesh slot; dirt/gravel right-clicks yield a small bonus scrap on cooldown. */
public class LoomframeBlockEntity extends BlockEntity implements Clearable {
    public static final int SIFT_COOLDOWN_TICKS = 60;

    private static final TagKey<Item> C_MESHES = TagKey.create(Registries.ITEM, ResourceLocation.parse("c:meshes"));
    private static final TagKey<Item> EXDEORUM_MESHES =
            TagKey.create(Registries.ITEM, ResourceLocation.parse("exdeorum:sieve_meshes"));

    private ItemStack mesh = ItemStack.EMPTY;
    private long lastSiftGameTime = Long.MIN_VALUE / 2;

    public LoomframeBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.LOOMFRAME.get(), pos, state);
    }

    public ItemStack getMesh() {
        return mesh;
    }

    public boolean hasMesh() {
        return !mesh.isEmpty();
    }

    public static boolean isMeshItem(ItemStack stack) {
        if (stack.isEmpty()) {
            return false;
        }
        if (stack.is(ModItems.THREAD_MESH_STRING.get())
                || stack.is(ModItems.THREAD_MESH_FLINT.get())
                || stack.is(ModItems.THREAD_MESH_IRON.get())) {
            return true;
        }
        return stack.is(C_MESHES) || stack.is(EXDEORUM_MESHES);
    }

    public boolean tryInsertMesh(ItemStack stack) {
        if (!mesh.isEmpty() || !isMeshItem(stack)) {
            return false;
        }
        mesh = stack.copyWithCount(1);
        sync();
        return true;
    }

    public ItemStack takeMesh() {
        if (mesh.isEmpty()) {
            return ItemStack.EMPTY;
        }
        ItemStack out = mesh;
        mesh = ItemStack.EMPTY;
        sync();
        return out;
    }

    private void sync() {
        setChanged();
        if (level != null && !level.isClientSide) {
            level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
        }
    }

    public boolean isOnCooldown(long gameTime) {
        return gameTime - lastSiftGameTime < SIFT_COOLDOWN_TICKS;
    }

    public boolean canSift(ItemStack stack) {
        return hasMesh() && isSiftable(stack);
    }

    public static boolean isSiftable(ItemStack stack) {
        return stack.is(Items.DIRT) || stack.is(Items.GRAVEL) || stack.is(Items.COARSE_DIRT);
    }

    /** Rolls a small bonus scrap. Does not consume the mesh. */
    public ItemStack sift(ItemStack input, long gameTime) {
        if (!canSift(input) || isOnCooldown(gameTime) || level == null) {
            return ItemStack.EMPTY;
        }
        lastSiftGameTime = gameTime;
        sync();

        float roll = level.getRandom().nextFloat();
        if (input.is(Items.GRAVEL)) {
            return roll < 0.2F ? new ItemStack(Items.IRON_NUGGET) : new ItemStack(Items.FLINT);
        }
        // dirt / coarse dirt
        if (roll < 0.05F) {
            return new ItemStack(ModItems.VOID_YARN.get());
        }
        if (roll < 0.30F) {
            return new ItemStack(Items.CLAY_BALL);
        }
        return new ItemStack(Items.FLINT);
    }

    @Override
    public void clearContent() {
        mesh = ItemStack.EMPTY;
        sync();
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        if (tag.contains("Mesh")) {
            mesh = ItemStack.parse(registries, tag.getCompound("Mesh")).orElse(ItemStack.EMPTY);
        } else {
            mesh = ItemStack.EMPTY;
        }
        lastSiftGameTime = tag.getLong("LastSift");
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        if (!mesh.isEmpty()) {
            tag.put("Mesh", mesh.save(registries));
        }
        tag.putLong("LastSift", lastSiftGameTime);
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
}
