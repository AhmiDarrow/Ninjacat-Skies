package com.ninjacat.skies.driftwrecks.item;

import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.driftwrecks.wreck.DriftManager;
import com.ninjacat.skies.driftwrecks.wreck.Wreck;
import net.minecraft.core.GlobalPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.LodestoneTracker;
import net.minecraft.world.level.Level;

import java.util.Optional;

/** Points at the Clowder's active Driftwreck; spins idle when there is none. Uses the lodestone-tracker angle. */
public class DriftNeedleItem extends Item {
    public DriftNeedleItem(Properties props) { super(props); }

    @Override
    public void inventoryTick(ItemStack stack, Level level, Entity entity, int slot, boolean selected) {
        if (!(level instanceof ServerLevel sl) || !(entity instanceof ServerPlayer p) || p.tickCount % 20 != 0) return;
        Wreck w = LoomTension.clowderOf(p).map(c -> DriftManager.get(sl.getServer()).byTeam(c.id())).orElse(null);
        LodestoneTracker now = stack.get(DataComponents.LODESTONE_TRACKER);
        if (w == null || w.phase == Wreck.Phase.UNRAVELING) {
            if (now != null) stack.remove(DataComponents.LODESTONE_TRACKER);
            return;
        }
        GlobalPos target = GlobalPos.of(DriftManager.level(sl.getServer()).dimension(), w.center());
        if (now == null || !now.target().equals(Optional.of(target))) stack.set(DataComponents.LODESTONE_TRACKER, new LodestoneTracker(Optional.of(target), false));
    }

    @Override
    public boolean isFoil(ItemStack stack) { return false; }
}
