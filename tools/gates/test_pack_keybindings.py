"""Validate the pack preset against itself and an optional actual client key inventory."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
rows=json.loads((root/'mods/ninjacatskies/src/main/resources/assets/ninjacatskies/keybindings.json').read_text(encoding='utf-8'))
assert len({r['name'] for r in rows})==len(rows),'Duplicate action in preset'
assert len({(r['key'],r['modifier']) for r in rows})==len(rows),'Duplicate chord in preset'
for row in rows:
 assert row['key'].startswith('key.keyboard.') and not row['key'].endswith('unknown')
 assert row['modifier'] in {'NONE','CONTROL','ALT','SHIFT'}
 assert row['context'] in {'world','original'}
required={'key.ftbquests.quests','skyguis.key.all_teams_screen','key.ftbteams.open_gui','key.ae2.wireless_terminal'}
assert required <= {r['name'] for r in rows}
if len(sys.argv)>1:
 options=Path(sys.argv[1]).read_text(encoding='utf-8')
 actual={line.split(':',1)[0][4:]:line.split(':',1)[1] for line in options.splitlines() if line.startswith('key_')}
 missing=[r['name'] for r in rows if r['name'] not in actual]
 assert not missing,missing
 mismatches=[r['name'] for r in rows if actual[r['name']]!=r['key']+(':'+r['modifier'] if r['modifier']!='NONE' else '')]
 assert not mismatches,mismatches
 print('PASS: every preset binding is present and saved with its intended modifier in the live client.')
print(f'PASS: {len(rows)} unique shortcuts; quest, team and terminal essentials assigned.')
