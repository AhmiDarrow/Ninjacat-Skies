package com.ninjacat.skies.core.tension;

import com.ninjacat.skies.core.NinjacatSkies;
import com.ninjacat.skies.core.item.ModItems;
import com.ninjacat.skies.core.network.TensionSyncPayload;
import com.ninjacat.skies.core.sound.ModSounds;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.advancements.AdvancementHolder;
import net.minecraft.core.BlockPos;
import net.minecraft.core.GlobalPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.fml.ModList;
import net.neoforged.neoforge.network.PacketDistributor;

import javax.annotation.Nullable;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Loom Tension: how much of the cut a Clowder has rewoven. One bit per seated Strand, a flag for the Fragment.
 * Team-scoped through FTB Teams when present; otherwise per player. All ceremony fires from here.
 */
public final class LoomTension {
    public static final String KEY_STRANDS = "strands";
    public static final String KEY_REWOVEN = "rewoven";
    public static final String KEY_POST = "post";
    public static final String KEY_PAGES = "pages";
    public static final String KEY_REWARDS = "rewards";
    private static final String PLAYER_ROOT = NinjacatSkies.MOD_ID;
    private static final String PLAYER_KEY = "clowder";

    private static final boolean FTB_TEAMS = ModList.get().isLoaded("ftbteams");

    /** Codex Page every third unique Strand — the tribes' margin notes. */
    private static final int PAGE_EVERY = 3;

    private LoomTension() {}

    // ---------------------------------------------------------------- lookup

    public static Optional<Clowder> clowderOf(ServerPlayer player) {
        if (FTB_TEAMS) {
            Optional<Clowder> team = FtbTeamsBridge.forPlayer(player);
            if (team.isPresent()) {
                return team;
            }
        }
        return Optional.of(new SoloClowder(player));
    }

    public static Optional<Clowder> clowderById(MinecraftServer server, UUID id) {
        if (FTB_TEAMS) {
            Optional<Clowder> team = FtbTeamsBridge.byId(id);
            if (team.isPresent()) {
                return team;
            }
        }
        ServerPlayer player = server.getPlayerList().getPlayer(id);
        return player == null ? Optional.empty() : Optional.of(new SoloClowder(player));
    }

    public static List<Clowder> allClowders(MinecraftServer server) {
        if (FTB_TEAMS) {
            List<Clowder> teams = FtbTeamsBridge.all(server);
            if (!teams.isEmpty()) {
                return teams;
            }
        }
        return server.getPlayerList().getPlayers().stream().map(p -> (Clowder) new SoloClowder(p)).toList();
    }

    // ---------------------------------------------------------------- state

    public static int strandBits(Clowder c) {
        return c.data().getInt(KEY_STRANDS);
    }

    public static int strandBits(ServerPlayer player) {
        return clowderOf(player).map(LoomTension::strandBits).orElse(0);
    }

    public static boolean isSeated(Clowder c, Strand s) {
        return (strandBits(c) & s.bit()) != 0;
    }

    public static int tension(Clowder c) {
        return Integer.bitCount(strandBits(c)) + (isRewoven(c) ? 1 : 0);
    }

    public static int tension(ServerPlayer player) {
        return clowderOf(player).map(LoomTension::tension).orElse(0);
    }

    public static boolean isRewoven(Clowder c) {
        return c.data().getBoolean(KEY_REWOVEN);
    }

    public static int braidCount(Clowder c) {
        int bits = strandBits(c);
        int n = 0;
        for (Strand s : Strand.BRAID) {
            if ((bits & s.bit()) != 0) {
                n++;
            }
        }
        return n;
    }

    public static boolean allSeated(Clowder c) {
        return Integer.bitCount(strandBits(c)) == Strand.ALL.length;
    }

    @Nullable
    public static GlobalPos postOf(Clowder c) {
        CompoundTag data = c.data();
        if (!data.contains(KEY_POST)) {
            return null;
        }
        return GlobalPos.CODEC.parse(NbtOps.INSTANCE, data.get(KEY_POST)).result().orElse(null);
    }

    public static void rememberPost(Clowder c, ServerLevel level, BlockPos pos) {
        Tag tag = GlobalPos.CODEC.encodeStart(NbtOps.INSTANCE, GlobalPos.of(level.dimension(), pos)).result().orElse(null);
        if (tag != null) {
            c.data().put(KEY_POST, tag);
            c.markDirty();
        }
    }

    /** Fraction of every Clowder's Strands that are seated, 0..1 — the server-wide state of the cut. */
    public static float serverProgress(MinecraftServer server) {
        List<Clowder> all = allClowders(server);
        if (all.isEmpty()) {
            return 0.0F;
        }
        int seated = 0;
        int possible = 0;
        for (Clowder c : all) {
            seated += Integer.bitCount(strandBits(c));
            possible += Strand.ALL.length;
        }
        return possible == 0 ? 0.0F : (float) seated / possible;
    }

    // ---------------------------------------------------------------- ceremony

    /**
     * Seat a Strand token at a Tension Post. Returns false if that Strand is already tensioned.
     * Fires the chime, the thread helix, the steward lines, advancements, and milestone rewards.
     */
    public static boolean seat(ServerLevel level, BlockPos pos, ServerPlayer player, Strand strand) {
        Optional<Clowder> maybe = clowderOf(player);
        if (maybe.isEmpty()) {
            return false;
        }
        Clowder c = maybe.get();
        int bits = strandBits(c);
        if ((bits & strand.bit()) != 0) {
            return false;
        }
        bits |= strand.bit();
        CompoundTag data = c.data();
        data.putInt(KEY_STRANDS, bits);
        rememberPost(c, level, pos);
        c.markDirty();

        int seated = Integer.bitCount(bits);
        int remaining = Strand.ALL.length - seated;

        // The whole Clowder hears it.
        Collection<ServerPlayer> members = c.onlineMembers();
        for (ServerPlayer member : members) {
            member.level().playSound(null, member.blockPosition(), ModSounds.STRAND_CHIME.get(), SoundSource.PLAYERS, 0.9F, strand.chimePitch());
            member.sendSystemMessage(NinjacatText.teal(strand.lineA()));
            member.sendSystemMessage(NinjacatText.gold(strand.lineB()));
            member.displayClientMessage(NinjacatText.gold(
                    remaining == 0
                            ? "Every Strand answers. The Spindle waits for a March stone."
                            : strand.title() + " is tensioned. " + remaining + (remaining == 1 ? " Strand remains." : " Strands remain.")
            ), true);
            awardAdvancement(member, strand.advancementId());
            sync(member, c);
        }
        level.playSound(null, pos, ModSounds.POST_SEAT.get(), SoundSource.BLOCKS, 1.0F, 1.0F);
        TensionEffects.helix(level, pos, strand.color(), 60);

        // Margin notes and small returns — to the one who seated it.
        int pages = data.getInt(KEY_PAGES) + 1;
        data.putInt(KEY_PAGES, pages);
        if (seated % PAGE_EVERY == 0) {
            ItemStack page = new ItemStack(ModItems.CODEX_PAGE.get());
            page.set(net.minecraft.core.component.DataComponents.CUSTOM_NAME,
                    Component.literal("Codex Page — " + strand.tribe()).withStyle(s -> s.withItalic(false).withColor(strand.color())));
            giveOrDrop(player, page);
            player.sendSystemMessage(NinjacatText.teal("A Codex Page slips free — a " + strand.tribe() + " margin note."));
        }
        milestone(c, player, seated);
        c.markDirty();
        NinjacatSkies.LOGGER.info("{} seated Strand {} ({} of {})", player.getGameProfile().getName(), strand.id(), seated, Strand.ALL.length);
        return true;
    }

    private static void milestone(Clowder c, ServerPlayer player, int seated) {
        CompoundTag rewards = c.data().getCompound(KEY_REWARDS);
        boolean gave = false;
        if (seated >= 3 && !rewards.getBoolean("r3")) {
            rewards.putBoolean("r3", true);
            giveOrDrop(player, new ItemStack(ModItems.FRAYED_THREAD.get(), 6));
            player.displayClientMessage(NinjacatText.gold("The Loom returns a little Thread. Root is holding."), false);
            gave = true;
        }
        if (seated >= 5 && !rewards.getBoolean("r5")) {
            rewards.putBoolean("r5", true);
            giveOrDrop(player, new ItemStack(ModItems.CODEX_PAGE.get(), 2));
            player.displayClientMessage(NinjacatText.gold("Two pages the stewards never finished. Read them anyway."), false);
            gave = true;
        }
        if (seated >= 7 && !rewards.getBoolean("r7")) {
            rewards.putBoolean("r7", true);
            giveOrDrop(player, new ItemStack(ModItems.FRAYED_THREAD.get(), 12));
            player.displayClientMessage(NinjacatText.gold("Bind is close. The post hums loud enough to feel in your teeth."), false);
            gave = true;
        }
        if (gave) {
            c.data().put(KEY_REWARDS, rewards);
        }
    }

    /** Braid Cord: any two of Clock / Swarm / Spark seated. Items are handled by the caller. */
    public static boolean canBraid(ServerPlayer player) {
        return clowderOf(player).map(c -> braidCount(c) >= 2).orElse(false);
    }

    /** Spindle Loom Fragment: all nine seated. Items are handled by the caller. */
    public static boolean canSpinFragment(ServerPlayer player) {
        return clowderOf(player).map(LoomTension::allSeated).orElse(false);
    }

    /** Seat the Fragment: the cut is closed for this Clowder. Server-wide finale. */
    public static boolean reweave(ServerLevel level, BlockPos pos, ServerPlayer player) {
        Optional<Clowder> maybe = clowderOf(player);
        if (maybe.isEmpty()) {
            return false;
        }
        Clowder c = maybe.get();
        if (!allSeated(c) || isRewoven(c)) {
            return false;
        }
        c.data().putBoolean(KEY_REWOVEN, true);
        rememberPost(c, level, pos);
        c.markDirty();

        MinecraftServer server = level.getServer();
        Component name = c.name();
        server.getPlayerList().broadcastSystemMessage(
                NinjacatText.gold("The Loom-stitchers' cut is closed. ").append(name.copy().withStyle(s -> s.withColor(NinjacatText.TEAL)))
                        .append(NinjacatText.gold(" has rewoven their Strand of the sky.")),
                false
        );
        for (ServerPlayer member : c.onlineMembers()) {
            awardAdvancement(member, ResourceLocation.fromNamespaceAndPath(NinjacatSkies.MOD_ID, "reweave"));
            member.sendSystemMessage(NinjacatText.teal("Nine tribes, one thread. Go and see what the March kept for you."));
            sync(member, c);
        }
        TensionEffects.finale(level, pos);
        return true;
    }

    // ---------------------------------------------------------------- helpers

    public static void sync(ServerPlayer player) {
        clowderOf(player).ifPresent(c -> sync(player, c));
    }

    public static void sync(ServerPlayer player, Clowder c) {
        PacketDistributor.sendToPlayer(player, new TensionSyncPayload(strandBits(c), isRewoven(c)));
    }

    private static void awardAdvancement(ServerPlayer player, ResourceLocation id) {
        AdvancementHolder holder = player.server.getAdvancements().get(id);
        if (holder == null) {
            return;
        }
        var progress = player.getAdvancements().getOrStartProgress(holder);
        if (!progress.isDone()) {
            for (String criterion : progress.getRemainingCriteria()) {
                player.getAdvancements().award(holder, criterion);
            }
        }
    }

    public static void giveOrDrop(ServerPlayer player, ItemStack stack) {
        if (!player.addItem(stack)) {
            player.drop(stack, false);
        }
    }

    @Nullable
    public static Item itemOrNull(String id) {
        Item item = BuiltInRegistries.ITEM.getOptional(ResourceLocation.parse(id)).orElse(null);
        return item == Items.AIR ? null : item;
    }

    /** Solo fallback: one player is their own Clowder. Data lives in persistent player NBT. */
    private record SoloClowder(ServerPlayer player) implements Clowder {
        @Override
        public UUID id() {
            return player.getUUID();
        }

        @Override
        public Component name() {
            return player.getDisplayName();
        }

        @Override
        public CompoundTag data() {
            CompoundTag root = player.getPersistentData();
            if (!root.contains(PLAYER_ROOT)) {
                root.put(PLAYER_ROOT, new CompoundTag());
            }
            CompoundTag mod = root.getCompound(PLAYER_ROOT);
            if (!mod.contains(PLAYER_KEY)) {
                mod.put(PLAYER_KEY, new CompoundTag());
            }
            return mod.getCompound(PLAYER_KEY);
        }

        @Override
        public void markDirty() {
            // Persistent data is written with the player.
        }

        @Override
        public Collection<ServerPlayer> onlineMembers() {
            return List.of(player);
        }
    }
}
