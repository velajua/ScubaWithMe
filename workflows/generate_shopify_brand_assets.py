from __future__ import annotations

import base64
import io
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BRAND_DIR = ROOT / "exports" / "shopify" / "brand"
SOURCE_TURTLE = BRAND_DIR / "turtle-mark-transparent.png"
SOURCE_LOGO_SHELL = BRAND_DIR / "logo-shell-transparent.png"
SOURCE_ICON_TURTLE = BRAND_DIR / "turtle-icon-transparent.png"

BRUSH_FONT = Path(r"C:\Windows\Fonts\BRUSHSCI.TTF")
UI_FONT = Path(r"C:\Windows\Fonts\segoeui.ttf")
UI_FONT_BOLD = Path(r"C:\Windows\Fonts\segoeuib.ttf")

COLORS = {
    "ocean": "#0C4454",
    "ocean_dark": "#072C3B",
    "ocean_mid": "#146779",
    "seafoam": "#8FD6D0",
    "seafoam_light": "#DDF4F2",
    "sand": "#D7BE8F",
    "ink": "#0A1E27",
    "white": "#FFFFFF",
}


def load_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def crop_alpha(img: Image.Image, pad: int = 0) -> Image.Image:
    bbox = img.getbbox()
    if not bbox:
        return img
    left = max(0, bbox[0] - pad)
    top = max(0, bbox[1] - pad)
    right = min(img.width, bbox[2] + pad)
    bottom = min(img.height, bbox[3] + pad)
    return img.crop((left, top, right, bottom))


def contain(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    copy = img.copy()
    copy.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return copy


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def paste_centered(base: Image.Image, overlay: Image.Image, x: int, y: int) -> None:
    base.alpha_composite(overlay, (x, y))


def draw_script_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fill: str,
    shadow: bool = False,
    anchor: str = "ls",
    font_size: int = 250,
) -> tuple[int, int, int, int]:
    f = font(BRUSH_FONT, font_size)
    if shadow:
        shadow_fill = (7, 44, 59, 90)
        draw.text((xy[0] + 7, xy[1] + 8), text, font=f, fill=shadow_fill, anchor=anchor)
    draw.text(xy, text, font=f, fill=fill, anchor=anchor)
    return draw.textbbox(xy, text, font=f, anchor=anchor)


def draw_subtitle(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fill: str,
    anchor: str = "la",
    font_size: int = 38,
) -> tuple[int, int, int, int]:
    f = font(UI_FONT, font_size)
    draw.text(xy, text, font=f, fill=fill, anchor=anchor)
    return draw.textbbox(xy, text, font=f, anchor=anchor)


def save_png(img: Image.Image, name: str) -> Path:
    out = BRAND_DIR / name
    img.save(out, format="PNG")
    return out


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def create_primary_logo(turtle: Image.Image, text_fill: str, filename: str) -> Path:
    canvas = Image.new("RGBA", (2600, 1200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    logo_turtle = contain(turtle, 1100, 820)
    turtle_x = 120
    turtle_y = 190
    paste_centered(canvas, logo_turtle, turtle_x, turtle_y)

    baseline_x = 1240
    baseline_y = 650
    draw_script_text(draw, (baseline_x, baseline_y), "ScubaWithMe", fill=text_fill, shadow=True, font_size=255)
    draw_subtitle(
        draw,
        (baseline_x + 12, baseline_y + 48),
        "UNDERWATER PHOTOGRAPHY",
        fill=ImageColor.getrgb(COLORS["ocean_mid"]) + (255,),
        font_size=40,
    )

    return save_png(canvas, filename)


def create_shell_logo(logo: Image.Image, size: tuple[int, int], filename: str) -> Path:
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    fitted = contain(logo, size[0] - 120, size[1] - 120)
    x = (size[0] - fitted.width) // 2
    y = (size[1] - fitted.height) // 2
    paste_centered(canvas, fitted, x, y)
    return save_png(canvas, filename)


def create_stacked_logo(turtle: Image.Image, text_fill: str, filename: str) -> Path:
    canvas = Image.new("RGBA", (1800, 1800), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    stacked_turtle = contain(turtle, 1200, 900)
    paste_centered(canvas, stacked_turtle, 300, 160)

    text_bbox = draw_script_text(draw, (900, 1270), "ScubaWithMe", fill=text_fill, shadow=True, anchor="ms", font_size=240)
    draw_subtitle(
        draw,
        (900, text_bbox[3] + 24),
        "UNDERWATER PHOTOGRAPHY",
        fill=ImageColor.getrgb(COLORS["ocean_mid"]) + (255,),
        anchor="ma",
        font_size=38,
    )
    return save_png(canvas, filename)


def create_wordmark(filename: str, fill: str) -> Path:
    canvas = Image.new("RGBA", (2000, 700), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw_script_text(draw, (130, 420), "ScubaWithMe", fill=fill, shadow=True, font_size=260)
    draw_subtitle(
        draw,
        (150, 455),
        "UNDERWATER PHOTOGRAPHY",
        fill=ImageColor.getrgb(COLORS["ocean_mid"]) + (255,),
        font_size=40,
    )
    return save_png(canvas, filename)


def create_icon_badge(turtle: Image.Image, size: int, filename: str) -> Path:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    margin = int(size * 0.06)
    circle_box = (margin, margin, size - margin, size - margin)
    draw.ellipse(circle_box, fill=COLORS["ocean_dark"])

    inner_margin = int(size * 0.11)
    draw.ellipse(
        (inner_margin, inner_margin, size - inner_margin, size - inner_margin),
        outline=ImageColor.getrgb(COLORS["seafoam"]) + (70,),
        width=max(4, size // 64),
    )

    icon_turtle = contain(turtle, int(size * 0.74), int(size * 0.60))
    tint = Image.new("RGBA", icon_turtle.size, ImageColor.getrgb(COLORS["white"]) + (0,))
    icon_group = Image.new("RGBA", icon_turtle.size, (0, 0, 0, 0))
    icon_group.alpha_composite(icon_turtle)
    icon_group.alpha_composite(tint)
    paste_centered(
        canvas,
        icon_group,
        (size - icon_turtle.width) // 2 - int(size * 0.02),
        (size - icon_turtle.height) // 2 + int(size * 0.02),
    )

    return save_png(canvas, filename)


def create_watermark(turtle: Image.Image, filename: str) -> Path:
    canvas = Image.new("RGBA", (2200, 900), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    muted_turtle = contain(turtle, 860, 620)
    alpha = muted_turtle.getchannel("A").point(lambda p: int(p * 0.62))
    white_turtle = Image.new("RGBA", muted_turtle.size, (255, 255, 255, 0))
    white_turtle.putalpha(alpha)
    paste_centered(canvas, white_turtle, 80, 120)
    draw_script_text(draw, (960, 520), "ScubaWithMe", fill=(255, 255, 255, 165), shadow=False, font_size=230)
    return save_png(canvas, filename)


def create_shell_watermark(logo: Image.Image, filename: str) -> Path:
    canvas = Image.new("RGBA", (2200, 1200), (0, 0, 0, 0))
    muted = contain(logo, 1700, 850)
    alpha = muted.getchannel("A").point(lambda p: int(p * 0.45))
    white_logo = Image.new("RGBA", muted.size, (255, 255, 255, 0))
    white_logo.putalpha(alpha)
    paste_centered(canvas, white_logo, (2200 - muted.width) // 2, (1200 - muted.height) // 2)
    return save_png(canvas, filename)


def create_brand_board(turtle: Image.Image, filename: str) -> Path:
    canvas = Image.new("RGBA", (1800, 1240), COLORS["seafoam_light"])
    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle((50, 50, 1750, 1190), radius=34, fill=(255, 255, 255, 235))
    draw_script_text(draw, (110, 215), "ScubaWithMe", fill=COLORS["ocean"], shadow=False, font_size=200)
    draw_subtitle(draw, (118, 250), "COASTAL SIGNATURE BRAND KIT", fill=COLORS["ocean_mid"], font_size=34)

    sample_turtle = contain(turtle, 540, 360)
    canvas.alpha_composite(sample_turtle, (1080, 120))

    swatches = [
        ("Ocean Dark", COLORS["ocean_dark"]),
        ("Ocean", COLORS["ocean"]),
        ("Seafoam", COLORS["seafoam"]),
        ("Sand", COLORS["sand"]),
    ]
    x = 118
    y = 380
    for label, color in swatches:
        draw.rounded_rectangle((x, y, x + 330, y + 170), radius=26, fill=color)
        draw.text((x + 24, y + 128), label, font=font(UI_FONT_BOLD, 30), fill=COLORS["white"])
        draw.text((x + 24, y + 92), color, font=font(UI_FONT, 24), fill=COLORS["seafoam_light"])
        x += 370

    draw.text((118, 660), "Recommended Shopify usage", font=font(UI_FONT_BOLD, 40), fill=COLORS["ocean_dark"])
    tips = [
        "Header logo: use logo-primary-color.png on light themes.",
        "Dark header: use logo-wordmark-white.png or logo-primary-whitewordmark.png.",
        "Favicon: use favicon-32.png.",
        "Social/avatar: use icon-badge-1024.png.",
    ]
    ty = 730
    for tip in tips:
        draw.ellipse((122, ty + 12, 138, ty + 28), fill=COLORS["seafoam"])
        draw.text((162, ty), tip, font=font(UI_FONT, 30), fill=COLORS["ink"])
        ty += 72

    return save_png(canvas, filename)


def create_brand_board_v2(shell_logo: Image.Image, icon_turtle: Image.Image, filename: str) -> Path:
    canvas = Image.new("RGBA", (1800, 1240), COLORS["seafoam_light"])
    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle((50, 50, 1750, 1190), radius=34, fill=(255, 255, 255, 235))
    draw_script_text(draw, (110, 215), "ScubaWithMe", fill=COLORS["ocean"], shadow=False, font_size=200)
    draw_subtitle(draw, (118, 250), "TURTLE SHELL LOGO KIT", fill=COLORS["ocean_mid"], font_size=34)

    sample_logo = contain(shell_logo, 620, 320)
    canvas.alpha_composite(sample_logo, (1085, 138))

    swatches = [
        ("Ocean Dark", COLORS["ocean_dark"]),
        ("Ocean", COLORS["ocean"]),
        ("Seafoam", COLORS["seafoam"]),
        ("Sand", COLORS["sand"]),
    ]
    x = 118
    y = 380
    for label, color in swatches:
        draw.rounded_rectangle((x, y, x + 330, y + 170), radius=26, fill=color)
        draw.text((x + 24, y + 128), label, font=font(UI_FONT_BOLD, 30), fill=COLORS["white"])
        draw.text((x + 24, y + 92), color, font=font(UI_FONT, 24), fill=COLORS["seafoam_light"])
        x += 370

    draw.text((118, 660), "Recommended Shopify usage", font=font(UI_FONT_BOLD, 40), fill=COLORS["ocean_dark"])
    tips = [
        "Header logo: use logo-primary-color.png.",
        "Square placements: use logo-stacked-color.png or icon-badge-1024.png.",
        "Favicon: use favicon-32.png.",
        "Keep the shell-lettered turtle as the primary storefront brand mark.",
    ]
    ty = 730
    for tip in tips:
        draw.ellipse((122, ty + 12, 138, ty + 28), fill=COLORS["seafoam"])
        draw.text((162, ty), tip, font=font(UI_FONT, 30), fill=COLORS["ink"])
        ty += 72

    return save_png(canvas, filename)


def create_svg_wrappers(shell_logo: Image.Image) -> None:
    shell_bytes = io.BytesIO()
    shell_logo.save(shell_bytes, format="PNG")
    encoded = base64.b64encode(shell_bytes.getvalue()).decode("ascii")
    image_href = f"data:image/png;base64,{encoded}"

    primary_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="2600" height="1200" viewBox="0 0 2600 1200">
  <image href="{image_href}" x="60" y="70" width="2480" height="1060"/>
</svg>
"""
    (BRAND_DIR / "logo-primary-color.svg").write_text(primary_svg, encoding="utf-8")

    stacked_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1800" viewBox="0 0 1800 1800">
  <image href="{image_href}" x="90" y="320" width="1620" height="760"/>
</svg>
"""
    (BRAND_DIR / "logo-stacked-color.svg").write_text(stacked_svg, encoding="utf-8")


def main() -> None:
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    turtle = crop_alpha(load_rgba(SOURCE_TURTLE), pad=10)
    shell_logo = crop_alpha(load_rgba(SOURCE_LOGO_SHELL), pad=10)
    icon_turtle = crop_alpha(load_rgba(SOURCE_ICON_TURTLE), pad=10)

    create_shell_logo(shell_logo, (2600, 1200), "logo-primary-color.png")
    create_shell_logo(shell_logo, (1800, 1800), "logo-stacked-color.png")
    create_primary_logo(turtle, COLORS["white"], "logo-primary-whitewordmark.png")
    create_wordmark("logo-wordmark-color.png", COLORS["ocean"])
    create_wordmark("logo-wordmark-white.png", COLORS["white"])
    create_icon_badge(icon_turtle, 1024, "icon-badge-1024.png")
    create_icon_badge(icon_turtle, 512, "favicon-512.png")
    create_icon_badge(icon_turtle, 180, "apple-touch-icon-180.png")
    create_icon_badge(icon_turtle, 32, "favicon-32.png")
    create_shell_watermark(shell_logo, "watermark-white.png")
    create_brand_board_v2(shell_logo, icon_turtle, "shopify-brand-board.png")
    create_svg_wrappers(shell_logo)


if __name__ == "__main__":
    main()
