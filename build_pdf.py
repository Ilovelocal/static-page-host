"""
Build Bridgeford-Marketing.pdf — 6-page brochure for The Bridgeford by Turtle Creek Homes
Fonts: Lora (headings) + Segoe UI (body)  |  Logo: TCLogo_edited_edited.png
"""
import os, io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE       = r"D:\downloads\TC Marketing\Bridgeford"
FONTS_DIR  = r"D:\downloads\TC Marketing\fonts"
WIN_FONTS  = r"C:\Windows\Fonts"
OUT        = os.path.join(BASE, "Bridgeford-Marketing-v3.pdf")
LOGO       = r"D:\downloads\TC Marketing\TCLogo_edited_edited.png"

def img(name): return os.path.join(BASE, name)

# ── Register Fonts ────────────────────────────────────────────────────────────
def register_fonts():
    pdfmetrics.registerFont(TTFont("Lora",        os.path.join(FONTS_DIR, "Lora-w400.ttf")))
    pdfmetrics.registerFont(TTFont("Lora-Bold",   os.path.join(FONTS_DIR, "Lora-w700.ttf")))
    pdfmetrics.registerFont(TTFont("Lora-Italic", os.path.join(FONTS_DIR, "Lora-BoldItalic.ttf")))
    pdfmetrics.registerFont(TTFont("SegoeUI",     os.path.join(WIN_FONTS, "segoeui.ttf")))
    pdfmetrics.registerFont(TTFont("SegoeUI-Bold",os.path.join(WIN_FONTS, "segoeuib.ttf")))
    pdfmetrics.registerFont(TTFont("SegoeUI-Light",os.path.join(WIN_FONTS,"segoeuil.ttf")))

# Aliases for readability
H1   = "Lora-Bold"       # primary serif heading
H1I  = "Lora-Italic"     # serif italic accent
H2   = "Lora"            # lighter serif
BODY = "SegoeUI"         # body text
BOLD = "SegoeUI-Bold"    # labels, captions
LITE = "SegoeUI-Light"   # light text

# ── Brand Colors ──────────────────────────────────────────────────────────────
DARK_TEAL  = HexColor("#0D5242")
TEAL       = HexColor("#1A7A60")
TEAL_LIGHT = HexColor("#2A9A78")
TEAL_TINT  = HexColor("#E2F5EF")
CREAM      = HexColor("#F6F4EF")
NEAR_BLACK = HexColor("#211E18")
TEXT_SOFT  = HexColor("#5C5444")
MUTED      = HexColor("#8A7F6E")
BORDER     = HexColor("#D5CEBC")
WHITE      = HexColor("#FFFFFF")

COVER_OVERLAY   = Color(0.051, 0.322, 0.259, 0.78)
GALLERY_BG      = Color(0.047, 0.043, 0.043, 1)
BACK_OVERLAY    = Color(0.051, 0.322, 0.259, 0.82)

W, H = letter  # 612 × 792

# ── Image Helpers ─────────────────────────────────────────────────────────────
def load_image(path, max_w=1200):
    """Load image, flatten transparency to white, resize if needed."""
    im = PILImage.open(path)
    if im.mode in ("RGBA", "P"):
        im = im.convert("RGBA")
        bg = PILImage.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[3])
        im = bg
    elif im.mode != "RGB":
        im = im.convert("RGB")
    if im.width > max_w:
        ratio = max_w / im.width
        im = im.resize((max_w, int(im.height * ratio)), PILImage.LANCZOS)
    buf = io.BytesIO()
    fmt = "PNG" if path.lower().endswith(".png") else "JPEG"
    if fmt == "JPEG":
        im.save(buf, format="JPEG", quality=83, optimize=True)
    else:
        im.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return ImageReader(buf)

def load_image_crop(path, target_w, target_h, dark_bg=True):
    """
    Load and center-crop image to exactly fill target_w × target_h.
    Prevents stretching — crops sides or top/bottom to match aspect ratio.
    """
    im = PILImage.open(path)
    bg_color = (10, 10, 10) if dark_bg else (255, 255, 255)
    if im.mode in ("RGBA", "P"):
        im = im.convert("RGBA")
        bg = PILImage.new("RGB", im.size, bg_color)
        bg.paste(im, mask=im.split()[3])
        im = bg
    elif im.mode != "RGB":
        im = im.convert("RGB")

    src_w, src_h = im.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if abs(src_ratio - target_ratio) > 0.01:
        if src_ratio > target_ratio:
            # Wider than slot — crop sides, keep full height
            new_w = int(src_h * target_ratio)
            left = (src_w - new_w) // 2
            im = im.crop((left, 0, left + new_w, src_h))
        else:
            # Taller than slot — crop top/bottom, keep upper ~55% (better for rooms)
            new_h = int(src_w / target_ratio)
            top = int((src_h - new_h) * 0.35)
            im = im.crop((0, top, src_w, top + new_h))

    im = im.resize((int(target_w * 1.5), int(target_h * 1.5)), PILImage.LANCZOS)
    im = im.resize((int(target_w), int(target_h)), PILImage.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=85, optimize=True)
    buf.seek(0)
    return ImageReader(buf)

def load_logo(path, max_w=600):
    """Load logo preserving transparency."""
    im = PILImage.open(path)
    if im.mode not in ("RGBA",):
        im = im.convert("RGBA")
    if im.width > max_w:
        ratio = max_w / im.width
        im = im.resize((max_w, int(im.height * ratio)), PILImage.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    buf.seek(0)
    return ImageReader(buf), im.size

# ── Drawing Helpers ───────────────────────────────────────────────────────────
def fill_page(c, color):
    c.setFillColor(color)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def draw_rect(c, x, y, w, h, fill=None, stroke_color=None, stroke_w=0.5):
    if fill:       c.setFillColor(fill)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(stroke_w)
    c.rect(x, y, w, h, fill=1 if fill else 0, stroke=1 if stroke_color else 0)

def draw_line(c, x1, y1, x2, y2, color=TEAL, width=0.75):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)

def draw_circle(c, x, y, r, fill_color=None, stroke_color=None, stroke_w=1):
    if fill_color:   c.setFillColor(fill_color)
    if stroke_color: c.setStrokeColor(stroke_color); c.setLineWidth(stroke_w)
    c.circle(x, y, r, fill=1 if fill_color else 0, stroke=1 if stroke_color else 0)

def text(c, s, x, y, font, size, color, anchor="left"):
    c.setFont(font, size)
    c.setFillColor(color)
    if   anchor == "center": c.drawCentredString(x, y, s)
    elif anchor == "right":  c.drawRightString(x, y, s)
    else:                    c.drawString(x, y, s)

def spaced(s, n=1):
    """Letter-spacing by inserting thin spaces."""
    return (" " * n).join(s)

def wrap_text(c, txt, x, y, max_w, font, size, color, lh=None):
    """Draw word-wrapped text, return y after last line."""
    if lh is None: lh = size * 1.55
    c.setFont(font, size); c.setFillColor(color)
    words = txt.split(); line = ""
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, font, size) <= max_w:
            line = test
        else:
            c.drawString(x, y, line); y -= lh; line = word
    if line: c.drawString(x, y, line); y -= lh
    return y

def teal_top_bar(c):
    draw_rect(c, 0, H-4, W, 4, fill=DARK_TEAL)

def footer_bar(c, label="THE BRIDGEFORD  ·  TURTLE CREEK HOMES"):
    draw_rect(c, 0, 0, W, 22, fill=DARK_TEAL)
    text(c, label, W/2, 7, BOLD, 6.5, CREAM, anchor="center")

def draw_logo(c, x, y, target_w, path=LOGO):
    """Draw logo at given position and width, maintaining aspect ratio."""
    ir, (pw, ph) = load_logo(path)
    scale = target_w / pw
    target_h = ph * scale
    c.drawImage(ir, x, y - target_h, width=target_w, height=target_h, mask='auto')
    return target_h


# ── PAGE 1: COVER ─────────────────────────────────────────────────────────────
def page_cover(c):
    ir = load_image(img("gallery_0.jpg"))
    c.drawImage(ir, 0, 0, width=W, height=H, preserveAspectRatio=False, mask='auto')
    # Overlay
    c.setFillColor(COVER_OVERLAY)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Logo top-left
    logo_w = 130
    logo_h = draw_logo(c, 40, H - 28, logo_w)

    # Thin teal rule below logo
    draw_line(c, 40, H - 38 - logo_h, W - 40, H - 38 - logo_h, color=TEAL, width=0.5)

    # Main title
    text(c, "The Bridgeford", W/2, 468, H1, 54, CREAM, anchor="center")

    # Subtitle
    c.setFont(LITE, 13.5)
    c.setFillColor(Color(0.965, 0.957, 0.937, 0.88))
    c.drawCentredString(W/2, 434, "Single-floor living at its finest")

    # Tagline
    c.setFont(BODY, 9.5)
    c.setFillColor(Color(0.965, 0.957, 0.937, 0.68))
    c.drawCentredString(W/2, 410,
        "An open, airy ranch with vaulted ceilings and every amenity on one level.")

    # Horizontal rule
    draw_line(c, 42, 218, W - 42, 218, color=TEAL, width=1)

    # Stat strip
    stats = [("3", "BEDROOMS"), ("2", "BATHROOMS"), ("RANCH", "SINGLE FLOOR"), ("2-CAR", "GARAGE")]
    xs = [88, 224, 388, 524]
    for (val, lbl), cx in zip(stats, xs):
        c.setFont(H1, 24); c.setFillColor(CREAM)
        c.drawCentredString(cx, 190, val)
        draw_line(c, cx - 22, 182, cx + 22, 182, color=TEAL, width=0.5)
        c.setFont(BOLD, 7); c.setFillColor(Color(0.965, 0.957, 0.937, 0.72))
        c.drawCentredString(cx, 168, lbl)

    # Footer line
    c.setFont(BODY, 7.5)
    c.setFillColor(Color(0.965, 0.957, 0.937, 0.58))
    c.drawRightString(W - 42, 36, "Town of Mosel, WI  ·  buildflow.ctrl-analytics.com/bridgeford")
    draw_circle(c, 42, 39, 3, fill_color=TEAL)

    c.showPage()


# ── PAGE 2: FEATURES ──────────────────────────────────────────────────────────
def page_features(c):
    fill_page(c, CREAM)
    teal_top_bar(c)

    # Logo small top-right
    draw_logo(c, W - 150, H - 10, 110)

    # Header block
    text(c, spaced("THOUGHTFULLY DESIGNED"), 54, H - 54, BOLD, 7, TEAL)
    text(c, "Built for how you live", 54, H - 86, H1, 30, DARK_TEAL)
    draw_line(c, 54, H - 98, 240, H - 98, color=TEAL, width=1)
    wrap_text(c,
        "Every inch of The Bridgeford is purposefully arranged — all the space you need on a single level, "
        "with a layout that flows naturally from kitchen to living to outdoors.",
        54, H - 120, 504, BODY, 9.5, TEXT_SOFT, lh=15)

    # ── 6 feature cards — 2 col × 3 row, vertically centered in remaining space ──
    features = [
        ("Vaulted Ceilings",
         "The open great room soars with vaulted ceilings, creating an airy, expansive feel from the moment you walk through the door."),
        ("Private Master Retreat",
         "The primary bedroom sits apart from secondary rooms, with an ensuite bath, walk-in closet, and its own private corridor."),
        ("Dedicated Home Office",
         "A proper, separate office — not just a desk nook — keeps work life separated from home life without leaving the house."),
        ("Mudroom + Laundry",
         "A generous mudroom with laundry keeps the mess contained. Drop zone, bench, and washer/dryer all in one organized space off the garage."),
        ("Open Kitchen + Dining",
         "The kitchen island anchors the open living space, with sightlines through to the family room and a large pantry just steps away."),
        ("Covered Porch",
         "A covered porch front and back means you're outside no matter the weather — morning coffee, evening wind-down, all year round."),
    ]

    card_w = 246
    card_h = 96        # fits title + 3-line description with comfortable padding
    gap    = 14
    left_x = 54

    # Center the 3-row grid vertically between header bottom and footer top
    header_bottom = H - 152   # first available y below intro text
    footer_top    = 22
    total_grid_h  = 3 * card_h + 2 * gap   # 316 pts
    available     = header_bottom - footer_top  # 618 pts
    pad_above     = int((available - total_grid_h) / 2)  # ~151 pts
    start_y       = header_bottom - pad_above   # top of first card row

    for i, (title, desc) in enumerate(features):
        col = i % 2
        row = i // 2
        cx = left_x + col * (card_w + gap)
        cy = start_y - row * (card_h + gap) - card_h   # bottom of card

        draw_rect(c, cx, cy, card_w, card_h, fill=WHITE, stroke_color=BORDER, stroke_w=0.5)

        # Teal accent bar (left edge, full card height)
        draw_rect(c, cx, cy, 3, card_h, fill=TEAL)

        # Title
        c.setFont(H1, 10.5); c.setFillColor(DARK_TEAL)
        c.drawString(cx + 14, cy + card_h - 20, title)
        draw_line(c, cx + 14, cy + card_h - 26, cx + card_w - 10, cy + card_h - 26,
                  color=BORDER, width=0.4)

        # Description — wrap within card width
        wrap_text(c, desc, cx + 14, cy + card_h - 42, card_w - 24, BODY, 8.5, TEXT_SOFT, lh=13)

    footer_bar(c)
    c.showPage()


# ── PAGE 3: GALLERY ───────────────────────────────────────────────────────────
def page_gallery(c):
    fill_page(c, GALLERY_BG)
    teal_top_bar(c)

    # Header
    text(c, spaced("INSIDE THE HOME"), W/2, H - 38, BOLD, 7, TEAL, anchor="center")
    text(c, "Every detail considered", W/2, H - 72, H1I, 28, CREAM, anchor="center")
    draw_line(c, W/2 - 60, H - 84, W/2 + 60, H - 84, color=TEAL, width=1)

    # Layout math: fill from below header (y=H-104) down to footer (y=22)
    lx       = 18
    pw       = (W - 2 * lx - 5) / 2   # ~289 pts per photo column
    gap      = 5
    banner_h = 118
    avail    = (H - 104) - 22          # 666 pts
    ph       = int((avail - banner_h - 2 * gap) / 2)   # ~269 pts per grid row

    banner_y = 22
    row2_y   = banner_y + banner_h + gap
    row1_y   = row2_y + ph + gap

    grid_images = [
        ("gallery_1.jpg", "OPEN LIVING AREA"),
        ("gallery_2.jpg", "KITCHEN"),
        ("gallery_3.jpg", "PRIMARY BEDROOM"),
        ("gallery_4.jpg", "HOME OFFICE"),
    ]
    col_xs = [lx, lx + pw + gap]
    row_ys = [row1_y, row2_y]

    for i, (fname, label) in enumerate(grid_images):
        row = i // 2; col = i % 2
        x = col_xs[col]; y = row_ys[row]
        # Crop-to-fill: no stretching, centered crop to match slot aspect ratio
        ir = load_image_crop(img(fname), pw, ph, dark_bg=True)
        c.drawImage(ir, x, y, width=pw, height=ph, preserveAspectRatio=False, mask='auto')
        # Label overlay strip
        c.setFillColor(Color(0, 0, 0, 0.65))
        c.rect(x, y, pw, 36, fill=1, stroke=0)
        c.setFont(BOLD, 7); c.setFillColor(CREAM)
        c.drawString(x + 10, y + 13, spaced(label))

    # Bottom banner — crop to very wide aspect (576 × 118)
    ir5 = load_image_crop(img("gallery_5.jpg"), W - 2 * lx, banner_h, dark_bg=True)
    c.drawImage(ir5, lx, banner_y, width=W - 2 * lx, height=banner_h,
                preserveAspectRatio=False, mask='auto')
    c.setFillColor(Color(0, 0, 0, 0.58))
    c.rect(lx, banner_y, W - 2 * lx, 36, fill=1, stroke=0)
    c.setFont(BOLD, 7); c.setFillColor(CREAM)
    c.drawCentredString(W / 2, banner_y + 13, spaced("BEDROOM 2"))

    footer_bar(c)
    c.showPage()


# ── PAGE 4: FLOOR PLANS ───────────────────────────────────────────────────────
def page_floorplans(c):
    fill_page(c, CREAM)
    teal_top_bar(c)

    text(c, spaced("THE BLUEPRINT"), 54, H - 52, BOLD, 7, TEAL)
    text(c, "A layout built for real life", 54, H - 84, H1, 28, DARK_TEAL)
    draw_line(c, 54, H - 96, 234, H - 96, color=TEAL, width=1)

    lx = 54; img_w = 296

    # Compute natural heights from actual image aspect ratios, then scale to fill column
    # Available vertical space for both images (from label y=H-120 to footer y=27)
    # Deduct: label1(8) + gap(8) + label2(18) + gap(8) = 42 pts overhead
    avail_imgs = (H - 128) - 27   # 637 pts
    overhead   = 8 + 18 + 8       # label spacing between images (34 pts)
    total_img_h = avail_imgs - overhead  # 603 pts for both images combined

    # Natural aspect ratios from PIL
    base_pil = PILImage.open(img("Bridgeford clean.png"))
    bw, bh   = base_pil.size
    base_natural_h = img_w * bh / bw

    var2_pil = PILImage.open(img("bridgeford 2.png"))
    vw, vh   = var2_pil.size
    var2_natural_h = img_w * vh / vw

    natural_total = base_natural_h + var2_natural_h
    if natural_total > 0:
        base_h = int(total_img_h * base_natural_h / natural_total)
        var2_h = int(total_img_h * var2_natural_h / natural_total)
    else:
        base_h = 300; var2_h = 280

    # Draw Base Layout
    text(c, spaced("BASE LAYOUT"), lx, H - 120, BOLD, 7, TEAL)
    base_y = H - 128 - base_h
    base_ir = load_image(img("Bridgeford clean.png"))
    c.drawImage(base_ir, lx, base_y, width=img_w, height=base_h,
                preserveAspectRatio=True, anchor='c', mask='auto')
    draw_rect(c, lx, base_y, img_w, base_h, stroke_color=BORDER, stroke_w=0.5)

    # Draw Variation 2
    var2_label_y = base_y - 18
    text(c, spaced("VARIATION 2"), lx, var2_label_y, BOLD, 7, TEAL)
    var2_y = var2_label_y - 8 - var2_h
    var2_ir = load_image(img("bridgeford 2.png"))
    c.drawImage(var2_ir, lx, var2_y, width=img_w, height=var2_h,
                preserveAspectRatio=True, anchor='c', mask='auto')
    draw_rect(c, lx, var2_y, img_w, var2_h, stroke_color=BORDER, stroke_w=0.5)

    # Right column: room list
    rx = 370; rw = W - rx - 42
    text(c, "Main Floor Rooms", rx, H - 118, H1, 11, DARK_TEAL)
    draw_line(c, rx, H - 126, rx + rw, H - 126, color=TEAL, width=0.75)

    rooms = [
        "Primary Bedroom w/ Ensuite & WIC",
        "Bedroom 2 (12×11')",
        "Bedroom 3 (12×10')",
        "Full Hall Bath",
        "Family Room (vaulted ceiling)",
        "Kitchen w/ 4×8 Island (18×11')",
        "Dining Area",
        "Entry Foyer",
        "Utility Room",
        "2-Car Garage (26×31')",
    ]
    ry = H - 142
    for room in rooms:
        draw_circle(c, rx + 5, ry + 3, 2, fill_color=TEAL)
        c.setFont(BODY, 8.5); c.setFillColor(TEXT_SOFT)
        c.drawString(rx + 13, ry, room); ry -= 14

    # Variation 2 callout box
    box_y = ry - 10; box_h = 76
    draw_rect(c, rx, box_y, rw, box_h, fill=TEAL_TINT, stroke_color=TEAL, stroke_w=1.5)
    text(c, spaced("VARIATION 2 ADDS:"), rx + 8, box_y + box_h - 14, BOLD, 7, TEAL)
    draw_line(c, rx + 8, box_y + box_h - 18, rx + rw - 8, box_y + box_h - 18,
              color=TEAL, width=0.4)
    wrap_text(c,
        "Expanded kitchen, covered porch access, workout/hobby room, and a separate office — all on one level.",
        rx + 8, box_y + box_h - 30, rw - 16, BODY, 8, TEXT_SOFT, lh=13)

    # URL footer note
    c.setFont(BODY, 7.5); c.setFillColor(MUTED)
    c.drawCentredString(W/2, 28, "Explore both layouts at buildflow.ctrl-analytics.com/bridgeford")

    footer_bar(c)
    c.showPage()


# ── PAGE 5: VIRTUAL TOUR + CTA ────────────────────────────────────────────────
def page_cta(c):
    # Raised split so dark-teal section is tighter around its content
    split_y = 454

    # Top half — dark teal (y=split_y to y=H)
    draw_rect(c, 0, split_y, W, H - split_y, fill=DARK_TEAL)
    teal_top_bar(c)

    text(c, spaced("IMMERSIVE 3D TOUR"), W/2, H - 52, BOLD, 7, TEAL_TINT, anchor="center")
    text(c, "Walk every room right now", W/2, H - 92, H1, 30, CREAM, anchor="center")
    draw_line(c, W/2 - 80, H - 104, W/2 + 80, H - 104, color=TEAL, width=0.75)

    c.setFont(BODY, 9.5)
    c.setFillColor(Color(0.965, 0.957, 0.937, 0.80))
    c.drawCentredString(W/2, H - 126,
        "No appointment needed. Explore every room, open hallway, and vaulted ceiling at your own pace.")

    bullets = [
        "Click anywhere to move through the home room by room",
        "Dollhouse view shows the full floor plan in 3D",
        "Built-in measurement tool — check if your furniture fits",
        "Works on phone, tablet, or desktop",
    ]
    by = H - 160
    for b in bullets:
        draw_circle(c, 82, by + 3.5, 3, fill_color=TEAL)
        c.setFont(BODY, 9); c.setFillColor(CREAM)
        c.drawString(96, by, b); by -= 22

    draw_line(c, 0, split_y + 1, W, split_y + 1, color=TEAL, width=2)

    # Bottom half — cream (y=0 to y=split_y)
    draw_rect(c, 0, 0, W, split_y, fill=CREAM)

    text(c, spaced("READY TO BUILD YOURS?"), W/2, split_y - 40, BOLD, 7, TEAL, anchor="center")
    text(c, "The Bridgeford is waiting for you", W/2, split_y - 78, H1, 24, DARK_TEAL, anchor="center")

    body_end_y = wrap_text(c,
        "Ranch living without the compromises. Two distinct layout options, one incredible single-story home. "
        "Reach out to explore lots, pricing, and how to make The Bridgeford yours.",
        76, split_y - 116, 460, BODY, 9, TEXT_SOFT, lh=15)

    # Contact box — centered between body end and footer note
    box_h  = 58
    box_w  = 330
    bx     = (W - box_w) / 2
    # Place box midway between body end and the "schedule a walkthrough" note at y=94
    box_y  = int((body_end_y + 94) / 2) - box_h // 2
    box_y  = max(box_y, 108)   # keep above footer note

    draw_rect(c, bx, box_y, box_w, box_h, fill=DARK_TEAL)
    text(c, spaced("GET IN TOUCH"), W/2, box_y + box_h - 17, BOLD, 7, TEAL_TINT, anchor="center")
    draw_line(c, bx + 16, box_y + box_h - 22, bx + box_w - 16, box_y + box_h - 22,
              color=TEAL, width=0.4)
    text(c, "kristindedering@oostburglumber.com", W/2, box_y + 16, BODY, 9, CREAM, anchor="center")

    c.setFont(BODY, 7.5); c.setFillColor(MUTED)
    c.drawCentredString(W/2, 94, "Schedule a walkthrough  ·  Request pricing  ·  Explore available lots")

    footer_bar(c)
    c.showPage()


# ── PAGE 6: BACK COVER ────────────────────────────────────────────────────────
def page_back(c):
    ir = load_image(img("gallery_3.jpg"))
    c.drawImage(ir, 0, 0, width=W, height=H, preserveAspectRatio=False, mask='auto')
    c.setFillColor(BACK_OVERLAY); c.rect(0, 0, W, H, fill=1, stroke=0)

    cx = W / 2

    # Logo centered
    logo_w = 160
    logo_h = draw_logo(c, cx - logo_w/2, H - 78, logo_w)

    # Thin rule below logo
    draw_line(c, cx - 80, H - 88 - logo_h, cx + 80, H - 88 - logo_h, color=TEAL, width=1)

    text(c, "The Bridgeford", cx, 470, H1I, 42, CREAM, anchor="center")

    c.setFont(LITE, 13); c.setFillColor(Color(0.965, 0.957, 0.937, 0.78))
    c.drawCentredString(cx, 440, "Ranch Living Redefined")

    draw_line(c, cx - 100, 424, cx + 100, 424, color=TEAL, width=1)

    c.setFont(BODY, 9); c.setFillColor(Color(0.965, 0.957, 0.937, 0.80))
    c.drawCentredString(cx, 396, "kristindedering@oostburglumber.com")
    c.setFont(BODY, 9); c.setFillColor(TEAL)
    c.drawCentredString(cx, 378, "buildflow.ctrl-analytics.com/bridgeford")

    c.setFont(BODY, 7); c.setFillColor(Color(0.965, 0.957, 0.937, 0.48))
    c.drawCentredString(cx, 38, "© 2025 Turtle Creek Homes  ·  The Bridgeford Model")

    c.showPage()


# ── Build ─────────────────────────────────────────────────────────────────────
def build():
    register_fonts()
    c = canvas.Canvas(OUT, pagesize=letter)
    c.setTitle("The Bridgeford — Turtle Creek Homes")
    c.setAuthor("Turtle Creek Homes")
    c.setSubject("The Bridgeford — Ranch Living Redefined")

    print("Page 1: Cover...")
    page_cover(c)
    print("Page 2: Features...")
    page_features(c)
    print("Page 3: Gallery...")
    page_gallery(c)
    print("Page 4: Floor Plans...")
    page_floorplans(c)
    print("Page 5: Virtual Tour + CTA...")
    page_cta(c)
    print("Page 6: Back Cover...")
    page_back(c)

    c.save()
    size_mb = os.path.getsize(OUT) / 1_048_576
    print(f"\nSaved: {OUT}")
    print(f"Size:  {size_mb:.2f} MB")

if __name__ == "__main__":
    build()
