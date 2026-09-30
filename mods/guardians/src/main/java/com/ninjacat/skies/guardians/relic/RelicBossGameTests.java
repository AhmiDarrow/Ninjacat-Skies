package com.ninjacat.skies.guardians.relic;

import com.ninjacat.skies.guardians.GuardianKind;
import com.ninjacat.skies.guardians.entity.GuardianEntity;
import com.ninjacat.skies.guardians.entity.ModEntities;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.animal.Bee;
import net.neoforged.neoforge.common.Tags;
import net.neoforged.neoforge.gametest.GameTestHolder;
import net.neoforged.neoforge.gametest.PrefixGameTestTemplate;

/** Relics never switch a boss fight off: fight bees stay hostile to Hivecall and Shuttle wearers, and Drumpulse stuns no boss. */
@GameTestHolder("guardians")
@PrefixGameTestTemplate(false)
public class RelicBossGameTests {
    @GameTest(template = "empty")
    public static void fightBeesIgnoreBeeRelics(GameTestHelper h) {
        ServerLevel level = h.getLevel();
        Bee drone = EntityType.BEE.create(level), wild = EntityType.BEE.create(level), summon = EntityType.BEE.create(level);
        if (drone == null || wild == null || summon == null) { h.fail("no bee"); return; }   // lang-exempt: GameTest assertion message
        drone.addTag(GuardianEntity.MINION_TAG_PREFIX + java.util.UUID.randomUUID());
        summon.addTag(RelicUtil.BEE_TAG);
        h.assertTrue(RelicUtil.fightBee(drone), "a guardian drone is a fight bee");   // lang-exempt: GameTest assertion message
        h.assertFalse(RelicUtil.fightBee(wild), "a wild bee outside the arenas is not");   // lang-exempt: GameTest assertion message
        h.assertFalse(RelicUtil.fightBee(summon), "a relic summon is not");   // lang-exempt: GameTest assertion message
        h.succeed();
    }

    @GameTest(template = "empty")
    public static void drumpulseSparesBosses(GameTestHelper h) {
        ServerLevel level = h.getLevel();
        for (GuardianKind k : GuardianKind.values()) {
            GuardianEntity g = ModEntities.create(k, level);
            if (g == null) { h.fail("no entity for " + k.id); return; }   // lang-exempt: GameTest assertion message
            h.assertTrue(g.getType().is(Tags.EntityTypes.BOSSES), k.id + " is in c:bosses");   // lang-exempt: GameTest assertion message
            RelicTimers.stun(g, 40);
            h.assertFalse(g.isNoAi(), k.id + " was stunned");   // lang-exempt: GameTest assertion message
        }
        for (EntityType<? extends Mob> type : java.util.List.<EntityType<? extends Mob>>of(EntityType.WITHER, EntityType.ENDER_DRAGON)) {
            Mob boss = type.create(level);
            if (boss == null) { h.fail("no " + type); return; }   // lang-exempt: GameTest assertion message
            h.assertTrue(RelicTimers.boss(boss), type + " counts as a boss");   // lang-exempt: GameTest assertion message
            RelicTimers.stun(boss, 40);
            h.assertFalse(boss.isNoAi(), type + " was stunned");   // lang-exempt: GameTest assertion message
        }
        Mob zombie = EntityType.ZOMBIE.create(level);
        if (zombie == null) { h.fail("no zombie"); return; }   // lang-exempt: GameTest assertion message
        h.assertFalse(RelicTimers.boss(zombie), "a zombie is no boss");   // lang-exempt: GameTest assertion message
        RelicTimers.stun(zombie, 1);
        h.assertTrue(zombie.isNoAi(), "an ordinary mob is still stunned");   // lang-exempt: GameTest assertion message
        zombie.setNoAi(false);
        h.succeed();
    }
}
