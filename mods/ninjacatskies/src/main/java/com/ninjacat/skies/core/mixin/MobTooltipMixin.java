package com.ninjacat.skies.core.mixin;

import com.ninjacat.skies.core.compat.JerMobTooltipGuard;
import jeresources.entry.MobEntry;
import jeresources.jei.mob.MobTooltip;
import mezz.jei.api.gui.ingredient.IRecipeSlotView;
import net.minecraft.network.chat.Component;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.List;

@Mixin(value = MobTooltip.class, remap = false)
public abstract class MobTooltipMixin {
    @Shadow
    @Final
    private MobEntry entry;

    @Inject(method = "onTooltip", at = @At("HEAD"), cancellable = true, remap = false)
    private void ncs$skipEmptyDropSlot(IRecipeSlotView slot, List<Component> tooltip, CallbackInfo ci) {
        if (JerMobTooltipGuard.shouldSkip(this.entry.getDrops().size(), slot.getSlotName().orElse("0"))) {
            ci.cancel();
        }
    }
}
