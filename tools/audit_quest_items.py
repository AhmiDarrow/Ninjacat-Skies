#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
known = set((ROOT / "INTERNAL/known_item_ids.txt").read_text(encoding="utf-8").split())
text = ""
for p in (ROOT / "pack/overrides/config/ftbquests").rglob("*.snbt"):
    text += p.read_text(encoding="utf-8") + "\n"
items = sorted(set(re.findall(r'id: "([a-z0-9_]+:[a-z0-9_/]+)"', text)))


def ok(i: str) -> bool:
    return i.startswith("minecraft:") or i in known


miss = [i for i in items if not ok(i)]
print(f"quest_items={len(items)} missing={len(miss)}")
for i in miss:
    print("MISS", i)
