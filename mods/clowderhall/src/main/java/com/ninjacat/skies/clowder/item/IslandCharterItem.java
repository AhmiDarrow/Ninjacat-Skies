package com.ninjacat.skies.clowder.item;

import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.Filterable;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.WrittenBookContent;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

import java.lang.reflect.Method;
import java.util.List;

/**
 * Ceremony item for claiming/visiting a Clowder island.
 * Full island placement is owned by Skyblock Builder / Sky GUIs;
 * this item is the pack-facing ritual and opens the guided Create Team screen.
 */
public class IslandCharterItem extends Item {
    private static final String RULES_TITLE = "Clowder Rules";
    private static final String RULES_AUTHOR = "Clowder Hall";
    private static final String CREATE_TEAM_SCREEN = "de.melanx.skyguis.client.screen.CreateTeamScreen";

    public IslandCharterItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        boolean onDock = isOnDock(level, player);
        if (level.isClientSide) {
            // Create Team only on overworld Dock — never in Hall or on a claimed pad.
            if (onDock) {
                openCreateTeamScreen();
            }
        } else if (player instanceof ServerPlayer serverPlayer) {
            // Seal spawn only on an overworld pad — never Dock, Hall, Nether, or End.
            boolean onPad = level.dimension().equals(Level.OVERWORLD) && !onDock;
            if (onPad) {
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
                        NinjacatText.teal("Create Team should be open — name your Clowder, then pick a pad."),
                        false
                );
                serverPlayer.displayClientMessage(
                        NinjacatText.gold("After you land, right-click Charter again to seal pad spawn. Lost? /clowder hub"),
                        false
                );
            } else if (!onPad) {
                serverPlayer.displayClientMessage(
                        NinjacatText.gold("Create Team only on Clowder Dock — Hub Key /clowder return, then Charter."),
                        false
                );
            }
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
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
        tooltip.add(Component.literal("Dock: Create Team. Overworld pad: seal spawn."));
    }

    private static void openCreateTeamScreen() {
        try {
            Class<?> screen = Class.forName(CREATE_TEAM_SCREEN);
            Method open = screen.getMethod("open");
            open.invoke(null);
        } catch (ReflectiveOperationException ex) {
            // Sky GUIs optional at compile; present in pack runtime.
            // Reflect Minecraft so this common class stays server-safe if the API renames.
            try {
                Class<?> mcClass = Class.forName("net.minecraft.client.Minecraft");
                Object mc = mcClass.getMethod("getInstance").invoke(null);
                Object player = mcClass.getField("player").get(mc);
                if (player != null) {
                    Method tell = player.getClass().getMethod(
                            "displayClientMessage",
                            net.minecraft.network.chat.Component.class,
                            boolean.class
                    );
                    tell.invoke(
                            player,
                            NinjacatText.gold("Create Team UI missing — press C (Sky GUIs) or /skyblock team."),
                            false
                    );
                }
            } catch (ReflectiveOperationException | RuntimeException ignored) {
                // Dedicated server / no client player — server-side Charter lines already guide.
            }
        }
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
                                "   (or press C — Sky GUIs)\n" +
                                "2) Create Team → type a name\n" +
                                "3) Pick a pad template:\n" +
                                "   Ninjacat Pad = Normal\n" +
                                "   Dojo Cottage = Easy\n" +
                                "   Frayed Thread = Hard\n" +
                                "4) Open FTB Quests — start Soil.\n\n" +
                                "Also: /clowder help · /clowder hub · Hub Key.\n" +
                                "Advanced: /skyblock create <name> skips pad pick."
                )),
                Filterable.passThrough(Component.literal(
                        "If you feel lost\n\n" +
                                "• Dock is the hub, not your pad.\n" +
                                "• On Dock: Charter opens Create Team (pick a pad).\n" +
                                "• On your pad: Charter seals spawn here.\n" +
                                "• /clowder hub is always safe.\n" +
                                "• /clowder return leaves the Hall.\n" +
                                "• Whisker Codex = in-world voice guide.\n" +
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
