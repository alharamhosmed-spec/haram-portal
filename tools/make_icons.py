"""
مولّد أيقونات «نمط التطبيق» — بدون نصوص (تبقى واضحة في كل المقاسات)
الاستخدام:  python3 tools/make_icons.py [glyph] [مجلد-التطبيق]
glyph: cross (افتراضي) | box | shield | doc | wrench | user | drop | key | grid
"""
import sys, os
from PIL import Image, ImageDraw

NAVY = (15, 42, 63)
TEAL = (14, 124, 123)
WHITE = (255, 255, 255)

def gradient(n):
    img = Image.new('RGB', (n, n))
    px = img.load()
    for y in range(n):
        for x in range(n):
            t = (x + y) / (2 * (n - 1))
            px[x, y] = tuple(int(NAVY[i] + (TEAL[i] - NAVY[i]) * t) for i in range(3))
    return img

def glyph(d, kind, cx, cy, s, col):
    """يرسم رمزاً داخل مربع طول ضلعه s ومركزه (cx, cy)"""
    h = s / 2
    w = s * 0.13  # سماكة الخط
    if kind == 'cross':
        a = s * 0.17
        d.rectangle([cx - a, cy - h * 0.72, cx + a, cy + h * 0.72], fill=col)
        d.rectangle([cx - h * 0.72, cy - a, cx + h * 0.72, cy + a], fill=col)
    elif kind == 'box':
        d.rounded_rectangle([cx - h*.7, cy - h*.45, cx + h*.7, cy + h*.65], radius=s*.06, outline=col, width=int(w))
        d.line([cx - h*.7, cy - h*.05, cx + h*.7, cy - h*.05], fill=col, width=int(w))
        d.line([cx, cy - h*.45, cx, cy + h*.2], fill=col, width=int(w))
    elif kind == 'shield':
        d.polygon([(cx, cy - h*.8), (cx + h*.65, cy - h*.5), (cx + h*.55, cy + h*.25), (cx, cy + h*.8), (cx - h*.55, cy + h*.25), (cx - h*.65, cy - h*.5)], fill=col)
    elif kind == 'doc':
        d.rounded_rectangle([cx - h*.55, cy - h*.75, cx + h*.55, cy + h*.75], radius=s*.06, outline=col, width=int(w))
        for k in (-.3, 0, .3):
            d.line([cx - h*.3, cy + h*k, cx + h*.3, cy + h*k], fill=col, width=int(w*.7))
    elif kind == 'wrench':
        d.ellipse([cx - h*.7, cy - h*.7, cx - h*.05, cy - h*.05], outline=col, width=int(w))
        d.line([cx - h*.2, cy - h*.2, cx + h*.65, cy + h*.65], fill=col, width=int(w*1.3))
    elif kind == 'user':
        d.ellipse([cx - h*.35, cy - h*.8, cx + h*.35, cy - h*.1], fill=col)
        d.pieslice([cx - h*.75, cy + h*.0, cx + h*.75, cy + h*1.4], 180, 360, fill=col)
    elif kind == 'drop':
        # قطرة: دائرة + مثلث مماسّ لها تماماً (بدون درجات عند نقطة الالتقاء)
        import math
        r = h * .52; ccx, ccy = cx, cy + h * .23; top = cy - h * .82
        th = math.acos(r / (ccy - top))
        pts = [(cx, top)]
        for i in range(0, 41):
            a = th + (2 * math.pi - 2 * th) * i / 40  # من نقطة المماس اليمنى حول الأسفل إلى اليسرى
            pts.append((ccx + r * math.sin(a), ccy - r * math.cos(a)))
        d.polygon(pts, fill=col)
    elif kind == 'key':
        d.ellipse([cx - h*.75, cy - h*.35, cx - h*.05, cy + h*.35], outline=col, width=int(w))
        d.line([cx - h*.05, cy, cx + h*.75, cy], fill=col, width=int(w))
        d.line([cx + h*.5, cy, cx + h*.5, cy + h*.3], fill=col, width=int(w))
    elif kind == 'grid':
        g = h * .12
        for i in (-1, 1):
            for j in (-1, 1):
                x0 = cx + (g if i > 0 else -h*.7); y0 = cy + (g if j > 0 else -h*.7)
                d.rounded_rectangle([x0, y0, x0 + h*.58, y0 + h*.58], radius=s*.04, fill=col)

def icon(n, kind, maskable=False, transparent=False):
    k = 4  # رسم بدقة أعلى ثم تصغير (حواف ناعمة)
    N = n * k
    base = gradient(N) if not transparent else Image.new('RGB', (N, N), NAVY)
    img = base.convert('RGBA')
    d = ImageDraw.Draw(img)
    # المنطقة الآمنة للأيقونة القابلة للقص (maskable) = 80% من المساحة
    tile = N * (0.50 if maskable else 0.62)
    c = N / 2
    d.rounded_rectangle([c - tile/2, c - tile/2, c + tile/2, c + tile/2], radius=tile * 0.24, fill=WHITE)
    glyph(d, kind, c, c, tile * 0.78, TEAL + (255,))
    img = img.resize((n, n), Image.LANCZOS)
    if not maskable:
        # زوايا دائرية للأيقونة العادية
        m = Image.new('L', (N, N), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, N - 1, N - 1], radius=N * 0.22, fill=255)
        img.putalpha(m.resize((n, n), Image.LANCZOS))
    return img

def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else 'cross'
    # الوسيط الثاني (اختياري): مجلد التطبيق الفرعي، مثل: python3 tools/make_icons.py drop naqaa
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    out = os.path.join(root, sys.argv[2]) if len(sys.argv) > 2 else root
    os.makedirs(out, exist_ok=True)
    icon(192, kind).save(os.path.join(out, 'icon-192.png'))
    icon(512, kind).save(os.path.join(out, 'icon-512.png'))
    icon(512, kind, maskable=True).save(os.path.join(out, 'icon-maskable-512.png'))
    # آيفون لا يقبل الشفافية: خلفية كاملة
    icon(180, kind, maskable=True).convert('RGB').save(os.path.join(out, 'apple-touch-icon.png'))
    icon(32, kind).save(os.path.join(out, 'favicon-32.png'))
    print('icons ->', os.path.abspath(out))

if __name__ == '__main__':
    main()
