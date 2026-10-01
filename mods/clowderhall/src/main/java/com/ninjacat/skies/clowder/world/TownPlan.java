package com.ninjacat.skies.clowder.world;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.ninjacat.skies.clowder.ClowderHall;
import com.ninjacat.skies.core.block.YarnBasketBlockEntity;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.TagParser;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.world.Container;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.decoration.GlowItemFrame;
import net.minecraft.world.entity.decoration.ItemFrame;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.entity.SignText;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraft.world.phys.AABB;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;

/**
 * Applies the hub town plan, a datapack file at {@code data/clowderhall/towns/clowder_town.json}. The town belongs to
 * the pack (tools/generate_hub_towns.py writes it into the pack's KubeJS data): without it Core raises only the
 * ceremony pad. The plan carries a {@code revision}; a world is rebuilt once each time the revision goes up.
 */
public final class TownPlan {
    public static final ResourceLocation PLAN = ResourceLocation.fromNamespaceAndPath(ClowderHall.MOD_ID, "towns/clowder_town.json");

    /** The town may reach this far from the pad in x and z (the chunks it loads while building). */
    public static final int BOUND = 160;

    private TownPlan() {}
    private record Fill(BlockPos from, BlockPos to, BlockState state) {}

    private static final String RESIDENT = "ncs_hub_resident";
    /** Residents also carry the revision that seated them ({@code ncs_hub_rev_2}), so a stale copy can be told apart. */
    private static final String REVISION_TAG = "ncs_hub_rev_";
    private static final AABB TOWN = new AABB(-BOUND, -64, -BOUND, BOUND, 200, BOUND);

    private static ResourceManager cachedFor;
    private static int cachedRevision;
    /** A plan that failed to apply is not retried (and re-read, 4 MB) on every visit until the next reload. */
    private static ResourceManager failedFor;

    /** The plan's revision, read once per resource reload; 0 when no plan is installed. */
    public static int revision(ServerLevel level) {
        ResourceManager resources = level.getServer().getResourceManager();
        if (resources != cachedFor) {
            cachedRevision = read(resources).map(p -> p.has("revision") ? p.get("revision").getAsInt() : 1).orElse(0);
            cachedFor = resources;
        }
        return cachedRevision;
    }

    private static Optional<JsonObject> read(ResourceManager resources) {
        var resource = resources.getResource(PLAN);
        if (resource.isEmpty()) return Optional.empty();
        try (var reader = new InputStreamReader(resource.get().open(), StandardCharsets.UTF_8)) {
            return Optional.of(JsonParser.parseReader(reader).getAsJsonObject());
        } catch (Exception e) {
            ClowderHall.LOGGER.error("Cannot read the hub town plan {}", PLAN, e);
            return Optional.empty();
        }
    }

    public static boolean build(ServerLevel level) {
        ResourceManager resources = level.getServer().getResourceManager();
        if (resources == failedFor) return false;
        var read = read(resources);
        if (read.isEmpty()) return false;
        try {
            return apply(level, read.get());
        } catch (RuntimeException e) {
            // A malformed plan must not break /clowder hub (ensureHubHall runs on every trip) or rebuild every visit.
            ClowderHall.LOGGER.error("Cannot apply the hub town plan {}", PLAN, e);
            failedFor = resources;
            return false;
        }
    }

    private static boolean apply(ServerLevel level, JsonObject plan) {
        // Validate the entire plan before changing the world. A block from a mod that is not installed is skipped
        // (and counted), so one missing mod never costs the whole town.
        var fills = new ArrayList<Fill>();
        var missing = new HashSet<String>();
        // ~62k boxes share a few hundred block specs: parse each spec once (Optional.empty() = not installed)
        var states = new HashMap<String, Optional<BlockState>>();
        for (var entry : plan.getAsJsonArray("boxes")) {
            var box = entry.getAsJsonObject();
            BlockPos from = pos(box, "from"), to = pos(box, "to");
            if (from.getX()>to.getX() || from.getY()>to.getY() || from.getZ()>to.getZ()
                    || Math.abs(from.getX())>BOUND || Math.abs(to.getX())>BOUND
                    || Math.abs(from.getZ())>BOUND || Math.abs(to.getZ())>BOUND
                    || from.getY()<0 || to.getY()>128) throw new IllegalArgumentException("Town bounds");
            String spec = box.get("block").getAsString();
            BlockState state = states.computeIfAbsent(spec, s -> Optional.ofNullable(state(s))).orElse(null);
            if (state == null) { missing.add(spec.split("\\[", 2)[0]); continue; }
            fills.add(new Fill(from, to, state));
        }
        // Cells the Java ceremony owns (chest, lectern, beacon, reweave ring, markers): the plan never touches them.
        var keep = new LongOpenHashSet();
        if (plan.has("keep")) for (var entry : plan.getAsJsonArray("keep")) {
            var a = entry.getAsJsonArray();
            keep.add(BlockPos.asLong(a.get(0).getAsInt(), a.get(1).getAsInt(), a.get(2).getAsInt()));
        }
        for (var fill : fills) {
            for (BlockPos p : BlockPos.betweenClosed(fill.from(), fill.to())) {
                if (keep.contains(p.asLong())) continue;
                // already right (most of a town on a revision rebuild): setBlock would change nothing either
                if (level.getBlockState(p) == fill.state()) continue;
                if (holdsSomething(level.getBlockEntity(p))) continue;
                level.setBlock(p, fill.state(), 2);
            }
        }
        if (!missing.isEmpty()) ClowderHall.LOGGER.warn("Hub town skipped blocks from missing mods: {}", missing);
        if (plan.has("signs")) for (var entry : plan.getAsJsonArray("signs")) {
            var sign = entry.getAsJsonObject();
            if (level.getBlockEntity(pos(sign,"pos")) instanceof SignBlockEntity be) {
                var text = new SignText().setColor(DyeColor.WHITE).setHasGlowingText(true);
                var lines = sign.getAsJsonArray("lines");
                for (int i=0;i<Math.min(4,lines.size());i++) { String line=lines.get(i).getAsString(); text=text.setMessage(i, line.isEmpty() ? Component.literal("") : Component.translatable(line)); }   // lines are lang keys
                be.setText(text,true); be.setText(text,false); be.setWaxed(true); be.setChanged();
            }
        }
        if (plan.has("frames")) for (var entry : plan.getAsJsonArray("frames")) placeFrame(level, entry.getAsJsonObject());
        if (plan.has("residents")) seatResidents(level, plan);
        return true;
    }

    /**
     * Residents keep their name across revisions: an existing one moves to its new spot instead of doubling up. A
     * resident is any entity id (the old plans said "cat" / "villager"), with optional SNBT merged over a fresh spawn
     * and entity tags the pack's scripts use to look after them. Only residents whose chunks have their entities
     * loaded are seen here (a build usually runs before anyone is in the town); {@link #tidyResidents} retires the
     * older copy of a resident once both are loaded.
     */
    private static void seatResidents(ServerLevel level, JsonObject plan) {
        int revision = plan.has("revision") ? plan.get("revision").getAsInt() : 1;
        var seated = new HashMap<String, Entity>();
        // Revision 1 residents carry no tag: adopt them by name so they walk over rather than double up.
        for (Entity entity : level.getEntities((Entity) null, TOWN,
                e -> e.hasCustomName() && (e.getTags().contains(RESIDENT) || isRevisionOneResident(e)))) {
            seated.putIfAbsent(entity.getCustomName().getString(), entity);
        }
        for (var entry : plan.getAsJsonArray("residents")) {
            var resident = entry.getAsJsonObject();
            var xyz = resident.getAsJsonArray("pos");
            String type = resident.get("type").getAsString();
            if (type.equals("cat") || type.equals("villager")) type = "minecraft:" + type;
            var typeId = ResourceLocation.tryParse(type);
            if (typeId == null || !BuiltInRegistries.ENTITY_TYPE.containsKey(typeId)) {
                ClowderHall.LOGGER.debug("Hub resident skipped (no such entity): {}", resident);
                continue;
            }
            String name = resident.get("name").getAsString();
            boolean ai = !resident.has("ai") || resident.get("ai").getAsBoolean();
            double x = xyz.get(0).getAsDouble(), y = xyz.get(1).getAsDouble(), z = xyz.get(2).getAsDouble();
            var entityType = BuiltInRegistries.ENTITY_TYPE.get(typeId);
            Entity entity = seated.get(name);
            if (entity != null && entity.getType() != entityType) {
                // The name went to a different creature this revision: the old one leaves, the new one is seated.
                entity.discard();
                entity = null;
            }
            boolean fresh = entity == null;
            if (fresh) {
                entity = entityType.create(level);
                if (entity == null) continue;
                entity.moveTo(x, y, z, 180, 0);
                if (entity instanceof Mob mob) {
                    mob.finalizeSpawn(level, level.getCurrentDifficultyAt(BlockPos.containing(x, y, z)), MobSpawnType.STRUCTURE, null);
                }
                entity.setCustomName(Component.literal(name));
                entity.setCustomNameVisible(!resident.has("show_name") || resident.get("show_name").getAsBoolean());
            }
            // Adopted residents take the plan's data too: an old village's villager gets its trade and empty offers.
            if (resident.has("nbt")) {
                try {
                    CompoundTag tag = entity.saveWithoutId(new CompoundTag());
                    tag.merge(TagParser.parseTag(resident.get("nbt").getAsString()));
                    entity.load(tag);
                } catch (CommandSyntaxException e) {
                    ClowderHall.LOGGER.warn("Hub resident {} has bad nbt: {}", name, e.getMessage());
                }
            }
            entity.moveTo(x, y, z, 180, 0);
            entity.addTag(RESIDENT);
            for (String t : List.copyOf(entity.getTags())) if (t.startsWith(REVISION_TAG)) entity.removeTag(t);
            entity.addTag(REVISION_TAG + revision);
            if (resident.has("tags")) for (var t : resident.getAsJsonArray("tags")) entity.addTag(t.getAsString());
            entity.setInvulnerable(true);
            if (entity instanceof Mob mob) {
                mob.setNoAi(!ai);
                mob.setPersistenceRequired();
            }
            if (fresh) { level.addFreshEntity(entity); seated.put(name, entity); }
        }
    }

    /**
     * A build usually runs before the town's entities are loaded (at server start, or as the first visitor arrives),
     * so it cannot see an older copy of a resident and seats a new one. Once both copies are loaded, the one from the
     * newest revision stays and the other goes: a resident is never doubled and never lost. Cheap; runs on each visit.
     */
    public static void tidyResidents(ServerLevel level) {
        var kept = new HashMap<String, Entity>();
        for (Entity entity : level.getEntities((Entity) null, TOWN,
                e -> e.hasCustomName() && (e.getTags().contains(RESIDENT) || isRevisionOneResident(e)))) {
            String name = entity.getCustomName().getString();
            Entity other = kept.putIfAbsent(name, entity);
            if (other == null) continue;
            if (seatedRevision(entity) > seatedRevision(other)) {
                kept.put(name, entity);
                other.discard();
            } else {
                entity.discard();
            }
        }
    }

    /** Lanternweave Village (revision 1) seated named, AI-less cats and villagers without any tag. */
    private static boolean isRevisionOneResident(Entity entity) {
        return entity instanceof Mob mob && mob.isNoAi() && !mob.getTags().contains(RESIDENT)
                && (mob.getType() == EntityType.CAT || mob.getType() == EntityType.VILLAGER)
                && !(mob instanceof TamableAnimal pet && pet.getOwnerUUID() != null);
    }

    private static int seatedRevision(Entity entity) {
        if (!entity.getTags().contains(RESIDENT)) return 0;
        int revision = 1;   // tagged before residents carried their revision
        for (String t : entity.getTags()) {
            if (!t.startsWith(REVISION_TAG)) continue;
            try { revision = Math.max(revision, Integer.parseInt(t.substring(REVISION_TAG.length()))); }
            catch (NumberFormatException ignored) {}
        }
        return revision;
    }

    /** A player's things are never replaced by scenery: a stocked container, or a Yarn Basket holding death drops. */
    private static boolean holdsSomething(BlockEntity be) {
        if (be instanceof YarnBasketBlockEntity) return true;
        return be instanceof Container container && !container.isEmpty();
    }

    /** Wares on a shop wall: a fixed, invulnerable frame (survival players cannot take the item), placed once. */
    private static void placeFrame(ServerLevel level, JsonObject spec) {
        BlockPos at = pos(spec, "pos");
        Direction facing = Direction.byName(spec.get("facing").getAsString());
        var id = ResourceLocation.tryParse(spec.get("item").getAsString());
        if (facing == null || id == null || !BuiltInRegistries.ITEM.containsKey(id)) {
            ClowderHall.LOGGER.debug("Hub frame skipped: {}", spec);
            return;
        }
        for (ItemFrame existing : level.getEntitiesOfClass(ItemFrame.class, new AABB(at))) {
            if (existing.getPos().equals(at) && existing.getDirection() == facing) return;
        }
        boolean glow = spec.has("glow") && spec.get("glow").getAsBoolean();
        ItemFrame frame = glow ? new GlowItemFrame(level, at, facing) : new ItemFrame(level, at, facing);
        frame.setItem(new ItemStack(BuiltInRegistries.ITEM.get(id)), false);
        CompoundTag tag = frame.saveWithoutId(new CompoundTag());
        tag.putBoolean("Fixed", true);
        tag.putBoolean("Invulnerable", true);
        frame.load(tag);
        level.addFreshEntity(frame);
    }

    private static BlockPos pos(JsonObject o,String key) {
        var a=o.getAsJsonArray(key);return new BlockPos(a.get(0).getAsInt(),a.get(1).getAsInt(),a.get(2).getAsInt());
    }

    /** The block state for a spec like {@code minecraft:oak_stairs[facing=east]}; null when the block is not installed. */
    private static BlockState state(String spec) {
        String[] parts=spec.split("\\[",2);
        var id=ResourceLocation.parse(parts[0]);
        if (!BuiltInRegistries.BLOCK.containsKey(id)) return null;
        BlockState state=BuiltInRegistries.BLOCK.get(id).defaultBlockState();
        // A property or value another mod version renamed is dropped (the block keeps its default there), never fatal.
        if (parts.length==2) for (String pair:parts[1].replace("]","").split(",")) {
            var kv=pair.split("=");
            var property=kv.length==2 ? state.getBlock().getStateDefinition().getProperty(kv[0]) : null;
            if (property==null) { ClowderHall.LOGGER.debug("Hub town: {} has no property {}", id, pair); continue; }
            state=value(state,property,kv[1]);
        }
        return state.is(Blocks.AIR) && !id.getPath().equals("air") ? null : state;
    }
    private static <T extends Comparable<T>> BlockState value(BlockState state,Property<T> property,String value) {
        var parsed = property.getValue(value);
        return parsed.isPresent() ? state.setValue(property, parsed.get()) : state;
    }
}
