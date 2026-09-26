package com.ninjacat.skies.craftweave;

import com.mojang.brigadier.CommandDispatcher;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * {@code /craftweave selftest} (operators): Craftweave on the server's real recipes. Four string in a square is both
 * vanilla's white wool and, in Ninjacat Skies, two Void Yarn: the test lays that grid on a crafting table for a stand-in
 * player, checks both recipes meet, cycles between them, and crafts each. The full-pack server gate runs it on the
 * packed Core jar; it prints one PASS or FAIL line.
 */
final class SelfTest {
    private static final Logger LOG = LoggerFactory.getLogger("craftweave");

    private SelfTest() {}

    static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("craftweave").requires(source -> source.hasPermission(2))
                .then(Commands.literal("selftest").executes(context -> {
                    String verdict = run(context.getSource().getLevel());
                    LOG.info("Craftweave selftest {}", verdict);
                    context.getSource().sendSuccess(() -> Component.literal("Craftweave selftest " + verdict), true);
                    return verdict.startsWith("PASS") ? 1 : 0;
                })));
    }

    static String run(ServerLevel level) {
        var player = FakePlayerFactory.getMinecraft(level);
        player.getInventory().clearContent();
        var menu = new CraftingMenu(0, player.getInventory(), ContainerLevelAccess.create(level, level.getSharedSpawnPos()));
        var previous = player.containerMenu;
        player.containerMenu = menu;
        CraftTables.owned(menu, player);
        List<String> notes = new ArrayList<>();
        try {
            for (int slot : new int[]{1, 2, 4, 5}) menu.getSlot(slot).set(new ItemStack(Items.STRING, 8));
            menu.slotsChanged(menu.getSlot(1).container);
            var matches = CraftTables.matches(level, CraftTables.input(menu));
            List<String> ids = matches.stream().map(h -> h.id().toString()).toList();
            notes.add("matches=" + ids);
            if (matches.size() < 2) return "FAIL four string in a square should meet at least two recipes; " + notes;
            boolean wool = false, yarn = false;
            for (int i = 0; i < matches.size() + 1; i++) {
                ItemStack shown = menu.getSlot(0).getItem().copy();
                notes.add("showing=" + shown);
                if (shown.isEmpty()) return "FAIL the table offered nothing; " + notes;
                int made = CraftTables.craft(player, 1);
                var id = net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(shown.getItem()).toString();
                if (made <= 0 || player.getInventory().countItem(shown.getItem()) <= 0) return "FAIL crafting " + id + " made nothing; " + notes;
                wool |= shown.is(Items.WHITE_WOOL);
                yarn |= id.equals("voidloom:void_yarn");
                ItemStack before = menu.getSlot(0).getItem().copy();
                CraftTables.cycle(player, 1);
                if (ItemStack.isSameItemSameComponents(before, menu.getSlot(0).getItem())) return "FAIL cycling did not change the result; " + notes;
            }
            if (!wool) return "FAIL white wool was never offered; " + notes;
            boolean pack = net.neoforged.fml.ModList.get().isLoaded("voidloom");
            if (pack && !yarn) return "FAIL Void Yarn was never offered; " + notes;
            return "PASS cycled " + matches.size() + " recipes on four string and crafted each (" + String.join(", ", ids) + ")";
        } finally {
            new Placer(menu).clear(player);
            player.containerMenu = previous;
            player.getInventory().clearContent();
        }
    }
}
