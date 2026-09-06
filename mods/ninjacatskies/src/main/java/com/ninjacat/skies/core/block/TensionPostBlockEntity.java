package com.ninjacat.skies.core.block;

import com.ninjacat.skies.core.sound.ModSounds;
import com.ninjacat.skies.core.tension.Strand;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.joml.Vector3f;

import javax.annotation.Nullable;
import java.util.UUID;

/** Holds which Clowder raised this Post and runs the client-side hum and thread particles. */
public class TensionPostBlockEntity extends BlockEntity {
    private static final int HUM_EVERY = 90;
    @Nullable
    private UUID clowder;

    public TensionPostBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.TENSION_POST.get(), pos, state);
    }

    @Nullable
    public UUID getClowder() {
        return clowder;
    }

    public void setClowder(UUID id) {
        if (!id.equals(clowder)) {
            clowder = id;
            setChanged();
        }
    }

    public static void clientTick(Level level, BlockPos pos, BlockState state, TensionPostBlockEntity be) {
        int seated = TensionPostBlock.seatedCount(state);
        if (seated == 0) {
            return;
        }
        RandomSource rand = level.random;
        double cx = pos.getX() + 0.5;
        double cz = pos.getZ() + 0.5;

        // One thin thread of dust per seated Strand, drifting up from its notch.
        for (Strand s : Strand.ALL) {
            if (!state.getValue(TensionPostBlock.SEATED.get(s)) || rand.nextInt(14) != 0) {
                continue;
            }
            int i = s.ordinal();
            double y = pos.getY() + (1.5 + i * 1.5) / 16.0;
            double ox = 0;
            double oz = 0;
            switch (i % 4) {
                case 0 -> oz = -0.42;
                case 1 -> ox = 0.42;
                case 2 -> oz = 0.42;
                default -> ox = -0.42;
            }
            int c = s.color();
            level.addParticle(new DustParticleOptions(new Vector3f(((c >> 16) & 0xFF) / 255F, ((c >> 8) & 0xFF) / 255F, (c & 0xFF) / 255F), 0.7F),
                    cx + ox, y, cz + oz, 0, 0.02, 0);
        }

        if (state.getValue(TensionPostBlock.REWOVEN) && rand.nextInt(6) == 0) {
            level.addParticle(ParticleTypes.END_ROD, cx, pos.getY() + 1.05, cz, 0, 0.03 + rand.nextDouble() * 0.02, 0);
        }

        // The hum: quiet, low, wooden. Louder as the Loom fills.
        if ((level.getGameTime() + pos.hashCode()) % HUM_EVERY == 0) {
            float volume = 0.10F + 0.035F * seated;
            float pitch = 0.85F + 0.03F * seated;
            level.playLocalSound(cx, pos.getY() + 0.5, cz, ModSounds.LOOM_HUM.get(), SoundSource.BLOCKS, volume, pitch, false);
        }
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        clowder = tag.hasUUID("Clowder") ? tag.getUUID("Clowder") : null;
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        if (clowder != null) {
            tag.putUUID("Clowder", clowder);
        }
    }

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider registries) {
        return saveWithoutMetadata(registries);
    }

    @Nullable
    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }
}
