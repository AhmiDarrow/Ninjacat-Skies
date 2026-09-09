import bpy, math, random
def reset():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
    for c in (bpy.data.materials,bpy.data.textures,bpy.data.meshes,bpy.data.armatures):
        for x in list(c):
            try: c.remove(x)
            except: pass
def sphere(loc,r,seg=24): 
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r,location=loc,segments=seg,ring_count=seg//2); return bpy.context.object
def cube(loc,size,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.scale=(size[0]/2,size[1]/2,size[2]/2); o.rotation_euler=rot; return o
def cyl(loc,r,h,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=h,location=loc,vertices=24); o=bpy.context.object; o.rotation_euler=rot; return o
def fuse(objs,voxel=0.16,disp=0.12,disp_scale=0.9,name="body",facet=0.0):
    """join overlapping volumes -> voxel remesh into ONE manifold solid -> subtle displacement crags"""
    for o in objs: 
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]; bpy.ops.object.join(); body=bpy.context.object; body.name=name
    body.data.materials.clear()  # drop any inherited placeholder slots so the surface material owns every face
    rm=body.modifiers.new("remesh",'REMESH'); rm.mode='VOXEL'; rm.voxel_size=voxel; rm.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier="remesh")
    if disp>0:
        t=bpy.data.textures.new("crag",type='CLOUDS'); t.noise_scale=disp_scale; t.noise_depth=3
        d=body.modifiers.new("crag",'DISPLACE'); d.texture=t; d.strength=disp; d.mid_level=0.5
        bpy.ops.object.modifier_apply(modifier="crag")
    if facet:
        dm=body.modifiers.new("facet",'DECIMATE'); dm.ratio=facet
        bpy.ops.object.modifier_apply(modifier="facet")
        bpy.ops.object.shade_flat()
    else:
        bpy.ops.object.shade_smooth()
    return body
def rock_material(name, base=(0.20,0.13,0.08), dark=(0.07,0.045,0.03), moss=(0.16,0.28,0.09), crack=(0.1,0.95,0.8), crack_str=3.0, moss_on=True, rough=0.92, bump=0.45, crack_scale=0.55, crack_width=0.02, crack_center=(0,-1.5,6.9), crack_radius=4.5):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new("ShaderNodeOutputMaterial"); p=nt.nodes.new("ShaderNodeBsdfPrincipled"); nt.links.new(p.outputs[0],out.inputs[0])
    p.inputs["Roughness"].default_value=rough
    tc=nt.nodes.new("ShaderNodeTexCoord")
    # colour variation
    n1=nt.nodes.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value=3.0; n1.inputs["Detail"].default_value=6; nt.links.new(tc.outputs["Object"],n1.inputs["Vector"])
    ramp=nt.nodes.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color=(*dark,1); ramp.color_ramp.elements[1].color=(*base,1); ramp.color_ramp.elements[0].position=0.35; ramp.color_ramp.elements[1].position=0.65
    nt.links.new(n1.outputs["Fac"],ramp.inputs["Fac"])
    col=ramp.outputs["Color"]
    if moss_on:
        geo=nt.nodes.new("ShaderNodeNewGeometry"); sep=nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Normal"],sep.inputs[0])
        mn=nt.nodes.new("ShaderNodeTexNoise"); mn.inputs["Scale"].default_value=6; nt.links.new(tc.outputs["Object"],mn.inputs["Vector"])
        mmath=nt.nodes.new("ShaderNodeMath"); mmath.operation='MULTIPLY_ADD'; nt.links.new(sep.outputs["Z"],mmath.inputs[0]); mmath.inputs[1].default_value=1.4; nt.links.new(mn.outputs["Fac"],mmath.inputs[2])
        mramp=nt.nodes.new("ShaderNodeMapRange"); mramp.inputs["From Min"].default_value=1.05; mramp.inputs["From Max"].default_value=1.35; nt.links.new(mmath.outputs[0],mramp.inputs["Value"])
        mix=nt.nodes.new("ShaderNodeMix"); mix.data_type='RGBA'; nt.links.new(mramp.outputs[0],mix.inputs["Factor"]); nt.links.new(col,mix.inputs[6]); mix.inputs[7].default_value=(*moss,1)
        col=mix.outputs[2]
    nt.links.new(col,p.inputs["Base Color"])
    # glowing crack network
    v=nt.nodes.new("ShaderNodeTexVoronoi"); v.feature='DISTANCE_TO_EDGE'; v.inputs["Scale"].default_value=crack_scale; nt.links.new(tc.outputs["Object"],v.inputs["Vector"])
    lt=nt.nodes.new("ShaderNodeMath"); lt.operation='LESS_THAN'; lt.inputs[1].default_value=crack_width; nt.links.new(v.outputs["Distance"],lt.inputs[0])
    flick=nt.nodes.new("ShaderNodeTexNoise"); flick.inputs["Scale"].default_value=1.0; nt.links.new(tc.outputs["Object"],flick.inputs["Vector"])
    gate=nt.nodes.new("ShaderNodeMath"); gate.operation='MULTIPLY'; nt.links.new(lt.outputs[0],gate.inputs[0]); nt.links.new(flick.outputs["Fac"],gate.inputs[1])
    # radial falloff from the core so fissures cluster round the wound and fade out
    sub=nt.nodes.new("ShaderNodeVectorMath"); sub.operation='SUBTRACT'; nt.links.new(tc.outputs["Object"],sub.inputs[0]); sub.inputs[1].default_value=crack_center
    ln=nt.nodes.new("ShaderNodeVectorMath"); ln.operation='LENGTH'; nt.links.new(sub.outputs[0],ln.inputs[0])
    fall=nt.nodes.new("ShaderNodeMapRange"); fall.inputs["From Min"].default_value=crack_radius*0.35; fall.inputs["From Max"].default_value=crack_radius; fall.inputs["To Min"].default_value=1.0; fall.inputs["To Max"].default_value=0.0; nt.links.new(ln.outputs["Value"],fall.inputs["Value"])
    gate2=nt.nodes.new("ShaderNodeMath"); gate2.operation='MULTIPLY'; nt.links.new(gate.outputs[0],gate2.inputs[0]); nt.links.new(fall.outputs[0],gate2.inputs[1])
    strength=nt.nodes.new("ShaderNodeMath"); strength.operation='MULTIPLY'; nt.links.new(gate2.outputs[0],strength.inputs[0]); strength.inputs[1].default_value=crack_str
    p.inputs["Emission Color"].default_value=(*crack,1); nt.links.new(strength.outputs[0],p.inputs["Emission Strength"])
    # bump
    bn=nt.nodes.new("ShaderNodeTexNoise"); bn.inputs["Scale"].default_value=14; bn.inputs["Detail"].default_value=8; bn.inputs["Roughness"].default_value=0.7; nt.links.new(tc.outputs["Object"],bn.inputs["Vector"])
    bnode=nt.nodes.new("ShaderNodeBump"); bnode.inputs["Strength"].default_value=bump; nt.links.new(bn.outputs["Fac"],bnode.inputs["Height"])
    nt.links.new(bnode.outputs["Normal"],p.inputs["Normal"])
    return m
def glow(name,rgb,strength):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    e=nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value=(*rgb,1); e.inputs["Strength"].default_value=strength
    o=nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs[0],o.inputs[0]); return m
def plain(name,rgb,rough=0.6,metal=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value=(*rgb,1); b.inputs["Roughness"].default_value=rough; b.inputs["Metallic"].default_value=metal; return m
def embers(n, center, spread, mats, rmin=0.03, rmax=0.06, seed=3):
    random.seed(seed); out=[]
    for i in range(n):
        p=(center[0]+random.uniform(-spread[0],spread[0]), center[1]+random.uniform(-spread[1],spread[1]), center[2]+random.uniform(-spread[2],spread[2]))
        bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(rmin,rmax),location=p,subdivisions=1); o=bpy.context.object
        o.data.materials.append(random.choice(mats)); out.append(o)
    return out
def ground_cracks(center, n=10, mat=None, seed=5, length=(3,9)):
    random.seed(seed)
    for i in range(n):
        a=random.uniform(0,math.tau); L=random.uniform(*length)
        x=center[0]+math.cos(a)*L/2; y=center[1]+math.sin(a)*L/2
        o=cube((x,y,0.02),(L,random.uniform(0.06,0.14),0.04),rot=(0,0,a)); o.data.materials.append(mat)
def studio(target_z, cam_loc, lens=45, fstop=3.2, sun=4.2, teal=1200, gold=900, fill=900):
    bpy.ops.mesh.primitive_plane_add(size=160); g=bpy.context.object; g.data.materials.append(plain("gnd",(0.028,0.032,0.038),0.55))
    w=bpy.data.worlds['World']; w.use_nodes=True
    w.node_tree.nodes["Background"].inputs[0].default_value=(0.012,0.015,0.026,1); w.node_tree.nodes["Background"].inputs[1].default_value=0.5
    bpy.ops.object.light_add(type='SUN',location=(6,-8,16)); s=bpy.context.object; s.data.energy=sun; s.data.angle=math.radians(4); s.rotation_euler=(math.radians(52),0,math.radians(30)); s.data.color=(1.0,0.93,0.82)
    bpy.ops.object.light_add(type='AREA',location=(-14,7,11)); a=bpy.context.object; a.data.energy=teal; a.data.size=12; a.data.color=(0.15,0.9,0.9)
    bpy.ops.object.light_add(type='AREA',location=(13,-5,4)); a2=bpy.context.object; a2.data.energy=gold; a2.data.size=8; a2.data.color=(1.0,0.72,0.3)
    bpy.ops.object.light_add(type='AREA',location=(4,-15,8)); f=bpy.context.object; f.data.energy=fill; f.data.size=8; f.data.color=(0.75,0.85,1.0)
    bpy.ops.object.empty_add(location=(0,0,target_z)); tgt=bpy.context.object
    bpy.ops.object.camera_add(location=cam_loc); cam=bpy.context.object; bpy.context.scene.camera=cam
    c=cam.constraints.new('TRACK_TO'); c.target=tgt; c.track_axis='TRACK_NEGATIVE_Z'; c.up_axis='UP_Y'
    cam.data.lens=lens; cam.data.dof.use_dof=True; cam.data.dof.focus_object=tgt; cam.data.dof.aperture_fstop=fstop
    sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.use_denoising=True
    sc.view_settings.view_transform='AgX'; sc.view_settings.look='AgX - Punchy'
    sc.use_nodes=True; nt=sc.node_tree
    for nd in list(nt.nodes):
        if nd.type=='GLARE': nt.nodes.remove(nd)
    rl=nt.nodes.get('Render Layers') or nt.nodes.new('CompositorNodeRLayers'); comp=nt.nodes.get('Composite') or nt.nodes.new('CompositorNodeComposite')
    gl=nt.nodes.new('CompositorNodeGlare'); gl.glare_type='FOG_GLOW'; gl.quality='HIGH'; gl.threshold=1.6; gl.size=7; gl.mix=-0.35
    nt.links.new(rl.outputs['Image'],gl.inputs['Image']); nt.links.new(gl.outputs['Image'],comp.inputs['Image'])
    return cam,tgt

def surface(name, base, dark, crack=(0.1,0.95,0.8), crack_str=3.0, crack_scale=0.5, crack_width=0.018, crack_center=(0,-2.5,6.5), crack_radius=5.0,
            moss=None, rough=0.9, metallic=0.0, bump=0.45, stripes=0.0, noise_scale=3.0, sheen=0.0):
    """general boss surface: colour noise, optional top-facing 'moss' (any colour), radial glowing cracks, bump, optional thread stripes, metal"""
    m=rock_material(name, base=base, dark=dark, moss=moss if moss else (0,0,0), crack=crack, crack_str=crack_str*0.45, moss_on=bool(moss), rough=rough, bump=bump,
                    crack_scale=crack_scale, crack_width=crack_width, crack_center=crack_center, crack_radius=crack_radius)
    nt=m.node_tree; p=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]
    p.inputs["Metallic"].default_value=metallic
    if sheen: p.inputs["Sheen Weight"].default_value=sheen
    for n in nt.nodes:
        if n.type=='TEX_NOISE' and abs(n.inputs["Scale"].default_value-3.0)<1e-6: n.inputs["Scale"].default_value=noise_scale
    if stripes>0:
        tc=[n for n in nt.nodes if n.type=='TEX_COORD'][0]
        wv=nt.nodes.new("ShaderNodeTexWave"); wv.wave_type='BANDS'; wv.inputs["Scale"].default_value=stripes; wv.inputs["Distortion"].default_value=2.5; wv.inputs["Detail"].default_value=3
        nt.links.new(tc.outputs["Object"],wv.inputs["Vector"])
        bnode=[n for n in nt.nodes if n.type=='BUMP'][0]
        b2=nt.nodes.new("ShaderNodeBump"); b2.inputs["Strength"].default_value=0.5; nt.links.new(wv.outputs["Fac"],b2.inputs["Height"])
        nt.links.new(bnode.outputs["Normal"],b2.inputs["Normal"]); nt.links.new(b2.outputs["Normal"],p.inputs["Normal"])
    return m
def glass(name, rgb=(0.02,0.0,0.05), rough=0.05):
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value=(*rgb,1); b.inputs["Roughness"].default_value=rough; b.inputs["Transmission Weight"].default_value=0.6; b.inputs["IOR"].default_value=1.5
    return m
def ring(loc,r,thick,mat,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(location=loc,major_radius=r,minor_radius=thick,rotation=rot,major_segments=48,minor_segments=10); o=bpy.context.object; o.data.materials.append(mat); return o
def cone(loc,r,h,mat,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cone_add(radius1=r,depth=h,location=loc,rotation=rot,vertices=16); o=bpy.context.object; o.data.materials.append(mat); return o

def seg(a,b,r):
    """cylinder running exactly from point a to point b"""
    import mathutils
    v=mathutils.Vector((b[0]-a[0],b[1]-a[1],b[2]-a[2])); L_=v.length
    o=cyl(((a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2),r,L_); o.rotation_euler=v.to_track_quat('Z','Y').to_euler(); return o
def limb(points, r_seg, r_joint=None, parts=None):
    """joint spheres + joint-to-joint segments: an unbreakable chain. Appends to parts if given; returns objs."""
    r_joint=r_joint or r_seg*1.25; out=[]
    for i,p in enumerate(points):
        out.append(sphere(p,r_joint if 0<i<len(points)-1 else r_joint*1.05))
        if i<len(points)-1: out.append(seg(p,points[i+1],r_seg))
    if parts is not None: parts.extend(out)
    return out
