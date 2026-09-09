package com.ninjacat.skies.guardians.arena;

import com.ninjacat.skies.guardians.GuardianKind;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;

import javax.annotation.Nullable;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** One running (or just finished) fight in one arena slot. Saved with the level so a restart mid-fight recovers. */
public final class ArenaInstance {
    public enum State { FIGHT, WON, WIPED }

    public final int slot;
    public final GuardianKind kind;
    public final BlockPos originPos;
    public final List<UUID> party = new ArrayList<>();
    @Nullable public UUID clowderId;
    @Nullable public UUID boss;
    public State state = State.FIGHT;
    public int stateTicks = 0, age = 0;
    public int radius;

    public ArenaInstance(int slot, GuardianKind kind, BlockPos originPos, int radius) { this.slot = slot; this.kind = kind; this.originPos = originPos; this.radius = radius; }

    public Vec3 origin() { return Vec3.atBottomCenterOf(originPos); }
    public int partySize() { return party.size(); }

    /** Party members currently online and inside the arena dimension. */
    public List<ServerPlayer> onlinePlayers() {
        List<ServerPlayer> out = new ArrayList<>();
        MinecraftServer server = net.neoforged.neoforge.server.ServerLifecycleHooks.getCurrentServer();
        if (server == null) return out;
        for (UUID id : party) {
            ServerPlayer p = server.getPlayerList().getPlayer(id);
            if (p != null && ArenaManager.inArena(p) && p.isAlive() && !p.isSpectator()) out.add(p);
        }
        return out;
    }

    public CompoundTag save() {
        CompoundTag t = new CompoundTag();
        t.putInt("Slot", slot); t.putString("Kind", kind.id); t.put("Origin", NbtUtils.writeBlockPos(originPos)); t.putInt("Radius", radius);
        ListTag l = new ListTag(); for (UUID u : party) l.add(NbtUtils.createUUID(u)); t.put("Party", l);
        if (clowderId != null) t.putUUID("Clowder", clowderId); if (boss != null) t.putUUID("Boss", boss);
        t.putString("State", state.name()); t.putInt("StateTicks", stateTicks); t.putInt("Age", age);
        return t;
    }

    @Nullable
    public static ArenaInstance load(CompoundTag t) {
        GuardianKind k = GuardianKind.byId(t.getString("Kind")); if (k == null) return null;
        ArenaInstance a = new ArenaInstance(t.getInt("Slot"), k, NbtUtils.readBlockPos(t, "Origin").orElse(BlockPos.ZERO), t.getInt("Radius"));
        for (Tag u : t.getList("Party", Tag.TAG_INT_ARRAY)) a.party.add(NbtUtils.loadUUID(u));
        if (t.hasUUID("Clowder")) a.clowderId = t.getUUID("Clowder"); if (t.hasUUID("Boss")) a.boss = t.getUUID("Boss");
        try { a.state = State.valueOf(t.getString("State")); } catch (IllegalArgumentException e) { a.state = State.WIPED; }
        a.stateTicks = t.getInt("StateTicks");
        a.age = 0;                       // a restart mid-fight starts the grace period again: the party and the boss's chunks are not back yet
        return a;
    }
}
