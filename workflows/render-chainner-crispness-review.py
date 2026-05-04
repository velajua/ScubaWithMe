from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat


ROOT = Path(__file__).resolve().parents[1]
BASELINE_DIR = ROOT / "exports" / "print-tests" / "ESRGAN-pytorch-RealESRNet"
VARIANT_ROOT = ROOT / "exports" / "print-tests" / "chainner_from_realesrnet"
OUT_DIR = ROOT / "exports" / "print-tests" / "render-review"
NOTES_PATH = ROOT / "notes" / "chainner-crispness-render-review.md"

THUMB_W = 220
THUMB_H = 180
CROP_SIZE = 220
PAD = 18
LABEL_H = 58
HEADER_H = 82
BG = (246, 246, 242)
INK = (18, 28, 33)
MUTED = (86, 94, 98)
LINE = (198, 203, 203)
WHITE = (255, 255, 255)


def font(size=18, bold=False):
    names = [
        "arialbd.ttf" if bold else "arial.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "calibrib.ttf" if bold else "calibri.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


F_TITLE = font(30, True)
F_HEAD = font(18, True)
F_BODY = font(15)
F_SMALL = font(12)


def text_fit(draw, text, width, fnt):
    if draw.textlength(text, font=fnt) <= width:
        return text
    ell = "..."
    while text and draw.textlength(text + ell, font=fnt) > width:
        text = text[:-1]
    return text + ell


def image_fit(im, box_w, box_h):
    im = im.convert("RGB")
    ratio = min(box_w / im.width, box_h / im.height)
    size = (max(1, int(im.width * ratio)), max(1, int(im.height * ratio)))
    resized = im.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (box_w, box_h), WHITE)
    canvas.paste(resized, ((box_w - size[0]) // 2, (box_h - size[1]) // 2))
    return canvas


def center_crop_1x(im, size):
    im = im.convert("RGB")
    side = min(im.width, im.height, size)
    left = (im.width - side) // 2
    top = (im.height - side) // 2
    crop = im.crop((left, top, left + side, top + side))
    if crop.size != (size, size):
        crop = crop.resize((size, size), Image.Resampling.NEAREST)
    return crop


def edge_score(im):
    gray = im.convert("L").resize((320, 320), Image.Resampling.LANCZOS)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    stat = ImageStat.Stat(edges)
    return round(stat.mean[0], 1)


def variant_label(path):
    stem = path.stem
    for marker in ["-t01-", "-t02-", "-t03-", "-t04-", "-t05-", "-t06-", "-t07-", "-t08-", "-t09-"]:
        if marker in stem:
            return marker[1:4] + " " + stem.split(marker, 1)[1].replace("-corrected", "").replace("-", " ")
    return stem.replace("_", " ")


def collect_sets():
    sets = {}
    for baseline in sorted(BASELINE_DIR.glob("*.png")):
        key = baseline.stem
        sets.setdefault(key, {})["baseline"] = baseline
    for folder in sorted(VARIANT_ROOT.iterdir()):
        if not folder.is_dir():
            continue
        key = folder.name
        variants = sorted(folder.glob("*.png"))
        if variants:
            sets.setdefault(key, {})["variants"] = variants
    return sets


def draw_card(draw, sheet, path, x, y, crop=False):
    with Image.open(path) as im:
        if crop:
            visual = center_crop_1x(im, CROP_SIZE)
            score = edge_score(visual)
            box_w, box_h = CROP_SIZE, CROP_SIZE
        else:
            visual = image_fit(im, THUMB_W, THUMB_H)
            score = edge_score(im)
            box_w, box_h = THUMB_W, THUMB_H
        sheet.paste(visual, (x, y + LABEL_H))
        draw.rectangle((x, y + LABEL_H, x + box_w - 1, y + LABEL_H + box_h - 1), outline=LINE)
        label = "baseline RealESRNet" if path.parent.name == "ESRGAN-pytorch-RealESRNet" else variant_label(path)
        draw.text((x, y), text_fit(draw, label, box_w, F_BODY), font=F_BODY, fill=INK)
        meta = f"{im.width}x{im.height} | edge {score}"
        draw.text((x, y + 23), meta, font=F_SMALL, fill=MUTED)


def make_overview(sets, crop=False):
    keys = sorted(sets)
    cols = 10
    card_w = CROP_SIZE if crop else THUMB_W
    card_h = (CROP_SIZE if crop else THUMB_H) + LABEL_H
    row_h = card_h + 34
    width = PAD * 2 + cols * card_w + (cols - 1) * PAD
    height = HEADER_H + len(keys) * row_h + PAD
    sheet = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(sheet)
    title = "chaiNNer crispness review: 1:1 center crops" if crop else "chaiNNer crispness review: full-image variants"
    draw.text((PAD, 20), title, font=F_TITLE, fill=INK)
    draw.text((PAD, 55), "Edge score is a rough visual aid only; inspect eyes, fine texture, halos, and fake detail by eye.", font=F_BODY, fill=MUTED)
    for row, key in enumerate(keys):
        y = HEADER_H + row * row_h
        draw.text((PAD, y), key, font=F_HEAD, fill=INK)
        paths = []
        if "baseline" in sets[key]:
            paths.append(sets[key]["baseline"])
        paths.extend(sets[key].get("variants", []))
        for col, path in enumerate(paths[:cols]):
            x = PAD + col * (card_w + PAD)
            draw_card(draw, sheet, path, x, y + 28, crop=crop)
    out = OUT_DIR / ("chainner-crispness-crops.png" if crop else "chainner-crispness-full-variants.png")
    sheet.save(out, quality=95)
    return out


def make_per_image(sets):
    paths = []
    for key in sorted(sets):
        entries = []
        if "baseline" in sets[key]:
            entries.append(sets[key]["baseline"])
        entries.extend(sets[key].get("variants", []))
        cols = 5
        card_w = THUMB_W + CROP_SIZE + PAD
        card_h = max(THUMB_H, CROP_SIZE) + LABEL_H
        width = PAD * 2 + cols * card_w + (cols - 1) * PAD
        rows = (len(entries) + cols - 1) // cols
        height = HEADER_H + rows * (card_h + PAD) + PAD
        sheet = Image.new("RGB", (width, height), BG)
        draw = ImageDraw.Draw(sheet)
        draw.text((PAD, 20), key, font=F_TITLE, fill=INK)
        draw.text((PAD, 55), "Left: whole image. Right: unscaled center crop for crispness and artifact review.", font=F_BODY, fill=MUTED)
        for idx, path in enumerate(entries):
            row = idx // cols
            col = idx % cols
            x = PAD + col * (card_w + PAD)
            y = HEADER_H + row * (card_h + PAD)
            with Image.open(path) as im:
                label = "baseline RealESRNet" if path.parent.name == "ESRGAN-pytorch-RealESRNet" else variant_label(path)
                draw.text((x, y), text_fit(draw, label, card_w, F_BODY), font=F_BODY, fill=INK)
                draw.text((x, y + 23), f"{im.width}x{im.height} | edge {edge_score(im)}", font=F_SMALL, fill=MUTED)
                whole = image_fit(im, THUMB_W, THUMB_H)
                crop = center_crop_1x(im, CROP_SIZE)
                sheet.paste(whole, (x, y + LABEL_H))
                sheet.paste(crop, (x + THUMB_W + PAD, y + LABEL_H))
                draw.rectangle((x, y + LABEL_H, x + THUMB_W - 1, y + LABEL_H + THUMB_H - 1), outline=LINE)
                draw.rectangle((x + THUMB_W + PAD, y + LABEL_H, x + THUMB_W + PAD + CROP_SIZE - 1, y + LABEL_H + CROP_SIZE - 1), outline=LINE)
        out = OUT_DIR / f"{key}-crispness-review.png"
        sheet.save(out, quality=95)
        paths.append(out)
    return paths


def write_notes(full, crops, per_image):
    lines = [
        "# chaiNNer Crispness Render Review",
        "",
        "Generated comparison renders for the chaiNNer exports. These are review aids, not proof of print readiness.",
        "",
        "## Main Sheets",
        "",
        f"- [Full-image variants]({full.relative_to(ROOT).as_posix()})",
        f"- [1:1 center crops]({crops.relative_to(ROOT).as_posix()})",
        "",
        "## Per-Image Sheets",
        "",
    ]
    for path in per_image:
        lines.append(f"- [{path.stem}]({path.relative_to(ROOT).as_posix()})")
    lines.extend([
        "",
        "## How to Inspect",
        "",
        "- Open the crop sheet at 100 percent zoom.",
        "- Look for crisp eyes, clean pattern edges, and believable texture.",
        "- Treat halos, crunchy edges, waxy smoothing, invented spots, or fake coral detail as print risks.",
        "- The edge score is only a rough signal; higher is not always better.",
    ])
    NOTES_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sets = collect_sets()
    full = make_overview(sets, crop=False)
    crops = make_overview(sets, crop=True)
    per_image = make_per_image(sets)
    write_notes(full, crops, per_image)
    print(f"Wrote {full}")
    print(f"Wrote {crops}")
    print(f"Wrote {len(per_image)} per-image review sheets")
    print(f"Wrote {NOTES_PATH}")


if __name__ == "__main__":
    main()
