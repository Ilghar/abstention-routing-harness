"""ilghar.studio light/dark theme for generated pages (case page, reports).

Base tokens are copied from the studio site (Ilghar/ilghar-studio src/styles.css, `:root` and `.dark`).
Two text-only tokens are added because the studio's --muted / --accent fall below WCAG AA (4.5:1)
for small text on --canvas: --muted-text and --accent-text. Decorative uses (borders, rules) keep the
studio values. tests/test_theme.py recomputes every contrast pair below for both themes.

Behaviour: no JS -> follows prefers-color-scheme. With JS a toggle button (aria-pressed) appears;
an explicit choice is stored in localStorage["ilg-theme"] and applied as data-theme on the scope.
"""
TOKENS = {
    "light": {"canvas": "#f3f1f6", "surface": "#fffcfe", "ink": "#4a3a5c", "muted": "#7a688c", "subtle": "#a394ae",
              "accent": "#c97a98", "accent-fg": "#fffafc", "line": "#e4dde8", "ring": "#c97a98",
              "muted-text": "#6a587c", "accent-text": "#9c4a6a", "figure-bg": "#fffcfe",
              "hit": "#e3efe2", "miss": "#f6e0de", "warn-bg": "#fbe3ea", "warn-ink": "#6e2440"},
    "dark": {"canvas": "#4a434c", "surface": "#5a535c", "ink": "#f4eef3", "muted": "#cbbdce", "subtle": "#9a8a9c",
             "accent": "#e8a8bc", "accent-fg": "#2c262f", "line": "#4a424c", "ring": "#e8a8bc",
             "muted-text": "#ddd2df", "accent-text": "#f6cdd9", "figure-bg": "#f3f1f6",
             "hit": "#35503c", "miss": "#6b3546", "warn-bg": "#6b3546", "warn-ink": "#fff3f7"},
}
SHADOWS = {
    "light": "--shadow-frame:inset 0 1px 0 rgba(255,255,255,.98),inset 0 -1px 0 rgba(74,58,92,.05),0 2px 3px rgba(74,58,92,.06),0 10px 18px rgba(74,58,92,.1),0 28px 44px -8px rgba(74,58,92,.22);"
             "--shadow-plate:0 1px 0 rgba(255,255,255,.7),0 6px 18px rgba(74,58,92,.1);",
    "dark": "--shadow-frame:inset 0 1px 0 rgba(255,255,255,.1),0 2px 4px rgba(0,0,0,.25),0 16px 32px -8px rgba(0,0,0,.45),0 32px 56px -16px rgba(0,0,0,.4);"
            "--shadow-plate:0 1px 0 rgba(255,255,255,.08),0 8px 20px rgba(0,0,0,.28);",
}
# (foreground, background, minimum ratio) checked in both themes
PAIRS = [("ink", "canvas", 4.5), ("ink", "surface", 4.5), ("muted-text", "canvas", 4.5), ("muted-text", "surface", 4.5),
         ("accent-text", "canvas", 4.5), ("accent-text", "surface", 4.5), ("ink", "hit", 4.5), ("ink", "miss", 4.5),
         ("warn-ink", "warn-bg", 4.5)]

def _lum(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]

def contrast(a, b):
    la, lb = _lum(a), _lum(b); return (max(la, lb) + .05) / (min(la, lb) + .05)

def _vars(mode):
    return "".join(f"--{k}:{v};" for k, v in TOKENS[mode].items()) + SHADOWS[mode] + f"color-scheme:{mode};"

def css(scope=".ilg-case"):
    s = scope
    return (f"{s}{{{_vars('light')}}}"
            f"@media (prefers-color-scheme:dark){{{s}:not([data-theme=light]){{{_vars('dark')}}}}}"
            f"{s}[data-theme=dark]{{{_vars('dark')}}}"
            f"{s}{{background:var(--canvas);color:var(--ink);min-height:100vh}}"
            f"{s} .ilg-theme-toggle{{position:fixed;top:1rem;inset-inline-end:1rem;z-index:10;font:inherit;font-size:.8rem;letter-spacing:.08em;"
            "text-transform:lowercase;color:var(--ink);background:var(--surface);border:1px solid var(--accent-text);border-radius:2rem;"
            "padding:.35rem .9rem;cursor:pointer;box-shadow:var(--shadow-plate)}"
            f"{s} .ilg-theme-toggle:focus-visible{{outline:2px solid var(--ring);outline-offset:2px}}"
            f"{s} .ilg-theme-toggle[hidden]{{display:none}}")

TOGGLE = '<button type="button" class="ilg-theme-toggle" aria-pressed="false" hidden>dark mode</button>'
# Inline, no network. Runs at end of body; without JS the button stays hidden and the system setting applies.
SCRIPT = ("<script>(function(){var r=document.querySelector('.ilg-case'),b=r&&r.querySelector('.ilg-theme-toggle');if(!b)return;"
          "var k='ilg-theme',m=window.matchMedia&&matchMedia('(prefers-color-scheme: dark)'),s=null;try{s=localStorage.getItem(k)}catch(e){}"
          "function dark(){var t=r.getAttribute('data-theme');return t?t==='dark':!!(m&&m.matches)}"
          "function sync(){b.setAttribute('aria-pressed',String(dark()))}"
          "if(s==='dark'||s==='light')r.setAttribute('data-theme',s);"
          "b.hidden=false;sync();if(m&&m.addEventListener)m.addEventListener('change',sync);"
          "b.addEventListener('click',function(){var n=dark()?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem(k,n)}catch(e){}sync()})})();</script>")
