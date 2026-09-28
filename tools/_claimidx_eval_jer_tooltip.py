"""Claimidx eval for JER MobTooltip empty-slot crash. Mirrors JerMobTooltipGuard."""
from pathlib import Path

src = Path("mods/ninjacatskies/src/main/java/com/ninjacat/skies/core/compat/JerMobTooltipGuard.java").read_text(encoding="utf-8")
assert "index >= dropCount" in src
assert "NumberFormatException" in src
mixin = Path("mods/ninjacatskies/src/main/java/com/ninjacat/skies/core/mixin/MobTooltipMixin.java").read_text(encoding="utf-8")
assert 'method = "onTooltip"' in mixin
assert "ncs$skipEmptyDropSlot" in mixin
print("ok")
