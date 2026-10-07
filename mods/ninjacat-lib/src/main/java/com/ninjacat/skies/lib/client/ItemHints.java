package com.ninjacat.skies.lib.client;

import com.ninjacat.skies.lib.NinjacatLib;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.language.I18n;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.FormattedText;
import net.minecraft.network.chat.Style;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.ItemTooltipEvent;

import java.util.List;
import java.util.Set;

/**
 * A grey how-to line for any item or block of the companion mods that declares {@code <descriptionId>.hint}
 * in its lang file, and a darker second line for {@code <descriptionId>.hint.2}. Long lines wrap to a
 * tooltip's width. Items the pack already describes through its own scripts simply declare no hint.
 *
 * <p>Only the Core companions' items are considered. Tribal Power, Chocobos Reborn and Shamanic Mounts run
 * the same hook for their own namespaces; a hint key looked up for every item would print once per mod.
 */
@EventBusSubscriber(modid = NinjacatLib.MOD_ID, value = Dist.CLIENT)
public final class ItemHints {
    private static final int WRAP_WIDTH = 220;
    /** The mod ids packaged into Ninjacat Skies Core (see tools/build_core_jar.py COMPANIONS). */
    private static final Set<String> NAMESPACES = Set.of(NinjacatLib.MOD_ID, "ninjacatskies", "voidloom",
            "clowderhall", "guardians", "driftwrecks", "craftweave");

    private ItemHints() {}

    @SubscribeEvent
    public static void tooltip(ItemTooltipEvent event) {
        if (!NAMESPACES.contains(BuiltInRegistries.ITEM.getKey(event.getItemStack().getItem()).getNamespace())) return;
        String key = event.getItemStack().getItem().getDescriptionId() + ".hint";
        if (I18n.exists(key)) addWrapped(event.getToolTip(), Component.translatable(key), ChatFormatting.GRAY);
        if (I18n.exists(key + ".2")) addWrapped(event.getToolTip(), Component.translatable(key + ".2"), ChatFormatting.DARK_GRAY);
    }

    private static void addWrapped(List<Component> lines, Component text, ChatFormatting colour) {
        for (FormattedText part : Minecraft.getInstance().font.getSplitter().splitLines(text, WRAP_WIDTH, Style.EMPTY)) {
            lines.add(Component.literal(part.getString()).withStyle(colour));
        }
    }
}
