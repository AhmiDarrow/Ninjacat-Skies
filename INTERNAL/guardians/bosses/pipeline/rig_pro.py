"""Procedural, densely-keyed animation. Every frame is computed: Catmull-Rom pose timelines + layered
secondary motion (breath, sway, traveling tail waves), child-lag follow-through, impact shake, settle overshoot."""
import bpy, math
from mathutils import Vector
import rig_lib as R
TAU=math.tau
def _sm(t): return t*t*(3-2*t)
def catmull(keys, t):
    """keys: list of (t, value_tuple) sorted; returns interpolated tuple (C1 smooth)."""
    if t<=keys[0][0]: return keys[0][1]
    if t>=keys[-1][0]: return keys[-1][1]
    for i in range(len(keys)-1):
        if keys[i][0]<=t<=keys[i+1][0]:
            p1,p2=keys[i],keys[i+1]; p0=keys[i-1] if i>0 else p1; p3=keys[i+2] if i+2<len(keys) else p2
            u=(t-p1[0])/(p2[0]-p1[0]); u=_sm(u)  # ease inside segment
            out=[]
            for k in range(len(p1[1])):
                a,b,c,d=p0[1][k],p1[1][k],p2[1][k],p3[1][k]
                out.append(0.5*((2*b)+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u))
            return tuple(out)
    return keys[-1][1]
class Anim:
    def __init__(self, arm, n, fps=24):
        self.arm=arm; self.n=n; self.tl={}   # bone -> list of (t, (rx,ry,rz,x,y,z))
        self.lag={}; self.layers=[]; self.scale={}
        bpy.context.scene.frame_start=1; bpy.context.scene.frame_end=n; bpy.context.scene.render.fps=fps
        R.clear(arm)
    def has(self,b): return b in self.arm.pose.bones
    def key(self,b,t,rot=(0,0,0),wloc=(0,0,0)):
        if not self.has(b): return
        self.tl.setdefault(b,[]).append((t,(rot[0],rot[1],rot[2],wloc[0],wloc[1],wloc[2])))
    def follow(self,b,frames): self.lag[b]=frames           # child lags its timeline by N frames (follow-through)
    def layer(self,b,fn): 
        if self.has(b): self.layers.append((b,fn))            # fn(t, fr) -> (rx,ry,rz,x,y,z) added on top
    def bake(self):
        n=self.n
        for b,keys in self.tl.items(): keys.sort()
        for fr in range(1,n+1):
            t=(fr-1)/(n-1) if n>1 else 0
            for b in set(list(self.tl.keys())+[l[0] for l in self.layers]):
                lagf=self.lag.get(b,0); tt=max(0,(fr-1-lagf))/(n-1) if n>1 else 0
                v=catmull(sorted(self.tl[b]),tt) if b in self.tl else (0,0,0,0,0,0)
                v=list(v)
                for lb,fn in self.layers:
                    if lb==b:
                        add=fn(t,fr); v=[v[i]+add[i] for i in range(6)]
                R.key(self.arm,b,fr,rot=(v[0],v[1],v[2]),wloc=(v[3],v[4],v[5]))
        # linear interpolation between dense keys (they're already smooth)
        if self.arm.animation_data and self.arm.animation_data.action:
            for fc in self.arm.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation='LINEAR'
def S(a,f=1,ph=0,loops=1): return lambda t,fr:(a*math.sin(TAU*f*loops*t+ph),0,0,0,0,0)
def SZ(a,f=1,ph=0,loops=1): return lambda t,fr:(0,0,a*math.sin(TAU*f*loops*t+ph),0,0,0)
def SY(a,f=1,ph=0,loops=1): return lambda t,fr:(0,a*math.sin(TAU*f*loops*t+ph),0,0,0,0)
def BOB(a,f=1,ph=0,loops=1): return lambda t,fr:(0,0,0,0,0,a*math.sin(TAU*f*loops*t+ph))
def SHAKE(fr0,amp,decay=0.22): 
    def fn(t,fr):
        d=fr-fr0
        if d<0: return (0,0,0,0,0,0)
        e=math.exp(-decay*d); return (amp*0.8*e*math.sin(d*2.4),0,0,0,0,amp*0.12*e*math.sin(d*2.9))
    return fn

# ================= HUMANOID =================
def humanoid(arm, kind, f=1, big="R", heavy=1.0, fps=24):
    d=-f; pel=arm.data.bones['root'].head_local.z
    if kind=='idle':
        A=Anim(arm,48,fps); n=48
        for b in ("root","spine","chest","head","upperarm.L","upperarm.R","forearm.L","forearm.R"): A.key(b,0); A.key(b,1)
        A.layer("chest",S(f*2.2,1)); A.layer("spine",S(f*1.4,1,0.3)); A.layer("root",BOB(0.07,1,-0.4)); A.layer("root",SZ(1.6,0.5))
        A.layer("head",S(-f*2.0,1,0.9)); A.layer("head",SZ(3.0,0.5,0.6)); A.follow("head",3)
        A.layer("upperarm.L",S(d*2.5,1,1.2)); A.layer("upperarm.R",S(d*2.5,1,1.2)); A.layer("upperarm.L",SZ(-2.0,0.5,0.4)); A.layer("upperarm.R",SZ(2.0,0.5,0.4))
        A.layer("forearm.L",S(-d*3,1,1.7)); A.layer("forearm.R",S(-d*3,1,1.7)); A.follow("forearm.L",2); A.follow("forearm.R",2)
        A.bake(); return
    if kind=='walk':
        A=Anim(arm,32,fps); a=30*heavy
        for b in ("root","spine","chest","head","thigh.L","thigh.R","shin.L","shin.R","foot.L","foot.R","upperarm.L","upperarm.R","forearm.L","forearm.R"): A.key(b,0); A.key(b,1)
        def leg(sx):
            def fn(t,fr):
                ph=TAU*t+(0 if sx>0 else math.pi); sw=math.sin(ph)
                return (d*a*sw,0,0,0,0,0)
            return fn
        def knee(sx):
            def fn(t,fr):
                ph=TAU*t+(0 if sx>0 else math.pi); fwd=max(0,math.sin(ph-math.pi/2+0.6))  # bend during the forward swing
                return (-d*40*fwd*fwd*heavy,0,0,0,0,0)
            return fn
        A.layer("thigh.R",leg(1)); A.layer("thigh.L",leg(-1)); A.layer("shin.R",knee(1)); A.layer("shin.L",knee(-1))
        A.layer("foot.R",lambda t,fr:(d*12*max(0,math.sin(TAU*t-1.2)),0,0,0,0,0)); A.layer("foot.L",lambda t,fr:(d*12*max(0,math.sin(TAU*t+math.pi-1.2)),0,0,0,0,0))
        A.layer("upperarm.R",lambda t,fr:(-d*22*math.sin(TAU*t),0,4,0,0,0)); A.layer("upperarm.L",lambda t,fr:(d*22*math.sin(TAU*t),0,-4,0,0,0))
        A.layer("forearm.R",lambda t,fr:(-d*(12+8*max(0,-math.sin(TAU*t))),0,0,0,0,0)); A.layer("forearm.L",lambda t,fr:(-d*(12+8*max(0,math.sin(TAU*t))),0,0,0,0,0))
        A.follow("forearm.R",2); A.follow("forearm.L",2)
        A.layer("root",lambda t,fr:(0,0,4*math.sin(TAU*t),0,0,0.12*(-math.cos(2*TAU*t))+0.04))   # roll + double bob
        A.layer("spine",lambda t,fr:(f*4,0,-3*math.sin(TAU*t),0,0,0)); A.layer("chest",lambda t,fr:(f*2,0,-2*math.sin(TAU*t),0,0,0))
        A.layer("head",lambda t,fr:(-f*3+f*1.5*math.sin(2*TAU*t),0,4*math.sin(TAU*t),0,0,0)); A.follow("head",3)
        A.bake(); return
    if kind=='attack':
        A=Anim(arm,40,fps); Aa=f"upperarm.{big}"; F=f"forearm.{big}"; O=f"upperarm.{'L' if big=='R' else 'R'}"; H=f"hand.{big}"
        rest={"root":((0,0,0),(0,0,0)),"spine":((0,0,0),(0,0,0)),"chest":((0,0,0),(0,0,0)),"head":((0,0,0),(0,0,0)),Aa:((0,0,0),(0,0,0)),F:((0,0,0),(0,0,0)),O:((0,0,0),(0,0,0)),H:((0,0,0),(0,0,0))}
        wind={"root":((0,0,-4),(0,0.4,0.35)),"spine":((-f*13,0,7),(0,0,0)),"chest":((-f*9,0,4),(0,0,0)),"head":((-f*11,0,-6),(0,0,0)),Aa:((-d*135,0,-12),(0,0,0)),F:((-d*38,0,0),(0,0,0)),O:((-d*32,0,22),(0,0,0)),H:((-d*20,0,0),(0,0,0))}
        slam={"root":((0,0,3),(0,-0.5,-0.5)),"spine":((f*26,0,-4),(0,0,0)),"chest":((f*17,0,-2),(0,0,0)),"head":((f*15,0,2),(0,0,0)),Aa:((d*38,0,0),(0,0,0)),F:((d*12,0,0),(0,0,0)),O:((-d*12,0,10),(0,0,0)),H:((d*15,0,0),(0,0,0))}
        hold={"root":((0,0,1.5),(0,-0.45,-0.3)),"spine":((f*22,0,-2),(0,0,0)),"chest":((f*14,0,-1),(0,0,0)),"head":((f*12,0,1),(0,0,0)),Aa:((d*30,0,0),(0,0,0)),F:((d*8,0,0),(0,0,0)),O:((-d*8,0,8),(0,0,0)),H:((d*10,0,0),(0,0,0))}
        recov={"root":((0,2,0),(0,-0.1,0.05)),"spine":((f*3,0,0),(0,0,0)),"chest":((0,0,0),(0,0,0)),"head":((f*1,0,0),(0,0,0)),Aa:((-d*8,0,0),(0,0,0)),F:((0,0,0),(0,0,0)),O:((0,0,0),(0,0,0)),H:((0,0,0),(0,0,0))}
        for b in rest:
            for t,pose in ((0,rest),(0.28,wind),(0.40,slam),(0.50,hold),(0.78,recov),(1,rest)): A.key(b,t,rot=pose[b][0],wloc=pose[b][1])
        A.follow("head",2); A.follow(F,2); A.follow(H,3); A.follow("chest",1)
        A.layer("root",SHAKE(int(40*0.40)+1,1.4))   # impact shake, decaying
        A.layer("chest",S(f*1.2,2)); A.bake(); return
    if kind=='death':
        A=Anim(arm,48,fps); drop=-pel*0.86
        B=["root","spine","chest","head","upperarm.L","upperarm.R","forearm.L","forearm.R","thigh.L","thigh.R","shin.L","shin.R"]
        Z=lambda: {b:((0,0,0),(0,0,0)) for b in B}
        rest=Z()
        stag=Z(); stag.update({"spine":((-f*11,0,6),(0,0,0)),"chest":((-f*6,0,4),(0,0,0)),"head":((-f*13,0,9),(0,0,0)),"upperarm.L":((-d*32,0,-16),(0,0,0)),"upperarm.R":((-d*32,0,16),(0,0,0)),"root":((0,0,3),(0,0,0.12))})
        buck=Z(); buck.update({"root":((f*15,0,4),(0,0,-0.35)),"spine":((f*9,0,10),(0,0,0)),"chest":((f*5,0,6),(0,0,0)),"head":((f*11,0,12),(0,0,0)),"thigh.L":((-d*16,0,0),(0,0,0)),"thigh.R":((-d*10,0,0),(0,0,0)),"shin.L":((d*20,0,0),(0,0,0)),"shin.R":((d*14,0,0),(0,0,0)),"upperarm.L":((-d*10,0,-10),(0,0,0)),"upperarm.R":((-d*10,0,10),(0,0,0))})
        fall=Z(); fall.update({"root":((f*86,0,12),(0,-f*1.7,drop*0.94)),"spine":((f*17,0,10),(0,0,0)),"chest":((f*6,0,4),(0,0,0)),"head":((f*24,0,14),(0,0,0)),"thigh.L":((-d*30,0,0),(0,0,0)),"thigh.R":((-d*24,0,0),(0,0,0)),"shin.L":((d*10,0,0),(0,0,0)),"shin.R":((d*8,0,0),(0,0,0)),"upperarm.L":((-d*22,0,-6),(0,0,0)),"upperarm.R":((-d*18,0,6),(0,0,0))})
        bounce=Z(); bounce.update({"root":((f*90,0,12),(0,-f*1.75,drop*1.02)),"spine":((f*14,0,10),(0,0,0)),"chest":((f*4,0,4),(0,0,0)),"head":((f*28,0,15),(0,0,0)),"thigh.L":((-d*28,0,0),(0,0,0)),"thigh.R":((-d*22,0,0),(0,0,0)),"upperarm.L":((-d*20,0,-6),(0,0,0)),"upperarm.R":((-d*16,0,6),(0,0,0))})
        settle=Z(); settle.update({"root":((f*88,0,12),(0,-f*1.72,drop)),"spine":((f*15,0,10),(0,0,0)),"chest":((f*4,0,4),(0,0,0)),"head":((f*26,0,15),(0,0,0)),"thigh.L":((-d*29,0,0),(0,0,0)),"thigh.R":((-d*23,0,0),(0,0,0)),"upperarm.L":((-d*21,0,-6),(0,0,0)),"upperarm.R":((-d*17,0,6),(0,0,0))})
        for b in B:
            for t,pose in ((0,rest),(0.22,stag),(0.46,buck),(0.72,fall),(0.82,bounce),(1,settle)): A.key(b,t,rot=pose[b][0],wloc=pose[b][1])
        A.follow("head",3); A.follow("chest",1); A.follow("forearm.L",2); A.follow("forearm.R",2)
        A.layer("root",SHAKE(int(48*0.72)+1,0.9,0.3)); A.bake(); return

# ================= QUADRUPED =================
def quad(arm, kind, fps=24):
    F=("FL","FR"); B=("BL","BR"); hip=arm.data.bones['root'].head_local.z
    tails=[t for t in ("tail1","tail2","tail3") if t in arm.pose.bones]
    def tailwave(A,amp=16,freq=1.0,loops=1):
        for i,t in enumerate(tails):
            A.layer(t,lambda tt,fr,i=i:(amp*0.35*math.sin(TAU*freq*loops*tt-i*1.1+0.7), 0, amp*(0.5+0.35*i)*math.sin(TAU*freq*loops*tt-i*1.3),0,0,0))
    if kind=='idle':
        A=Anim(arm,48,fps)
        for b in ("root","chest","neck","head")+tuple(tails)+tuple(f"{l}{s}" for l in F+B for s in "abc"): A.key(b,0); A.key(b,1)
        A.layer("chest",S(1.6,1)); A.layer("root",BOB(0.05,1,-0.5)); A.layer("neck",S(-3,1,0.8)); A.layer("neck",SZ(5,0.5,0.3)); A.layer("head",S(3,1,1.4)); A.layer("head",SZ(7,0.5,0.9)); A.follow("head",3)
        A.layer("FLa",S(2,0.5,0.2)); A.layer("FRa",S(2,0.5,2.2)); tailwave(A,18,1.0); A.bake(); return
    if kind=='walk':   # prowl: diagonal gait, spine flex, head bob, tail wave
        A=Anim(arm,32,fps)
        for b in ("root","chest","neck","head")+tuple(tails)+tuple(f"{l}{s}" for l in F+B for s in "abc"): A.key(b,0); A.key(b,1)
        for L_,ph in (("FL",0),("BR",0),("FR",math.pi),("BL",math.pi)):
            A.layer(f"{L_}a",lambda t,fr,ph=ph:(24*math.sin(TAU*t+ph),0,0,0,0,0))
            A.layer(f"{L_}b",lambda t,fr,ph=ph:(-30*max(0,math.sin(TAU*t+ph-1.0))**1.5,0,0,0,0,0))
            A.layer(f"{L_}c",lambda t,fr,ph=ph:(14*max(0,math.sin(TAU*t+ph-1.6)),0,0,0,0,0))
        A.layer("root",lambda t,fr:(0,0,3*math.sin(TAU*t),0,0,0.08*(-math.cos(2*TAU*t))))
        A.layer("chest",lambda t,fr:(2.5*math.sin(2*TAU*t),0,-3*math.sin(TAU*t),0,0,0))
        A.layer("neck",lambda t,fr:(-2+3*math.sin(2*TAU*t+0.6),0,4*math.sin(TAU*t),0,0,0)); A.layer("head",lambda t,fr:(2*math.sin(2*TAU*t+1.2),0,-3*math.sin(TAU*t),0,0,0)); A.follow("head",3)
        tailwave(A,20,1.0); A.bake(); return
    if kind=='attack':   # crouch -> leap (arc) -> land squash -> recover
        A=Anim(arm,40,fps); n=40
        Bn=("root","chest","neck","head")+tuple(f"{l}{s}" for l in F+B for s in "abc")
        Z=lambda: {b:((0,0,0),(0,0,0)) for b in Bn}
        rest=Z()
        crouch=Z(); crouch.update({"root":((7,0,0),(0,0.7,-0.9)),"chest":((3,0,0),(0,0,0)),"neck":((12,0,0),(0,0,0)),"head":((-10,0,0),(0,0,0))})
        for L_ in F: crouch.update({f"{L_}a":((32,0,0),(0,0,0)),f"{L_}b":((-48,0,0),(0,0,0)),f"{L_}c":((18,0,0),(0,0,0))})
        for L_ in B: crouch.update({f"{L_}a":((28,0,0),(0,0,0)),f"{L_}b":((-52,0,0),(0,0,0)),f"{L_}c":((22,0,0),(0,0,0))})
        leap=Z(); leap.update({"root":((-24,0,0),(0,-2.8,1.9)),"chest":((-9,0,0),(0,0,0)),"neck":((-18,0,0),(0,0,0)),"head":((-8,0,0),(0,0,0))})
        for L_ in F: leap.update({f"{L_}a":((-72,0,0),(0,0,0)),f"{L_}b":((22,0,0),(0,0,0)),f"{L_}c":((-35,0,0),(0,0,0))})
        for L_ in B: leap.update({f"{L_}a":((-38,0,0),(0,0,0)),f"{L_}b":((32,0,0),(0,0,0)),f"{L_}c":((-10,0,0),(0,0,0))})
        land=Z(); land.update({"root":((6,0,0),(0,-3.4,-0.6)),"chest":((4,0,0),(0,0,0)),"neck":((10,0,0),(0,0,0)),"head":((6,0,0),(0,0,0))})
        for L_ in F: land.update({f"{L_}a":((-8,0,0),(0,0,0)),f"{L_}b":((-30,0,0),(0,0,0)),f"{L_}c":((12,0,0),(0,0,0))})
        for L_ in B: land.update({f"{L_}a":((14,0,0),(0,0,0)),f"{L_}b":((-34,0,0),(0,0,0)),f"{L_}c":((10,0,0),(0,0,0))})
        recov=Z(); recov.update({"root":((1,0,0),(0,-3.2,0.0)),"neck":((2,0,0),(0,0,0))})
        for b in Bn:
            for t,pose in ((0,rest),(0.28,crouch),(0.46,leap),(0.60,land),(0.80,recov),(1,rest)): A.key(b,t,rot=pose[b][0],wloc=pose[b][1])
        A.follow("neck",1); A.follow("head",3)
        A.layer("root",SHAKE(int(n*0.60)+1,1.0,0.3)); tailwave(A,22,1.5); A.bake(); return
    if kind=='death':
        A=Anim(arm,48,fps)
        Bn=("root","chest","neck","head")+tuple(f"{l}{s}" for l in F+B for s in "abc")
        Z=lambda: {b:((0,0,0),(0,0,0)) for b in Bn}
        rest=Z()
        s1=Z(); s1.update({"root":((4,0,0),(0,0,-0.5)),"neck":((12,0,-8),(0,0,0)),"head":((14,0,-10),(0,0,0))})
        for L_ in F+B: s1.update({f"{L_}a":((15,0,0),(0,0,0)),f"{L_}b":((-30,0,0),(0,0,0))})
        s2=Z(); s2.update({"root":((6,-18,0),(0,0,-(hip-1.9))),"neck":((28,0,-16),(0,0,0)),"head":((34,0,-22),(0,0,0))})
        for L_ in F+B: s2.update({f"{L_}a":((42,0,0),(0,0,0)),f"{L_}b":((-70,0,0),(0,0,0)),f"{L_}c":((20,0,0),(0,0,0))})
        s3=Z(); s3.update({"root":((5,-24,0),(0,0,-(hip-1.65))),"neck":((32,0,-18),(0,0,0)),"head":((40,0,-27),(0,0,0))})
        for L_ in F+B: s3.update({f"{L_}a":((46,0,0),(0,0,0)),f"{L_}b":((-74,0,0),(0,0,0)),f"{L_}c":((22,0,0),(0,0,0))})
        s4=Z(); s4.update({"root":((5,-24,0),(0,0,-(hip-1.75))),"neck":((32,0,-18),(0,0,0)),"head":((38,0,-26),(0,0,0))})
        for L_ in F+B: s4.update({f"{L_}a":((46,0,0),(0,0,0)),f"{L_}b":((-74,0,0),(0,0,0)),f"{L_}c":((22,0,0),(0,0,0))})
        for b in Bn:
            for t,pose in ((0,rest),(0.3,s1),(0.66,s2),(0.8,s3),(1,s4)): A.key(b,t,rot=pose[b][0],wloc=pose[b][1])
        for i,t in enumerate(tails): A.key(t,0); A.key(t,0.66,rot=(-6*(i+1),0,18)); A.key(t,1,rot=(-14*(i+1),0,26))
        A.follow("neck",2); A.follow("head",4); A.bake(); return

# ================= SPIDER =================
def spider(arm, kind, legs=8, fps=24):
    L=[f"leg{i}" for i in range(legs)]
    if kind=='idle':
        A=Anim(arm,48,fps)
        for b in ("root","head")+tuple(l+s for l in L for s in "ab"): A.key(b,0); A.key(b,1)
        A.layer("root",BOB(0.12,1)); A.layer("root",SZ(1.5,0.5)); A.layer("head",S(3,1,0.5)); A.layer("head",SZ(6,0.5,1.0)); A.follow("head",3)
        for i,l in enumerate(L): A.layer(l+"b",S(4,1,i*0.8)); A.layer(l+"a",SZ(2,0.5,i*0.6))
        A.bake(); return
    if kind=='walk':
        A=Anim(arm,32,fps)
        for b in ("root","head")+tuple(l+s for l in L for s in "ab"): A.key(b,0); A.key(b,1)
        for i,l in enumerate(L):
            ph=0 if i%2==0 else math.pi; side=1 if i>=legs//2 else -1
            A.layer(l+"a",lambda t,fr,ph=ph,side=side:(0,0,side*16*math.sin(TAU*t+ph),0,0,0))
            A.layer(l+"b",lambda t,fr,ph=ph:(-22*max(0,math.sin(TAU*t+ph-0.8))**1.4,0,0,0,0,0))
        A.layer("root",lambda t,fr:(0,2*math.sin(TAU*t),0,0,0,0.10*(-math.cos(2*TAU*t))))
        A.layer("head",lambda t,fr:(2*math.sin(2*TAU*t),0,3*math.sin(TAU*t),0,0,0)); A.follow("head",2); A.bake(); return
    if kind=='attack':   # rear up, front legs stab down
        A=Anim(arm,40,fps); n=40
        Bn=("root","head")+tuple(l+s for l in L for s in "ab"); Z=lambda:{b:((0,0,0),(0,0,0)) for b in Bn}
        rest=Z(); rear=Z(); rear.update({"root":((-30,0,0),(0,0.7,1.3)),"head":((-22,0,0),(0,0,0))})
        for i,l in enumerate(L):
            front=i%(legs//2)<2; rear.update({l+"a":((0,0,-38 if front else 10),(0,0,0)),l+"b":((-45 if front else 0,0,0),(0,0,0))})
        stab=Z(); stab.update({"root":((16,0,0),(0,-0.5,-0.4)),"head":((20,0,0),(0,0,0))})
        for i,l in enumerate(L):
            front=i%(legs//2)<2; stab.update({l+"a":((0,0,34 if front else -6),(0,0,0)),l+"b":((50 if front else 0,0,0),(0,0,0))})
        hold=Z(); hold.update({"root":((12,0,0),(0,-0.4,-0.25)),"head":((16,0,0),(0,0,0))})
        for i,l in enumerate(L):
            front=i%(legs//2)<2; hold.update({l+"a":((0,0,30 if front else -4),(0,0,0)),l+"b":((44 if front else 0,0,0),(0,0,0))})
        for b in Bn:
            for t,pose in ((0,rest),(0.3,rear),(0.44,stab),(0.54,hold),(1,rest)): A.key(b,t,rot=pose[b][0],wloc=pose[b][1])
        A.follow("head",2); A.layer("root",SHAKE(int(n*0.44)+1,1.1)); A.bake(); return
    if kind=='death':
        A=Anim(arm,48,fps); Bn=("root","head")+tuple(l+s for l in L for s in "ab"); Z=lambda:{b:((0,0,0),(0,0,0)) for b in Bn}
        rest=Z(); s1=Z(); s1.update({"root":((6,8,0),(0,0,0.3)),"head":((-15,0,20),(0,0,0))})
        s2=Z(); s2.update({"root":((3,-8,22),(0,0,-2.4)),"head":((25,0,30),(0,0,0))})
        for i,l in enumerate(L): s2.update({l+"a":((0,0,26 if i%2 else -26),(0,0,0)),l+"b":((58,0,0),(0,0,0))})
        s3=Z(); s3.update({"root":((3,-10,25),(0,0,-2.2)),"head":((25,0,30),(0,0,0))})
        for i,l in enumerate(L): s3.update({l+"a":((0,0,25 if i%2 else -25),(0,0,0)),l+"b":((60,0,0),(0,0,0))})
        for b in Bn:
            for t,pose in ((0,rest),(0.35,s1),(0.75,s2),(0.85,s3),(1,s3)): A.key(b,t,rot=pose[b][0],wloc=pose[b][1])
        A.follow("head",3); A.bake(); return

# ================= TOWER =================
def tower(arm, kind, fps=24):
    if kind=='idle':
        A=Anim(arm,48,fps)
        for b in ("base","mid","top","face"): A.key(b,0); A.key(b,1)
        for i,b in enumerate(("base","mid","top")): A.layer(b,S(1.5+i*1.2,1,-i*0.7)); A.layer(b,SZ(1.0+i*0.8,0.5,-i*0.5))
        A.layer("face",S(-3,1,0.8)); A.layer("face",SZ(5,0.5,0.4)); A.follow("face",3); A.bake(); return
    if kind=='walk':
        A=Anim(arm,32,fps)
        for b in ("base","mid","top","face"): A.key(b,0); A.key(b,1)
        A.layer("base",lambda t,fr:(8*math.sin(TAU*t),0,0,0,0,0.5*max(0,math.sin(TAU*t)))); A.layer("mid",S(10,1,-0.5)); A.layer("top",S(12,1,-1.0)); A.layer("face",S(6,1,-1.4)); A.follow("mid",1); A.follow("top",2); A.follow("face",3); A.bake(); return
    if kind=='attack':
        A=Anim(arm,40,fps); n=40
        for b,(a,bb,c) in {"base":(-9,11,0),"mid":(-15,22,0),"top":(-20,28,0),"face":(-15,22,0)}.items():
            for t,v in ((0,0),(0.3,a),(0.46,bb),(0.56,bb*0.85),(1,0)): A.key(b,t,rot=(v,0,0))
        A.follow("mid",1); A.follow("top",2); A.follow("face",3); A.layer("base",SHAKE(int(n*0.46)+1,1.0)); A.bake(); return
    if kind=='death':
        A=Anim(arm,48,fps)
        for b,(s1,s2,s3) in {"base":((0,0,0),(70,0,8),(74,0,8)),"mid":((-8,0,10),(30,0,15),(32,0,15)),"top":((-12,0,14),(35,0,20),(36,0,20)),"face":((-8,0,6),(30,0,0),(32,0,0))}.items():
            for t,v in ((0,(0,0,0)),(0.4,s1),(0.82,s2),(1,s3)): A.key(b,t,rot=v,wloc=((0,-1.5,-1.4) if (t>=0.82 and b=="base") else (0,0,0)))
        A.follow("mid",1); A.follow("top",2); A.follow("face",3); A.bake(); return
