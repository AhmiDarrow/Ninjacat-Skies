package com.ninjacat.skies.driftwrecks.item;

import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.DriftConfig;
import com.ninjacat.skies.driftwrecks.registry.DwComponents;
import com.ninjacat.skies.driftwrecks.wreck.DriftManager;
import com.ninjacat.skies.driftwrecks.wreck.TeamDrift;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;

import javax.annotation.Nullable;
import java.util.List;
import java.util.Optional;

/**
 * Bait of thread and a bead. Used at your Tension Post it fills Drift pressure at once; a Strand-bead Lure also
 * gives a 60% chance the wreck wears that Strand's skin. One lure per Clowder per cooldown.
 */
public class DriftlureItem extends Item {
    private final boolean strandBead;

    public DriftlureItem(boolean strandBead, Properties props) { super(props); this.strandBead = strandBead; }

    @Nullable
    public static Strand strandOf(ItemStack s) {
        String id = s.get(DwComponents.STRAND.get());
        return id == null ? null : Strand.byId(id);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (!level.isClientSide) player.displayClientMessage(NinjacatText.tealKey("message.driftwrecks.lure.hang_on_post"), true);
        return InteractionResultHolder.pass(player.getItemInHand(hand));
    }

    /** Called when the lure is used on a Tension Post. Returns true if it was spent. */
    public boolean apply(ServerPlayer p, ItemStack stack) {
        Optional<Clowder> oc = LoomTension.clowderOf(p);
        if (oc.isEmpty()) return false;
        Clowder c = oc.get();
        if (!LoomTension.isSeated(c, Strand.SOIL)) { p.displayClientMessage(NinjacatText.tealKey("message.driftwrecks.lure.need_soil"), true); return false; }
        DriftManager m = DriftManager.get(p.server);
        if (m.byTeam(c.id()) != null) { p.displayClientMessage(NinjacatText.tealKey("message.driftwrecks.lure.already_holds"), true); return false; }
        TeamDrift t = TeamDrift.of(c);
        long now = p.serverLevel().getGameTime();
        if (now < t.lureReadyAt()) {
            long mins = (t.lureReadyAt() - now + 1199) / 1200;
            p.displayClientMessage((mins == 1 ? NinjacatText.tealKey("message.driftwrecks.lure.settling_one", mins) : NinjacatText.tealKey("message.driftwrecks.lure.settling_many", mins)), true);
            return false;
        }
        Strand s = strandBead ? strandOf(stack) : null;
        if (strandBead && (s == null || !LoomTension.isSeated(c, s))) { p.displayClientMessage(NinjacatText.tealKey("message.driftwrecks.lure.bead_not_tensioned"), true); return false; }
        t.fill();
        t.setLureStrand(s);
        t.setLureReadyAt(now + DriftConfig.LURE_COOLDOWN_MINUTES.get() * 1200L);
        t.dirty();
        p.sendSystemMessage(NinjacatText.tealKey("message.driftwrecks.lure.hums"));
        return true;
    }

    @Override
    public Component getName(ItemStack stack) {
        Strand s = strandOf(stack);
        if (strandBead && s != null) return Component.translatable("item.driftwrecks.strand_lure.named", s.title());
        return super.getName(stack);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> tip, TooltipFlag flag) {
        tip.add(Component.translatable(strandBead ? "item.driftwrecks.strand_lure.tip" : "item.driftwrecks.driftlure.tip").withStyle(st -> st.withColor(0x3D7A7A)));
    }
}
