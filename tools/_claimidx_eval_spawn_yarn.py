from pathlib import Path

t = Path("pack/overrides/config/skyblockbuilder/spawn.json5").read_text(encoding="utf-8")
events = t.split("spawnProtectionEvents")[1].split("]")[0]
assert "interact_blocks" not in events
assert "interact_items" not in events
s = Path("pack/overrides/kubejs/server_scripts/shop_sinks.js").read_text(encoding="utf-8")
assert "event.shapeless('minecraft:string'" in s
assert "4x minecraft:string',\n    'voidloom:void_yarn'" not in s
print("ok")
