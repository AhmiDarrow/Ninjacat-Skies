import re
from pathlib import Path
text = Path(__file__).with_name("generate_item_textures.py").read_text(encoding="utf-8")
for i, line in enumerate(text.splitlines(), 1):
    for m in re.finditer(r'"([A-Za-z0-9\.\s]{8,})"', line):
        s = m.group(1)
        if s.startswith(".") or "...." in s:
            if len(s) != 16:
                print(i, len(s), repr(s))
