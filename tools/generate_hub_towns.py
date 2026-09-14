"""Deterministic block-native town plans; no generated raster art."""
import json, math
from pathlib import Path

class Town:
    def __init__(self, name, y, warm=False):
        self.name,self.y,self.warm=name,y,warm
        self.ops=[]; self.signs=[]; self.residents=[]
        self.wood='spruce' if warm else 'dark_oak'
        self.roof='waxed_oxidized_cut_copper' if warm else 'deepslate_tiles'
    def box(self,x,y,z,X,Y,Z,b):
        self.ops.append(dict(from_=[x,y,z],to=[X,Y,Z],block='minecraft:'+b))
    def p(self,x,y,z,b):self.box(x,y,z,x,y,z,b)
    def sign(self,x,y,z,*lines):
        self.p(x,y,z,'oak_sign[rotation=0]')
        self.signs.append(dict(pos=[x,y,z],lines=list(lines)))
    def lamp(self,x,z):
        y=self.y
        self.p(x,y+1,z,'stone_brick_wall')
        self.box(x,y+2,z,x,y+3,z,self.wood+'_fence')
        self.p(x,y+4,z,'lantern')
    def tree(self,x,z):
        assert all((x+dx,z+dz) in self.surface for dx in [-1,0,1] for dz in [-1,0,1]), ("unsupported tree",x,z)
        y=self.y
        self.box(x,y+1,z,x,y+5,z,'oak_log')
        for dy,r in [(4,2),(5,3),(6,2),(7,1)]:
            for dx in range(-r,r+1):
                for dz in range(-r,r+1):
                    if abs(dx)+abs(dz)<=r+1 and (dx or dz):
                        self.p(x+dx,y+dy,z+dz,'oak_leaves[persistent=true]')
        self.p(x,y+7,z,'oak_leaves[persistent=true]')
    def house(self,x,z,w,d,label,accent='cyan',open_front=False):
        first_op=len(self.ops); first_sign=len(self.signs)
        y=self.y; X=x+w-1; Z=z+d-1; mid=x+w//2
        self.box(x,y,z,X,y,Z,'stone_bricks')
        self.box(x,y+1,z,X,y+5,Z,'stripped_birch_wood' if self.warm else 'white_terracotta')
        self.box(x+1,y+1,z+1,X-1,y+5,Z-1,'air')
        self.box(x+1,y,z+1,X-1,y,Z-1,self.wood+'_planks')
        for a in [x,X]:
            for b in [z,Z]: self.box(a,y+1,b,a,y+5,b,self.wood+'_log')
        self.box(x,y+5,z,X,y+5,z,self.wood+'_log[axis=x]')
        self.box(x,y+5,Z,X,y+5,Z,self.wood+'_log[axis=x]')
        for a in [x+2,X-2]:
            self.box(a,y+2,z,a+1,y+3,z,'glass')
            self.box(a,y+2,Z,a+1,y+3,Z,'glass')
            self.p(a,y+1,z-1,self.wood+'_trapdoor[facing=north,half=top]')
            self.p(a,y+2,z-1,'potted_fern')
        for b in [z+3,Z-3]:
            self.box(x,y+2,b,x,y+3,b+1,'glass')
            self.box(X,y+2,b,X,y+3,b+1,'glass')
        # Deep eaves, layered gable, contrasting ridge; real accessible interiors.
        for r in range((w+2)//2):
            self.box(x-1+r,y+6+r,z-1,x-1+r,y+6+r,Z+1,self.roof)
            self.box(X+1-r,y+6+r,z-1,X+1-r,y+6+r,Z+1,self.roof)
            if r>0:
                self.box(x+r,y+5+r,z,X-r,y+5+r,z,self.wood+'_planks')
                self.box(x+r,y+5+r,Z,X-r,y+5+r,Z,self.wood+'_planks')
        self.box(mid,y+6+w//2,z-1,mid,y+6+w//2,Z+1,accent+'_concrete')
        self.box(mid-1,y+1,z,mid+1,y+3,z,'air')
        if not open_front:
            self.p(mid,y+1,z,self.wood+'_door[facing=north,half=lower]')
            self.p(mid,y+2,z,self.wood+'_door[facing=north,half=upper]')
            self.box(mid-1,y+1,z,mid-1,y+3,z,self.wood+'_planks')
            self.box(mid+1,y+1,z,mid+1,y+3,z,self.wood+'_planks')
        self.box(mid-2,y,z-3,mid+2,y,z-1,'stone_bricks')
        self.p(mid-2,y+3,z-1,'lantern')
        self.p(mid+2,y+3,z-1,'lantern')
        self.p(x+2,y+1,Z-2,'crafting_table')
        self.p(x+3,y+1,Z-2,'barrel')
        self.p(X-2,y+1,Z-2,'smoker[facing=north]')
        self.p(x+2,y+1,z+2,self.wood+'_stairs[facing=south]')
        self.p(X-2,y+1,z+2,self.wood+'_stairs[facing=south]')
        self.p(mid,y+4,z+d//2,'lantern[hanging=true]')
        self.sign(mid-2,y+1,z-2,label,'Welcome, traveler')
        # Northern buildings open toward the shared street, not the island edge.
        if z < (-70 if not self.warm else 0):
            for o in self.ops[first_op:]:
                lo,hi=o['from_'][2],o['to'][2]
                o['from_'][2],o['to'][2]=z+Z-hi,z+Z-lo
                o['block']=o['block'].replace('facing=north','facing=TEMP').replace('facing=south','facing=north').replace('facing=TEMP','facing=south').replace('rotation=0','rotation=8')
            for sign in self.signs[first_sign:]:sign['pos'][2]=z+Z-sign['pos'][2]
    def stall(self,x,z,color,label):
        y=self.y
        for a in [x,x+4]:
            for b in [z,z+3]:self.box(a,y+1,b,a,y+3,b,self.wood+'_fence')
        for a in range(x-1,x+6):self.box(a,y+4,z-1,a,y+4,z+4,('white' if a%2 else color)+'_wool')
        self.box(x+1,y+1,z+2,x+3,y+1,z+2,'barrel')
        self.p(x+2,y+2,z+2,'lantern')
        self.sign(x+2,y+1,z,label)
    def resident(self,x,z,name,kind='villager'):
        self.residents.append(dict(pos=[x+.5,self.y+1,z+.5],name=name,type=kind))
    def island(self,rx,rz,cz=0):
        y=self.y
        for x in range(-rx,rx+1):
            reach=int(rz*math.sqrt(max(0,1-(x/rx)**2)))
            if reach<1:continue
            self.box(x,y-2,cz-reach,x,y-1,cz+reach,'stone')
            self.box(x,y,cz-reach,x,y,cz+reach,'grass_block')
            # Tapered underside instead of a two-block floating sheet.
            for depth,scale in [(3,.94),(5,.84),(8,.65),(12,.38)]:
                if abs(x)>rx*scale:continue
                rr=int(rz*scale*math.sqrt(max(0,1-(x/(rx*scale))**2)))
                self.box(x,y-depth,cz-rr,x,y-depth+(3 if depth==12 else 2),cz+rr,'tuff' if depth<8 else 'deepslate')
            for z in [cz-reach,cz+reach]:
                self.p(x,y,z,'mossy_stone_bricks')
                self.p(x,y+1,z,self.wood+'_fence[east=true,west=true]')
        # Close the complete stepped perimeter, including the east/west tips.
        surface={(x,z) for x in range(-rx+1,rx) for z in range(cz-int(rz*math.sqrt(1-(x/rx)**2)),cz+int(rz*math.sqrt(1-(x/rx)**2))+1)}
        self.surface=surface
        for x,z in sorted(surface):
            if any((x+dx,z+dz) not in surface for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]):
                self.p(x,y+1,z,self.wood+'_fence[north=true,south=true,east=true,west=true]')
    def save(self,path):
        Path(path).parent.mkdir(parents=True,exist_ok=True)
        Path(path).write_text(json.dumps(dict(name=self.name,boxes=[{'from':o['from_'], 'to':o['to'],'block':o['block']} for o in self.ops],signs=self.signs,residents=self.residents),indent=2)+'\n')

def race():
    t=Town('Whiskerwind Race Town',64)
    t.island(82,85,-15)
    # Spacious cobbled racing town north of every course footprint.
    for z in range(-94,-43):
        width=min(43,int(82*math.sqrt(1-((z+15)/85)**2))-2)
        t.box(-width,64,z,width,64,z,'stone_bricks')
    t.box(-5,64,-94,5,64,-44,'polished_andesite')
    t.box(-43,64,-73,43,64,-69,'polished_andesite')
    for x in [-7,7]:t.box(x,64,-92,x,64,-45,'cyan_terracotta')
    t.house(-34,-90,15,13,'The Feather Inn','yellow')
    t.house(18,-90,17,13,'Cloudhoof Stables','cyan',True)
    # Stable bays with hay, water troughs and a generous 3-wide entry.
    for x in [21,26,31]:
        t.box(x,65,-81,x+1,65,-79,'hay_block')
        t.p(x,65,-84,'water_cauldron[level=3]')
    t.house(-39,-65,13,13,'Tack & Thread','cyan')
    t.house(26,-65,13,13,'Riders Lodge','yellow')
    for x,z,c,label in [(-20,-61,'yellow','Gysahl Market'),(15,-61,'cyan','Race Supplies'),(-20,-49,'cyan','Feather Fair'),(15,-49,'yellow','Victory Treats')]: t.stall(x,z,c,label)
    # Cat-eared arch framing the town street, leaving five blocks headroom.
    for x in [-8,8]:t.box(x,65,-72,x,73,-72,'polished_blackstone_bricks')
    t.box(-8,73,-72,8,74,-72,'polished_blackstone_bricks')
    for x in [-7,7]:t.box(x,75,-72,x,77,-72,'cyan_concrete')
    for x in [-3,3]:t.p(x,74,-73,'sea_lantern')
    t.sign(-6,65,-74,'WHISKERWIND','Race Town','Stables & market','Track ahead')
    # Spectator terrace beyond the largest course, central aisle and safe rail.
    for row in range(4):
        z=46+row*2
        for a,b in [(-30,-4),(4,30)]:
            t.box(a,64,z,b,64+row,z+1,'stone_bricks')
            t.box(a,65+row,z,b,65+row,z,'dark_oak_stairs[facing=north]')
    for x in [-32,32]:t.box(x,65,46,x,74,55,'dark_oak_log')
    t.box(-33,75,45,33,75,56,'deepslate_tile_slab')
    for x in range(-30,31,6):
        t.box(x,74,45,x+2,74,45,'cyan_wool' if x%12 else 'yellow_wool')
        t.p(x,73,50,'lantern[hanging=true]')
    # Permanent infield garden stays inside the smallest oval.
    t.box(-7,64,-4,7,64,4,'moss_block')
    t.box(-2,65,-2,2,65,2,'stone_bricks')
    t.box(-1,65,-1,1,65,1,'water')
    t.p(0,65,0,'gold_block');t.p(0,66,0,'chiseled_deepslate');t.p(0,67,0,'sea_lantern')
    for x,z in [(-10,-85),(10,-85),(-45,-52),(45,-52),(-50,42),(50,42),(-70,-22),(70,-22)]:t.tree(x,z)
    for x in [-42,42]:
        for z in [-88,-72,-48]:t.lamp(x,z)
    for x in [-11,11]:
        for z in [-88,-70,-48]:t.lamp(x,z)
    for x,z in [(-47,-69),(47,-69),(-40,-85),(40,-85),(-8,1),(8,1)]:
        t.p(x,65,z,'flowering_azalea');t.p(x+1,65,z,'poppy')
    t.sign(-7,65,-48,'COURSE ONE','Right-click: ranked','Left-click: duel')
    t.sign(7,65,-48,'COURSE TWO','Right-click: ranked','Left-click: duel')
    for x,z,n in [(-28,-86,'Pip'),(23,-87,'Mira'),(-35,-60,'Jun'),(30,-60,'Ori')]:t.resident(x,z,n)
    t.resident(-22,-85,'Saffron','cat');t.resident(29,-86,'Mochi','cat')
    return t

def clowder():
    t=Town('Lanternweave Village',63,True);t.island(46,42)
    t.box(-11,63,-11,11,63,11,'stone_bricks')
    t.box(-3,63,-37,3,63,37,'polished_andesite')
    t.box(-39,63,-3,39,63,3,'polished_andesite')
    for x in [-5,5]:t.box(x,63,-35,x,63,35,'cyan_terracotta')
    t.house(-30,-28,13,12,'The Purring Hearth','orange')
    t.house(18,-28,13,12,'Weavers Workshop','cyan')
    t.house(-30,14,13,12,'Clowder Commons','orange')
    t.house(18,14,13,12,'Lantern Library','cyan')
    # A shared bell tower gives the village a landmark beyond repeated cottages.
    for x in [-5,5]:
        for z in [-29,-23]:t.box(x,64,z,x,74,z,'spruce_log')
    t.box(-5,74,-29,5,74,-29,'spruce_planks')
    t.box(-5,74,-23,5,74,-23,'spruce_planks')
    for r in range(6):
        t.box(-6+r,75+r,-30,-6+r,75+r,-22,'waxed_oxidized_cut_copper')
        t.box(6-r,75+r,-30,6-r,75+r,-22,'waxed_oxidized_cut_copper')
    t.box(0,81,-30,0,81,-22,'orange_concrete')
    t.box(-4,72,-26,4,72,-26,'spruce_log[axis=x]')
    t.p(0,71,-26,'bell[attachment=ceiling,facing=south]')
    for x in [-4,4]:t.p(x,73,-22,'lantern')
    t.sign(-4,64,-21,'LANTERN BELFRY','Gather together')
    # Commons chimney and library dormer distinguish each roofline.
    t.box(-28,68,23,-27,77,24,'bricks');t.p(-28,78,23,'campfire[lit=false]')
    t.box(22,69,13,26,72,15,'spruce_planks');t.box(23,70,13,25,71,13,'glass')
    t.box(21,73,12,27,73,16,'waxed_oxidized_cut_copper_slab')
    # Library shelves and workshop stations are usable, not scenery shells.
    t.box(20,64,22,27,66,23,'bookshelf');t.p(24,64,19,'lectern')
    t.p(21,64,-20,'loom');t.p(23,64,-20,'cartography_table')
    for x in [-24,24]:
        t.box(x-2,63,-16,x+2,63,13,'stone_bricks')
        t.box(x-2,63,-33,x+2,63,-29,'stone_bricks')
    t.box(-32,63,-33,32,63,-30,'stone_bricks')
    t.box(-32,63,10,32,63,12,'stone_bricks')
    t.stall(-18,-6,'cyan','Strand Exchange');t.stall(14,-6,'orange','Community Pantry')
    # Nine-strand lantern walk and communal picnic gardens.
    for x in range(-16,17,4):
        t.p(x,64,31,'chiseled_stone_bricks');t.p(x,65,31,'lantern')
    t.sign(0,64,28,'LANTERN WALK','Nine strands','One shared sky')
    for x,z in [(-36,-12),(36,-12),(-36,11),(36,11),(-12,-32),(12,-32),(-12,30),(12,30)]:t.tree(x,z)
    for x,z in [(-11,-11),(11,-11),(-11,11),(11,11),(-35,0),(35,0),(0,-35),(0,35)]:t.lamp(x,z)
    for x in [-13,13]:
        for z in [-20,20]:
            t.box(x-1,64,z,x+1,64,z,'spruce_slab[type=top]')
            t.box(x-1,64,z+2,x+1,64,z+2,'spruce_stairs[facing=north]')
            t.p(x,65,z,'lantern')
    for x,z in [(-40,0),(40,0),(-10,-25),(10,-25),(-10,25),(10,25)]:
        t.p(x,64,z,'flowering_azalea');t.p(x+1,64,z,'blue_orchid')
    for x,z,n in [(-26,-24,'Nori'),(22,-24,'Tavi'),(-26,20,'Ember'),(23,19,'Lumi')]:t.resident(x,z,n)
    t.resident(-25,19,'Button','cat');t.resident(23,-24,'Nimbus','cat')
    # Keep the original ceremony pad and its saved chests/ring fully untouched.
    return t

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('kind',choices=['race','clowder']);p.add_argument('output');a=p.parse_args()
    (race() if a.kind=='race' else clowder()).save(a.output)
