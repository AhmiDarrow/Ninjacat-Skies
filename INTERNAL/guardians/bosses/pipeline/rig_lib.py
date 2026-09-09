import bpy, math
from mathutils import Vector
def humanoid_armature(pts, name="rig"):
    """pts: dict of key points. Builds a humanoid armature; returns armature object."""
    bpy.ops.object.armature_add(enter_editmode=True,location=(0,0,0)); arm=bpy.context.object; arm.name=name
    eb=arm.data.edit_bones; eb.remove(eb[0])
    def B(n,h,t,parent=None,connect=False):
        b=eb.new(n); b.head=Vector(h); b.tail=Vector(t)
        if parent: b.parent=eb[parent]; b.use_connect=connect
        return b
    p=pts
    B("root",p['pelvis'],p['spine0'])
    B("spine",p['spine0'],p['chest0'],"root",True); B("chest",p['chest0'],p['neck0'],"spine",True)
    B("neck",p['neck0'],p['head0'],"chest",True); B("head",p['head0'],p['head1'],"neck",True)
    for s,sx in (("L",-1),("R",1)):
        m=lambda v:(v[0]*sx,v[1],v[2])
        B(f"shoulder.{s}",p['neck0'],m(p['shoulder']),"chest")
        B(f"upperarm.{s}",m(p['shoulder']),m(p['elbow']),f"shoulder.{s}",True)
        B(f"forearm.{s}",m(p['elbow']),m(p['wrist']),f"upperarm.{s}",True)
        B(f"hand.{s}",m(p['wrist']),m(p['hand']),f"forearm.{s}",True)
        B(f"thigh.{s}",m(p['hip']),m(p['knee']),"root")
        B(f"shin.{s}",m(p['knee']),m(p['ankle']),f"thigh.{s}",True)
        B(f"foot.{s}",m(p['ankle']),m(p['toe']),f"shin.{s}",True)
    bpy.ops.object.mode_set(mode='OBJECT'); return arm
def _weighted_verts(body):
    return sum(1 for v in body.data.vertices if any(g.weight>0.001 for g in v.groups))
def manual_weights(body, arm, k=2, power=2.0):
    """robust skinning: each vertex weighted to its nearest k bones by inverse distance to the bone segment"""
    for vg in list(body.vertex_groups): body.vertex_groups.remove(vg)
    bones=[(b.name, arm.matrix_world@b.head_local, arm.matrix_world@b.tail_local) for b in arm.data.bones]
    groups={n:body.vertex_groups.new(name=n) for n,_,_ in bones}
    mw=body.matrix_world
    def segdist(p,a,b):
        ab=b-a; t=max(0.0,min(1.0,(p-a).dot(ab)/max(1e-9,ab.dot(ab)))); return (p-(a+ab*t)).length
    for v in body.data.vertices:
        p=mw@v.co
        ds=sorted(((segdist(p,a,b),n) for n,a,b in bones))[:k]
        ws=[(1.0/((d+0.15)**power),n) for d,n in ds]; tot=sum(w for w,_ in ws)
        for w,n in ws: groups[n].add([v.index],w/tot,'REPLACE')
def skin(body, arm):
    bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active=arm
    try: bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    except Exception as e: print("AUTO WEIGHTS RAISED",e)
    nverts=len(body.data.vertices); wv=_weighted_verts(body)
    if wv < nverts*0.9:
        print(f"bone-heat weights incomplete ({wv}/{nverts}) -> manual nearest-bone weights")
        if body.parent!=arm:
            body.parent=arm; body.matrix_parent_inverse=arm.matrix_world.inverted()
        if not any(m.type=='ARMATURE' for m in body.modifiers):
            md=body.modifiers.new("Armature",'ARMATURE'); md.object=arm
        manual_weights(body,arm)
    print(f"SKIN {body.name}: {_weighted_verts(body)}/{nverts} weighted")
def bone_parent_nearest(objs, arm):
    """rigid-attach accessory objects to the nearest bone (by bone midpoint)"""
    mids={b.name:(arm.matrix_world@((b.head_local+b.tail_local)/2)) for b in arm.data.bones}
    for o in objs:
        loc=o.matrix_world.translation
        bn=min(mids,key=lambda n:(mids[n]-loc).length)
        mw=o.matrix_world.copy()
        o.parent=arm; o.parent_type='BONE'; o.parent_bone=bn
        o.matrix_world=mw  # keeps world placement
def key(arm, bone, frame, rot=(0,0,0), loc=None, scale=None, wloc=None):
    pb=arm.pose.bones[bone]; pb.rotation_mode='XYZ'
    if wloc is not None:   # world-space offset -> this bone's local axes (rest pose)
        loc=arm.data.bones[bone].matrix_local.to_3x3().inverted() @ Vector(wloc)
    bpy.context.scene.frame_set(frame)
    pb.rotation_euler=[math.radians(a) for a in rot]; pb.keyframe_insert('rotation_euler')
    if loc is not None: pb.location=loc; pb.keyframe_insert('location')
    if scale is not None: pb.scale=scale; pb.keyframe_insert('scale')
def ease(arm):
    if arm.animation_data and arm.animation_data.action:
        for fc in arm.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation='BEZIER'; kp.easing='EASE_IN_OUT'
def clear(arm):
    for pb in arm.pose.bones: pb.rotation_euler=(0,0,0); pb.location=(0,0,0); pb.scale=(1,1,1)
    if arm.animation_data: arm.animation_data_clear()

# ---------- humanoid animation set (bone-space X rotations; sign 'f' flips forward direction) ----------
def anim(arm, kind, n=24, f=1, big_hand="R", heavy=1.0):
    sc=bpy.context.scene; sc.frame_start=1; sc.frame_end=n; clear(arm)
    K=lambda b,fr,**kw: key(arm,b,fr,**kw)
    d=-f  # limbs point down: opposite local-X sense to the spine
    pel=arm.data.bones['root'].head_local.z if 'root' in arm.data.bones else 4.0
    if kind=='idle':   # breathe + slow weight shift, loops
        for fr,t,w in ((1,0,0),(n//4,0.6,1),(n//2,1,0),(3*n//4,0.6,-1),(n,0,0)):
            K("root",fr,wloc=(0,0,0.10*t),rot=(0,0,2.0*w))
            K("spine",fr,rot=(f*2.0*t,0,1.2*w)); K("chest",fr,rot=(f*2.5*t,0,0),scale=(1,1+0.025*t,1+0.02*t))
            K("head",fr,rot=(-f*2.5*t,0,3.0*w)); K("upperarm.L",fr,rot=(d*3*t,0,-2.5*w)); K("upperarm.R",fr,rot=(d*3*t,0,-2.5*w))
    elif kind=='walk':  # heavy stride: swing, knee bend, counter-swing, roll, bob. seamless loop.
        h=n//2; a=32*heavy
        for fr,s in ((1,1),(h,-1),(n,1)):
            K("thigh.L",fr,rot=(d*a*s,0,0)); K("thigh.R",fr,rot=(-d*a*s,0,0))
            K("upperarm.L",fr,rot=(-d*20*s,0,-4)); K("upperarm.R",fr,rot=(d*20*s,0,4))
            K("forearm.L",fr,rot=(-d*12,0,0)); K("forearm.R",fr,rot=(-d*12,0,0))
            K("root",fr,rot=(0,0,4*s)); K("spine",fr,rot=(f*4,0,-3*s)); K("chest",fr,rot=(f*2,0,-3*s)); K("head",fr,rot=(-f*3,0,4*s))
        for fr,s in ((n//4,1),(3*n//4,-1)):   # passing position: knees bent, body highest
            K("shin.L",fr,rot=(-d*30*max(0,s),0,0)); K("shin.R",fr,rot=(-d*30*max(0,-s),0,0))
            K("thigh.L",fr,rot=(0,0,0)); K("thigh.R",fr,rot=(0,0,0))
        for fr in (1,h,n): K("shin.L",fr,rot=(0,0,0)); K("shin.R",fr,rot=(0,0,0))
        for fr,z in ((1,-0.08),(n//4,0.22),(h,-0.08),(3*n//4,0.22),(n,-0.08)): K("root",fr,wloc=(0,0,z))
    elif kind=='attack':
        A=f"upperarm.{big_hand}"; F=f"forearm.{big_hand}"; O=f"upperarm.{'L' if big_hand=='R' else 'R'}"
        K("root",1,rot=(0,0,0),wloc=(0,0,0)); K("spine",1,rot=(0,0,0)); K("chest",1,rot=(0,0,0)); K(A,1,rot=(0,0,0)); K(F,1,rot=(0,0,0)); K("head",1,rot=(0,0,0)); K(O,1,rot=(0,0,0))
        a=int(n*0.3)   # wind-up: rear back, raise the heavy arm high, other arm out for balance
        K("spine",a,rot=(-f*12,0,6)); K("chest",a,rot=(-f*8,0,4)); K(A,a,rot=(-d*130,0,-10)); K(F,a,rot=(-d*35,0,0)); K("head",a,rot=(-f*10,0,-6)); K("root",a,wloc=(0,0,0.4),rot=(0,0,-4)); K(O,a,rot=(-d*30,0,20))
        b=int(n*0.42)  # SLAM
        K("spine",b,rot=(f*24,0,-4)); K("chest",b,rot=(f*16,0,-2)); K(A,b,rot=(d*35,0,0)); K(F,b,rot=(d*10,0,0)); K("head",b,rot=(f*14,0,2)); K("root",b,wloc=(0,0,-0.45),rot=(0,0,3)); K(O,b,rot=(-d*10,0,10))
        c=int(n*0.5)   # impact shake
        K("root",c,wloc=(0,0,-0.25),rot=(0,0,1)); K(A,c,rot=(d*28,0,0)); K("spine",c,rot=(f*20,0,-2))
        e=int(n*0.78)  # recover
        K("root",e,rot=(0,2,0),wloc=(0,0,0.05)); K("spine",e,rot=(f*2,0,0)); K("chest",e,rot=(0,0,0)); K(A,e,rot=(-d*6,0,0)); K(F,e,rot=(0,0,0)); K("head",e,rot=(1,0,0)); K(O,e,rot=(0,0,0))
        K("root",n,rot=(0,0,0),wloc=(0,0,0)); K("spine",n,rot=(0,0,0)); K("chest",n,rot=(0,0,0)); K(A,n,rot=(0,0,0)); K(F,n,rot=(0,0,0)); K("head",n,rot=(0,0,0)); K(O,n,rot=(0,0,0))
    elif kind=='death':
        drop=-pel*0.85
        K("root",1,rot=(0,0,0),wloc=(0,0,0)); K("spine",1,rot=(0,0,0)); K("head",1,rot=(0,0,0))
        for L_ in ("L","R"): K(f"upperarm.{L_}",1,rot=(0,0,0)); K(f"thigh.{L_}",1,rot=(0,0,0))
        s1=int(n*0.25); K("spine",s1,rot=(-f*10,0,6)); K("head",s1,rot=(-f*12,0,8)); K("upperarm.L",s1,rot=(-d*30,0,-15)); K("upperarm.R",s1,rot=(-d*30,0,15)); K("root",s1,wloc=(0,0,0.1))   # stagger up
        s2=int(n*0.5);  K("root",s2,rot=(f*14,0,4),wloc=(0,0,-0.3)); K("spine",s2,rot=(f*8,0,10)); K("head",s2,rot=(f*10,0,12)); K("thigh.L",s2,rot=(-d*15,0,0)); K("thigh.R",s2,rot=(-d*10,0,0))   # knees buckle
        s3=int(n*0.85); K("root",s3,rot=(f*84,0,12),wloc=(0,-f*1.6,drop*0.92)); K("spine",s3,rot=(f*16,0,10)); K("head",s3,rot=(f*22,0,14))
        for L_ in ("L","R"): K(f"upperarm.{L_}",s3,rot=(-d*20,0,0)); K(f"thigh.{L_}",s3,rot=(-d*28,0,0))
        K("root",n,rot=(f*88,0,12),wloc=(0,-f*1.7,drop)); K("spine",n,rot=(f*14,0,10)); K("head",n,rot=(f*26,0,15))   # settle
    ease(arm)

# ---------- custom rigs ----------
def custom_armature(bones, name="rig"):
    """bones: list of (name, head, tail, parent_or_None)"""
    bpy.ops.object.armature_add(enter_editmode=True,location=(0,0,0)); arm=bpy.context.object; arm.name=name
    eb=arm.data.edit_bones; eb.remove(eb[0])
    for n,h,t,p in bones:
        b=eb.new(n); b.head=Vector(h); b.tail=Vector(t)
        if p: b.parent=eb[p]
    bpy.ops.object.mode_set(mode='OBJECT'); return arm

def anim_spider(arm, kind, n=20, legs=8):
    """legs named leg{i}a (hip->knee) / leg{i}b (knee->tip); root = body. Tetrapod gait."""
    sc=bpy.context.scene; sc.frame_start=1; sc.frame_end=n; clear(arm)
    K=lambda b,fr,**kw: key(arm,b,fr,**kw)
    groupA=[i for i in range(legs) if i%2==0]; groupB=[i for i in range(legs) if i%2==1]
    if kind=='idle':
        for fr,t in ((1,0),(n//2,1),(n,0)):
            K("root",fr,wloc=(0,0,0.18*t),rot=(0,0,1.5*t)); K("head",fr,rot=(4*t,0,6*t))
            for i in range(legs): K(f"leg{i}a",fr,rot=(0,0,0)); K(f"leg{i}b",fr,rot=(6*t*(1 if i%2 else -1),0,0))
    elif kind=='walk':
        h=n//2
        for fr,s in ((1,1),(h,-1),(n,1)):
            for i in groupA: K(f"leg{i}a",fr,rot=(0,0,16*s)); K(f"leg{i}b",fr,rot=(-18*max(0,s),0,0))
            for i in groupB: K(f"leg{i}a",fr,rot=(0,0,-16*s)); K(f"leg{i}b",fr,rot=(-18*max(0,-s),0,0))
        for fr,z in ((1,0),(n//4,0.2),(h,0),(3*n//4,0.2),(n,0)): K("root",fr,wloc=(0,0,z))
    elif kind=='attack':
        K("root",1,rot=(0,0,0),wloc=(0,0,0))
        for i in range(legs): K(f"leg{i}a",1,rot=(0,0,0)); K(f"leg{i}b",1,rot=(0,0,0))
        a=int(n*0.35); K("root",a,rot=(-28,0,0),wloc=(0,0.6,1.2)); K("head",a,rot=(-20,0,0))
        for i in range(legs):
            front = i<legs//2
            K(f"leg{i}a",a,rot=(0,0,-35 if front else 10)); K(f"leg{i}b",a,rot=(-40 if front else 0,0,0))
        b=int(n*0.5); K("root",b,rot=(14,0,0),wloc=(0,-0.4,-0.3)); K("head",b,rot=(18,0,0))
        for i in range(legs):
            front = i<legs//2
            K(f"leg{i}a",b,rot=(0,0,30 if front else -6)); K(f"leg{i}b",b,rot=(45 if front else 0,0,0))
        K("root",n,rot=(0,0,0),wloc=(0,0,0)); K("head",n,rot=(0,0,0))
        for i in range(legs): K(f"leg{i}a",n,rot=(0,0,0)); K(f"leg{i}b",n,rot=(0,0,0))
    elif kind=='death':
        K("root",1,rot=(0,0,0),wloc=(0,0,0))
        for i in range(legs): K(f"leg{i}a",1,rot=(0,0,0)); K(f"leg{i}b",1,rot=(0,0,0))
        K("root",int(n*0.4),rot=(6,8,0),wloc=(0,0,0.3)); K("head",int(n*0.4),rot=(-15,0,20))
        K("root",n,rot=(3,-10,25),wloc=(0,0,-2.2)); K("head",n,rot=(25,0,30))
        for i in range(legs): K(f"leg{i}a",n,rot=(0,0,(25 if i%2 else -25))); K(f"leg{i}b",n,rot=(55,0,0))
    ease(arm)

def anim_tower(arm, kind, n=20):
    """tower chain: base->mid->top (+ 'face'). Sway, lurch, swarm-rear, collapse."""
    sc=bpy.context.scene; sc.frame_start=1; sc.frame_end=n; clear(arm)
    K=lambda b,fr,**kw: key(arm,b,fr,**kw)
    if kind=='idle':
        for fr,t in ((1,0),(n//2,1),(n,0)):
            K("base",fr,rot=(2*t,0,0)); K("mid",fr,rot=(3*t,0,2*t)); K("top",fr,rot=(4*t,0,-3*t)); K("face",fr,rot=(-3*t,0,4*t))
    elif kind=='walk':
        for fr,t in ((1,0),(n//3,1),(2*n//3,-1),(n,0)):
            K("base",fr,rot=(7*t,0,0),wloc=(0,0,0.5*abs(t))); K("mid",fr,rot=(9*t,0,0)); K("top",fr,rot=(11*t,0,0))
    elif kind=='attack':
        K("base",1,rot=(0,0,0)); K("mid",1,rot=(0,0,0)); K("top",1,rot=(0,0,0)); K("face",1,rot=(0,0,0))
        a=int(n*0.35); K("base",a,rot=(-8,0,0)); K("mid",a,rot=(-14,0,0)); K("top",a,rot=(-18,0,0)); K("face",a,rot=(-14,0,0))
        b=int(n*0.55); K("base",b,rot=(10,0,0)); K("mid",b,rot=(20,0,0)); K("top",b,rot=(26,0,0)); K("face",b,rot=(20,0,0))
        K("base",n,rot=(0,0,0)); K("mid",n,rot=(0,0,0)); K("top",n,rot=(0,0,0)); K("face",n,rot=(0,0,0))
    elif kind=='death':
        K("base",1,rot=(0,0,0),wloc=(0,0,0)); K("mid",1,rot=(0,0,0)); K("top",1,rot=(0,0,0))
        K("mid",int(n*0.4),rot=(-8,0,10)); K("top",int(n*0.4),rot=(-12,0,14))
        K("base",n,rot=(70,0,8),wloc=(0,-1.5,-1.4)); K("mid",n,rot=(30,0,15)); K("top",n,rot=(35,0,20)); K("face",n,rot=(30,0,0))
    ease(arm)

def anim_quad(arm, kind, n=20):
    """quadruped: root(hips), chest, neck, head, tail1, tail2, legs FL/FR/BL/BR each with a(upper) b(lower) c(paw)."""
    sc=bpy.context.scene; sc.frame_start=1; sc.frame_end=n; clear(arm)
    K=lambda b,fr,**kw: key(arm,b,fr,**kw)
    F=("FL","FR"); B=("BL","BR")
    if kind=='idle':
        for fr,t in ((1,0),(n//2,1),(n,0)):
            K("chest",fr,rot=(0,0,0),scale=(1,1+0.03*t,1)); K("neck",fr,rot=(-4*t,0,3*t)); K("head",fr,rot=(3*t,0,4*t))
            K("tail1",fr,rot=(0,0,18*t)); K("tail2",fr,rot=(0,0,22*t)); K("root",fr,wloc=(0,0,0.08*t))
    elif kind=='walk':
        h=n//2
        for fr,s in ((1,1),(h,-1),(n,1)):
            for L_,sg in (("FL",1),("BR",1),("FR",-1),("BL",-1)):
                K(f"{L_}a",fr,rot=(22*s*sg,0,0)); K(f"{L_}b",fr,rot=(-16*max(0,s*sg),0,0))
            K("root",fr,rot=(0,0,3*s)); K("neck",fr,rot=(-3,0,4*s)); K("head",fr,rot=(2,0,-3*s)); K("tail1",fr,rot=(0,0,14*s)); K("tail2",fr,rot=(0,0,20*s))
        for fr,z in ((1,0),(n//4,0.15),(h,0),(3*n//4,0.15),(n,0)): K("root",fr,wloc=(0,0,z))
    elif kind=='attack':   # crouch, then POUNCE with front paws
        K("root",1,rot=(0,0,0),wloc=(0,0,0)); K("chest",1,rot=(0,0,0)); K("neck",1,rot=(0,0,0)); K("head",1,rot=(0,0,0))
        for L_ in F+B: K(f"{L_}a",1,rot=(0,0,0)); K(f"{L_}b",1,rot=(0,0,0))
        a=int(n*0.3); K("root",a,rot=(6,0,0),wloc=(0,0.6,-0.7)); K("neck",a,rot=(10,0,0)); K("head",a,rot=(-8,0,0))
        for L_ in F: K(f"{L_}a",a,rot=(30,0,0)); K(f"{L_}b",a,rot=(-40,0,0))
        for L_ in B: K(f"{L_}a",a,rot=(25,0,0)); K(f"{L_}b",a,rot=(-45,0,0))
        b=int(n*0.5); K("root",b,rot=(-22,0,0),wloc=(0,-2.6,1.6)); K("chest",b,rot=(-8,0,0)); K("neck",b,rot=(-16,0,0)); K("head",b,rot=(-10,0,0))
        for L_ in F: K(f"{L_}a",b,rot=(-70,0,0)); K(f"{L_}b",b,rot=(20,0,0)); K(f"{L_}c",b,rot=(-30,0,0))
        for L_ in B: K(f"{L_}a",b,rot=(-35,0,0)); K(f"{L_}b",b,rot=(30,0,0))
        c=int(n*0.7); K("root",c,rot=(4,0,0),wloc=(0,-3.0,-0.2)); K("neck",c,rot=(6,0,0))
        for L_ in F: K(f"{L_}a",c,rot=(-10,0,0)); K(f"{L_}b",c,rot=(-10,0,0)); K(f"{L_}c",c,rot=(0,0,0))
        for L_ in B: K(f"{L_}a",c,rot=(10,0,0)); K(f"{L_}b",c,rot=(-10,0,0))
        K("root",n,rot=(0,0,0),wloc=(0,0,0)); K("chest",n,rot=(0,0,0)); K("neck",n,rot=(0,0,0)); K("head",n,rot=(0,0,0))
        for L_ in F+B: K(f"{L_}a",n,rot=(0,0,0)); K(f"{L_}b",n,rot=(0,0,0)); K(f"{L_}c",n,rot=(0,0,0))
    elif kind=='death':   # legs buckle, body sags to the ground, head drops, slight roll onto the shoulder
        hip=arm.data.bones['root'].head_local.z
        K("root",1,rot=(0,0,0),wloc=(0,0,0)); K("neck",1,rot=(0,0,0)); K("head",1,rot=(0,0,0))
        for L_ in F+B: K(f"{L_}a",1,rot=(0,0,0)); K(f"{L_}b",1,rot=(0,0,0)); K(f"{L_}c",1,rot=(0,0,0))
        s1=int(n*0.3); K("root",s1,rot=(4,0,0),wloc=(0,0,-0.5)); K("neck",s1,rot=(12,0,-8)); K("head",s1,rot=(14,0,-10))
        for L_ in F+B: K(f"{L_}a",s1,rot=(15,0,0)); K(f"{L_}b",s1,rot=(-30,0,0))
        s2=int(n*0.7); K("root",s2,rot=(6,-18,0),wloc=(0,0,-(hip-1.9))); K("neck",s2,rot=(28,0,-16)); K("head",s2,rot=(34,0,-22))
        for L_ in F+B: K(f"{L_}a",s2,rot=(42,0,0)); K(f"{L_}b",s2,rot=(-70,0,0)); K(f"{L_}c",s2,rot=(20,0,0))
        K("root",n,rot=(5,-24,0),wloc=(0,0,-(hip-1.75))); K("neck",n,rot=(32,0,-18)); K("head",n,rot=(38,0,-26))
        for L_ in F+B: K(f"{L_}a",n,rot=(46,0,0)); K(f"{L_}b",n,rot=(-74,0,0)); K(f"{L_}c",n,rot=(22,0,0))
    # cat tail: its own life — random lazy sway independent of the body, on every clip
    import random as _r; _r.seed(hash(kind)&0xffff)
    tails=[t for t in ("tail1","tail2","tail3") if t in arm.pose.bones]
    if kind!='death':
        for fr in range(1,n+1,max(2,n//6)):
            for i,t in enumerate(tails):
                K(t,fr,rot=(_r.uniform(-8,14)*(i+1)*0.6, _r.uniform(-6,6), _r.uniform(-28,28)*(i+1)*0.55))
        for t in tails: K(t,n,rot=arm.pose.bones[t].rotation_euler.copy() if False else (0,0,0))
    else:
        for i,t in enumerate(tails): K(t,1,rot=(0,0,0)); K(t,n,rot=(10*(i+1),0,30))
    ease(arm)
