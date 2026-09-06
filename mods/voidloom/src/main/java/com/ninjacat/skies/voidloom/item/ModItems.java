package com.ninjacat.skies.voidloom.item;

import com.ninjacat.skies.voidloom.Voidloom;
import com.ninjacat.skies.voidloom.block.ModBlocks;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Tiers;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(Voidloom.MOD_ID);

    public static final DeferredItem<Item> VOID_YARN = ITEMS.registerSimpleItem("void_yarn");
    public static final DeferredItem<Item> BINDING_KNOT = ITEMS.registerSimpleItem("binding_knot");
    public static final DeferredItem<Item> THREAD_MESH_STRING = ITEMS.registerSimpleItem("thread_mesh_string");
    public static final DeferredItem<Item> THREAD_MESH_FLINT = ITEMS.registerSimpleItem("thread_mesh_flint");
    public static final DeferredItem<Item> THREAD_MESH_IRON = ITEMS.registerSimpleItem("thread_mesh_iron");

    public static final DeferredItem<SpindleHammerItem> SPINDLE_HAMMER = ITEMS.register(
            "spindle_hammer",
            () -> new SpindleHammerItem(Tiers.STONE, new Item.Properties().attributes(
                    SpindleHammerItem.createAttributes(Tiers.STONE, 1.5F, -2.8F)
            ))
    );

    public static final DeferredItem<SpindleCrookItem> SPINDLE_CROOK = ITEMS.register(
            "spindle_crook",
            () -> new SpindleCrookItem(new Item.Properties().durability(128), 4.0F)
    );

    public static final DeferredItem<BlockItem> LOOMFRAME = ITEMS.registerSimpleBlockItem("loomframe", ModBlocks.LOOMFRAME);
    public static final DeferredItem<BlockItem> TENSION_BARREL = ITEMS.registerSimpleBlockItem("tension_barrel", ModBlocks.TENSION_BARREL);

    private ModItems() {}
}
