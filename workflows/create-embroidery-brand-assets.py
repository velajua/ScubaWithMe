from __future__ import annotations

import base64
from collections import deque
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "exports" / "shopify" / "brand"
OUT = BRAND / "embroidery"

OCEAN_DARK = (7, 44, 59, 255)
OCEAN = (12, 68, 84, 255)
SAND = (215, 190, 143, 255)
TRANSPARENT = (0, 0, 0, 0)


def trim_alpha(image: Image.Image, padding: int = 32) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        return image
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(image.width, bbox[2] + padding)
    bottom = min(image.height, bbox[3] + padding)
    return image.crop((left, top, right, bottom))


def load_embedded_svg_png(path: Path) -> Image.Image:
    text = path.read_text(encoding="utf-8")
    marker = "base64,"
    start = text.index(marker) + len(marker)
    end = text.index('"', start)
    data = base64.b64decode(text[start:end])
    return Image.open(BytesIO(data)).convert("RGBA")


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    bbox = image.getchannel("A").getbbox()
    if not bbox:
        return (0, 0, image.width, image.height)
    return bbox


def remove_small_alpha_islands(image: Image.Image, min_pixels: int = 12000) -> Image.Image:
    image = image.convert("RGBA")
    pixels = image.load()
    width, height = image.size
    seen: set[tuple[int, int]] = set()

    for start_y in range(height):
        for start_x in range(width):
            if (start_x, start_y) in seen or pixels[start_x, start_y][3] < 32:
                continue

            queue = deque([(start_x, start_y)])
            component: list[tuple[int, int]] = []
            seen.add((start_x, start_y))
            while queue:
                x, y = queue.popleft()
                component.append((x, y))
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if nx < 0 or ny < 0 or nx >= width or ny >= height:
                        continue
                    if (nx, ny) in seen or pixels[nx, ny][3] < 32:
                        continue
                    seen.add((nx, ny))
                    queue.append((nx, ny))

            if len(component) < min_pixels:
                for x, y in component:
                    pixels[x, y] = (0, 0, 0, 0)

    return image


def crop_to_art_from_stacked_svg() -> Image.Image:
    source = load_embedded_svg_png(BRAND / "logo-stacked-color.svg")
    source = trim_alpha(source, padding=0)
    return remove_small_alpha_islands(source, min_pixels=18000)


def nearest_palette_color(r: int, g: int, b: int, palette: tuple[tuple[int, int, int, int], ...]) -> tuple[int, int, int, int]:
    return min(
        palette,
        key=lambda color: (r - color[0]) ** 2 + (g - color[1]) ** 2 + (b - color[2]) ** 2,
    )


def flatten_to_palette(
    image: Image.Image,
    palette: tuple[tuple[int, int, int, int], ...],
    alpha_threshold: int = 72,
    cleanup_size: int = 0,
) -> Image.Image:
    image = image.convert("RGBA")
    output = Image.new("RGBA", image.size, (0, 0, 0, 0))
    src = image.load()
    dst = output.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = src[x, y]
            if a < alpha_threshold:
                continue
            dst[x, y] = nearest_palette_color(r, g, b, palette)
    if cleanup_size >= 3:
        output = output.filter(ImageFilter.ModeFilter(cleanup_size))
        pixels = output.load()
        allowed = set(palette)
        for y in range(output.height):
            for x in range(output.width):
                pixel = pixels[x, y]
                if pixel[3] == 0:
                    pixels[x, y] = (0, 0, 0, 0)
                elif pixel not in allowed:
                    pixels[x, y] = nearest_palette_color(pixel[0], pixel[1], pixel[2], palette)
    return trim_alpha(output)


def build_lettering_fill_mask(flat_logo: Image.Image) -> Image.Image:
    flat_logo = flat_logo.convert("RGBA")
    left, top, right, bottom = alpha_bbox(flat_logo)
    art_width = right - left
    art_height = bottom - top
    output = Image.new("L", flat_logo.size, 0)

    wordmark = Image.open(BRAND / "logo-wordmark-color.png").convert("RGBA")
    wordmark = wordmark.crop((0, 0, wordmark.width, 455))
    wordmark = trim_alpha(wordmark, padding=0)
    wordmark_mask = wordmark.getchannel("A").point(lambda value: 255 if value >= 72 else 0)

    target_box = (
        left + int(art_width * 0.16),
        top + int(art_height * 0.15),
        left + int(art_width * 0.75),
        top + int(art_height * 0.50),
    )
    target_width = target_box[2] - target_box[0]
    target_height = target_box[3] - target_box[1]
    wordmark_mask = wordmark_mask.resize((target_width, target_height), Image.Resampling.BICUBIC)
    output.paste(wordmark_mask, target_box[:2], wordmark_mask)

    return output.filter(ImageFilter.ModeFilter(5))


def expand_mask(mask: Image.Image, radius: int) -> Image.Image:
    return mask.filter(ImageFilter.MaxFilter(radius * 2 + 1))


def make_lettering_asset(flat_logo: Image.Image, fill_mask: Image.Image) -> Image.Image:
    outline_mask = expand_mask(fill_mask, 8)
    output = Image.new("RGBA", flat_logo.size, TRANSPARENT)
    out = output.load()
    fill = fill_mask.load()
    outline = outline_mask.load()
    for y in range(flat_logo.height):
        for x in range(flat_logo.width):
            if outline[x, y] == 0:
                continue
            out[x, y] = SAND if fill[x, y] else OCEAN_DARK
    return trim_alpha(output)


def shell_point(left: int, top: int, art_width: int, art_height: int, x: float, y: float) -> tuple[int, int]:
    return (left + int(art_width * x), top + int(art_height * y))


def draw_shell_seams(
    draw: ImageDraw.ImageDraw,
    left: int,
    top: int,
    art_width: int,
    art_height: int,
) -> None:
    seam_width = max(5, int(art_width * 0.006))

    def line(points: list[tuple[float, float]], width: int = seam_width) -> None:
        draw.line(
            [shell_point(left, top, art_width, art_height, x, y) for x, y in points],
            fill=SAND,
            width=width,
            joint="curve",
        )

    # Broad shell seams only. Small texture is avoided because it will not embroider cleanly.
    line([(0.18, 0.34), (0.25, 0.21), (0.38, 0.12), (0.55, 0.11), (0.70, 0.18), (0.79, 0.32)])
    line([(0.19, 0.43), (0.32, 0.53), (0.50, 0.55), (0.66, 0.50), (0.76, 0.42)])
    line([(0.30, 0.18), (0.35, 0.31), (0.35, 0.50)])
    line([(0.45, 0.12), (0.47, 0.29), (0.46, 0.55)])
    line([(0.59, 0.12), (0.57, 0.30), (0.56, 0.54)])
    line([(0.70, 0.20), (0.65, 0.34), (0.66, 0.50)])
    line([(0.23, 0.39), (0.32, 0.36), (0.44, 0.36), (0.58, 0.37), (0.72, 0.36)], width=max(4, seam_width - 1))


def remove_lettering_from_logo(flat_logo: Image.Image, fill_mask: Image.Image) -> Image.Image:
    output = flat_logo.copy()
    left, top, right, bottom = alpha_bbox(output)
    art_width = right - left
    art_height = bottom - top
    shell_patch = (
        left + int(art_width * 0.17),
        top + int(art_height * 0.08),
        left + int(art_width * 0.80),
        top + int(art_height * 0.54),
    )
    draw = ImageDraw.Draw(output)
    draw.ellipse(shell_patch, fill=OCEAN)

    erase_mask = expand_mask(fill_mask, 10)
    pixels = output.load()
    erase = erase_mask.load()
    for y in range(output.height):
        for x in range(output.width):
            if erase[x, y] and pixels[x, y][3] > 0:
                pixels[x, y] = OCEAN
    draw_shell_seams(draw, left, top, art_width, art_height)
    return trim_alpha(output)


def make_lettering_only() -> Path:
    source = crop_to_art_from_stacked_svg()
    flat_logo = flatten_to_palette(source, (OCEAN_DARK, OCEAN, SAND), alpha_threshold=72, cleanup_size=7)
    fill_mask = build_lettering_fill_mask(flat_logo)
    output = make_lettering_asset(flat_logo, fill_mask)
    path = OUT / "scubawithme-lettering-only-2color.png"
    output.save(path)
    return path


def make_turtle_lettering() -> Path:
    source = crop_to_art_from_stacked_svg()
    output = flatten_to_palette(source, (OCEAN_DARK, OCEAN, SAND), alpha_threshold=72, cleanup_size=7)
    path = OUT / "scubawithme-turtle-with-lettering-3color.png"
    output.save(path)
    return path


def make_turtle_only() -> Path:
    source = crop_to_art_from_stacked_svg()
    flat_logo = flatten_to_palette(source, (OCEAN_DARK, OCEAN, SAND), alpha_threshold=72, cleanup_size=7)
    fill_mask = build_lettering_fill_mask(flat_logo)
    output = remove_lettering_from_logo(flat_logo, fill_mask)
    path = OUT / "scubawithme-turtle-only-3color.png"
    output.save(path)
    return path


def opaque_color_count(path: Path) -> int:
    image = Image.open(path).convert("RGBA")
    colors = {
        pixel
        for pixel in image.getdata()
        if pixel[3] > 0
    }
    return len(colors)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [make_lettering_only(), make_turtle_lettering(), make_turtle_only()]
    for path in paths:
        image = Image.open(path).convert("RGBA")
        print(f"{path.relative_to(ROOT)} {image.size} opaque_colors={opaque_color_count(path)}")


if __name__ == "__main__":
    main()
