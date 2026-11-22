#!/usr/bin/env python3
"""Draw the 22 November 2026 world-news front page, 1024x1024 PNG.

Deterministic: fixed date string, no wall-clock time, no randomness,
no network. Run: python3 draw_news22.py [output_path]  (default entry.png)
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (26, 26, 26)
RED = (176, 42, 32)
GREY = (110, 104, 92)
LIGHT = (238, 232, 219)
PANEL = (252, 250, 244)

FONT_DIR = "/usr/share/fonts/truetype/noto/"
SERIF_BLACK = FONT_DIR + "NotoSerif-Black.ttf"
SERIF_BOLD = FONT_DIR + "NotoSerif-Bold.ttf"
SERIF_REG = FONT_DIR + "NotoSerif-Regular.ttf"
SANS_BOLD = FONT_DIR + "NotoSans-Bold.ttf"
SANS_REG = FONT_DIR + "NotoSans-Regular.ttf"
SANS_BLACK = FONT_DIR + "NotoSans-Black.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by measured pixel width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None):
    lines = wrap(draw, text, fnt, max_w)
    lh = leading or int(fnt.size * 1.28)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def kicker(draw, x, y, text, color=RED):
    f = font(SANS_BLACK, 17)
    draw.text((x, y), text, font=f, fill=color)
    return y + 24


def panel(draw, x, y, w, h, kicker_text, headline, body, pictogram=None,
          head_size=25, body_size=18, head_reduce=0):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=6,
                           outline=(200, 192, 176), width=2, fill=PANEL)
    px, py = x + 16, y + 14
    py = kicker(draw, px, py, kicker_text)
    py = draw_wrapped(draw, px, py, headline, font(SERIF_BOLD, head_size),
                      w - 32 - head_reduce, leading=head_size + 5)
    py += 6
    draw_wrapped(draw, px, py, body, font(SANS_REG, body_size),
                 w - 32, leading=body_size + 5)
    if pictogram:
        pictogram(draw, x, y, w, h)


# --- pictograms (simple geometry, drawn inside panel corners) ---
def pic_bahrain(draw, x, y, w, h):
    # Night sky over Manama: missile trails, a radar dish, city skyline.
    bx, by = x, y
    draw.rectangle([bx, by, bx + w, by + h], fill=(38, 44, 66))
    # stars (right side only; label sits top-left)
    for sx, sy in ((190, 12), (240, 26), (160, 44), (220, 52)):
        draw.ellipse([bx + sx, by + sy, bx + sx + 3, by + sy + 3],
                     fill=(255, 255, 255))
    draw.text((bx + 10, by + 10), "MANAMA  ·  BAHRAIN",
              font=font(SANS_BOLD, 15), fill=(200, 200, 200))
    # missile trails: dotted arcs
    for sx, sy in ((30, 44), (120, 30), (200, 40)):
        for k in range(5):
            draw.ellipse([bx + sx + k * 12, by + sy + k * 4,
                          bx + sx + k * 12 + 5, by + sy + k * 4 + 5],
                         fill=(255, 120, 80))
    # radar dish on a rooftop
    rx, ry = bx + w - 62, by + 78
    draw.line([(rx, ry), (rx - 6, ry + 34)], fill=(200, 200, 200), width=4)
    draw.arc([rx - 26, ry - 26, rx + 26, ry + 26], start=200, end=340,
             fill=(220, 220, 220), width=4)
    # city skyline
    for sx, sw, sh in ((0, 44, 52), (48, 30, 72), (82, 52, 44),
                       (140, 34, 64), (178, 40, 50)):
        draw.rectangle([bx + sx, by + h - sh, bx + sx + sw, by + h],
                       fill=(20, 24, 38))
        for wy in range(by + h - sh + 8, by + h - 6, 12):
            draw.rectangle([bx + sx + 6, wy, bx + sx + 12, wy + 5],
                           fill=(255, 210, 90))


def pic_arrest(draw, x, y, w, h):
    # Sheriff star over prison bars.
    cx, cy = x + w - 44, y + 46
    pts = []
    import math
    for i in range(10):
        r = 30 if i % 2 == 0 else 13
        a = math.pi * i / 5 - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=(176, 42, 32))
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 210, 90))
    for bx in range(x + w - 96, x + w - 8, 12):
        draw.line([(bx, y + h - 52), (bx, y + h - 8)], fill=(90, 90, 90),
                  width=4)


def pic_cop(draw, x, y, w, h):
    # Globe with a leaf.
    cx, cy = x + w - 44, y + 56
    draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=(40, 120, 60),
                 width=4)
    draw.ellipse([cx - 12, cy - 28, cx + 12, cy + 28], outline=(40, 120, 60),
                 width=3)
    draw.line([(cx - 28, cy), (cx + 28, cy)], fill=(40, 120, 60), width=3)
    draw.line([(cx - 24, cy - 16), (cx + 24, cy - 16)], fill=(40, 120, 60),
              width=2)
    draw.line([(cx - 24, cy + 16), (cx + 24, cy + 16)], fill=(40, 120, 60),
              width=2)
    draw.polygon([(cx + 18, cy - 34), (cx + 40, cy - 44), (cx + 34, cy - 20)],
                 fill=(40, 120, 60))


def pic_tennis(draw, x, y, w, h):
    # Tennis ball with curved seams.
    cx, cy = x + w - 44, y + 56
    draw.ellipse([cx - 26, cy - 26, cx + 26, cy + 26],
                 fill=(190, 210, 60), outline=(120, 140, 40), width=3)
    draw.arc([cx - 40, cy - 26, cx + 6, cy + 26], start=270, end=90,
             fill=(255, 255, 255), width=4)
    draw.arc([cx - 6, cy - 26, cx + 40, cy + 26], start=90, end=270,
             fill=(255, 255, 255), width=4)


def pic_ebola(draw, x, y, w, h):
    # Medical cross inside a shield outline.
    cx, cy = x + w - 44, y + 56
    draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=RED, width=4)
    draw.rectangle([cx - 7, cy - 18, cx + 7, cy + 18], fill=RED)
    draw.rectangle([cx - 18, cy - 7, cx + 18, cy + 7], fill=RED)


def pic_quake(draw, x, y, w, h):
    # Seismograph zigzag.
    bx, by = x + w - 96, y + 44
    pts = [(bx, by + 20), (bx + 12, by + 20), (bx + 18, by + 6),
           (bx + 26, by + 34), (bx + 34, by + 2), (bx + 42, by + 38),
           (bx + 50, by + 12), (bx + 58, by + 26), (bx + 66, by + 20),
           (bx + 88, by + 20)]
    draw.line(pts, fill=(176, 42, 32), width=4, joint="curve")
    draw.line([(bx - 6, by + 20), (bx + 94, by + 20)], fill=GREY, width=2)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 36  # margin
    CW = W - 2 * M  # content width

    # Masthead
    d.text((W // 2, 34), "THE WORLD IN ONE IMAGE",
           font=font(SERIF_BLACK, 58), fill=INK, anchor="ma")
    d.line([(M, 112), (W - M, 112)], fill=RED, width=4)
    d.text((W // 2, 124), "S U N D A Y   2 2   N O V E M B E R   2 0 2 6",
           font=font(SANS_BOLD, 20), fill=RED, anchor="ma")

    # Lead story
    ly, lh = 162, 244
    d.rounded_rectangle([M, ly, W - M, ly + lh], radius=6,
                        outline=(200, 192, 176), width=2, fill=PANEL)
    lx, lw = M + 18, 600
    py = kicker(d, lx, ly + 14, "LEAD STORY")
    py = draw_wrapped(d, lx, py, "IRAN STRIKES US BASES IN BAHRAIN",
                      font(SERIF_BLACK, 40), lw, leading=46)
    py += 8
    draw_wrapped(d, lx, py,
                 "Iran fires missiles and drones at US bases in Bahrain "
                 "overnight; its Revolutionary Guard claims two Patriot "
                 "radars destroyed. Bahrain says an industrial site caught "
                 "fire and no one was hurt.",
                 font(SANS_REG, 19), lw, leading=26)
    pic_bahrain(d, W - M - 18 - 284, ly + 40, 284, 146)

    # Row 2: two panels
    y2, h2 = 422, 194
    pw2 = (CW - 16) // 2
    panel(d, M, y2, pw2, h2, "EL CHAPO ISIDRO CAUGHT",
          "Mexico captures FBI top-10 fugitive",
          "Troops seize Fausto Isidro Meza Flores in Sinaloa on Friday "
          "night; cartel gunmen answer with burning roadblocks across "
          "the city.",
          pic_arrest, head_size=24, body_size=17, head_reduce=76)
    panel(d, M + pw2 + 16, y2, pw2, h2, "COP31 IN OVERTIME",
          "Climate talks drag into Sunday",
          "Nearly 200 nations remain split over fossil fuels and finance "
          "in Antalya; the EU warns it is a good deal or no deal at all.",
          pic_cop, head_size=24, body_size=17, head_reduce=76)

    # Row 3: three panels
    y3, h3 = 632, 224
    pw3 = (CW - 32) // 3
    panel(d, M, y3, pw3, h3, "ATP FINALS TODAY",
          "Zverev v Alcaraz for the title",
          "The top two seeds meet in Turin at 6pm; Alcaraz rallied past "
          "Shelton, Zverev beat Medvedev in Saturday's semis.",
          pic_tennis, head_size=24, body_size=17, head_reduce=76)
    panel(d, M + pw3 + 16, y3, pw3, h3, "EBOLA EMERGENCY",
          "WHO keeps Ebola emergency",
          "The DR Congo outbreak has reached 11,613 cases and 5,678 "
          "deaths; Kenya counts down to Ebola-free.",
          pic_ebola, head_size=24, body_size=17, head_reduce=76)
    panel(d, M + 2 * (pw3 + 16), y3, pw3, h3, "QUAKE IN MYANMAR",
          "Magnitude 4.1 shakes Myanmar",
          "An earthquake of magnitude 4.1 strikes Myanmar in the early "
          "hours of Sunday.",
          pic_quake, head_size=24, body_size=17, head_reduce=76)

    # ALSO strip
    ay, ah = 872, 88
    d.rounded_rectangle([M, ay, W - M, ay + ah], radius=6, fill=LIGHT,
                        outline=(200, 192, 176), width=2)
    d.text((M + 16, ay + 12), "ALSO:", font=font(SANS_BLACK, 19), fill=RED)
    draw_wrapped(d, M + 16, ay + 38,
                 "Teen gamer helps the FBI rescue a kidnapped girl · UN "
                 "talks on autonomous weapons end without a deal · "
                 "Princess of Wales documentary leads the Sunday papers",
                 font(SANS_REG, 19), CW - 32, leading=26)

    # Footer
    d.line([(M, 974), (W - M, 974)], fill=(200, 192, 176), width=2)
    d.text((W // 2, 984), "Summarised from multiple news reports · 22 November 2026",
           font=font(SERIF_REG, 17), fill=GREY, anchor="ma")

    img.save(out, "PNG", optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
