"""Render a slowly spinning flat 'vector' earth as PNG frames (pure Python + Pillow)."""
import math, sys, os
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from geo import LAND, WATER

MW, MH = 1440, 720  # equirectangular land mask
def land_mask():
    m = Image.new("L", (MW, MH), 0); d = ImageDraw.Draw(m)
    xy = lambda pts: [((lon + 180) / 360 * MW, (90 - lat) / 180 * MH) for lon, lat in pts]
    for p in LAND.values(): d.polygon(xy(p), fill=255)
    for p in WATER.values(): d.polygon(xy(p), fill=0)
    return m
MASK = land_mask(); MB = MASK.tobytes()
def is_land(lat, lon):
    x = int((lon + 180) % 360 / 360 * MW) % MW; y = min(MH - 1, max(0, int((90 - lat) / 180 * MH)))
    return MB[y * MW + x] > 127

TILT = math.radians(23.4)   # axis tilted toward the viewer's upper right
VIEW_LAT = math.radians(12) # look slightly from above the equator

def body_coords(px, py):
    """Screen unit-disc point -> (lat, lon) on the globe at rotation 0, or None."""
    z2 = 1 - px * px - py * py
    if z2 <= 0: return None
    x, y, z = px, -py, math.sqrt(z2)
    # undo axial tilt (rotate around view axis)
    c, s = math.cos(-TILT), math.sin(-TILT); x, y = c * x - s * y, s * x + c * y
    # undo view latitude (rotate around x)
    c, s = math.cos(VIEW_LAT), math.sin(VIEW_LAT); y, z = c * y + s * z, -s * y + c * z
    return math.degrees(math.asin(max(-1, min(1, y)))), math.degrees(math.atan2(x, z))

def to_screen(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    x, y, z = math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo)
    c, s = math.cos(VIEW_LAT), math.sin(VIEW_LAT); y, z = c * y - s * z, s * y + c * z
    c, s = math.cos(TILT), math.sin(TILT); x, y = c * x - s * y, s * x + c * y
    return x, -y, z

def hexc(h, a=255): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (a,)

def render_solid(size, frames, out, ocean="#18293c", land="#e9eef3", grid="#ffffff", ss=2):
    S = size * ss; R = S / 2 - ss * 2
    cache = []
    for j in range(S):
        row = []
        for i in range(S):
            row.append(body_coords((i + .5 - S / 2) / R, (j + .5 - S / 2) / R))
        cache.append(row)
    oc, lc = hexc(ocean), hexc(land)
    for f in range(frames):
        rot = 360 * f / frames
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0)); px = img.load()
        for j in range(S):
            row = cache[j]
            for i in range(S):
                ll = row[i]
                if ll is None: continue
                px[i, j] = lc if is_land(ll[0], ll[1] - rot) else oc
        d = ImageDraw.Draw(img, "RGBA")
        g = hexc(grid, 22)
        for lat in range(-60, 61, 30): curve(d, [(lat, lo) for lo in range(-180, 181, 3)], rot, S, R, g, ss)
        for lon in range(0, 360, 30): curve(d, [(la, lon) for la in range(-90, 91, 3)], rot, S, R, g, ss)
        d.ellipse([S/2-R, S/2-R, S/2+R, S/2+R], outline=hexc("#ffffff", 70), width=ss)
        img.resize((size, size), Image.LANCZOS).save(f"{out}/earth-{f+1:04d}.png", optimize=True)

def curve(d, pts, rot, S, R, col, ss):
    seg = []
    for lat, lon in pts:
        x, y, z = to_screen(lat, lon + rot)
        if z > 0: seg.append((S/2 + x*R, S/2 + y*R))
        else:
            if len(seg) > 1: d.line(seg, fill=col, width=ss)
            seg = []
    if len(seg) > 1: d.line(seg, fill=col, width=ss)

def dot_grid(step=2.6):
    pts = []
    lat = -90 + step / 2
    while lat < 90:
        n = max(1, round(360 * math.cos(math.radians(lat)) / step))
        for k in range(n): pts.append((lat, -180 + 360 * (k + .5) / n))
        lat += step
    return pts

def render_dots(size, frames, out, ss=3, step=2.6):
    S = size * ss; R = S / 2 - ss * 2
    pts = [(la, lo, is_land(la, lo)) for la, lo in dot_grid(step)]
    rdot = R * math.radians(step) * 0.34
    for f in range(frames):
        rot = 360 * f / frames
        img = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(img, "RGBA")
        for la, lo, land in pts:
            x, y, z = to_screen(la, lo + rot)
            if z <= 0.02: continue
            cx, cy = S/2 + x*R, S/2 + y*R
            a = int((235 if land else 34) * (0.35 + 0.65 * z))
            r = rdot * (0.55 + 0.45 * z) * (1 if land else 0.7)
            d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255, 255, 255, a))
        img.resize((size, size), Image.LANCZOS).save(f"{out}/earth-{f+1:04d}.png", optimize=True)

if __name__ == "__main__":
    style, size, frames, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    os.makedirs(out, exist_ok=True)
    (render_solid if style == "solid" else render_dots)(size, frames, out)
