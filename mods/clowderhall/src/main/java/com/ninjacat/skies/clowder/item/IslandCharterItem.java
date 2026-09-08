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
    private static final String RULES_TITLE = "Clowder Rules";
    private static final String RULES_AUTHOR = "Clowder Hall";


    public IslandCharterItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        boolean onDock = isOnDock(level, player);
        if (level.isClientSide) {
            if (!player.isShiftKeyDown()) {
                if (ModList.get().isLoaded("skyguis")) com.ninjacat.skies.clowder.client.ClowderClient.open();
                else player.displayClientMessage(NinjacatText.gold("Clowder UI requires Sky GUIs. Use /skyblock help for island commands."), false);
            }
        } else if (player instanceof ServerPlayer serverPlayer) {
            // Seal spawn only on an overworld pad — never Dock, Hall, Nether, or End.
            boolean onPad = level.dimension().equals(Level.OVERWORLD) && !onDock;
            if (onPad && player.isShiftKeyDown()) {
                if (!hasSolidFooting(level, serverPlayer.blockPosition())) {
                    serverPlayer.displayClientMessage(
                            NinjacatText.gold("Stand on solid pad ground before sealing spawn."),
                            true
                    );
                } else {
                    serverPlayer.setRespawnPosition(
                            serverPlayer.level().dimension(),
                            serverPlayer.blockPosition(),
                            serverPlayer.getYRot(),
                            true,
                            true
                    );
                    serverPlayer.displayClientMessage(
                            NinjacatText.teal("Pad spawn sealed here."),
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
                        NinjacatText.gold("Clowder Rules pressed into your hands."),
                        false
                );
            }

            if (onDock) {
                serverPlayer.displayClientMessage(
                        NinjacatText.teal("Open Create Team in the Clowder panel, name your Clowder, then pick a pad."),
                        false
                );
                serverPlayer.displayClientMessage(
                        NinjacatText.gold("After you land, sneak-use Charter to seal pad spawn. Lost? /clowder hub"),
                        false
                );
            } else if (!onPad) {
                serverPlayer.displayClientMessage(
                        NinjacatText.gold("Charter opens the Clowder panel. Sneak-use on your Overworld pad to seal spawn."),
                        false
                );
            }
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
    }

    /** Right-click another player while holding the Charter: invite them to your Clowder. */
    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
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

    /** Reject mid-air / void seals so soft-hardcore respawn does not drop the player. */
    private static boolean hasSolidFooting(Level level, BlockPos feet) {
        BlockPos below = feet.below();
        BlockState state = level.getBlockState(below);
        return !state.isAir() && !state.getCollisionShape(level, below).isEmpty();
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(NinjacatText.indigo("Names a pad as yours. Ink still wet."));
        tooltip.add(Component.literal("Use: Clowder panel. Right-click a friend: invite. Sneak-use on your pad: seal spawn."));
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
                Filterable.passThrough(Component.literal(
                        "Clowder Rules\n\n" +
                                "1. The Dock is shared.\n" +
                                "2. Pads belong to Clowders — claim via Create Team + pad template.\n" +
                                "3. Soil first. Stone: 1 Thread → 3 string; " +
                                "4 string → 2 Void Yarn; then Tension Barrel clay / porcelain / sieve.\n" +
                                "4. Frayed Thread buys help, not a skip past the braid."
                )),
                Filterable.passThrough(Component.literal(
                        "Strand tribes\n\n" +
                                "Soil — Pad-keepers\n" +
                                "Stone — Grit-singers\n" +
                                "Sprout — Rootbinders\n" +
                                "Claw — Edge-walkers\n" +
                                "Spark — Drumhearts\n" +
                                "Clock — Pattern-weavers\n" +
                                "Swarm — Colony-keepers\n" +
                                "Sigil — Seal-carvers\n" +
                                "Spindle — Loom-stitchers"
                )),
                Filterable.passThrough(Component.literal(
                        "How to start (OOC)\n\n" +
                                "1) Right-click Island Charter\n" +
                                "   (or press K — Clowder panel)\n" +
                                "2) Create Team → type a name\n" +
                                "3) Pick a pad template:\n" +
                                "   Ninjacat Pad = Normal\n" +
                                "   Dojo Cottage = Easy\n" +
                                "   Frayed Thread = Hard\n" +
                                "4) Open FTB Quests — start Soil.\n\n" +
                                "Invite a friend: hold this Charter and\n" +
                                "right-click them, or /clowder invite <name>.\n" +
                                "They accept with /clowder accept.\n\n" +
                                "Also: /clowder help · /clowder hub · Hub Key."
                )),
                Filterable.passThrough(Component.literal(
                        "If you feel lost\n\n" +
                                "• Dock is the hub, not your pad.\n" +
                                "• Charter opens Clowders; Create Team picks a pad.\n" +
                                "• On your pad: sneak-use Charter seals spawn here.\n" +
                                "• /clowder hub is always safe.\n" +
                                "• /clowder return leaves the Hall.\n" +
                                "• Whisker Codex = quests, rewards and hints.\n" +
                                "• How to Start book = plain OOC steps."
                ))
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
        return book;
    }
}
