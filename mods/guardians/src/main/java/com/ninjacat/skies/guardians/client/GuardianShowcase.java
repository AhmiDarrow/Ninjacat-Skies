package com.ninjacat.skies.guardians.client;

import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.neoforged.neoforge.client.event.RenderGuiEvent;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Headless play-test hook ({@code -Dguardians.showcase=true}): a driver that owns the server through RCON (see
 * {@code tools/guardians_showcase.py}) writes one command to {@code <gameDir>/showcase-command.txt}; the client polls it
 * twice a second on the render thread, executes it, and replaces it with {@code showcase-done.txt} holding the result.
 * <ul>
 *   <li>{@code shot <label>} — capture {@code showcase-<n>-<label>.png} of the current frame.</li>
 *   <li>{@code look <yaw> <pitch>} — turn the local player's head.</li>
 *   <li>{@code hud <on|off>} — hide or show the HUD (clean model shots).</li>
 *   <li>{@code attack} — swing at whatever the crosshair is on.</li>
 *   <li>{@code fov <n>} — set the field of view.</li>
 *   <li>{@code close} — close any open screen.</li>
 * </ul>
 * Nothing here runs unless the property is set; it is a development aid, not a feature.
 */
public final class GuardianShowcase {
    private static final boolean ENABLED = Boolean.getBoolean("guardians.showcase");
    private static final long POLL_MS = 500;
    private static long nextPoll;
    private static int captures;

    private GuardianShowcase() {}

    public static boolean enabled() { return ENABLED; }

    public static void onGui(RenderGuiEvent.Post event) {
        if (!ENABLED) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.player == null) return;
        long now = System.currentTimeMillis();
        if (now < nextPoll) return;
        nextPoll = now + POLL_MS;
        Path command = mc.gameDirectory.toPath().resolve("showcase-command.txt");
        if (!Files.isRegularFile(command)) return;
        String line;
        try { line = Files.readString(command).strip(); Files.deleteIfExists(command); } catch (IOException e) { return; }
        if (line.isEmpty()) return;
        String result;
        try { result = execute(mc, line); } catch (RuntimeException e) { result = "error " + e; }
        try { Files.writeString(mc.gameDirectory.toPath().resolve("showcase-done.txt"), line + "\n" + result + "\n"); } catch (IOException ignored) {}
    }

    private static String execute(Minecraft mc, String line) {
        String[] p = line.split("\\s+");
        switch (p[0]) {
            case "shot" -> {
                String label = p.length > 1 ? p[1].replaceAll("[^A-Za-z0-9_-]", "_") : "shot";
                String name = "showcase-" + (++captures) + "-" + label + ".png";
                Screenshot.grab(mc.gameDirectory, name, mc.getMainRenderTarget(), m -> {});
                return "ok " + name;
            }
            case "look" -> {
                if (p.length < 3) return "error look <yaw> <pitch>";
                float yaw = Float.parseFloat(p[1]), pitch = Float.parseFloat(p[2]);
                mc.player.setYRot(yaw); mc.player.setYHeadRot(yaw); mc.player.yRotO = yaw; mc.player.setXRot(pitch); mc.player.xRotO = pitch;
                return "ok " + yaw + " " + pitch;
            }
            case "hud" -> { mc.options.hideGui = p.length > 1 && p[1].equals("off"); return "ok hud " + !mc.options.hideGui; }
            case "attack" -> { if (mc.gameMode != null && mc.hitResult instanceof net.minecraft.world.phys.EntityHitResult ehr) { mc.gameMode.attack(mc.player, ehr.getEntity()); mc.player.swing(net.minecraft.world.InteractionHand.MAIN_HAND); return "ok hit " + ehr.getEntity().getId(); } return "ok nothing"; }
            case "fov" -> { mc.options.fov().set(Integer.parseInt(p[1])); return "ok fov " + p[1]; }
            case "close" -> { mc.setScreen(null); return "ok closed"; }
            default -> { return "error unknown " + p[0]; }
        }
    }
}
