from PIL import Image
# palette keys: . transparent  o outline  d dark  m mid  l light  h highlight  t teal glow  T teal bright  g gold glow  G gold bright  k black
BASE={'.':(0,0,0,0),'o':(18,14,22,255),'k':(8,6,10,255),'t':(24,150,140,255),'T':(120,240,220,255),'g':(190,130,40,255),'G':(255,210,110,255)}
def pal(d,m,l,h): p=dict(BASE); p.update({'d':d,'m':m,'l':l,'h':h}); return p
ART={}
def add(name,palette,rows): ART[name]=(palette,rows)

# ---- Rootheart (Soil): teal heart-gem bound in brown roots ----
add("rootheart",pal((72,44,24,255),(112,72,40,255),(150,104,62,255),(190,140,90,255)),[
"................",
"...oooo..oooo...",
"..omllmoomllmo..",
".omlTTTmmTTTlmo.",
".omTTTTTTTTTTmo.",
".omTTTtTTTtTTmo.",
".odmTTTTTTTTmdo.",
"..odmTTTtTTmdo..",
"...odmTTTTmdo...",
"....odmTTmdo....",
".....odmmdo.....",
"...o..oddo..o...",
"..od..od.o..do..",
"...od.o...o.d...",
"....o.......o...",
"................"])
# ---- Grindcore (Stone): stone gear-disc, gold teeth ----
add("grindcore",pal((60,60,64,255),(96,96,100,255),(134,134,138,255),(176,176,180,255)),[
"................",
"......GG.GG.....",
"....GomlmmoG....",
"...Gommlllmmo...",
"..GomllmmmllmoG.",
"..omllmodmmllmo.",
"..Gmlmodkkdmlm..",
"...mlmdkTkdmlG..",
"..Gmlmdkkkdmlm..",
"..omllmoddmllmo.",
"..GomllmmmllmoG.",
"...Gommlllmmo...",
"....GomlmmoG....",
"......GG.GG.....",
"................",
"................"])
# ---- Thornseed (Sprout): green seed pod, gold thorns, teal spark ----
add("thornseed",pal((30,70,30,255),(52,110,44,255),(80,150,62,255),(130,200,100,255)),[
"................",
".......G........",
"......oGo.......",
".....odmdo......",
"....odmlmdo.....",
"...Godmlhmdo....",
"...odmlhTlmdoG..",
"..odmlhTTTlmdo..",
"..odmlhTTlmdo...",
"..Godmllllmdo...",
"...odmmllmdoG...",
"....oddmmdo.....",
".....oddddo.....",
"......oooo......",
".......G........",
"................"])
# ---- Edgestep (Claw): black cat-claw sickle, gold edge ----
add("edgestep",pal((22,22,30,255),(40,40,52,255),(64,64,80,255),(96,96,116,255)),[
"................",
"..........oo....",
".........omo....",
"........odmo....",
".......odmlo....",
"......odmllo....",
".....odmllGo....",
"....odmllG......",
"...odmllG.......",
"..odmlGG........",
".odmlG..........",
".omGG...........",
".oGG...tT.......",
"..o....T........",
"................",
"................"])
# ---- Drumpulse (Spark): brass drum, glowing orange skin ----
add("drumpulse",pal((110,70,24,255),(160,104,36,255),(200,140,60,255),(240,190,110,255)),[
"................",
".....oooooo.....",
"...ooGGGGGGoo...",
"..oGGGhhGGGGGo..",
"..oGGGGGGGGGGo..",
"..omGGGGGGGGmo..",
"..ohlooooooolho.",
"..ohlmdlmdlmlho.",
"..ohmldmldmdmho.",
"..ohldmldmlmdho.",
"..ohlmdlmdlmlho.",
"..ohlooooooolho.",
"...omddddddmo...",
"....oo.TT.oo....",
".......tt.......",
"................"])
# ---- Cogloop (Clock): brass ring gear, teal core ----
add("cogloop",pal((90,60,22,255),(140,96,34,255),(186,134,52,255),(224,176,90,255)),[
"................",
".....o.oo.o.....",
"....omlmmlmo....",
"...omlmoomlmo...",
"..omlmo..omlmo..",
".omlmo.tt.omlmo.",
".omlm..TT..mlmo.",
".oml...TT...lmo.",
".omlm..TT..mlmo.",
".omlmo.tt.omlmo.",
"..omlmo..omlmo..",
"...omlmoomlmo...",
"....omlmmlmo....",
".....o.oo.o.....",
"................",
"................"])
# ---- Hivecall (Swarm): honeycomb amulet with a bee ----
add("hivecall",pal((120,80,20,255),(180,130,40,255),(220,170,60,255),(250,215,120,255)),[
"................",
"......oooo......",
".....omllmo.....",
"....omlmmlmo....",
"...omlmoomlmo...",
"...olmo..omlo...",
"...olmo..omlo...",
"...olm.hh.mlo...",
"...olmoGkGomlo..",
"...olm.kGk.mlo..",
"...olmo.GomTlo..",
"...omlmoomTmo...",
"....omlmmlmo....",
".....omllmo.....",
"......oooo......",
"................"])
# ---- Sealmark (Sigil): dark stone tablet, gold sigil ----
add("sealmark",pal((44,40,60,255),(70,64,92,255),(98,90,124,255),(130,120,160,255)),[
"................",
"....oooooooo....",
"...omlllllllo...",
"...omlGGGGlmo...",
"...oml.GG.lmo...",
"...omlGGGGlmo...",
"...oml.GG.lmo...",
"...omlGtGGlmo...",
"...oml.TT.lmo...",
"...omlGtGGlmo...",
"...oml.GG.lmo...",
"...omllllllmo...",
"...oddddddddo...",
"....oooooooo....",
"................",
"................"])
# ---- Loomthread (Spindle): gold spool, teal thread ----
add("loomthread",pal((110,80,30,255),(170,124,44,255),(215,168,70,255),(245,205,120,255)),[
"................",
"...oooooooooo...",
"..omllllllllmo..",
"..oddddddddddo..",
"...oTtTtTtTto...",
"...otTtTtTtTo...",
"...oTtTtTtTto...",
"...otTtTtTtTo...",
"...oTtTtTtTto...",
"...otTtTtTtTo...",
"..oddddddddddo..",
"..omllllllllmo..",
"...oooooooooo...",
".........T......",
"..........T.....",
"................"])
# ---- Lintwisp (Lint Golem): grey fluff with button eyes ----
add("lintwisp",pal((110,112,120,255),(150,152,160,255),(185,187,195,255),(215,217,225,255)),[
"................",
".....oo..oo.....",
"....odmoodmo....",
"...odmlmmlmdo...",
"..odmlllllllmdo.",
"..omlGolllGolmo.",
"..omlooll.oolmo.",
"..odmlllllllmdo.",
"..odmmlllllmmdo.",
"...odmmmmmmmdo..",
"....odmmmmmdo...",
".....oddddo.....",
"......o.oo.T....",
"...........T....",
"................",
"................"])
# ---- Knotcharm (Tangle): tied rope knot loop ----
add("knotcharm",pal((120,86,40,255),(170,124,60,255),(205,158,86,255),(230,190,120,255)),[
"................",
".....oooooo.....",
"....omllmmlo....",
"...omlooooomo...",
"...olmo...omlo..",
"..oolmoo.oomloo.",
".omlmmlmoolmmlmo",
".olmoolmmmmloomo",
".olmo.ommmmo.lmo",
".omlmoolmmloomlo",
"..oolmlmoolmloo.",
"...omlmo.omlmo..",
"...olmo...omlo..",
"...omo..T..omo..",
"....o..tT...o...",
"................"])
# ---- Shard of the First Cut: black obsidian shard, gold cut line ----
add("firstcut_shard",pal((28,18,40,255),(46,30,66,255),(70,48,98,255),(100,72,136,255)),[
"................",
"........o.......",
".......odo......",
"......odmdo.....",
"......odmGo.....",
".....odmlGdo....",
".....odmGldo....",
"....odmlGlmdo...",
"....odmGllmdo...",
"...odmlGllmmdo..",
"...odmGlllmmdo..",
"...odmmllmmddo..",
"....odmmmmddo...",
".....oddddoT....",
"......oooo.t....",
"................"])
# ---- Overweaver's Shuttle: purple loom shuttle, gold thread ----
add("overweaver_shuttle",pal((60,40,110,255),(92,64,160,255),(126,96,200,255),(170,140,235,255)),[
"................",
"o...............",
"oo..............",
".ooo............",
"..odmoo.........",
"...odmlmoo......",
"....odmlllmoo...",
".....odmGGllmoo.",
"......odmlGGlmo.",
".......odmlGlmo.",
"........odmlmo..",
".........odmo...",
"..........oo....",
"..........T.....",
".........T......",
"................"])

import os
R=os.path.join(os.environ.get('NCS_ART_ROOT', os.path.expanduser('~')),'relics')
os.makedirs(f'{R}/tex16',exist_ok=True); os.makedirs(f'{R}/preview',exist_ok=True)
names=list(ART.keys())
for n,(p,rows) in ART.items():
    assert len(rows)==16 and all(len(r)==16 for r in rows), n
    im=Image.new('RGBA',(16,16),(0,0,0,0))
    for y,row in enumerate(rows):
        for x,ch in enumerate(row): im.putpixel((x,y),p[ch])
    im.save(f'{R}/tex16/{n}.png')
    im.resize((128,128),Image.NEAREST).save(f'{R}/preview/{n}_x8.png')
# contact sheet
sheet=Image.new('RGBA',(128*7+8*8,128*2+8*3+40),(20,22,30,255))
from PIL import ImageDraw; dr=ImageDraw.Draw(sheet)
for i,n in enumerate(names):
    x=8+(i%7)*136; y=8+(i//7)*(136+20)
    sheet.paste(Image.open(f'{R}/preview/{n}_x8.png'),(x,y),Image.open(f'{R}/preview/{n}_x8.png'))
    dr.text((x+2,y+130),n.replace('_',' '),fill=(200,200,210,255))
sheet.save(f'{R}/relic_icons_sheet.png'); print("13 textures:",names)
