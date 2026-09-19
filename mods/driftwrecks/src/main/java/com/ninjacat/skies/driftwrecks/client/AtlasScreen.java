package com.ninjacat.skies.driftwrecks.client;

import com.ninjacat.skies.core.client.ClientTension;
import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.registry.DwBlocks;
import com.ninjacat.skies.driftwrecks.wreck.WreckCore;
import com.ninjacat.skies.driftwrecks.wreck.WreckModifier;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

import java.util.ArrayList;
import java.util.List;

/**
 * The Wreck Atlas: nine Strand columns by six core rows. A filled cell shows that tribe's Keepsake (or a glowing
 * thread knot if the Keepsake is still out there); a locked column waits for its Strand. Below: modifier stamps,
 * Remnant stamps and the perks the Clowder has earned.
 */
public class AtlasScreen extends Screen {
    private static final int CELL = 22, GAP = 2;
    private static final int INK = 0xFF2A2F4F, PAPER = 0xFFEDE3CC, PAPER_DARK = 0xFFD9CBA8, TEAL = 0xFF3D7A7A, GOLD = 0xFFD4A84B, FADED = 0xFF9C9181;

    public AtlasScreen() { super(Component.translatable("item.driftwrecks.wreck_atlas")); }

    @Override public boolean isPauseScreen() { return false; }

    @Override
    public void render(GuiGraphics g, int mx, int my, float partial) {
        super.render(g, mx, my, partial);
        CompoundTag t = ClientAtlas.get();
        CompoundTag atlas = t.getCompound("atlas");
        int cols = Strand.ALL.length, rows = WreckCore.ALL.length;
        int gridW = cols * (CELL + GAP), gridH = rows * (CELL + GAP);
        int left = 70, panelW = left + gridW + 16, panelH = 34 + gridH + 96;
        int x0 = (width - panelW) / 2, y0 = Math.max(4, (height - panelH) / 2);
        g.fill(x0 - 2, y0 - 2, x0 + panelW + 2, y0 + panelH + 2, INK);
        g.fill(x0, y0, x0 + panelW, y0 + panelH, PAPER);
        int cells = 0;
        for (Strand s : Strand.ALL) cells += Integer.bitCount(atlas.getInt(s.id()));
        g.drawString(font, title, x0 + 8, y0 + 6, INK, false);
        String count = cells + " / " + (cols * rows);
        g.drawString(font, count, x0 + panelW - 8 - font.width(count), y0 + 6, TEAL, false);
        int gx = x0 + left, gy = y0 + 30;
        List<Component> tip = new ArrayList<>();
        for (int c = 0; c < cols; c++) {
            Strand s = Strand.ALL[c];
            boolean open = ClientTension.isSeated(s);
            int cx = gx + c * (CELL + GAP);
            int colour = 0xFF000000 | s.color();
            g.fill(cx, gy - 10, cx + CELL, gy - 7, open ? colour : FADED);
            if (mx >= cx && mx < cx + CELL && my >= gy - 12 && my < gy) {
                tip.add(Component.literal(s.tribe()).withStyle(st -> st.withColor(s.color())));
                if (!open) tip.add(Component.translatable("gui.driftwrecks.atlas.locked", s.title()));
            }
            for (int r = 0; r < rows; r++) {
                WreckCore core = WreckCore.ALL[r];
                int cy = gy + r * (CELL + GAP);
                boolean filled = (atlas.getInt(s.id()) & core.bit()) != 0;
                boolean keepsake = (t.getLong("keepsakes") & (1L << (s.ordinal() * rows + r))) != 0;
                g.fill(cx, cy, cx + CELL, cy + CELL, open ? PAPER_DARK : FADED);
                if (filled) {
                    g.fill(cx + 1, cy + 1, cx + CELL - 1, cy + CELL - 1, 0x55000000 | s.color());
                    if (keepsake) g.renderItem(new ItemStack(DwBlocks.keepsake(s, core)), cx + 3, cy + 3);
                    else g.fill(cx + 8, cy + 8, cx + CELL - 8, cy + CELL - 8, TEAL);
                }
                if (mx >= cx && mx < cx + CELL && my >= cy && my < cy + CELL) {
                    tip.add(Component.literal(s.tribe() + " · " + core.title).withStyle(st -> st.withColor(s.color())));
                    if (!open) tip.add(Component.translatable("gui.driftwrecks.atlas.locked", s.title()));
                    else if (filled) tip.add(Component.translatable("gui.driftwrecks.place." + s.id() + "_" + core.id).withStyle(st -> st.withItalic(true).withColor(0x3D7A7A)));
                    else tip.add(Component.translatable("gui.driftwrecks.atlas.unseen"));
                    if (keepsake) tip.add(Component.translatable("block.driftwrecks.keepsake_" + s.id() + "_" + core.id).withStyle(st -> st.withColor(0xD4A84B)));
                }
            }
        }
        for (int r = 0; r < rows; r++) {
            WreckCore core = WreckCore.ALL[r];
            boolean row = true;
            for (Strand s : Strand.ALL) if ((atlas.getInt(s.id()) & core.bit()) == 0) row = false;
            g.drawString(font, core.title, x0 + 8, gy + r * (CELL + GAP) + 7, row ? GOLD : INK, false);
        }
        // stamps
        int sy = gy + gridH + 8;
        g.drawString(font, Component.translatable("gui.driftwrecks.atlas.stamps"), x0 + 8, sy, INK, false);
        int mods = t.getInt("modStamps");
        for (int i = 0; i < WreckModifier.ALL.length; i++) {
            int bx = x0 + left + i * 38;
            boolean on = (mods & (1 << i)) != 0;
            g.fill(bx, sy - 2, bx + 34, sy + 10, on ? TEAL : PAPER_DARK);
            g.drawString(font, WreckModifier.ALL[i].title.substring(0, Math.min(6, WreckModifier.ALL[i].title.length())), bx + 2, sy, on ? PAPER : FADED, false);
        }
        int ry = sy + 16;
        g.drawString(font, Component.translatable("gui.driftwrecks.atlas.remnants"), x0 + 8, ry, INK, false);
        int rem = t.getInt("remnants");
        for (int i = 0; i < Strand.ALL.length; i++) {
            int bx = gx + i * (CELL + GAP) + 6;
            boolean on = (rem & (1 << i)) != 0;
            g.fill(bx, ry - 1, bx + 9, ry + 8, on ? 0xFF000000 | Strand.ALL[i].color() : PAPER_DARK);
        }
        // perks
        int py = ry + 16;
        List<String> perks = perks(t, atlas, mods, rem);
        g.drawString(font, Component.translatable("gui.driftwrecks.atlas.perks"), x0 + 8, py, INK, false);
        if (perks.isEmpty()) g.drawString(font, Component.translatable("gui.driftwrecks.atlas.no_perks"), x0 + left, py, FADED, false);
        for (int i = 0; i < perks.size() && i < 4; i++) g.drawString(font, perks.get(i), x0 + left, py + i * 10, TEAL, false);
        int hw = t.getInt("heartwreck");
        if (hw > 0) g.drawString(font, Component.translatable("gui.driftwrecks.atlas.heart." + Math.min(3, hw)), x0 + 8, y0 + panelH - 12, GOLD, false);
        if (!tip.isEmpty()) g.renderComponentTooltip(font, tip, mx, my);
    }

    private static List<String> perks(CompoundTag t, CompoundTag atlas, int mods, int rem) {
        List<String> out = new ArrayList<>();
        for (Strand s : Strand.ALL) if (Integer.bitCount(atlas.getInt(s.id())) == WreckCore.ALL.length) out.add(s.title() + ": half-price lures, +10% " + s.title() + " wrecks, banner");
        for (WreckCore c : WreckCore.ALL) {
            boolean row = true;
            for (Strand s : Strand.ALL) if ((atlas.getInt(s.id()) & c.bit()) == 0) row = false;
            if (row) out.add(c.title + " hidden rooms always open");
        }
        if (Integer.bitCount(mods) == WreckModifier.ALL.length) out.add("Wrecks hold 25% longer");
        if (Integer.bitCount(rem) == Strand.ALL.length) out.add("Weft Keys cost half");
        return out;
    }
}
