package com.ninjacat.skies.lib;

import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.Style;
import net.minecraft.network.chat.TextColor;

/** Shared Codex-voice text helpers. Keep copy short and concrete. */
public final class NinjacatText {
    public static final int INDIGO = 0x2A2F4F;
    public static final int TEAL = 0x3D7A7A;
    public static final int GOLD = 0xD4A84B;

    private NinjacatText() {}

    public static MutableComponent indigo(String text) {
        return Component.literal(text).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(INDIGO)));
    }

    public static MutableComponent teal(String text) {
        return Component.literal(text).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(TEAL)));
    }

    public static MutableComponent gold(String text) {
        return Component.literal(text).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(GOLD)));
    }

    // Player-facing text goes through lang keys so it can be translated; the String forms above are for
    // text that is not language (player names, numbers, ids). tools/gates/test_lang_keys.py enforces it.

    public static MutableComponent indigoKey(String key, Object... args) {
        return Component.translatable(key, args).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(INDIGO)));
    }

    public static MutableComponent tealKey(String key, Object... args) {
        return Component.translatable(key, args).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(TEAL)));
    }

    public static MutableComponent goldKey(String key, Object... args) {
        return Component.translatable(key, args).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(GOLD)));
    }
}
