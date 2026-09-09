"""Generate GitHub credits from verified CurseForge metadata and check pack coverage."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWN_MODS = ("ninjacatlib-", "ninjacatskies-", "clowderhall-", "voidloom-", "guardians-", "tribalpower-")


def main():
    rows = json.loads((ROOT / "tools/mod_credits.json").read_text(encoding="utf-8"))
    jars = {p.name for p in (ROOT / "pack/mods").glob("*.jar") if not p.name.startswith(OWN_MODS)}
    credited = {row["filename"] for row in rows}
    if jars != credited:
        raise SystemExit(f"Credits out of date: missing={sorted(jars - credited)}, stale={sorted(credited - jars)}")
    assert len(credited) == len(rows), "Duplicate credits entries"
    lines = [
        "# Mod credits", "",
        "Ninjacat Skies is possible because of the work of the modding community. Thank you to the authors and contributors of every project below.", "",
        f"This page credits all **{len(rows)} outside mods** shipped with the current pack, including libraries, performance tools, and other dependencies. Each mod name links to its CurseForge project page; the names beside it are the authors listed there.", "",
        "Project pages and author listings were verified against the CurseForge API on September 7, 2026. Projects retain their own licenses and attribution requirements.", "",
        "## Outside mods", "",
    ]
    for row in sorted(rows, key=lambda r: r["name"].casefold()):
        assert row["url"].startswith("https://www.curseforge.com/minecraft/mc-mods/")
        name = row["name"].replace("[", r"\[").replace("]", r"\]")
        lines.append(f"- [{name}]({row['url']}) — {', '.join(row['authors'])}")
    lines += ["", "## Pack projects", "",
              "Ninjacat Skies, Ninjacat Lib, Clowder Hall, and Voidloom are the pack's own companion projects. [TribalPower](https://www.curseforge.com/minecraft/mc-mods/tribalpower) is our separately maintained shamanic technomancy mod, also available standalone.", "",
              "[Back to Ninjacat Skies](../README.md)", ""]
    (ROOT / "docs/CREDITS.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated credits: {len(rows)} outside mods; complete installed-pack coverage")


if __name__ == "__main__":
    main()
