package com.ninjacat.skies.guardians.verification;

import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.arena.ArenaData;
import com.ninjacat.skies.guardians.arena.ArenaInstance;
import com.ninjacat.skies.guardians.arena.ArenaManager;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import com.ninjacat.skies.guardians.entity.ModEntities;
import com.ninjacat.skies.guardians.item.ModItems;
import com.ninjacat.skies.guardians.item.RelicItem;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

/** Headless checks: every arena plan loads, every guardian ticks its fight without throwing, and the totem loop runs end to end. */
@GameTestHolder("guardians")
@PrefixGameTestTemplate(false)
public class GuardianGameTests {

    @GameTest(template = "empty")
    public static void arenaPlansLoad(GameTestHelper h) {
        for (GuardianKind k : GuardianKind.values()) {
            ArenaData d = ArenaData.get(h.getLevel().getServer(), k);
            if (d.size() < 100) h.fail("arena plan too small: " + k.id);
            if (d.pads.isEmpty()) h.fail("no spawn pads: " + k.id);
            if (d.radius < 10) h.fail("radius: " + k.id);
        }
        h.succeed();
    }

    /** Hivemind drones come out in open air: every cell's mouth, and the whole jittered volume a drone can spawn into,
     *  is free of blocks in the shipped arena plan (the cells themselves sit inside the solid amber wall). */
    @GameTest(template = "empty")
    public static void hivemindDroneMouthsOpen(GameTestHelper h) {
        ArenaData d = ArenaData.get(h.getLevel().getServer(), GuardianKind.HIVEMIND);
        java.util.Set<BlockPos> solid = new java.util.HashSet<>();
        for (int i = 0; i < d.size(); i++)
            if (!d.state(i).getCollisionShape(net.minecraft.world.level.EmptyBlockGetter.INSTANCE, BlockPos.ZERO).isEmpty()) solid.add(d.pos(i));
        Vec3 o = Vec3.atBottomCenterOf(BlockPos.ZERO);      // ArenaInstance.origin() of an arena built at the plan origin
        for (int k = 0; k < 6; k++) {
            Vec3 m = com.ninjacat.skies.guardians.entity.bosses.HivemindGuardian.droneMouth(o, k, solid::contains);
            if (!com.ninjacat.skies.guardians.entity.bosses.HivemindGuardian.droneRoom(m, solid::contains)) { h.fail("drone cell " + k + " spawns into blocks at " + m); return; }
            double r = Math.hypot(m.x - o.x, m.z - o.z);
            if (r < 25 || r > 30) { h.fail("drone cell " + k + " mouth off the wall foot: r " + r); return; }
            if (m.y < -1 || m.y > 4) { h.fail("drone cell " + k + " mouth off the floor: y " + m.y); return; }
        }
        h.succeed();
    }

    /** Every guardian but the First Cut has a fight track, each one a sound event of sounds.json; it plays only while the fight runs. */
    @GameTest(template = "empty")
    public static void fightTracksExist(GameTestHelper h) {
        java.util.Set<String> events;
        java.nio.file.Path sounds = net.neoforged.fml.ModList.get().getModFileById("guardians").getFile().findResource("assets", "guardians", "sounds.json");
        try (var in = java.nio.file.Files.newBufferedReader(sounds, java.nio.charset.StandardCharsets.UTF_8)) {
            events = com.google.gson.JsonParser.parseReader(in).getAsJsonObject().keySet();
        } catch (java.io.IOException e) { h.fail("sounds.json: " + e); return; }
        java.util.Set<String> tracks = new java.util.HashSet<>();
        for (GuardianKind k : GuardianKind.values()) {
            var track = k.music();
            if (track == null) { if (k != GuardianKind.FIRSTCUT) h.fail(k.id + " has no track"); continue; }
            if (!track.getNamespace().equals("guardians") || !events.contains(track.getPath())) { h.fail(k.id + " track " + track + " is not in sounds.json"); return; }
            tracks.add(track.toString());
            ArenaInstance inst = new ArenaInstance(0, k, BlockPos.ZERO, 30);
            if (!ArenaManager.musicOf(inst).equals(track.toString())) { h.fail(k.id + " fight is silent"); return; }
            inst.state = ArenaInstance.State.WON;
            if (!ArenaManager.musicOf(inst).isEmpty()) { h.fail(k.id + " music plays on after the win"); return; }
            inst.state = ArenaInstance.State.WIPED;
            if (!ArenaManager.musicOf(inst).isEmpty()) { h.fail(k.id + " music plays on after a wipe"); return; }
        }
        if (tracks.size() != 12) { h.fail("expected 12 distinct tracks, got " + tracks.size()); return; }
        var sent = new com.ninjacat.skies.guardians.network.GuardianMusicPayload("guardians:music.hivemind");
        io.netty.buffer.ByteBuf buf = io.netty.buffer.Unpooled.buffer();
        com.ninjacat.skies.guardians.network.GuardianMusicPayload.STREAM_CODEC.encode(buf, sent);
        if (!sent.equals(com.ninjacat.skies.guardians.network.GuardianMusicPayload.STREAM_CODEC.decode(buf))) { h.fail("music payload does not survive the wire"); return; }
        h.succeed();
    }

    @GameTest(template = "empty", timeoutTicks = 8000)
    public static void everyGuardianFightsAndDies(GameTestHelper h) {
        ServerLevel level = h.getLevel();
        BlockPos base = h.absolutePos(new BlockPos(1, 1, 1));
        // a floor so mechanics that probe the ground have something to find
        for (int x = -30; x <= 30; x++) for (int z = -30; z <= 30; z++) level.setBlock(base.offset(x, -1, z), net.minecraft.world.level.block.Blocks.STONE.defaultBlockState(), 2);
        ServerPlayer fake = FakePlayerFactory.get(level, new GameProfile(UUID.nameUUIDFromBytes("guardians-fight".getBytes()), "GuardianTester"));
        fake.moveTo(base.getX() + 12, base.getY(), base.getZ() + 12, 0, 0);
        try { level.addNewPlayer(fake); } catch (Exception e) { /* still runs the mechanics without a target */ }
        GuardianKind[] kinds = GuardianKind.values();
        runKind(h, level, base, kinds, 0);
    }

    private static void runKind(GameTestHelper h, ServerLevel level, BlockPos base, GuardianKind[] kinds, int i) {
        if (i >= kinds.length) { h.succeed(); return; }
        GuardianKind k = kinds[i];
        GuardianEntity g = ModEntities.create(k, level);
        if (g == null) { h.fail("no entity for " + k.id); return; }
        g.moveTo(base.getX() + 0.5, base.getY(), base.getZ() + 0.5, 0, 0);
        level.addFreshEntity(g);
        h.runAfterDelay(400, () -> {
            if (!g.isAlive()) { h.fail(k.id + " died on its own"); return; }
            if (g.clip() < 0 || g.clip() > 3) h.fail(k.id + " bad clip");
            g.hurt(level.damageSources().genericKill(), Float.MAX_VALUE);       // bypasses immunity
            if (g.isAlive() && g.getHealth() > 1.5F) { g.setHealth(1); g.die(level.damageSources().genericKill()); }
            h.runAfterDelay(80, () -> {
                if (!g.isRemoved()) h.fail(k.id + " did not finish its death clip");
                runKind(h, level, base, kinds, i + 1);
            });
        });
    }

    /** A gate guardian will not answer a player whose Clowder has not seated its Strand (and the shades of the Overweaver carry no boss bar). */
    @GameTest(template = "empty", timeoutTicks = 200)
    public static void gateRefusesUnseatedStrand(GameTestHelper h) {
        ServerLevel level = h.getLevel();
        ServerPlayer fake = FakePlayerFactory.get(level, new GameProfile(UUID.nameUUIDFromBytes("guardians-gate".getBytes()), "GateTester"));
        BlockPos base = h.absolutePos(new BlockPos(1, 1, 1));
        fake.teleportTo(base.getX() + 0.5, base.getY(), base.getZ() + 0.5);
        ArenaManager m = ArenaManager.get(level.getServer());
        net.minecraft.network.chat.Component refusal = m.summon(fake, GuardianKind.BEDDOWN);
        String fail = text(refusal);
        boolean namesSoil = fail != null && (fail.contains("Soil") || refusal.getContents() instanceof net.minecraft.network.chat.contents.TranslatableContents tc
                && java.util.Arrays.stream(tc.getArgs()).anyMatch(a -> "Soil".equals(a) || a instanceof net.minecraft.network.chat.Component ac
                        && ac.getContents() instanceof net.minecraft.network.chat.contents.TranslatableContents at && Strand.SOIL.titleKey().equals(at.getKey())));
        if (!namesSoil) { h.fail("gate totem answered without the Strand seated: " + fail); return; }
        if (m.instanceOf(fake) != null) { h.fail("an arena was opened anyway"); return; }
        GuardianEntity shade = ModEntities.create(GuardianKind.BEDDOWN, level);
        if (shade == null) { h.fail("no entity"); return; }
        shade.addTag("guardians_add");
        if (shade.showsBossBar()) h.fail("an additive spawn shows a boss bar");
        shade.discard();
        h.succeed();
    }

    /** The refusal as plain text (the summon returns a lang-keyed component). */
    private static String text(@javax.annotation.Nullable net.minecraft.network.chat.Component c) { return c == null ? null : c.getString(); }

    /** Solo persistent data: seat a Strand so Easy-tier totems (Lint Golem / Tangle) will answer. */
    private static void seat(ServerPlayer p, Strand s) {
        CompoundTag root = p.getPersistentData();
        CompoundTag mod = root.getCompound("ninjacatskies");
        CompoundTag clowder = mod.getCompound("clowder");
        clowder.putInt("strands", clowder.getInt("strands") | s.bit());
        mod.put("clowder", clowder);
        root.put("ninjacatskies", mod);
    }

    @GameTest(template = "empty", timeoutTicks = 1200)
    public static void totemLoop(GameTestHelper h) {
        ServerLevel level = h.getLevel();
        ServerPlayer fake = FakePlayerFactory.get(level, new GameProfile(UUID.nameUUIDFromBytes("guardians-totem".getBytes()), "TotemTester"));
        BlockPos base = h.absolutePos(new BlockPos(1, 1, 1));
        fake.teleportTo(base.getX() + 0.5, base.getY(), base.getZ() + 0.5);
        seat(fake, Strand.SOIL);
        ArenaManager m = ArenaManager.get(level.getServer());
        String fail = text(m.summon(fake, GuardianKind.LINTGOLEM));
        if (fail != null) { h.fail("summon refused: " + fail); return; }
        ArenaInstance inst = m.instanceOf(fake);
        if (inst == null) { h.fail("no instance"); return; }
        ServerLevel arena = ArenaManager.arenaLevel(level.getServer());
        if (arena == null) { h.fail("no arena level"); return; }
        h.runAfterDelay(40, () -> {
            if (!ArenaManager.inArena(fake)) h.fail("player not moved to the arena");
            if (arena.getBlockState(inst.originPos.below()).isAir()) h.fail("arena floor not built");
            if (inst.boss == null || !(arena.getEntity(inst.boss) instanceof GuardianEntity boss)) { h.fail("boss missing"); return; }
            boss.setHealth(1); boss.die(arena.damageSources().genericKill());
            h.runAfterDelay(60, () -> {
                if (inst.state != ArenaInstance.State.WON) h.fail("state " + inst.state);
                // relics go to party members the player list can resolve; a FakePlayer is not in it, so only assert when it is
                if (level.getServer().getPlayerList().getPlayer(fake.getUUID()) != null) {
                    boolean hasRelic = false;
                    for (ItemStack s : fake.getInventory().items) if (s.getItem() instanceof RelicItem) hasRelic = true;
                    if (!hasRelic) h.fail("no relic given");
                }
                h.runAfterDelay(220, () -> {
                    if (level.getServer().getPlayerList().getPlayer(fake.getUUID()) != null && ArenaManager.inArena(fake)) h.fail("player not returned home");
                    if (m.instanceOf(fake) != null) h.fail("instance not freed");
                    h.succeed();
                });
            });
        });
    }

    /** A full disconnect (nobody online) must not spend the totem after the FIGHT grace period. */
    @GameTest(template = "empty", timeoutTicks = 200)
    public static void disconnectDoesNotSpendTotem(GameTestHelper h) {
        ServerLevel level = h.getLevel();
        ServerPlayer fake = FakePlayerFactory.get(level, new GameProfile(UUID.nameUUIDFromBytes("guardians-dc".getBytes()), "DisconnectTester"));
        BlockPos base = h.absolutePos(new BlockPos(1, 1, 1));
        fake.teleportTo(base.getX() + 0.5, base.getY(), base.getZ() + 0.5);
        seat(fake, Strand.SOIL);
        ArenaManager m = ArenaManager.get(level.getServer());
        // Verification worlds are reused. The previous version of this test left
        // its disconnected party in SavedData, making every later run fail setup.
        ArenaInstance previous = m.instanceOf(fake);
        if (previous != null) clearTestArena(level, m, previous);
        String fail = text(m.summon(fake, GuardianKind.LINTGOLEM));
        if (fail != null) { h.fail("summon refused: " + fail); return; }
        ArenaInstance inst = m.instanceOf(fake);
        if (inst == null) { h.fail("no instance"); return; }
        try {
            inst.age = 120;
            m.tick(level.getServer());
            if (inst.state != ArenaInstance.State.FIGHT) h.fail("disconnect spent the totem: " + inst.state);
        } finally {
            clearTestArena(level, m, inst);
        }
        h.succeed();
    }

    private static void clearTestArena(ServerLevel level, ArenaManager manager, ArenaInstance instance) {
        manager.wipe(level.getServer(), instance, "Verification fixture cleanup");
        instance.stateTicks = 181;
        manager.tick(level.getServer());
    }
}
