package com.ninjacat.skies.core.block;

import com.mojang.serialization.MapCodec;
import com.ninjacat.skies.core.item.ModItems;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;

import javax.annotation.Nullable;
import java.util.EnumMap;
import java.util.Map;

/**
 * The Tension Post: a Clowder's monument. Seat Strand tokens here; the notches light one tribe at a time.
 * Braid Cord and the Spindle Loom Fragment are spun at the Post rather than crafted from tokens,
 * so tokens are proof, never fuel.
 */
public class TensionPostBlock extends BaseEntityBlock {
    public static final MapCodec<TensionPostBlock> CODEC = simpleCodec(TensionPostBlock::new);
    public static final Map<Strand, BooleanProperty> SEATED = new EnumMap<>(Strand.class);
    public static final BooleanProperty REWOVEN = BooleanProperty.create("rewoven");
    private static final VoxelShape SHAPE = Block.box(5, 0, 5, 11, 16, 11);

    static {
        for (Strand s : Strand.ALL) {
            SEATED.put(s, BooleanProperty.create(s.id()));
        }
    }

    public TensionPostBlock(Properties properties) {
        super(properties);
        BlockState state = getStateDefinition().any().setValue(REWOVEN, false);
        for (BooleanProperty p : SEATED.values()) {
            state = state.setValue(p, false);
        }
        registerDefaultState(state);
    }

    public static int lightFor(BlockState state) {
        int n = 0;
        for (BooleanProperty p : SEATED.values()) {
            if (state.getValue(p)) {
                n++;
            }
        }
        return Math.min(15, n + (state.getValue(REWOVEN) ? 6 : 0));
    }

    public static int seatedCount(BlockState state) {
        int n = 0;
        for (BooleanProperty p : SEATED.values()) {
            if (state.getValue(p)) {
                n++;
            }
        }
        return n;
    }

    @Override protected boolean hasAnalogOutputSignal(BlockState state) { return true; }
    @Override protected int getAnalogOutputSignal(BlockState state, Level level, BlockPos pos) {
        return state.getValue(REWOVEN) ? 15 : seatedCount(state);
    }

    public static BlockState withBits(BlockState state, int bits, boolean rewoven) {
        for (Strand s : Strand.ALL) {
            state = state.setValue(SEATED.get(s), (bits & s.bit()) != 0);
        }
        return state.setValue(REWOVEN, rewoven);
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        for (Strand s : Strand.ALL) {
            builder.add(SEATED.get(s));
        }
        builder.add(REWOVEN);
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() {
        return CODEC;
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        return defaultBlockState();
    }

    @Override
    public void setPlacedBy(Level level, BlockPos pos, BlockState state, @Nullable LivingEntity placer, ItemStack stack) {
        super.setPlacedBy(level, pos, state, placer, stack);
        if (level instanceof ServerLevel serverLevel && placer instanceof ServerPlayer player) {
            LoomTension.clowderOf(player).ifPresent(c -> {
                level.setBlock(pos, withBits(state, LoomTension.strandBits(c), LoomTension.isRewoven(c)), 3);
                LoomTension.rememberPost(c, serverLevel, pos);
                if (level.getBlockEntity(pos) instanceof TensionPostBlockEntity be) {
                    be.setClowder(c.id());
                }
                int seated = Integer.bitCount(LoomTension.strandBits(c));
                player.displayClientMessage(NinjacatText.teal(
                        seated == 0
                                ? "A Tension Post. Seat Strand tokens here as the Clowder tensions them."
                                : "The Post remembers " + seated + (seated == 1 ? " Strand." : " Strands.")
                ), true);
            });
        }
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new TensionPostBlockEntity(pos, state);
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        return level.isClientSide
                ? createTickerHelper(type, ModBlockEntities.TENSION_POST.get(), TensionPostBlockEntity::clientTick)
                : null;
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hit) {
        if (level.hasNeighborSignal(pos)) {
            if (!level.isClientSide) player.displayClientMessage(net.minecraft.network.chat.Component.literal("The Post is locked by redstone."), true);
            return ItemInteractionResult.CONSUME;
        }
        if (stack.isEmpty()) {
            return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        }
        if (!(level instanceof ServerLevel serverLevel) || !(player instanceof ServerPlayer sp)) {
            return ItemInteractionResult.SUCCESS;
        }
        if (!owns(serverLevel, pos, sp)) {
            player.displayClientMessage(NinjacatText.teal("This Post answers to another Clowder."), true);
            return ItemInteractionResult.CONSUME;
        }

        // Strand token → seat it.
        Strand strand = Strand.byToken(BuiltInRegistries.ITEM.getKey(stack.getItem()));
        if (strand != null) {
            if (LoomTension.seat(serverLevel, pos, sp, strand)) {
                consume(player, stack);
                refresh(serverLevel, pos, sp);
            } else {
                level.playSound(null, pos, SoundEvents.NOTE_BLOCK_BASS.value(), SoundSource.BLOCKS, 0.6F, 0.6F);
                player.displayClientMessage(NinjacatText.teal(strand.title() + " is already tensioned here. Keep the spare as proof."), true);
            }
            return ItemInteractionResult.CONSUME;
        }

        // Strand Filament → Braid Cord, once two of Clock / Swarm / Spark are seated.
        if (ModItems.is(stack, "voidloom:strand_filament")) {
            if (LoomTension.canBraid(sp)) {
                consume(player, stack);
                LoomTension.giveOrDrop(sp, new ItemStack(ModItems.BRAID_CORD.get()));
                level.playSound(null, pos, SoundEvents.NOTE_BLOCK_CHIME.value(), SoundSource.BLOCKS, 0.8F, 1.3F);
                player.displayClientMessage(NinjacatText.gold("The filament takes the braid. Two paths, one cord."), true);
            } else {
                player.displayClientMessage(NinjacatText.teal("A braid needs two of Clock, Swarm, or Spark seated first."), true);
            }
            return ItemInteractionResult.CONSUME;
        }

        // March stone → Spindle Loom Fragment, once all nine are seated.
        if (ModItems.is(stack, "tribalpower:march_stone")) {
            if (LoomTension.canSpinFragment(sp)) {
                consume(player, stack);
                LoomTension.giveOrDrop(sp, new ItemStack(ModItems.SPINDLE_LOOM_FRAGMENT.get()));
                level.playSound(null, pos, SoundEvents.NOTE_BLOCK_BELL.value(), SoundSource.BLOCKS, 1.0F, 0.8F);
                player.displayClientMessage(NinjacatText.gold("March stone against nine Strands. The Spindle spins a Fragment."), true);
            } else {
                player.displayClientMessage(NinjacatText.teal("The Spindle needs every Strand seated before it will take March stone."), true);
            }
            return ItemInteractionResult.CONSUME;
        }

        // The Fragment itself → Reweave.
        if (stack.is(ModItems.SPINDLE_LOOM_FRAGMENT.get())) {
            if (state.getValue(REWOVEN) || LoomTension.clowderOf(sp).map(LoomTension::isRewoven).orElse(false)) {
                player.displayClientMessage(NinjacatText.teal("Your Clowder has already rewoven its sky."), true);
                refresh(serverLevel, pos, sp);                                       // a second Post catches up with the Clowder
            } else if (LoomTension.reweave(serverLevel, pos, sp)) {
                consume(player, stack);
                refresh(serverLevel, pos, sp);
            } else {
                player.displayClientMessage(NinjacatText.teal("Nine Strands first. Then the Fragment."), true);
            }
            return ItemInteractionResult.CONSUME;
        }

        return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (level.hasNeighborSignal(pos)) return InteractionResult.CONSUME;
        if (level.isClientSide || !(player instanceof ServerPlayer sp)) {
            return InteractionResult.SUCCESS;
        }
        if (!owns((ServerLevel) level, pos, sp)) {
            player.displayClientMessage(NinjacatText.teal("This Post answers to another Clowder."), true);
            return InteractionResult.CONSUME;
        }
        refresh((ServerLevel) level, pos, sp);
        LoomTension.clowderOf(sp).ifPresent(c -> {
            int bits = LoomTension.strandBits(c);
            StringBuilder seated = new StringBuilder();
            StringBuilder waiting = new StringBuilder();
            for (Strand s : Strand.ALL) {
                StringBuilder target = (bits & s.bit()) != 0 ? seated : waiting;
                if (target.length() > 0) {
                    target.append(", ");
                }
                target.append(s.title());
            }
            player.displayClientMessage(NinjacatText.gold("Tensioned: ").append(Component.literal(seated.length() == 0 ? "none yet" : seated.toString())), false);
            if (waiting.length() > 0) {
                player.displayClientMessage(NinjacatText.teal("Waiting: ").append(Component.literal(waiting.toString())), false);
            }
            if (LoomTension.isRewoven(c)) {
                player.displayClientMessage(NinjacatText.gold("Rewoven. The cut is closed above this pad."), false);
            }
        });
        return InteractionResult.CONSUME;
    }

    /**
     * A Post belongs to the Clowder that first used it. Unowned posts (placed before this rule, or whose
     * Clowder no longer exists — e.g. a party that was disbanded) are claimed by the next Clowder to use them.
     */
    private static boolean owns(ServerLevel level, BlockPos pos, ServerPlayer player) {
        if (!(level.getBlockEntity(pos) instanceof TensionPostBlockEntity be) || be.getClowder() == null) return true;
        var mine = LoomTension.clowderOf(player);
        if (mine.isEmpty()) return true;
        if (be.getClowder().equals(mine.get().id())) return true;
        if (LoomTension.clowderById(level.getServer(), be.getClowder()).isPresent()) return false;
        // Unknown id: a disbanded party (reclaimable) — but never a solo player who is merely offline. A solo Clowder's id is the
        // player's own UUID, so a saved player file settles it (the profile cache alone forgets players after a month away).
        if (java.nio.file.Files.exists(level.getServer().getWorldPath(net.minecraft.world.level.storage.LevelResource.PLAYER_DATA_DIR).resolve(be.getClowder() + ".dat"))) return false;
        return level.getServer().getProfileCache() == null || level.getServer().getProfileCache().get(be.getClowder()).isEmpty();
    }

    /** Re-read the Clowder's state into the blockstate (covers posts placed before a seat elsewhere). */
    private static void refresh(ServerLevel level, BlockPos pos, ServerPlayer player) {
        LoomTension.clowderOf(player).ifPresent(c -> {
            BlockState current = level.getBlockState(pos);
            BlockState next = withBits(current, LoomTension.strandBits(c), LoomTension.isRewoven(c));
            if (next != current) {
                level.setBlock(pos, next, 3);
            }
            if (level.getBlockEntity(pos) instanceof TensionPostBlockEntity be) {
                be.setClowder(c.id());
            }
        });
    }

    private static void consume(Player player, ItemStack stack) {
        if (!player.getAbilities().instabuild) {
            stack.shrink(1);
        }
    }
}
