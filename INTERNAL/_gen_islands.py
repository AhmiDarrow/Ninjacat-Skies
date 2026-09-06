"""Generate original Ninjacat Skies island structure NBTs for Skyblock Builder."""
from pathlib import Path
import json
from nbtlib import File, Compound, List, Int, Byte, String

DATA_VERSION = 3955  # Minecraft 1.21.1
_REPO = Path(__file__).resolve().parents[1]
OUT_CFG = _REPO / "pack" / "overrides" / "config" / "skyblockbuilder" / "templates" / "islands"
OUT_MIRROR = _REPO / "pack" / "overrides" / "structures" / "islands"


def block(name, props=None):
    c = Compound({"Name": String(name)})
    if props:
        c["Properties"] = Compound({k: String(v) for k, v in props.items()})
    return c


def pos(x, y, z):
    return List[Int]([Int(x), Int(y), Int(z)])


def blk(x, y, z, state, nbt=None):
    c = Compound({"pos": pos(x, y, z), "state": Int(state)})
    if nbt is not None:
        c["nbt"] = nbt
    return c


def item_stack(slot, item_id, count):
    return Compound({"Slot": Byte(slot), "id": String(item_id), "count": Int(count)})


def written_book_item(slot, title, author, pages):
    """1.21 component-format written book for structure chests / lecterns."""
    page_list = []
    for page in pages:
        if isinstance(page, str):
            page = {"text": page}
        page_list.append(Compound({"raw": String(json.dumps(page, separators=(",", ":")))}))
    return Compound({
        "Slot": Byte(slot),
        "id": String("minecraft:written_book"),
        "count": Int(1),
        "components": Compound({
            "minecraft:written_book_content": Compound({
                "title": String(title),
                "author": String(author),
                "generation": Int(0),
                "resolved": Byte(1),
                "pages": List[Compound](page_list),
            })
        }),
    })


def chest_nbt(items):
    return Compound({"id": String("minecraft:chest"), "Items": List[Compound](items)})


def save_structure(path: Path, size, palette, blocks):
    root = File({
        "size": List[Int]([Int(size[0]), Int(size[1]), Int(size[2])]),
        "palette": List[Compound](palette),
        "blocks": List[Compound](blocks),
        "entities": List[Compound]([]),
        "DataVersion": Int(DATA_VERSION),
    })
    path.parent.mkdir(parents=True, exist_ok=True)
    root.save(str(path), gzipped=True)
    print(f"wrote {path} ({path.stat().st_size} bytes, {len(blocks)} blocks)")


def make_normal():
    # ~9x9 pad with corner posts, fence edge, light, crafting, modest chest
    sx, sy, sz = 9, 4, 9
    palette = [
        block("minecraft:dirt"),
        block("minecraft:grass_block", {"snowy": "false"}),
        block("minecraft:oak_sapling", {"stage": "0"}),
        block("minecraft:chest", {"facing": "south", "type": "single", "waterlogged": "false"}),
        block("minecraft:oak_log", {"axis": "y"}),
        block("minecraft:crafting_table"),
        block("minecraft:oak_fence", {
            "east": "true", "north": "false", "south": "false", "west": "true", "waterlogged": "false"
        }),
        block("minecraft:oak_fence", {
            "east": "true", "north": "false", "south": "false", "west": "false", "waterlogged": "false"
        }),
        block("minecraft:oak_fence", {
            "east": "false", "north": "false", "south": "false", "west": "true", "waterlogged": "false"
        }),
        block("minecraft:lantern", {"hanging": "false", "waterlogged": "false"}),
    ]
    blocks = []
    for x in range(sx):
        for z in range(sz):
            blocks.append(blk(x, 0, z, 0))
            blocks.append(blk(x, 1, z, 1))
    # Corner posts
    for x, z in ((0, 0), (0, 8), (8, 0), (8, 8)):
        blocks.append(blk(x, 2, z, 4))
    # Short fence along north edge (z=0), between posts
    blocks.append(blk(1, 2, 0, 7))
    blocks.append(blk(2, 2, 0, 6))
    blocks.append(blk(3, 2, 0, 6))
    blocks.append(blk(4, 2, 0, 6))
    blocks.append(blk(5, 2, 0, 6))
    blocks.append(blk(6, 2, 0, 6))
    blocks.append(blk(7, 2, 0, 8))
    blocks.append(blk(4, 2, 4, 2))  # sapling
    blocks.append(blk(3, 2, 4, 5))  # crafting table
    blocks.append(blk(5, 2, 3, 9))  # lantern
    normal_items = [
        item_stack(0, "minecraft:bread", 8),
        item_stack(1, "minecraft:oak_sapling", 1),
        item_stack(2, "minecraft:bone_meal", 4),
        item_stack(3, "minecraft:oak_log", 8),
        item_stack(4, "minecraft:ice", 2),
        item_stack(5, "minecraft:lava_bucket", 1),
        # Empty bucket — melt ice → fill → Tension Barrel clay (lava alone is not enough).
        item_stack(6, "minecraft:bucket", 1),
        item_stack(7, "voidloom:void_yarn", 2),
        item_stack(8, "ninjacatskies:frayed_thread", 6),
        # clearInitialInventory wipes the login kit — restore Codex after claim.
        item_stack(9, "ninjacatskies:whisker_codex", 1),
        item_stack(10, "clowderhall:island_charter", 1),
        item_stack(11, "clowderhall:hub_key", 1),
        written_book_item(12, "How to Start", "Skybound Field Desk", starter_howto_pages()),
    ]
    blocks.append(blk(4, 2, 6, 3, chest_nbt(normal_items)))
    # Spawn near south edge, centered on 9-wide pad
    return (sx, sy, sz), palette, blocks, {"south": [[4, 2, 1]]}


def make_easy():
    # 11x11 pad + cottage with slab roof, windows, bed, lantern, flower pot
    sx, sy, sz = 11, 6, 11
    palette = [
        block("minecraft:dirt"),  # 0
        block("minecraft:grass_block", {"snowy": "false"}),  # 1
        block("minecraft:cobblestone"),  # 2
        block("minecraft:oak_planks"),  # 3
        block("minecraft:oak_log", {"axis": "y"}),  # 4
        block("minecraft:oak_sapling", {"stage": "0"}),  # 5
        block("minecraft:chest", {"facing": "south", "type": "single", "waterlogged": "false"}),  # 6
        block("minecraft:crafting_table"),  # 7
        block("minecraft:oak_door", {"facing": "south", "half": "lower", "hinge": "left", "open": "false", "powered": "false"}),  # 8
        block("minecraft:oak_door", {"facing": "south", "half": "upper", "hinge": "left", "open": "false", "powered": "false"}),  # 9
        block("minecraft:oak_slab", {"type": "bottom", "waterlogged": "false"}),  # 10
        block("minecraft:glass_pane", {
            "east": "true", "north": "false", "south": "false", "west": "true", "waterlogged": "false"
        }),  # 11 east-west wall pane
        block("minecraft:glass_pane", {
            "east": "false", "north": "true", "south": "true", "west": "false", "waterlogged": "false"
        }),  # 12 north-south wall pane
        block("minecraft:white_bed", {"facing": "east", "occupied": "false", "part": "foot"}),  # 13
        block("minecraft:white_bed", {"facing": "east", "occupied": "false", "part": "head"}),  # 14
        block("minecraft:lantern", {"hanging": "false", "waterlogged": "false"}),  # 15
        block("minecraft:potted_poppy"),  # 16
        block("minecraft:torch"),  # 17
    ]
    blocks = []
    x0, x1, z0, z1 = 3, 7, 3, 7
    for x in range(sx):
        for z in range(sz):
            blocks.append(blk(x, 0, z, 0))
            inside = (x0 < x < x1) and (z0 < z < z1)
            blocks.append(blk(x, 1, z, 3 if inside else 1))
    for y in (2, 3):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                on_edge = x in (x0, x1) or z in (z0, z1)
                if not on_edge:
                    continue
                if z == z1 and x == 5:
                    continue  # door gap
                # Windows at mid-wall (y=3)
                if y == 3:
                    if z in (z0, z1) and x in (4, 6):
                        blocks.append(blk(x, y, z, 11))
                        continue
                    if x in (x0, x1) and z in (4, 6):
                        blocks.append(blk(x, y, z, 12))
                        continue
                is_corner = x in (x0, x1) and z in (z0, z1)
                blocks.append(blk(x, y, z, 4 if is_corner else 2))
    # Door
    blocks.append(blk(5, 2, z1, 8))
    blocks.append(blk(5, 3, z1, 9))
    # Oak slab roof
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            blocks.append(blk(x, 4, z, 10))
    # Exterior sapling, interior furniture
    blocks.append(blk(9, 2, 5, 5))
    blocks.append(blk(4, 2, 4, 7))  # crafting table
    blocks.append(blk(5, 2, 4, 13))  # bed foot
    blocks.append(blk(6, 2, 4, 14))  # bed head (facing east)
    blocks.append(blk(5, 2, 5, 15))  # lantern
    blocks.append(blk(4, 2, 6, 16))  # flower pot
    blocks.append(blk(6, 2, 6, 17))  # torch
    easy_items = [
        item_stack(0, "minecraft:bread", 16),
        item_stack(1, "minecraft:apple", 8),
        item_stack(2, "minecraft:oak_sapling", 4),
        item_stack(3, "minecraft:bone_meal", 16),
        item_stack(4, "minecraft:oak_log", 16),
        item_stack(5, "minecraft:cobblestone", 32),
        item_stack(6, "minecraft:ice", 4),
        item_stack(7, "minecraft:lava_bucket", 1),
        item_stack(8, "minecraft:water_bucket", 1),
        item_stack(9, "minecraft:wooden_pickaxe", 1),
        item_stack(10, "minecraft:wooden_axe", 1),
        item_stack(11, "minecraft:wooden_hoe", 1),
        item_stack(12, "minecraft:torch", 16),
        item_stack(13, "minecraft:wheat_seeds", 8),
        item_stack(14, "minecraft:pumpkin_seeds", 2),
        item_stack(15, "minecraft:melon_seeds", 2),
        item_stack(16, "minecraft:sugar_cane", 2),
        item_stack(17, "minecraft:cactus", 1),
        item_stack(18, "minecraft:dirt", 16),
        item_stack(19, "voidloom:spindle_crook", 1),
        item_stack(20, "voidloom:thread_mesh_string", 1),
        item_stack(21, "ninjacatskies:whisker_codex", 1),
        item_stack(22, "ninjacatskies:frayed_thread", 8),
        item_stack(23, "voidloom:void_yarn", 2),
        # clearInitialInventory wipes Dock loot — restore ceremony tools.
        item_stack(24, "clowderhall:island_charter", 1),
        item_stack(25, "clowderhall:hub_key", 1),
        written_book_item(26, "How to Start", "Skybound Field Desk", starter_howto_pages()),
    ]
    blocks.append(blk(6, 2, 5, 6, chest_nbt(easy_items)))
    return (sx, sy, sz), palette, blocks, {"south": [[5, 2, 9]]}


def make_hard():
    # Brutal 3x3: one edge dirt missing, cracked deepslate rim flair, hanging roots under, sapling.
    # Minimal chest restores Codex after clearInitialInventory wipe on claim.
    sx, sy, sz = 3, 4, 3
    palette = [
        block("minecraft:dirt"),  # 0
        block("minecraft:grass_block", {"snowy": "false"}),  # 1
        block("minecraft:oak_sapling", {"stage": "0"}),  # 2
        block("minecraft:cracked_deepslate_bricks"),  # 3
        block("minecraft:hanging_roots", {"waterlogged": "false"}),  # 4
        block("minecraft:chest", {"facing": "south", "type": "single", "waterlogged": "false"}),  # 5
    ]
    blocks = []
    # Bottom flair: hanging roots under center, cracked rim on two corners
    blocks.append(blk(1, 0, 1, 4))
    blocks.append(blk(0, 0, 0, 3))
    blocks.append(blk(2, 0, 2, 3))
    # Dirt / grass — skip south-east edge tile (x=2,z=0) to keep it hard
    for x in range(3):
        for z in range(3):
            if x == 2 and z == 0:
                continue
            if (x, z) in ((0, 0), (2, 2)):
                # cracked already at y=0; grass on top of rim
                blocks.append(blk(x, 1, z, 1))
            elif (x, z) == (1, 1):
                blocks.append(blk(x, 1, z, 0))
                blocks.append(blk(x, 2, z, 1))
            else:
                blocks.append(blk(x, 1, z, 0))
                blocks.append(blk(x, 2, z, 1))
    blocks.append(blk(1, 3, 1, 2))
    hard_items = [
        item_stack(0, "ninjacatskies:whisker_codex", 1),
        # 6 Thread → enough string for Stone's 4 Void Yarn opener after claim wipe.
        item_stack(1, "ninjacatskies:frayed_thread", 6),
        # 4 meal: grow the sapling once + pad-compost slime without Desk panic.
        item_stack(2, "minecraft:bone_meal", 4),
        item_stack(3, "minecraft:wheat_seeds", 2),
        item_stack(4, "clowderhall:island_charter", 1),
        item_stack(5, "clowderhall:hub_key", 1),
        written_book_item(6, "How to Start", "Skybound Field Desk", starter_howto_pages()),
        # Minimal cobble-gen + empty bucket so Tension Barrel clay works (melt ice → fill).
        item_stack(7, "minecraft:ice", 2),
        item_stack(8, "minecraft:lava_bucket", 1),
        item_stack(9, "minecraft:bucket", 1),
    ]
    blocks.append(blk(0, 3, 1, 5, chest_nbt(hard_items)))
    return (sx, sy, sz), palette, blocks, {"south": [[1, 3, 0]]}


def sign_message(text):
    return String(json.dumps({"text": text}, separators=(",", ":")))


def sign_nbt(lines, color="black", glowing=True, waxed=True):
    padded = list(lines) + [""] * (4 - len(lines))
    empty = [sign_message("") for _ in range(4)]
    return Compound({
        "id": String("minecraft:sign"),
        "is_waxed": Byte(1 if waxed else 0),
        "front_text": Compound({
            "has_glowing_text": Byte(1 if glowing else 0),
            "color": String(color),
            "messages": List[String]([sign_message(t) for t in padded[:4]]),
        }),
        "back_text": Compound({
            "has_glowing_text": Byte(0),
            "color": String("black"),
            "messages": List[String](empty),
        }),
    })


def starter_howto_pages():
    """OOC / plain-language how-to-start pages (also used in chest book). Keep in sync with starter_book.js v4."""
    return [
        "HOW TO START (read me)\n\n"
        "You are on Clowder Dock — the shared hub, not your forever island.\n\n"
        "Goal: open Create Team, pick a pad template, then open quests.",
        "CLAIM A PAD (guided)\n\n"
        "1) Right-click your Island Charter ON THE DOCK\n"
        "   (or press C — Sky GUIs key)\n"
        "2) Click Create Team\n"
        "3) Type a Clowder name\n"
        "4) Pick a pad template:\n"
        "   Ninjacat Pad = Normal (start here)\n"
        "   Dojo Cottage = Easy\n"
        "   Frayed Thread = Hard\n"
        "5) Click Create — you teleport\n\n"
        "Do NOT use chat create if you want to pick a pad —\n"
        "/skyblock create <name> skips the picker.\n\n"
        "Dock: Charter opens Create Team.\n"
        "Pad: Charter seals spawn here.\n"
        "Hall: Hub Key toggles leave — Create Team is Dock-only.",
        "QUESTS\n\n"
        "Open FTB Quests (quest book key / inventory button).\n"
        "Start Soil (Wake). Do not skip ahead.\n\n"
        "Easy ships water already.\n"
        "Normal/Hard: ice + lava + empty bucket.\n"
        "Place lava, melt ice into water, fill bucket.\n\n"
        "Stone / Recover:\n"
        "1) Unravel Frayed Thread → 3 string\n"
        "2) Craft 4 string → 2 Void Yarn\n"
        "3) Spindle Hammer = cobble + sticks\n"
        "4) Tension Barrel: water+dirt → clay (bucket returns to you)\n"
        "5) Porcelain clay → smelt porcelain bucket\n"
        "6) Then sieve grit; slime = dirt+seeds+meal\n\n"
        "Whisker Codex is the in-world guide.",
        "HELPFUL COMMANDS\n\n"
        "  /clowder help\n"
        "  /clowder hub     → Clowder Hall dimension\n"
        "  /clowder return  → leave Hall to your pad\n"
        "  /clowder revive  → self if spectator (soft hardcore)\n"
        "  /clowder revive <mate> → pull a teammate back\n"
        "  /skyblock home   → your pad\n"
        "  /skyblock create <name>  → advanced (skips pad pick)\n\n"
        "Ops: /skybound revive [player]\n"
        "Hub Key toggles Hall enter/leave.\n"
        "Lost? Charter seals spawn on pad; hub is always safe.",
        "WHAT IS THIS PACK?\n\n"
        "Void skyblock + Loom Braid quests.\n"
        "Tribal Power (drums / Pulse / March) is a core pillar — not a side mod.\n\n"
        "This book is OOC on purpose. Signs & Codex stay in-voice.",
    ]


def lectern_book_nbt():
    """Welcome book seated on the Clowder Dock lectern (faces arrivals)."""
    pages = [{"text": p} for p in starter_howto_pages()]
    page_list = []
    for page in pages:
        page_list.append(Compound({"raw": String(json.dumps(page, separators=(",", ":")))}))
    book = Compound({
        "id": String("minecraft:written_book"),
        "count": Int(1),
        "components": Compound({
            "minecraft:written_book_content": Compound({
                "title": String("How to Start"),
                "author": String("Skybound Field Desk"),
                "generation": Int(0),
                "resolved": Byte(1),
                "pages": List[Compound](page_list),
            })
        }),
    })
    return Compound({
        "id": String("minecraft:lectern"),
        "Book": book,
        "Page": Int(0),
    })


def make_clowder_dock():
    # Shared hub: 15x15 pad, beacon frame, lectern+book, chest, banners, Ninjacat plaque
    sx, sy, sz = 15, 6, 15
    palette = [
        block("minecraft:dirt"),  # 0
        block("minecraft:grass_block", {"snowy": "false"}),  # 1
        block("minecraft:oak_log", {"axis": "y"}),  # 2
        block("minecraft:oak_fence", {
            "east": "true", "north": "false", "south": "false", "west": "true", "waterlogged": "false"
        }),  # 3
        block("minecraft:oak_fence", {
            "east": "true", "north": "false", "south": "false", "west": "false", "waterlogged": "false"
        }),  # 4
        block("minecraft:oak_fence", {
            "east": "false", "north": "false", "south": "false", "west": "true", "waterlogged": "false"
        }),  # 5
        block("minecraft:lantern", {"hanging": "false", "waterlogged": "false"}),  # 6
        block("minecraft:iron_block"),  # 7
        block("minecraft:beacon"),  # 8
        block("minecraft:lectern", {"facing": "south", "has_book": "true", "powered": "false"}),  # 9
        block("minecraft:chest", {"facing": "south", "type": "single", "waterlogged": "false"}),  # 10
        # Standing sign rotation: 0=south (text toward spawn apron), 8=north (wrong — backs the player).
        block("minecraft:oak_sign", {"rotation": "0", "waterlogged": "false"}),  # 11 faces south
        block("minecraft:oak_fence", {
            "east": "false", "north": "false", "south": "false", "west": "false", "waterlogged": "false"
        }),  # 12 free-standing post
        block("minecraft:cyan_banner", {"rotation": "4"}),  # 13 west post, faces west-ish
        block("minecraft:white_banner", {"rotation": "12"}),  # 14 east post, faces east-ish
        block("minecraft:polished_deepslate"),  # 15 path
        block("minecraft:cyan_carpet"),  # 16
        block("minecraft:sea_lantern"),  # 17
        block("minecraft:oak_wall_sign", {"facing": "south", "waterlogged": "false"}),  # 18 plaque on post
    ]
    blocks = []
    for x in range(sx):
        for z in range(sz):
            blocks.append(blk(x, 0, z, 0))
            # Deepslate runner down the centerline; grass elsewhere
            if x == 7 and 3 <= z <= 12:
                blocks.append(blk(x, 1, z, 15))
            else:
                blocks.append(blk(x, 1, z, 1))

    # Corner posts
    for x, z in ((0, 0), (0, 14), (14, 0), (14, 14)):
        blocks.append(blk(x, 2, z, 2))
        blocks.append(blk(x, 3, z, 2))
        blocks.append(blk(x, 4, z, 6))  # lantern cap

    # North fence between posts
    blocks.append(blk(1, 2, 0, 4))
    for x in range(2, 13):
        blocks.append(blk(x, 2, 0, 3))
    blocks.append(blk(13, 2, 0, 5))

    # Beacon frame (level-1 iron pyramid) toward north
    for x in range(6, 9):
        for z in range(1, 4):
            blocks.append(blk(x, 2, z, 7))
    blocks.append(blk(7, 3, 2, 8))

    # Carpet accents flanking the path near the beacon
    blocks.append(blk(6, 2, 4, 16))
    blocks.append(blk(8, 2, 4, 16))
    blocks.append(blk(6, 2, 5, 16))
    blocks.append(blk(8, 2, 5, 16))

    # Banner posts mid-east / mid-west
    blocks.append(blk(2, 2, 7, 12))
    blocks.append(blk(2, 3, 7, 13))
    blocks.append(blk(12, 2, 7, 12))
    blocks.append(blk(12, 3, 7, 14))

    # Ceremony cluster: lectern + chest + sea lanterns
    blocks.append(blk(7, 2, 8, 9, lectern_book_nbt()))
    dock_items = [
        item_stack(0, "clowderhall:island_charter", 1),
        item_stack(1, "clowderhall:hub_key", 1),
        item_stack(2, "minecraft:bread", 8),
        item_stack(3, "ninjacatskies:frayed_thread", 4),
        item_stack(4, "ninjacatskies:whisker_codex", 1),
        item_stack(5, "minecraft:torch", 8),
        written_book_item(6, "How to Start", "Skybound Field Desk", starter_howto_pages()),
    ]
    blocks.append(blk(8, 2, 8, 10, chest_nbt(dock_items)))
    blocks.append(blk(6, 2, 8, 17))
    blocks.append(blk(8, 2, 9, 17))

    # Standing plaque south of lectern — text faces south toward spawn
    blocks.append(blk(7, 2, 9, 11, sign_nbt(
        ["Clowder Dock", "Charter / press C", "Create Team", "pick a pad"],
        color="cyan",
        glowing=True,
    )))

    # Wall plaque on a short post (sign sits south of the log; facing=south)
    blocks.append(blk(7, 2, 4, 2))
    blocks.append(blk(7, 2, 5, 18, sign_nbt(
        ["Welcome,", "Skybound.", "Hub ≠ pad.", "Claim below."],
        color="white",
        glowing=True,
    )))

    # Spawn on the south apron, facing the ceremony (north)
    return (sx, sy, sz), palette, blocks, {"north": [[7, 2, 12]]}


def main():
    islands = {
        "ninjacat_pad.nbt": make_normal(),
        "dojo_cottage.nbt": make_easy(),
        "frayed_thread.nbt": make_hard(),
        "clowder_dock.nbt": make_clowder_dock(),
    }
    spawn_meta = {}
    for name, (size, palette, blocks, spawns) in islands.items():
        save_structure(OUT_CFG / name, size, palette, blocks)
        save_structure(OUT_MIRROR / name, size, palette, blocks)
        spawn_meta[name] = {"size": size, "spawns": spawns, "blocks": len(blocks)}
    print(json.dumps(spawn_meta, indent=2))


if __name__ == "__main__":
    main()
