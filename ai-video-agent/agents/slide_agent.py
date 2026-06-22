import json
import os
from PIL import Image, ImageDraw, ImageFont

with open("data/scenes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

os.makedirs("outputs/slides", exist_ok=True)

# ── Canvas ──────────────────────────────────────────────────
W, H         = 1280, 720

# ── Layout zones ────────────────────────────────────────────
HEADER_H     = 62          # top header bar
FOOTER_H     = 90          # bottom subtitle bar
DIVIDER      = 2
CONTENT_TOP  = HEADER_H + DIVIDER
CONTENT_BOT  = H - FOOTER_H - DIVIDER

# Avatar reserved zone (bottom-right of content area)
AV_X1, AV_Y1 = 840, CONTENT_TOP + 160
AV_X2, AV_Y2 = 1240, CONTENT_BOT - 10
AV_W  = AV_X2 - AV_X1      # 400
AV_H  = AV_Y2 - AV_Y1      # varies

# ── Colours ─────────────────────────────────────────────────
BG          = (10, 14, 28)
HEADER_BG   = (14, 20, 42)
FOOTER_BG   = (8, 12, 22)
ACCENT      = (0, 210, 150)
ACCENT2     = (0, 160, 110)
CARD_BG     = (18, 26, 52)
DIV_COL     = (30, 42, 78)
WHITE       = (255, 255, 255)
LIGHT       = (210, 220, 240)
MUTED       = (110, 125, 155)
CHECK_COL   = (0, 210, 150)
AV_BORDER   = (0, 180, 130)
AV_BG       = (14, 22, 44)

TOTAL_SCENES = len(data["scenes"])

# ── Font helper ─────────────────────────────────────────────
def font(size, bold=False):
    candidates = (
        ["arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]
        if bold else
        ["arial.ttf", "DejaVuSans.ttf", "arialbd.ttf"]
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except:
            pass
    return ImageFont.load_default()

def wrap_text(draw, text, font_obj, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textbbox((0,0), test, font=font_obj)[2] <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ── Draw each scene slide ────────────────────────────────────
for scene in data["scenes"]:
    scene_no = scene["scene"]
    title    = scene["slide_title"]
    bullets  = scene["bullet_points"]

    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── Subtle bg gradient ───────────────────────────────────
    for y in range(H):
        v = int(y / H * 12)
        draw.line([(0,y),(W,y)], fill=(BG[0]+v, BG[1]+v, BG[2]+v))

    # ── Left accent glow strip ───────────────────────────────
    for i in range(5):
        draw.rectangle([(i, 0),(i+1, H)],
                        fill=(0, max(0,210-i*40), max(0,150-i*28)))

    # ════════════════════════════════════════════════════════
    # HEADER
    # ════════════════════════════════════════════════════════
    draw.rectangle([(0,0),(W, HEADER_H)], fill=HEADER_BG)

    # Left accent bar in header
    draw.rectangle([(0,0),(5, HEADER_H)], fill=ACCENT)

    # Brand
    bf = font(20, bold=True)
    draw.text((24, 20), "Blazly Academy", fill=ACCENT, font=bf)

    # Scene counter (right side)
    sf  = font(17)
    lbl = f"Scene  {scene_no}  /  {TOTAL_SCENES}"
    lw  = draw.textbbox((0,0), lbl, font=sf)[2]
    draw.text((W - lw - 28, 22), lbl, fill=MUTED, font=sf)

    # Header divider
    draw.rectangle([(0, HEADER_H),(W, HEADER_H+DIVIDER)], fill=ACCENT2)

    # ════════════════════════════════════════════════════════
    # CONTENT AREA
    # ════════════════════════════════════════════════════════
    # Left content zone (leave right side for avatar)
    LEFT_MAX_X = AV_X1 - 30   # ~810

    # Title
    tf = font(36, bold=True)
    # shrink if too wide
    while draw.textbbox((0,0), title, font=tf)[2] > LEFT_MAX_X - 36 and tf.size > 22:
        tf = font(tf.size - 2, bold=True)

    ty = CONTENT_TOP + 30
    draw.text((30, ty), title, fill=WHITE, font=tf)

    # Accent underline
    tw = draw.textbbox((30, ty), title, font=tf)[2]
    draw.rectangle([(30, ty + tf.size + 6),
                    (min(tw, 30 + 260), ty + tf.size + 10)], fill=ACCENT)

    # ── Bullets ──────────────────────────────────────────────
    bf2 = font(24)
    by  = ty + tf.size + 36
    MAX_BULLET_W = LEFT_MAX_X - 80

    for bullet in bullets:
        if by > CONTENT_BOT - 30:
            break

        lines = wrap_text(draw, bullet, bf2, MAX_BULLET_W)

        # Checkmark circle
        cx, cy = 40, by + 10
        draw.ellipse([(cx-12, cy-12),(cx+12, cy+12)], fill=ACCENT)
        draw.text((cx-7, cy-10), "✓", fill=(10,14,28), font=font(16, bold=True))

        for li, line in enumerate(lines[:2]):
            draw.text((64, by + li*30), line, fill=LIGHT, font=bf2)

        by += len(lines[:2]) * 30 + 22

    # ════════════════════════════════════════════════════════
    # AVATAR ZONE (bottom-right placeholder)
    # ════════════════════════════════════════════════════════
    # Card background
    draw.rounded_rectangle(
        [(AV_X1-4, AV_Y1-4),(AV_X2+4, AV_Y2+4)],
        radius=14, fill=CARD_BG
    )
    # Border
    draw.rounded_rectangle(
        [(AV_X1-4, AV_Y1-4),(AV_X2+4, AV_Y2+4)],
        radius=14, outline=AV_BORDER, width=2
    )
    # Inner fill (will be covered by avatar in video_agent)
    draw.rectangle([(AV_X1, AV_Y1),(AV_X2, AV_Y2)], fill=AV_BG)

    # "AI Tutor" label above avatar zone
    lt = font(15)
    ll = "AI Tutor"
    lw = draw.textbbox((0,0), ll, font=lt)[2]
    lx = AV_X1 + (AV_W - lw) // 2
    draw.text((lx, AV_Y1 - 28), ll, fill=ACCENT, font=lt)
    # small dot line
    draw.rectangle([(AV_X1, AV_Y1-14),(AV_X2, AV_Y1-12)], fill=DIV_COL)

    # ════════════════════════════════════════════════════════
    # CONTENT DIVIDER (above footer)
    # ════════════════════════════════════════════════════════
    draw.rectangle([(0, CONTENT_BOT),(W, CONTENT_BOT+DIVIDER)], fill=DIV_COL)

    # ════════════════════════════════════════════════════════
    # FOOTER
    # ════════════════════════════════════════════════════════
    draw.rectangle([(0, CONTENT_BOT+DIVIDER),(W, H)], fill=FOOTER_BG)

    # Quote icon
    qf = font(28, bold=True)
    draw.text((22, CONTENT_BOT + 14), "\u201c", fill=ACCENT, font=qf)

    # Narration text (will be replaced dynamically per scene in video)
    nf   = font(19)
    narr = scene.get("narration", "")
    nlines = wrap_text(draw, narr, nf, W - 80)
    ny = CONTENT_BOT + 16
    for nl in nlines[:2]:
        draw.text((46, ny), nl, fill=LIGHT, font=nf)
        ny += 26

    # Powered by (right side of footer)
    pf = font(14)
    pl = "Powered by Blazly AI"
    pw = draw.textbbox((0,0), pl, font=pf)[2]
    draw.text((W - pw - 20, H - 24), pl, fill=MUTED, font=pf)

    img.save(f"outputs/slides/slide_{scene_no}.png")
    print(f"✅ slide_{scene_no}.png created")

print("🎉 All slides generated")