package com.ninjacat.skies.driftwrecks.wreck;

import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;

import javax.annotation.Nullable;

/**
 * The layout of a wreck. Each core has one plan per tier (data/driftwrecks/wreck/&lt;core&gt;_&lt;tier&gt;.ncga).
 * Names and the Codex hint line live in the lang file under wreck.driftwrecks.core.&lt;id&gt;.
 */
public enum WreckCore {
    SHRINE("shrine"),
    WATCHTOWER("watchtower"),
    LIBRARY("library"),
    FORGE("forge"),
    GARDEN("garden"),
    VAULT("vault");

    public static final WreckCore[] ALL = values();

    public final String id;

    WreckCore(String id) { this.id = id; }

    public int bit() { return 1 << ordinal(); }

    public String key(String part) { return "wreck.driftwrecks.core." + id + "." + part; }

    /** The core's name ("Forge"). */
    public MutableComponent title() { return Component.translatable(key("title")); }

    /** The name as it reads mid-sentence ("forge"). */
    public MutableComponent titleInline() { return Component.translatable(key("title_inline")); }

    /** The Codex hint page line; points at the hidden room without naming it. */
    public String hintKey() { return key("hint"); }

    public MutableComponent hint() { return Component.translatable(hintKey()); }

    @Nullable
    public static WreckCore byId(String id) {
        for (WreckCore c : ALL) if (c.id.equals(id)) return c;
        return null;
    }
}
