#!/usr/bin/env python3
"""The World in One Image - 22 November 2026.

Draws a deterministic 1024x1024 newspaper front page with PIL.
No external images, no network calls, no timestamps: the same run
always renders the same bytes. Run: python3 draw_news22.py
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 234)
PANEL = (253, 250, 242)
INK = (20, 20, 20)
GREY = (112, 106, 92)
RED = (163, 18, 18)
RED_DARK = (122, 10, 10)
NAVY = (29, 43, 69)
NAVY_DARK = (20, 31, 52)
GOLD = (232, 185, 80)
GREEN = (46, 125, 60)
BORDER = (201, 191, 168)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"

SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF_I = "DejaVuSerif-Italic.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def load(name, size):
    """Load a DejaVu font; fall back to the PIL default bitmap font."""
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


def wrap(text, font, max_w):
    """Greedy word wrap using pixel widths; returns a list of lines."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if font.getlength(trial) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, font, fill, leading):
    """Draw lines top to bottom; return the y just below the last line."""
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def draw_tracked(draw, text, font, cx, y, fill, tracking):
    """Draw text centred on cx with extra space between letters."""
    widths = [font.getlength(ch) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking


def hrule(draw, x1, x2, y, fill=INK, width=1):
    draw.line([(x1, y), (x2, y)], fill=fill, width=width)


def panel(draw, box, fill=PANEL, outline=BORDER, width=1, radius=10):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)


def star_points(cx, cy, r_outer, r_inner, points=5):
    """Vertices of a 5-pointed star, tip pointing up."""
    pts = []
    for i in range(points * 2):
        r = r_outer if i % 2 == 0 else r_inner
        ang = math.radians(-90 + i * 180 / points)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def icon_star(draw, cx, cy, r):
    draw.polygon(star_points(cx, cy, r, r * 0.45), fill=RED,
                 outline=RED_DARK)
    draw.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30],
                 fill=GOLD)


def icon_globe(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GREEN, width=3)
    draw.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
                 outline=GREEN, width=2)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=GREEN, width=2)
    draw.line([(cx + r * 0.55, cy - r * 0.85), (cx + r * 1.15, cy - r * 1.25)],
              fill=GREEN, width=3)
    draw.polygon([(cx + r * 1.15, cy - r * 1.25), (cx + r * 0.85, cy - r * 1.15),
                  (cx + r * 1.05, cy - r * 0.90)], fill=GREEN)


def icon_ball(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=(196, 214, 90), outline=(140, 160, 40), width=2)
    draw.arc([cx - r, cy - r * 0.55, cx + r * 0.25, cy + r * 0.55],
             270, 90, fill=(255, 255, 255), width=3)
    draw.arc([cx - r * 0.25, cy - r * 0.55, cx + r, cy + r * 0.55],
             90, 270, fill=(255, 255, 255), width=3)


def icon_cross(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED, width=3)
    t = r * 0.28
    draw.rectangle([cx - t, cy - r * 0.62, cx + t, cy + r * 0.62], fill=RED)
    draw.rectangle([cx - r * 0.62, cy - t, cx + r * 0.62, cy + t], fill=RED)


def icon_quake(draw, cx, cy, r):
    draw.line([(cx - r, cy), (cx + r, cy)], fill=GREY, width=2)
    pts = [(cx - r, cy), (cx - r * 0.60, cy - 2), (cx - r * 0.35, cy + 2),
           (cx - r * 0.15, cy - r * 0.70), (cx + r * 0.05, cy + r * 0.70),
           (cx + r * 0.25, cy - r * 0.40), (cx + r * 0.45, cy + 2),
           (cx + r, cy)]
    draw.line(pts, fill=RED, width=3, joint="curve")


def draw_night_panel(draw, box):
    """Manama at night: skyline, radar dish, dotted missile trails."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=NAVY)
    # stars
    for sx, sy in [(22, 14), (58, 30), (126, 12), (216, 22), (286, 10),
                   (306, 34), (166, 34), (252, 46)]:
        draw.ellipse([x0 + sx - 1.5, y0 + sy - 1.5,
                      x0 + sx + 1.5, y0 + sy + 1.5], fill=(255, 255, 255))
    # dotted missile trails rising rightwards
    for k, base in enumerate((0, 26)):
        for i in range(9):
            dx = 34 + i * 26
            dy = 96 - i * 7 - base
            draw.ellipse([x0 + dx - 2.5, y0 + dy - 2.5,
                          x0 + dx + 2.5, y0 + dy + 2.5],
                         fill=(255, 150, 60))
    # radar dish, right side
    rx, ry = x1 - 52, y1 - 58
    draw.arc([rx - 26, ry - 26, rx + 26, ry + 26], 200, 340,
             fill=(255, 255, 255), width=3)
    draw.line([(rx, ry), (rx - 12, y1 - 18)], fill=(255, 255, 255), width=3)
    draw.line([(rx - 22, y1 - 18), (rx + 2, y1 - 18)],
              fill=(255, 255, 255), width=3)
    # skyline silhouettes along the bottom, with lit windows
    base_y = y1
    buildings = [(0, 46, 62), (48, 34, 84), (84, 52, 48), (138, 30, 96),
                 (170, 58, 58), (230, 36, 78), (268, 52, 44)]
    for bx, bw, bh in buildings:
        draw.rectangle([x0 + bx, base_y - bh, x0 + bx + bw, base_y],
                       fill=NAVY_DARK)
        for wy in range(base_y - bh + 10, base_y - 8, 14):
            for wx in range(x0 + bx + 8, x0 + bx + bw - 6, 12):
                if (wx + wy) % 3 == 0:
                    draw.rectangle([wx, wy, wx + 4, wy + 6], fill=GOLD)


def story_panel(draw, box, kicker, headline, body, icon=None,
                head_size=26, body_size=17, body_max=3):
    """One news panel: red kicker, serif headline, serif body.

    The icon (if any) sits in the kicker row at top right; the headline
    is wrapped narrow enough to stay clear of it, and the body starts
    below the icon, so text and icon can never overlap.
    """
    x0, y0, x1, y1 = box
    panel(draw, box)
    pad = 16
    tx = x0 + pad
    tw = x1 - x0 - 2 * pad
    y = y0 + 12
    kfont = load(SANS_B, 15)
    if icon is not None and kfont.getlength(kicker) > tw - 48:
        kfont = load(SANS_B, 13)
    draw.text((tx, y), kicker, font=kfont, fill=RED)
    if icon is not None:
        icon(draw, x1 - pad - 19, y + 19, 19)
    y += 25
    hfont = load(SERIF_B, head_size)
    hw = tw - 48 if icon is not None else tw
    hlines = wrap(headline, hfont, hw)
    y = draw_lines(draw, hlines, tx, y, hfont, INK, head_size + 6)
    y += 6
    bfont = load(SERIF, body_size)
    blines = wrap(body, bfont, tw)[:body_max]
    draw_lines(draw, blines, tx, y, bfont, INK, body_size + 6)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # frame
    d.rectangle([12, 12, W - 13, H - 13], outline=INK, width=2)
    d.rectangle([18, 18, W - 19, H - 19], outline=BORDER, width=1)

    # masthead
    title = "THE WORLD IN ONE IMAGE"
    tf = load(SERIF_B, 54)
    d.text(((W - tf.getlength(title)) / 2, 30), title, font=tf, fill=INK)
    hrule(d, 36, W - 36, 102, fill=RED, width=3)
    draw_tracked(d, "SUNDAY, 22 NOVEMBER 2026", load(SANS_B, 18),
                 W / 2, 112, RED, 4)
    hrule(d, 36, W - 36, 142, fill=INK, width=4)
    hrule(d, 36, W - 36, 148, fill=INK, width=1)

    # lead story
    panel(d, (36, 162, 988, 458))
    kfont = load(SANS_B, 16)
    d.text((56, 178), "LEAD STORY \u00b7 MANAMA, BAHRAIN",
           font=kfont, fill=RED)
    hfont = load(SERIF_B, 42)
    hlines = wrap("IRAN STRIKES US BASES IN BAHRAIN", hfont, 560)
    draw_lines(d, hlines, 56, 204, hfont, INK, 50)
    bfont = load(SERIF, 20)
    lead_body = ("Iran's Revolutionary Guard says its missiles and drones "
                 "hit two US Patriot radars, at al-Riffa and Awali. "
                 "Bahrain says an industrial site caught fire and no one "
                 "was hurt.")
    blines = wrap(lead_body, bfont, 560)
    draw_lines(d, blines, 56, 314, bfont, INK, 28)
    draw_night_panel(d, (648, 178, 968, 392))
    cfont = load(SERIF_I, 13)
    d.text((648, 400), "The Manama skyline, after dark.",
           font=cfont, fill=GREY)

    # sub-stories, row one
    story_panel(d, (36, 474, 502, 658),
                "EL CHAPO ISIDRO CAUGHT",
                "Mexico captures FBI top-10 fugitive",
                "Troops seize Fausto Isidro Meza Flores in Sinaloa on "
                "Friday night; cartel gunmen answer with burning "
                "roadblocks across the city.",
                icon=icon_star, head_size=26, body_size=17)
    story_panel(d, (522, 474, 988, 658),
                "COP31 IN OVERTIME",
                "Climate talks drag into Sunday",
                "Nearly 200 nations remain split over fossil fuels and "
                "finance in Antalya; the EU warns it is a good deal or "
                "no deal at all.",
                icon=icon_globe, head_size=26, body_size=17)

    # sub-stories, row two
    story_panel(d, (36, 674, 340, 858),
                "ATP FINALS TODAY",
                "Zverev v Alcaraz for the title",
                "Top two seeds meet in Turin at 6pm. Alcaraz beat "
                "Shelton; Zverev beat Medvedev.",
                icon=icon_ball, head_size=22, body_size=16)
    story_panel(d, (360, 674, 664, 858),
                "EBOLA EMERGENCY STANDS",
                "WHO keeps Ebola emergency",
                "The DR Congo outbreak: 11,613 cases and 5,678 deaths. "
                "Kenya counts down to Ebola-free.",
                icon=icon_cross, head_size=22, body_size=16)
    story_panel(d, (684, 674, 988, 858),
                "QUAKE IN MYANMAR",
                "Magnitude 4.1 shakes Myanmar",
                "An earthquake of magnitude 4.1 strikes Myanmar in the "
                "early hours of Sunday.",
                icon=icon_quake, head_size=22, body_size=16)

    # also strip
    panel(d, (36, 874, 988, 950))
    afont = load(SANS_B, 17)
    d.text((56, 900), "ALSO:", font=afont, fill=RED)
    sfont = load(SERIF, 17)
    also = ("Teen gamer helps the FBI rescue a kidnapped girl \u00b7 "
            "UN talks on autonomous weapons end without a deal \u00b7 "
            "Princess of Wales documentary leads the Sunday papers")
    alines = wrap(also, sfont, 820)
    draw_lines(d, alines, 128, 894, sfont, INK, 24)

    # footer
    ffont = load(SERIF, 13)
    foot = "Summarised from multiple news reports \u00b7 22 November 2026"
    d.text(((W - ffont.getlength(foot)) / 2, 964), foot,
           font=ffont, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
