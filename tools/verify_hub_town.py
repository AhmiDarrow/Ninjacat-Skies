"""Spatial regression checks against the actual generated block plans."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def cells(path,protect=False):
    data=json.loads(path.read_text()); result={}
    for b in data['boxes']:
        a,c=b['from'],b['to'];assert all(a[i]<=c[i] for i in range(3))
        for x in range(a[0],c[0]+1):
            for y in range(a[1],c[1]+1):
                for z in range(a[2],c[2]+1):
                    if protect and abs(x)<=7 and abs(z)<=7 and y>=62:continue
                    result[x,y,z]=b['block']
    return data,result
hub,h=cells(ROOT/'ninjacat-skies/mods/clowderhall/src/main/resources/data/clowderhall/towns/clowder_town.json',True)
assert not any(abs(x)<=7 and abs(z)<=7 and y>=62 for x,y,z in h)
for x in range(-3,4):
    for z in range(-35,36):
        if abs(z)>7:assert (x,63,z) in h,('hub path gap',x,z)
for data,c,y in [(hub,h,63)]:
    for resident in data['residents']:
        x,_,z=map(math.floor,resident['pos'])
        assert (x,y,z) in c and c.get((x,y+1,z),'minecraft:air')=='minecraft:air',('resident blocked',resident)
print('PASS: ceremony preservation, village paths, resident spawn spaces')
