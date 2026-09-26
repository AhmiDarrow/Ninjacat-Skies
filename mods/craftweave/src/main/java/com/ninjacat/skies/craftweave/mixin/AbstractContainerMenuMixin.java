package com.ninjacat.skies.craftweave.mixin;

import com.ninjacat.skies.craftweave.CraftTables;
import net.minecraft.world.Container;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.CraftingMenu;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Tables that are not vanilla's (the Tribal Bench and its kind) make their result in their own slotsChanged and then
 * call up to this one: that is the moment to apply the player's pick.
 */
@Mixin(AbstractContainerMenu.class)
public abstract class AbstractContainerMenuMixin {
    @Inject(method = "slotsChanged", at = @At("TAIL"))
    private void craftweave$applyPick(Container container, CallbackInfo ci) {
        AbstractContainerMenu self = (AbstractContainerMenu) (Object) this;
        if (self instanceof CraftingMenu || !CraftTables.isTable(self)) return;
        var owner = CraftTables.owner(self);
        if (owner != null) CraftTables.applyPick(self, owner);
    }
}
