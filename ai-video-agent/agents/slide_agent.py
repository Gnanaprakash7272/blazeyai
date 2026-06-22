import json
import os
from PIL import Image, ImageDraw, ImageFont

# Load scenes
with open("data/scenes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

os.makedirs("outputs/slides", exist_ok=True)

WIDTH  = 1280
HEIGHT = 720

# Colors
BG_COLOR       = (10, 15, 30)       # Deep navy
ACCENT         = (0, 210, 150)      # Blazly green
ACCENT_DARK    = (0, 140, 100)
TITLE_COLOR    = (255, 255, 255)
BULLET_COLOR   = (220, 230, 245)
BRAND_COLOR    = (0, 210, 150)
FOOTER_COLOR   = (120, 130, 150)
CARD_COLOR     = (20, 30, 55)
BULLET_DOT     = (0, 210, 150)

def get_font(size):
    for font_name in ["arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(font_name, size)
        except:
            continue
    return ImageFont.load_default()

def draw_rounded_rect(draw, xy, radius, fill):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.ellipse([x1, y1, x1 + 2*radius, y1 + 2*radius], fill=fill)
    draw.ellipse([x2 - 2*radius, y1, x2, y1 + 2*radius], fill=fill)
    draw.ellipse([x1, y2 - 2*radius, x1 + 2*radius, y2], fill=fill)
    draw.ellipse([x2 - 2*radius, y2 - 2*radius, x2, y2], fill=fill)

for scene in data["scenes"]:

    scene_no = scene["scene"]
    title    = scene["slide_title"]
    bullets  = scene["bullet_points"]

    img  = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --- Subtle gradient overlay (dark top to slightly lighter bottom) ---
    for y in range(HEIGHT):
        alpha = int(y / HEIGHT * 18)
        draw.line([(0, y), (WIDTH, y)], fill=(10 + alpha, 15 + alpha, 30 + alpha))

    # --- Left accent bar ---
    draw.rectangle([(0, 0), (6, HEIGHT)], fill=ACCENT)

    # --- Top accent glow strip ---
    for i in range(12):
        opacity = int(180 - i * 14)
        draw.rectangle([(6, i), (WIDTH, i + 1)],
                        fill=(0, 210, 150, opacity) if False else ACCENT if i == 0
                        else (0, max(0, 210 - i*16), max(0, 150 - i*11)))

    # --- Brand name top-left ---
    brand_font = get_font(18)
    draw.text((30, 22), "Blazly Academy", fill=BRAND_COLOR, font=brand_font)

    # --- Scene number top-right ---
    scene_font = get_font(18)
    scene_label = f"Scene {scene_no} / {len(data['scenes'])}"
    bbox = draw.textbbox((0, 0), scene_label, font=scene_font)
    draw.text((WIDTH - bbox[2] - 40, 22), scene_label, fill=FOOTER_COLOR, font=scene_font)

    # --- Separator line under header ---
    draw.rectangle([(30, 52), (WIDTH - 30, 54)], fill=(30, 45, 75))

    # --- Title ---
    title_font = get_font(40)
    # Wrap title if too long
    max_title_w = WIDTH - 80
    while True:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        if bbox[2] <= max_title_w or title_font.size <= 28:
            break
        title_font = get_font(title_font.size - 2)

    draw.text((36, 80), title, fill=TITLE_COLOR, font=title_font)

    # Accent underline under title
    title_bbox = draw.textbbox((36, 80), title, font=title_font)
    draw.rectangle([(36, title_bbox[3] + 8), (36 + min(300, title_bbox[2] - 36), title_bbox[3] + 12)],
                   fill=ACCENT)

    # --- Content card background ---
    card_top = title_bbox[3] + 30
    card_bottom = HEIGHT - 60
    draw_rounded_rect(draw, (30, card_top, WIDTH - 30, card_bottom), 12, CARD_COLOR)

    # --- Bullet points ---
    bullet_font  = get_font(26)
    small_font   = get_font(20)
    y = card_top + 28
    max_bullet_w = WIDTH - 160

    for i, bullet in enumerate(bullets):
        if y + 36 > card_bottom - 10:
            break

        # Dot
        dot_y = y + 10
        draw.ellipse([(50, dot_y), (62, dot_y + 12)], fill=BULLET_DOT)

        # Bullet text — wrap if too long
        words = bullet.split()
        lines = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            bbox = draw.textbbox((0, 0), test, font=bullet_font)
            if bbox[2] <= max_bullet_w:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        for line in lines[:2]:  # max 2 lines per bullet
            draw.text((78, y), line, fill=BULLET_COLOR, font=bullet_font)
            y += 34

        y += 14  # spacing between bullets

    # --- Footer ---
    footer_font = get_font(16)
    draw.rectangle([(0, HEIGHT - 42), (WIDTH, HEIGHT)], fill=(8, 12, 24))
    draw.rectangle([(0, HEIGHT - 43), (WIDTH, HEIGHT - 42)], fill=ACCENT_DARK)
    draw.text((36, HEIGHT - 28), "Powered by Blazly AI  •  Educational Video Generator",
              fill=FOOTER_COLOR, font=footer_font)

    img.save(f"outputs/slides/slide_{scene_no}.png")
    print(f"✅ slide_{scene_no}.png created")

print("🎉 All slides generated")