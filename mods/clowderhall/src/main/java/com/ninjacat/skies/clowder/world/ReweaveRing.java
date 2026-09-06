package com.ninjacat.skies.clowder.world;

import com.ninjacat.skies.clowder.ClowderHall;
import com.ninjacat.skies.core.tension.Clowder;
import com.ninjacat.skies.core.tension.LoomTension;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.entity.SignText;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

/**
 * The Hall brightens as the server reweaves: twelve pillars ring the ceremony pad, one lit sea lantern
 * and a name plaque per Clowder that has seated its Fragment. Refreshed every time someone enters the Hall.
 */
public final class ReweaveRing {
    /** (dx, dz) around the pad centre, all at radius ~6, clear of the path, banners, and the arrival apron. */
    private static final int[][] SPOTS = {
            {6, -4}, {6, -1}, {6, 2}, {6, 5},
            {-6, -4}, {-6, -1}, {-6, 2}, {-6, 5},
            {3, -6}, {-3, -6}, {3, 6}, {-3, 6},
    };

    private ReweaveRing() {}

    public static void refresh(ServerLevel hall, BlockPos padCenter) {
        List<Clowder> rewoven = new ArrayList<>();
        for (Clowder c : LoomTension.allClowders(hall.getServer())) {
            if (LoomTension.isRewoven(c)) {
                rewoven.add(c);
            }
        }
        rewoven.sort(Comparator.comparing(c -> c.name().getString()));

        for (int i = 0; i < SPOTS.length; i++) {
            int dx = SPOTS[i][0];
            int dz = SPOTS[i][1];
            BlockPos pillar = padCenter.offset(dx, 1, dz);
            BlockPos cap = pillar.above();
            boolean lit = i < rewoven.size();

            hall.setBlockAndUpdate(pillar, Blocks.POLISHED_DEEPSLATE.defaultBlockState());
            hall.setBlockAndUpdate(cap, lit ? Blocks.SEA_LANTERN.defaultBlockState() : Blocks.POLISHED_DEEPSLATE_SLAB.defaultBlockState());

            // Name plaque on the inward face.
            Direction inward = Math.abs(dx) == 6 ? (dx > 0 ? Direction.WEST : Direction.EAST) : (dz > 0 ? Direction.NORTH : Direction.SOUTH);
            BlockPos signPos = pillar.relative(inward);
            if (lit) {
                hall.setBlockAndUpdate(signPos, Blocks.OAK_WALL_SIGN.defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, inward));
                if (hall.getBlockEntity(signPos) instanceof SignBlockEntity sign) {
                    String name = rewoven.get(i).name().getString();
                    if (name.length() > 15) {
                        name = name.substring(0, 15);
                    }
                    SignText text = new SignText()
                            .setColor(DyeColor.CYAN)
                            .setHasGlowingText(true)
                            .setMessage(0, Component.literal("Rewoven"))
                            .setMessage(1, Component.literal(name))
                            .setMessage(2, Component.literal("nine Strands"))
                            .setMessage(3, Component.literal("one thread"));
                    sign.setText(text, true);
                    sign.setText(text, false);
                }
            } else if (hall.getBlockState(signPos).is(Blocks.OAK_WALL_SIGN)) {
                hall.setBlockAndUpdate(signPos, Blocks.AIR.defaultBlockState());
            }
        }
        if (!rewoven.isEmpty()) {
            ClowderHall.LOGGER.debug("Reweave ring: {} lit", rewoven.size());
        }
    }
}
