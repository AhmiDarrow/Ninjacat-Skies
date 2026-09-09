"""Native quest-map headings and node silhouettes; stable quest IDs remain in generate_quests."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'mods/ninjacatskies/src/main/resources/assets'
INK=(17,26,34,255); COPPER=(171,115,73,255); BONE=(225,217,189,255); TEAL=(116,212,178,255)
COLORS=[(147,183,112,255),(159,179,186,255),(120,195,130,255),(224,165,130,255),(233,195,113,255),COPPER,(228,194,123,255),(186,158,230,255),TEAL]

def save(path,im):
    path.parent.mkdir(parents=True,exist_ok=True);im.save(path)

def nodes():
    for name,sides in [('loom',8),('loom_milestone',6)]:
        pts=[(32+29*math.cos(math.pi/8+i*math.tau/sides),32+29*math.sin(math.pi/8+i*math.tau/sides)) for i in range(sides)]
        for layer in ['background','outline','shape']:
            im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im)
            if layer=='background':
                d.polygon(pts,fill=INK,outline=COPPER,width=2)
                inner=[(32+(x-32)*0.87,32+(y-32)*0.87) for x,y in pts]
                d.line(inner+[inner[0]],fill=(52,78,82,255),width=1)
            elif layer=='outline': d.line(pts+[pts[0]],fill='white',width=3)
            else: d.polygon(pts,fill='white')
            save(ASSETS/f'ftbquests/textures/shapes/{name}/{layer}.png',im)

def chapter_images(chapter_id, number, title, quests):
    """One restrained masthead per map; texture text stays out of the clickable graph."""
    nodes() if number==1 else None
    color=COLORS[(number-1)%len(COLORS)]
    im=Image.new('RGBA',(1024,160));d=ImageDraw.Draw(im)
    name=f'chapter_{number:02}'
    out=ASSETS/f'ninjacatskies/textures/gui/quests/{name}.png'
    serif,sans,native=fonts()
    if not native and out.exists():
        # Off Windows the mastheads are rendered with metric-compatible stand-ins; keep the shipped Georgia ones.
        return image_ref(number,name,quests)
    large=ImageFont.truetype(serif,44)
    small=ImageFont.truetype(sans,19)
    d.line((0,137,1000,137),fill=(75,95,95,180),width=1)
    d.line((0,137,200,137),fill=color,width=3)
    d.text((99,15),f'N I N J A C A T   S K I E S   /   {number:02}',font=small,fill=COPPER)
    d.text((97,47),title,font=large,fill=BONE)
    d.text((100,105),'Follow the lit thread. Build what answers.',font=small,fill=(150,176,172,255))
    d.regular_polygon((42,72,34),6,rotation=30,outline=color,width=2)
    d.text((21,56),f'{number:02}',font=ImageFont.truetype(serif,28),fill=color)
    save(out,im)
    return image_ref(number,name,quests)

def image_ref(number,name,quests):
    xs=[float(str(q.get('x',0)).removesuffix('d')) for q in quests]
    x=min(xs,default=0)+6.0
    return [{'id':f'{0x6700000000000000+number:016X}', 'x':x, 'y':-4.2,
             'width':16.0,'height':2.5,'image':f'ninjacatskies:textures/gui/quests/{name}.png',
             'order':-10,'position_locked':True}]

def fonts():
    """(serif, sans, native): Georgia + Segoe UI on Windows; otherwise NCS_FONT_SERIF / NCS_FONT_SANS
    (Gelasio and Open Sans are the metric-compatible open stand-ins) and finally DejaVu."""
    import os
    georgia,segoe='C:/Windows/Fonts/georgia.ttf','C:/Windows/Fonts/segoeui.ttf'
    if Path(georgia).exists() and Path(segoe).exists(): return georgia,segoe,True
    serif=os.environ.get('NCS_FONT_SERIF','/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')
    sans=os.environ.get('NCS_FONT_SANS','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    return serif,sans,False
