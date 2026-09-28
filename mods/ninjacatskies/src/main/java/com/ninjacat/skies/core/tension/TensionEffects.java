package com.ninjacat.skies.core.tension;

import com.ninjacat.skies.core.NinjacatSkies;
import com.ninjacat.skies.core.config.SkiesConfig;
import com.ninjacat.skies.core.network.FraySyncPayload;
import com.ninjacat.skies.core.sound.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.GlobalPos;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.Level;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.server.ServerLifecycleHooks;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * Everything the Loom does to the world once Strands are seated:
 * thread helixes at ceremony, the Reweave finale, the Fray over the Dock (drawn on every client), and the Post's aura.
 */
public final class TensionEffects {
    private static final List<Scripted> SCRIPTS = new ArrayList<>();
    /** Frames scheduled while SCRIPTS is being iterated (the finale spawns helixes). */
    private static final List<Scripted> PENDING = new ArrayList<>();
    private static final DustParticleOptions FRAY_LIT = new DustParticleOptions(new Vector3f(0.83F, 0.66F, 0.29F), 1.0F);

    /** Aura radius around a Clowder's Tension Post, in blocks. */
    private static final double AURA_RADIUS = 24.0;
    /** Edge-walker footing: no fall damage this close to the Post once Claw is seated. */
    private static final double FOOTING_RADIUS = 48.0;

    public TensionEffects() {}

    // ---------------------------------------------------------------- scripted particle runs

    @FunctionalInterface
    private interface Frame {
        void run(int tick);
    }

    private static final class Scripted {
        final int length;
        final Frame frame;
        int tick;

        Scripted(int length, Frame frame) {
            this.length = length;
            this.frame = frame;
        }
    }

    private static void schedule(int length, Frame frame) {
        PENDING.add(new Scripted(length, frame));
    }

    /** A rising helix of Strand-colored dust from the Post. */
    public static void helix(ServerLevel level, BlockPos pos, int color, int length) {
        DustParticleOptions dust = new DustParticleOptions(rgb(color), 1.1F);
        double cx = pos.getX() + 0.5;
        double cz = pos.getZ() + 0.5;
        double baseY = pos.getY();
        schedule(length, tick -> {
            double t = tick / (double) length;
            double angle = tick * 0.55;
            double radius = 0.9 - 0.5 * t;
            double y = baseY + 0.2 + t * 3.2;
            for (int arm = 0; arm < 2; arm++) {
                double a = angle + arm * Math.PI;
                level.sendParticles(dust, cx + Math.cos(a) * radius, y, cz + Math.sin(a) * radius, 1, 0, 0.01, 0, 0);
            }
            if (tick % 6 == 0) {
                level.sendParticles(ParticleTypes.END_ROD, cx, y + 0.2, cz, 1, 0.05, 0.05, 0.05, 0.0);
            }
        });
    }

    /** The Reweave: nine chimes in sequence, a ring across the pad, thread rising, fireworks. */
    public static void finale(ServerLevel level, BlockPos pos) {
        double cx = pos.getX() + 0.5;
        double cy = pos.getY() + 1.0;
        double cz = pos.getZ() + 0.5;
        level.playSound(null, pos, ModSounds.REWEAVE.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        schedule(200, tick -> {
            // Chimes: one Strand every 12 ticks, in canon order.
            if (tick % 12 == 0 && tick / 12 < Strand.ALL.length) {
                Strand s = Strand.ALL[tick / 12];
                level.playSound(null, pos, ModSounds.STRAND_CHIME.get(), SoundSource.BLOCKS, 1.0F, s.chimePitch());
                helix(level, pos, s.color(), 40);
            }
            // Expanding ring at pad level.
            double r = 1.0 + tick * 0.18;
            int points = (int) Math.min(64, 12 + r * 2);
            for (int i = 0; i < points; i++) {
                double a = (Math.PI * 2 * i) / points + tick * 0.02;
                level.sendParticles(FRAY_LIT, cx + Math.cos(a) * r, cy - 0.6, cz + Math.sin(a) * r, 1, 0, 0.02, 0, 0);
            }
            // A lit thread straight up.
            if (tick % 2 == 0) {
                level.sendParticles(ParticleTypes.END_ROD, cx, cy + (tick % 40) * 0.6, cz, 1, 0.02, 0, 0.02, 0.0);
            }
            // Fireworks in Loom colors.
            if (tick >= 30 && tick % 25 == 0) {
                launchFirework(level, cx + (level.random.nextDouble() - 0.5) * 6, cy, cz + (level.random.nextDouble() - 0.5) * 6);
            }
        });
    }

    private static void launchFirework(ServerLevel level, double x, double y, double z) {
        // Particles only: a vanilla LARGE_BALL rocket deals blast damage and can spend Clowder lives.
        level.sendParticles(ParticleTypes.FIREWORK, x, y + 2.5, z, 25, 0.4, 1.2, 0.4, 0.08);
        level.sendParticles(FRAY_LIT, x, y + 2.0, z, 12, 0.3, 0.8, 0.3, 0.02);
    }

    private static Vector3f rgb(int color) {
        return new Vector3f(((color >> 16) & 0xFF) / 255.0F, ((color >> 8) & 0xFF) / 255.0F, (color & 0xFF) / 255.0F);
    }

    // ---------------------------------------------------------------- server tick: scripts + the Fray

    @SubscribeEvent
    public void onServerTick(ServerTickEvent.Post event) {
        MinecraftServer server = event.getServer();
        if (!PENDING.isEmpty()) {
            SCRIPTS.addAll(PENDING);
            PENDING.clear();
        }
        Iterator<Scripted> it = SCRIPTS.iterator();
        while (it.hasNext()) {
            Scripted s = it.next();
            try {
                s.frame.run(s.tick);
            } catch (Exception e) {
                NinjacatSkies.LOGGER.warn("Tension effect failed", e);
                it.remove();
                continue;
            }
            if (++s.tick >= s.length) {
                it.remove();
            }
        }

        if (server.getTickCount() % 40 == 0) {
            broadcastFray(server);
        }
    }

    // ---------------------------------------------------------------- the Fray

    /** An operator's preview (`/skybound fray <closed>`), or -1 for the server's true reweave. */
    private static float frayOverride = -1F;
    private static float lastFray = -1F;
    private static boolean frayDirty;

    /**
     * How far the whole server has rewoven, 0 open .. 1 closed: the state of the cut over the Dock. Every client
     * draws the Fray from this, so it thins as any Clowder seats a Strand and turns to lit thread only once every
     * Clowder online has rewoven.
     */
    public static float frayProgress(MinecraftServer server) {
        return frayOverride >= 0F ? frayOverride : LoomTension.serverProgress(server);
    }

    public static float frayOverride() {
        return frayOverride;
    }

    /** Operators can hold the Fray at a value to see it; -1 lets it follow the server again. */
    public static void setFrayOverride(float closed) {
        frayOverride = closed < 0F ? -1F : Math.clamp(closed, 0F, 1F);
        frayDirty = true;
    }

    private static FraySyncPayload frayPayload(MinecraftServer server) {
        return new FraySyncPayload(SkiesConfig.FRAY_ENABLED.get(), SkiesConfig.FRAY_DIMENSION.get(),
                SkiesConfig.FRAY_X.get(), SkiesConfig.FRAY_Y.get(), SkiesConfig.FRAY_Z.get(), frayProgress(server));
    }

    /** Every two seconds: if the cut changed (a seat, a Reweave, a Clowder coming or going), tell every client. */
    private static void broadcastFray(MinecraftServer server) {
        float progress = frayProgress(server);
        if (!frayDirty && Math.abs(progress - lastFray) < 0.0005F) {
            return;
        }
        lastFray = progress;
        frayDirty = false;
        FraySyncPayload payload = frayPayload(server);
        for (ServerPlayer player : server.getPlayerList().getPlayers()) {
            sendFray(player, payload);
        }
    }

    private static void sendFray(ServerPlayer player, FraySyncPayload payload) {
        // A connection that never negotiated the channel (a GameTest mock player) cannot take it: sending would throw.
        if (!player.connection.hasChannel(FraySyncPayload.TYPE)) return;
        PacketDistributor.sendToPlayer(player, payload);
    }

    // ---------------------------------------------------------------- player: aura, footing, sync

    @SubscribeEvent
    public void onPlayerTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || player.tickCount % 100 != 0) {
            return;
        }
        LoomTension.clowderOf(player).ifPresent(c -> {
            GlobalPos post = LoomTension.postOf(c);
            if (post == null || !post.dimension().equals(player.level().dimension())) {
                return;
            }
            BlockPos pos = post.pos();
            // Distance first: reading the Post's block would load its chunk from anywhere in the dimension.
            if (player.distanceToSqr(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5) > AURA_RADIUS * AURA_RADIUS
                    || !player.level().isLoaded(pos)
                    || !player.level().getBlockState(pos).is(com.ninjacat.skies.core.block.ModBlocks.TENSION_POST.get())) {
                return;
            }
            int bits = LoomTension.strandBits(c);
            int seated = Integer.bitCount(bits);
            // Pad-keepers' hearth: the pad mends you.
            if (seated >= 1) {
                player.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 120, 0, true, false, true));
            }
            // Rootbinders: the pad feeds you a little.
            if ((bits & Strand.SPROUT.bit()) != 0 && player.getFoodData().getFoodLevel() < 18) {
                player.getFoodData().eat(1, 0.4F);
            }
            // Pattern-weavers / Drumhearts: hands move to the beat.
            if (seated >= 5) {
                player.addEffect(new MobEffectInstance(MobEffects.DIG_SPEED, 120, 0, true, false, true));
            }
            // Seal-carvers: the world is a little kinder with what it drops.
            if ((bits & Strand.SIGIL.bit()) != 0) {
                player.addEffect(new MobEffectInstance(MobEffects.LUCK, 120, 0, true, false, true));
            }
            if (LoomTension.isRewoven(c)) {
                player.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 120, 0, true, false, true));
            }
        });
    }

    @SubscribeEvent
    public void onFall(LivingIncomingDamageEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || !event.getSource().is(DamageTypes.FALL)) {
            return;
        }
        LoomTension.clowderOf(player).ifPresent(c -> {
            if ((LoomTension.strandBits(c) & Strand.CLAW.bit()) == 0) {
                return;
            }
            GlobalPos post = LoomTension.postOf(c);
            if (post == null || !post.dimension().equals(player.level().dimension())) {
                return;
            }
            BlockPos pos = post.pos();
            if (player.distanceToSqr(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5) <= FOOTING_RADIUS * FOOTING_RADIUS
                    && player.level().isLoaded(pos)
                    && player.level().getBlockState(pos).is(com.ninjacat.skies.core.block.ModBlocks.TENSION_POST.get())) {
                event.setCanceled(true);
                player.displayClientMessage(com.ninjacat.skies.lib.NinjacatText.tealKey("message.ninjacatskies.tension.edge_footing"), true);
            }
        });
    }

    @SubscribeEvent
    public void onLogin(PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            LoomTension.onClowderChanged(player);   // also grants advancements earned while offline
            // The newcomer sees the cut at once; everyone else follows on the next broadcast, since a Clowder
            // coming online can change the server's count.
            sendFray(player, frayPayload(player.server));
            frayDirty = true;
        }
    }

    @SubscribeEvent
    public void onServerStopping(net.neoforged.neoforge.event.server.ServerStoppingEvent event) {
        SCRIPTS.clear();
        PENDING.clear();
        frayOverride = -1F;
        lastFray = -1F;
    }

    @SubscribeEvent
    public void onChangeDimension(PlayerEvent.PlayerChangedDimensionEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            LoomTension.sync(player);
        }
    }

    /** For scripts and commands: the overworld is the Loom's home level. */
    public static Level home() {
        return ServerLifecycleHooks.getCurrentServer().overworld();
    }
}
