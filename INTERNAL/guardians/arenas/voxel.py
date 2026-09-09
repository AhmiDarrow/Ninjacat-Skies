"""Tiny voxel builder for Minecraft-style arena concepts: paint blocks into a dict, then emit one mesh per material
with only the exposed faces. Coordinates are block coordinates (ints); block (x,y,z) occupies [x,x+1)x[y,y+1)x[z,z+1)."""
import bpy, math, random

class Voxels:
    def __init__(self):
        self.b = {}          # (x,y,z) -> material key
        self.mats = {}       # key -> bpy material

    def mat(self, key, material): self.mats[key] = material; return key

    def set(self, x, y, z, key): self.b[(int(math.floor(x)), int(math.floor(y)), int(math.floor(z)))] = key
    def clear(self, x, y, z): self.b.pop((int(math.floor(x)), int(math.floor(y)), int(math.floor(z))), None)
    def get(self, x, y, z): return self.b.get((int(math.floor(x)), int(math.floor(y)), int(math.floor(z))))

    def column(self, x, y, z0, z1, key):
        for z in range(int(z0), int(z1)): self.set(x, y, z, key)

    def box(self, x0, y0, z0, x1, y1, z1, key, hollow=False):
        for x in range(int(x0), int(x1)):
            for y in range(int(y0), int(y1)):
                for z in range(int(z0), int(z1)):
                    if hollow and x0 < x < x1-1 and y0 < y < y1-1 and z0 < z < z1-1: continue
                    self.set(x, y, z, key)

    def disc(self, cx, cy, r, z0, z1, key, rin=0.0, jitter=0.0, rnd=None):
        """filled disc (or annulus with rin) of columns; jitter roughens the outer edge in blocks"""
        rnd = rnd or random.Random(1)
        R = int(r+jitter*2+1)
        # organic edge: a few random harmonics around the rim instead of per-column noise
        harm = [(rnd.randint(2, 7), rnd.uniform(0, 6.28), rnd.uniform(0.4, 1.0)) for _ in range(3)] if jitter else []
        for x in range(int(cx-R), int(cx+R)+1):
            for y in range(int(cy-R), int(cy+R)+1):
                px, py = x+0.5-cx, y+0.5-cy; d = math.hypot(px, py); a = math.atan2(py, px)
                ro = r + sum(jitter*w*math.sin(f*a+ph) for f, ph, w in harm)/max(1, len(harm)*0.7) + (rnd.uniform(-0.15, 0.15) if jitter else 0)
                if rin <= d <= ro: self.column(x, y, z0, z1, key)

    def hexagon(self, cx, cy, r, z0, z1, key):
        for x in range(int(cx-r-1), int(cx+r+2)):
            for y in range(int(cy-r-1), int(cy+r+2)):
                px, py = x+0.5-cx, y+0.5-cy
                if abs(px) <= r*0.866 and abs(py) <= r and abs(py) + abs(px)/math.sqrt(3) <= r: self.column(x, y, z0, z1, key)

    def line(self, x0, y0, x1, y1, z0, z1, key, width=1):
        n = int(max(abs(x1-x0), abs(y1-y0))*2)+1
        for i in range(n+1):
            t = i/n; x = x0+(x1-x0)*t; y = y0+(y1-y0)*t
            for dx in range(-(width//2), width-(width//2)):
                for dy in range(-(width//2), width-(width//2)):
                    self.column(x+dx, y+dy, z0, z1, key)

    def sphere(self, cx, cy, cz, r, key):
        for x in range(int(cx-r-1), int(cx+r+2)):
            for y in range(int(cy-r-1), int(cy+r+2)):
                for z in range(int(cz-r-1), int(cz+r+2)):
                    if math.dist((x+0.5, y+0.5, z+0.5), (cx, cy, cz)) <= r: self.set(x, y, z, key)

    def build(self, name="voxels"):
        by = {}
        for (x, y, z), k in self.b.items(): by.setdefault(k, []).append((x, y, z))
        objs = []
        FACES = [((1, 0, 0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]), ((-1, 0, 0), [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
                 ((0, 1, 0), [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]), ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
                 ((0, 0, 1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]), ((0, 0, -1), [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)])]
        for k, cells in by.items():
            verts = []; faces = []; idx = {}
            def vi(p):
                if p not in idx: idx[p] = len(verts); verts.append(p)
                return idx[p]
            for (x, y, z) in cells:
                for (nx, ny, nz), quad in FACES:
                    if (x+nx, y+ny, z+nz) in self.b: continue           # hidden face
                    faces.append([vi((x+q[0], y+q[1], z+q[2])) for q in quad])
            me = bpy.data.meshes.new(f"{name}_{k}"); me.from_pydata(verts, [], faces); me.update()
            o = bpy.data.objects.new(f"{name}_{k}", me); bpy.context.collection.objects.link(o); o.data.materials.append(self.mats[k]); objs.append(o)
        return objs
