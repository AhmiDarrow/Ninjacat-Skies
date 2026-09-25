package com.ninjacat.skies.clowder.world;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.entity.SignText;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

/** Applies the same reviewed block plan used by the native preview exporter. */
public final class TownPlan {
    private TownPlan() {}
    private record Fill(BlockPos from, BlockPos to, BlockState state) {}

    public static void build(ServerLevel level, String resource, boolean preserveCeremony) {
        JsonObject plan;
        try (var stream = TownPlan.class.getResourceAsStream(resource)) {
            if (stream == null) throw new IllegalStateException("Missing town plan " + resource);
            plan = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
        } catch (java.io.IOException e) { throw new IllegalStateException("Cannot read town plan", e); }
        // Validate the entire plan before changing the world.
        var fills = new ArrayList<Fill>();
        for (var entry : plan.getAsJsonArray("boxes")) {
            var box = entry.getAsJsonObject();
            BlockPos from = pos(box, "from"), to = pos(box, "to");
            if (from.getX()>to.getX() || from.getY()>to.getY() || from.getZ()>to.getZ()
                    || Math.abs(from.getX())>100 || Math.abs(to.getX())>100
                    || Math.abs(from.getZ())>110 || Math.abs(to.getZ())>110
                    || from.getY()<40 || to.getY()>100) throw new IllegalArgumentException("Town bounds");
            fills.add(new Fill(from, to, state(box.get("block").getAsString())));
        }
        for (var fill : fills) {
            for (BlockPos p : BlockPos.betweenClosed(fill.from(), fill.to())) {
                if (preserveCeremony && Math.abs(p.getX())<=7 && Math.abs(p.getZ())<=7 && p.getY()>=62) continue;
                // Existing player inventories are never replaced by a scenery upgrade.
                if (level.getBlockEntity(p) instanceof net.minecraft.world.Container) continue;
                level.setBlock(p, fill.state(), 2);
            }
        }
        for (var entry : plan.getAsJsonArray("signs")) {
            var sign = entry.getAsJsonObject();
            if (level.getBlockEntity(pos(sign,"pos")) instanceof SignBlockEntity be) {
                var text = new SignText().setColor(DyeColor.WHITE).setHasGlowingText(true);
                var lines = sign.getAsJsonArray("lines");
                for (int i=0;i<Math.min(4,lines.size());i++) { String line=lines.get(i).getAsString(); text=text.setMessage(i, line.isEmpty() ? Component.literal("") : Component.translatable(line)); }   // lines are lang keys
                be.setText(text,true); be.setText(text,false); be.setWaxed(true); be.setChanged();
            }
        }
        var seated = new ArrayList<String>();
        for (Mob mob : level.getEntitiesOfClass(Mob.class, new AABB(-100, 40, -110, 100, 100, 110))) {
            if (mob.hasCustomName()) seated.add(mob.getCustomName().getString());
        }
        for (var entry : plan.getAsJsonArray("residents")) {
            var resident=entry.getAsJsonObject(); var xyz=resident.getAsJsonArray("pos");
            var type=resident.get("type").getAsString().equals("cat")?EntityType.CAT:EntityType.VILLAGER;
            String name = resident.get("name").getAsString();
            if (seated.contains(name)) continue;
            var entity=type.create(level);
            if (entity != null) {
                Mob mob = entity;
                mob.moveTo(xyz.get(0).getAsDouble(), xyz.get(1).getAsDouble(), xyz.get(2).getAsDouble(), 180, 0);
                mob.setCustomName(Component.literal(name));
                mob.setCustomNameVisible(true);
                mob.setNoAi(true);
                mob.setPersistenceRequired(); seated.add(name); level.addFreshEntity(mob);
            }
        }
    }
    private static BlockPos pos(JsonObject o,String key) {
        var a=o.getAsJsonArray(key);return new BlockPos(a.get(0).getAsInt(),a.get(1).getAsInt(),a.get(2).getAsInt());
    }
    private static BlockState state(String spec) {
        String[] parts=spec.split("\\[",2);
        var id=ResourceLocation.parse(parts[0]);
        if (!BuiltInRegistries.BLOCK.containsKey(id)) throw new IllegalArgumentException(spec);
        BlockState state=BuiltInRegistries.BLOCK.get(id).defaultBlockState();
        if (parts.length==2) for (String pair:parts[1].replace("]","").split(",")) {
            var kv=pair.split("="); var property=state.getBlock().getStateDefinition().getProperty(kv[0]);
            if (property==null) throw new IllegalArgumentException(spec);
            state=value(state,property,kv[1]);
        }
        return state;
    }
    private static <T extends Comparable<T>> BlockState value(BlockState state,Property<T> property,String value) {
        return state.setValue(property,property.getValue(value).orElseThrow(()->new IllegalArgumentException(value)));
    }
}

