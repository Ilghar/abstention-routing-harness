"""Adversarial contrast gate: every text colour in use, and the pixels of the exported boards."""
import os, pathlib, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
# ---- contrast gate: every text colour token in use + pixels sampled from the boards ----
# Stdlib only. WCAG 2.2 1.4.3: 4.5:1 normal text, 3:1 large (>=24px, or >=18.66px bold).
# Board sampling follows the method used in the design review: per text region, background =
# per-channel median, text = median of the 3% of pixels furthest in luminance from it.
# Guide lines / back struts are decorative (WCAG 1.4.3 does not apply) and are not sampled.
import base64, re, struct, zlib

def _lin(c):
    c /= 255; return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
_LUT = [_lin(float(i)) for i in range(256)]
def _lum_rgb(r, g, b): return .2126 * _LUT[r] + .7152 * _LUT[g] + .0722 * _LUT[b]
def _rgb(h):
    h = h.strip().lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def lum(h): return _lum_rgb(*_rgb(h))
def ratio(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True); return (x + .05) / (y + .05)
def _hex(c): return "#%02x%02x%02x" % tuple(int(round(v)) for v in c)

# -- CSS: resolve custom properties per theme, then list every rule that sets a text colour --
def style_of(html): return "".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
def _flat(css):  # drop @media wrappers, keep inner rules
    return re.sub(r"@media[^{]*\{((?:[^{}]*\{[^{}]*\})*)\s*\}", r"\1", css)
def _rules(css): return [(s.strip(), b) for s, b in re.findall(r"([^{}]+)\{([^{}]*)\}", _flat(css))]
def theme_vars(css):
    """{'light': {...}, 'dark': {...}} from the first rule defining --canvas (light) and the
    first one whose --canvas is the studio dark canvas #4a434c (dark)."""
    out = {}
    for sel, body in _rules(css):
        d = dict((k, v.strip()) for k, v in re.findall(r"--([\w-]+)\s*:\s*([^;]+)", body))
        if "canvas" not in d: continue
        mode = "dark" if d["canvas"].lower() == "#4a434c" else "light"
        out.setdefault(mode, d)
    return out
def resolve(val, vs, depth=0):
    val = val.strip()
    m = re.fullmatch(r"var\(--([\w-]+)\s*(?:,\s*([^)]+))?\)", val)
    if m and depth < 8:
        return resolve(vs[m.group(1)], vs, depth + 1) if m.group(1) in vs else (resolve(m.group(2), vs, depth + 1) if m.group(2) else None)
    return val.lower() if re.fullmatch(r"#[0-9a-fA-F]{6}", val) else None
def _px(v):
    m = re.match(r"\s*(?:clamp|max|min)?\(?\s*([\d.]+)(px|rem|em)", v)
    return float(m.group(1)) * (1 if m.group(2) == "px" else 16) if m else None
def text_rules(css):
    """(selector, colour value, own background value or None, large?) for every rule setting color."""
    out = []
    for sel, body in _rules(css):
        decl = dict((k.strip(), v.strip()) for k, v in re.findall(r"(?<![-\w])([a-z-]+)\s*:\s*([^;]+)", body))
        col = decl.get("color")
        if not col or col in ("inherit", "currentColor", "transparent"): continue
        bg = decl.get("background-color") or decl.get("background")
        size = _px(decl.get("font-size", "")); bold = decl.get("font-weight", "400") in ("700", "800", "900", "bold")
        large = bool(size and (size >= 24 or (bold and size >= 18.66))) or re.search(r"(^|[\s,])h1\b", sel) is not None
        out.append((sel, col, bg, large))
    return out
def text_failures(css, page_bgs=("canvas", "surface")):
    """Every text colour in use, both themes, against its own background or every page background."""
    vs, bad, seen = theme_vars(css), [], []
    for mode, v in vs.items():
        for sel, col, bg, large in text_rules(css):
            fg = resolve(col, v)
            if fg is None: bad.append(f"{mode}: {sel}: colour {col!r} does not resolve to a token"); continue
            bgs = [resolve(bg, v)] if bg and resolve(bg, v) else [v[b] for b in page_bgs if b in v]
            for b in bgs:
                r, need = ratio(fg, b), (3.0 if large else 4.5); seen.append((mode, sel, fg, b, round(r, 2)))
                if r < need: bad.append(f"{mode}: {sel}: {fg} on {b} = {r:.2f} < {need}")
    return bad, seen

# -- PNG decoder (8-bit RGB/RGBA, non-interlaced), enough for exported boards --
def png_rows(data, upto):
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    i, idat = 8, []
    while i < len(data):
        n, typ = struct.unpack(">I4s", data[i:i + 8]); body = data[i + 8:i + 8 + n]; i += 12 + n
        if typ == b"IHDR": w, h, depth, ctype, _, _, inter = struct.unpack(">IIBBBBB", body)
        elif typ == b"IDAT": idat.append(body)
        elif typ == b"IEND": break
    assert depth == 8 and ctype in (2, 6) and inter == 0, "only 8-bit RGB/RGBA non-interlaced PNG"
    bpp = 3 if ctype == 2 else 4; stride = w * bpp
    raw = zlib.decompress(b"".join(idat)); prev = bytearray(stride); rows = []
    for y in range(min(h, upto)):
        f = raw[y * (stride + 1)]; cur = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        if f == 1:
            for x in range(bpp, stride): cur[x] = (cur[x] + cur[x - bpp]) & 255
        elif f == 2:
            cur = bytearray((a + b) & 255 for a, b in zip(cur, prev))
        elif f == 3:
            for x in range(stride): cur[x] = (cur[x] + (((cur[x - bpp] if x >= bpp else 0) + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(stride):
                a = cur[x - bpp] if x >= bpp else 0; b = prev[x]; c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                cur[x] = (cur[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(cur) if bpp == 3 else bytes(b for k, b in enumerate(cur) if k % 4 != 3)); prev = cur
    return w, h, rows

def board_image(svg_text):
    """(mime, bytes) of the raster embedded in a board SVG."""
    m = re.search(r'href="data:image/([\w+]+);base64,([^"]+)"', svg_text)
    if not m: return None, b""
    return m.group(1), base64.b64decode(m.group(2))

def sample(rows, box):
    """Contrast of the text in box: (fg hex, bg hex, ratio)."""
    x0, y0, x1, y1 = box; px = []
    for y in range(y0, y1):
        r = rows[y]; px.extend(zip(r[3 * x0:3 * x1:3], r[3 * x0 + 1:3 * x1:3], r[3 * x0 + 2:3 * x1:3]))
    med = lambda v: sorted(v)[len(v) // 2]
    bg = tuple(med([p[k] for p in px]) for k in range(3)); lb = _lum_rgb(*bg)
    d = sorted(((abs(_lum_rgb(*p) - lb), p) for p in px), key=lambda t: t[0])
    top = [p for _, p in d[int(len(d) * .97):]] or [d[-1][1]]
    fg = tuple(med([p[k] for p in top]) for k in range(3)); lf = _lum_rgb(*fg)
    return _hex(fg), _hex(bg), (max(lf, lb) + .05) / (min(lf, lb) + .05)

TEXT_INKS = ("#4a3a5c", "#f4eef3")  # plum (light) / ink (dark): the only board text colours
def board_failures(svg_text, regions, large=("title",)):
    """List of failures for one board; text regions only (guides are decorative)."""
    mime, data = board_image(svg_text)
    if mime != "png":
        return [f"board raster is {mime or 'missing'}: re-export as lossless PNG so text pixels can be verified"
                " (JPEG cannot be decoded with the standard library, and its ringing hides faint text)"]
    w, h, rows = png_rows(data, max(b[3] for b in regions.values()))
    bad = []
    for name, box in regions.items():
        fg, bg, r = sample(rows, box); need = 3.0 if name in large else 4.5
        grey = max(_rgb(fg)) - min(_rgb(fg)) < 12 and fg not in TEXT_INKS
        if r < need: bad.append(f"{name}: {fg} on {bg} = {r:.2f} < {need}" + (" (faint grey text)" if grey else ""))
        if min(max(abs(a - b) for a, b in zip(_rgb(fg), _rgb(t))) for t in TEXT_INKS) > 40:
            bad.append(f"{name}: text colour {fg} is not plum #4a3a5c / ink #f4eef3" + (" (grey)" if grey else ""))
    return bad

# Text regions on the 2400x1500 board layout (x0, y0, x1, y1). Guides, star outlines and back struts
# are decorative and deliberately not listed.
REGIONS = {'title': (117, 70, 656, 199),
    'ilghar.studio': (2086, 1406, 2285, 1465),
    'persian': (797, 105, 961, 199),
    'subtitle': (2004, 136, 2285, 188),
    'caption': (117, 1230, 516, 1270),
    'body': (1371, 820, 2250, 1160)}
PAGES = ['site/index.html', 'reports/index.html', 'reports/mock/index.html']

class TextTokenContrast(unittest.TestCase):
    def test_every_text_colour_in_use_meets_wcag(self):
        for page in PAGES:
            css = style_of((ROOT / page).read_text(encoding="utf-8"))
            self.assertEqual(sorted(theme_vars(css)), ["dark", "light"], page)
            bad, seen = text_failures(css)
            self.assertTrue(seen, f"{page}: no text colour rules found")
            self.assertEqual(bad, [], page)
    def test_gate_catches_faint_text(self):
        css = ".x{--canvas:#f3f1f6;--surface:#fffcfe;--ink:#4a3a5c;--muted:#a394ae}" \
              ".y{--canvas:#4a434c;--surface:#5a535c;--ink:#f4eef3;--muted:#7a688c}.cap{color:var(--muted)}"
        bad, _ = text_failures(css); self.assertEqual(len(bad), 4, bad)
        big = ".x{--canvas:#ffffff;--surface:#ffffff}.y{--canvas:#4a434c;--surface:#4a434c}h1{color:#949494}"
        self.assertEqual(text_failures(big)[0], [])  # 3.0:1 is enough for large text

class BoardPixels(unittest.TestCase):
    def check(self, svg_text, where):
        bad = board_failures(svg_text, REGIONS)
        self.assertEqual(bad, [], where)
    def test_committed_boards_text_is_legible(self):
        for t in ("light", "dark"):
            with self.subTest(theme=t):
                self.check((ROOT / f"assets/board-{t}.svg").read_text(encoding="utf-8"), f"assets/board-{t}.svg")
    @unittest.skipUnless(os.environ.get("BOARD_DIR"), "set BOARD_DIR to a folder of P01_board_<theme>.png renders")
    def test_rendered_board_pngs_text_is_legible(self):
        import base64
        for t in ("light", "dark"):
            p = pathlib.Path(os.environ["BOARD_DIR"]) / f"P01_board_{t}.png"
            svg = '<svg><image href="data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode() + '"/></svg>'
            with self.subTest(theme=t): self.check(svg, str(p))
    def test_sampler_flags_faint_grey(self):
        import base64
        w, h = 40, 20; rows = []
        for y in range(h):
            rows.append(b"\x00" + b"".join(b"\x99\x99\x99" if 15 <= x < 25 and 5 <= y < 15 else b"\xff\xff\xff" for x in range(w)))
        def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + \
              chunk(b"IDAT", zlib.compress(b"".join(rows))) + chunk(b"IEND", b"")
        svg = '<svg><image href="data:image/png;base64,' + base64.b64encode(png).decode() + '"/></svg>'
        bad = board_failures(svg, {"caption": (0, 0, w, h)})
        self.assertTrue(any("faint grey" in b for b in bad), bad)
        self.assertTrue(board_failures('<svg><image href="data:image/jpeg;base64,AAAA"/></svg>', {"x": (0, 0, 1, 1)}))

if __name__ == "__main__": unittest.main()
