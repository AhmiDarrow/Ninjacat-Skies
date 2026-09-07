package com.ninjacat.skies.core.client;

/** Client-only optional bridge, using the same entry point as FTB's own quest book. */
public final class QuestBookClient {
    public static void open() { dev.ftb.mods.ftbquests.client.FTBQuestsClient.openGui(); }
    private QuestBookClient() {}
}
