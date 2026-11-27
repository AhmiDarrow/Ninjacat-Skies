package com.ninjacat.skies.craftweave.mixin;

import com.ninjacat.skies.craftweave.CraftTables;
import net.minecraft.world.inventory.AbstractContainerMenu;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * The Tribal Bench remakes its default result whenever the result slot is about to be picked up, which would hand
 * over the default recipe instead of the player's pick. Optional: without Tribal Power there is nothing to patch.
 */
@Pseudo
@Mixin(targets = "tk.darrow.tribalpower.bench.BenchMenu")
public abstract class TribalBenchMenuMixin {
    @Inject(method = "refreshResult", at = @At("TAIL"), require = 0, remap = false)
    private void craftweave$keepPick(CallbackInfo ci) {
        AbstractContainerMenu self = (AbstractContainerMenu) (Object) this;
        if (!CraftTables.isTable(self)) return;
        var owner = CraftTables.owner(self);
        if (owner != null) CraftTables.applyPick(self, owner);
    }
}
