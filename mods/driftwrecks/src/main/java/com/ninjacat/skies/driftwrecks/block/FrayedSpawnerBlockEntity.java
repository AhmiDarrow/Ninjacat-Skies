package com.ninjacat.skies.driftwrecks.block;

import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.driftwrecks.registry.DwRegistries;
import com.ninjacat.skies.driftwrecks.wreck.DriftManager;
import com.ninjacat.skies.driftwrecks.wreck.Wreck;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;

/**
 * Spawns a couple of the wreck's mobs every 10-20 seconds while a player is within 16 blocks, up to a cap that
 * grows with the Clowder members online. Mobs are tagged to the wreck and leave with it.
 */
public class FrayedSpawnerBlockEntity extends BlockEntity {
    private int wreckId = -1;
    private int delay = 200;

    public FrayedSpawnerBlockEntity(BlockPos pos, BlockState state) { super(DwRegistries.FRAYED_SPAWNER.get(), pos, state); }

    public void setup(Wreck w, RandomSource rng) {
        wreckId = w.id;
        delay = 100 + rng.nextInt(100);
        setChanged();
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, FrayedSpawnerBlockEntity be) {
        if (!(level instanceof ServerLevel sl) || --be.delay > 0) return;
        be.delay = 200 + level.random.nextInt(200);
        if (level.getNearestPlayer(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 16, p -> !p.isSpectator() && !((net.minecraft.world.entity.player.Player) p).isCreative()) == null) return;
        DriftManager m = DriftManager.get(sl.getServer());
        Wreck w = m.byId(be.wreckId);
        if (w == null || w.phase != Wreck.Phase.ACTIVE) return;
        int online = LoomTension.clowderById(sl.getServer(), w.team).map(c -> c.onlineMembers().size()).orElse(1);
        int cap = Math.round(4 * DriftManager.partyScale(online));
        AABB near = new AABB(pos).inflate(16);
        int have = sl.getEntitiesOfClass(Mob.class, near, DriftManager::isWreckMob).size();
        for (int i = 0; i < 2 && have < cap; i++, have++) {
            EntityType<?> type = m.mobFor(w, level.random.nextInt(8));
            Entity e = type.create(sl);
            if (!(e instanceof Mob mob)) continue;
            double x = pos.getX() + 0.5 + (level.random.nextDouble() - 0.5) * 4, z = pos.getZ() + 0.5 + (level.random.nextDouble() - 0.5) * 4;
            BlockPos at = BlockPos.containing(x, pos.getY(), z);
            for (int dy = 0; dy < 3 && !sl.getBlockState(at).isAir(); dy++) at = at.above();
            if (!sl.getBlockState(at.below()).isSolid()) at = pos.above();
            mob.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, level.random.nextFloat() * 360, 0);
            mob.finalizeSpawn(sl, sl.getCurrentDifficultyAt(at), MobSpawnType.SPAWNER, null);
            m.tagMob(w, mob);
            sl.addFreshEntity(mob);
            sl.sendParticles(ParticleTypes.ASH, at.getX() + 0.5, at.getY() + 0.5, at.getZ() + 0.5, 12, 0.4, 0.6, 0.4, 0.02);
        }
        be.setChanged();
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider regs) {
        super.saveAdditional(tag, regs);
        tag.putInt("wreck", wreckId); tag.putInt("delay", delay);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider regs) {
        super.loadAdditional(tag, regs);
        wreckId = tag.getInt("wreck"); delay = tag.getInt("delay");
    }
}
