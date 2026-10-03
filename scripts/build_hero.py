#!/usr/bin/env python3
"""Build the profile hero plates.

Four self-contained SVGs: wide and narrow, light and dark.
Motion is SMIL, which GitHub keeps inside an <img>. Every animated
element's plain attributes are the finished picture, so a renderer
that drops animation still shows the world.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"

LIGHT = {
    "bg": "#FBF8F4",
    "ink": "#1C1915",
    "muted": "#8C8378",
    "coral": "#E15A3A",
    "teal": "#0F6E56",
    "sky": "#E5F2EC",
    "hill_back": "#C9E0D6",
    "hill_mid": "#8FC4B0",
    "hill_front": "#157A62",
    "hill_deep": "#0C4E40",
    "gold": "#E0A322",
    "path": "#1C1915",
    "path_under": "#FFFDF8",
    "card": "#FFFCF8",
    "line": "#E3DAD0",
    "tick": "#C9BBA8",
    "stage": "#D5E6DE",
    "paper_stroke": "#E7DDD0",
    "node": "#FFFCF8",
}

DARK = {
    "bg": "#0D1117",
    "ink": "#F4EFE6",
    "muted": "#93A0AA",
    "coral": "#FF8B6A",
    "teal": "#6EE0B8",
    "sky": "#101A20",
    "hill_back": "#17362F",
    "hill_mid": "#1C5648",
    "hill_front": "#1B7A62",
    "hill_deep": "#0E3F34",
    "gold": "#F0C14A",
    "path": "#F4EFE6",
    "path_under": "#04140F",
    "card": "#172027",
    "line": "#24313A",
    "tick": "#3A4A55",
    "stage": "#24313A",
    "paper_stroke": "#2C3A44",
    "node": "#172027",
}

SERIF = "Georgia, 'Iowan Old Style', 'Palatino Linotype', Palatino, 'Noto Serif', 'Times New Roman', serif"


def once(attr, values, dur, keys=None, spline=None):
    extra = ""
    if keys:
        extra += f' keyTimes="{keys}"'
    if spline:
        extra += f' calcMode="spline" keySplines="{spline}"'
    return (
        f'<animate attributeName="{attr}" values="{values}" dur="{dur}" '
        f'fill="freeze"{extra}/>'
    )


def pulse(attr, values, dur, begin=None):
    b = f' begin="{begin}"' if begin else ""
    return (
        f'<animate attributeName="{attr}" values="{values}" dur="{dur}" '
        f'repeatCount="indefinite"{b}/>'
    )


def voice(x, y, scale, coral):
    """Concentric speech arcs. x,y is the dot center."""
    s = scale
    return f'''
    <g fill="none" stroke="{coral}" stroke-linecap="round">
      <circle cx="{x}" cy="{y}" r="{3.2 * s:.1f}" fill="{coral}" stroke="none"/>
      <path d="M{x + 8*s:.1f} {y - 8*s:.1f} a{12*s:.1f} {12*s:.1f} 0 0 1 0 {16*s:.1f}" stroke-width="{2.1 * s:.2f}">
        {pulse("opacity", "0.30;1;0.30", "2.6s")}
      </path>
      <path d="M{x + 14*s:.1f} {y - 15*s:.1f} a{20*s:.1f} {20*s:.1f} 0 0 1 0 {30*s:.1f}" stroke-width="{2.1 * s:.2f}" opacity="0.75">
        {pulse("opacity", "0.18;0.85;0.18", "2.6s", "0.28s")}
      </path>
      <path d="M{x + 20*s:.1f} {y - 22*s:.1f} a{28*s:.1f} {28*s:.1f} 0 0 1 0 {44*s:.1f}" stroke-width="{2.1 * s:.2f}" opacity="0.45">
        {pulse("opacity", "0.08;0.6;0.08", "2.6s", "0.56s")}
      </path>
    </g>'''


def diagram(x, y, w, h, p, area, curve, exit_xy):
    """A field card. Its curve leaves the card and becomes the path outside."""
    axis_x = x + 22
    axis_y = y + h - 26
    top = y + 18
    right = x + w - 28
    ex, ey = exit_xy
    return f'''
    <g>
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{p["card"]}" stroke="{p["paper_stroke"]}" stroke-width="1.5"/>
      <line x1="{axis_x}" y1="{top}" x2="{axis_x}" y2="{axis_y}" stroke="{p["tick"]}" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="{axis_x}" y1="{axis_y}" x2="{right}" y2="{axis_y}" stroke="{p["tick"]}" stroke-width="1.5" stroke-linecap="round"/>
      <path d="{area}" fill="{p["teal"]}" opacity="0.16"/>
      <path d="{curve}" fill="none" stroke="{p["ink"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"
            pathLength="100" stroke-dasharray="100" stroke-dashoffset="0">
        {once("stroke-dashoffset", "100;100;0", "3.4s", "0;0.42;1")}
      </path>
      <circle cx="{ex}" cy="{ey}" r="4.5" fill="{p["coral"]}"/>
    </g>'''


def nodes(p, spots):
    """Three marks on the path: a point, a system, a measure."""
    out = []
    # Staggered arrival, held by keyTimes. Base opacity is 1.
    windows = [
        ("0;0;1", "0;0.46;0.62"),
        ("0;0;1", "0;0.54;0.70"),
        ("0;0;1", "0;0.62;0.78"),
    ]
    for (cx, cy, kind), (values, keys) in zip(spots, windows):
        fade = once("opacity", values, "4.2s", keys)
        if kind == "point":
            body = f'''
            <circle cx="{cx}" cy="{cy}" r="12" fill="{p["node"]}" stroke="{p["coral"]}" stroke-width="2"/>
            <circle cx="{cx}" cy="{cy}" r="3.4" fill="{p["coral"]}"/>'''
        elif kind == "system":
            body = f'''
            <rect x="{cx-12}" y="{cy-12}" width="24" height="24" rx="6" fill="{p["node"]}" stroke="{p["ink"]}" stroke-width="2"/>
            <path d="M{cx-5} {cy-5} h3.2 v3.2 h-3.2 z M{cx+1.6} {cy-5} h3.2 v3.2 h-3.2 z M{cx-5} {cy+1.6} h3.2 v3.2 h-3.2 z M{cx+1.6} {cy+1.6} h3.2 v3.2 h-3.2 z" fill="{p["ink"]}"/>'''
        else:
            body = f'''
            <circle cx="{cx}" cy="{cy}" r="12" fill="{p["node"]}" stroke="{p["teal"]}" stroke-width="2"/>
            <path d="M{cx-5.5} {cy+4} v-4 M{cx-1.2} {cy+4} v-7 M{cx+3.2} {cy+4} v-10" stroke="{p["teal"]}" stroke-width="1.8" stroke-linecap="round"/>'''
        out.append(f'<g opacity="1">{body}{fade}</g>')
    return "\n".join(out)


def world(p, geom):
    g = geom
    stars = ""
    if g.get("stars"):
        bits = []
        for sx, sy, r in g["stars"]:
            bits.append(
                f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="{p["ink"]}" opacity="0.45">'
                f'{pulse("opacity", "0.15;0.7;0.15", f"{3.2 + r:.1f}s")}</circle>'
            )
        stars = "\n".join(bits)

    hills = "\n".join(
        f'<path d="{d}" fill="{p[key]}"/>' for d, key in g["hills"]
    )

    path = g["path"]
    length = g["path_length"]
    draw = once("stroke-dashoffset", f"{length};{length};0", "3.6s", "0;0.38;1")

    return f'''
    <g clip-path="url(#plate)">
      <rect x="{g["stage"][0]}" y="{g["stage"][1]}" width="{g["stage"][2]}" height="{g["stage"][3]}" fill="{p["sky"]}"/>
      {stars}
      <circle cx="{g["sun"][0]}" cy="{g["sun"][1]}" r="{g["sun"][2] + 16}" fill="none" stroke="{p["gold"]}" stroke-width="1.6" opacity="0.4">
        {pulse("opacity", "0.18;0.55;0.18", "5.2s")}
      </circle>
      <circle cx="{g["sun"][0]}" cy="{g["sun"][1]}" r="{g["sun"][2]}" fill="{p["gold"]}"/>
      <path d="{g["wave"]}" fill="none" stroke="{p["coral"]}" stroke-width="2.4" stroke-linecap="round" opacity="0.85">
        {pulse("opacity", "0.4;0.9;0.4", "3.8s")}
      </path>
      {hills}
      <path d="{path}" fill="none" stroke="{p["path_under"]}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" opacity="0.55"
            pathLength="{length}" stroke-dasharray="{length}" stroke-dashoffset="0">{draw}</path>
      <path d="{path}" fill="none" stroke="{p["path"]}" stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round"
            pathLength="{length}" stroke-dasharray="{length}" stroke-dashoffset="0">{draw}</path>
      {nodes(p, g["nodes"])}
      <g>
        <circle r="10" fill="none" stroke="{p["coral"]}" stroke-width="1.5" opacity="0.55"/>
        <circle r="4.5" fill="{p["coral"]}"/>
        <animateMotion dur="14s" repeatCount="indefinite" rotate="0" path="{path}"/>
      </g>
      {diagram(g["diagram"][0], g["diagram"][1], g["diagram"][2], g["diagram"][3], p, g["area"], g["curve"], g["exit"])}
    </g>'''


def plate_frame(g, p):
    x, y, w, h = g["stage"]
    return f'''
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{p["sky"]}" stroke="{p["stage"]}" stroke-width="1.75"/>
    <rect x="{x+10}" y="{y+10}" width="{w-20}" height="{h-20}" rx="12" fill="none" stroke="{p["stage"]}" stroke-width="1" opacity="0.85"/>'''


WIDE = {
    "view": (960, 560),
    "stage": (40, 168, 880, 360),
    "speak": (112, 68, 28),
    "line": (112, 134, 48),
    "voice": (46, 96, 0.92),
    "rule": (116, 80, 68),
    "sun": (812, 228, 26),
    "wave": "M72 246 q18 -16 36 0 t36 0 t36 0 t36 0 t36 0",
    "hills": [
        (
            "M50 400 C150 400 190 318 300 312 C410 306 460 372 560 382 "
            "C670 394 710 324 810 316 C880 310 910 352 910 372 L910 518 L50 518 Z",
            "hill_back",
        ),
        (
            "M50 448 C170 430 240 392 360 404 C490 418 540 468 660 456 "
            "C780 444 840 400 910 424 L910 518 L50 518 Z",
            "hill_mid",
        ),
        (
            "M50 492 C210 468 340 512 500 498 C660 484 760 452 910 478 L910 518 L50 518 Z",
            "hill_front",
        ),
    ],
    "path": "M284 408 C316 403 390 358 490 346 C580 336 640 398 712 406 C792 416 838 362 892 374",
    "path_length": 100,
    "nodes": [(490, 346, "point"), (712, 406, "system"), (852, 375, "measure")],
    "diagram": (64, 328, 220, 158),
    "area": "M98 450 C145 446 180 412 220 396 C248 384 260 412 284 408 L284 458 L98 458 Z",
    "curve": "M98 450 C145 446 180 412 220 396 C248 384 260 412 284 408",
    "exit": (284, 408),
    "stars": None,
}

# Stars only applied for dark, added in render().
DARK_STARS_WIDE = [
    (620, 230, 1.3), (688, 252, 1.1), (648, 286, 1.6),
    (860, 230, 1.2), (500, 240, 1.0), (560, 300, 1.4),
    (910, 300, 1.1), (430, 250, 1.2),
]

NARROW = {
    "view": (640, 760),
    "stage": (20, 196, 600, 532),
    "speak": (36, 58, 24),
    "line1": (36, 112, 40),
    "line2": (36, 164, 46),
    "voice": (560, 86, 0.78),
    "rule": (38, 176, 0),
    "sun": (520, 268, 28),
    "wave": "M44 268 q16 -16 32 0 t32 0 t32 0 t32 0",
    "hills": [
        (
            "M30 430 C120 430 150 360 240 352 C330 344 370 410 450 418 "
            "C520 426 555 368 610 380 L610 718 L30 718 Z",
            "hill_back",
        ),
        (
            "M30 500 C140 478 200 440 310 452 C430 466 480 520 610 490 L610 718 L30 718 Z",
            "hill_mid",
        ),
        (
            "M30 560 C160 540 260 590 400 572 C500 558 560 530 610 548 L610 718 L30 718 Z",
            "hill_front",
        ),
    ],
    "path": "M40 470 C110 456 150 408 230 400 C320 390 360 452 450 448 C520 444 560 408 604 420",
    "path_length": 100,
    "nodes": [(230, 400, "point"), (450, 448, "system"), (580, 412, "measure")],
    "diagram": (36, 548, 568, 156),
    "area": "M64 672 C140 668 200 624 280 608 C370 590 450 600 560 612 L560 672 L64 672 Z",
    "curve": "M64 672 C140 668 200 624 280 608 C370 590 450 600 560 612",
    "exit": (560, 612),
    "stars": None,
}

DARK_STARS_NARROW = [
    (80, 260, 1.2), (140, 300, 1.4), (360, 270, 1.1),
    (420, 310, 1.5), (560, 260, 1.1), (300, 340, 1.2),
    (200, 250, 1.0), (600, 340, 1.3),
]


def headline_wide(p, g):
    x, y, size = g["speak"]
    lx, ly, lsize = g["line"]
    rx, ry, rw = g["rule"]
    rule = ""
    if rw:
        rule = f'''
    <line x1="{rx}" y1="{ry}" x2="{rx + rw}" y2="{ry}" stroke="{p["coral"]}" stroke-width="2" stroke-linecap="round"
          pathLength="100" stroke-dasharray="100" stroke-dashoffset="0">
      {once("stroke-dashoffset", "100;0", "0.7s", spline="0.2 0.8 0.2 1")}
    </line>'''
    return f'''
    <text x="{x}" y="{y}" fill="{p["coral"]}" font-family="{SERIF}" font-style="italic" font-size="{size}" opacity="1">
      Speak,
      {once("opacity", "0;1", "0.55s")}
    </text>
    {rule}
    <g clip-path="url(#type)">
      <text x="{lx}" y="{ly}" font-family="{SERIF}" font-size="{lsize}">
        <tspan fill="{p["ink"]}">and a world </tspan><tspan fill="{p["teal"]}">appears.</tspan>
      </text>
    </g>'''


def headline_narrow(p, g):
    x, y, size = g["speak"]
    x1, y1, s1 = g["line1"]
    x2, y2, s2 = g["line2"]
    return f'''
    <text x="{x}" y="{y}" fill="{p["coral"]}" font-family="{SERIF}" font-style="italic" font-size="{size}" opacity="1">
      Speak,
      {once("opacity", "0;1", "0.5s")}
    </text>
    <g clip-path="url(#type)">
      <text x="{x1}" y="{y1}" fill="{p["ink"]}" font-family="{SERIF}" font-size="{s1}">and a world</text>
      <text x="{x2}" y="{y2}" fill="{p["teal"]}" font-family="{SERIF}" font-size="{s2}">appears.</text>
    </g>'''


def build(p, g, narrow=False):
    vw, vh = g["view"]
    sx, sy, sw, sh = g["stage"]
    # Clip matches the inner hairline so ellipses stay inside the plate.
    clip = (sx + 10, sy + 10, sw - 20, sh - 20)
    title = "Speak, and a world appears"
    desc = "A sentence resolves into a small landscape with a path, three marks, and a diagram."
    head = headline_narrow(p, g) if narrow else headline_wide(p, g)
    # Typing window. Base width is the full line so a static renderer shows the sentence.
    if narrow:
        clip_rect = f'<rect x="32" y="72" width="520" height="110">{once("width", "0;0;520", "2.15s", "0;0.12;1", "0.2 0.8 0.2 1;0.16 0.84 0.32 1")}</rect>'
    else:
        clip_rect = f'<rect x="108" y="86" width="640" height="72">{once("width", "0;640", "1.7s", spline="0.16 0.84 0.3 1")}</rect>'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{vw}" height="{vh}" viewBox="0 0 {vw} {vh}" role="img">
  <title>{title}</title>
  <desc>{desc}</desc>
  <rect width="{vw}" height="{vh}" fill="{p["bg"]}"/>
  <defs>
    <clipPath id="type">{clip_rect}</clipPath>
    <clipPath id="plate">
      <rect x="{clip[0]}" y="{clip[1]}" width="{clip[2]}" height="{clip[3]}" rx="12"/>
    </clipPath>
  </defs>
  {head}
  {voice(*g["voice"], p["coral"])}
  {plate_frame(g, p)}
  {world(p, g)}
</svg>
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wide_light = dict(WIDE)
    wide_dark = dict(WIDE)
    wide_dark["stars"] = DARK_STARS_WIDE
    narrow_light = dict(NARROW)
    narrow_dark = dict(NARROW)
    narrow_dark["stars"] = DARK_STARS_NARROW

    files = {
        "hero-light.svg": build(LIGHT, wide_light, narrow=False),
        "hero-dark.svg": build(DARK, wide_dark, narrow=False),
        "hero-light-narrow.svg": build(LIGHT, narrow_light, narrow=True),
        "hero-dark-narrow.svg": build(DARK, narrow_dark, narrow=True),
    }
    for name, text in files.items():
        path = OUT / name
        path.write_text(text.strip() + "\n", encoding="utf-8")
        print(f"{name:24} {path.stat().st_size:6} bytes")


if __name__ == "__main__":
    main()
