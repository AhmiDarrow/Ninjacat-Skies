package com.ninjacat.skies.core.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.ninjacat.skies.core.NinjacatSkies;
import net.minecraft.client.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.client.event.ClientTickEvent;

/** Opt-in client smoke test, run only in the isolated developer pack profile. */
public final class UiVerification {
    private int stage;
    private long next;
    @SubscribeEvent public void tick(ClientTickEvent.Post event) {
        if(!Boolean.getBoolean("ninjacatskies.uiVerification") || stage>9)return;
        var mc=Minecraft.getInstance();
        if(mc.player==null||mc.level==null||mc.gameMode==null)return;
        if(next==0){next=System.currentTimeMillis()+12000;return;}
        if(System.currentTimeMillis()<next)return;
        next=System.currentTimeMillis()+6000;
        if(stage==0)use(mc,"ninjacatskies:whisker_codex");
        if(stage==1){capture(mc,"quests-from-codex");mc.setScreen(null);use(mc,"clowderhall:island_charter");}
        if(stage==2){
            capture(mc,"clowders-from-charter");
            if(mc.screen!=null)for(var child:mc.screen.children())if(child instanceof net.minecraft.client.gui.components.Button button && button.getMessage().getString().equals("Create New Team")){button.onPress();break;}
        }
        if(stage==3){capture(mc,"create-team-from-panel");mc.setScreen(null);press("key.keyboard.k");}
        if(stage==4){capture(mc,"clowders-from-key");mc.setScreen(null);press("key.keyboard.grave.accent");}
        if(stage==5){capture(mc,"quests-from-key");mc.setScreen(new net.minecraft.client.gui.screens.options.controls.KeyBindsScreen(null,mc.options));}
        if(stage==6){
            capture(mc,"pack-controls");mc.options.save();
            int slot=9;
            for(String tier:new String[]{"small","medium","large"})
                mc.player.getInventory().setItem(slot++,new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.parse("ninjacatskies:"+tier+"_steward_cache"))));
            mc.setScreen(new net.minecraft.client.gui.screens.inventory.InventoryScreen(mc.player));
        }
        if(stage==7)capture(mc,"steward-cache-models");
        if(stage==8){
            mc.setScreen(null);
            mc.player.connection.sendCommand("give @s ninjacatskies:whisker_codex");
            mc.player.setShiftKeyDown(true);
            mc.player.connection.send(new net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket(mc.player,
                    net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket.Action.PRESS_SHIFT_KEY));
            use(mc,"ninjacatskies:whisker_codex");
        }
        if(stage==9){
            capture(mc,"lore-from-codex");
            mc.player.setShiftKeyDown(false);
            mc.player.connection.send(new net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket(mc.player,
                    net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket.Action.RELEASE_SHIFT_KEY));
        }
        stage++;
    }
    private static void use(Minecraft mc,String id){
        mc.player.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.parse(id))));
        mc.gameMode.useItem(mc.player,InteractionHand.MAIN_HAND);
    }
    private static void press(String name){
        var key=InputConstants.getKey(name);
        KeyMapping.click(key);
        net.neoforged.neoforge.common.NeoForge.EVENT_BUS.post(new net.neoforged.neoforge.client.event.InputEvent.Key(key.getValue(),0,org.lwjgl.glfw.GLFW.GLFW_PRESS,0));
    }
    private static void capture(Minecraft mc,String name){
        NinjacatSkies.LOGGER.info("UI verification {}: {}",name,mc.screen==null?"NO SCREEN":mc.screen.getClass().getName());
        Screenshot.grab(mc.gameDirectory,name+".png",mc.getMainRenderTarget(),message->{});
    }
}
