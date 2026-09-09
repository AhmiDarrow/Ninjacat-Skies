import bpy, mathutils, math, sys, random, os
ART=os.environ.get('NCS_ART_ROOT', os.path.expanduser('~'))   # work root: <ART>/renders, libs beside this file or in <ART>
sys.path.insert(0,ART); sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import boss_lib2 as L, rig_lib as R, rig_pro as PRO
S=L.sphere; C=L.cube; Y=L.cyl; rad=math.radians
TEAL_RGB=(0.12,0.95,0.82); GOLD_RGB=(1.0,0.72,0.18)
def glows(): return L.glow("gold",GOLD_RGB,3.2), L.glow("teal",TEAL_RGB,2.4), L.glow("eye",(1.0,0.8,0.3),4.5)
DIM=lambda rgb,s=1.1: L.glow("dim",rgb,s)

# ---------------- STONE: the Grindmaw (low, wide, armored maw) ----------------
def grindmaw():
    L.reset(); random.seed(2); parts=[]; P=lambda o:(parts.append(o),o)[1]
    for sx in(-1,1):
        P(C((sx*2.4,0.2,0.8),(3.4,3.8,1.6))); P(Y((sx*2.4,0,2.2),1.5,2.8)); P(S((sx*2.4,0,3.4),1.6))
    P(C((0,0,4.6),(9.0,5.0,3.6))); P(C((0,-0.6,6.6),(8.2,4.6,2.6),rot=(rad(-6),0,0)))      # wide flat body + upper slab
    P(C((0,-2.0,3.9),(6.4,2.6,2.4)))                                                       # lower jaw block (the maw)
    P(C((0,-2.0,6.1),(6.6,2.4,1.6),rot=(rad(-10),0,0)))                                    # upper jaw
    for sx in(-1,1):
        P(S((sx*4.6,-0.2,6.9),2.1)); P(C((sx*4.8,-0.4,7.6),(3.0,3.2,1.2),rot=(0,rad(-sx*15),0)))   # shoulder domes + plates
        P(Y((sx*5.4,0.2,4.6),1.2,4.2,rot=(0,rad(sx*8),0))); P(Y((sx*5.9,0.6,2.0),1.7,2.2))       # arm + grinder drum hand
    P(Y((0,-0.6,7.6),1.5,1.6)); P(C((0,-0.8,8.3),(3.8,3.4,2.0))); P(C((0,-2.2,8.6),(3.4,1.0,0.9)))   # neck + low head block + brow
    body=L.fuse(parts,voxel=0.16,disp=0.16,disp_scale=1.3,facet=0.05)
    body.data.materials.append(L.surface("grindmaw",(0.30,0.29,0.27),(0.09,0.09,0.1),crack=GOLD_RGB,crack_str=3.0,crack_center=(0,-2.4,5.0),crack_radius=5.5,metallic=0.35,rough=0.75,bump=0.5))
    GOLD,TEAL,EYE=glows(); acc=[]
    # maw: rows of gold teeth, teal throat core deep inside
    for k in range(7):
        o=C((-2.4+k*0.8,-3.3,5.2),(0.34,0.5,0.75)); o.data.materials.append(GOLD); acc.append(o)
        o=C((-2.4+k*0.8,-3.3,4.35),(0.34,0.5,0.6)); o.data.materials.append(GOLD); acc.append(o)
    o=C((0,-2.6,4.8),(4.0,0.8,0.8)); o.data.materials.append(TEAL); acc.append(o)
    for sx in(-1,1): o=C((sx*0.9,-2.75,8.7),(0.7,0.4,0.28)); o.data.materials.append(EYE); acc.append(o)
    for sx in(-1,1):
        for k in range(2): o=L.ring((sx*5.9,0.6,1.5+k*0.9),1.8,0.09,TEAL); acc.append(o)
    L.ground_cracks((0,0),n=12,mat=GOLD,seed=4,length=(3,9)); L.embers(30,(0,-1,4.5),(8,4,4),[GOLD,TEAL],0.03,0.08,seed=5)
    pts=dict(pelvis=(0,0,3.2),spine0=(0,0,4.4),chest0=(0,-0.3,6.0),neck0=(0,-0.5,7.3),head0=(0,-0.7,7.9),head1=(0,-0.9,9.4),
             shoulder=(4.6,-0.2,7.0),elbow=(5.4,0.2,4.6),wrist=(5.8,0.5,2.6),hand=(5.9,0.6,1.0),
             hip=(2.4,0,3.6),knee=(2.4,0,2.0),ankle=(2.4,0.05,1.0),toe=(2.4,-1.3,0.3))
    arm=R.humanoid_armature(pts); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=5.2,cam=(17,-19,5.2),lens=42,f=1,big="R")

# ---------------- SPROUT: the Thornmother (tall gaunt bark witch) ----------------
def thornmother():
    L.reset(); random.seed(3); parts=[]; P=lambda o:(parts.append(o),o)[1]
    for i in range(7):   # root-legs splaying into the ground (chains: hip -> mid -> ground)
        a=i/7*math.tau; L.limb([(0,0,3.4),(math.cos(a)*1.4,math.sin(a)*1.4,1.7),(math.cos(a)*2.4,math.sin(a)*2.4,0.2)],0.42,0.55,parts)
    P(S((0,0,3.6),1.6)); L.limb([(0,0,3.4),(0,0.15,7.0),(0,-0.1,10.6)],1.0,1.15,parts)         # hips + trunk (two segments, slight sway)
    P(S((0,-0.3,10.8),1.7)); P(C((0,-0.2,11.5),(4.2,2.2,1.6)))                                   # chest + shoulder bar
    for sx in(-1,1):   # long thin arms as chains: shoulder -> elbow -> wrist -> twig-hand
        L.limb([(sx*2.1,-0.1,11.4),(sx*3.3,0.6,8.2),(sx*3.8,0.2,5.0),(sx*4.0,-0.4,3.2)],0.42,0.62,parts)
        for k in range(3): P(L.seg((sx*4.0,-0.4,3.2),(sx*(4.0+(k-1)*0.7),-1.2,1.3),0.16))          # twig fingers
    L.limb([(0,-0.4,12.2),(0,-0.7,13.4)],0.5,0.6,parts); P(S((0,-0.9,14.2),1.35)); P(C((0,-1.0,14.3),(2.3,2.1,2.1)))   # neck + head
    for k in range(9):   # BIG branch crown
        a=k/9*math.tau; tip=(math.cos(a)*2.4,-0.9+math.sin(a)*2.4,16.6+random.random()*0.8)
        P(L.seg((0,-0.9,15.0),tip,0.22)); P(L.seg(tip,(tip[0]*1.25,tip[1]*1.25-0.2,tip[2]+0.9),0.14))
    body=L.fuse(parts,voxel=0.12,disp=0.12,disp_scale=0.9,facet=0.05)
    body.data.materials.append(L.surface("bark",(0.24,0.15,0.08),(0.07,0.045,0.03),moss=(0.18,0.32,0.10),crack=TEAL_RGB,crack_str=3.0,crack_center=(0,-1.9,10.8),crack_radius=5.5,rough=0.95,bump=0.7,stripes=9.0,noise_scale=5.0))
    GOLD,TEAL,EYE=glows(); acc=[]
    o=S((0,-2.05,10.9),0.7); o.data.materials.append(TEAL); acc.append(o)                       # blossom heart (weak point)
    for k in range(5): o=C((-1.0+k*0.5,-2.35,10.9+math.sin(k*1.3)*0.45),(0.14,0.3,1.4),rot=(0,0,rad(10*((k%2)*2-1)))); o.data.materials.append(GOLD); acc.append(o)
    for sx in(-1,1): o=C((sx*0.5,-2.1,14.5),(0.45,0.3,0.22)); o.data.materials.append(EYE); acc.append(o)
    VINE=L.plain("vine",(0.10,0.18,0.06),0.9)
    for k in range(14):   # hanging vines from the crown and shoulders
        a=random.random()*math.tau; x=math.cos(a)*random.uniform(0.8,2.2); y=-0.9+math.sin(a)*random.uniform(0.8,2.2); z0=random.uniform(11.5,15.5)
        o=C((x,y,z0-random.uniform(1.5,3.2)/2),(0.08,0.08,random.uniform(1.5,3.2)),rot=(rad(random.uniform(-8,8)),rad(random.uniform(-8,8)),0)); o.data.materials.append(VINE); acc.append(o)
    L.embers(40,(0,-1,10),(6,5,8),[TEAL,L.glow("spore",(0.5,0.95,0.4),2.0)],0.02,0.05,seed=8)
    L.ground_cracks((0,0),n=9,mat=DIM(TEAL_RGB,1.2),seed=3,length=(2,7))
    pts=dict(pelvis=(0,0,3.4),spine0=(0,0,5.0),chest0=(0,-0.1,9.8),neck0=(0,-0.4,12.2),head0=(0,-0.7,13.4),head1=(0,-1.0,15.6),
             shoulder=(2.1,-0.1,11.4),elbow=(3.3,0.6,8.2),wrist=(3.8,0.2,5.0),hand=(4.0,-0.6,2.4),
             hip=(1.0,0,3.4),knee=(1.4,0,1.7),ankle=(2.0,0,0.5),toe=(2.5,-0.4,0.2))
    arm=R.humanoid_armature(pts); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=8.8,cam=(15,-21,9.0),lens=42,f=1,big="R")

# ---------------- CLAW: the Edgewalker (hovering blade-wraith, solid this time) ----------------
def edgewalker():
    L.reset(); random.seed(7); parts=[]; P=lambda o:(parts.append(o),o)[1]
    # --- feline proportions: shoulder height ~5.5, body ~6 long, deep chest, narrow waist, long legs ---
    P(S((0,-2.2,4.7),1.75)); P(S((0,0.4,4.75),1.15)); P(S((0,2.6,5.0),1.45))                     # chest / waist / hips
    P(C((0,0.2,4.85),(2.1,5.4,1.9))); P(C((0,0.4,5.7),(1.2,5.0,0.9)))                              # torso + arched spine ridge
    for sx in(-1,1): P(S((sx*1.25,-2.0,4.9),1.0)); P(S((sx*1.25,2.6,5.0),1.15))                   # shoulder muscle / haunch
    L.limb([(0,-3.4,4.95),(0,-5.0,5.75),(0,-6.4,6.05)],0.72,0.82,parts)                            # long neck, forward-up
    sk=S((0,-7.1,6.0),1.05); sk.scale=(1.0,1.2,0.85); P(sk)                                          # skull
    P(C((0,-8.2,5.6),(1.2,1.5,0.8))); P(C((0,-8.05,5.1),(1.0,1.3,0.45))); P(C((0,-7.5,6.55),(1.9,1.0,0.4)))   # muzzle, jaw, brow
    for sx in(-1,1): P(L.cone((sx*0.75,-6.6,7.1),0.3,1.1,None,rot=(rad(-25),rad(sx*18),0)))        # ears
    legs={}
    for nm,sx,pts in (("FL",-1,[(-1.2,-2.2,4.9),(-1.5,-2.6,3.0),(-1.55,-2.9,1.4),(-1.6,-3.4,0.35)]),
                      ("FR", 1,[( 1.2,-2.2,4.9),( 1.5,-2.6,3.0),( 1.55,-2.9,1.4),( 1.6,-3.4,0.35)]),
                      ("BL",-1,[(-1.2,2.6,5.0),(-1.5,3.4,2.9),(-1.55,3.0,1.3),(-1.6,2.5,0.35)]),
                      ("BR", 1,[( 1.2,2.6,5.0),( 1.5,3.4,2.9),( 1.55,3.0,1.3),( 1.6,2.5,0.35)])):
        L.limb(pts,0.36,0.48,parts); legs[nm]=pts
        px,py,pz=pts[-1]; P(C((px,py-0.25,0.3),(0.95,1.3,0.5)))                                     # paw
    L.limb([(0,4.0,5.0),(0,6.6,5.0),(0,9.2,5.6),(0,11.4,7.0),(0,12.6,9.2)],0.22,0.3,parts)             # long cat tail
    for k in range(7): P(L.cone((0,-2.0+k*0.85,6.25+(0.25 if 1<k<5 else 0.0)),0.22,1.2,None))         # blade ridge
    body=L.fuse(parts,voxel=0.09,disp=0.04,disp_scale=0.7,facet=0.06)
    body.data.materials.append(L.surface("obsidian",(0.11,0.11,0.15),(0.03,0.03,0.045),crack=TEAL_RGB,crack_str=2.8,crack_scale=0.6,crack_width=0.015,crack_center=(0,-5.6,5.1),crack_radius=3.6,metallic=0.4,rough=0.3,bump=0.28,noise_scale=7.0))
    GOLD,TEAL,EYE=glows(); acc=[]
    for sx in(-1,1): o=C((sx*0.5,-8.25,6.15),(0.5,0.35,0.24),rot=(0,0,rad(sx*-14))); o.data.materials.append(EYE); acc.append(o)   # eyes seated in the face
    for sx in(-1,1): o=L.cone((sx*0.33,-8.45,5.05),0.1,0.62,GOLD,rot=(rad(180),0,0)); acc.append(o)                                # fangs rooted in the jaw
    o=C((0,-5.6,5.15),(0.9,0.5,0.4),rot=(rad(28),0,0)); o.data.materials.append(GOLD); acc.append(o)                                # throat seam core
    for k in range(4): o=C((-0.45+k*0.3,-5.55,5.15+(k%2)*0.12),(0.08,0.28,0.8),rot=(rad(28),0,0)); o.data.materials.append(TEAL); acc.append(o)
    for nm,pts in legs.items():
        px,py,pz=pts[-1]
        for k in range(3): o=L.cone((px+(k-1)*0.3,py-0.95,0.25),0.09,0.7,GOLD,rot=(rad(84),0,0)); acc.append(o)                       # claw-blades
    for k in range(4): o=C((-1.5+k*1.0,-10.5,0.02),(0.12,3.0,0.03),rot=(0,0,rad(-18))); o.data.materials.append(DIM(TEAL_RGB,1.3))
    L.embers(28,(0,-3,5),(5,6,4),[TEAL,GOLD],0.02,0.05,seed=6)
    bones=[("root",(0,2.6,5.0),(0,0.4,4.75),None),("chest",(0,0.4,4.75),(0,-3.4,4.95),"root"),("neck",(0,-3.4,4.95),(0,-5.0,5.75),"chest"),("head",(0,-5.0,5.75),(0,-8.8,5.6),"neck"),
           ("tail1",(0,4.0,5.0),(0,6.6,5.0),"root"),("tail2",(0,6.6,5.0),(0,9.2,5.6),"tail1"),("tail3",(0,9.2,5.6),(0,12.6,9.2),"tail2")]
    for nm,pts in legs.items():
        par="chest" if nm[0]=="F" else "root"
        bones+=[(f"{nm}a",pts[0],pts[1],par),(f"{nm}b",pts[1],pts[2],f"{nm}a"),(f"{nm}c",pts[2],pts[3],f"{nm}b")]
    arm=R.custom_armature(bones); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=4.6,cam=(-11,-19,4.4),lens=45,f=1,big="R",custom="quad",target_xy=(0,-3.4))

# ---------------- SPARK: the Drumheart (brass drum-bodied brute) ----------------
def drumheart():
    L.reset(); random.seed(9); parts=[]; P=lambda o:(parts.append(o),o)[1]
    for sx in(-1,1):
        P(C((sx*1.6,0.1,0.7),(2.8,3.2,1.4))); P(Y((sx*1.6,0,2.6),1.15,3.6)); P(S((sx*1.6,0,4.2),1.35))
    P(S((0,0,4.8),2.0))
    P(Y((0,-0.2,7.2),3.2,4.4,rot=(rad(90),0,0)))                       # THE DRUM: big cylinder lying front-back
    P(Y((0,-0.2,7.2),3.5,0.8,rot=(rad(90),0,0)))                       # rim hoop
    P(C((0,-0.3,9.6),(6.6,3.6,1.4)))                                   # shoulder bar
    for sx in(-1,1):
        P(S((sx*3.6,-0.2,9.4),1.5)); P(Y((sx*4.1,0.2,6.6),1.0,4.6,rot=(0,rad(sx*8),0))); P(S((sx*4.5,0.5,3.4),2.1))   # arms + MALLET fists
    P(Y((0,-0.4,10.6),0.9,1.4)); P(S((0,-0.6,11.6),1.3)); P(C((0,-0.7,11.7),(2.4,2.2,1.9)))                             # head
    for k in range(3): P(L.cone((0,0.2-k*0.25,12.6+k*0.4),0.5,1.6,L.plain("z",(0,0,0)),rot=(rad(-30-k*10),0,0)))          # flame crest
    body=L.fuse(parts,voxel=0.14,disp=0.09,disp_scale=1.0,facet=0.05)
    body.data.materials.append(L.surface("brass",(0.55,0.36,0.14),(0.18,0.11,0.05),crack=(1.0,0.5,0.1),crack_str=3.0,crack_center=(0,-2.4,7.2),crack_radius=5.0,metallic=0.85,rough=0.42,bump=0.3,noise_scale=4.0))
    GOLD,TEAL,EYE=glows(); acc=[]
    o=Y((0,-2.55,7.2),2.6,0.18,rot=(rad(90),0,0)); o.data.materials.append(L.glow("skin",(1.0,0.62,0.15),1.6)); acc.append(o)   # glowing drum membrane = weak point
    o=L.ring((0,-2.6,7.2),2.65,0.12,TEAL,rot=(rad(90),0,0)); acc.append(o)
    for k in range(8):   # teal beat-lines radiating on the membrane
        a=k/8*math.tau; o=C((math.cos(a)*1.4,-2.7,7.2+math.sin(a)*1.4),(0.12,0.1,1.2),rot=(0,0,a)); o.data.materials.append(TEAL); acc.append(o)
    for sx in(-1,1): o=C((sx*0.6,-1.9,11.8),(0.55,0.4,0.3)); o.data.materials.append(EYE); acc.append(o)
    for k in range(3): o=L.ring((0,0,0.05+k*0.02),4.0+k*1.6,0.06,DIM(TEAL_RGB,1.0)); # shockwave rings on the ground
    L.embers(40,(0,-1,6),(6,4,7),[GOLD,L.glow("spark",(1.0,0.45,0.1),3.0)],0.02,0.07,seed=11)
    pts=dict(pelvis=(0,0,4.2),spine0=(0,0,5.4),chest0=(0,-0.2,8.0),neck0=(0,-0.4,9.9),head0=(0,-0.5,10.6),head1=(0,-0.7,12.6),
             shoulder=(3.6,-0.2,9.4),elbow=(4.1,0.2,6.4),wrist=(4.4,0.4,4.4),hand=(4.5,0.5,2.2),
             hip=(1.6,0,4.3),knee=(1.6,0,2.4),ankle=(1.6,0.05,1.0),toe=(1.6,-1.1,0.3))
    arm=R.humanoid_armature(pts); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=6.8,cam=(16,-18,6.5),lens=44,f=1,big="R")

BOSSES=dict(grindmaw=grindmaw,thornmother=thornmother,edgewalker=edgewalker,drumheart=drumheart)

def run(name,mode):
    b=BOSSES[name]()
    ls=b.get('light',1.0)
    cam,tgt=L.studio(target_z=b['target_z'],cam_loc=b['cam'],lens=b['lens'],fstop=2.8,teal=1200*ls,gold=900*ls,fill=900*ls,sun=4.2)
    if 'target_xy' in b: tgt.location.x,tgt.location.y=b['target_xy']
    sc=bpy.context.scene
    if mode=="hero":
        sc.cycles.samples=110; sc.render.resolution_x=820; sc.render.resolution_y=1025
        sc.render.filepath=f'{ART}/renders/{name}_hero.png'; bpy.ops.render.render(write_still=True); print("HERO",name,"DONE")
    else:
        for kind in mode.split(","):
            d=f'{ART}/renders/{name}_{kind}'
            need={'idle':48,'walk':32,'attack':40,'death':48}[kind]
            if os.path.isdir(d) and len([x for x in os.listdir(d) if x.endswith('.png')])>=need: print('SKIP',name,kind); continue
            cu=b.get('custom')
            if cu=='spider': PRO.spider(b['arm'],kind,legs=b.get('legs',8))
            elif cu=='quad': PRO.quad(b['arm'],kind)
            elif cu=='tower':
                PRO.tower(b['arm'],kind)
                n=bpy.context.scene.frame_end
                for i,dn in enumerate(b.get('drones',[])):   # continuous orbit + bob; surge outward on attack
                    x0,y0,z0=dn.location; a0=math.atan2(y0,x0); r0=math.hypot(x0,y0)
                    for fr in range(1,n+1):
                        t=(fr-1)/(n-1); surge=(0.9*math.sin(math.pi*min(1,max(0,(t-0.3)/0.4))) if kind=='attack' and 0.3<t<0.7 else 0.0)
                        a=a0+t*math.tau*(1.0 if kind!='idle' else 0.5); rr=r0*(1+surge)
                        dn.location=(math.cos(a)*rr,math.sin(a)*rr,z0+0.35*math.sin(t*math.tau*2+i)); dn.rotation_euler=(0,0,a+math.pi/2); dn.keyframe_insert('location',frame=fr); dn.keyframe_insert('rotation_euler',frame=fr)
                        for w in dn.children:
                            if 'flap' in w: w.rotation_euler=(w['flap']*0.55*math.sin(fr*2.4), 0, w.rotation_euler.z); w.keyframe_insert('rotation_euler',frame=fr)
            else: PRO.humanoid(b['arm'],kind,f=b['f'],big=b['big'],heavy=b.get('heavy',1.0))
            n=bpy.context.scene.frame_end
            for j,w in enumerate(b.get('wards',[])):     # spin about own normal; flare then shatter (scale to 0) in death
                rx,ry=w['tilt']; turns={'idle':1,'walk':1,'attack':2,'death':1}[kind]*(1 if j%2 else -1)
                for fr in range(1,n+1):
                    t=(fr-1)/(n-1)
                    w.rotation_euler=(rx,ry,t*math.tau*turns); w.keyframe_insert('rotation_euler',frame=fr)
                    if kind=='death':
                        sc_=1.0 if t<0.3 else (1.0+0.25*math.sin(math.pi*(t-0.3)/0.15) if t<0.45 else max(0.0,1.0-(t-0.45)/0.3))
                        w.scale=(sc_,sc_,sc_); w.keyframe_insert('scale',frame=fr)
                    elif kind=='attack':
                        sc_=1.0+0.18*math.sin(math.pi*max(0,min(1,(t-0.3)/0.4))); w.scale=(sc_,sc_,sc_); w.keyframe_insert('scale',frame=fr)
            sc.cycles.samples=8; sc.render.resolution_x=360; sc.render.resolution_y=450; cam.data.dof.use_dof=False
            cam.data.lens=b['lens']*(0.78 if kind=='death' else 1.0); tgt.location.z=b['target_z']*(0.72 if kind=='death' else 1.0)
            os.makedirs(d,exist_ok=True); sc.render.filepath=d+'/f_'
            bpy.ops.render.render(animation=True); print("CLIP",name,kind,"DONE")

# ---------------- CLOCK: the Cogwright (clockwork spider) ----------------
def cogwright():
    L.reset(); random.seed(12); parts=[]; P=lambda o:(parts.append(o),o)[1]
    Z=4.2  # body height
    P(Y((0,0,Z),2.6,2.6,rot=(rad(90),0,0))); P(S((0,0,Z+0.6),2.3))                      # gear-drum abdomen + dome
    P(Y((0,-2.9,Z-0.2),1.6,2.2,rot=(rad(90),0,0))); P(S((0,-3.6,Z-0.1),1.5))            # thorax + head turret
    P(Y((0,-4.6,Z-0.1),0.9,1.2,rot=(rad(90),0,0)))                                     # lens housing
    for k in range(12):   # big gear teeth around the abdomen (fused) + a second gear on the back
        a=k/12*math.tau; P(C((math.cos(a)*2.7,0,Z+math.sin(a)*2.7),(0.6,1.4,0.7),rot=(0,a,0)))
    P(Y((0,1.8,Z+1.6),1.5,0.6,rot=(rad(90),0,0)))
    for k in range(10): a=k/10*math.tau; P(C((math.cos(a)*1.55,1.8,Z+1.6+math.sin(a)*1.55),(0.4,0.6,0.4),rot=(0,a,0)))
    legs=[]
    for i in range(8):
        side=-1 if i<4 else 1; j=i%4
        hip=(side*1.9, -1.8+j*1.3, Z-0.2); knee=(side*4.6, -2.6+j*1.75, Z+2.2); tip=(side*6.4,-3.2+j*2.1,0.0)
        P(S(hip,0.7)); P(Y(((hip[0]+knee[0])/2,(hip[1]+knee[1])/2,(hip[2]+knee[2])/2),0.42,4.0,rot=L_rot(hip,knee)))
        P(S(knee,0.6)); P(Y(((knee[0]+tip[0])/2,(knee[1]+tip[1])/2,(knee[2]+tip[2])/2),0.3,5.0,rot=L_rot(knee,tip)))
        legs.append((hip,knee,tip))
    body=L.fuse(parts,voxel=0.13,disp=0.05,disp_scale=0.7,facet=0.06)
    body.data.materials.append(L.surface("clockbrass",(0.48,0.30,0.12),(0.14,0.09,0.05),crack=TEAL_RGB,crack_str=3.0,crack_center=(0,0,Z-2.0),crack_radius=4.5,metallic=0.9,rough=0.38,bump=0.35,noise_scale=5.0))
    GOLD,TEAL,EYE=glows(); acc=[]
    o=Y((0,-5.35,Z-0.1),0.7,0.25,rot=(rad(90),0,0)); o.data.materials.append(L.glow("lens",(1.0,0.8,0.3),2.2)); acc.append(o)   # single gold lens eye
    o=L.ring((0,-5.4,Z-0.1),0.85,0.1,L.plain("bezel",(0.2,0.14,0.06),0.5,0.9),rot=(rad(90),0,0)); acc.append(o)
    o=Y((0,0,Z-2.7),1.3,0.25,rot=(rad(0),0,0)); o.data.materials.append(TEAL); acc.append(o)                     # PENDULUM CORE under the belly (weak point)
    o=Y((0,0,Z-1.6),0.12,2.2); o.data.materials.append(GOLD); acc.append(o)                                       # pendulum rod
    BR=L.plain("gearbrass",(0.5,0.32,0.12),0.45,0.9)
    o=L.ring((0,2.35,Z+1.6),1.9,0.22,BR,rot=(rad(90),0,0)); acc.append(o)   # big spoked back-gear (accent, keeps its teeth)
    for k in range(12): a=k/12*math.tau; o=C((math.cos(a)*2.05,2.35,Z+1.6+math.sin(a)*2.05),(0.5,0.4,0.5),rot=(0,a,0)); o.data.materials.append(BR); acc.append(o)
    for k in range(6): a=k/6*math.tau; o=C((math.cos(a)*0.9,2.35,Z+1.6+math.sin(a)*0.9),(0.18,0.3,1.8),rot=(0,a,0)); o.data.materials.append(BR); acc.append(o)
    o=Y((0,2.35,Z+1.6),0.45,0.5,rot=(rad(90),0,0)); o.data.materials.append(GOLD); acc.append(o)
    for k in range(3): L.ring((0,0,0.04),3.5+k*1.5,0.05,DIM(GOLD_RGB,0.9))
    L.embers(30,(0,0,Z),(7,6,4),[GOLD,TEAL],0.02,0.06,seed=13)
    bones=[("root",(0,0.5,Z),(0,-2.5,Z),None),("head",(0,-2.5,Z),(0,-5.0,Z),"root")]
    for i,(hip,knee,tip) in enumerate(legs): bones+=[(f"leg{i}a",hip,knee,"root"),(f"leg{i}b",knee,tip,f"leg{i}a")]
    arm=R.custom_armature(bones); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=Z-0.2,cam=(15,-17,7.5),lens=42,f=1,big="R",custom="spider")
def L_rot(a,b):
    import mathutils
    v=mathutils.Vector((b[0]-a[0],b[1]-a[1],b[2]-a[2])); return v.to_track_quat('Z','Y').to_euler()

# ---------------- SWARM: the Hivemind (waxy hive tower + drone swarm) ----------------
def hivemind():
    L.reset(); random.seed(21); parts=[]; P=lambda o:(parts.append(o),o)[1]
    P(Y((0,0,0.9),3.4,1.8)); P(S((0,0,2.4),3.0)); P(S((0.3,-0.2,4.6),2.7)); P(S((-0.2,0.2,6.6),2.4)); P(S((0.2,-0.3,8.4),2.1))   # stacked hive lobes
    for i in range(12):
        a=random.random()*math.tau; z=1.5+random.random()*7.0; r=(3.0-0.2*z)*0.95
        P(S((math.cos(a)*r,math.sin(a)*r,z),0.5+random.random()*0.45))
    # QUEEN HEAD on top: a big readable head lobe, brow ridge, two antennae, mandibles
    P(S((0,-0.6,10.3),2.0)); P(C((0,-1.6,10.9),(3.2,1.4,1.0))); P(C((0,-0.4,11.9),(2.6,2.4,0.8)))
    for sx in(-1,1):
        P(Y((sx*1.1,-0.8,13.0),0.16,2.6,rot=(rad(-25),rad(sx*30),0))); P(S((sx*1.7,-1.6,14.1),0.32))            # antennae + knobs
        P(L.cone((sx*0.9,-2.6,9.4),0.32,1.5,None,rot=(rad(75),0,rad(sx*15))))                                    # mandibles
    body=L.fuse(parts,voxel=0.13,disp=0.07,disp_scale=1.2,facet=0.06)
    body.data.materials.append(L.surface("hivewax",(0.62,0.42,0.12),(0.24,0.13,0.04),crack=GOLD_RGB,crack_str=2.0,crack_scale=0.45,crack_width=0.014,crack_center=(0,-2.0,6.0),crack_radius=5.0,rough=0.5,bump=0.4,sheen=0.4,noise_scale=4.0))
    GOLD,TEAL,EYE=glows(); acc=[]
    for sx in(-1,1): o=S((sx*0.75,-2.35,10.5),0.42); o.data.materials.append(EYE); acc.append(o)                # two big compound eyes
    o=Y((0,-2.55,5.6),1.1,0.5,rot=(rad(90),0,0)); o.data.materials.append(L.glow("royal",(1.0,0.55,0.1),2.6)); acc.append(o)   # ROYAL CHAMBER: glowing hex mouth in the belly (weak point)
    o=L.ring((0,-2.6,5.6),1.25,0.12,L.plain("rim",(0.12,0.07,0.02),0.7),rot=(rad(90),0,0)); acc.append(o)
    # bee drones: thorax + striped abdomen + head with glowing eyes, six legs, stinger, two flapping wings (keyed in run())
    def band_mat(name,a,b,scale):
        m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; p=nt.nodes["Principled BSDF"]; p.inputs["Roughness"].default_value=0.5
        tc=nt.nodes.new("ShaderNodeTexCoord"); wv=nt.nodes.new("ShaderNodeTexWave"); wv.wave_type='BANDS'; wv.bands_direction='X'
        wv.inputs["Scale"].default_value=scale; wv.inputs["Distortion"].default_value=0.2; wv.inputs["Detail"].default_value=1
        cr=nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position=0.45; cr.color_ramp.elements[1].position=0.55
        cr.color_ramp.elements[0].color=(*a,1); cr.color_ramp.elements[1].color=(*b,1)
        nt.links.new(tc.outputs["Object"],wv.inputs["Vector"]); nt.links.new(wv.outputs["Fac"],cr.inputs["Fac"]); nt.links.new(cr.outputs["Color"],p.inputs["Base Color"]); return m
    BEE=band_mat("beebands",(0.9,0.65,0.12),(0.05,0.04,0.02),4.0); FUZZ=L.plain("beefuzz",(0.45,0.32,0.08),0.9); BLK=L.plain("beeblk",(0.04,0.04,0.04),0.5)
    WING=L.glass("beewing",(0.6,0.9,0.9),0.08); WING.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value=0.45
    drones=[]
    for i in range(16):
        a=i/16*math.tau; r=4.6+random.random()*1.6; z=3+random.random()*8
        bpy.ops.object.empty_add(location=(math.cos(a)*r,math.sin(a)*r,z)); d=bpy.context.object; d.rotation_euler=(0,0,a+math.pi/2); d.empty_display_size=0.1
        def part(o):
            o.parent=d; o.matrix_parent_inverse=d.matrix_world.inverted(); return o
        M=d.matrix_world
        def lp(x,y,zz): v=M@mathutils.Vector((x,y,zz)); return (v.x,v.y,v.z)
        ab=S(lp(-0.30,0,0),0.36); ab.scale=(1.5,1.0,0.9); ab.rotation_euler=d.rotation_euler; ab.data.materials.append(BEE); part(ab)          # striped abdomen
        th=S(lp(0.25,0,0.04),0.27); th.data.materials.append(FUZZ); part(th)                                                              # fuzzy thorax
        hd=S(lp(0.58,0,0.02),0.2); hd.data.materials.append(BLK); part(hd)                                                                 # head
        for sy in(-1,1):
            e=S(lp(0.7,sy*0.12,0.08),0.07); e.data.materials.append(EYE); part(e)                                                        # glowing eyes
            an=Y(lp(0.78,sy*0.08,0.3),0.02,0.35,rot=(sy*rad(30),rad(-30),0)); an.data.materials.append(BLK); part(an)                     # antennae
            for k in range(3):
                lg=Y(lp(0.3-0.25*k,sy*0.3,-0.22),0.03,0.45,rot=(sy*rad(35),0,0)); lg.data.materials.append(BLK); part(lg)                # legs
            w=C(lp(0.15,sy*0.42,0.30),(1.05,0.5,0.03)); w.rotation_euler=(0,0,a+math.pi/2+sy*0.45); w.data.materials.append(WING); part(w) # wings
            w.name=f"wing_{i}_{sy}"; w['flap']=sy
        st=L.cone(lp(-0.9,0,-0.02),0.08,0.28,TEAL,rot=(0,rad(-90)+0,a+math.pi/2)); part(st)                                              # stinger
        drones.append(d)
    L.embers(30,(0,0,6),(6,6,6),[GOLD,L.glow("honey",(1.0,0.6,0.15),2.0)],0.02,0.05,seed=22)
    L.ground_cracks((0,0),n=8,mat=DIM(GOLD_RGB,1.0),seed=7,length=(2,7))
    bones=[("base",(0,0,0.5),(0,0,4.0),None),("mid",(0,0,4.0),(0,0,7.5),"base"),("top",(0,0,7.5),(0,0,10.0),"mid"),("face",(0,-0.4,10.0),(0,-1.6,12.4),"top")]
    arm=R.custom_armature(bones); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=6.4,cam=(16,-18,7.4),lens=42,f=1,big="R",custom="tower",drones=drones)

# ---------------- SIGIL: the Sealbreaker (robed sigil-stone mage) ----------------
def sealbreaker():
    L.reset(); random.seed(31); parts=[]; P=lambda o:(parts.append(o),o)[1]
    P(L.cone((0,0,3.2),2.8,6.4,None)); P(Y((0,0,6.6),1.4,2.4)); P(S((0,-0.2,8.2),1.7)); P(C((0,-0.2,8.9),(4.4,2.4,1.2)))   # robe cone, waist, chest, shoulder bar
    for sx in(-1,1):
        P(S((sx*2.2,-0.1,8.8),0.9)); P(L.cone((sx*3.0,0.5,6.0),1.0,5.2,None,rot=(rad(-16),rad(sx*-18),0)))                  # wide hanging sleeves
        P(S((sx*3.6,-0.8,3.6),0.75))                                                                                        # floating hands
    P(Y((0,-0.3,9.9),0.6,1.2)); P(S((0,-0.4,10.9),1.25)); P(L.cone((0,-0.1,11.8),1.7,3.2,None))                              # neck, head, HOOD
    P(Y((3.6,-1.2,5.5),0.18,10.0)); P(S((3.6,-1.2,10.6),0.7))                                                                # staff + orb
    body=L.fuse(parts,voxel=0.12,disp=0.08,disp_scale=1.0,facet=0.06)
    body.data.materials.append(L.surface("sigilstone",(0.16,0.15,0.2),(0.05,0.045,0.07),crack=GOLD_RGB,crack_str=3.6,crack_scale=0.7,crack_width=0.02,crack_center=(0,-1.8,7.6),crack_radius=5.5,rough=0.8,bump=0.4,noise_scale=4.0))
    GOLD,TEAL,EYE=glows(); acc=[]
    o=C((0,-2.05,7.6),(1.6,0.3,1.6)); o.data.materials.append(GOLD); acc.append(o)                     # CHEST SIGIL PLATE (weak point)
    for k in range(4): a=k/4*math.tau+0.6; o=C((math.cos(a)*0.55,-2.25,7.6+math.sin(a)*0.55),(0.22,0.2,0.9),rot=(0,0,a)); o.data.materials.append(TEAL); acc.append(o)
    o=C((0,-1.55,11.0),(0.9,0.3,0.25)); o.data.materials.append(EYE); acc.append(o)                    # single eye-slit in the hood's dark
    o=S((3.6,-1.2,10.6),0.55); o.data.materials.append(TEAL); acc.append(o)                            # staff orb glow
    # orbiting ward rings with rune cubes: each ring is a spinning unit (rune cubes parented to it), all ride the chest bone
    wards=[]
    for k,(rx,ry) in enumerate(((0,0),(rad(60),rad(20)),(rad(-50),rad(70)))):
        rg=L.ring((0,-0.3,7.2),4.2+k*0.5,0.07,TEAL if k%2 else GOLD,rot=(rx,ry,0)); rg.rotation_mode='ZYX'; rg['tilt']=(rx,ry); wards.append(rg); acc.append(rg)
        for j in range(6):
            a=j/6*math.tau; v=mathutils.Vector((math.cos(a)*(4.2+k*0.5),math.sin(a)*(4.2+k*0.5),0)); v.rotate(mathutils.Euler((rx,ry,0)))
            o=C((v.x,v.y-0.3,v.z+7.2),(0.35,0.35,0.35),rot=(rx,ry,a)); o.data.materials.append(GOLD if k%2 else TEAL)
            o.parent=rg; o.matrix_parent_inverse=rg.matrix_world.inverted()
    L.embers(30,(0,-1,7),(5,4,6),[GOLD,TEAL],0.02,0.06,seed=33); L.ground_cracks((0,0),n=8,mat=GOLD,seed=31,length=(2,6))
    pts=dict(pelvis=(0,0,3.6),spine0=(0,0,5.0),chest0=(0,-0.2,7.4),neck0=(0,-0.3,9.3),head0=(0,-0.4,10.0),head1=(0,-0.2,13.0),
             shoulder=(2.2,-0.1,8.8),elbow=(3.0,0.3,6.4),wrist=(3.4,-0.4,4.4),hand=(3.6,-0.9,3.0),
             hip=(0.9,0,3.6),knee=(1.0,0,1.9),ankle=(1.1,0,0.7),toe=(1.1,-0.8,0.2))
    arm=R.humanoid_armature(pts); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=7.0,cam=(15,-18,7.4),lens=42,f=1,big="R",wards=wards)

# ---------------- SPINDLE: the Unwoven (finale loom-wraith) ----------------
def unwoven():
    L.reset(); random.seed(41); parts=[]; P=lambda o:(parts.append(o),o)[1]
    P(L.cone((0,0,2.2),2.2,4.4,None)); P(L.cone((0,0,6.4),2.0,4.2,None,rot=(rad(180),0,0)))       # spindle body: two cones point-to-point at the waist
    P(S((0,0,4.3),0.9)); P(S((0,-0.2,8.4),1.9)); P(C((0,-0.2,9.2),(4.6,2.2,1.2)))                    # waist knot, chest, shoulder bar
    for sx in(-1,1):
        P(S((sx*2.3,-0.1,9.0),0.85)); P(Y((sx*3.0,0.3,6.8),0.5,4.4,rot=(rad(8),rad(sx*16),0))); P(S((sx*3.6,0.6,4.6),0.7)); P(Y((sx*4.0,0.9,2.9),0.4,3.4,rot=(rad(-10),rad(sx*8),0))); P(S((sx*4.3,0.6,1.3),0.75))
    P(Y((0,-0.3,10.2),0.55,1.2)); P(Y((0,-0.3,11.4),1.1,2.0)); P(Y((0,-0.3,12.6),1.5,0.5)); P(Y((0,-0.3,10.6),1.5,0.5))   # BOBBIN head (spool with flanges)
    body=L.fuse(parts,voxel=0.12,disp=0.05,disp_scale=0.8,facet=0.06)
    body.data.materials.append(L.surface("loomthread",(0.10,0.08,0.20),(0.03,0.02,0.07),crack=TEAL_RGB,crack_str=3.4,crack_scale=0.6,crack_width=0.02,crack_center=(0,-2.0,8.2),crack_radius=6.0,rough=0.75,bump=0.5,stripes=16.0,noise_scale=6.0,sheen=0.5))
    # loom frame behind: STATIC scenery (separate solid), the warp threads run to it
    FR=L.plain("loomwood",(0.16,0.12,0.09),0.8)
    for o in (L.cyl((-4.6,2.2,6.5),0.35,13.0),L.cyl((4.6,2.2,6.5),0.35,13.0),L.cube((0,2.2,13.0),(9.6,0.7,0.7))): o.data.materials.append(FR)
    GOLD,TEAL,EYE=glows(); acc=[]
    o=C((0,-2.05,8.2),(1.9,0.5,0.8),rot=(0,0,rad(0))); o.data.materials.append(GOLD); acc.append(o)              # the SHUTTLE in the chest (weak point)
    for k in range(5): o=C((-1.0+k*0.5,-2.3,8.2+math.sin(k*1.4)*0.45),(0.12,0.25,1.6),rot=(0,0,rad(10*((k%2)*2-1)))); o.data.materials.append(TEAL); acc.append(o)
    for sx in(-1,1): o=C((sx*0.45,-1.45,11.4),(0.4,0.3,0.2)); o.data.materials.append(EYE); acc.append(o)
    # WARP THREADS: many taut strands from the crossbar down to the ground and into the body
    for k in range(26):
        x=-4.2+k*0.336; o=C((x,2.2,6.5),(0.035,0.035,12.6)); o.data.materials.append(TEAL if k%3 else GOLD)
    # loose threads trailing from the arms
    for sx in(-1,1):
        for k in range(5): o=C((sx*(4.3+k*0.12),0.6+k*0.15,0.7),(0.04,0.04,1.3+k*0.3),rot=(rad(random.uniform(-15,15)),rad(random.uniform(-15,15)),0)); o.data.materials.append(TEAL); acc.append(o)
    L.embers(45,(0,0,7),(6,4,7),[TEAL,GOLD],0.02,0.06,seed=44); L.ground_cracks((0,0),n=10,mat=TEAL,seed=41,length=(2,8))
    pts=dict(pelvis=(0,0,3.8),spine0=(0,0,4.6),chest0=(0,-0.2,7.6),neck0=(0,-0.3,9.6),head0=(0,-0.3,10.3),head1=(0,-0.3,12.8),
             shoulder=(2.3,-0.1,9.0),elbow=(3.5,0.5,4.8),wrist=(4.1,0.8,2.2),hand=(4.3,0.6,0.8),
             hip=(0.8,0,3.8),knee=(1.0,0,2.0),ankle=(1.1,0,0.7),toe=(1.1,-0.8,0.2))
    arm=R.humanoid_armature(pts); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=7.0,cam=(16,-19,7.6),lens=40,f=1,big="R")

BOSSES.update(cogwright=cogwright,hivemind=hivemind,sealbreaker=sealbreaker,unwoven=unwoven)

# ---------------- SOIL: the Beddown (calibrated, in the factory) ----------------
def beddown():
    L.reset(); random.seed(4); parts=[]; P=lambda o:(parts.append(o),o)[1]
    for sx in(-1,1):
        P(C((sx*1.5,0.2,0.75),(3.2,3.6,1.5))); P(Y((sx*1.5,0,2.9),1.25,4.2)); P(S((sx*1.5,0,4.8),1.45))
    P(C((0,0,5.0),(5.2,3.4,2.4))); P(S((0,-0.3,7.0),3.0)); P(C((0,-0.4,7.2),(6.2,3.6,4.2))); P(S((0,-1.3,6.3),2.0)); P(C((0,-0.6,9.1),(6.4,3.8,1.4)))
    for sx in(-1,1):
        P(S((sx*3.3,-0.3,8.6),1.75)); P(Y((sx*3.7,0.0,5.6),1.05,5.4,rot=(0,rad(sx*6),0))); P(S((sx*3.95,0.3,2.6),1.5)); P(S((sx*4.1,0.5,1.7),1.85 if sx>0 else 1.6))
    P(Y((0,-0.6,9.9),1.1,1.6)); P(S((0,-0.8,11.0),1.75)); P(C((0,-0.9,11.0),(3.2,3.0,2.6))); P(C((0,-2.0,11.5),(3.3,0.9,0.9))); P(C((0,-0.3,12.4),(2.6,2.4,0.7)))
    for sx in(-1,1):
        P(C((sx*3.4,-0.5,9.5),(2.4,2.6,1.1),rot=(0,rad(sx*-12),0))); P(C((sx*3.9,0.4,4.6),(1.7,1.9,3.2),rot=(rad(8),0,rad(sx*10)))); P(C((sx*1.6,-0.9,2.4),(1.9,1.4,2.6),rot=(rad(-10),0,0)))
    P(C((0,-1.9,8.1),(4.4,1.2,1.6),rot=(rad(-12),0,0))); P(C((0,1.0,7.6),(4.6,1.8,3.6),rot=(rad(14),0,0))); P(C((0,-0.9,12.0),(3.6,2.2,0.9),rot=(rad(-8),0,0)))
    body=L.fuse(parts,voxel=0.14,disp=0.22,disp_scale=1.5,facet=0.045)
    body.data.materials.append(L.surface("beddown_rock",(0.20,0.13,0.08),(0.07,0.045,0.03),moss=(0.16,0.28,0.09),crack=TEAL_RGB,crack_str=3.5,crack_scale=0.5,crack_width=0.018,crack_center=(0,-2.5,6.5),crack_radius=5.0,rough=0.92,bump=0.45))
    GOLD,TEAL,EYE=glows(); acc=[]
    o=C((0,-3.35,6.5),(2.8,0.9,1.2)); o.data.materials.append(GOLD); acc.append(o)
    for k in range(6):
        o=C((-1.9+k*0.76,-3.6,6.5+math.sin(k*1.1)*0.55),(0.22,0.35,1.9+(k%2)*0.5),rot=(0,0,rad(12*((k%2)*2-1)))); o.data.materials.append(TEAL); acc.append(o)
    for sx in(-1,1): o=C((sx*0.75,-2.45,11.15),(0.75,0.4,0.32)); o.data.materials.append(EYE); acc.append(o)
    for k in range(3): o=Y((4.1,0.5,1.0+k*0.55),1.95,0.09); o.data.materials.append(TEAL); acc.append(o)
    L.ground_cracks((0,0),n=12,mat=DIM(TEAL_RGB,1.2),seed=9,length=(3,9)); L.embers(35,(0,-1,6),(6,4,6),[TEAL,GOLD],0.02,0.06,seed=2)
    pts=dict(pelvis=(0,0,4.4),spine0=(0,0,5.7),chest0=(0,-0.3,7.7),neck0=(0,-0.5,9.4),head0=(0,-0.7,10.2),head1=(0,-0.8,12.6),
             shoulder=(3.3,-0.3,8.7),elbow=(3.8,0.1,5.4),wrist=(3.95,0.3,2.7),hand=(4.1,0.5,0.9),
             hip=(1.5,0,4.9),knee=(1.5,0,2.8),ankle=(1.5,0.05,1.0),toe=(1.5,-1.2,0.3))
    arm=R.humanoid_armature(pts); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=6.4,cam=(15,-17.5,5.6),lens=44,f=1,big="R")
BOSSES.update(beddown=beddown)

# ---------------- EASY: the Lint Golem (Dock tutorial — soft lumpy wool thing) ----------------
def lintgolem():
    L.reset(); random.seed(51); parts=[]; P=lambda o:(parts.append(o),o)[1]
    for sx in(-1,1): P(S((sx*0.8,0,0.7),0.75)); P(S((sx*0.8,0,1.6),0.7))                     # stubby legs
    P(S((0,0,2.9),1.7)); P(S((0.2,-0.3,3.6),1.5)); P(S((-0.3,0.2,4.2),1.35))                   # lumpy body
    for i in range(10): a=random.random()*math.tau; z=1.8+random.random()*3.2; P(S((math.cos(a)*1.3,math.sin(a)*1.3,z),0.45+random.random()*0.4))  # fluff lumps
    for sx in(-1,1): L.limb([(sx*1.7,-0.2,4.0),(sx*2.5,0.2,2.6),(sx*2.7,-0.2,1.4)],0.42,0.55,parts)   # stubby arms
    P(S((0,-0.4,5.5),1.2)); P(S((0.4,-0.6,6.0),0.7))                                           # head + tuft
    body=L.fuse(parts,voxel=0.12,disp=0.14,disp_scale=0.5,facet=0.05)
    body.data.materials.append(L.surface("lint",(0.55,0.56,0.58),(0.22,0.24,0.3),crack=TEAL_RGB,crack_str=1.6,crack_scale=0.7,crack_center=(0,-1.6,3.6),crack_radius=2.5,rough=1.0,bump=0.6,stripes=22.0,noise_scale=9.0,sheen=0.9))
    GOLD,TEAL,EYE=glows(); acc=[]
    for sx in(-1,1): o=S((sx*0.42,-1.5,5.6),0.24); o.data.materials.append(EYE); acc.append(o)  # button eyes
    o=C((0,-1.9,3.5),(0.7,0.3,0.4)); o.data.materials.append(GOLD); acc.append(o)                # small seam
    for k in range(3): o=C((-0.3+k*0.3,-2.0,3.5),(0.08,0.2,0.9),rot=(0,0,rad(8*((k%2)*2-1)))); o.data.materials.append(TEAL); acc.append(o)
    o=C((0.9,-1.0,2.2),(0.05,0.05,2.6),rot=(rad(15),rad(20),0)); o.data.materials.append(TEAL); acc.append(o)   # loose trailing thread
    L.embers(24,(0,-0.5,3.5),(3,3,3),[L.glow("fluff",(0.8,0.8,0.85),0.6),TEAL],0.03,0.07,seed=52)
    pts=dict(pelvis=(0,0,2.0),spine0=(0,0,2.8),chest0=(0,-0.2,3.9),neck0=(0,-0.3,4.7),head0=(0,-0.4,5.0),head1=(0,-0.5,6.6),
             shoulder=(1.7,-0.2,4.0),elbow=(2.5,0.2,2.6),wrist=(2.6,0,1.9),hand=(2.7,-0.2,1.2),
             hip=(0.8,0,2.0),knee=(0.8,0,1.2),ankle=(0.8,0,0.5),toe=(0.8,-0.7,0.2))
    arm=R.humanoid_armature(pts); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=3.4,cam=(8,-9,3.6),lens=45,f=1,big="R",heavy=1.3)

# ---------------- EASY: the Tangle (rolling knot of cords with rope tentacles) ----------------
def tangle():
    L.reset(); random.seed(61); parts=[]; P=lambda o:(parts.append(o),o)[1]
    Z=3.4
    P(S((0,0,Z),1.7))                                                                        # fused core (darker, cords wrap it)
    loops=[]
    for i in range(16):   # thick rope loops crisscrossing into a knot — kept as separate crisp cords
        a=random.random()*math.tau; b=random.random()*math.pi; r=1.75+random.random()*0.5
        loops.append(L.ring((random.uniform(-0.25,0.25),random.uniform(-0.25,0.25),Z+random.uniform(-0.25,0.25)),r,0.34,None,rot=(b,0,a)))
    for i in range(10):   # cords threaded straight through the ball
        a=random.random()*math.tau; b=random.random()*math.pi
        p=(math.cos(a)*math.sin(b)*2.6,math.sin(a)*math.sin(b)*2.6,Z+math.cos(b)*2.6); q=(-p[0]*0.9,-p[1]*0.9,2*Z-p[2]*0.9+0.2)
        parts.append(L.seg(p,q,0.36))
    tent=[]
    for i in range(5):   # rope tentacles out of the knot, ending in frayed tips
        a=i/5*math.tau+0.4; pts=[(math.cos(a)*1.8,math.sin(a)*1.8,Z+0.3),(math.cos(a)*4.0,math.sin(a)*4.0,Z+1.4+math.sin(i*2)*0.7),(math.cos(a)*5.8,math.sin(a)*5.8,0.4)]
        L.limb(pts,0.34,0.44,parts); tent.append(pts)
        for k in range(4): P(L.cone((pts[2][0]+math.cos(a+k*1.5)*0.25,pts[2][1]+math.sin(a+k*1.5)*0.25,0.5),0.09,0.9,None,rot=(rad(random.uniform(-40,40)),rad(random.uniform(-40,40)),0)))
    for i in range(7):   # loose cord ends dangling off the knot
        a=random.random()*math.tau; p=(math.cos(a)*2.3,math.sin(a)*2.3,Z-0.6+random.random()*1.2); q=(p[0]*1.25,p[1]*1.25,max(0.15,p[2]-2.4)); m=((p[0]+q[0])/2+random.uniform(-0.4,0.4),(p[1]+q[1])/2+random.uniform(-0.4,0.4),(p[2]+q[2])/2)
        L.limb([p,m,q],0.16,0.2,parts)
    body=L.fuse(parts,voxel=0.11,disp=0.04,disp_scale=0.5,facet=0.08)
    ROPEM=L.surface("rope",(0.66,0.50,0.28),(0.30,0.21,0.10),crack=TEAL_RGB,crack_str=0.8,crack_scale=0.9,crack_center=(0,-2.2,Z),crack_radius=2.0,rough=0.72,bump=0.25,stripes=0.0,noise_scale=2.5)
    body.data.materials.append(L.surface("ropecore",(0.30,0.21,0.11),(0.10,0.07,0.04),crack=TEAL_RGB,crack_str=1.2,crack_scale=0.9,crack_center=(0,-2.2,Z),crack_radius=2.4,rough=0.9,bump=0.5,stripes=12.0,noise_scale=6.0))
    GOLD,TEAL,EYE=glows(); acc=[]
    for o in loops:
        o.data.materials.clear(); o.data.materials.append(ROPEM); bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.shade_smooth(); acc.append(o)
    for sx in(-1,1): o=S((sx*0.8,-2.45,Z+0.6),0.46); o.data.materials.append(EYE); acc.append(o)  # eyes peering out of the knot
    o=S((0,-2.35,Z-0.5),0.55); o.data.materials.append(GOLD); acc.append(o)                       # the gold knot-core, visible in a gap
    L.embers(24,(0,0,Z),(5,5,3),[TEAL,L.glow("fiber",(0.9,0.75,0.5),0.8)],0.02,0.05,seed=62)
    bones=[("root",(0,0.6,Z),(0,-1.6,Z),None),("head",(0,-1.6,Z),(0,-2.8,Z),"root")]
    for i,pts in enumerate(tent): bones+=[(f"leg{i}a",pts[0],pts[1],"root"),(f"leg{i}b",pts[1],pts[2],f"leg{i}a")]
    arm=R.custom_armature(bones); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=Z-0.2,cam=(12,-14,5.5),lens=42,f=1,big="R",custom="spider",legs=5)

def player_figure(loc):
    """a player-sized reference silhouette (~2 units tall) for the colossal bosses"""
    M=L.plain("player",(0.35,0.55,0.7),0.6)
    for o in (L.cube((loc[0],loc[1],loc[2]+1.1),(0.5,0.28,0.75)),L.cube((loc[0],loc[1],loc[2]+1.75),(0.5,0.5,0.5)),
              L.cube((loc[0]-0.16,loc[1],loc[2]+0.36),(0.22,0.28,0.72)),L.cube((loc[0]+0.16,loc[1],loc[2]+0.36),(0.22,0.28,0.72)),
              L.cube((loc[0]-0.38,loc[1],loc[2]+1.1),(0.2,0.24,0.72)),L.cube((loc[0]+0.38,loc[1],loc[2]+1.1),(0.2,0.24,0.72))): o.data.materials.append(M)

# ---------------- INSANE: the First Cut (void-glass titan with the Cut torn through it; ~32 tall = 16x player) ----------------
def firstcut():
    L.reset(); random.seed(71); parts=[]; P=lambda o:(parts.append(o),o)[1]
    K=2.6; s=lambda v:tuple(x*K for x in v)
    # gaunt angular void-reaper: narrow waist, tall torso, long limbs — clean silhouette
    for sx in(-1,1):
        L.limb([s((sx*1.3,0,6.0)),s((sx*1.5,0.1,3.0)),s((sx*1.6,-0.1,0.6))],0.7*K,0.85*K,parts); P(C(s((sx*1.6,-0.3,0.45)),s((1.8,2.6,0.9))))
    P(C(s((0,0,6.4)),s((3.6,2.4,2.4)))); P(S(s((0,-0.1,7.2)),1.6*K))                               # hips + waist knot (bridges torso)
    P(C(s((0,-0.2,9.4)),s((4.4,2.4,5.2)))); P(C(s((0,-0.4,11.6)),s((6.4,2.8,1.6))))               # tall angular torso + broad shoulder yoke
    for sx in(-1,1):
        P(C(s((sx*3.2,-0.4,11.6)),s((2.0,2.4,2.0))))                                             # shoulder blocks
        L.limb([s((sx*3.4,-0.3,11.4)),s((sx*4.4,0.2,7.4)),s((sx*4.8,0.0,3.6))],0.55*K,0.7*K,parts) # long arms
    # THE BLADE: colossal single-edged blade in the right hand, tip to the ground, taller than the body
    P(C(s((5.0,-0.4,7.0)),s((0.6,1.6,14.0)),rot=(0,0,rad(-10))))
    P(C(s((5.6,-0.4,13.6)),s((0.5,1.4,3.0)),rot=(0,0,rad(-28))))                                   # hooked tip
    P(C(s((-4.9,0.0,3.2)),s((1.6,1.2,1.4))))                                                      # left fist
    # head: tall hooded wedge + crown of shards
    P(Y(s((0,-0.5,12.6)),0.8*K,1.6*K)); P(C(s((0,-0.6,13.8)),s((2.4,2.2,2.6)))); P(L.cone(s((0,-0.6,15.6)),1.5*K,2.6*K,None))
    for k in range(5): P(L.cone(s((-1.6+k*0.8,0.4,15.2+abs(k-2)*0.2)),0.32*K,2.4*K,None,rot=(rad(-18),rad((k-2)*10),0)))
    # shard mantle fanning back from the shoulders (silhouette)
    for sx in(-1,1):
        for k in range(4): P(L.cone(s((sx*(2.0+k*0.9),1.2,11.0+k*0.5)),0.45*K,4.6*K,None,rot=(rad(-32),0,rad(sx*(14+k*12)))))
    body=L.fuse(parts,voxel=0.30,disp=0.10,disp_scale=3.5,facet=0.06)
    body.data.materials.append(L.surface("voidglass",(0.09,0.06,0.15),(0.015,0.005,0.03),crack=TEAL_RGB,crack_str=2.4,crack_scale=0.09,crack_width=0.007,crack_center=s((0,-1.6,9.4)),crack_radius=5.0*K,metallic=0.25,rough=0.22,bump=0.2,noise_scale=1.2))
    GOLD,TEAL,EYE=glows(); acc=[]
    # THE CUT: one clean tall glowing tear from throat to belly
    o=C(s((0,-1.45,9.6)),s((0.55,0.6,6.6)),rot=(0,0,rad(4))); o.data.materials.append(L.glow("cutlight",(1.0,0.74,0.28),4.5)); acc.append(o)
    for k in range(6): o=C(s((-0.6+(k%2)*1.2,-1.5,6.6+k*1.1)),s((0.12,0.4,0.9)),rot=(0,0,rad(16*((k%2)*2-1)))); o.data.materials.append(TEAL); acc.append(o)
    o=C(s((0,-1.85,13.9)),s((1.5,0.4,0.24))); o.data.materials.append(EYE); acc.append(o)                                   # one gold eye-slit
    o=C(s((5.3,-1.25,7.0)),s((0.08,0.5,13.6)),rot=(0,0,rad(-6))); o.data.materials.append(GOLD); acc.append(o)                # gold cutting edge of the blade
    o=C(s((5.9,-1.15,13.6)),s((0.07,0.4,2.9)),rot=(0,0,rad(-28))); o.data.materials.append(GOLD); acc.append(o)
    L.ground_cracks((0,0),n=16,mat=DIM(TEAL_RGB,1.3),seed=71,length=(10,34))
    FRAG=L.plain("frag",(0.08,0.05,0.14),0.2,0.2)
    for i in range(20):
        a=random.random()*math.tau; r=random.uniform(10,16); z=random.uniform(8,32)
        o=L.cube((math.cos(a)*r,math.sin(a)*r,z),(random.uniform(0.6,1.6),random.uniform(0.3,0.7),random.uniform(1.0,2.8)),rot=(random.random()*3,random.random()*3,random.random()*3)); o.data.materials.append(FRAG)
    L.embers(50,(0,-3,16),(12,10,16),[TEAL,GOLD],0.04,0.1,seed=72)
    player_figure((8,-15,0))
    # strong teal rim light from behind so the black glass outline reads
    bpy.ops.object.light_add(type='AREA',location=(-30,40,40)); rim=bpy.context.object; rim.data.energy=60000; rim.data.size=30; rim.data.color=(0.2,0.9,0.9)
    pts={k:s(v) for k,v in dict(pelvis=(0,0,6.0),spine0=(0,0,7.2),chest0=(0,-0.2,9.8),neck0=(0,-0.4,12.2),head0=(0,-0.5,13.0),head1=(0,-0.6,16.6),
             shoulder=(3.4,-0.3,11.4),elbow=(4.4,0.2,7.4),wrist=(4.8,0.0,3.6),hand=(5.0,-0.2,2.2),
             hip=(1.3,0,6.0),knee=(1.5,0.1,3.0),ankle=(1.6,-0.1,0.9),toe=(1.6,-1.2,0.3)).items()}
    arm=R.humanoid_armature(pts); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=15.5,cam=(34,-54,11),lens=38,f=1,big="R",heavy=0.7,light=7.0)

# ---------------- INSANE: the Overweaver (the Loom itself turned hostile; ~36 tall = 18x player) ----------------
def overweaver():
    L.reset(); random.seed(81); parts=[]; P=lambda o:(parts.append(o),o)[1]
    K=2.9; s=lambda v:tuple(x*K for x in v)
    # colossal loom-deity: pillar legs, spool hips, a great frame torso with a shuttle head, many arms
    for sx in(-1,1): P(Y(s((sx*1.8,0,2.6)),1.3*K,5.2*K)); P(C(s((sx*1.8,0.1,0.5)),s((3.4,3.6,1.0))))
    P(Y(s((0,0,5.6)),2.4*K,1.6*K,rot=(0,rad(90),0))); P(Y(s((0,0,5.6)),2.7*K,0.5*K,rot=(0,rad(90),0)))   # spool hips
    P(C(s((0,-0.2,8.9)),s((6.0,2.6,6.2)))); P(C(s((0,-0.2,11.4)),s((7.6,3.0,2.0)))); P(S(s((0,-0.3,11.2)),2.2*K))   # frame torso + top beam (well overlapped)
    for sx in(-1,1): P(Y(s((sx*3.4,-0.2,8.6)),0.6*K,5.0*K))                                                # frame posts
    for sx in(-1,1):   # THREE arms per side, staggered
        for j,(zz,ln) in enumerate(((11.0,4.6),(9.2,5.2),(7.4,4.4))):
            L.limb([s((sx*3.8,-0.3,zz)),s((sx*(5.6+j*0.4),0.4-j*0.5,zz-2.4)),s((sx*(6.6+j*0.5),-0.2,zz-4.8))],0.42*K,0.55*K,parts)
            P(S(s((sx*(6.6+j*0.5),-0.2,zz-4.8)),0.75*K))
    P(Y(s((0,-0.4,12.3)),1.15*K,3.2*K)); P(S(s((0,-0.5,13.2)),1.4*K)); P(C(s((0,-0.6,13.9)),s((4.4,1.8,1.6))))     # thick neck + SHUTTLE head (long, pointed)
    for sx in(-1,1): P(L.cone(s((sx*2.6,-0.6,13.9)),0.8*K,1.8*K,None,rot=(0,rad(sx*90),0)))
    body=L.fuse(parts,voxel=0.34,disp=0.1,disp_scale=3.0,facet=0.05)
    body.data.materials.append(L.surface("overweave",(0.16,0.12,0.30),(0.04,0.03,0.09),crack=GOLD_RGB,crack_str=3.6,crack_scale=0.18,crack_width=0.012,crack_center=s((0,-1.6,8.6)),crack_radius=8.0*K,metallic=0.3,rough=0.55,bump=0.45,stripes=6.0,noise_scale=1.2,sheen=0.5))
    GOLD,TEAL,EYE=glows(); acc=[]
    o=C(s((0,-1.55,8.6)),s((2.2,0.5,1.0))); o.data.materials.append(GOLD); acc.append(o)      # great shuttle-core in the chest
    for k in range(7): o=C(s((-1.5+k*0.5,-1.7,8.6+math.sin(k*1.3)*0.6)),s((0.16,0.3,2.2)),rot=(0,0,rad(10*((k%2)*2-1)))); o.data.materials.append(TEAL); acc.append(o)
    for sx in(-1,1): o=C(s((sx*0.8,-1.55,13.95)),s((0.9,0.3,0.28))); o.data.materials.append(EYE); acc.append(o)
    # WINGS of warp threads spanning from the top beam down to the ground, both sides
    for sx in(-1,1):
        for k in range(22):
            x=sx*(3.8+k*0.55)*K; top=(x*0.55, 0.9*K, 11.6*K); bot=(x, 2.0*K+k*0.15*K, 0.1)
            o=L.seg(top,bot,0.045*K); o.data.materials.append(TEAL if k%3 else GOLD)
    L.ground_cracks((0,0),n=16,mat=DIM(GOLD_RGB,1.3),seed=81,length=(10,36))
    L.embers(70,(0,-3,18),(16,10,18),[GOLD,TEAL],0.04,0.1,seed=82)
    player_figure((9,-15,0))
    pts={k:s(v) for k,v in dict(pelvis=(0,0,5.0),spine0=(0,0,6.4),chest0=(0,-0.2,9.0),neck0=(0,-0.4,12.0),head0=(0,-0.5,12.8),head1=(0,-0.7,15.2),
             shoulder=(3.8,-0.3,9.2),elbow=(6.0,-0.1,6.8),wrist=(7.1,-0.2,4.4),hand=(7.4,-0.2,3.6),
             hip=(1.8,0,5.2),knee=(1.8,0,2.6),ankle=(1.8,0,1.0),toe=(1.8,-1.4,0.3)).items()}
    arm=R.humanoid_armature(pts); R.skin(body,arm); R.bone_parent_nearest(acc,arm)
    return dict(body=body,arm=arm,target_z=17.0,cam=(46,-50,15),lens=40,f=1,big="R",heavy=0.6,light=8.0)

BOSSES.update(lintgolem=lintgolem,tangle=tangle,firstcut=firstcut,overweaver=overweaver)

if __name__=="__main__":
    a=sys.argv; i=a.index("--"); run(a[i+1],a[i+2])
