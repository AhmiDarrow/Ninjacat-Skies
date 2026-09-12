package com.ninjacat.skies.voidloom.block;

import com.ninjacat.skies.voidloom.compat.ExDeorumSieveBridge;
import com.ninjacat.skies.voidloom.item.ModItems;
import com.ninjacat.skies.voidloom.sound.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.util.RandomSource;
import net.minecraft.world.Clearable;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.server.level.ServerLevel;
import net.neoforged.fml.ModList;
import net.neoforged.neoforge.items.IItemHandler;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;

/**
 * The Loomframe: a mesh stretched on a frame that sifts on its own, slowly, with a shuttle clack.
 * Feed grit by hopper on top; sit it on a hopper to pull scraps. When Ex Deorum is present it uses that
 * sieve table at {@link com.ninjacat.skies.voidloom.compat.LoomframeYield#AUTOMATED} of a hand sieve.
 */
public class LoomframeBlockEntity extends BlockEntity implements Clearable {
    public static final int SIFT_TICKS = 50;
    public static final int OUTPUT_SLOTS = 4;
    public static final int INPUT_MAX = 64;

    private static final TagKey<Item> C_MESHES = TagKey.create(Registries.ITEM, ResourceLocation.parse("c:meshes"));
    private static final TagKey<Item> EXDEORUM_MESHES = TagKey.create(Registries.ITEM, ResourceLocation.parse("exdeorum:sieve_meshes"));
    private static final ResourceLocation FRAYED_THREAD = ResourceLocation.parse("ninjacatskies:frayed_thread");

    private ItemStack mesh = ItemStack.EMPTY;
    private ItemStack input = ItemStack.EMPTY;
    private final NonNullList<ItemStack> output = NonNullList.withSize(OUTPUT_SLOTS, ItemStack.EMPTY);
    // At most one paid sift waits here when its random results exceed output capacity.
    private final NonNullList<ItemStack> pending = NonNullList.withSize(16, ItemStack.EMPTY);
    private int progress;
    private final IItemHandler handler = new Handler();

    public LoomframeBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.LOOMFRAME.get(), pos, state);
    }

    // ------------------------------------------------------------ mesh

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
        if (stack.is(ModItems.THREAD_MESH_STRING.get()) || stack.is(ModItems.THREAD_MESH_FLINT.get()) || stack.is(ModItems.THREAD_MESH_IRON.get())) {
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
        ItemStack out = mesh;
        mesh = ItemStack.EMPTY;
        progress = 0;
        sync();
        return out;
    }

    /** 0 = string, 1 = flint, 2 = iron, 3 = better than iron. */
    public int meshTier() {
        if (mesh.isEmpty()) {
            return -1;
        }
        String path = BuiltInRegistries.ITEM.getKey(mesh.getItem()).getPath();
        if (path.contains("netherite") || path.contains("diamond") || path.contains("gold")) {
            return 3;
        }
        if (path.contains("iron")) {
            return 2;
        }
        if (path.contains("flint")) {
            return 1;
        }
        return 0;
    }

    // ------------------------------------------------------------ input / output

    public static boolean isSiftable(ItemStack stack) {
        return stack.is(Items.DIRT) || stack.is(Items.GRAVEL) || stack.is(Items.COARSE_DIRT);
    }

    public boolean canAccept(ItemStack stack) {
        if (stack.isEmpty()) return false;
        if (level != null && ModList.get().isLoaded("exdeorum")) {
            if (!mesh.isEmpty()) return ExDeorumSieveBridge.hasRecipes(level, mesh, stack);
            return ExDeorumSieveBridge.isSiftable(level, stack);
        }
        return isSiftable(stack);
    }

    private boolean canProcess() {
        if (!isMeshItem(mesh) || input.isEmpty()) return false;
        if (level != null && ModList.get().isLoaded("exdeorum")) {
            return ExDeorumSieveBridge.hasRecipes(level, mesh, input);
        }
        return isSiftable(input);
    }

    public ItemStack getInput() {
        return input;
    }

    /** Insert as much of the stack as fits; returns how many were taken. */
    public int insertInput(ItemStack stack, boolean simulate) {
        if (!canAccept(stack)) {
            return 0;
        }
        if (!input.isEmpty() && !ItemStack.isSameItemSameComponents(input, stack)) {
            return 0;
        }
        int room = INPUT_MAX - input.getCount();
        int take = Math.min(room, stack.getCount());
        if (take <= 0) {
            return 0;
        }
        if (!simulate) {
            if (input.isEmpty()) {
                input = stack.copyWithCount(take);
            } else {
                input.grow(take);
            }
            sync();
        }
        return take;
    }

    public ItemStack takeInput() {
        ItemStack out = input;
        input = ItemStack.EMPTY;
        progress = 0;
        sync();
        return out;
    }

    public boolean hasOutput() {
        for (ItemStack s : output) {
            if (!s.isEmpty()) {
                return true;
            }
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

    private boolean flushPending() {
        boolean blocked = false;
        boolean changed = false;
        for (int i = 0; i < pending.size(); i++) {
            ItemStack stack = pending.get(i);
            if (stack.isEmpty()) continue;
            int remaining = OutputStorage.insert(output, stack, false);
            if (remaining != stack.getCount()) {
                pending.set(i, remaining == 0 ? ItemStack.EMPTY : stack.copyWithCount(remaining));
                changed = true;
            }
            blocked |= remaining > 0;
        }
        if (changed) sync();
        return !blocked;
    }

    public int progressPercent() {
        return (progress * 100) / SIFT_TICKS;
    }

    // ------------------------------------------------------------ the sift

    public static void serverTick(Level level, BlockPos pos, BlockState state, LoomframeBlockEntity be) {
        if (level.hasNeighborSignal(pos)) return;
        if (!be.flushPending()) return;
        if (!be.canProcess()) {
            if (be.progress != 0) {
                be.progress = 0;
                be.setChanged();
            }
            return;
        }
        be.progress++;
        be.setChanged();
        if (be.progress < SIFT_TICKS) {
            if (be.progress % 10 == 0 && level instanceof ServerLevel sl) {
                Block grit = Block.byItem(be.input.getItem());
                sl.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, grit == Blocks.AIR ? Blocks.DIRT.defaultBlockState() : grit.defaultBlockState()),
                        pos.getX() + 0.5, pos.getY() + 0.9, pos.getZ() + 0.5, 3, 0.2, 0.05, 0.2, 0.02);
            }
            return;
        }
        be.progress = 0;
        List<ItemStack> drops = be.roll(level, be.input, be.mesh);
        be.input.shrink(1);
        if (be.input.isEmpty()) {
            be.input = ItemStack.EMPTY;
        }
        for (int i = 0; i < drops.size(); i++) {
            int slot = i % be.pending.size();
            if (i > 0 && slot == 0) be.flushPending();   // more rolls than pending slots: push the earlier batch out first
            if (be.pending.get(slot).isEmpty()) be.pending.set(slot, drops.get(i));
            else net.minecraft.world.Containers.dropItemStack(level, pos.getX() + 0.5, pos.getY() + 1.0, pos.getZ() + 0.5, drops.get(i));
        }
        be.flushPending();
        level.playSound(null, pos, ModSounds.LOOMFRAME_SIFT.get(), SoundSource.BLOCKS, 0.55F, 0.95F + level.random.nextFloat() * 0.1F);
        if (level instanceof ServerLevel sl && !drops.isEmpty()) {
            sl.sendParticles(ParticleTypes.END_ROD, pos.getX() + 0.5, pos.getY() + 1.05, pos.getZ() + 0.5, 2, 0.15, 0.02, 0.15, 0.0);
        }
        be.sync();
    }

    /** Ex Deorum sieve table at automated yield when present; otherwise the built-in scrap table. */
    private List<ItemStack> roll(Level level, ItemStack in, ItemStack meshStack) {
        if (level instanceof ServerLevel sl && ModList.get().isLoaded("exdeorum")) {
            return ExDeorumSieveBridge.roll(sl, meshStack, in, sl.random);
        }
        return rollFallback(level.random, in, meshTier());
    }

    /** Scrap table used when Ex Deorum is not loaded (GameTests, bare Voidloom). */
    private List<ItemStack> rollFallback(RandomSource rand, ItemStack in, int tier) {
        List<ItemStack> out = new ArrayList<>();
        boolean gravel = in.is(Items.GRAVEL);
        if (gravel) {
            chance(out, rand, 0.30F, Items.FLINT);
            chance(out, rand, 0.15F, Items.IRON_NUGGET);
            if (tier >= 1) chance(out, rand, 0.06F, Items.GOLD_NUGGET);
            if (tier >= 1) chance(out, rand, 0.03F, threadOrLint());
            if (tier >= 2) chance(out, rand, 0.06F, Items.RAW_COPPER);
            if (tier >= 2) chance(out, rand, 0.02F, ModItems.STRAND_FILAMENT.get());
            if (tier >= 3) chance(out, rand, 0.04F, ModItems.STRAND_FILAMENT.get());
        } else {
            chance(out, rand, 0.35F, Items.FLINT);
            chance(out, rand, 0.20F, Items.CLAY_BALL);
            chance(out, rand, 0.08F, ModItems.LOOM_LINT.get());
            chance(out, rand, 0.03F, ModItems.VOID_YARN.get());
            if (tier >= 1) chance(out, rand, 0.10F, Items.IRON_NUGGET);
            if (tier >= 1) chance(out, rand, 0.03F, threadOrLint());
            if (tier >= 2) chance(out, rand, 0.12F, Items.IRON_NUGGET);
            if (tier >= 2) chance(out, rand, 0.02F, ModItems.STRAND_FILAMENT.get());
            if (tier >= 3) chance(out, rand, 0.04F, ModItems.STRAND_FILAMENT.get());
        }
        return out;
    }

    private static Item threadOrLint() {
        Item thread = BuiltInRegistries.ITEM.getOptional(FRAYED_THREAD).orElse(null);
        return thread == null || thread == Items.AIR ? ModItems.LOOM_LINT.get() : thread;
    }

    private static void chance(List<ItemStack> out, RandomSource rand, float p, Item item) {
        if (rand.nextFloat() < p) {
            out.add(new ItemStack(item));
        }
    }

    // ------------------------------------------------------------ capability (hoppers, pipes)

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
            return slot == 0 ? input : output.get(slot - 1);
        }

        @Override
        public ItemStack insertItem(int slot, ItemStack stack, boolean simulate) {
            if (level != null && level.hasNeighborSignal(worldPosition)) return stack;
            if (slot != 0 || stack.isEmpty()) {
                return stack;
            }
            int taken = insertInput(stack, simulate);
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
            return slot == 0 && canAccept(stack);
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
        mesh = ItemStack.EMPTY;
        input = ItemStack.EMPTY;
        output.clear();
        pending.clear();
        progress = 0;
        sync();
    }

    public List<ItemStack> drainForDrop() {
        List<ItemStack> all = new ArrayList<>();
        if (!mesh.isEmpty()) all.add(mesh);
        if (!input.isEmpty()) all.add(input);
        for (ItemStack s : output) {
            if (!s.isEmpty()) all.add(s);
        }
        for (ItemStack s : pending) if (!s.isEmpty()) all.add(s);
        pending.clear();
        mesh = ItemStack.EMPTY;
        input = ItemStack.EMPTY;
        progress = 0;
        for (int i = 0; i < output.size(); i++) output.set(i, ItemStack.EMPTY);
        return all;
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        mesh = tag.contains("Mesh") ? ItemStack.parse(registries, tag.getCompound("Mesh")).orElse(ItemStack.EMPTY) : ItemStack.EMPTY;
        input = tag.contains("Input") ? ItemStack.parse(registries, tag.getCompound("Input")).orElse(ItemStack.EMPTY) : ItemStack.EMPTY;
        for (int i = 0; i < output.size(); i++) output.set(i, ItemStack.EMPTY);
        ContainerHelper.loadAllItems(tag, output, registries);
        pending.clear();
        ContainerHelper.loadAllItems(tag.getCompound("Pending"), pending, registries);
        progress = Math.clamp(tag.getInt("Progress"), 0, SIFT_TICKS - 1);
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        if (!mesh.isEmpty()) tag.put("Mesh", mesh.save(registries));
        if (!input.isEmpty()) tag.put("Input", input.save(registries));
        ContainerHelper.saveAllItems(tag, output, registries);
        var pendingTag = new CompoundTag();
        ContainerHelper.saveAllItems(pendingTag, pending, registries);
        tag.put("Pending", pendingTag);
        tag.putInt("Progress", progress);
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
