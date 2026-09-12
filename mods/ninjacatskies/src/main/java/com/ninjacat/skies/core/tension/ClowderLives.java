package com.ninjacat.skies.core.tension;

import java.util.UUID;

/** One persistent life pool per Clowder, including members who are offline. */
public final class ClowderLives {
    private static final String KEY = "shared_lives";
    private static final String CONTRIBUTORS = "life_contributors";
    private static final String EXHAUSTED_MEMBERS = "exhausted_members";
    private static final int MAX_LIVES = 1_000_000;

    private ClowderLives() {}

    /** Receipt is persisted with the team: multiple members cannot multiply a quest reward. */
    public static boolean award(Clowder team, int startingLives, String milestone) {
        if (!java.util.Set.of("clock", "dragon", "power", "sigil", "bestiary", "reweave").contains(milestone)) return false;
        String receipt = "life_reward_" + milestone;
        if (team.data().getBoolean(receipt)) return false;
        int lives = remaining(team, startingLives);
        if (lives >= MAX_LIVES) return false;
        team.data().putInt(KEY, lives + 1);
        team.data().putBoolean(receipt, true);
        team.data().remove(EXHAUSTED_MEMBERS);
        team.markDirty();
        return true;
    }

    /** Player persistent-data flag set by SkyboundEvents when a Clowder's pool hits zero. */
    public static final String EXHAUSTED_FLAG = "skybound_exhausted";

    public static int remaining(Clowder team, int startingLives) {
        var data = team.data();
        int saved = data.getInt(KEY);
        int lives = Math.max(0, Math.min(MAX_LIVES, saved));
        var contributors = data.getCompound(CONTRIBUTORS);
        boolean changed = saved != lives || !data.contains(KEY);
        // members who have spent a Clowder's last life bring no fresh lives with them: leaving a party and joining
        // another (or falling back to a solo team) must not be a revive
        java.util.Set<UUID> exhausted = new java.util.HashSet<>();
        var savedExhausted = data.getCompound(EXHAUSTED_MEMBERS);
        for (String k : savedExhausted.getAllKeys()) {
            if (savedExhausted.getBoolean(k)) {
                try { exhausted.add(UUID.fromString(k)); } catch (IllegalArgumentException ignored) {}
            }
        }
        for (var online : team.onlineMembers()) if (online.getPersistentData().getBoolean(EXHAUSTED_FLAG)) exhausted.add(online.getUUID());
        for (var member : team.memberIds()) {
            if (!contributors.getBoolean(member.toString())) {
                if (!exhausted.contains(member)) lives = (int) Math.min(MAX_LIVES, (long) lives + Math.max(1, Math.min(99, startingLives)));
                contributors.putBoolean(member.toString(), true);
                changed = true;
            }
        }
        if (changed) {
            data.putInt(KEY, lives);
            data.put(CONTRIBUTORS, contributors);
            team.markDirty();
        }
        return lives;
    }

    public static int spend(Clowder team, int startingLives) {
        int lives = Math.max(0, remaining(team, startingLives) - 1);
        team.data().putInt(KEY, lives);
        if (lives == 0) {
            var ex = team.data().getCompound(EXHAUSTED_MEMBERS);
            for (UUID id : team.memberIds()) ex.putBoolean(id.toString(), true);
            team.data().put(EXHAUSTED_MEMBERS, ex);
        }
        team.markDirty();
        return lives;
    }

    public static int reset(Clowder team, int startingLives) {
        remaining(team, startingLives); // Record current contributors without erasing old receipts.
        int lives = (int) Math.min(MAX_LIVES, (long) Math.max(1, team.memberIds().size())
                * Math.max(1, Math.min(99, startingLives)));
        team.data().putInt(KEY, lives);
        team.data().remove(EXHAUSTED_MEMBERS);
        team.markDirty();
        return lives;
    }

    /** One life for one mate (Overweaver shuttle). Other exhausted members stay down. */
    public static int restoreOne(Clowder team, UUID member, int startingLives) {
        int lives = remaining(team, startingLives);
        if (lives >= MAX_LIVES) return lives;
        lives++;
        team.data().putInt(KEY, lives);
        var ex = team.data().getCompound(EXHAUSTED_MEMBERS);
        ex.remove(member.toString());
        team.data().put(EXHAUSTED_MEMBERS, ex);
        team.markDirty();
        return lives;
    }

    public static boolean isExhausted(Clowder team, UUID member) {
        return team.data().getCompound(EXHAUSTED_MEMBERS).getBoolean(member.toString());
    }
}
