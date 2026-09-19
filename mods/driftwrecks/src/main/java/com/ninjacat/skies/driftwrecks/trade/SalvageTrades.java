package com.ninjacat.skies.driftwrecks.trade;

import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.registry.DwBlocks;
import com.ninjacat.skies.driftwrecks.registry.DwItems;
import com.ninjacat.skies.driftwrecks.wreck.StrandSkin;
import com.ninjacat.skies.driftwrecks.wreck.TeamDrift;
import com.ninjacat.skies.driftwrecks.wreck.WreckCore;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.Merchant;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;

import javax.annotation.Nullable;
import java.util.Optional;

/**
 * The Salvager's Frame: Salvaged Weft buys the tools of the hunt (spools, lures, keys, maps), Keepsake reprints of
 * what the Clowder already found, tribe decor and, with a full set, a Tribe Banner. Offers are built per player from
 * their Clowder's Strands and Atlas, so a locked column never shows.
 */
public final class SalvageTrades implements Merchant {
    private final ServerPlayer player;
    private final MerchantOffers offers;

    private SalvageTrades(ServerPlayer player, MerchantOffers offers) { this.player = player; this.offers = offers; }

    public static void open(ServerPlayer p) {
        SalvageTrades t = new SalvageTrades(p, build(p));
        t.openTradingScreen(p, Component.translatable("container.driftwrecks.salvagers_frame"), 0);
    }

    public static MerchantOffers build(ServerPlayer p) {
        MerchantOffers o = new MerchantOffers();
        Optional<Clowder> oc = LoomTension.clowderOf(p);
        TeamDrift team = oc.map(TeamDrift::of).orElse(null);
        int seated = oc.map(c -> Integer.bitCount(LoomTension.strandBits(c))).orElse(0);
        o.add(offer(4, new ItemStack(DwItems.TETHER_SPOOL.get())));
        o.add(offer(10, new ItemStack(DwItems.DRIFTLURE.get())));
        o.add(offer(16, new ItemStack(DwItems.WRECK_MAP_SCROLL.get())));
        o.add(offer(6, new ItemStack(DwItems.DRIFT_NEEDLE.get())));
        o.add(offer(8, new ItemStack(DwBlocks.SALVAGE_CRATE.get())));
        if (oc.isEmpty()) return o;
        Clowder c = oc.get();
        for (Strand s : Strand.ALL) {
            if (!LoomTension.isSeated(c, s)) continue;
            int lure = team.halfPriceLure(s) ? 12 : 24;
            o.add(offer(lure, DwItems.strandStack(DwItems.STRAND_LURE.get(), s)));
            if (seated >= 7) {
                int key = team.halfPriceKeys() ? 15 : 30;
                o.add(new MerchantOffer(new ItemCost(DwItems.SALVAGED_WEFT.get(), key), Optional.of(keyMaterial(s)),
                        DwItems.strandStack(DwItems.WEFT_KEY.get(), s), Integer.MAX_VALUE, 0, 0F));
            }
            // tribe decor: that Strand's palette, by the stack
            o.add(offer(12, new ItemStack(StrandSkin.resolve(s, "wall").getBlock().asItem(), 32)));
            o.add(offer(16, new ItemStack(StrandSkin.resolve(s, "trim").getBlock().asItem(), 24)));
            o.add(offer(20, new ItemStack(StrandSkin.resolve(s, "roof").getBlock().asItem(), 32)));
            if (hasSet(team, s) || team.columnComplete(s)) o.add(offer(20, new ItemStack(DwBlocks.BANNERS.get(s).get().asItem())));
            for (WreckCore core : WreckCore.ALL) if (team.hasKeepsake(s, core)) o.add(offer(60, new ItemStack(DwBlocks.keepsake(s, core).asItem())));
        }
        return o;
    }

    private static boolean hasSet(TeamDrift t, Strand s) {
        for (WreckCore c : WreckCore.ALL) if (!t.hasKeepsake(s, c)) return false;
        return true;
    }

    /** The Strand's material for its Weft Key. */
    private static ItemCost keyMaterial(Strand s) {
        return switch (s) {
            case SOIL -> new ItemCost(Items.ROOTED_DIRT, 16);
            case STONE -> new ItemCost(Items.AMETHYST_SHARD, 12);
            case SPROUT -> new ItemCost(Items.GLOW_BERRIES, 16);
            case CLAW -> new ItemCost(Items.GOLD_INGOT, 6);
            case SPARK -> new ItemCost(Items.COPPER_INGOT, 24);
            case CLOCK -> new ItemCost(Items.REDSTONE, 24);
            case SWARM -> new ItemCost(Items.HONEYCOMB, 12);
            case SIGIL -> new ItemCost(Items.ENDER_PEARL, 4);
            case SPINDLE -> new ItemCost(Items.CYAN_WOOL, 16);
        };
    }

    private static MerchantOffer offer(int weft, ItemStack out) {
        Item w = DwItems.SALVAGED_WEFT.get();
        ItemCost a = new ItemCost(w, Math.min(64, weft));
        Optional<ItemCost> b = weft > 64 ? Optional.of(new ItemCost(w, weft - 64)) : Optional.empty();
        return new MerchantOffer(a, b, out, Integer.MAX_VALUE, 0, 0F);
    }

    @Override public void setTradingPlayer(@Nullable Player p) {}
    @Nullable @Override public Player getTradingPlayer() { return player; }
    @Override public MerchantOffers getOffers() { return offers; }
    @Override public void overrideOffers(MerchantOffers o) {}
    @Override public void notifyTrade(MerchantOffer offer) { offer.increaseUses(); }
    @Override public void notifyTradeUpdated(ItemStack stack) {}
    @Override public int getVillagerXp() { return 0; }
    @Override public void overrideXp(int xp) {}
    @Override public boolean showProgressBar() { return false; }
    @Override public SoundEvent getNotifyTradeSound() { return SoundEvents.VILLAGER_YES; }
    @Override public boolean isClientSide() { return false; }
}
