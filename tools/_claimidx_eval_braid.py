from pathlib import Path

t = Path("mods/ninjacatskies/src/main/java/com/ninjacat/skies/core/item/ModItems.java").read_text(encoding="utf-8")
assert "stacksTo(16)" in t
s = Path("pack/overrides/kubejs/server_scripts/strand_gates.js").read_text(encoding="utf-8")
assert "Item.exists" in s and "march_stone" in s
print("ok")
