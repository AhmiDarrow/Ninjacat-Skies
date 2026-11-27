"""Every word a player reads goes through a lang key, so the pack can be translated.

Checks, per surface:
  * Java (mods/*/src/main/java, GameTests excepted): no English inside Component.literal(...) or the
    NinjacatText teal/gold/indigo(String) helpers; every translatable key used exists in a lang file.
  * Java prose anywhere: no string literal of three or more words (enum fields, drawString, string building),
    except in logger calls, exceptions, annotations and comments.
  * The Whisker Codex (modonomicon JSON, Core and the pack copy): every title, text, name and description
    is a lang key that exists.
  * KubeJS client tooltips: no Text.<colour>('English'); Text.translate keys exist.
A line that must stay literal (an operator-only debug dump, say) carries `// lang-exempt: <why>`.
"""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODS = ROOT / 'mods'
WORDS = re.compile(r'"(?:[^"\\]|\\.)*[A-Za-z]{2,}(?:[^"\\]|\\.)*"')
LITERAL_CALL = re.compile(r'(Component\.literal|NinjacatText\.(?:teal|gold|indigo))\(')
KEY_USE = re.compile(r'(?:Component\.translatable|translatable|(?:teal|gold|indigo)Key)\(\s*"([a-z0-9_.\-]+)"(?!\s*\+)')
BOOK_FIELDS = ('title', 'text', 'name', 'description')
KEY_SHAPE = re.compile(r'^[a-z0-9_.\-]+$')
LOCALES = ('es_es', 'fr_fr', 'de_de', 'pt_br', 'it_it', 'ru_ru', 'pl_pl', 'ja_jp', 'ko_kr', 'zh_cn', 'es_mx')
PLACEHOLDERS = re.compile(r'%(?:\d+\$)?[sdif]|%%|\{\d+\}')
ITEM_IDS = re.compile(r'\b[a-z][a-z0-9_]*:[a-z0-9_./]+\b')
QUEST_LANG = ROOT / 'pack/overrides/config/ftbquests/quests/lang'


def lang_keys():
    keys = set()
    for path in list(MODS.glob('*/src/main/resources/assets/*/lang/en_us.json')) + \
            list((ROOT / 'pack/overrides/kubejs/assets').glob('*/lang/en_us.json')):
        keys |= set(json.loads(path.read_text(encoding='utf-8')))
    return keys


def java_files():
    for path in MODS.glob('*/src/main/java/**/*.java'):
        if '/verification/' in path.as_posix():
            continue
        yield path


def java_violations():
    bad = []
    for path in java_files():
        for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if 'lang-exempt:' in line or line.strip().startswith('//') or line.strip().startswith('*'):
                continue
            for m in LITERAL_CALL.finditer(line):
                rest = line[m.end():]
                if WORDS.search(rest.split(';')[0]):
                    bad.append(f'{path.relative_to(ROOT).as_posix()}:{n}: {line.strip()[:110]}')
                    break
    return bad


# Java tokens that can hold a quote: comments, text blocks, strings, chars. Scanning them in one pass keeps a quote
# inside a comment (or an apostrophe inside a string) from confusing what counts as a literal.
JAVA_TOKEN = re.compile(r'//[^\n]*|/\*.*?\*/|"""(?:\\.|[^\\])*?"""|"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'', re.S)
PROSE = re.compile(r'[A-Za-z]+ [A-Za-z]+ [A-Za-z]+')
# Statement prefixes whose literals are not player text: log lines, exceptions (thrown or built), annotations.
NOT_PLAYER_TEXT = re.compile(r'\b(?:LOGGER|LOG|logger|log)\s*\.\s*(?:trace|debug|info|warn|error|fatal)\s*\(|\bthrow\s+new\b'
                             r'|\bnew\s+[\w.]*(?:Exception|Error)\s*\(|^\s*@')


def java_prose_violations():
    """String literals of three or more words: prose that reaches a player without a lang key."""
    bad = []
    for path in java_files():
        text = path.read_text(encoding='utf-8')
        lines = text.splitlines()
        masked = []   # the source with comments and literal contents blanked, for finding statement starts
        last = 0
        literals = []
        for m in JAVA_TOKEN.finditer(text):
            masked.append(text[last:m.start()])
            tok = m.group(0)
            if tok.startswith('"'):
                literals.append((m.start(), tok.strip('"')))
                masked.append('"' + re.sub(r'[^\n]', ' ', tok[1:-1]) + '"')
            else:
                masked.append(re.sub(r'[^\n]', ' ', tok))
            last = m.end()
        masked.append(text[last:])
        masked = ''.join(masked)
        for pos, content in literals:
            if not PROSE.search(content):
                continue
            n = text.count('\n', 0, pos) + 1
            line = lines[n - 1]
            if 'lang-exempt:' in line:
                continue
            start = max(masked.rfind(c, 0, pos) for c in ';{}') + 1
            if NOT_PLAYER_TEXT.search(masked[start:pos]):
                continue
            bad.append(f'{path.relative_to(ROOT).as_posix()}:{n}: {line.strip()[:110]}')
    return bad


def java_missing_keys(keys):
    missing = []
    for path in java_files():
        for key in KEY_USE.findall(path.read_text(encoding='utf-8')):
            if key not in keys:
                missing.append(f'{path.relative_to(ROOT).as_posix()}: {key}')
    return missing


def book_problems(keys):
    bad = []
    for book in (MODS / 'ninjacatskies/src/main/resources/data/ninjacatskies/modonomicon',
                 ROOT / 'pack/overrides/kubejs/data/ninjacatskies/modonomicon'):
        for path in book.rglob('*.json'):
            def walk(node):
                if isinstance(node, dict):
                    for k, v in node.items():
                        if k in BOOK_FIELDS and isinstance(v, str) and v:
                            if not KEY_SHAPE.match(v):
                                bad.append(f'{path.relative_to(ROOT).as_posix()}: {k} is English, not a key: {v[:60]}')
                            elif v not in keys:
                                bad.append(f'{path.relative_to(ROOT).as_posix()}: {k} key missing from lang: {v}')
                        else:
                            walk(v)
                elif isinstance(node, list):
                    for v in node:
                        walk(v)
            walk(json.loads(path.read_text(encoding='utf-8')))
    return bad


def kubejs_problems(keys):
    bad = []
    for path in (ROOT / 'pack/overrides/kubejs').glob('*_scripts/*.js'):
        text = path.read_text(encoding='utf-8')
        for n, line in enumerate(text.splitlines(), 1):
            if 'lang-exempt:' in line:
                continue
            if re.search(r"Text\.(?!translate)\w+\(\s*'[^']*[A-Za-z]{2,}", line) or re.search(r'Text\.(?!translate)\w+\(\s*"[^"]*[A-Za-z]{2,}', line):
                bad.append(f'{path.relative_to(ROOT).as_posix()}:{n}: {line.strip()[:110]}')
        checked = '\n'.join(line for line in text.splitlines() if 'lang-exempt:' not in line)
        for key in re.findall(r"Text\.translate\(\s*['\"]([a-z0-9_.\-]+)['\"]", checked):
            if key not in keys:
                bad.append(f'{path.relative_to(ROOT).as_posix()}: key missing from lang: {key}')
    return bad


def text_markers(text):
    """Tokens a translation must keep: format args, percents, markdown, breaks, commands, colour codes, item ids."""
    return (
        tuple(PLACEHOLDERS.findall(text)),
        text.count('%'),
        text.count('**'),
        text.count('\n'),
        text.count('\\.'),
        tuple(re.findall(r'`([^`]*)`', text)),
        tuple(re.findall(r'§.', text)),
        tuple(ITEM_IDS.findall(text)),
    )


def en_lang_files():
    return list(MODS.glob('*/src/main/resources/assets/*/lang/en_us.json')) + \
        list((ROOT / 'pack/overrides/kubejs/assets').glob('*/lang/en_us.json'))


def parse_snbt(text):
    """FTB Quests lang files: a compound of strings and string arrays, no commas between keys."""
    i = 0
    n = len(text)

    def skip():
        nonlocal i
        while i < n and text[i] in ' \t\r\n':
            i += 1

    def parse_string():
        nonlocal i
        if text[i] != '"':
            raise ValueError(f'expected string at {i}')
        i += 1
        buf = []
        simple = {'"': '"', '\\': '\\', 'n': '\n', 't': '\t', 'r': '\r', '/': '/', 'b': '\b', 'f': '\f'}
        while i < n:
            c = text[i]
            if c == '\\':
                i += 1
                if i >= n:
                    break
                e = text[i]
                i += 1
                if e == 'u' and i + 4 <= n:
                    buf.append(chr(int(text[i:i + 4], 16)))
                    i += 4
                elif e in simple:
                    buf.append(simple[e])
                else:
                    # SNBT escapes characters JSON does not, such as \& for a literal ampersand.
                    buf.append(e)
                continue
            if c == '"':
                i += 1
                return ''.join(buf)
            buf.append(c)
            i += 1
        raise ValueError('unterminated string')

    def parse_value():
        nonlocal i
        skip()
        if i >= n:
            raise ValueError('truncated value')
        if text[i] == '"':
            return parse_string()
        if text[i] == '[':
            i += 1
            arr = []
            while True:
                skip()
                if i < n and text[i] == ']':
                    i += 1
                    return arr
                arr.append(parse_value())
                skip()
                if i < n and text[i] == ',':
                    i += 1
            return arr
        if text[i] == '{':
            return parse_compound()
        start = i
        while i < n and text[i] not in ' \t\r\n,}]':
            i += 1
        return text[start:i]

    def parse_compound():
        nonlocal i
        skip()
        if i >= n or text[i] != '{':
            raise ValueError(f'expected compound at {i}')
        i += 1
        obj = {}
        while True:
            skip()
            if i < n and text[i] == '}':
                i += 1
                return obj
            start = i
            while i < n and text[i] != ':':
                i += 1
            key = text[start:i].strip()
            if not key or i >= n or text[i] != ':':
                raise ValueError(f'bad key at {start}')
            i += 1
            obj[key] = parse_value()
        return obj

    return parse_compound()


def marker_problems(where, en, translated):
    bad = []
    if not isinstance(en, str) or not isinstance(translated, str):
        return [f'{where}: type {type(en).__name__} vs {type(translated).__name__}']
    if text_markers(en) != text_markers(translated):
        bad.append(f'{where}: placeholders or markup differ')
    if translated.strip() == '' and en.strip() != '':
        bad.append(f'{where}: blank translation')
    return bad


def locale_json_problems():
    bad = []
    for path in en_lang_files():
        english = json.loads(path.read_text(encoding='utf-8'))
        if not english:
            continue
        en_keys = list(english)
        for locale in LOCALES:
            loc_path = path.with_name(locale + '.json')
            if not loc_path.is_file():
                bad.append(f'missing {loc_path.relative_to(ROOT).as_posix()}')
                continue
            try:
                translated = json.loads(loc_path.read_text(encoding='utf-8'))
            except json.JSONDecodeError as exc:
                bad.append(f'{loc_path.relative_to(ROOT).as_posix()}: {exc}')
                continue
            if list(translated) != en_keys:
                missing = [k for k in en_keys if k not in translated]
                extra = [k for k in translated if k not in english]
                bad.append(
                    f'{loc_path.relative_to(ROOT).as_posix()}: key set differs '
                    f'(missing {len(missing)}, extra {len(extra)})')
            for key, en_val in english.items():
                if key not in translated:
                    continue
                bad.extend(marker_problems(
                    f'{loc_path.relative_to(ROOT).as_posix()}:{key}', en_val, translated[key]))
        es_es = path.with_name('es_es.json')
        es_mx = path.with_name('es_mx.json')
        if es_es.is_file() and es_mx.is_file() and es_es.read_bytes() != es_mx.read_bytes():
            bad.append(f'{es_mx.relative_to(ROOT).as_posix()}: expected a copy of es_es.json')
    return bad


def locale_quest_problems():
    bad = []
    english_path = QUEST_LANG / 'en_us.snbt'
    if not english_path.is_file():
        return ['missing quest lang en_us.snbt']
    english = parse_snbt(english_path.read_text(encoding='utf-8'))
    for locale in LOCALES:
        loc_path = QUEST_LANG / f'{locale}.snbt'
        if not loc_path.is_file():
            bad.append(f'missing {loc_path.relative_to(ROOT).as_posix()}')
            continue
        try:
            translated = parse_snbt(loc_path.read_text(encoding='utf-8'))
        except ValueError as exc:
            bad.append(f'{loc_path.relative_to(ROOT).as_posix()}: {exc}')
            continue
        if list(translated) != list(english):
            missing = [k for k in english if k not in translated]
            extra = [k for k in translated if k not in english]
            bad.append(
                f'{loc_path.relative_to(ROOT).as_posix()}: key set differs '
                f'(missing {len(missing)}, extra {len(extra)})')
        for key, en_val in english.items():
            if key not in translated:
                continue
            tr = translated[key]
            if isinstance(en_val, list):
                if not isinstance(tr, list) or len(tr) != len(en_val):
                    bad.append(f'{loc_path.name}:{key}: line count {len(en_val)} vs {len(tr) if isinstance(tr, list) else type(tr).__name__}')
                    continue
                for n, (a, b) in enumerate(zip(en_val, tr)):
                    bad.extend(marker_problems(f'{loc_path.name}:{key}[{n}]', a, b))
            else:
                bad.extend(marker_problems(f'{loc_path.name}:{key}', en_val, tr))
    es_es = QUEST_LANG / 'es_es.snbt'
    es_mx = QUEST_LANG / 'es_mx.snbt'
    if es_es.is_file() and es_mx.is_file() and es_es.read_bytes() != es_mx.read_bytes():
        bad.append('quests/lang/es_mx.snbt: expected a copy of es_es.snbt')
    return bad


class LangKeyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys = lang_keys()

    def test_java_has_no_hardcoded_english(self):
        bad = java_violations()
        self.assertEqual(bad, [], f'{len(bad)} hard-coded messages:\n' + '\n'.join(bad[:40]))

    def test_java_has_no_prose_literals(self):
        bad = java_prose_violations()
        self.assertEqual(bad, [], f'{len(bad)} prose literals (move to a lang key, or `// lang-exempt: <why>` '
                                  'if no player reads it):\n' + '\n'.join(bad[:60]))

    def test_java_keys_exist(self):
        missing = java_missing_keys(self.keys)
        self.assertEqual(missing, [], '\n'.join(missing[:40]))

    def test_codex_is_keyed(self):
        bad = book_problems(self.keys)
        self.assertEqual(bad, [], f'{len(bad)} codex fields:\n' + '\n'.join(bad[:40]))

    def test_kubejs_tooltips_are_keyed(self):
        bad = kubejs_problems(self.keys)
        self.assertEqual(bad, [], f'{len(bad)} tooltip lines:\n' + '\n'.join(bad[:40]))

    def test_locale_files_match_english(self):
        bad = locale_json_problems()
        self.assertEqual(bad, [], f'{len(bad)} locale problems:\n' + '\n'.join(bad[:40]))

    def test_quest_locales_match_english(self):
        bad = locale_quest_problems()
        self.assertEqual(bad, [], f'{len(bad)} quest locale problems:\n' + '\n'.join(bad[:40]))


if __name__ == '__main__':
    result = unittest.main(exit=False, verbosity=1).result
    sys.exit(0 if result.wasSuccessful() else 1)
