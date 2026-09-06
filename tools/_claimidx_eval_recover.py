from pathlib import Path

t = Path("pack/overrides/kubejs/server_scripts/voidloom_recipes.js").read_text(encoding="utf-8")
assert "void_yarn_from_string" in t
assert "string_from_frayed_thread" in t
assert "slime_from_pad_compost" in t
print("ok")
