from pathlib import Path

t = Path("INTERNAL/_gen_islands.py").read_text(encoding="utf-8")
assert "whisker_codex" in t
assert "Charter / press C" in t
assert t.count("clowderhall:island_charter") >= 3  # normal + easy + hard
assert t.count("clowderhall:hub_key") >= 3
print("ok")
