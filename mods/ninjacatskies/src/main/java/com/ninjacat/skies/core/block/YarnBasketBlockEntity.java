package com.ninjacat.skies.core.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** What a player was carrying when they died, and whose it is. */
public class YarnBasketBlockEntity extends BlockEntity {
    private final List<ItemStack> items = new ArrayList<>();
    @Nullable private UUID owner;
    @Nullable private UUID clowder;
    private String ownerName = "";

    public YarnBasketBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.YARN_BASKET.get(), pos, state);
    }

    public void fill(UUID owner, String ownerName, @Nullable UUID clowder, List<ItemStack> stacks) {
        this.owner = owner;
        this.ownerName = ownerName;
        this.clowder = clowder;
        for (ItemStack s : stacks) if (!s.isEmpty()) items.add(s.copy());
        setChanged();
    }

    /** Hands the contents over and empties the basket, so removing the block afterwards drops nothing twice. */
    public List<ItemStack> takeAll() {
        List<ItemStack> out = new ArrayList<>(items);
        items.clear();
        setChanged();
        return out;
    }

    public List<ItemStack> items() { return List.copyOf(items); }
    @Nullable public UUID owner() { return owner; }
    @Nullable public UUID clowder() { return clowder; }
    public String ownerName() { return ownerName; }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        if (owner != null) tag.putUUID("Owner", owner);
        if (clowder != null) tag.putUUID("Clowder", clowder);
        tag.putString("OwnerName", ownerName);
        ListTag list = new ListTag();
        for (ItemStack s : items) if (!s.isEmpty()) list.add(s.save(registries));
        tag.put("Items", list);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        owner = tag.hasUUID("Owner") ? tag.getUUID("Owner") : null;
        clowder = tag.hasUUID("Clowder") ? tag.getUUID("Clowder") : null;
        ownerName = tag.getString("OwnerName");
        items.clear();
        ListTag list = tag.getList("Items", Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            ItemStack s = ItemStack.parseOptional(registries, list.getCompound(i));
            if (!s.isEmpty()) items.add(s);
        }
    }
}
