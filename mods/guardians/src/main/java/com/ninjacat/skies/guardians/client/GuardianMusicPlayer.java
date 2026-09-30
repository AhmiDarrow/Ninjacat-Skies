package com.ninjacat.skies.guardians.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.core.Holder;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.Music;
import net.minecraft.sounds.SoundEvent;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.SelectMusicEvent;

import java.util.HashMap;
import java.util.Map;

/**
 * Client only. While the server says this player stands in a running fight ({@link ClientGuardianMusic}), the music
 * manager plays that guardian's track in place of the situational music, on a loop and at once, as vanilla does for
 * the Ender Dragon. When the fight ends for the player (win, wipe, leave) the track is cut, not left to play out.
 */
public final class GuardianMusicPlayer {
    private final Map<String, Music> tracks = new HashMap<>();
    /** The track this listener last put on ("" none). */
    private String playing = "";

    /** Lowest priority: the latest music set wins, so the fight track is chosen after any biome or dimension music. */
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onSelectMusic(SelectMusicEvent event) {
        String want = ClientGuardianMusic.track();
        Music music = want.isEmpty() ? null : tracks.computeIfAbsent(want, GuardianMusicPlayer::music);
        if (music != null) {
            playing = want;
            event.overrideMusic(music);
            return;
        }
        if (playing.isEmpty()) return;
        SoundInstance current = event.getPlayingMusic();
        if (current != null && current.getLocation().toString().equals(playing)) Minecraft.getInstance().getMusicManager().stopPlaying();
        playing = "";
    }

    @SubscribeEvent
    public void onLogout(ClientPlayerNetworkEvent.LoggingOut event) {
        ClientGuardianMusic.reset();
    }

    /** A looping fight track: no gap between plays, and it replaces whatever is playing. */
    private static Music music(String track) {
        ResourceLocation id = ResourceLocation.tryParse(track);
        return id == null ? null : new Music(Holder.direct(SoundEvent.createVariableRangeEvent(id)), 0, 0, true);
    }
}
