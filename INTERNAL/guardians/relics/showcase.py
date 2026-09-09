"""Woven Relic showcase renders: each relic as a 3D hero prop on a stone plinth with
colour-keyed rings, embers, ground cracks and an 'activation' burst.
usage: blender --background --python relics/showcase.py -- <relic|all> [samples]
"""
import bpy, math, sys, random, os
ART = os.environ.get('NCS_ART_ROOT', os.path.expanduser('~'))   # work root; boss_lib2.py lives in <ART> or next to this file's parent
sys.path.insert(0, ART); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from boss_lib2 import *   # reset, sphere, cube, cyl, fuse, surface, glow, plain, glass, ring, cone, embers, ground_cracks, studio, limb
from mathutils import Vector

OUT = os.path.join(ART, 'relics', 'renders'); os.makedirs(OUT, exist_ok=True)

TEAL = (0.10, 0.95, 0.80); GOLD = (1.0, 0.72, 0.25)

def col(r, g, b): return (r/255, g/255, b/255)

def cubeS(loc, s, rot=(0, 0, 0)): return cube(loc, (s, s, s), rot)

def clear_slots(o):
    o.data.materials.clear()

def setmat(o, m):
    clear_slots(o); o.data.materials.append(m); return o

def smooth(o, on=True):
    bpy.context.view_layer.objects.active = o
    for p in o.data.polygons: p.use_smooth = on
    return o

def bevel(o, w=0.03, seg=3):
    md = o.modifiers.new('bev', 'BEVEL'); md.width = w; md.segments = seg; md.limit_method = 'ANGLE'; return o

def subsurf(o, lv=2):
    md = o.modifiers.new('ss', 'SUBSURF'); md.levels = lv; md.render_levels = lv; return o

def torus_knot(p=2, q=3, R=1.0, r=0.45, n=160):
    pts = []
    for i in range(n):
        t = 2*math.pi*i/n
        rr = R + r*math.cos(q*t)
        pts.append((rr*math.cos(p*t), rr*math.sin(p*t), r*math.sin(q*t)))
    return pts

def tube(points, radius, mat, closed=False, bevres=8):
    cu = bpy.data.curves.new('tube', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = radius; cu.bevel_resolution = bevres; cu.use_fill_caps = True
    sp = cu.splines.new('NURBS'); sp.points.add(len(points)-1)
    for i, p in enumerate(points): sp.points[i].co = (*p, 1)
    sp.use_cyclic_u = closed; sp.use_endpoint_u = not closed; sp.order_u = 4
    o = bpy.data.objects.new('tube', cu); bpy.context.collection.objects.link(o); o.data.materials.append(mat); return o


def group(objs, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
    bpy.ops.object.empty_add(location=loc); e = bpy.context.object; e.rotation_euler = rot; e.scale = (scale,)*3
    for o in objs: o.parent = e
    return e

def facet(o, angle=22):
    md = o.modifiers.new('dec', 'DECIMATE'); md.decimate_type = 'DISSOLVE'; md.angle_limit = math.radians(angle)
    for p in o.data.polygons: p.use_smooth = False
    return o

def ring_emission_material(name, base, glow_rgb, scale=6.0, strength=2.0, rings=True):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*base, 1); p.inputs["Roughness"].default_value = 0.6
    tc = nt.nodes.new("ShaderNodeTexCoord"); wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'RINGS' if rings else 'BANDS'
    wv.rings_direction = 'Z' if rings else 'X'; wv.inputs["Scale"].default_value = scale; wv.inputs["Distortion"].default_value = 0.0
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.72; cr.color_ramp.elements[1].position = 0.86
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"]); nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = strength
    nt.links.new(cr.outputs["Color"], mul.inputs[0]); nt.links.new(mul.outputs[0], p.inputs["Emission Strength"])
    p.inputs["Emission Color"].default_value = (*glow_rgb, 1)
    return m

def band_material(name, a, b, scale=8.0, axis='X', rough=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord"); wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'BANDS'; wv.bands_direction = axis
    wv.inputs["Scale"].default_value = scale; wv.inputs["Distortion"].default_value = 0.3; wv.inputs["Detail"].default_value = 1
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.45; cr.color_ramp.elements[1].position = 0.55
    cr.color_ramp.elements[0].color = (*a, 1); cr.color_ramp.elements[1].color = (*b, 1)
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"]); nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"]); nt.links.new(cr.outputs["Color"], p.inputs["Base Color"])
    return m

def gem_material(name, rgb, glow_rgb, emit=0.25):
    m = bpy.data.materials.new(name); m.use_nodes = True; p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = 0.04; p.inputs["Transmission Weight"].default_value = 0.85
    p.inputs["IOR"].default_value = 1.7; p.inputs["Emission Color"].default_value = (*glow_rgb, 1); p.inputs["Emission Strength"].default_value = emit
    return m

def helix(center, r, h, turns, radius, mat, n=160):
    pts = []
    for i in range(n+1):
        t = i/n
        pts.append((center[0]+r*math.cos(turns*6.283*t), center[1]+r*math.sin(turns*6.283*t), center[2]-h/2+h*t))
    return tube(pts, radius, mat)

def leaf(loc, size, rot, mat):
    l = sphere(loc, size, 16); l.scale = (1.0, 0.45, 0.10); l.rotation_euler = rot; setmat(l, mat); smooth(l); return l

# ---------- shared staging ----------
def plinth(colour, z=0.0):
    stone = surface("plinth", base=(0.10, 0.10, 0.12), dark=(0.03, 0.03, 0.04), crack=colour, crack_str=2.2, crack_scale=0.9, crack_width=0.02,
                    crack_center=(0, 0, 0.9), crack_radius=2.4, rough=0.85, bump=0.5)
    base = setmat(cyl((0, 0, z+0.25), 2.6, 0.5), stone); bevel(base, 0.08, 4)
    top = setmat(cyl((0, 0, z+0.62), 2.0, 0.28), stone); bevel(top, 0.06, 4)
    rim = ring((0, 0, z+0.78), 2.0, 0.03, glow("rimglow", colour, 0.9))
    return base, top, rim

def halo(colour, z, r=1.5, n=2, tilt=0.5, seed=1):
    rnd = random.Random(seed); out = []
    for i in range(n):
        rot = (rnd.uniform(-tilt, tilt), rnd.uniform(-tilt, tilt), rnd.uniform(0, 3.14))
        out.append(ring((0, 0, z), r + 0.3*i, 0.012, glow(f"halo{i}", colour, 0.8 + 0.3*i), rot=rot))
    return out

def burst(colour, z, r=1.2):
    """activation burst: a flat expanding disc + upward shards"""
    d = ring((0, 0, z), r, 0.04, glow("burst", colour, 1.3))
    d.scale = (1, 1, 0.35)
    shards = []
    rnd = random.Random(7)
    for i in range(10):
        a = 2*math.pi*i/10 + rnd.uniform(-0.2, 0.2); rr = r*rnd.uniform(0.6, 1.0)
        h = rnd.uniform(0.25, 0.7)
        c = cone((rr*math.cos(a), rr*math.sin(a), z + h/2), 0.035, h*0.7, glow("shard%d" % i, colour, 1.4))
        shards.append(c)
    return d, shards

def stage(colour, relic_z=2.4, cam=(5.0, -6.0, 4.0), lens=72, glow_pts=(1.2, 0.9, 1.3)):
    reset()
    cam_o, tgt = studio(relic_z-0.25, cam, lens=lens, fstop=2.8, sun=2.2, teal=700, gold=600, fill=650)
    plinth(colour)
    halo(colour, relic_z, r=1.45, n=2)
    burst(colour, 0.80)
    embers(16, (0, 0, relic_z), (1.8, 1.8, 1.4), [glow("emb_a", colour, 1.6), glow("emb_b", GOLD, 1.4)], rmin=0.02, rmax=0.04, seed=11)
    ground_cracks((0, 0, 0.01), n=8, mat=glow("gc", colour, 0.7), seed=4, length=(3, 7))
    bpy.ops.object.light_add(type='POINT', location=(0, 0, relic_z+0.6)); pl = bpy.context.object
    pl.data.energy = 400*glow_pts[0]; pl.data.color = colour; pl.data.shadow_soft_size = 0.6
    return cam_o, tgt

# ---------- relic builders (each returns nothing; adds objects centred at (0,0,z)) ----------
def rootheart(z):
    c = col(120, 240, 220)
    gem = gem_material("heartgem", (0.05, 0.55, 0.5), c, 0.2)
    parts = [sphere((-0.42, 0, z+0.35), 0.58), sphere((0.42, 0, z+0.35), 0.58), cone((0, 0, z-0.55), 0.85, 1.4, gem, rot=(math.pi, 0, 0)), sphere((0, 0, z+0.05), 0.72)]
    heart = fuse(parts, voxel=0.06, disp=0.0, name="heart", facet=0.0); setmat(heart, gem); facet(heart, 16)
    heart.scale = (1, 0.62, 1)
    core = setmat(sphere((0, 0, z-0.05), 0.28, 16), glow("heartcore", c, 2.6)); core.scale = (1, 0.7, 1.2)
    gt = glow("goldthread", GOLD, 1.3)
    for k in range(7):
        y0 = z+0.85-k*0.24
        tube([(-0.16, -0.40, y0), (0.16, -0.40, y0-0.12)], 0.022, gt, bevres=3)
    tube([(0, -0.44, z+0.9), (0, -0.46, z-0.8)], 0.016, gt, bevres=3)
    bark = surface("bark", base=(0.34, 0.21, 0.10), dark=(0.10, 0.06, 0.03), crack=c, crack_str=1.2, crack_scale=1.4, crack_width=0.02, crack_center=(0, 0, z), crack_radius=1.5, rough=0.9, bump=0.7, stripes=6)
    leafm = surface("rootleaf", base=(0.16, 0.42, 0.16), dark=(0.04, 0.14, 0.05), crack_str=0, rough=0.6, sheen=0.4)
    rnd = random.Random(3)
    for i in range(7):
        a = 2*math.pi*i/7 + rnd.uniform(-0.3, 0.3)
        pts = [(0.15*math.cos(a), 0.10*math.sin(a), z-0.55)]
        rr = 0.35; zz = z-0.55
        for k in range(4):
            rr += 0.32; zz -= 0.28 + 0.1*k; a += rnd.uniform(-0.35, 0.35)
            pts.append((rr*math.cos(a), 0.7*rr*math.sin(a), max(zz, 0.82)))
        tube(pts, 0.09 - 0.012*i/7, bark)
        if i % 2 == 0:
            p = pts[2]; leaf((p[0]*1.1, p[1]*1.1, p[2]+0.12), 0.22, (0.3, 0.5, a), leafm)
    pts = [((0.95+0.08*math.sin(6*t))*math.cos(t*5), 0.62*math.sin(t*5), z-0.5+t*1.3) for t in [i/50 for i in range(51)]]
    tube(pts, 0.04, bark)
    for t in (0.2, 0.55, 0.85):
        p = ((0.95)*math.cos(t*5), 0.62*math.sin(t*5), z-0.5+t*1.3); leaf((p[0]*1.12, p[1]*1.12, p[2]+0.1), 0.16, (0.4, 0.2, t*5), leafm)

def grindcore(z):
    stone = surface("gcstone", base=(0.46, 0.45, 0.47), dark=(0.16, 0.16, 0.18), crack=TEAL, crack_str=0, rough=0.75, bump=0.3, noise_scale=6)
    brass = surface("gcbrass", base=(0.78, 0.55, 0.2), dark=(0.3, 0.2, 0.05), crack_str=0, rough=0.3, metallic=0.95, bump=0.15)
    dark = plain("groove", (0.06, 0.06, 0.07), 0.9)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1.0, depth=0.38, location=(0, 0, 0)); disc = bpy.context.object
    parts = [disc]
    for i in range(14):
        a = 2*math.pi*i/14
        t = cube((1.12*math.cos(a), 1.12*math.sin(a), 0), (0.7, 0.42, 0.7), rot=(0, 0, a)); parts.append(t)
    for p in parts: clear_slots(p)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = disc; bpy.ops.object.join(); gear = bpy.context.object
    setmat(gear, stone); bevel(gear, 0.03, 3)
    objs = [gear]
    for i in range(8):
        a = 2*math.pi*i/8 + math.pi/8
        g = cube((0.66*math.cos(a), 0.66*math.sin(a), 0.19), (0.9, 0.14, 0.06), rot=(0, 0, a)); setmat(g, dark); objs.append(g)
        b = cube((0.66*math.cos(a), 0.66*math.sin(a), 0.2), (0.86, 0.06, 0.05), rot=(0, 0, a)); setmat(b, brass); objs.append(b)
    hub = setmat(ring((0, 0, 0.19), 0.36, 0.06, brass), brass); objs.append(hub)
    hub2 = setmat(ring((0, 0, 0.19), 0.98, 0.035, brass), brass); objs.append(hub2)
    core = setmat(sphere((0, 0, 0), 0.30, 16), glow("gccore", TEAL, 2.4)); objs.append(core)
    for i in range(6):
        a = 2*math.pi*i/6
        sp = cube((0.17*math.cos(a), 0.17*math.sin(a), 0.2), (0.36, 0.05, 0.05), rot=(0, 0, a)); setmat(sp, brass); objs.append(sp)
    e = group(objs, (0, 0, z), (math.pi/2, 0, -0.35))
    rnd = random.Random(21); chip = plain("chip", (0.55, 0.55, 0.58), 0.9)
    for i in range(30):
        a = rnd.uniform(-0.3, 2.2); r = 1.3 + a*0.35
        c = cubeS((r*math.cos(a)*0.95, -0.2 - a*0.25, z+r*math.sin(a)), rnd.uniform(0.03, 0.08), rot=(rnd.uniform(0, 3), rnd.uniform(0, 3), 0))
        setmat(c, chip if i % 3 else glow("gritglow", TEAL, 1.6))

def thornseed(z):
    leafmat = surface("leaf", base=(0.13, 0.45, 0.17), dark=(0.03, 0.14, 0.05), crack_str=0, rough=0.55, bump=0.3, noise_scale=5, sheen=0.5)
    pod = sphere((0, 0, z), 0.75, 48); pod.scale = (0.8, 0.8, 1.25); setmat(pod, leafmat); smooth(pod)
    vm = glow("vein", TEAL, 1.5)
    for i in range(6):
        ph = 2*math.pi*i/6 + 0.2
        pts = [(0.6*math.sin(t)*math.cos(ph)*0.995, 0.6*math.sin(t)*math.sin(ph)*0.995, z+0.94*math.cos(t)*0.995) for t in [0.15+2.8*k/24 for k in range(25)]]
        tube(pts, 0.022, vm, bevres=4)
    thorn = surface("thornmat", base=(0.82, 0.62, 0.24), dark=(0.35, 0.22, 0.05), crack_str=0, rough=0.35, metallic=0.6)
    rnd = random.Random(5)
    for i in range(16):
        th = rnd.uniform(0.35, 2.6); ph = rnd.uniform(0, 6.28)
        d = Vector((math.sin(th)*math.cos(ph)*0.6, math.sin(th)*math.sin(ph)*0.6, math.cos(th)*0.94))
        p = Vector((0, 0, z)) + d*0.97 + d.normalized()*0.18
        c = cone((*p,), 0.075, 0.45, thorn); c.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); facet(c, 30)
    for i in range(5):
        a = 2*math.pi*i/5
        l = leaf((0.55*math.cos(a), 0.55*math.sin(a), z-0.95), 0.55, (0, -0.9, a), leafmat)
    setmat(sphere((0, 0, z+1.3), 0.10), glow("seedtip", GOLD, 2.2))
    tube([(0, 0, z+1.3), (0.1, 0.05, z+1.55), (0.3, 0.0, z+1.7), (0.42, -0.1, z+1.62)], 0.02, leafmat)
    leaf((0.5, -0.15, z+1.62), 0.18, (0.3, 0.6, -0.3), leafmat)

def edgestep(z):
    steel = surface("claw", base=(0.30, 0.30, 0.36), dark=(0.04, 0.04, 0.06), crack=GOLD, crack_str=0, rough=0.25, metallic=0.9, bump=0.1)
    edge = glow("edge", GOLD, 2.2)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1.35, depth=0.14, location=(0, 0, z), rotation=(math.pi/2, 0, 0)); outer = bpy.context.object
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1.15, depth=0.5, location=(0.55, 0, z+0.35), rotation=(math.pi/2, 0, 0)); inner = bpy.context.object
    md = outer.modifiers.new('bool', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = inner
    inner.hide_render = True; inner.hide_viewport = True
    setmat(outer, steel); bevel(outer, 0.03, 3)
    pts = [(0.55+1.15*math.cos(t), 0, z+0.35+1.15*math.sin(t)) for t in [math.pi*0.55+i*(math.pi*1.05)/40 for i in range(41)]]
    tube(pts, 0.03, edge)
    # cord wrap at the thick end + teal pommel
    cord = surface("cord", base=(0.3, 0.18, 0.08), dark=(0.1, 0.05, 0.02), crack_str=0, rough=0.9, stripes=14)
    d = Vector((-0.55, 0, -0.35)).normalized(); tng = Vector((d.z, 0, -d.x)); mid = Vector((-0.78, 0, z-0.50))
    th = math.atan2(tng.x, tng.z)
    for k in (-0.16, 0.0, 0.16):
        p = mid + tng*k
        ring((p.x, 0, p.z), 0.42, 0.05, cord, rot=(0, th, 0))
    pp = mid + tng*0.34
    ring((pp.x, 0, pp.z), 0.30, 0.04, glow("pommel", TEAL, 1.8), rot=(0, th, 0))
    # dash trail: faint gold streaks behind the blade
    for i in range(6):
        y = 0.5 + i*0.22
        st = tube([(0.9+0.3*i, y, z+0.9-0.2*i), (2.6+0.3*i, y*1.3, z+0.9-0.2*i)], 0.012, glow("streak%d" % i, GOLD, 1.0-0.1*i), bevres=3)
    for o in list(bpy.context.scene.objects):
        if o.type in ('MESH', 'CURVE') and o.location.z > 1.0 and not o.name.startswith(('Icosphere', 'Cone', 'Cube')) and not (o.name.startswith('Torus') and abs(o.location.x) < 0.01 and abs(o.location.y) < 0.01):
            o.rotation_euler.z += -0.35
            x, y = o.location.x, o.location.y
            o.location.x = x*math.cos(-0.35) - y*math.sin(-0.35); o.location.y = x*math.sin(-0.35) + y*math.cos(-0.35)

def drumpulse(z):
    brass = surface("drumbrass", base=(0.74, 0.48, 0.15), dark=(0.28, 0.16, 0.04), crack_str=0, rough=0.32, metallic=0.95, bump=0.12, noise_scale=9)
    dark = surface("drumwood", base=(0.22, 0.12, 0.06), dark=(0.08, 0.04, 0.02), crack_str=0, rough=0.7, bump=0.3, stripes=20)
    skin = ring_emission_material("drumskin", (0.9, 0.6, 0.3), (1.0, 0.5, 0.12), scale=7.0, strength=2.2)
    objs = []
    body = setmat(cyl((0, 0, -0.2), 0.95, 1.2), dark); bevel(body, 0.04, 3); objs.append(body)
    for k in (-0.72, 0.42):
        h = setmat(ring((0, 0, -0.2+k), 0.97, 0.07, brass), brass); objs.append(h)
    top = setmat(cyl((0, 0, 0.42), 0.9, 0.06), skin); objs.append(top)
    for i in range(10):
        a = 2*math.pi*i/10
        rod = setmat(cyl((0.99*math.cos(a), 0.99*math.sin(a), -0.15), 0.035, 1.15), brass); objs.append(rod)
        for zz in (0.42, -0.92):
            rv = setmat(sphere((0.99*math.cos(a), 0.99*math.sin(a), -0.2+zz), 0.06, 10), brass); objs.append(rv)
    mal = setmat(cyl((0.35, -0.3, 1.05), 0.04, 1.2, rot=(0.5, 0.35, 0)), dark); objs.append(mal)
    head = setmat(sphere((0.15, -0.12, 0.6), 0.16, 16), brass); objs.append(head)
    for i, sc in enumerate((1.05, 1.3, 1.6)):
        r = ring((0, 0, 0.45+0.03*i), sc, 0.012, glow("pulse%d" % i, (1.0, 0.6, 0.2), 1.4-0.3*i)); r.scale = (1, 1, 0.4); objs.append(r)
    group(objs, (0, 0, z), (0.18, 0, 0.4))

def cogloop(z):
    brass = surface("cogbrass", base=(0.72, 0.5, 0.16), dark=(0.28, 0.17, 0.04), crack_str=0, rough=0.3, metallic=0.9, bump=0.15)
    parts = [ring((0, 0, z), 1.0, 0.22, brass, rot=(math.pi/2, 0, 0))]
    for i in range(16):
        a = 2*math.pi*i/16
        parts.append(cube((1.2*math.cos(a), 0, z+1.2*math.sin(a)), (0.4, 0.5, 0.36), rot=(0, -a, 0)))
    for p in parts[1:]: clear_slots(p)
    cog = fuse(parts, voxel=0.04, disp=0.0, name="cog", facet=0.0); setmat(cog, brass); bevel(cog, 0.015, 2)
    inner = setmat(ring((0, 0, z), 0.62, 0.05, glow("cogglow", TEAL, 2.6), rot=(math.pi/2, 0, 0)), glow("cogglow", TEAL, 2.6))
    gem = setmat(sphere((0, 0, z), 0.3, 12), glass("coggem", (0.0, 0.5, 0.45), 0.05)); gem.scale = (1, 0.55, 1)
    gem.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (*TEAL, 1)
    gem.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0
    # hands
    for ang, ln in ((0.6, 0.55), (2.4, 0.4)):
        h = cubeS((0.5*ln*math.cos(ang), -0.26, z+0.5*ln*math.sin(ang)), 1.0, rot=(0, -ang, 0)); h.scale = (ln, 0.05, 0.09); setmat(h, glow("hand", GOLD, 2.0))

def hivecall(z):
    wax = surface("wax", base=(0.86, 0.62, 0.2), dark=(0.42, 0.26, 0.05), crack_str=0, rough=0.5, bump=0.3, noise_scale=6, sheen=0.3)
    honey = glow("honey", (1.0, 0.65, 0.15), 1.6)
    objs = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=1.25, depth=0.3, location=(0, 0, 0)); plate = bpy.context.object; setmat(plate, wax); bevel(plate, 0.04, 3); objs.append(plate)
    rnd = random.Random(8); dx = 0.30; dy = dx*math.sqrt(3)/2
    for row in range(-3, 4):
        for colx in range(-4, 5):
            x = colx*dx + (dx/2 if row % 2 else 0); y = row*dy
            if math.hypot(x, y) > 0.95: continue
            capped = rnd.random() < 0.3
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.13, depth=0.16 if capped else 0.08, location=(x, y, 0.15+(0.06 if capped else 0.02)), rotation=(0, 0, math.pi/6))
            cell = bpy.context.object; setmat(cell, wax if capped else honey); objs.append(cell)
    beem = band_material("bee", (0.95, 0.72, 0.15), (0.03, 0.03, 0.03), scale=5.5, axis='X', rough=0.5)
    b = setmat(sphere((0, 0, 0), 0.30, 24), beem); b.scale = (1.5, 0.95, 0.9); smooth(b)
    th = setmat(sphere((0.38, 0, 0.02), 0.19, 16), plain("thorax", (0.25, 0.18, 0.05), 0.6)); smooth(th)
    hd = setmat(sphere((0.62, 0, 0.0), 0.15, 16), plain("beehead", (0.06, 0.06, 0.06), 0.4)); smooth(hd)
    bee = [b, th, hd]
    for sgn in (-1, 1):
        e = setmat(sphere((0.7, sgn*0.09, 0.05), 0.05, 8), glow("beeeye", TEAL, 1.8)); bee.append(e)
        wm = bpy.data.materials.new("wing"); wm.use_nodes = True; q = wm.node_tree.nodes["Principled BSDF"]
        q.inputs["Base Color"].default_value = (0.75, 0.97, 0.95, 1); q.inputs["Alpha"].default_value = 0.6; q.inputs["Roughness"].default_value = 0.15
        q.inputs["Emission Color"].default_value = (0.5, 0.95, 0.9, 1); q.inputs["Emission Strength"].default_value = 0.35
        w = setmat(sphere((0.15, sgn*0.24, 0.34), 0.40, 16), wm); w.scale = (1.4, 0.5, 0.05); w.rotation_euler = (sgn*0.7, 0, sgn*0.4); bee.append(w)
        vein = tube([(0.15+0.05, sgn*0.24, 0.35), (0.15+0.5*math.cos(sgn*0.4), sgn*(0.24+0.45*math.sin(0.4)), 0.35+0.3)], 0.012, glow("wingvein", TEAL, 1.2), bevres=3); bee.append(vein)
        ant = tube([(0.7, sgn*0.05, 0.1), (0.85, sgn*0.15, 0.25)], 0.012, plain("ant", (0.05, 0.05, 0.05)), bevres=3); bee.append(ant)
        for k in range(3):
            lg = tube([(0.3-0.2*k, sgn*0.2, -0.1), (0.3-0.2*k, sgn*0.32, -0.3)], 0.015, plain("leg", (0.05, 0.05, 0.05)), bevres=3); bee.append(lg)
    st = setmat(cone((-0.5, 0, 0), 0.06, 0.2, glow("sting", TEAL, 2.0), rot=(0, -math.pi/2, 0)), glow("sting", TEAL, 2.0)); bee.append(st)
    group(bee, (0.1, -0.75, z+0.15), (0.2, 0.0, 0.6), 0.9)
    e = group(objs, (0, 0, z), (math.pi/2, 0, -0.3))
    for i in range(3):
        a = 2*math.pi*i/3 + 0.5
        d = setmat(sphere((1.7*math.cos(a), 1.2*math.sin(a), z+0.6*math.sin(a*2)), 0.08, 10), beem); d.scale = (1.5, 1, 1); d.rotation_euler = (0, 0, a+math.pi/2)
        setmat(sphere((1.7*math.cos(a)-0.1*math.sin(a), 1.2*math.sin(a)+0.1*math.cos(a), z+0.6*math.sin(a*2)), 0.05, 8), plain("dhead", (0.05, 0.05, 0.05)))
        tube([(1.7*math.cos(a), 1.2*math.sin(a), z+0.6*math.sin(a*2)), (0.9*math.cos(a+0.6), 0.6*math.sin(a+0.6), z+0.3*math.sin(a*2)), (0, -0.7, z)], 0.008, glow("lane", GOLD, 1.0), bevres=3)

def sealmark(z):
    stone = surface("sealstone", base=(0.38, 0.34, 0.5), dark=(0.10, 0.08, 0.16), crack=GOLD, crack_str=0, rough=0.7, bump=0.4)
    tab = cubeS((0, 0, z), 1.0); tab.scale = (1.55, 0.2, 2.0); setmat(tab, stone); bevel(tab, 0.05, 3)
    gm = glow("sigil", GOLD, 2.6); tm = glow("sigilt", TEAL, 3.0)
    # engraved sigil: outer ring, inner triangle, centre eye
    r = ring((0, -0.17, z), 0.62, 0.035, gm, rot=(math.pi/2, 0, 0))
    for i in range(3):
        a = math.pi/2 + 2*math.pi*i/3; a2 = math.pi/2 + 2*math.pi*(i+1)/3
        p1 = (0.5*math.cos(a), -0.17, z+0.5*math.sin(a)); p2 = (0.5*math.cos(a2), -0.17, z+0.5*math.sin(a2))
        tube([p1, p2], 0.03, gm, bevres=4)
    eye = setmat(sphere((0, -0.19, z-0.05), 0.11, 12), tm)
    # runes along the edges
    for k in range(4):
        for s in (-1, 1):
            c = cubeS((s*0.72, -0.17, z-0.6+k*0.4), 1.0); c.scale = (0.06, 0.03, 0.16); setmat(c, gm)
    # ward shell
    wm = bpy.data.materials.new("ward"); wm.use_nodes = True; nt = wm.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.1, 0.9, 0.8, 1); p.inputs["Roughness"].default_value = 0.4; p.inputs["Alpha"].default_value = 0.10
    p.inputs["Emission Color"].default_value = (*TEAL, 1); p.inputs["Emission Strength"].default_value = 0.25
    # hex ward plates on the shell
    rnd = random.Random(17)
    for i in range(14):
        th = rnd.uniform(0.5, 2.6); ph = rnd.uniform(0, 6.28)
        d = Vector((math.sin(th)*math.cos(ph), math.sin(th)*math.sin(ph), math.cos(th)))
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.16, depth=0.01, location=(d.x*1.46, d.y*1.46, z+d.z*1.46)); hx = bpy.context.object
        hx.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); hm = bpy.data.materials.new("hexw%d" % i); hm.use_nodes = True; q = hm.node_tree.nodes["Principled BSDF"]
        q.inputs["Alpha"].default_value = 0.35; q.inputs["Emission Color"].default_value = (*TEAL, 1); q.inputs["Emission Strength"].default_value = 1.2; setmat(hx, hm)

def loomthread(z):
    gold = surface("spoolgold", base=(0.8, 0.58, 0.2), dark=(0.35, 0.22, 0.05), crack_str=0, rough=0.3, metallic=0.9, bump=0.15)
    thread = surface("thread", base=(0.1, 0.8, 0.7), dark=(0.02, 0.3, 0.28), crack_str=0, rough=0.7, stripes=30, sheen=0.5)
    setmat(cyl((0, 0, z), 0.5, 1.5), thread)
    for s in (-1, 1):
        d = setmat(cyl((0, 0, z+s*0.85), 0.85, 0.2), gold); bevel(d, 0.04, 3)
    setmat(cyl((0, 0, z), 0.12, 2.3), gold)
    # thread winding around the spool as a helix
    pts = [(0.53*math.cos(t*7), 0.53*math.sin(t*7), z-0.7+t*1.4) for t in [i/120 for i in range(121)]]
    tube(pts, 0.035, glow("threadglow", TEAL, 1.8))
    # trailing thread down to the plinth
    tail = [(0.53, 0, z-0.7), (0.9, 0.3, z-1.0), (1.3, -0.2, z-1.4), (1.6, 0.4, 0.85)]
    tube(tail, 0.03, glow("threadglow2", TEAL, 2.2))
    # keystone facet floating above
    ks = setmat(sphere((0, 0, z+1.45), 0.22, 8), glow("keystone", GOLD, 1.7)); ks.rotation_euler = (0.4, 0.3, 0)

def lintwisp(z):
    fluff = surface("fluff", base=(0.68, 0.66, 0.66), dark=(0.36, 0.34, 0.36), crack_str=0, rough=1.0, bump=0.6, noise_scale=12.0, sheen=1.0)
    rnd = random.Random(9); parts = [sphere((0, 0, z), 0.8, 20)]
    for i in range(22):
        th = rnd.uniform(0, 3.14); ph = rnd.uniform(0, 6.28)
        d = (math.sin(th)*math.cos(ph), math.sin(th)*math.sin(ph), math.cos(th))
        parts.append(sphere((d[0]*0.7, d[1]*0.7, z+d[2]*0.7), rnd.uniform(0.25, 0.45), 12))
    body = fuse(parts, voxel=0.07, disp=0.22, disp_scale=1.6, name="lint", facet=0.0); setmat(body, fluff); smooth(body)
    bm = plain("button", (0.9, 0.7, 0.25), 0.4, 0.8)
    fwd = Vector((0.64, -0.77, 0.0)); side = Vector((0.77, 0.64, 0.0)); q = fwd.to_track_quat('Z', 'Y').to_euler()
    for s in (-1, 1):
        c = fwd*0.86 + side*(s*0.3); c.z = z+0.18
        b = setmat(cyl((c.x, c.y, c.z), 0.16, 0.06, rot=q), bm)
        for k in range(4):
            a = k*math.pi/2 + math.pi/4
            h = c + side*(0.06*math.cos(a)) + fwd*0.03; h.z += 0.06*math.sin(a)
            setmat(cyl((h.x, h.y, h.z), 0.02, 0.05, rot=q), plain("hole", (0.05, 0.05, 0.05)))
    # stray fibres
    rnd2 = random.Random(31); wisp = plain("wisp", (0.82, 0.8, 0.8), 1.0)
    for i in range(70):
        th = rnd2.uniform(0.3, 2.9); ph = rnd2.uniform(0, 6.28)
        d = Vector((math.sin(th)*math.cos(ph), math.sin(th)*math.sin(ph), math.cos(th)))
        p0 = d*0.9; p0.z += z; L = rnd2.uniform(0.15, 0.4)
        side = Vector((rnd2.uniform(-1, 1), rnd2.uniform(-1, 1), rnd2.uniform(-1, 1))).normalized()
        p1 = p0 + d*L*0.5 + side*L*0.25; p2 = p0 + d*L + side*L*0.6
        tube([(*p0,), (*p1,), (*p2,)], 0.0045, wisp, bevres=2)
    # loose thread
    pts = [(0.5, -0.5, z-0.5), (0.8, -0.7, z-0.9), (0.6, -0.9, z-1.3), (0.9, -0.6, 0.85)]
    tube(pts, 0.025, glow("lintthread", TEAL, 1.8))

def knotcharm(z):
    rope = surface("rope", base=(0.62, 0.42, 0.18), dark=(0.25, 0.15, 0.05), crack_str=0, rough=0.85, bump=0.6, stripes=24, noise_scale=6)
    pts = [(x*0.95, y*0.95, z+zz*0.95) for (x, y, zz) in torus_knot(2, 3, 0.75, 0.32, 200)]
    k = tube(pts, 0.14, rope, closed=True)
    # teal core thread running inside the rope (visible as glow through gaps)
    tube([(x*1.0, y*1.0, zz) for (x, y, zz) in pts], 0.03, glow("knotglow", TEAL, 2.4), closed=True)
    # charm tag
    tag = setmat(sphere((0, 0, z-1.0), 0.22, 10), glow("tag", GOLD, 1.3)); tag.scale = (1, 0.4, 1.3); facet(tag, 20)

def firstcut_shard(z):
    obs = surface("obsid", base=(0.08, 0.05, 0.12), dark=(0.01, 0.0, 0.02), crack=GOLD, crack_str=0, rough=0.12, metallic=0.2, bump=0.0)
    parts = [cone((0, 0, z+0.2), 0.5, 2.4, obs), cone((0.15, 0.1, z-0.3), 0.42, 1.6, obs, rot=(0.25, -0.2, 0)), cone((-0.18, -0.05, z-0.1), 0.35, 1.9, obs, rot=(-0.15, 0.3, 0))]
    for p in parts: clear_slots(p)
    sh = fuse(parts, voxel=0.045, disp=0.0, name="shard", facet=0.0); setmat(sh, obs)
    md = sh.modifiers.new('dec', 'DECIMATE'); md.decimate_type = 'DISSOLVE'; md.angle_limit = math.radians(18)
    # the cut: a gold seam splitting it, and a rip of teal void behind
    seam = tube([(-0.35, -0.5, z-0.9), (-0.05, -0.52, z-0.2), (0.12, -0.45, z+0.5), (0.05, -0.3, z+1.2)], 0.035, glow("cutseam", GOLD, 3.4))
    rip = setmat(sphere((0.1, 0.55, z+0.1), 0.9, 24), glass("void", (0.0, 0.0, 0.0), 0.0)); rip.scale = (0.02, 0.35, 1.25); rip.rotation_euler = (0, 0, 0.5)
    rip.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (*TEAL, 1)
    rip.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.9
    # floating fragments
    rnd = random.Random(13)
    for i in range(9):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(0.9, 1.6)
        f = cone((r*math.cos(a), r*math.sin(a), z+rnd.uniform(-1.0, 1.2)), rnd.uniform(0.05, 0.12), rnd.uniform(0.2, 0.45), obs, rot=(rnd.uniform(0, 3), rnd.uniform(0, 3), 0))

def overweaver_shuttle(z):
    wood = surface("shuttlewood", base=(0.30, 0.16, 0.50), dark=(0.08, 0.04, 0.16), crack=GOLD, crack_str=1.4, crack_scale=1.2, crack_width=0.02, crack_center=(0, 0, 0), crack_radius=1.8, rough=0.35, metallic=0.15, bump=0.2)
    gold = surface("shuttlegold", base=(0.8, 0.58, 0.2), dark=(0.35, 0.22, 0.05), crack_str=0, rough=0.3, metallic=0.9)
    objs = []
    body = sphere((0, 0, 0), 0.45, 48); body.scale = (3.3, 0.95, 0.85); smooth(body)
    hole = cube((0, 0, 0.42), (4.2, 1.1, 1.4))
    md = body.modifiers.new('bool', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = hole; md.solver = 'EXACT'
    bpy.context.view_layer.objects.active = body; body.select_set(True)
    with bpy.context.temp_override(object=body, active_object=body, selected_objects=[body]):
        bpy.ops.object.modifier_apply(modifier='bool')
    print("SHUTTLE verts", len(body.data.vertices)); bpy.data.objects.remove(hole)
    setmat(body, wood); objs.append(body)
    for sgn in (-1, 1):
        tip = cone((sgn*1.62, 0, 0), 0.2, 0.5, gold, rot=(0, sgn*math.pi/2, 0)); facet(tip, 30); objs.append(tip)
    bob = setmat(cyl((0, 0, -0.05), 0.07, 1.1, rot=(0, math.pi/2, 0)), gold); objs.append(bob)
    thr = surface("bobthread", base=(0.9, 0.7, 0.3), dark=(0.5, 0.35, 0.1), crack_str=0, rough=0.6, stripes=40, sheen=0.5)
    wound = setmat(cyl((0, 0, -0.05), 0.15, 0.9, rot=(0, math.pi/2, 0)), thr); objs.append(wound)
    hx = helix((0, 0, -0.05), 0.165, 0.9, 14, 0.014, glow("goldthr", GOLD, 1.3)); hx.rotation_euler = (0, math.pi/2, 0); objs.append(hx)
    for k in (-0.55, 0.55):
        cap = setmat(cyl((k, 0, -0.05), 0.19, 0.05, rot=(0, math.pi/2, 0)), gold); objs.append(cap)
    for k in (-0.9, 0.9):
        band = setmat(ring((k, 0, 0), 0.30, 0.03, gold, rot=(0, math.pi/2, 0)), gold); band.scale = (1, 1.1, 1); objs.append(band)
    e = group(objs, (0, 0, z), (0.85, -0.15, 0.3))
    for i in range(9):
        a = -1.0 + i*0.25
        pts = [(0, 0, z), (1.1*math.cos(a), 1.1*math.sin(a), z-0.5), (2.0*math.cos(a), 2.0*math.sin(a), 0.85)]
        tube(pts, 0.016, glow("strand%d" % i, TEAL if i % 2 else GOLD, 1.4))

RELICS = {
    'rootheart': (rootheart, col(120, 240, 220)),
    'grindcore': (grindcore, TEAL),
    'thornseed': (thornseed, col(120, 220, 110)),
    'edgestep': (edgestep, GOLD),
    'drumpulse': (drumpulse, col(255, 150, 50)),
    'cogloop': (cogloop, col(255, 200, 90)),
    'hivecall': (hivecall, col(255, 190, 70)),
    'sealmark': (sealmark, col(180, 150, 255)),
    'loomthread': (loomthread, TEAL),
    'lintwisp': (lintwisp, col(200, 205, 220)),
    'knotcharm': (knotcharm, col(240, 190, 110)),
    'firstcut_shard': (firstcut_shard, col(255, 170, 60)),
    'overweaver_shuttle': (overweaver_shuttle, col(190, 140, 255)),
}

def render(name, samples=64):
    fn, colour = RELICS[name]
    z = 2.55
    stage(colour, relic_z=z)
    fn(z)
    sc = bpy.context.scene
    sc.render.resolution_x = 700; sc.render.resolution_y = 880; sc.render.resolution_percentage = 100
    sc.cycles.samples = samples; sc.render.film_transparent = False
    sc.render.filepath = f'{OUT}/{name}.png'
    bpy.ops.render.render(write_still=True)
    print("RENDERED", name)

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['all']
    which = list(RELICS) if argv[0] == 'all' else argv[0].split(',')
    samples = int(argv[1]) if len(argv) > 1 else 64
    for n in which: render(n, samples)
