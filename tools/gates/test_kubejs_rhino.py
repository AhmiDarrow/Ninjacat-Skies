"""Every KubeJS script must parse with the pack's own Rhino (KubeJS's JS engine).

node/`new Function` accept ES2015+ syntax that Rhino rejects — an ES6 shorthand property (`{ type }`) killed the
whole voidloom_recipes.js in 0.6.6, silently dropping every Voidloom recipe. This gate compiles tools/gates/rhino/
RhinoCheck.java against pack/mods/rhino-*.jar and parses pack/overrides/kubejs/**/*.js with it.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

LOOP_OR_TRY = re.compile(r"(\btry|\bfinally|\bcatch\s*\([^)]*\)|\b(?:for|while)\s*\((?:[^()]|\([^()]*\))*\))\s*$")


def const_in_reexecuted_block(src: str) -> list[str]:
    """Rhino (verified on rhino-2101.2.7) throws 'redeclaration of var' when a `const` inside a loop body or a try /
    catch / finally block runs a second time. Find every `const` and look at the block that encloses it."""
    # strip comments and string contents so braces inside them do not count
    clean = re.sub(r"//[^\n]*", lambda m: " " * len(m.group()), src)
    clean = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group()), clean, flags=re.S)
    clean = re.sub(r"'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\"|`(?:\\.|[^`\\])*`", lambda m: re.sub(r"[^\n]", " ", m.group()), clean, flags=re.S)
    problems = []
    for m in re.finditer(r"\bconst\b", clean):
        depth = 0
        i = m.start() - 1
        while i >= 0:
            c = clean[i]
            if c == "}": depth += 1
            elif c == "{":
                if depth == 0:
                    head = clean[max(0, i - 200):i]
                    if LOOP_OR_TRY.search(head):
                        problems.append(f"line {clean.count(chr(10), 0, m.start()) + 1}: const inside a {'try block' if 'try' in head[-12:] or 'catch' in head[-40:] or 'finally' in head[-12:] else 'loop body'} — Rhino throws 'redeclaration' on the second pass; use let")
                    break
                depth -= 1
            i -= 1
    return problems


def main() -> int:
    rhino = sorted((ROOT / "pack/mods").glob("rhino-*.jar"))
    if not rhino:
        print("SKIP kubejs-rhino: no rhino jar in pack/mods"); return 0
    if not shutil.which("javac") or not shutil.which("java"):
        print("SKIP kubejs-rhino: no JDK on PATH"); return 0
    src = ROOT / "tools/gates/rhino"
    out = ROOT / "tools/gates/rhino/build"
    out.mkdir(exist_ok=True)
    cp = str(rhino[-1])
    r = subprocess.run(["javac", "-cp", cp, "-d", str(out), str(src / "RhinoCheck.java")], capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL kubejs-rhino: cannot compile checker\n" + r.stderr); return 1
    sep = ";" if sys.platform.startswith("win") else ":"
    r = subprocess.run(["java", "-cp", cp + sep + str(out), "RhinoCheck", str(ROOT / "pack/overrides/kubejs")], capture_output=True, text=True)
    problems = []
    for js in sorted((ROOT / "pack/overrides/kubejs").rglob("*.js")):
        for msg in const_in_reexecuted_block(js.read_text(encoding="utf-8")):
            problems.append(f"{js.relative_to(ROOT)} :: {msg}")
    ok = r.returncode == 0 and not problems
    print(("PASS" if ok else "FAIL") + " kubejs-rhino: " + r.stdout.strip().splitlines()[-1] + f", {len(problems)} const-in-block")
    if r.returncode != 0: print(r.stdout)
    for pr in problems: print("FAIL " + pr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
