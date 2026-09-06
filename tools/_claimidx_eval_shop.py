from pathlib import Path

t = Path("pack/overrides/config/ftbquests/quests/chapters/16_shop.snbt").read_text(encoding="utf-8")
assert "consume_items: true" in t
assert "minecraft:oak_sapling" in t
print("ok")
