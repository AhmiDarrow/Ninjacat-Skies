"""Export a Snapped Guardian to the runtime model format used by the `guardians` companion mod.
usage: NCS_ART_ROOT=<dir> blender --background --python export_boss.py -- <boss|all> [outdir]

Per boss: one .ncgb file (little-endian binary):
  magic "NCGB", u32 version=1
  u32 nBones ; bone: str name, i32 parent
  u32 nParts ; part: str name, u8 textured, u32 nVerts, verts[ pos f32x3, normal f32x3, uv f32x2, rgb u8x3, emit u8x3, bone u16x4, weight f32x4 ], u32 nTris, tris u32x3
  (textured parts sample <boss>.png (albedo) and <boss>_emit.png (emissive, additive); untextured parts use the vertex colours)
  u32 nClips ; clip: str name, f32 fps, u32 nFrames, frames[ bones[ f32x12 (3x4 row-major affine) ] ]
  f32 height, f32 width (hitbox hints, blocks)
Coordinates are converted from Blender Z-up to Minecraft Y-up: (x, y, z) -> (x, z, -y). 1 unit = 1 block.
Colours come from a Cycles bake of the procedural materials into vertex colours (albedo) and emission.
"""
import bpy, math, sys, os, struct, time
from mathutils import Matrix, Vector
ART = os.environ.get('NCS_ART_ROOT', os.path.expanduser('~'))
sys.path.insert(0, ART); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boss_lib2 as L, boss_factory as BF

CLIPS = ('idle', 'walk', 'attack', 'death')
C = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))   # blender -> mc
CI = C.inverted()

def is_included(o, arm, roots=()):
    """skinned meshes, anything bone-parented, and animated props (drones/wards) with their children"""
    if o.type != 'MESH': return False
    if any(m.type == 'ARMATURE' for m in o.modifiers): return True
    p = o
    while p is not None:
        if p == arm or p in roots: return True
        if p.animation_data and p.animation_data.action: return True
        p = p.parent
    return False

def material_kind(m):
    if m is None: return 'plain', (0.5, 0.5, 0.5), 0.0
    nt = m.node_tree
    em = [n for n in nt.nodes if n.type == 'EMISSION']
    if em and not any(n.type == 'BSDF_PRINCIPLED' for n in nt.nodes):
        c = em[0].inputs['Color'].default_value; return 'glow', (c[0], c[1], c[2]), em[0].inputs['Strength'].default_value
    p = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]
    if p.inputs['Base Color'].is_linked: return 'baked', None, 0.0
    c = p.inputs['Base Color'].default_value; e = p.inputs['Emission Strength'].default_value
    ec = p.inputs['Emission Color'].default_value
    return 'plain', (c[0], c[1], c[2]), (e, (ec[0], ec[1], ec[2]))

def bake_vertex_colors(o):
    """bake albedo (DIFFUSE colour) and emission of a node material into two colour attributes"""
    me = o.data
    for name in ('Col', 'Emit'):
        if name not in me.color_attributes: me.color_attributes.new(name, 'BYTE_COLOR', 'CORNER')
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 4; sc.cycles.use_denoising = False
    sc.render.bake.target = 'VERTEX_COLORS'
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    me.color_attributes.active_color = me.color_attributes['Col']
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, target='VERTEX_COLORS')
    me.color_attributes.active_color = me.color_attributes['Emit']
    bpy.ops.object.bake(type='EMIT', target='VERTEX_COLORS')

def bake_textures(o, outdir, name, size=1024):
    """smart-UV the body and bake albedo + emission to two PNGs"""
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02); bpy.ops.object.mode_set(mode='OBJECT')
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = 16; sc.cycles.use_denoising = False
    sc.render.bake.target = 'IMAGE_TEXTURES'; sc.render.bake.margin = 6
    mat = o.data.materials[0]; nt = mat.node_tree
    out = {}
    for tag, btype, pf in (('', 'DIFFUSE', {'COLOR'}), ('_emit', 'EMIT', set())):
        img = bpy.data.images.new(f'{name}{tag}', size, size); img.colorspace_settings.name = 'sRGB'
        node = nt.nodes.new('ShaderNodeTexImage'); node.image = img; nt.nodes.active = node
        if pf: bpy.ops.object.bake(type=btype, pass_filter=pf, target='IMAGE_TEXTURES')
        else: bpy.ops.object.bake(type=btype, target='IMAGE_TEXTURES')
        p = os.path.join(outdir, f'{name}{tag}.png'); img.filepath_raw = p; img.file_format = 'PNG'; img.save(); out[tag] = p
        nt.nodes.remove(node)
    return out

def srgb(c):
    return tuple(int(255*max(0, min(1, (v*12.92 if v <= 0.0031308 else 1.055*v**(1/2.4)-0.055)))) for v in c[:3])

def export(name, outdir):
    t0 = time.time()
    b = BF.BOSSES[name]()
    arm = b['arm']; body = b['body']
    roots = set(b.get('drones', [])) | set(b.get('wards', []))
    objs = [o for o in bpy.data.objects if is_included(o, arm, roots)]
    # runtime budget: tiny rigid trinkets (legs, antennae) are dropped unless they glow; big rigid props are decimated
    def diag(o): return (Vector(o.dimensions)).length
    def is_skinned(o): return any(m.type == 'ARMATURE' for m in o.modifiers)
    keep = []
    for o in objs:
        kind, _, _ = material_kind(o.data.materials[0] if o.data.materials else None)
        if not is_skinned(o) and diag(o) < 0.5 and kind != 'glow': continue
        if not is_skinned(o):
            ntri = sum(len(p.vertices) - 2 for p in o.data.polygons)
            if ntri > 160:
                md = o.modifiers.new('budget', 'DECIMATE'); md.ratio = max(0.05, 160.0/ntri); md.use_collapse_triangulate = True
        keep.append(o)
    objs = keep
    print(name, 'objects:', len(objs))
    # ---- rest state: armature in rest pose, rigid rest matrices captured before any clip is keyed
    arm.data.pose_position = 'REST'; bpy.context.view_layer.update()
    rest_world = {o.name: o.matrix_world.copy() for o in objs}
    bones = [bn.name for bn in arm.data.bones]
    bone_index = {n: i for i, n in enumerate(bones)}
    bone_parent = [bone_index.get(arm.data.bones[n].parent.name, -1) if arm.data.bones[n].parent else -1 for n in bones]
    rest_bone = {n: arm.matrix_world @ arm.data.bones[n].matrix_local for n in bones}
    # rigid objects become pseudo-bones (one per object) so every animated prop rides its own track
    rigid = [o for o in objs if not any(m.type == 'ARMATURE' for m in o.modifiers)]
    for o in rigid:
        bone_index[o.name] = len(bones); bones.append(o.name); bone_parent.append(-1)
    # ---- colours
    baked = []; textured = set()
    for o in objs:
        kind, col, em = material_kind(o.data.materials[0] if o.data.materials else None)
        if kind == 'baked':
            try:
                if o == body: bake_textures(o, outdir, name); textured.add(o.name)
                else: bake_vertex_colors(o)
                baked.append(o.name)
            except Exception as e: print('bake failed', o.name, e)
    print('baked', baked, 'textured', textured, f'{time.time()-t0:.0f}s')
    # ---- mesh parts (rest pose, world space -> mc space)
    dg = bpy.context.evaluated_depsgraph_get()
    parts = []
    for o in objs:
        ev = o.evaluated_get(dg); me = ev.to_mesh()
        me.calc_loop_triangles()
        try: me.calc_normals_split()
        except Exception: pass
        kind, col, em = material_kind(o.data.materials[0] if o.data.materials else None)
        skinned = any(m.type == 'ARMATURE' for m in o.modifiers)
        M = rest_world[o.name]; Mn = M.to_3x3().inverted().transposed()
        tex = o.name in textured; uvl = me.uv_layers.active if tex else None
        colA = me.color_attributes.get('Col') if kind == 'baked' and not tex else None
        emA = me.color_attributes.get('Emit') if kind == 'baked' else None
        groups = {g.index: g.name for g in o.vertex_groups} if skinned else {}
        verts = []; tris = []; key = {}
        def vkey(vi, li):
            p = C @ (M @ me.vertices[vi].co); n = (C.to_3x3() @ (Mn @ me.loops[li].normal)).normalized()
            uv = tuple(uvl.data[li].uv) if uvl else (0.0, 0.0)
            if tex:
                c = (255, 255, 255); e = (0, 0, 0)
            elif kind == 'baked':
                c = srgb(colA.data[li].color) if colA else (128, 128, 128); e = srgb(emA.data[li].color) if emA else (0, 0, 0)
            elif kind == 'glow':
                s = min(1.0, em/3.0); c = srgb(col); e = srgb(tuple(min(1, v*max(0.6, s)) for v in col))
            else:
                c = srgb(col); e = srgb(tuple(v*min(1, em[0]/2.0) for v in em[1])) if em[0] > 0 else (0, 0, 0)
            if skinned:
                ws = sorted(((g.weight, bone_index.get(groups.get(g.group, ''), -1)) for g in me.vertices[vi].groups if bone_index.get(groups.get(g.group, ''), -1) >= 0), reverse=True)[:4]
                tot = sum(w for w, _ in ws) or 1.0; ws = [(w/tot, bi) for w, bi in ws]
            else:
                ws = [(1.0, bone_index[o.name])]
            while len(ws) < 4: ws.append((0.0, 0))
            k = (round(p.x, 4), round(p.y, 4), round(p.z, 4), round(n.x, 3), round(n.y, 3), round(n.z, 3), c, e, round(uv[0], 4), round(uv[1], 4))
            if k not in key: key[k] = len(verts); verts.append((p, n, c, e, ws, uv))
            return key[k]
        for tri in me.loop_triangles:
            tris.append(tuple(vkey(tri.vertices[i], tri.loops[i]) for i in range(3)))
        parts.append((o.name, verts, tris, tex)); ev.to_mesh_clear()
    # ---- clips: per-frame bone deltas (pose @ rest^-1) and rigid deltas, in mc space
    arm.data.pose_position = 'POSE'
    clips = []
    for kind in CLIPS:
        BF.animate(b, kind)
        sc = bpy.context.scene; n = sc.frame_end
        frames = []
        for f in range(1, n+1):
            sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
            row = []
            for bn in arm.data.bones:
                pb = arm.pose.bones[bn.name]
                D = C @ (arm.matrix_world @ pb.matrix @ rest_bone[bn.name].inverted() @ arm.matrix_world.inverted()) @ CI
                row.append(D)
            for o in rigid:
                D = C @ (o.evaluated_get(dg).matrix_world @ rest_world[o.name].inverted()) @ CI
                row.append(D)
            frames.append(row)
        clips.append((kind, 24.0, frames))
        print(' clip', kind, n, 'frames')
    # ---- size hints
    xs = [v[0] for _, vs, _, _ in parts for v in vs]
    height = max(v.y for v in xs); width = max(max(abs(v.x), abs(v.z)) for v in xs)*2
    # ---- write
    out = os.path.join(outdir, f'{name}.ncgb'); os.makedirs(outdir, exist_ok=True)
    with open(out, 'wb') as fh:
        w = fh.write
        def s(x): bb = x.encode(); w(struct.pack('<H', len(bb))); w(bb)
        w(b'NCGB'); w(struct.pack('<I', 1))
        w(struct.pack('<I', len(bones)))
        for i, bn in enumerate(bones): s(bn); w(struct.pack('<i', bone_parent[i]))
        w(struct.pack('<I', len(parts)))
        nv = nt = 0
        for pname, verts, tris, tex in parts:
            s(pname); w(struct.pack('<BI', 1 if tex else 0, len(verts)))
            for p, n, c, e, ws, uv in verts:
                w(struct.pack('<8f', p.x, p.y, p.z, n.x, n.y, n.z, uv[0], 1.0-uv[1])); w(bytes(c)); w(bytes(e))
                w(struct.pack('<4H', *[bi for _, bi in ws])); w(struct.pack('<4f', *[wt for wt, _ in ws]))
            w(struct.pack('<I', len(tris)))
            for t in tris: w(struct.pack('<3I', *t))
            nv += len(verts); nt += len(tris)
        w(struct.pack('<I', len(clips)))
        for cname, fps, frames in clips:
            s(cname); w(struct.pack('<fI', fps, len(frames)))
            for row in frames:
                for D in row: w(struct.pack('<12f', *[D[r][c] for r in range(3) for c in range(4)]))
        w(struct.pack('<2f', height, width))
    print(f'WROTE {out}: bones={len(bones)} parts={len(parts)} verts={nv} tris={nt} height={height:.1f} width={width:.1f} size={os.path.getsize(out)//1024}KB {time.time()-t0:.0f}s')

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['all']
    which = list(BF.BOSSES) if argv[0] == 'all' else argv[0].split(',')
    outdir = argv[1] if len(argv) > 1 else os.path.join(ART, 'export')
    for n in which: export(n, outdir)
