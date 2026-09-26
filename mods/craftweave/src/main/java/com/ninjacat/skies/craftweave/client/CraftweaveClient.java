package com.ninjacat.skies.craftweave.client;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import com.ninjacat.skies.craftweave.CraftTables;
import com.ninjacat.skies.craftweave.Craftweave;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.loading.FMLPaths;
import net.neoforged.neoforge.client.event.ScreenEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Craftweave at the table: three small things around the result slot, each shown only when it has a job.
 * <ul>
 *   <li>A "2/3" chip above the result when several recipes match the grid. Click for the next, right-click for the
 *       previous; the server remembers the pick for next time those recipes meet.</li>
 *   <li>A quantity box under the result. Empty or 1 is the table as always; type 64 and one click on the result
 *       crafts 64 (or as close as the grid allows) straight into the pack. Shift-click is untouched.</li>
 *   <li>A star beside the result bookmarks its recipe. Bookmarks wait on a slim tab at the table's right edge that
 *       opens on hover: click one to lay it out on the grid (the recipe book's own placement), right-click to drop it.</li>
 * </ul>
 */
public final class CraftweaveClient {
    private static final int INK = 0xE0101418, RIM = 0xFF3A4C52, TEXT = 0xFFE8E0CC, QUIET = 0xFF8FA0A0, GOLD = 0xFFFFD36B;
    private static final int ICON = 18, TAB_W = 14, MAX_SHOWN = 8;

    private static final Map<Screen, State> STATES = new WeakHashMap<>();
    private static List<ResourceLocation> bookmarks;

    private CraftweaveClient() {}

    /** Per open table: the quantity box and a cache of the recipes the grid matched last time we looked. */
    private static final class State {
        EditBox quantity;
        List<ItemStack> grid = List.of();
        List<RecipeHolder<CraftingRecipe>> matches = List.of();
        boolean tabOpen;
        int scroll;
    }

    public static void init(IEventBus modBus) {
        NeoForge.EVENT_BUS.addListener(CraftweaveClient::screenInit);
        NeoForge.EVENT_BUS.addListener(CraftweaveClient::renderPre);
        NeoForge.EVENT_BUS.addListener(CraftweaveClient::renderPost);
        NeoForge.EVENT_BUS.addListener(CraftweaveClient::mousePressed);
        NeoForge.EVENT_BUS.addListener(CraftweaveClient::mouseScrolled);
        NeoForge.EVENT_BUS.addListener(CraftweaveClient::keyPressed);
    }

    private static AbstractContainerScreen<?> table(Screen screen) {
        return screen instanceof AbstractContainerScreen<?> acs && CraftTables.isTable(acs.getMenu()) ? acs : null;
    }

    // ---- bookmarks, kept per player on this machine ---------------------------------------------------------------

    private static Path file() {
        return FMLPaths.CONFIGDIR.get().resolve("craftweave-bookmarks.json");
    }

    private static List<ResourceLocation> bookmarks() {
        if (bookmarks == null) {
            bookmarks = new ArrayList<>();
            try {
                if (Files.exists(file())) {
                    JsonArray array = JsonParser.parseString(Files.readString(file())).getAsJsonArray();
                    for (var element : array) {
                        ResourceLocation id = ResourceLocation.tryParse(element.getAsString());
                        if (id != null && !bookmarks.contains(id)) bookmarks.add(id);
                    }
                }
            } catch (Exception ignored) {
                // a damaged file starts an empty list rather than breaking the table
            }
        }
        return bookmarks;
    }

    private static void saveBookmarks() {
        try {
            Files.writeString(file(), new Gson().toJson(bookmarks().stream().map(ResourceLocation::toString).toList()));
        } catch (Exception ignored) {
            // bookmarks are a convenience: failing to save them must never break crafting
        }
    }

    private static RecipeHolder<CraftingRecipe> recipe(ResourceLocation id) {
        var level = Minecraft.getInstance().level;
        if (level == null) return null;
        var holder = level.getRecipeManager().byKey(id).orElse(null);
        if (holder == null || !(holder.value() instanceof CraftingRecipe)) return null;
        @SuppressWarnings("unchecked") RecipeHolder<CraftingRecipe> crafting = (RecipeHolder<CraftingRecipe>) holder;
        return crafting;
    }

    // ---- layout ---------------------------------------------------------------------------------------------------

    private static int resultX(AbstractContainerScreen<?> s) {
        return s.getGuiLeft() + s.getMenu().getSlot(0).x;
    }

    private static int resultY(AbstractContainerScreen<?> s) {
        return s.getGuiTop() + s.getMenu().getSlot(0).y;
    }

    private static int[] cycleBox(AbstractContainerScreen<?> s) {
        return new int[]{resultX(s) - 3, resultY(s) - 15, 22, 11};
    }

    private static int[] starBox(AbstractContainerScreen<?> s) {
        return new int[]{resultX(s) + 19, resultY(s) + 3, 10, 10};
    }

    /** The small clear button just off the grid's top-right corner. */
    private static int[] clearBox(AbstractContainerScreen<?> s) {
        var corner = s.getMenu().getSlot(3);
        return new int[]{s.getGuiLeft() + corner.x + 18, s.getGuiTop() + corner.y - 9, 8, 8};
    }

    private static boolean gridEmpty(AbstractContainerScreen<?> s) {
        for (int i = 1; i <= 9; i++) if (s.getMenu().getSlot(i).hasItem()) return false;
        return true;
    }

    private static int wanted(State state) {
        String text = state.quantity == null ? "" : state.quantity.getValue();
        return text.isEmpty() ? 1 : Math.max(1, Integer.parseInt(text));
    }

    private static void craftWanted(AbstractContainerScreen<?> s, State state) {
        PacketDistributor.sendToServer(new Craftweave.Craft(s.getMenu().containerId, Math.min(wanted(state), CraftTables.MAX_ITEMS)));
        Minecraft.getInstance().getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(
                net.minecraft.sounds.SoundEvents.UI_BUTTON_CLICK.value(), 1.2F, 0.4F));
    }

    private static int[] tabBox(AbstractContainerScreen<?> s, State state) {
        int x = s.getGuiLeft() + s.getXSize(), y = s.getGuiTop() + 4;
        int shown = Math.min(MAX_SHOWN, bookmarks().size());
        return state.tabOpen ? new int[]{x, y, ICON + 6, 14 + shown * ICON + 4} : new int[]{x, y, TAB_W, 22};
    }

    private static boolean inside(int[] box, double mx, double my) {
        return mx >= box[0] && mx < box[0] + box[2] && my >= box[1] && my < box[1] + box[3];
    }

    private static List<RecipeHolder<CraftingRecipe>> matches(AbstractContainerScreen<?> s, State state) {
        var level = Minecraft.getInstance().level;
        if (level == null) return List.of();
        List<ItemStack> now = new ArrayList<>(9);
        for (int i = 1; i <= 9; i++) now.add(s.getMenu().getSlot(i).getItem().copy());
        boolean same = now.size() == state.grid.size();
        for (int i = 0; same && i < now.size(); i++) same = ItemStack.matches(now.get(i), state.grid.get(i));
        if (!same) {
            state.grid = now;
            state.matches = CraftTables.matches(level, CraftTables.input(s.getMenu()));
        }
        return state.matches;
    }

    /** The recipe the result slot is showing, when one can be told apart. */
    private static RecipeHolder<CraftingRecipe> current(AbstractContainerScreen<?> s, State state) {
        var list = matches(s, state);
        if (list.isEmpty() || s.getMenu().getSlot(0).getItem().isEmpty()) return null;
        return list.get(CraftTables.index(Minecraft.getInstance().level, s.getMenu(), list));
    }

    // ---- events ---------------------------------------------------------------------------------------------------

    private static void screenInit(ScreenEvent.Init.Post event) {
        AbstractContainerScreen<?> s = table(event.getScreen());
        if (s == null) return;
        State state = STATES.computeIfAbsent(s, k -> new State());
        String kept = state.quantity == null ? "" : state.quantity.getValue();
        EditBox box = new EditBox(Minecraft.getInstance().font, resultX(s) - 4, resultY(s) + 21, 24, 11, Component.translatable("craftweave.quantity"));
        box.setMaxLength(4);
        box.setFilter(text -> text.matches("\\d{0,4}"));
        box.setBordered(false);
        box.setTextColor(TEXT);
        box.setHint(Component.literal("×1").withStyle(ChatFormatting.GRAY));
        box.setValue(kept);
        box.setTooltip(net.minecraft.client.gui.components.Tooltip.create(Component.translatable("craftweave.quantity.tip")));
        state.quantity = box;
        event.addListener(box);
    }

    private static void renderPre(ScreenEvent.Render.Pre event) {
        AbstractContainerScreen<?> s = table(event.getScreen());
        State state = s == null ? null : STATES.get(s);
        if (state == null || state.quantity == null) return;
        // the recipe book slides the table sideways: keep the box under the result
        state.quantity.setX(resultX(s) - 2);
        state.quantity.setY(resultY(s) + 23);
    }

    private static void renderPost(ScreenEvent.Render.Post event) {
        AbstractContainerScreen<?> s = table(event.getScreen());
        State state = s == null ? null : STATES.get(s);
        if (state == null) return;
        GuiGraphics g = event.getGuiGraphics();
        var font = Minecraft.getInstance().font;
        int mx = event.getMouseX(), my = event.getMouseY();
        g.pose().pushPose();
        g.pose().translate(0, 0, 300);

        // the quantity box's frame, drawn under the widget's text
        int qx = resultX(s) - 4, qy = resultY(s) + 21;
        g.fill(qx, qy, qx + 24, qy + 11, 0xB0101418);
        g.renderOutline(qx, qy, 24, 11, state.quantity != null && state.quantity.isFocused() ? GOLD : RIM);
        if (state.quantity != null) state.quantity.render(g, mx, my, event.getPartialTick());
        RecipeHolder<CraftingRecipe> made = current(s, state);
        if (made != null) {
            int can = CraftTables.canMake(Minecraft.getInstance().player, s.getMenu(), made);
            String max = Component.translatable("craftweave.max", can).getString();
            g.pose().pushPose();
            g.pose().translate(qx + 26, qy + 3, 0);
            g.pose().scale(0.6F, 0.6F, 1);
            g.drawString(font, max, 0, 0, can >= wanted(state) ? QUIET : 0xFFE08070, false);
            g.pose().popPose();
        }
        if (!gridEmpty(s)) {
            int[] c = clearBox(s);
            boolean hot = inside(c, mx, my);
            g.drawString(font, "\u00d7", c[0] + 1, c[1] - 1, hot ? 0xFFFF8070 : QUIET, false);
            if (hot) g.renderTooltip(font, Component.translatable("craftweave.clear"), mx, my);
        }

        var list = matches(s, state);
        if (list.size() > 1) {
            int[] c = cycleBox(s);
            boolean hot = inside(c, mx, my);
            g.fill(c[0], c[1], c[0] + c[2], c[1] + c[3], hot ? 0xF0203038 : INK);
            g.renderOutline(c[0], c[1], c[2], c[3], hot ? GOLD : RIM);
            int at = CraftTables.index(Minecraft.getInstance().level, s.getMenu(), list) + 1;
            String label = at + "/" + list.size();
            g.pose().pushPose();
            g.pose().translate(c[0] + c[2] / 2F, c[1] + 2, 0);
            g.pose().scale(0.75F, 0.75F, 1);
            g.drawCenteredString(font, label, 0, 0, hot ? GOLD : TEXT);
            g.pose().popPose();
            if (hot) g.renderComponentTooltip(font, List.of(
                    Component.translatable("craftweave.cycle", at, list.size()).withStyle(ChatFormatting.GOLD),
                    Component.translatable("craftweave.cycle.tip").withStyle(ChatFormatting.GRAY)), mx, my);
        }

        RecipeHolder<CraftingRecipe> showing = current(s, state);
        if (showing != null) {
            int[] b = starBox(s);
            boolean marked = bookmarks().contains(showing.id()), hot = inside(b, mx, my);
            g.drawString(font, marked ? "★" : "☆", b[0] + 1, b[1], marked ? GOLD : hot ? TEXT : QUIET, false);
            if (hot) g.renderTooltip(font, Component.translatable(marked ? "craftweave.unbookmark" : "craftweave.bookmark"), mx, my);
        }

        if (!bookmarks().isEmpty()) {
            int[] t = tabBox(s, state);
            state.tabOpen = inside(t, mx, my) || (state.tabOpen && inside(tabBox(s, state), mx, my));
            t = tabBox(s, state);
            g.fill(t[0], t[1], t[0] + t[2], t[1] + t[3], INK);
            g.renderOutline(t[0] - 1, t[1], t[2] + 1, t[3], RIM);
            if (!state.tabOpen) {
                g.drawString(font, "★", t[0] + 3, t[1] + 3, GOLD, false);
                g.pose().pushPose();
                g.pose().translate(t[0] + TAB_W / 2F, t[1] + 13, 0);
                g.pose().scale(0.6F, 0.6F, 1);
                g.drawCenteredString(font, String.valueOf(bookmarks().size()), 0, 0, QUIET);
                g.pose().popPose();
            } else {
                g.drawString(font, "★", t[0] + 8, t[1] + 3, GOLD, false);
                List<ResourceLocation> marks = bookmarks();
                state.scroll = Math.max(0, Math.min(state.scroll, marks.size() - MAX_SHOWN));
                for (int i = 0; i < Math.min(MAX_SHOWN, marks.size()); i++) {
                    var holder = recipe(marks.get(i + state.scroll));
                    int ix = t[0] + 3, iy = t[1] + 14 + i * ICON;
                    boolean hot = mx >= ix && mx < ix + ICON && my >= iy && my < iy + ICON;
                    if (hot) g.fill(ix, iy, ix + ICON, iy + ICON, 0x60FFFFFF);
                    if (holder == null) {
                        g.drawString(font, "?", ix + 6, iy + 5, QUIET, false);
                        continue;
                    }
                    ItemStack out = holder.value().getResultItem(Minecraft.getInstance().level.registryAccess());
                    g.renderItem(out, ix + 1, iy + 1);
                    g.renderItemDecorations(font, out, ix + 1, iy + 1);
                    int can = CraftTables.canMake(Minecraft.getInstance().player, s.getMenu(), holder);
                    if (can == 0) g.fill(ix + 1, iy + 1, ix + 17, iy + 17, 0x80400000);
                    if (hot) g.renderComponentTooltip(font, List.of(out.getHoverName().copy().withStyle(ChatFormatting.WHITE),
                            can > 0 ? Component.translatable("craftweave.bookmark.can", can).withStyle(ChatFormatting.GREEN)
                                    : Component.translatable("craftweave.bookmark.short").withStyle(ChatFormatting.RED),
                            Component.translatable("craftweave.bookmark.place").withStyle(ChatFormatting.GRAY),
                            Component.translatable("craftweave.bookmark.remove").withStyle(ChatFormatting.DARK_GRAY)), mx, my);
                }
                if (marks.size() > MAX_SHOWN) {
                    g.pose().pushPose();
                    g.pose().translate(t[0] + t[2] / 2F, t[1] + t[3] - 3, 0);
                    g.pose().scale(0.6F, 0.6F, 1);
                    g.drawCenteredString(font, (state.scroll + 1) + "-" + (state.scroll + MAX_SHOWN) + "/" + marks.size(), 0, 0, QUIET);
                    g.pose().popPose();
                }
            }
        }
        g.pose().popPose();
    }

    private static void mousePressed(ScreenEvent.MouseButtonPressed.Pre event) {
        AbstractContainerScreen<?> s = table(event.getScreen());
        State state = s == null ? null : STATES.get(s);
        if (state == null) return;
        double mx = event.getMouseX(), my = event.getMouseY();
        int button = event.getButton();
        int container = s.getMenu().containerId;
        var mc = Minecraft.getInstance();

        if (matches(s, state).size() > 1 && inside(cycleBox(s), mx, my)) {
            PacketDistributor.sendToServer(new Craftweave.Cycle(container, button == 1 ? -1 : 1));
            mc.getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(net.minecraft.sounds.SoundEvents.UI_BUTTON_CLICK.value(), 1.4F, 0.4F));
            event.setCanceled(true);
            return;
        }
        if (!gridEmpty(s) && inside(clearBox(s), mx, my)) {
            PacketDistributor.sendToServer(new Craftweave.Clear(container));
            event.setCanceled(true);
            return;
        }
        RecipeHolder<CraftingRecipe> showing = current(s, state);
        if (showing != null && inside(starBox(s), mx, my)) {
            if (!bookmarks().remove(showing.id())) bookmarks().add(0, showing.id());
            saveBookmarks();
            event.setCanceled(true);
            return;
        }
        if (!bookmarks().isEmpty() && state.tabOpen && inside(tabBox(s, state), mx, my)) {
            int[] t = tabBox(s, state);
            int row = (int) ((my - t[1] - 14) / ICON);
            if (row >= 0 && row < Math.min(MAX_SHOWN, bookmarks().size())) {
                ResourceLocation id = bookmarks().get(row + state.scroll);
                if (button == 1) {
                    bookmarks().remove(id);
                    saveBookmarks();
                } else {
                    if (recipe(id) != null) PacketDistributor.sendToServer(new Craftweave.Place(container, id, Screen.hasShiftDown()));
                }
            }
            event.setCanceled(true);
            return;
        }
        // a typed quantity turns one click on the result into that many items
        int[] result = {resultX(s) - 4, resultY(s) - 4, 24, 24};   // the result slot and its frame, where the click landed
        if (button == 0 && !Screen.hasShiftDown() && state.quantity != null && inside(result, mx, my)
                && s.getMenu().getSlot(0).hasItem()) {
            if (wanted(state) > 1) {
                craftWanted(s, state);
                event.setCanceled(true);
            }
        }
        if (state.quantity != null && !state.quantity.isMouseOver(mx, my)) state.quantity.setFocused(false);
    }

    private static void mouseScrolled(ScreenEvent.MouseScrolled.Pre event) {
        AbstractContainerScreen<?> s = table(event.getScreen());
        State state = s == null ? null : STATES.get(s);
        if (state != null && state.quantity != null && inside(new int[]{resultX(s) - 4, resultY(s) + 21, 24, 11}, event.getMouseX(), event.getMouseY())) {
            // the wheel nudges the quantity: one at a time, a stack at a time with shift
            int step = Screen.hasShiftDown() ? 64 : 1;
            int next = Math.max(1, Math.min(9999, wanted(state) + (int) Math.signum(event.getScrollDeltaY()) * step));
            state.quantity.setValue(next == 1 ? "" : String.valueOf(next));
            event.setCanceled(true);
            return;
        }
        if (state == null || !state.tabOpen || !inside(tabBox(s, state), event.getMouseX(), event.getMouseY())) return;
        state.scroll -= (int) Math.signum(event.getScrollDeltaY());
        event.setCanceled(true);
    }

    /** Enter in the quantity box crafts that many, without reaching for the result slot. */
    private static void keyPressed(ScreenEvent.KeyPressed.Pre event) {
        AbstractContainerScreen<?> s = table(event.getScreen());
        State state = s == null ? null : STATES.get(s);
        if (state == null || state.quantity == null || !state.quantity.isFocused()) return;
        int key = event.getKeyCode();
        if ((key == org.lwjgl.glfw.GLFW.GLFW_KEY_ENTER || key == org.lwjgl.glfw.GLFW.GLFW_KEY_KP_ENTER) && s.getMenu().getSlot(0).hasItem()) {
            craftWanted(s, state);
            event.setCanceled(true);
        }
    }
}
