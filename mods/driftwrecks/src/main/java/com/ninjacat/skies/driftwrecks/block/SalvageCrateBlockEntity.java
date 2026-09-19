package com.ninjacat.skies.driftwrecks.block;

import com.ninjacat.skies.driftwrecks.registry.DwRegistries;
import net.minecraft.core.BlockPos;
import net.minecraft.core.GlobalPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BaseContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;

import javax.annotation.Nullable;

public class SalvageCrateBlockEntity extends BaseContainerBlockEntity {
    private NonNullList<ItemStack> items = NonNullList.withSize(27, ItemStack.EMPTY);

    public SalvageCrateBlockEntity(BlockPos pos, BlockState state) { super(DwRegistries.SALVAGE_CRATE.get(), pos, state); }

    /** The crate within 6 blocks of a Tension Post, if one was placed. */
    @Nullable
    public static SalvageCrateBlockEntity near(MinecraftServer server, GlobalPos post) {
        ServerLevel level = server.getLevel(post.dimension());
        if (level == null) return null;
        level.getChunkAt(post.pos());
        for (BlockPos p : BlockPos.betweenClosed(post.pos().offset(-6, -3, -6), post.pos().offset(6, 3, 6))) {
            if (level.isLoaded(p) && level.getBlockEntity(p) instanceof SalvageCrateBlockEntity be) return be;
        }
        return null;
    }

    /** Put a stack in the first empty slot. Returns false when the crate is full. */
    public boolean insert(ItemStack stack) {
        for (int i = 0; i < items.size(); i++) {
            if (items.get(i).isEmpty()) { items.set(i, stack); setChanged(); return true; }
        }
        return false;
    }

    @Override protected Component getDefaultName() { return Component.translatable("container.driftwrecks.salvage_crate"); }
    @Override protected NonNullList<ItemStack> getItems() { return items; }
    @Override protected void setItems(NonNullList<ItemStack> items) { this.items = items; }
    @Override protected AbstractContainerMenu createMenu(int id, Inventory inv) { return ChestMenu.threeRows(id, inv, this); }
    @Override public int getContainerSize() { return 27; }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider regs) {
        super.saveAdditional(tag, regs);
        ContainerHelper.saveAllItems(tag, items, regs);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider regs) {
        super.loadAdditional(tag, regs);
        items = NonNullList.withSize(27, ItemStack.EMPTY);
        ContainerHelper.loadAllItems(tag, items, regs);
    }
}
