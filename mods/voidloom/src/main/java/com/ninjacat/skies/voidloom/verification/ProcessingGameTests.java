package com.ninjacat.skies.voidloom.verification;

import com.ninjacat.skies.voidloom.block.*;
import com.ninjacat.skies.voidloom.compat.LoomframeYield;
import com.ninjacat.skies.voidloom.item.ModItems;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.neoforged.neoforge.gametest.*;

@GameTestHolder("voidloom")
@PrefixGameTestTemplate(false)
public class ProcessingGameTests {
    private static CompoundTag outputs(GameTestHelper h, ItemStack... stacks) {
        var tag=new CompoundTag();var list=NonNullList.withSize(stacks.length,ItemStack.EMPTY);
        for(int i=0;i<stacks.length;i++) list.set(i,stacks[i]);
        ContainerHelper.saveAllItems(tag,list,h.getLevel().registryAccess());return tag;
    }
    private static void tick(GameTestHelper h, TensionBarrelBlockEntity be, int count) {
        for(int i=0;i<count;i++) TensionBarrelBlockEntity.serverTick(h.getLevel(),be.getBlockPos(),be.getBlockState(),be);
    }
    private static void tick(GameTestHelper h, LoomframeBlockEntity be, int count) {
        for(int i=0;i<count;i++) LoomframeBlockEntity.serverTick(h.getLevel(),be.getBlockPos(),be.getBlockState(),be);
    }
    @GameTest(template="empty")
    public static void barrelCombinesPartialStacks(GameTestHelper h) {
        h.setBlock(2,1,2,ModBlocks.TENSION_BARREL.get());var be=(TensionBarrelBlockEntity)h.getBlockEntity(new BlockPos(2,1,2));
        var tag=outputs(h,new ItemStack(ModItems.VOID_YARN.get(),63),new ItemStack(ModItems.VOID_YARN.get(),63),new ItemStack(Items.STONE,64));
        tag.putInt("String",1);tag.putInt("Pearls",1);be.loadWithComponents(tag,h.getLevel().registryAccess());
        tick(h,be,TensionBarrelBlockEntity.YARN_TIME);
        h.assertTrue(be.handler().getStackInSlot(1).getCount()==64 && be.handler().getStackInSlot(2).getCount()==64,"Two yarn must fit across two partial stacks");
        h.assertTrue(be.takeDryInputs().isEmpty(),"Craft must consume exactly one string and pearl");h.succeed();
    }
    @GameTest(template="empty")
    public static void barrelClampsCorruptCounters(GameTestHelper h) {
        h.setBlock(2,1,2,ModBlocks.TENSION_BARREL.get());var be=(TensionBarrelBlockEntity)h.getBlockEntity(new BlockPos(2,1,2));
        var tag=new CompoundTag();tag.putInt("Water",Integer.MAX_VALUE);tag.putInt("Dirt",-3);tag.putInt("String",Integer.MAX_VALUE);tag.putInt("Pearls",Integer.MAX_VALUE);tag.putInt("Progress",Integer.MAX_VALUE);tag.putInt("ProgressTotal",120);
        be.loadWithComponents(tag,h.getLevel().registryAccess());
        h.assertTrue(be.getWater()==8 && be.getProgress()==0,"Saved water and progress must remain bounded");
        tick(h,be,120);var dry=be.takeDryInputs();
        h.assertTrue(dry.size()==2 && dry.stream().allMatch(s->s.getCount()==7),"Dry inputs must clamp to eight and consume one each");h.succeed();
    }
    @GameTest(template="empty")
    public static void barrelBucketSimulationAndRedstone(GameTestHelper h) {
        h.setBlock(2,1,2,ModBlocks.TENSION_BARREL.get());var be=(TensionBarrelBlockEntity)h.getBlockEntity(new BlockPos(2,1,2));var handler=be.handler();
        h.assertTrue(handler.insertItem(0,new ItemStack(Items.WATER_BUCKET),true).isEmpty() && be.getWater()==0 && !be.hasOutput(),"Bucket simulation must not create water or a bucket");
        handler.insertItem(0,new ItemStack(Items.WATER_BUCKET),false);
        h.assertTrue(be.getWater()==4 && handler.getStackInSlot(1).is(Items.BUCKET),"Committed bucket must conserve its container");
        h.setBlock(3,1,2,Blocks.REDSTONE_BLOCK);
        h.assertTrue(handler.extractItem(1,1,false).isEmpty() && !handler.insertItem(0,new ItemStack(Items.WATER_BUCKET),false).isEmpty() && be.getWater()==4,"Cached automation must obey a live redstone lock");h.succeed();
    }
    @GameTest(template="empty")
    public static void barrelRefusesBucketWithoutRoomForEmpty(GameTestHelper h) {
        h.setBlock(2,1,2,ModBlocks.TENSION_BARREL.get());var be=(TensionBarrelBlockEntity)h.getBlockEntity(new BlockPos(2,1,2));var handler=be.handler();
        be.loadWithComponents(outputs(h,new ItemStack(Items.STONE,64),new ItemStack(Items.STONE,64),new ItemStack(Items.STONE,64)),h.getLevel().registryAccess());
        h.assertFalse(handler.insertItem(0,new ItemStack(Items.WATER_BUCKET),true).isEmpty(),"Simulated pour must refuse when the empty bucket has nowhere to go");
        h.assertFalse(handler.insertItem(0,new ItemStack(Items.WATER_BUCKET),false).isEmpty(),"Pour must refuse when the empty bucket has nowhere to go");
        h.assertTrue(be.getWater()==0,"Refused pour must not add water");
        h.assertItemEntityNotPresent(Items.BUCKET,new BlockPos(2,1,2),3);h.succeed();
    }
    @GameTest(template="empty")
    public static void barrelAnalogSeesTankFill(GameTestHelper h) {
        h.setBlock(2,1,2,ModBlocks.TENSION_BARREL.get());var be=(TensionBarrelBlockEntity)h.getBlockEntity(new BlockPos(2,1,2));
        h.assertTrue(be.analogSignal()==0,"An empty barrel must read 0");
        var tag=new CompoundTag();tag.putInt("Water",4);
        be.loadWithComponents(tag,h.getLevel().registryAccess());
        h.assertTrue(be.analogSignal()>0 && be.analogSignal()<15,"Tank water with no output must still read on a comparator");
        var full=outputs(h,new ItemStack(Items.CLAY_BALL,64),new ItemStack(Items.CLAY_BALL,64),new ItemStack(Items.CLAY_BALL,64));
        full.putInt("Water",0);
        be.loadWithComponents(full,h.getLevel().registryAccess());
        h.assertTrue(be.analogSignal()>=15,"Full output slots must read 15");
        h.succeed();
    }
    @GameTest(template="empty")
    public static void barrelBreakSpillsWaterWithoutContainers(GameTestHelper h) {
        h.setBlock(2,1,2,ModBlocks.TENSION_BARREL.get());var be=(TensionBarrelBlockEntity)h.getBlockEntity(new BlockPos(2,1,2));
        var tag=new CompoundTag();tag.putInt("Water",5);tag.putInt("Dirt",2);
        be.loadWithComponents(tag,h.getLevel().registryAccess());
        BlockPos pos=new BlockPos(2,1,2);
        be.dropAll(h.getLevel(), h.absolutePos(pos));
        h.assertTrue(be.getWater()==0 && be.takeDryInputs().isEmpty(),"Breaking must empty tank water and dry inputs");
        h.assertItemEntityNotPresent(Items.WATER_BUCKET, pos, 2);
        h.assertItemEntityNotPresent(Items.POTION, pos, 2);
        h.assertItemEntityPresent(Items.DIRT, pos, 2);
        h.succeed();
    }
    @GameTest(template="empty")
    public static void loomAnalogSeesGritAndMesh(GameTestHelper h) {
        h.setBlock(2,1,2,ModBlocks.LOOMFRAME.get());var be=(LoomframeBlockEntity)h.getBlockEntity(new BlockPos(2,1,2));
        h.assertTrue(be.analogSignal()==0,"An empty Loomframe must read 0");
        var tag=new CompoundTag();
        tag.put("Mesh",new ItemStack(ModItems.THREAD_MESH_STRING.get()).save(h.getLevel().registryAccess()));
        be.loadWithComponents(tag,h.getLevel().registryAccess());
        h.assertTrue(be.analogSignal()==1,"A stretched mesh with no grit must read 1");
        tag.put("Input",new ItemStack(Items.DIRT,64).save(h.getLevel().registryAccess()));
        be.loadWithComponents(tag,h.getLevel().registryAccess());
        h.assertTrue(be.analogSignal()>=7 && be.analogSignal()<15,"Full grit with no scraps must read in the grit band");
        h.succeed();
    }
    @GameTest(template="empty")
    public static void loomPendingSurvivesReloadAndLock(GameTestHelper h) {
        h.setBlock(2,1,2,ModBlocks.LOOMFRAME.get());var be=(LoomframeBlockEntity)h.getBlockEntity(new BlockPos(2,1,2));
        var tag=outputs(h,new ItemStack(Items.DIAMOND,64),new ItemStack(Items.DIAMOND,64),new ItemStack(Items.DIAMOND,64),new ItemStack(Items.DIAMOND,64));
        tag.put("Pending",outputs(h,new ItemStack(Items.FLINT,3),new ItemStack(Items.CLAY_BALL,4),new ItemStack(Items.IRON_NUGGET,5)));
        tag.put("Mesh",new ItemStack(ModItems.THREAD_MESH_STRING.get()).save(h.getLevel().registryAccess()));tag.put("Input",new ItemStack(Items.DIRT,2).save(h.getLevel().registryAccess()));
        be.loadWithComponents(tag,h.getLevel().registryAccess());tick(h,be,500);
        h.assertTrue(be.getInput().getCount()==2,"Blocked pending batch must not consume or reroll another input");
        var saved=be.saveWithoutMetadata(h.getLevel().registryAccess());be.clearContent();be.loadWithComponents(saved,h.getLevel().registryAccess());be.takeAllOutput();
        h.setBlock(3,1,2,Blocks.REDSTONE_BLOCK);tick(h,be,100);
        h.assertFalse(be.hasOutput(),"Redstone must also lock pending output delivery");h.setBlock(3,1,2,Blocks.AIR);tick(h,be,1);
        h.assertTrue(be.takeAllOutput().stream().mapToInt(ItemStack::getCount).sum()==12 && be.getInput().getCount()==2,"Reloaded pending batch must deliver every item exactly once");
        h.assertTrue(be.drainForDrop().stream().mapToInt(ItemStack::getCount).sum()==3,"Breaking after delivery must not duplicate pending items");h.succeed();
    }
    @GameTest(template="empty")
    public static void loomFullOutputCannotDiscardRolls(GameTestHelper h) {
        h.setBlock(2,1,2,ModBlocks.LOOMFRAME.get());var be=(LoomframeBlockEntity)h.getBlockEntity(new BlockPos(2,1,2));
        var tag=outputs(h,new ItemStack(Items.DIAMOND,64),new ItemStack(Items.DIAMOND,64),new ItemStack(Items.DIAMOND,64),new ItemStack(Items.DIAMOND,64));
        tag.put("Mesh",new ItemStack(ModItems.THREAD_MESH_STRING.get()).save(h.getLevel().registryAccess()));tag.put("Input",new ItemStack(Items.DIRT,64).save(h.getLevel().registryAccess()));
        be.loadWithComponents(tag,h.getLevel().registryAccess());h.getLevel().random.setSeed(4096);tick(h,be,1000);
        var saved=be.saveWithoutMetadata(h.getLevel().registryAccess());
        h.assertFalse(saved.getCompound("Pending").getList("Items",10).isEmpty(),"A full machine must retain its paid random roll");
        int remaining=be.getInput().getCount();h.assertTrue(remaining>0 && remaining<64,"Machine must pay for a batch and then pause");tick(h,be,1000);
        h.assertTrue(be.getInput().getCount()==remaining,"Backpressure must not reroll or burn more input");
        int count=be.drainForDrop().stream().mapToInt(ItemStack::getCount).sum();h.assertTrue(count>257+remaining,"Breaking must recover mesh, input, full outputs and paid pending loot");
        h.assertTrue(be.drainForDrop().isEmpty(),"Repeated drain must not duplicate drops");h.succeed();
    }
    @GameTest(template="empty")
    public static void loomframeYieldIsEightyPercent(GameTestHelper h) {
        var rand = net.minecraft.util.RandomSource.create(1L);
        int kept = 0;
        for (int i = 0; i < 10000; i++) kept += LoomframeYield.scale(1, rand);
        h.assertTrue(kept > 7700 && kept < 8300, "Automated yield keeps ~80% of a sieve count");
        h.assertTrue(LoomframeYield.scale(0, rand) == 0, "A miss stays a miss");
        h.succeed();
    }
    @GameTest(template="empty")
    public static void loomHopperInsertAndExtract(GameTestHelper h) {
        h.setBlock(2,1,2,ModBlocks.LOOMFRAME.get());
        var be = (LoomframeBlockEntity) h.getBlockEntity(new BlockPos(2,1,2));
        var tag = outputs(h, new ItemStack(Items.FLINT, 4));
        tag.put("Mesh", new ItemStack(ModItems.THREAD_MESH_STRING.get()).save(h.getLevel().registryAccess()));
        be.loadWithComponents(tag, h.getLevel().registryAccess());
        h.assertTrue(LoomframeBlockEntity.isSiftable(new ItemStack(Items.DIRT))
                && LoomframeBlockEntity.isSiftable(new ItemStack(Items.SAND))
                && LoomframeBlockEntity.isSiftable(new ItemStack(Items.GRAVEL)),
                "Loomframe must accept dirt, sand and gravel");
        h.assertTrue(be.handler().insertItem(0, new ItemStack(Items.DIRT, 8), false).isEmpty() && be.getInput().getCount() == 8, "Hopper above inserts grit");
        h.assertTrue(be.handler().extractItem(0, 8, false).isEmpty() && be.getInput().getCount() == 8, "Hopper must not steal grit");
        h.assertTrue(be.handler().extractItem(1, 2, false).getCount() == 2, "Hopper below pulls scraps");
        h.assertTrue(!be.handler().insertItem(1, new ItemStack(Items.DIRT), false).isEmpty(), "Hopper cannot push into scrap slots");
        h.succeed();
    }
    @GameTest(template="empty")
    public static void loomframeAndBarrelDropThemselves(GameTestHelper h) {
        h.assertFalse(ModBlocks.LOOMFRAME.get().defaultBlockState().requiresCorrectToolForDrops(), "Loomframe must drop by hand");
        h.assertFalse(ModBlocks.TENSION_BARREL.get().defaultBlockState().requiresCorrectToolForDrops(), "Tension Barrel must drop by hand");
        h.succeed();
    }
}
