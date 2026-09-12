package com.ninjacat.skies.core.verification;

import com.ninjacat.skies.core.tension.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.gametest.*;
import java.util.*;

@GameTestHolder("ninjacatskies")
@PrefixGameTestTemplate(false)
public class LivesGameTests {
    private record TestTeam(UUID id, CompoundTag data) implements Clowder {
        public Component name() { return Component.literal("Test Clowder"); }
        public void markDirty() { data.putBoolean("saved", true); }
        public Collection<ServerPlayer> onlineMembers() { return List.of(); }
    }

    @GameTest(template="empty")
    public static void membersSharePoolAndOtherTeamsAreIndependent(GameTestHelper h) {
        var id = UUID.randomUUID(); var shared = new CompoundTag();
        Clowder first = new TestTeam(id, shared), second = new TestTeam(id, shared);
        Clowder other = new TestTeam(UUID.randomUUID(), new CompoundTag());
        h.assertTrue(ClowderLives.remaining(first, 3) == 3, "Team starts with three");
        ClowderLives.spend(first, 3);
        h.assertTrue(ClowderLives.remaining(second, 3) == 2, "Second member sees first death");
        ClowderLives.spend(second, 3);
        h.assertTrue(ClowderLives.remaining(first, 3) == 1, "Both deaths charge the same pool");
        h.assertTrue(ClowderLives.remaining(other, 3) == 3, "Other team stays independent");
        h.succeed();
    }

    @GameTest(template="empty")
    public static void exhaustedPoolSurvivesReloadAndRevivesTogether(GameTestHelper h) {
        var id = UUID.randomUUID(); Clowder team = new TestTeam(id, new CompoundTag());
        for (int i = 0; i < 10; i++) ClowderLives.spend(team, 3);
        h.assertTrue(team.data().getBoolean("saved"), "Mutations mark the team dirty");
        Clowder reloaded = new TestTeam(id, team.data().copy());
        h.assertTrue(ClowderLives.remaining(reloaded, 3) == 0, "Zero survives save/reload without refill");
        h.assertTrue(ClowderLives.reset(reloaded, 3) == 3, "Revive restores the pool");
        h.assertTrue(ClowderLives.remaining(new TestTeam(id, reloaded.data()), 3) == 3,
                "Rejoining members see restored pool");
        h.succeed();
    }

    @GameTest(template="empty")
    public static void corruptSavedLivesRemainBounded(GameTestHelper h) {
        Clowder team = new TestTeam(UUID.randomUUID(), new CompoundTag());
        ClowderLives.remaining(team, 3);
        team.data().putInt("shared_lives", -100);
        h.assertTrue(ClowderLives.remaining(team, 3) == 0, "Negative saves cannot grant lives");
        team.data().putInt("shared_lives", Integer.MAX_VALUE);
        h.assertTrue(ClowderLives.remaining(team, 3) == 1_000_000, "Oversized saves are bounded");
        h.succeed();
    }
    @GameTest(template="empty")
    public static void rareRewardsCannotBeMultipliedOrReset(GameTestHelper h) {
        var id = UUID.randomUUID(); var shared = new CompoundTag();
        Clowder member = new TestTeam(id, shared), mate = new TestTeam(id, shared);
        h.assertTrue(ClowderLives.award(member, 3, "sigil"), "Milestone grants one life");
        h.assertTrue(!ClowderLives.award(mate, 3, "sigil"), "Another member cannot duplicate it");
        h.assertTrue(ClowderLives.remaining(mate, 3) == 4, "Reward adds exactly one");
        ClowderLives.reset(mate, 3);
        Clowder reloaded = new TestTeam(id, shared.copy());
        h.assertTrue(!ClowderLives.award(reloaded, 3, "sigil"), "Revive and reload preserve receipts");
        for (int i = 0; i < 3; i++) ClowderLives.spend(reloaded, 3);
        h.assertTrue(ClowderLives.award(reloaded, 3, "bestiary"), "Earned reward rescues exhausted pool");
        h.assertTrue(ClowderLives.remaining(reloaded, 3) == 1, "Rescue grants one, not starting lives");
        h.assertTrue(!ClowderLives.award(reloaded, 3, "invented"), "Unknown milestones rejected");
        h.succeed();
    }
    @GameTest(template="empty")
    public static void everyMemberContributesOnceIncludingOfflineAndRejoins(GameTestHelper h) {
        var members = new HashSet<UUID>(); var first = UUID.randomUUID(); var second = UUID.randomUUID();
        members.add(first);
        Clowder team = new Clowder() {
            private final UUID id = UUID.randomUUID();
            private final CompoundTag data = new CompoundTag();
            public UUID id() { return id; }
            public CompoundTag data() { return data; }
            public Component name() { return Component.literal("Party"); }
            public void markDirty() {}
            public Collection<ServerPlayer> onlineMembers() { return List.of(); }
            public Collection<UUID> memberIds() { return members; }
        };
        h.assertTrue(ClowderLives.remaining(team, 3) == 3, "One member starts with three");
        members.add(second);
        h.assertTrue(ClowderLives.remaining(team, 3) == 6, "Offline second member contributes three");
        ClowderLives.spend(team, 3);
        members.remove(second);
        h.assertTrue(ClowderLives.remaining(team, 3) == 5, "Leaving does not rewind spent lives");
        members.add(second);
        h.assertTrue(ClowderLives.remaining(team, 3) == 5, "Rejoining cannot refill the pool");
        members.add(UUID.randomUUID());
        h.assertTrue(ClowderLives.remaining(team, 3) == 8, "Third member adds three to remaining lives");
        h.assertTrue(ClowderLives.reset(team, 3) == 9, "Operator reset scales to current three members");
        h.succeed();
    }

    @GameTest(template="empty")
    public static void restoreOneUnexhaustsOnlyTheMate(GameTestHelper h) {
        var members = new HashSet<UUID>();
        UUID a = UUID.randomUUID(), b = UUID.randomUUID();
        members.add(a); members.add(b);
        Clowder team = new Clowder() {
            private final UUID id = UUID.randomUUID();
            private final CompoundTag data = new CompoundTag();
            public UUID id() { return id; }
            public CompoundTag data() { return data; }
            public Component name() { return Component.literal("Party"); }
            public void markDirty() {}
            public Collection<ServerPlayer> onlineMembers() { return List.of(); }
            public Collection<UUID> memberIds() { return members; }
        };
        while (ClowderLives.remaining(team, 3) > 0) ClowderLives.spend(team, 3);
        h.assertTrue(ClowderLives.isExhausted(team, a) && ClowderLives.isExhausted(team, b), "Both mates exhausted at zero");
        h.assertTrue(ClowderLives.restoreOne(team, a, 3) == 1, "Shuttle restores one life");
        h.assertTrue(!ClowderLives.isExhausted(team, a), "Rescued mate stands");
        h.assertTrue(ClowderLives.isExhausted(team, b), "Other mate stays down");
        h.assertTrue(ClowderLives.remaining(team, 3) == 1, "Pool is one, not a full reset");
        h.succeed();
    }
}
