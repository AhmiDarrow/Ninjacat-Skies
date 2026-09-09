"""Reference reader + software renderer for .ncgb files (validates the format and the skinning math).
usage: python3 ncgb_view.py <file.ncgb> <clip> <frame> <out.png>"""
import struct, sys, math
from PIL import Image, ImageDraw

def read(path):
    d = open(path, 'rb').read(); o = 0
    def u(fmt):
        nonlocal o; v = struct.unpack_from('<'+fmt, d, o); o += struct.calcsize('<'+fmt); return v
    def s():
        nonlocal o; (n,) = u('H'); v = d[o:o+n].decode(); o += n; return v
    assert d[:4] == b'NCGB'; o = 4; (ver,) = u('I')
    (nb,) = u('I'); bones = [(s(), u('i')[0]) for _ in range(nb)]
    (np_,) = u('I'); parts = []
    for _ in range(np_):
        name = s(); (tex, nv) = u('BI'); verts = []
        for _ in range(nv):
            p = u('3f'); n = u('3f'); uv = u('2f'); c = u('3B'); e = u('3B'); bi = u('4H'); w = u('4f'); verts.append((p, n, c, e, bi, w, uv))
        (nt,) = u('I'); tris = [u('3I') for _ in range(nt)]; parts.append((name, verts, tris, tex))
    (nc,) = u('I'); clips = {}
    for _ in range(nc):
        name = s(); fps, nf = u('fI'); frames = [[u('12f') for _ in range(nb)] for _ in range(nf)]; clips[name] = (fps, frames)
    height, width = u('2f')
    return dict(bones=bones, parts=parts, clips=clips, height=height, width=width, path=path)

def xf(M, p):
    return (M[0]*p[0]+M[1]*p[1]+M[2]*p[2]+M[3], M[4]*p[0]+M[5]*p[1]+M[6]*p[2]+M[7], M[8]*p[0]+M[9]*p[1]+M[10]*p[2]+M[11])
def xfn(M, n):
    return (M[0]*n[0]+M[1]*n[1]+M[2]*n[2], M[4]*n[0]+M[5]*n[1]+M[6]*n[2], M[8]*n[0]+M[9]*n[1]+M[10]*n[2])

def render(m, clip, frame, out, size=(520, 640)):
    fps, frames = m['clips'][clip]; F = frames[frame % len(frames)]
    tris = []
    light = (0.4, 0.8, -0.45); ll = math.sqrt(sum(v*v for v in light)); light = tuple(v/ll for v in light)
    import os
    base = os.path.splitext(m['path'])[0]
    alb = Image.open(base+'.png').convert('RGB') if os.path.exists(base+'.png') else None
    emi = Image.open(base+'_emit.png').convert('RGB') if os.path.exists(base+'_emit.png') else None
    for name, verts, tl, tex in m['parts']:
        sk = []
        for p, n, c, e, bi, w, uv in verts:
            if tex and alb:
                px = (int(uv[0]*(alb.width-1)) % alb.width, int(uv[1]*(alb.height-1)) % alb.height)
                c = alb.getpixel(px); e = emi.getpixel(px) if emi else (0, 0, 0)
            P = [0, 0, 0]; N = [0, 0, 0]
            for k in range(4):
                if w[k] <= 0: continue
                q = xf(F[bi[k]], p); qn = xfn(F[bi[k]], n)
                for i in range(3): P[i] += w[k]*q[i]; N[i] += w[k]*qn[i]
            sk.append((P, N, c, e))
        for a, b, c_ in tl:
            (pa, na, ca, ea), (pb, nb, cb, eb), (pc, nc, cc, ec) = sk[a], sk[b], sk[c_]
            tris.append((pa, pb, pc, na, ca, ea))
    # camera: look from +x,+z diagonal, y up. rotate 35deg about Y then tilt
    def cam(p):
        x, y, z = p; a = math.radians(-35); x2 = x*math.cos(a)-z*math.sin(a); z2 = x*math.sin(a)+z*math.cos(a)
        t = math.radians(18); y2 = y*math.cos(t)-z2*math.sin(t); z3 = y*math.sin(t)+z2*math.cos(t)
        return x2, y2, z3
    H = m['height']; scale = (size[1]*0.85)/max(H, 1)
    im = Image.new('RGB', size, (14, 16, 24)); dr = ImageDraw.Draw(im)
    proj = []
    for pa, pb, pc, n, c, e in tris:
        ca, cb, cc = cam(pa), cam(pb), cam(pc); depth = (ca[2]+cb[2]+cc[2])/3
        nn = cam(n); shade = max(0.25, abs(nn[0]*light[0]+nn[1]*light[1]+nn[2]*light[2]))
        col = tuple(min(255, int(c[i]*shade + e[i]*1.2)) for i in range(3))
        pts = [(size[0]/2 + q[0]*scale, size[1]*0.92 - q[1]*scale) for q in (ca, cb, cc)]
        proj.append((depth, pts, col))
    proj.sort(key=lambda t: t[0])
    for _, pts, col in proj: dr.polygon(pts, fill=col)
    im.save(out)

if __name__ == '__main__':
    m = read(sys.argv[1]); print('bones', len(m['bones']), 'parts', len(m['parts']), 'clips', {k: len(v[1]) for k, v in m['clips'].items()}, 'h', m['height'])
    render(m, sys.argv[2], int(sys.argv[3]), sys.argv[4])
