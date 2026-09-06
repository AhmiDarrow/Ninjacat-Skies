package com.ninjacat.skies.core.item;

import com.ninjacat.skies.core.sound.ModSounds;
import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * A page torn from a steward's margin. Right-click to read it. Pages are kept, not spent —
 * nine tribes' worth make a shelf worth having.
 */
public class CodexPageItem extends Item {
    /** Three notes per tribe, in canon order. Each is one screen, one thought, one verb. */
    private static final String[][] NOTES = {
            { // Soil — Pad-keepers
                    "We never called it dirt. We called it what was left, and we kept it warm.",
                    "A pad holds because someone decided it would. Decide daily.",
                    "Plant the sapling before you are hungry. Hunger makes poor gardeners."
            },
            { // Stone — Grit-singers
                    "Every shard has a note. Iron is low and patient. Gold barely bothers to answer.",
                    "The mesh does not find the ore. The mesh gives the ore somewhere to land.",
                    "Yarn from the void is not magic. It is thread that remembers where it came from."
            },
            { // Sprout — Rootbinders
                    "Roots are the only rope the void respects.",
                    "Feed the pad and the pad feeds the Clowder. That is the whole treaty.",
                    "A seed you can grow twice is worth more than an ingot you can grow once."
            },
            { // Claw — Edge-walkers
                    "The rim is not the edge of the world. It is the edge of your attention.",
                    "Boots first. Then the bridge. Then the courage; it arrives on its own.",
                    "We left footholds so nobody would have to be brave in the same place twice."
            },
            { // Spark — Drumhearts
                    "Power is a rhythm before it is a number.",
                    "The drum is not loud. The drum is steady. Be the drum.",
                    "An orphan engine still hums. Listen to it before you feed it."
            },
            { // Clock — Pattern-weavers
                    "A factory is a song that has stopped needing the singer.",
                    "Make one thing well. Then teach the cogs to make it without you.",
                    "Every belt is a thread. Every gear is a knot. You already know this craft."
            },
            { // Swarm — Colony-keepers
                    "You do not own a hive. You are on good terms with it.",
                    "Living industry forgives mistakes that machines do not.",
                    "The March had flowers that hummed back. We miss them most at dusk."
            },
            { // Sigil — Seal-carvers
                    "A seal is a promise you carve so the world has to keep it.",
                    "Never bind what you would not be willing to unbind.",
                    "Spirit goes where it is asked politely and stays where it is fed."
            },
            { // Spindle — Loom-stitchers
                    "We cut the gate-paths. We always meant to come back and mend them.",
                    "The Loom was never one thread. It was nine agreeing.",
                    "When you reach the March, tell it we are sorry it took so long."
            },
    };

    public CodexPageItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!(player instanceof ServerPlayer sp)) {
            return InteractionResultHolder.sidedSuccess(stack, true);
        }
        Strand strand = tribeOf(stack);
        int slot = Math.floorMod((int) (level.getGameTime() / 20L) + player.getUUID().hashCode(), 3);
        String note = NOTES[strand.ordinal()][slot];

        level.playSound(null, player.blockPosition(), ModSounds.PAGE.get(), SoundSource.PLAYERS, 0.8F, 1.0F);
        sp.sendSystemMessage(Component.literal("— " + strand.tribe() + " margin —").withStyle(s -> s.withColor(strand.color()).withItalic(true)));
        sp.sendSystemMessage(NinjacatText.teal(note));
        player.getCooldowns().addCooldown(this, 20);
        return InteractionResultHolder.sidedSuccess(stack, false);
    }

    /** A page named at seat time knows its tribe; a Desk page picks one by where it is in the stack. */
    private static Strand tribeOf(ItemStack stack) {
        Component name = stack.get(DataComponents.CUSTOM_NAME);
        if (name != null) {
            String raw = name.getString();
            for (Strand s : Strand.ALL) {
                if (raw.contains(s.tribe())) {
                    return s;
                }
            }
        }
        return Strand.ALL[Math.floorMod(stack.getCount() * 7 + 3, Strand.ALL.length)];
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.ninjacatskies.codex_page").withStyle(s -> s.withColor(0x8A8580)));
    }
}
