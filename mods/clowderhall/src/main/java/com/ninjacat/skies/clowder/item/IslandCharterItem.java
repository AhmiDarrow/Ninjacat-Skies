package com.ninjacat.skies.clowder.item;

import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.Filterable;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.WrittenBookContent;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

import net.neoforged.fml.ModList;
import java.util.List;

/**
 * Ceremony item for claiming/visiting a Clowder island.
 * Full island placement is owned by Skyblock Builder / Sky GUIs;
 * this item is the pack-facing ritual and opens the guided Create Team screen.
 */
public class IslandCharterItem extends Item {
    private static final String RULES_TITLE = "Clowder Rules";   // lang-exempt: vanilla book title is a plain string (matched by id); the shown name is the CUSTOM_NAME key
    private static final String RULES_AUTHOR = "Clowder Hall";   // lang-exempt: vanilla book author is a plain string, a byline name


    public IslandCharterItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.isSpectator()) return InteractionResultHolder.fail(stack);
        boolean onDock = isOnDock(level, player);
        if (level.isClientSide) {
            if (!player.isShiftKeyDown()) {
                if (ModList.get().isLoaded("skyguis")) com.ninjacat.skies.clowder.client.ClowderClient.open();
                else player.displayClientMessage(NinjacatText.goldKey("message.clowderhall.charter.needs_skyguis"), false);
            }
        } else if (player instanceof ServerPlayer serverPlayer) {
            // Seal spawn only on an overworld pad — never Dock, Hall, Nether, or End.
            boolean onPad = level.dimension().equals(Level.OVERWORLD) && !onDock;
            if (onPad && player.isShiftKeyDown()) {
                BlockPos feet = serverPlayer.blockPosition();
                // Forced respawn rejects a pos whose block (or the one above) is solid, so a
                // slab/farmland/path at the feet stores the air block above it.
                BlockPos spawn = level.getBlockState(feet).getCollisionShape(level, feet).isEmpty() ? feet : feet.above();
                if (!hasSolidFooting(level, feet)) {
                    serverPlayer.displayClientMessage(
                            NinjacatText.goldKey("message.clowderhall.charter.need_solid_ground"),
                            true
                    );
                } else if (!canRespawnIn(level, spawn) || !canRespawnIn(level, spawn.above())) {
                    serverPlayer.displayClientMessage(
                            NinjacatText.goldKey("message.clowderhall.charter.no_headroom"),
                            true
                    );
                } else {
                    serverPlayer.setRespawnPosition(
                            serverPlayer.level().dimension(),
                            spawn,
                            serverPlayer.getYRot(),
                            true,
                            true
                    );
                    serverPlayer.displayClientMessage(
                            NinjacatText.tealKey("message.clowderhall.charter.spawn_sealed"),
                            true
                    );
                }
            }

            if (!playerHasRulesBook(serverPlayer)) {
                ItemStack book = createRulesBook();
                if (!serverPlayer.getInventory().add(book)) {
                    serverPlayer.drop(book, false);
                }
                serverPlayer.displayClientMessage(
                        NinjacatText.goldKey("message.clowderhall.charter.rules_given"),
                        false
                );
            }

            if (onDock) {
                serverPlayer.displayClientMessage(
                        NinjacatText.tealKey("message.clowderhall.charter.dock_create_team"),
                        false
                );
                serverPlayer.displayClientMessage(
                        NinjacatText.goldKey("message.clowderhall.charter.dock_after_land"),
                        false
                );
            } else if (!onPad) {
                serverPlayer.displayClientMessage(
                        NinjacatText.goldKey("message.clowderhall.charter.off_pad"),
                        false
                );
            }
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }

    /** Right-click another player while holding the Charter: invite them to your Clowder. */
    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (player.isSpectator()) return InteractionResult.FAIL;
        if (player.level().isClientSide) {
            return target instanceof Player ? InteractionResult.SUCCESS : InteractionResult.PASS;
        }
        if (player instanceof ServerPlayer actor && target instanceof ServerPlayer invitee
                && ModList.get().isLoaded("skyblockbuilder")) {
            com.ninjacat.skies.clowder.command.ClowderCommands.doInvite(actor, invitee);
            return InteractionResult.SUCCESS;
        }
        return InteractionResult.PASS;
    }

    /** Overworld shared spawn only — Clowder Hall pad center must not count as Dock. */
    private static boolean isOnDock(Level level, Player player) {
        if (!level.dimension().equals(Level.OVERWORLD)) {
            return false;
        }
        return player.blockPosition().closerThan(level.getSharedSpawnPos(), 24.0);
    }

    /** Reject mid-air / void seals so soft-hardcore respawn does not drop the player.
     *  Same footing rule as hub/arena snap: a slab/farmland at the feet counts, not only the block below. */
    private static boolean hasSolidFooting(Level level, BlockPos feet) {
        BlockState atFeet = level.getBlockState(feet);
        if (!atFeet.getCollisionShape(level, feet).isEmpty()) {
            return !atFeet.isCollisionShapeFullBlock(level, feet);
        }
        BlockPos below = feet.below();
        BlockState under = level.getBlockState(below);
        return under.blocksMotion() || !under.getCollisionShape(level, below).isEmpty();
    }

    /** Same test as ServerPlayer.findRespawnAndUseSpawnBlock for a forced spawn. */
    private static boolean canRespawnIn(Level level, BlockPos pos) {
        BlockState state = level.getBlockState(pos);
        return state.getBlock().isPossibleToRespawnInThis(state);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(NinjacatText.indigoKey("message.clowderhall.charter.tooltip"));
        tooltip.add(Component.translatable("item.clowderhall.island_charter.desc"));
    }

    private static boolean playerHasRulesBook(ServerPlayer player) {
        for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
            ItemStack slot = player.getInventory().getItem(i);
            if (!slot.is(Items.WRITTEN_BOOK)) {
                continue;
            }
            WrittenBookContent content = slot.get(DataComponents.WRITTEN_BOOK_CONTENT);
            if (content != null && RULES_TITLE.equals(content.title().raw())) {
                return true;
            }
        }
        return false;
    }

    private static ItemStack createRulesBook() {
        List<Filterable<Component>> pages = List.of(
                Filterable.passThrough(Component.translatable("message.clowderhall.book_rules.page_1")),
                Filterable.passThrough(Component.translatable("message.clowderhall.book_rules.page_2")),
                Filterable.passThrough(Component.translatable("message.clowderhall.book_rules.page_3")),
                Filterable.passThrough(Component.translatable("message.clowderhall.book_rules.page_4"))
        );
        WrittenBookContent content = new WrittenBookContent(
                Filterable.passThrough(RULES_TITLE),
                RULES_AUTHOR,
                0,
                pages,
                true
        );
        ItemStack book = new ItemStack(Items.WRITTEN_BOOK);
        book.set(DataComponents.WRITTEN_BOOK_CONTENT, content);
        book.set(DataComponents.CUSTOM_NAME, Component.translatable("message.clowderhall.book_rules.title").withStyle(s -> s.withItalic(false)));
        return book;
    }
}
