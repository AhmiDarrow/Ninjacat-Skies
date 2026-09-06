"""Proof evals for 2026-09-06 NCS polish sweep."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]

# No KubeJS Hum recipe duplicates
braid = (root / "pack/overrides/kubejs/server_scripts/braid_gates.js").read_text(encoding="utf-8")
assert "ninjacatskies:tribal_spirit_codex" not in braid
assert "ninjacatskies:tribal_drumheart" not in braid
assert "braid_cord" in braid

# Spindle hammer is cobble, not iron
vl = (root / "pack/overrides/kubejs/server_scripts/voidloom_recipes.js").read_text(encoding="utf-8")
assert "voidloom:spindle_hammer" in vl
hammer = vl.split("voidloom:spindle_hammer")[1].split("event.shaped")[0]
assert "minecraft:cobblestone" in hammer
assert "minecraft:iron_ingot" not in hammer

# Charter Dock-only Create Team + overworld check
charter = (root / "mods/clowderhall/src/main/java/com/ninjacat/skies/clowder/item/IslandCharterItem.java").read_text(encoding="utf-8")
assert "isOnDock" in charter
assert "Level.OVERWORLD" in charter
assert "if (onDock) {\n                openCreateTeamScreen();" in charter or "if (onDock) {\r\n                openCreateTeamScreen();" in charter

# Hall return gated
dims = (root / "mods/clowderhall/src/main/java/com/ninjacat/skies/clowder/world/ModDimensions.java").read_text(encoding="utf-8")
assert "hub_return_not_in_hall" in dims
assert "dimension().equals(CLOWDER_HALL)" in dims

# Tribal chapter order: Bone Chime before Spirit Codex
tribal = (root / "pack/overrides/config/ftbquests/quests/chapters/34_tribal.snbt").read_text(encoding="utf-8")
chime_i = tribal.find("tribalpower:bone_chime")
codex_i = tribal.find("tribalpower:spirit_codex")
shard_i = tribal.find("tribalpower:spirit_shard")
assert 0 <= chime_i < shard_i < codex_i or (chime_i >= 0 and shard_i >= 0 and codex_i >= 0 and chime_i < codex_i)

# Welcome marks seen on open
welcome = (root / "pack/overrides/config/fancymenu/customization/ninjacat_skies_welcome_layout.txt").read_text(encoding="utf-8")
assert "ncs-welcome-seen-ticker" in welcome
assert "ncs_welcome_seen:1" in welcome

# download-mods no longer targets unavailable classics
dl = (root / "tools/download-mods.ps1").read_text(encoding="utf-8")
assert 'Key = "Botania"' not in dl
assert 'Key = "Tinkers Construct"' not in dl

# Soft hardcore revive seats player
events = (root / "mods/ninjacatskies/src/main/java/com/ninjacat/skies/core/event/SkyboundEvents.java").read_text(encoding="utf-8")
assert "seatAtRespawnOrDock" in events
assert "revivePlayer" in events
assert "clowderhall:island_charter" in events
assert "clowderhall:hub_key" in events

# Clowder revive (self + mate)
clowder_cmds = (root / "mods/clowderhall/src/main/java/com/ninjacat/skies/clowder/command/ClowderCommands.java").read_text(encoding="utf-8")
assert 'literal("revive")' in clowder_cmds
assert "reviveSelf" in clowder_cmds
assert "ClowderTeams.sameClowder" in clowder_cmds

# Charter pad-only seal + solid footing; Hub Key toggle
charter = (root / "mods/clowderhall/src/main/java/com/ninjacat/skies/clowder/item/IslandCharterItem.java").read_text(encoding="utf-8")
assert "boolean onPad = level.dimension().equals(Level.OVERWORLD) && !onDock" in charter
assert "hasSolidFooting" in charter
hub = (root / "mods/clowderhall/src/main/java/com/ninjacat/skies/clowder/item/HubKeyItem.java").read_text(encoding="utf-8")
assert "returnFromHub" in hub

# Starter book v4 + Tribal porcelain water alts
starter = (root / "pack/overrides/kubejs/server_scripts/starter_book.js").read_text(encoding="utf-8")
assert "ncs_starter_howto_v4" in starter
assert "bucket returns to you" in starter
tribal_porc = (root / "pack/overrides/kubejs/server_scripts/tribal_porcelain.js").read_text(encoding="utf-8")
assert "porcelain_water_bucket" in tribal_porc
assert "tribal_totem_water_porcelain" in tribal_porc

# Spark Hum order in generator
gq = (root / "tools/generate_quests.py").read_text(encoding="utf-8")
spark = gq.split("def build_spark()")[1].split("def build_")[0]
assert spark.find("bone_chime") < spark.find("drumheart")
assert spark.find("spirit_shard") < spark.find("drumheart")
assert spark.find("copper_resonator") < spark.find("drumheart")
sigil = gq.split("def build_sigil()")[1].split("def build_")[0]
assert sigil.find("braid_cord") < sigil.find("occultism:dictionary")
spindle = gq.split("def build_spindle()")[1].split("def build_")[0]
assert spindle.find("braid_cord") < spindle.find("molecular_assembler")
assert spindle.find("strand_token_spindle") < spindle.find("spindle_loom_fragment")
assert "Buy Leather" in gq
assert "Buy Feather Pack" in gq and "Buy Lapis Pack" in gq
assert 'reward["team_reward"] = False' in gq
assert 'q["repeatable"] = True' in gq
assert "3 string; craft 4 string" in gq
assert "empty bucket returns to you" in gq
# Empty bucket early on Desk spine (before Deposit II).
shop = gq.split("def build_shop()")[1].split("def write_")[0]
assert shop.find("Buy Empty Bucket") < shop.find("Desk Deposit II")
assert "porcelain water + dirt" in (root / "pack/overrides/kubejs/client_scripts/voidloom_tooltips.js").read_text(encoding="utf-8")
assert not (root / "data/tribalpower").exists()
hall_howto = (root / "mods/clowderhall/src/main/java/com/ninjacat/skies/clowder/world/ModDimensions.java").read_text(encoding="utf-8")
assert "QUESTS / RECOVER" in hall_howto and "Craft 4 string" in hall_howto

# Hard pad cobble-gen kit in generator
gen = (root / "INTERNAL/_gen_islands.py").read_text(encoding="utf-8")
assert 'item_stack(7, "minecraft:ice", 2)' in gen
assert 'item_stack(8, "minecraft:lava_bucket", 1)' in gen
assert 'item_stack(2, "minecraft:bone_meal", 4)' in gen
assert "Easy ships water already" in gen

# Hall chest includes Codex
hall = (root / "mods/clowderhall/src/main/java/com/ninjacat/skies/clowder/world/ModDimensions.java").read_text(encoding="utf-8")
assert "WHISKER_CODEX" in hall
assert "createHowToStartBook" in hall

# Deferred polish: real banner pattern, crook class, barrel eject, clay-before-porcelain
assert (root / "mods/clowderhall/src/main/resources/data/clowderhall/banner_pattern/strand.json").exists()
assert (root / "mods/clowderhall/src/main/resources/data/clowderhall/tags/banner_pattern/pattern_item/strand.json").exists()
mi = (root / "mods/clowderhall/src/main/java/com/ninjacat/skies/clowder/item/ModItems.java").read_text(encoding="utf-8")
assert "BannerPatternItem" in mi
crook = (root / "mods/voidloom/src/main/java/com/ninjacat/skies/voidloom/item/SpindleCrookItem.java").read_text(encoding="utf-8")
assert "BlockTags.LEAVES" in crook
assert (root / "mods/voidloom/src/main/resources/data/exdeorum/tags/item/crooks.json").exists()
stone = gq.split("def build_stone()")[1].split("def build_")[0]
assert stone.find("clay_ball") < stone.find("porcelain_bucket")
assert stone.find("porcelain_clay_ball") < stone.find("porcelain_bucket")
assert stone.find("tension_barrel") < stone.find("clay_ball")

# Bucket kit + better pearl yarn + barrel returns bucket to player
assert 'item_stack(9, "minecraft:bucket", 1)' in gen or 'item_stack(6, "minecraft:bucket", 1)' in gen
vl = (root / "pack/overrides/kubejs/server_scripts/voidloom_recipes.js").read_text(encoding="utf-8")
assert "2x voidloom:void_yarn" in vl and "ender_pearl" in vl
tb2 = (root / "mods/voidloom/src/main/java/com/ninjacat/skies/voidloom/block/TensionBarrelBlockEntity.java").read_text(encoding="utf-8")
assert "rememberUser" in tb2 and "porcelain_water_bucket" in tb2 and "returnEmptyBucket" in tb2
assert "Buy Empty Bucket" in gq

print("ok")




