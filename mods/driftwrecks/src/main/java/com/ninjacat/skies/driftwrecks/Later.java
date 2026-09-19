package com.ninjacat.skies.driftwrecks;

import net.minecraft.server.MinecraftServer;

import java.util.ArrayList;
import java.util.List;

/**
 * Work that runs a number of ticks from now: the "watch the order" cues (idol pillars, Remnant tiles and wards).
 * {@code server.tell(new TickTask(tick + delay, ...))} is not a delay: a server with time to spare runs it at once,
 * so every cue fired together. Ticked from {@link DriftEvents}; nothing survives a server stop.
 */
public final class Later {
    private record Task(long due, Runnable run) {}
    private static final List<Task> TASKS = new ArrayList<>();

    private Later() {}

    public static void run(MinecraftServer server, int delayTicks, Runnable task) {
        if (delayTicks <= 0) { task.run(); return; }
        TASKS.add(new Task(server.getTickCount() + (long) delayTicks, task));
    }

    static void tick(MinecraftServer server) {
        if (TASKS.isEmpty()) return;
        long now = server.getTickCount();
        List<Task> due = new ArrayList<>();
        TASKS.removeIf(t -> { if (t.due() > now) return false; due.add(t); return true; });
        for (Task t : due) {
            try { t.run().run(); } catch (Exception e) { Driftwrecks.LOGGER.error("Delayed driftwreck task failed", e); }
        }
    }

    static void clear() { TASKS.clear(); }
}
