package com.ninjacat.skies.core.tension;

/** One persistent life pool per Clowder, including members who are offline. */
public final class ClowderLives {
    private static final String KEY = "shared_lives";
    private static final String CONTRIBUTORS = "life_contributors";
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
        team.markDirty();
        return true;
    }

    public static int remaining(Clowder team, int startingLives) {
        var data = team.data();
        int saved = data.getInt(KEY);
        int lives = Math.max(0, Math.min(MAX_LIVES, saved));
        var contributors = data.getCompound(CONTRIBUTORS);
        boolean changed = saved != lives || !data.contains(KEY);
        for (var member : team.memberIds()) {
            if (!contributors.getBoolean(member.toString())) {
                lives = (int) Math.min(MAX_LIVES, (long) lives + Math.max(1, Math.min(99, startingLives)));
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
        team.markDirty();
        return lives;
    }

    public static int reset(Clowder team, int startingLives) {
        remaining(team, startingLives); // Record current contributors without erasing old receipts.
        int lives = (int) Math.min(MAX_LIVES, (long) Math.max(1, team.memberIds().size())
                * Math.max(1, Math.min(99, startingLives)));
        team.data().putInt(KEY, lives);
        team.markDirty();
        return lives;
    }
}
