package com.ninjacat.skies.voidloom.block;

import com.ninjacat.skies.voidloom.item.ModItems;
import com.ninjacat.skies.voidloom.sound.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Clearable;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.Containers;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.items.IItemHandler;
import org.joml.Vector3f;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Tension Barrel — a slow, wet transform station with no GUI.
 * <ul>
 *   <li>Water (iron or porcelain bucket, 4 charges each; the empty bucket comes straight back) + dirt → clay ball, ~8 s each</li>
 *   <li>String + ender pearl → 2 Void Yarn, ~6 s each</li>
 * </ul>
 * Holds up to 8 of each dry input and 8 charges of water, so a stack of dirt and two buckets is one visit.
 */
public class TensionBarrelBlockEntity extends BlockEntity implements Clearable {
    public static final int CLAY_TIME = 160;
    public static final int YARN_TIME = 120;
    public static final int WATER_PER_BUCKET = 4;
    public static final int WATER_MAX = 8;
    public static final int DRY_MAX = 8;
    public static final int OUTPUT_SLOTS = 3;

    private static final ResourceLocation PORCELAIN_WATER = ResourceLocation.parse("exdeorum:porcelain_water_bucket");
    private static final ResourceLocation PORCELAIN_BUCKET = ResourceLocation.parse("exdeorum:porcelain_bucket");
    private static final DustParticleOptions RING = new DustParticleOptions(new Vector3f(0.35F, 0.59F, 0.58F), 0.8F);

    private int water;
    private int dirt;
    private int string;
    private int pearls;
    private final NonNullList<ItemStack> output = NonNullList.withSize(OUTPUT_SLOTS, ItemStack.EMPTY);
    private int progress;
    private int progressTotal;
    private final IItemHandler handler = new Handler();

    public TensionBarrelBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.TENSION_BARREL.get(), pos, state);
    }

    // ------------------------------------------------------------ inputs

    public static boolean isWaterCarrier(ItemStack stack) {
        return stack.is(Items.WATER_BUCKET) || BuiltInRegistries.ITEM.getOptional(PORCELAIN_WATER).filter(stack::is).isPresent();
    }

    public static boolean isDirt(ItemStack stack) {
        return stack.is(Items.DIRT) || stack.is(Items.COARSE_DIRT);
    }

    public static boolean isAcceptedInput(ItemStack stack) {
        return isWaterCarrier(stack) || isDirt(stack) || stack.is(Items.STRING) || stack.is(Items.ENDER_PEARL);
    }

    /** Returns the empty bucket to hand back, or EMPTY if there was no room for water. */
    public ItemStack pourWater(ItemStack bucket) {
        if (!isWaterCarrier(bucket) || water + WATER_PER_BUCKET > WATER_MAX) {
            return ItemStack.EMPTY;
        }
        water += WATER_PER_BUCKET;
        sync();
        return emptyWaterCarrier(bucket);
    }

    private static ItemStack emptyWaterCarrier(ItemStack bucket) {
        boolean porcelain = !bucket.is(Items.WATER_BUCKET);
        return porcelain
                ? BuiltInRegistries.ITEM.getOptional(PORCELAIN_BUCKET).map(ItemStack::new).orElseGet(() -> new ItemStack(Items.BUCKET))
                : new ItemStack(Items.BUCKET);
    }

    /** Insert dry inputs; returns how many were taken. */
    public int insertDry(ItemStack stack, boolean simulate) {
        int current;
        if (isDirt(stack)) current = dirt;
        else if (stack.is(Items.STRING)) current = string;
        else if (stack.is(Items.ENDER_PEARL)) current = pearls;
        else return 0;
        int take = Math.min(DRY_MAX - current, stack.getCount());
        if (take <= 0) {
            return 0;
        }
        if (!simulate) {
            if (isDirt(stack)) dirt += take;
            else if (stack.is(Items.STRING)) string += take;
            else pearls += take;
            sync();
        }
        return take;
    }

    public List<ItemStack> takeDryInputs() {
        List<ItemStack> out = new ArrayList<>();
        if (dirt > 0) out.add(new ItemStack(Items.DIRT, dirt));
        if (string > 0) out.add(new ItemStack(Items.STRING, string));
        if (pearls > 0) out.add(new ItemStack(Items.ENDER_PEARL, pearls));
        dirt = string = pearls = 0;
        progress = 0;
        progressTotal = 0;
        sync();
        return out;
    }

    public boolean hasOutput() {
        for (ItemStack s : output) {
            if (!s.isEmpty()) return true;
        }
        return false;
    }

    public List<ItemStack> takeAllOutput() {
        List<ItemStack> out = new ArrayList<>();
        for (int i = 0; i < output.size(); i++) {
            if (!output.get(i).isEmpty()) {
                out.add(output.get(i));
                output.set(i, ItemStack.EMPTY);
            }
        }
        sync();
        return out;
    }

    public int getWater() {
        return water;
    }

    public int getProgress() {
        return progress;
    }

    public int getProgressTotal() {
        return progressTotal;
    }

    private boolean canStore(ItemStack stack) {
        return OutputStorage.insert(output, stack, true) == 0;
    }

    private void store(ItemStack stack) {
        if (!canStore(stack)) throw new IllegalStateException("Output capacity changed during processing");
        OutputStorage.insert(output, stack, false);
    }

    // ------------------------------------------------------------ work

    private enum Recipe {
        CLAY(CLAY_TIME), YARN(YARN_TIME);

        final int time;

        Recipe(int time) {
            this.time = time;
        }
    }

    @Nullable
    private Recipe match() {
        if (water > 0 && dirt > 0 && canStore(new ItemStack(Items.CLAY_BALL))) {
            return Recipe.CLAY;
        }
        if (string > 0 && pearls > 0 && canStore(new ItemStack(ModItems.VOID_YARN.get(), 2))) {
            return Recipe.YARN;
        }
        return null;
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, TensionBarrelBlockEntity be) {
        if (level.hasNeighborSignal(pos)) return;
        Recipe recipe = be.match();
        if (recipe == null) {
            if (be.progress != 0) {
                be.progress = 0;
                be.progressTotal = 0;
                be.setChanged();
            }
            return;
        }
        if (be.progressTotal != recipe.time) {
            be.progress = 0;
            be.progressTotal = recipe.time;
        }
        be.progress++;
        if (be.progress % 8 == 0 && level instanceof ServerLevel sl) {
            // A thread-ring turning on the rim while tension builds.
            double a = (be.progress / 8.0) * 0.9;
            sl.sendParticles(RING, pos.getX() + 0.5 + Math.cos(a) * 0.42, pos.getY() + 1.02, pos.getZ() + 0.5 + Math.sin(a) * 0.42, 1, 0, 0, 0, 0);
        }
        if (be.progress >= recipe.time) {
            be.finish(level, pos, recipe);
        }
        be.setChanged();
    }

    private void finish(Level level, BlockPos pos, Recipe recipe) {
        progress = 0;
        progressTotal = 0;
        switch (recipe) {
            case CLAY -> {
                water--;
                dirt--;
                store(new ItemStack(Items.CLAY_BALL));
            }
            case YARN -> {
                string--;
                pearls--;
                store(new ItemStack(ModItems.VOID_YARN.get(), 2));
            }
        }
        level.playSound(null, pos, ModSounds.BARREL_SETTLE.get(), SoundSource.BLOCKS, 0.6F, 0.95F + level.random.nextFloat() * 0.1F);
        if (level instanceof ServerLevel sl) {
            sl.sendParticles(ParticleTypes.SPLASH, pos.getX() + 0.5, pos.getY() + 1.0, pos.getZ() + 0.5, 6, 0.2, 0.05, 0.2, 0.0);
        }
        sync();
    }

    // ------------------------------------------------------------ status

    public void tellStatus(Player player) {
        if (hasOutput()) {
            player.displayClientMessage(Component.translatable("message.voidloom.tension.ready"), true);
            return;
        }
        if (progressTotal > 0) {
            int pct = Math.min(100, (progress * 100) / progressTotal);
            player.displayClientMessage(Component.translatable("message.voidloom.tension.progress", pct), true);
            return;
        }
        if (water == 0 && dirt == 0 && string == 0 && pearls == 0) {
            player.displayClientMessage(Component.translatable("message.voidloom.tension.empty"), true);
        } else {
            player.displayClientMessage(Component.translatable("message.voidloom.tension.holding", water, dirt, string, pearls), true);
        }
    }

    // ------------------------------------------------------------ capability

    public IItemHandler handler() {
        return handler;
    }

    private final class Handler implements IItemHandler {
        @Override
        public int getSlots() {
            return 1 + OUTPUT_SLOTS;
        }

        @Override
        public ItemStack getStackInSlot(int slot) {
            return slot == 0 ? ItemStack.EMPTY : output.get(slot - 1);
        }

        @Override
        public ItemStack insertItem(int slot, ItemStack stack, boolean simulate) {
            if (level != null && level.hasNeighborSignal(worldPosition)) return stack;
            if (slot != 0 || stack.isEmpty()) {
                return stack;
            }
            if (isWaterCarrier(stack)) {
                if (water + WATER_PER_BUCKET > WATER_MAX || !canStore(emptyWaterCarrier(stack))) {
                    return stack;
                }
                if (!simulate) {
                    ItemStack empty = pourWater(stack);
                    store(empty);
                    sync();
                }
                return stack.getCount() > 1 ? stack.copyWithCount(stack.getCount() - 1) : ItemStack.EMPTY;
            }
            int taken = insertDry(stack, simulate);
            if (taken <= 0) {
                return stack;
            }
            return taken >= stack.getCount() ? ItemStack.EMPTY : stack.copyWithCount(stack.getCount() - taken);
        }

        @Override
        public ItemStack extractItem(int slot, int amount, boolean simulate) {
            if (level != null && level.hasNeighborSignal(worldPosition)) return ItemStack.EMPTY;
            if (slot == 0 || amount <= 0) {
                return ItemStack.EMPTY;
            }
            ItemStack s = output.get(slot - 1);
            if (s.isEmpty()) {
                return ItemStack.EMPTY;
            }
            int take = Math.min(amount, s.getCount());
            ItemStack out = s.copyWithCount(take);
            if (!simulate) {
                s.shrink(take);
                if (s.isEmpty()) {
                    output.set(slot - 1, ItemStack.EMPTY);
                }
                sync();
            }
            return out;
        }

        @Override
        public int getSlotLimit(int slot) {
            return 64;
        }

        @Override
        public boolean isItemValid(int slot, ItemStack stack) {
            return slot == 0 && isAcceptedInput(stack);
        }
    }

    // ------------------------------------------------------------ plumbing

    private void sync() {
        if (level != null) level.updateNeighbourForOutputSignal(worldPosition, getBlockState().getBlock());
        setChanged();
        if (level != null && !level.isClientSide) {
            level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_ALL);
        }
    }

    @Override
    public void clearContent() {
        water = dirt = string = pearls = 0;
        output.clear();
        progress = 0;
        progressTotal = 0;
        sync();
    }

    public void dropAll(Level level, BlockPos pos) {
        for (ItemStack s : takeDryInputs()) {
            Containers.dropItemStack(level, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, s);
        }
        for (ItemStack s : takeAllOutput()) {
            Containers.dropItemStack(level, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, s);
        }
        water = 0;
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        water = Math.clamp(tag.getInt("Water"), 0, WATER_MAX);
        dirt = Math.clamp(tag.getInt("Dirt"), 0, DRY_MAX);
        string = Math.clamp(tag.getInt("String"), 0, DRY_MAX);
        pearls = Math.clamp(tag.getInt("Pearls"), 0, DRY_MAX);
        progress = tag.getInt("Progress");
        progressTotal = tag.getInt("ProgressTotal");
        if (progressTotal != CLAY_TIME && progressTotal != YARN_TIME) progressTotal = 0;
        if (progress < 0 || progress >= progressTotal) progress = 0;
        for (int i = 0; i < output.size(); i++) output.set(i, ItemStack.EMPTY);
        ContainerHelper.loadAllItems(tag, output, registries);
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        tag.putInt("Water", water);
        tag.putInt("Dirt", dirt);
        tag.putInt("String", string);
        tag.putInt("Pearls", pearls);
        tag.putInt("Progress", progress);
        tag.putInt("ProgressTotal", progressTotal);
        ContainerHelper.saveAllItems(tag, output, registries);
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

    @SuppressWarnings("unused")
    private static Optional<Item> porcelainEmpty() {
        return BuiltInRegistries.ITEM.getOptional(PORCELAIN_BUCKET);
    }
}
