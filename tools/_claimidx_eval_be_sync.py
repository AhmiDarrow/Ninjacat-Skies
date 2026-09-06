from pathlib import Path
a = Path("mods/voidloom/src/main/java/com/ninjacat/skies/voidloom/block/LoomframeBlockEntity.java").read_text(encoding="utf-8")
b = Path("mods/voidloom/src/main/java/com/ninjacat/skies/voidloom/block/TensionBarrelBlockEntity.java").read_text(encoding="utf-8")
assert "getUpdatePacket" in a and "getUpdatePacket" in b
assert "ClientboundBlockEntityDataPacket" in a and "ClientboundBlockEntityDataPacket" in b
print("ok")
