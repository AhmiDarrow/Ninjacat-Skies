package com.ninjacat.skies.driftwrecks.block;

import com.ninjacat.skies.driftwrecks.registry.DwRegistries;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

import java.util.ArrayList;
import java.util.List;

public class TrophyPlinthBlockEntity extends BlockEntity {
    public static final int SLOTS = 6;
    private final NonNullList<ItemStack> items = NonNullList.withSize(SLOTS, ItemStack.EMPTY);

    public TrophyPlinthBlockEntity(BlockPos pos, BlockState state) { super(DwRegistries.TROPHY_PLINTH.get(), pos, state); }

    public static boolean isKeepsake(ItemStack s) { return s.getItem() instanceof BlockItem bi && bi.getBlock() instanceof KeepsakeBlock; }

    public boolean add(ItemStack s) {
        for (int i = 0; i < SLOTS; i++) if (items.get(i).isEmpty()) { items.set(i, s); changed(); return true; }
        return false;
    }

    public ItemStack takeLast() {
        for (int i = SLOTS - 1; i >= 0; i--) if (!items.get(i).isEmpty()) { ItemStack s = items.get(i); items.set(i, ItemStack.EMPTY); changed(); return s; }
        return ItemStack.EMPTY;
    }

    public List<ItemStack> items() {
        List<ItemStack> out = new ArrayList<>();
        for (ItemStack s : items) if (!s.isEmpty()) out.add(s);
        return out;
    }

    public ItemStack slot(int i) { return items.get(i); }

    private void changed() {
        setChanged();
        if (level != null) level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), 3);
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider regs) {
        super.saveAdditional(tag, regs);
        ContainerHelper.saveAllItems(tag, items, true, regs);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider regs) {
        super.loadAdditional(tag, regs);
        for (int i = 0; i < SLOTS; i++) items.set(i, ItemStack.EMPTY);
        ContainerHelper.loadAllItems(tag, items, regs);
    }

    @Override public CompoundTag getUpdateTag(HolderLookup.Provider regs) { return saveWithoutMetadata(regs); }
    @Override public Packet<ClientGamePacketListener> getUpdatePacket() { return ClientboundBlockEntityDataPacket.create(this); }
}
