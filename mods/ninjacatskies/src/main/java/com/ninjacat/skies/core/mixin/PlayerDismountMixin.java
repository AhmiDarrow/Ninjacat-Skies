package com.ninjacat.skies.core.mixin;

import com.ninjacat.skies.core.config.SkiesConfig;
import com.ninjacat.skies.core.event.DismountRequests;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Vanilla dismounts a rider whose sneak is held ({@code Player.rideTick} asks {@code wantsToStopRiding}).
 * Here only a Dismount-key request does. For that one tick the rider reads as sneaking, so mods that guard
 * a sneak-dismount (Chocobos Reborn will not drop you mid-flight or onto water) still get their say.
 */
@Mixin(Player.class)
public abstract class PlayerDismountMixin {
    @Unique
    private boolean ninjacat$emulatedSneak;

    @Inject(method = "wantsToStopRiding", at = @At("HEAD"), cancellable = true)
    private void ninjacat$dismountKey(CallbackInfoReturnable<Boolean> cir) {
        if (!((Object) this instanceof ServerPlayer player) || SkiesConfig.SNEAK_DISMOUNTS.get()) return;
        boolean requested = DismountRequests.take(player);
        if (requested && !player.isShiftKeyDown()) {
            ninjacat$emulatedSneak = true;
            player.setShiftKeyDown(true);
        }
        cir.setReturnValue(requested);
    }

    @Inject(method = "rideTick", at = @At("RETURN"))
    private void ninjacat$releaseEmulatedSneak(CallbackInfo ci) {
        if (!ninjacat$emulatedSneak) return;
        ninjacat$emulatedSneak = false;
        ((Player) (Object) this).setShiftKeyDown(false);
    }
}
