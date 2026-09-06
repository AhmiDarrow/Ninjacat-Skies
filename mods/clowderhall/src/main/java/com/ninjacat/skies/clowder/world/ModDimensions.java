package com.ninjacat.skies.clowder.world;

import com.ninjacat.skies.clowder.ClowderHall;
import com.ninjacat.skies.clowder.item.ModItems;
import com.ninjacat.skies.lib.NinjacatText;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import net.minecraft.network.chat.TextColor;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.Filterable;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.WrittenBookContent;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.entity.LecternBlockEntity;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.entity.SignText;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.RotationSegment;
import net.minecraft.world.level.portal.DimensionTransition;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/**
 * Clowder Hall hub dimension travel. Overworld skyblock islands are untouched —
 * this is a separate void dimension with a Java-built ceremony pad.
 */
public final class ModDimensions {
    public static final ResourceKey<Level> CLOWDER_HALL = ResourceKey.create(
            Registries.DIMENSION,
            ResourceLocation.fromNamespaceAndPath(ClowderHall.MOD_ID, "clowder_hall")
    );

    private static final String ROOT = ClowderHall.MOD_ID;
    private static final String RETURN_TAG = "hub_return";
    private static final BlockPos MARKER_POS = new BlockPos(0, 62, 0);
    private static final BlockPos PAD_CENTER = new BlockPos(0, 63, 0);
    private static final int PAD_RADIUS = 7;

    private ModDimensions() {}

    public static boolean travelToHub(ServerPlayer player) {
        ServerLevel hub = player.server.getLevel(CLOWDER_HALL);
        if (hub == null) {
            player.displayClientMessage(msg("message.clowderhall.hub_missing", NinjacatText.TEAL), false);
            ClowderHall.LOGGER.warn("Dimension {} is not loaded", CLOWDER_HALL.location());
            return false;
        }

        if (player.level().dimension().equals(CLOWDER_HALL)) {
            ensureHubHall(hub);
            player.displayClientMessage(msg("message.clowderhall.hub_already", NinjacatText.GOLD), true);
            return true;
        }

        storeReturnPoint(player);
        ensureHubHall(hub);

        // South apron, facing the beacon (north).
        double x = 0.5;
        double y = 65.0;
        double z = 5.5;
        player.changeDimension(new DimensionTransition(
                hub,
                new Vec3(x, y, z),
                Vec3.ZERO,
                180.0F,
                0.0F,
                DimensionTransition.DO_NOTHING
        ));
        player.displayClientMessage(msg("message.clowderhall.hub_arrive", NinjacatText.TEAL), true);
        return true;
    }

    public static boolean returnFromHub(ServerPlayer player) {
        if (!player.level().dimension().equals(CLOWDER_HALL)) {
            player.displayClientMessage(msg("message.clowderhall.hub_return_not_in_hall", NinjacatText.GOLD), false);
            return false;
        }

        CompoundTag root = player.getPersistentData().getCompound(ROOT);
        if (!root.contains(RETURN_TAG)) {
            return teleportOverworldSpawn(player);
        }

        CompoundTag ret = root.getCompound(RETURN_TAG);
        ResourceLocation dimId = ResourceLocation.tryParse(ret.getString("dim"));
        if (dimId == null) {
            return teleportOverworldSpawn(player);
        }

        ResourceKey<Level> key = ResourceKey.create(Registries.DIMENSION, dimId);
        ServerLevel target = player.server.getLevel(key);
        if (target == null) {
            return teleportOverworldSpawn(player);
        }

        double x = ret.getDouble("x");
        double y = ret.getDouble("y");
        double z = ret.getDouble("z");
        float yaw = ret.getFloat("yaw");
        float pitch = ret.getFloat("pitch");

        BlockPos feet = BlockPos.containing(x, y, z);
        ensureLandingClearance(target, feet);

        player.changeDimension(new DimensionTransition(
                target,
                new Vec3(x, y, z),
                Vec3.ZERO,
                yaw,
                pitch,
                DimensionTransition.DO_NOTHING
        ));
        player.displayClientMessage(msg("message.clowderhall.hub_return", NinjacatText.TEAL), true);
        return true;
    }

    /** Builds the ceremony hall once (marker = reinforced deepslate under pad center). */
    public static void ensureHubHall(ServerLevel level) {
        if (!level.getBlockState(MARKER_POS).is(Blocks.REINFORCED_DEEPSLATE)
                && !level.getBlockState(PAD_CENTER).isAir()) {
            // Something already occupies the pad without our marker — leave it alone.
            return;
        }
        if (level.getBlockState(MARKER_POS).is(Blocks.REINFORCED_DEEPSLATE)) {
            return;
        }

        // Marker + deepslate underlayer + cyan terracotta / deepslate pad (~15x15).
        level.setBlockAndUpdate(MARKER_POS, Blocks.REINFORCED_DEEPSLATE.defaultBlockState());
        for (int dx = -PAD_RADIUS; dx <= PAD_RADIUS; dx++) {
            for (int dz = -PAD_RADIUS; dz <= PAD_RADIUS; dz++) {
                BlockPos under = PAD_CENTER.offset(dx, -1, dz);
                BlockPos surface = PAD_CENTER.offset(dx, 0, dz);
                if (!under.equals(MARKER_POS)) {
                    level.setBlockAndUpdate(under, Blocks.DEEPSLATE.defaultBlockState());
                }
                boolean path = dx == 0 && dz >= -5 && dz <= 4;
                BlockState top = path
                        ? Blocks.POLISHED_DEEPSLATE.defaultBlockState()
                        : Blocks.CYAN_TERRACOTTA.defaultBlockState();
                level.setBlockAndUpdate(surface, top);
                clearColumn(level, surface.above(), 4);
            }
        }

        // Corner posts + lantern caps.
        for (int dx : new int[]{-PAD_RADIUS, PAD_RADIUS}) {
            for (int dz : new int[]{-PAD_RADIUS, PAD_RADIUS}) {
                BlockPos base = PAD_CENTER.offset(dx, 1, dz);
                level.setBlockAndUpdate(base, Blocks.DARK_OAK_LOG.defaultBlockState());
                level.setBlockAndUpdate(base.above(), Blocks.DARK_OAK_LOG.defaultBlockState());
                level.setBlockAndUpdate(base.above(2), Blocks.LANTERN.defaultBlockState());
            }
        }

        // Iron / beacon frame toward north (negative Z).
        for (int dx = -1; dx <= 1; dx++) {
            for (int dz = -5; dz <= -3; dz++) {
                level.setBlockAndUpdate(PAD_CENTER.offset(dx, 1, dz), Blocks.IRON_BLOCK.defaultBlockState());
            }
        }
        level.setBlockAndUpdate(PAD_CENTER.offset(0, 2, -4), Blocks.BEACON.defaultBlockState());

        // Carpet accents flanking the path.
        level.setBlockAndUpdate(PAD_CENTER.offset(-1, 1, -2), Blocks.CYAN_CARPET.defaultBlockState());
        level.setBlockAndUpdate(PAD_CENTER.offset(1, 1, -2), Blocks.CYAN_CARPET.defaultBlockState());
        level.setBlockAndUpdate(PAD_CENTER.offset(-1, 1, -1), Blocks.WHITE_CARPET.defaultBlockState());
        level.setBlockAndUpdate(PAD_CENTER.offset(1, 1, -1), Blocks.WHITE_CARPET.defaultBlockState());

        // Four banner posts (mid-sides).
        placeBannerPost(level, PAD_CENTER.offset(-5, 1, 0), Blocks.CYAN_BANNER.defaultBlockState()
                .setValue(BlockStateProperties.ROTATION_16, RotationSegment.convertToSegment(Direction.WEST)));
        placeBannerPost(level, PAD_CENTER.offset(5, 1, 0), Blocks.WHITE_BANNER.defaultBlockState()
                .setValue(BlockStateProperties.ROTATION_16, RotationSegment.convertToSegment(Direction.EAST)));
        placeBannerPost(level, PAD_CENTER.offset(-4, 1, 4), Blocks.CYAN_BANNER.defaultBlockState()
                .setValue(BlockStateProperties.ROTATION_16, RotationSegment.convertToSegment(Direction.SOUTH)));
        placeBannerPost(level, PAD_CENTER.offset(4, 1, 4), Blocks.WHITE_BANNER.defaultBlockState()
                .setValue(BlockStateProperties.ROTATION_16, RotationSegment.convertToSegment(Direction.SOUTH)));

        // Sea lanterns.
        level.setBlockAndUpdate(PAD_CENTER.offset(-2, 1, 1), Blocks.SEA_LANTERN.defaultBlockState());
        level.setBlockAndUpdate(PAD_CENTER.offset(2, 1, 1), Blocks.SEA_LANTERN.defaultBlockState());
        level.setBlockAndUpdate(PAD_CENTER.offset(0, 1, -6), Blocks.SEA_LANTERN.defaultBlockState());

        // Lectern with welcome book (facing south toward arrivals).
        BlockPos lecternPos = PAD_CENTER.offset(0, 1, 1);
        level.setBlockAndUpdate(
                lecternPos,
                Blocks.LECTERN.defaultBlockState()
                        .setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.SOUTH)
                        .setValue(BlockStateProperties.HAS_BOOK, true)
        );
        if (level.getBlockEntity(lecternPos) instanceof LecternBlockEntity lectern) {
            lectern.setBook(createHallBook());
        }

        // Ceremony chest — align with Dock / pad kits when empty.
        BlockPos chestPos = PAD_CENTER.offset(1, 1, 1);
        level.setBlockAndUpdate(
                chestPos,
                Blocks.CHEST.defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.SOUTH)
        );
        if (level.getBlockEntity(chestPos) instanceof ChestBlockEntity chest && chest.isEmpty()) {
            chest.setItem(0, new ItemStack(com.ninjacat.skies.core.item.ModItems.WHISKER_CODEX.get()));
            chest.setItem(1, new ItemStack(ModItems.ISLAND_CHARTER.get()));
            chest.setItem(2, new ItemStack(ModItems.HUB_KEY.get()));
            chest.setItem(3, createHowToStartBook());
            chest.setItem(4, new ItemStack(Items.BREAD, 8));
            chest.setItem(5, new ItemStack(Items.TORCH, 8));
            chest.setItem(6, new ItemStack(com.ninjacat.skies.core.item.ModItems.FRAYED_THREAD.get(), 4));
        }

        // Glow plaques.
        BlockPos standSign = PAD_CENTER.offset(0, 1, 2);
        level.setBlockAndUpdate(
                standSign,
                Blocks.OAK_SIGN.defaultBlockState()
                        .setValue(BlockStateProperties.ROTATION_16, RotationSegment.convertToSegment(Direction.SOUTH))
        );
        writeSign(level, standSign, new String[]{
                "Clowder Hall",
                "Nine Strands",
                "One Loom",
                "— Ninjacats —"
        }, DyeColor.CYAN);

        BlockPos post = PAD_CENTER.offset(0, 1, -2);
        level.setBlockAndUpdate(post, Blocks.DARK_OAK_LOG.defaultBlockState());
        BlockPos wallSign = PAD_CENTER.offset(0, 1, -1);
        level.setBlockAndUpdate(
                wallSign,
                Blocks.OAK_WALL_SIGN.defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING, Direction.SOUTH)
        );
        writeSign(level, wallSign, new String[]{
                "Welcome,",
                "Skybound.",
                "Claim a pad.",
                "Reweave."
        }, DyeColor.WHITE);

        ClowderHall.LOGGER.info("Clowder Hall ceremony pad raised at {}", PAD_CENTER);
    }

    private static void placeBannerPost(ServerLevel level, BlockPos base, BlockState banner) {
        level.setBlockAndUpdate(base, Blocks.DARK_OAK_FENCE.defaultBlockState());
        level.setBlockAndUpdate(base.above(), banner);
    }

    private static void writeSign(ServerLevel level, BlockPos pos, String[] lines, DyeColor color) {
        if (!(level.getBlockEntity(pos) instanceof SignBlockEntity sign)) {
            return;
        }
        SignText text = new SignText();
        for (int i = 0; i < 4; i++) {
            String line = i < lines.length ? lines[i] : "";
            text = text.setMessage(i, Component.literal(line));
        }
        text = text.setColor(color).setHasGlowingText(true);
        sign.setText(text, true);
        sign.setWaxed(true);
    }

    private static ItemStack createHallBook() {
        List<Filterable<Component>> pages = List.of(
                Filterable.passThrough(Component.literal(
                        "Clowder Hall\n\n" +
                                "Teams are Clowders.\n" +
                                "Pads are claimed, not owned forever.\n" +
                                "The Loom still listens."
                )),
                Filterable.passThrough(Component.literal(
                        "Hall rules\n\n" +
                                "1. Share the hub.\n" +
                                "2. Claim a pad via Skyblock / Charter.\n" +
                                "3. Pull Strands; do not skip Soil.\n" +
                                "4. Frayed Thread buys help, not shortcuts past the braid."
                )),
                Filterable.passThrough(Component.literal(
                        "Begin\n\n" +
                                "/clowder help\n" +
                                "Hub Key toggles leave Hall.\n" +
                                "/clowder revive (self) or <mate>\n\n" +
                                "Create Team is Dock-only:\n" +
                                "return to Clowder Dock, then\n" +
                                "right-click Island Charter (or C)."
                ))
        );
        WrittenBookContent content = new WrittenBookContent(
                Filterable.passThrough("Clowder Hall"),
                "Ninjacats",
                0,
                pages,
                true
        );
        ItemStack book = new ItemStack(Items.WRITTEN_BOOK);
        book.set(DataComponents.WRITTEN_BOOK_CONTENT, content);
        return book;
    }

    private static ItemStack createHowToStartBook() {
        // Keep Recover / kit copy aligned with starter_book.js v4 + _gen_islands howto.
        List<Filterable<Component>> pages = List.of(
                Filterable.passThrough(Component.literal(
                        "HOW TO START (read me)\n\n" +
                                "You are in Clowder Hall or on Dock — not your forever island.\n\n" +
                                "Goal: open Create Team on the Dock, pick a pad, then open quests."
                )),
                Filterable.passThrough(Component.literal(
                        "CLAIM A PAD\n\n" +
                                "1) Leave Hall (Hub Key / /clowder return)\n" +
                                "2) On Clowder Dock: Island Charter (or C)\n" +
                                "3) Create Team → name your Clowder\n" +
                                "4) Pick a pad:\n" +
                                "   Ninjacat Pad = Normal\n" +
                                "   Dojo Cottage = Easy\n" +
                                "   Frayed Thread = Hard\n" +
                                "5) Open FTB Quests — start Soil.\n\n" +
                                "Create Team is Dock-only."
                )),
                Filterable.passThrough(Component.literal(
                        "QUESTS / RECOVER\n\n" +
                                "Easy ships water already.\n" +
                                "Normal/Hard: ice + lava + empty bucket.\n\n" +
                                "1) Unravel Thread → 3 string\n" +
                                "2) Craft 4 string → 2 Void Yarn\n" +
                                "3) Spindle Hammer = cobble + sticks\n" +
                                "4) Tension Barrel: water+dirt → clay\n" +
                                "   (empty bucket returns to you)\n" +
                                "5) Porcelain clay → porcelain bucket\n" +
                                "6) Sieve grit; slime = dirt+seeds+meal"
                )),
                Filterable.passThrough(Component.literal(
                        "SOFT HARDCORE\n\n" +
                                "If lives are on and you go spectator:\n" +
                                "• /clowder revive (self)\n" +
                                "• Mate: /clowder revive <you>\n" +
                                "• Op: /skybound revive [player]\n\n" +
                                "Hub Key toggles Hall enter/leave.\n" +
                                "Charter seals spawn on solid pad ground."
                ))
        );
        WrittenBookContent content = new WrittenBookContent(
                Filterable.passThrough("How to Start"),
                "Skybound Field Desk",
                0,
                pages,
                true
        );
        ItemStack book = new ItemStack(Items.WRITTEN_BOOK);
        book.set(DataComponents.WRITTEN_BOOK_CONTENT, content);
        return book;
    }

    private static void clearColumn(ServerLevel level, BlockPos start, int height) {
        for (int i = 0; i < height; i++) {
            BlockPos p = start.above(i);
            BlockState state = level.getBlockState(p);
            if (!state.isAir() && (state.canBeReplaced() || state.blocksMotion() || !state.getCollisionShape(level, p).isEmpty())) {
                level.setBlockAndUpdate(p, Blocks.AIR.defaultBlockState());
            }
        }
    }

    private static void ensureLandingClearance(ServerLevel level, BlockPos feet) {
        BlockPos ground = feet.below();
        if (!level.getBlockState(ground).blocksMotion()) {
            level.setBlockAndUpdate(ground, Blocks.STONE.defaultBlockState());
        }
        clearColumn(level, feet, 2);
    }

    private static void storeReturnPoint(ServerPlayer player) {
        CompoundTag root = player.getPersistentData().getCompound(ROOT);
        CompoundTag ret = new CompoundTag();
        ret.putString("dim", player.level().dimension().location().toString());
        ret.putDouble("x", player.getX());
        ret.putDouble("y", player.getY());
        ret.putDouble("z", player.getZ());
        ret.putFloat("yaw", player.getYRot());
        ret.putFloat("pitch", player.getXRot());
        root.put(RETURN_TAG, ret);
        player.getPersistentData().put(ROOT, root);
    }

    private static boolean teleportOverworldSpawn(ServerPlayer player) {
        ServerLevel overworld = player.server.getLevel(Level.OVERWORLD);
        if (overworld == null) {
            player.displayClientMessage(msg("message.clowderhall.hub_return_fail", NinjacatText.TEAL), false);
            return false;
        }
        BlockPos spawn = overworld.getSharedSpawnPos();
        ensureLandingClearance(overworld, spawn);
        player.changeDimension(new DimensionTransition(
                overworld,
                new Vec3(spawn.getX() + 0.5, spawn.getY(), spawn.getZ() + 0.5),
                Vec3.ZERO,
                overworld.getSharedSpawnAngle(),
                0.0F,
                DimensionTransition.DO_NOTHING
        ));
        player.displayClientMessage(msg("message.clowderhall.hub_return_spawn", NinjacatText.GOLD), true);
        return true;
    }

    private static Component msg(String key, int rgb) {
        return Component.translatable(key).withStyle(Style.EMPTY.withColor(TextColor.fromRgb(rgb)));
    }
}
