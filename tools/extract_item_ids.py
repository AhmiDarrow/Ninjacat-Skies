#!/usr/bin/env python3
"""Extract candidate item IDs from pack/mods jars (models + recipes)."""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODS = ROOT / "pack/mods"
OUT = ROOT / "INTERNAL/known_item_ids.txt"

def scan_zip(z: zipfile.ZipFile, ids: set[str], depth: int = 0) -> None:
    for n in z.namelist():
        m = re.match(r"assets/([^/]+)/models/item/(.+)\.json$", n)
        if m:
            ids.add(f"{m.group(1)}:{m.group(2)}")
        m = re.match(r"data/([^/]+)/recipe(?:s)?/(.+)\.json$", n)
        if m:
            leaf = m.group(2).split("/")[-1]
            if not leaf.startswith("_"):
                ids.add(f"{m.group(1)}:{leaf}")
        if depth == 0 and n.endswith(".jar") and n.startswith("META-INF/jarjar/"):
            try:
                import io
                with zipfile.ZipFile(io.BytesIO(z.read(n))) as nested:
                    scan_zip(nested, ids, depth + 1)
            except Exception as exc:
                print("skip nested", n, exc)


ids: set[str] = set()
for jar in MODS.glob("*.jar"):
    try:
        with zipfile.ZipFile(jar) as z:
            scan_zip(z, ids)
    except Exception as exc:
        print("skip", jar.name, exc)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(sorted(ids)) + "\n", encoding="utf-8")
print(f"ids={len(ids)} -> {OUT}")

probes = [
    "mysticalagriculture:inferium_essence",
    "mysticalagriculture:dirt_seeds",
    "create:andesite_alloy",
    "ae2:controller",
    "ae2:certus_quartz_crystal",
    "silentgear:blueprint_paper",
    "silentgear:pickaxe_blueprint",
    "farmersdelight:flint_knife",
    "botanypots:terracotta_botany_pot",
    "exdeorum:porcelain_bucket",
    "voidloom:void_yarn",
    "ninjacatskies:whisker_codex",
    "powah:energy_cell_starter",
    "mekanism:ingot_steel",
    "functionalstorage:oak_1",
    "productivebees:honey_treat",
]
for p in probes:
    print(("OK  " if p in ids else "MISS"), p)
