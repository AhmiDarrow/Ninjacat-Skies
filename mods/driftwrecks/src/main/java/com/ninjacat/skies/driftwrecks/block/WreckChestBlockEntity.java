package com.ninjacat.skies.driftwrecks.block;

import com.ninjacat.skies.core.tension.Strand;
import com.ninjacat.skies.driftwrecks.Driftwrecks;
import com.ninjacat.skies.driftwrecks.registry.DwRegistries;
import com.ninjacat.skies.driftwrecks.wreck.DriftManager;
import com.ninjacat.skies.driftwrecks.wreck.Wreck;
import com.ninjacat.skies.driftwrecks.wreck.WreckModifier;
import com.ninjacat.skies.driftwrecks.wreck.WreckObjective;
import com.ninjacat.skies.driftwrecks.wreck.WreckRewards;
import com.ninjacat.skies.driftwrecks.wreck.WreckTier;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.Vec3;

import java.util.*;

/**
 * Per-player salvage: each opener gets a private 27-slot roll of this chest's tables (no racing teammates). The heart
 * chest finishes a Salvage objective; a hidden-room chest rolls at one tier up. At unravel, anything a member left
 * behind (or never rolled) is bundled for them.
 */
public class WreckChestBlockEntity extends BlockEntity {
    private static final int SIZE = 27;
    private int wreckId = -1;
    private String tier = WreckTier.RAFT.id, skin = Strand.SOIL.id(), modifier = WreckModifier.UNMARKED.id;
    private boolean heart, hidden;
    private final Map<UUID, NonNullList<ItemStack>> rolls = new HashMap<>();
    private long seed;

    public WreckChestBlockEntity(BlockPos pos, BlockState state) { super(DwRegistries.WRECK_CHEST.get(), pos, state); }

    public void setup(Wreck w, boolean heart, boolean hidden) {
        this.wreckId = w.id; this.tier = w.tier.id; this.skin = w.skin.id(); this.modifier = w.modifier.id;
        this.heart = heart; this.hidden = hidden;
        this.seed = worldPosition.asLong() ^ ((long) w.id << 32);
        rolls.clear();
        setChanged();
    }

    public boolean isHeart() { return heart; }

    public void open(ServerPlayer p) {
        ServerLevel level = (ServerLevel) this.level;
        if (level == null) return;
        NonNullList<ItemStack> items = rolls.computeIfAbsent(p.getUUID(), u -> roll(level, u, p));
        setChanged();
        // built from the roll directly: filling a view slot by slot would write the still-empty slots back over it
        SimpleContainer view = new SimpleContainer(items.toArray(new ItemStack[0])) {
            @Override public void setChanged() {
                super.setChanged();
                for (int i = 0; i < SIZE; i++) items.set(i, getItem(i));
                WreckChestBlockEntity.this.setChanged();
            }
        };
        Component title = Component.translatable(heart ? "container.driftwrecks.heart_chest" : hidden ? "container.driftwrecks.hidden_chest" : "container.driftwrecks.wreck_chest");
        p.openMenu(new SimpleMenuProvider((id, inv, pl) -> ChestMenu.threeRows(id, inv, view), title));
        level.playSound(null, worldPosition, SoundEvents.BARREL_OPEN, SoundSource.BLOCKS, 0.8F, 0.8F);
        Wreck w = DriftManager.get(level.getServer()).byId(wreckId);
        if (w != null && heart && w.objective == WreckObjective.SALVAGE && !w.objectiveDone) {
            p.sendSystemMessage(NinjacatText.gold("The heart of the wreck gives up what it kept."));
            DriftManager.get(level.getServer()).completeObjective(level, w);
        }
        if (hidden) WreckRewards.award(p, "hidden_room");
    }

    private NonNullList<ItemStack> roll(ServerLevel level, UUID who, ServerPlayer opener) {
        NonNullList<ItemStack> out = NonNullList.withSize(SIZE, ItemStack.EMPTY);
        SimpleContainer box = new SimpleContainer(SIZE);
        long s = seed ^ who.getMostSignificantBits() ^ who.getLeastSignificantBits();
        LootParams.Builder params = new LootParams.Builder(level).withParameter(LootContextParams.ORIGIN, Vec3.atCenterOf(worldPosition));
        if (opener != null) params.withLuck(opener.getLuck()).withParameter(LootContextParams.THIS_ENTITY, opener);
        LootParams built = params.create(LootContextParamSets.CHEST);
        for (ResourceLocation id : tables()) {
            LootTable table = level.getServer().reloadableRegistries().getLootTable(ResourceKey.create(Registries.LOOT_TABLE, id));
            table.fill(box, built, s++);
        }
        for (int i = 0; i < SIZE; i++) out.set(i, box.getItem(i));
        return out;
    }

    /** Tier table (+1 when hidden), the skin's pool, the heart bonus and Unstable's extra roll. */
    private List<ResourceLocation> tables() {
        List<ResourceLocation> t = new ArrayList<>();
        WreckTier tr = WreckTier.byId(tier);
        int lvl = tr == null ? 1 : tr.level();
        if (hidden) lvl = Math.min(4, lvl + 1);
        t.add(rl("chests/tier" + lvl));
        t.add(rl("chests/skin/" + skin));
        if (heart) t.add(rl("chests/heart"));
        if (WreckModifier.UNSTABLE.id.equals(modifier)) t.add(rl("chests/tier" + Math.min(3, lvl)));
        return t;
    }

    private static ResourceLocation rl(String p) { return ResourceLocation.fromNamespaceAndPath(Driftwrecks.MOD_ID, p); }

    /** At unravel: the member's leftovers, or a fresh roll if they never opened it. Empties their slot. */
    public List<ItemStack> salvageFor(ServerLevel level, UUID member) {
        NonNullList<ItemStack> items = rolls.remove(member);
        if (items == null) items = roll(level, member, null);
        setChanged();
        List<ItemStack> out = new ArrayList<>();
        for (ItemStack s : items) if (!s.isEmpty()) out.add(s);
        return out;
    }

    public boolean opened(UUID u) { return rolls.containsKey(u); }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider regs) {
        super.saveAdditional(tag, regs);
        tag.putInt("wreck", wreckId); tag.putString("tier", tier); tag.putString("skin", skin); tag.putString("modifier", modifier);
        tag.putBoolean("heart", heart); tag.putBoolean("hidden", hidden); tag.putLong("seed", seed);
        ListTag l = new ListTag();
        for (Map.Entry<UUID, NonNullList<ItemStack>> e : rolls.entrySet()) {
            CompoundTag c = new CompoundTag();
            c.putUUID("who", e.getKey());
            ContainerHelper.saveAllItems(c, e.getValue(), true, regs);
            l.add(c);
        }
        tag.put("rolls", l);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider regs) {
        super.loadAdditional(tag, regs);
        wreckId = tag.getInt("wreck"); tier = tag.getString("tier"); skin = tag.getString("skin"); modifier = tag.getString("modifier");
        heart = tag.getBoolean("heart"); hidden = tag.getBoolean("hidden"); seed = tag.getLong("seed");
        rolls.clear();
        for (Tag t : tag.getList("rolls", Tag.TAG_COMPOUND)) {
            CompoundTag c = (CompoundTag) t;
            NonNullList<ItemStack> items = NonNullList.withSize(SIZE, ItemStack.EMPTY);
            ContainerHelper.loadAllItems(c, items, regs);
            rolls.put(c.getUUID("who"), items);
        }
    }

}
