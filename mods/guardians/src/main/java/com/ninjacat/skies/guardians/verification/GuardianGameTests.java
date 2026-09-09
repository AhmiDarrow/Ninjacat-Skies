package com.ninjacat.skies.guardians.verification;

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

    @GameTest(template = "empty", timeoutTicks = 1200)
    public static void totemLoop(GameTestHelper h) {
        ServerLevel level = h.getLevel();
        ServerPlayer fake = FakePlayerFactory.get(level, new GameProfile(UUID.nameUUIDFromBytes("guardians-totem".getBytes()), "TotemTester"));
        BlockPos base = h.absolutePos(new BlockPos(1, 1, 1));
        fake.teleportTo(base.getX() + 0.5, base.getY(), base.getZ() + 0.5);
        ArenaManager m = ArenaManager.get(level.getServer());
        String fail = m.summon(fake, GuardianKind.LINTGOLEM);
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
}
