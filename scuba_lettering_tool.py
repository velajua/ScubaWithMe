from __future__ import annotations

import json
import math
import re
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, ttk

from PIL import Image, ImageDraw, ImageFont, ImageTk


ROOT = Path(__file__).resolve().parent
DEFAULT_IMAGE_DIR = ROOT / "exports" / "print-tests" / "chainner_from_realesrnet"
DEFAULT_OVERLAY_DIR = ROOT / "exports" / "shopify" / "brand"
DEFAULT_OUTPUT_ROOT = ROOT / "exports" / "shopify" / "images"
DEFAULT_PRESET_DIR = ROOT / "workflows" / "lettering-presets"
FONT_PATH = Path("C:/Windows/Fonts/arialbd.ttf")
DEFAULT_TEXT = "The Original Chill Diver"
DEFAULT_FILL = "#fffff5"
DEFAULT_STROKE = "#021e2d"
DEFAULT_FONT_NAME = "ScubaWithMe Logo Script"
FONT_OPTIONS = {
    "ScubaWithMe Logo Script": Path("C:/Windows/Fonts/BRUSHSCI.TTF"),
    "Segoe Print": Path("C:/Windows/Fonts/segoepr.ttf"),
    "Segoe Print Bold": Path("C:/Windows/Fonts/segoeprb.ttf"),
    "Segoe Script": Path("C:/Windows/Fonts/segoesc.ttf"),
    "Segoe Script Bold": Path("C:/Windows/Fonts/segoescb.ttf"),
    "Freestyle Script": Path("C:/Windows/Fonts/FREESCPT.TTF"),
    "French Script MT": Path("C:/Windows/Fonts/FRSCRIPT.TTF"),
    "Script MT Bold": Path("C:/Windows/Fonts/SCRIPTBL.TTF"),
    "Arial Bold": Path("C:/Windows/Fonts/arialbd.ttf"),
    "Arial": Path("C:/Windows/Fonts/arial.ttf"),
    "Arial Narrow Bold": Path("C:/Windows/Fonts/ARIALNB.TTF"),
    "Arial Black": Path("C:/Windows/Fonts/ariblk.ttf"),
    "Georgia Bold": Path("C:/Windows/Fonts/georgiab.ttf"),
    "Verdana Bold": Path("C:/Windows/Fonts/verdanab.ttf"),
}

PRESET_DEFAULTS = {
    "text": DEFAULT_TEXT,
    "font_name": DEFAULT_FONT_NAME,
    "fill_hex": DEFAULT_FILL,
    "stroke_hex": DEFAULT_STROKE,
    "x_percent": 50,
    "y_percent": 18,
    "size_percent": 8,
    "curve_percent": 0,
    "opacity_percent": 95,
    "bubble_overlay": False,
    "bubble_opacity_percent": 55,
    "bubble_density_percent": 55,
    "overlay_path": "",
    "overlay_x_percent": 50,
    "overlay_y_percent": 50,
    "overlay_size_percent": 25,
    "overlay_opacity_percent": 75,
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "lettering"


def resolve_font_path(font_name: str | None = None) -> Path:
    if font_name and FONT_OPTIONS.get(font_name, Path()).exists():
        return FONT_OPTIONS[font_name]
    for path in FONT_OPTIONS.values():
        if path.exists():
            return path
    return FONT_PATH


def load_font(size: int, font_name: str | None = None) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_path = resolve_font_path(font_name)
    if font_path.exists():
        return ImageFont.truetype(str(font_path), max(8, size))
    return ImageFont.load_default()


def hex_to_rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    cleaned = value.strip().lstrip("#")
    if len(cleaned) != 6:
        cleaned = DEFAULT_FILL.lstrip("#")
    try:
        red = int(cleaned[0:2], 16)
        green = int(cleaned[2:4], 16)
        blue = int(cleaned[4:6], 16)
    except ValueError:
        red, green, blue = 255, 255, 245
    return (red, green, blue, max(0, min(255, alpha)))


def build_output_path(
    source_path: str | Path,
    text: str,
    output_dir: str | Path | None = None,
    project_root: str | Path = ROOT,
) -> Path:
    source_path = Path(source_path)
    image_id = re.split(r"[_-]", source_path.stem, maxsplit=1)[0]
    if output_dir:
        target_dir = Path(output_dir)
    else:
        target_dir = Path(project_root) / "exports" / "shopify" / "images" / image_id
    return target_dir / f"{source_path.stem}-{slugify(text)}-lettered.png"


def make_project_relative(path: str | Path, project_root: str | Path = ROOT) -> str:
    if not path:
        return ""
    source = Path(path)
    try:
        return source.resolve().relative_to(Path(project_root).resolve()).as_posix()
    except ValueError:
        return str(path)


def resolve_project_path(path: str | Path, project_root: str | Path = ROOT) -> Path:
    source = Path(path)
    if source.is_absolute():
        return source
    return Path(project_root) / source


def normalize_preset_paths(settings: dict, project_root: str | Path = ROOT) -> dict:
    normalized = dict(settings)
    normalized["overlay_path"] = make_project_relative(normalized.get("overlay_path", ""), project_root)
    return normalized


def save_preset(path: str | Path, settings: dict, project_root: str | Path = ROOT) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = normalize_preset_paths({**PRESET_DEFAULTS, **settings}, project_root)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_preset(path: str | Path, project_root: str | Path = ROOT) -> dict:
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    settings = {**PRESET_DEFAULTS, **{key: data[key] for key in PRESET_DEFAULTS if key in data}}
    return normalize_preset_paths(settings, project_root)


def text_size(text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def curved_layout_width(text: str, font: ImageFont.ImageFont) -> int:
    spacing = max(1, font.size // 9)
    widths = [max(1, text_size(char, font)[0]) for char in text]
    return sum(widths) + max(0, len(widths) - 1) * spacing


def fit_font_to_width(
    text: str,
    requested_size: int,
    image_width: int,
    font_name: str | None = None,
    max_width_percent: float = 0.9,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_size = max(8, requested_size)
    max_width = image_width * max_width_percent
    font = load_font(font_size, font_name)
    width = max(text_size(text, font)[0], curved_layout_width(text, font))
    while width > max_width and font_size > 8:
        font_size -= 2
        font = load_font(font_size, font_name)
        width = max(text_size(text, font)[0], curved_layout_width(text, font))
    return font


def apply_bubbles_overlay(
    image: Image.Image,
    opacity_percent: int = 55,
    density_percent: int = 55,
) -> Image.Image:
    width, height = image.size
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    alpha_scale = max(0, min(100, opacity_percent)) / 100
    count = max(4, int((width * height / 90000) * max(10, density_percent) / 10))
    for index in range(count):
        x = int((width * ((index * 37) % 101)) / 100)
        y = int((height * ((index * 61 + 17) % 101)) / 100)
        radius = max(5, int(min(width, height) * (0.006 + ((index % 5) * 0.002))))
        alpha = int((58 + (index % 4) * 18) * alpha_scale)
        outline = (235, 255, 255, alpha)
        highlight = (255, 255, 255, int(alpha * 0.65))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=outline, width=max(1, radius // 5))
        draw.ellipse(
            (x - radius // 3, y - radius // 3, x - radius // 8, y - radius // 8),
            fill=highlight,
        )
    return Image.alpha_composite(image, layer)


def apply_image_overlay(
    image: Image.Image,
    overlay_path: str | Path,
    x_percent: int = 50,
    y_percent: int = 50,
    size_percent: int = 25,
    opacity_percent: int = 75,
) -> Image.Image:
    overlay = Image.open(overlay_path).convert("RGBA")
    target_width = max(1, int(image.size[0] * max(1, size_percent) / 100))
    ratio = target_width / overlay.size[0]
    target_height = max(1, int(overlay.size[1] * ratio))
    overlay = overlay.resize((target_width, target_height), Image.Resampling.LANCZOS)
    if opacity_percent < 100:
        alpha = overlay.getchannel("A").point(lambda value: int(value * max(0, opacity_percent) / 100))
        overlay.putalpha(alpha)
    x = int(image.size[0] * x_percent / 100 - overlay.size[0] / 2)
    y = int(image.size[1] * y_percent / 100 - overlay.size[1] / 2)
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    layer.alpha_composite(overlay, (x, y))
    return Image.alpha_composite(image, layer)


def draw_straight_text(
    layer: Image.Image,
    text: str,
    center: tuple[float, float],
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    stroke_fill: tuple[int, int, int, int],
    stroke_width: int,
) -> None:
    draw = ImageDraw.Draw(layer)
    width, height = text_size(text, font)
    draw.text(
        (center[0] - width / 2, center[1] - height / 2),
        text,
        font=font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def draw_curved_text(
    layer: Image.Image,
    text: str,
    center: tuple[float, float],
    font: ImageFont.ImageFont,
    curve_percent: int,
    fill: tuple[int, int, int, int],
    stroke_fill: tuple[int, int, int, int],
    stroke_width: int,
) -> None:
    chars = list(text)
    widths = [max(1, text_size(char, font)[0]) for char in chars]
    spacing = max(1, font.size // 9)
    total_width = sum(widths) + max(0, len(chars) - 1) * spacing
    half_width = max(1, total_width / 2)
    arc_strength = max(-100, min(100, curve_percent)) / 100
    arc_height = font.size * 1.2 * arc_strength
    max_rotation = 24 * arc_strength
    cursor = 0

    for char, char_width in zip(chars, widths):
        dx = -half_width + cursor + char_width / 2
        normalized = dx / half_width
        x = center[0] + dx
        y = center[1] + (normalized * normalized) * arc_height
        rotate_degrees = normalized * max_rotation

        bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox(
            (0, 0),
            char,
            font=font,
            stroke_width=stroke_width,
        )
        char_layer = Image.new(
            "RGBA",
            (bbox[2] - bbox[0] + 4, bbox[3] - bbox[1] + 4),
            (0, 0, 0, 0),
        )
        draw = ImageDraw.Draw(char_layer)
        draw.text(
            (2 - bbox[0], 2 - bbox[1]),
            char,
            font=font,
            fill=fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        rotated = char_layer.rotate(rotate_degrees, expand=True, resample=Image.Resampling.BICUBIC)
        layer.alpha_composite(rotated, (int(x - rotated.width / 2), int(y - rotated.height / 2)))
        cursor += char_width + spacing


def render_lettering(
    image_path: str | Path,
    output_path: str | Path,
    text: str,
    x_percent: int = 50,
    y_percent: int = 18,
    size_percent: int = 8,
    curve_percent: int = 0,
    opacity_percent: int = 95,
    font_name: str = "Arial Bold",
    fill_hex: str = DEFAULT_FILL,
    stroke_hex: str = DEFAULT_STROKE,
    bubble_overlay: bool = False,
    bubble_opacity_percent: int = 55,
    bubble_density_percent: int = 55,
    overlay_path: str | Path | None = None,
    overlay_x_percent: int = 50,
    overlay_y_percent: int = 50,
    overlay_size_percent: int = 25,
    overlay_opacity_percent: int = 75,
) -> Path:
    image_path = Path(image_path)
    output_path = Path(output_path)
    image = Image.open(image_path).convert("RGBA")
    width, height = image.size
    font_size = max(12, int(min(width, height) * size_percent / 100))
    font = fit_font_to_width(text, font_size, width, font_name)
    alpha = int(255 * max(0, min(100, opacity_percent)) / 100)
    fill = hex_to_rgba(fill_hex, alpha)
    stroke_fill = hex_to_rgba(stroke_hex, min(220, alpha))
    stroke_width = max(1, font_size // 18)
    center = (width * x_percent / 100, height * y_percent / 100)

    output = image
    if bubble_overlay:
        output = apply_bubbles_overlay(output, bubble_opacity_percent, bubble_density_percent)
    if overlay_path:
        output = apply_image_overlay(
            output,
            overlay_path,
            overlay_x_percent,
            overlay_y_percent,
            overlay_size_percent,
            overlay_opacity_percent,
        )
    if text:
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        if abs(curve_percent) < 3:
            draw_straight_text(layer, text, center, font, fill, stroke_fill, stroke_width)
        else:
            draw_curved_text(layer, text, center, font, curve_percent, fill, stroke_fill, stroke_width)
        output = Image.alpha_composite(output, layer)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.convert("RGB").save(output_path, quality=95)
    return output_path


class LetteringApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ScubaWithMe Lettering Tool")
        self.image_path: Path | None = None
        self.overlay_path: Path | None = None
        self.preview_image: Image.Image | None = None
        self.preview_photo: ImageTk.PhotoImage | None = None

        self.text_var = tk.StringVar(value=DEFAULT_TEXT)
        self.font_var = tk.StringVar(value=DEFAULT_FONT_NAME)
        self.fill_color = DEFAULT_FILL
        self.stroke_color = DEFAULT_STROKE
        self.x_var = tk.IntVar(value=50)
        self.y_var = tk.IntVar(value=18)
        self.size_var = tk.IntVar(value=8)
        self.curve_var = tk.IntVar(value=0)
        self.opacity_var = tk.IntVar(value=95)
        self.bubble_var = tk.BooleanVar(value=False)
        self.bubble_opacity_var = tk.IntVar(value=55)
        self.bubble_density_var = tk.IntVar(value=55)
        self.overlay_x_var = tk.IntVar(value=50)
        self.overlay_y_var = tk.IntVar(value=50)
        self.overlay_size_var = tk.IntVar(value=25)
        self.overlay_opacity_var = tk.IntVar(value=75)

        self.build_ui()

    def build_ui(self) -> None:
        controls_canvas = tk.Canvas(self.root, width=320, bg=self.root.cget("bg"), highlightthickness=0)
        controls_scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=controls_canvas.yview)
        controls_canvas.configure(yscrollcommand=controls_scrollbar.set)
        controls_canvas.pack(side=tk.LEFT, fill=tk.Y)
        controls_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        controls = tk.Frame(controls_canvas, padx=10, pady=10)
        controls_window = controls_canvas.create_window((0, 0), window=controls, anchor="nw")

        def update_scroll_region(_event: tk.Event) -> None:
            controls_canvas.configure(scrollregion=controls_canvas.bbox("all"))

        def update_controls_width(event: tk.Event) -> None:
            controls_canvas.itemconfigure(controls_window, width=event.width)

        def on_mousewheel(event: tk.Event) -> None:
            controls_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        controls.bind("<Configure>", update_scroll_region)
        controls_canvas.bind("<Configure>", update_controls_width)
        controls_canvas.bind_all("<MouseWheel>", on_mousewheel)

        tk.Button(controls, text="Choose Image", command=self.choose_image).pack(fill=tk.X)
        self.image_label = tk.Label(controls, text="No image selected", wraplength=260, justify=tk.LEFT)
        self.image_label.pack(anchor="w", pady=(4, 10))

        tk.Label(controls, text="Lettering").pack(anchor="w", pady=(14, 2))
        entry = tk.Entry(controls, textvariable=self.text_var, width=34)
        entry.pack(fill=tk.X)
        entry.bind("<KeyRelease>", lambda _event: self.refresh_preview())

        tk.Label(controls, text="Font").pack(anchor="w", pady=(8, 2))
        font_menu = ttk.Combobox(
            controls,
            textvariable=self.font_var,
            values=list(FONT_OPTIONS.keys()),
            state="readonly",
        )
        font_menu.pack(fill=tk.X)
        font_menu.bind("<<ComboboxSelected>>", lambda _event: self.refresh_preview())

        color_frame = tk.Frame(controls)
        color_frame.pack(fill=tk.X, pady=(8, 2))
        self.fill_button = tk.Button(color_frame, text="Text Color", command=self.choose_fill_color)
        self.fill_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 3))
        self.stroke_button = tk.Button(color_frame, text="Outline Color", command=self.choose_stroke_color)
        self.stroke_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(3, 0))

        preset_frame = tk.Frame(controls)
        preset_frame.pack(fill=tk.X, pady=(6, 10))
        for phrase in ("The Original Chill Diver", "Just Keep Drifting", "ScubaWithMe"):
            tk.Button(
                preset_frame,
                text=phrase,
                command=lambda value=phrase: self.set_text(value),
            ).pack(fill=tk.X, pady=1)

        preset_actions = tk.LabelFrame(controls, text="Presets", padx=8, pady=6)
        preset_actions.pack(fill=tk.X, pady=(4, 10))
        tk.Button(preset_actions, text="Save Preset", command=self.save_preset_file).pack(
            side=tk.LEFT,
            expand=True,
            fill=tk.X,
            padx=(0, 3),
        )
        tk.Button(preset_actions, text="Load Preset", command=self.load_preset_file).pack(
            side=tk.LEFT,
            expand=True,
            fill=tk.X,
            padx=(3, 0),
        )

        self.add_slider(controls, "X position", self.x_var, -50, 150)
        self.add_slider(controls, "Y position", self.y_var, -50, 150)
        self.add_slider(controls, "Size", self.size_var, 1, 45)
        self.add_slider(controls, "Curve", self.curve_var, -200, 200)
        self.add_slider(controls, "Opacity", self.opacity_var, 0, 100)

        overlay_box = tk.LabelFrame(controls, text="Overlays", padx=8, pady=6)
        overlay_box.pack(fill=tk.X, pady=(12, 0))
        tk.Checkbutton(
            overlay_box,
            text="Add bubbles",
            variable=self.bubble_var,
            command=self.refresh_preview,
        ).pack(anchor="w")
        self.add_slider(overlay_box, "Bubble opacity", self.bubble_opacity_var, 0, 100)
        self.add_slider(overlay_box, "Bubble density", self.bubble_density_var, 1, 200)
        tk.Button(overlay_box, text="Choose Overlay Image", command=self.choose_overlay).pack(fill=tk.X, pady=(8, 0))
        tk.Button(overlay_box, text="Clear Overlay Image", command=self.clear_overlay).pack(fill=tk.X, pady=(3, 0))
        self.overlay_label = tk.Label(overlay_box, text="No overlay image", wraplength=240, justify=tk.LEFT)
        self.overlay_label.pack(anchor="w", pady=(4, 0))
        self.add_slider(overlay_box, "Overlay X", self.overlay_x_var, -100, 200)
        self.add_slider(overlay_box, "Overlay Y", self.overlay_y_var, -100, 200)
        self.add_slider(overlay_box, "Overlay size", self.overlay_size_var, 1, 250)
        self.add_slider(overlay_box, "Overlay opacity", self.overlay_opacity_var, 0, 100)

        tk.Button(controls, text="Save PNG", command=self.save_image).pack(fill=tk.X, pady=(14, 0))

        self.canvas = tk.Canvas(self.root, width=820, height=720, bg="#142833", highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas.create_text(
            410,
            360,
            text="Choose an image to start",
            fill="#dceff5",
            font=("Arial", 18, "bold"),
        )

    def add_slider(self, parent: tk.Widget, label: str, variable: tk.IntVar, low: int, high: int) -> None:
        tk.Label(parent, text=label).pack(anchor="w", pady=(8, 0))
        tk.Scale(
            parent,
            from_=low,
            to=high,
            orient=tk.HORIZONTAL,
            variable=variable,
            command=lambda _value: self.refresh_preview(),
        ).pack(fill=tk.X)

    def set_text(self, value: str) -> None:
        self.text_var.set(value)
        if value == "ScubaWithMe":
            self.size_var.set(max(self.size_var.get(), 10))
        self.refresh_preview()

    def collect_preset_settings(self) -> dict:
        return {
            "text": self.text_var.get(),
            "font_name": self.font_var.get(),
            "fill_hex": self.fill_color,
            "stroke_hex": self.stroke_color,
            "x_percent": self.x_var.get(),
            "y_percent": self.y_var.get(),
            "size_percent": self.size_var.get(),
            "curve_percent": self.curve_var.get(),
            "opacity_percent": self.opacity_var.get(),
            "bubble_overlay": self.bubble_var.get(),
            "bubble_opacity_percent": self.bubble_opacity_var.get(),
            "bubble_density_percent": self.bubble_density_var.get(),
            "overlay_path": str(self.overlay_path) if self.overlay_path else "",
            "overlay_x_percent": self.overlay_x_var.get(),
            "overlay_y_percent": self.overlay_y_var.get(),
            "overlay_size_percent": self.overlay_size_var.get(),
            "overlay_opacity_percent": self.overlay_opacity_var.get(),
        }

    def apply_preset_settings(self, settings: dict) -> None:
        self.text_var.set(settings["text"])
        self.font_var.set(settings["font_name"] if settings["font_name"] in FONT_OPTIONS else DEFAULT_FONT_NAME)
        self.fill_color = settings["fill_hex"]
        self.stroke_color = settings["stroke_hex"]
        self.x_var.set(settings["x_percent"])
        self.y_var.set(settings["y_percent"])
        self.size_var.set(settings["size_percent"])
        self.curve_var.set(settings["curve_percent"])
        self.opacity_var.set(settings["opacity_percent"])
        self.bubble_var.set(settings["bubble_overlay"])
        self.bubble_opacity_var.set(settings["bubble_opacity_percent"])
        self.bubble_density_var.set(settings["bubble_density_percent"])
        overlay_path = resolve_project_path(settings["overlay_path"]) if settings["overlay_path"] else None
        self.overlay_path = overlay_path if overlay_path and overlay_path.exists() else None
        self.overlay_label.config(text=self.overlay_path.name if self.overlay_path else "No overlay image")
        self.overlay_x_var.set(settings["overlay_x_percent"])
        self.overlay_y_var.set(settings["overlay_y_percent"])
        self.overlay_size_var.set(settings["overlay_size_percent"])
        self.overlay_opacity_var.set(settings["overlay_opacity_percent"])
        self.refresh_preview()

    def save_preset_file(self) -> None:
        DEFAULT_PRESET_DIR.mkdir(parents=True, exist_ok=True)
        filename = filedialog.asksaveasfilename(
            initialdir=DEFAULT_PRESET_DIR,
            initialfile=f"{slugify(self.text_var.get()) or 'lettering'}-preset.json",
            title="Save preset",
            defaultextension=".json",
            filetypes=(("JSON preset", "*.json"), ("All files", "*.*")),
        )
        if filename:
            path = save_preset(filename, self.collect_preset_settings())
            messagebox.showinfo("Preset saved", f"Saved:\n{path}")

    def load_preset_file(self) -> None:
        DEFAULT_PRESET_DIR.mkdir(parents=True, exist_ok=True)
        filename = filedialog.askopenfilename(
            initialdir=DEFAULT_PRESET_DIR,
            title="Load preset",
            filetypes=(("JSON preset", "*.json"), ("All files", "*.*")),
        )
        if not filename:
            return
        try:
            settings = load_preset(filename)
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("Preset error", f"Could not load preset:\n{exc}")
            return
        self.apply_preset_settings(settings)

    def choose_fill_color(self) -> None:
        color = colorchooser.askcolor(color=self.fill_color, title="Choose text color")[1]
        if color:
            self.fill_color = color
            self.refresh_preview()

    def choose_stroke_color(self) -> None:
        color = colorchooser.askcolor(color=self.stroke_color, title="Choose outline color")[1]
        if color:
            self.stroke_color = color
            self.refresh_preview()

    def choose_image(self) -> None:
        filename = filedialog.askopenfilename(
            initialdir=DEFAULT_IMAGE_DIR,
            title="Choose image",
            filetypes=(("Image files", "*.png *.jpg *.jpeg *.tif *.tiff"), ("All files", "*.*")),
        )
        if filename:
            self.load_image(Path(filename))

    def choose_overlay(self) -> None:
        filename = filedialog.askopenfilename(
            initialdir=DEFAULT_OVERLAY_DIR,
            title="Choose overlay image",
            filetypes=(("Image files", "*.png *.jpg *.jpeg *.tif *.tiff"), ("All files", "*.*")),
        )
        if filename:
            self.overlay_path = Path(filename)
            self.overlay_label.config(text=self.overlay_path.name)
            self.refresh_preview()

    def clear_overlay(self) -> None:
        self.overlay_path = None
        self.overlay_label.config(text="No overlay image")
        self.refresh_preview()

    def load_image(self, path: Path) -> None:
        self.image_path = path
        self.preview_image = Image.open(path).convert("RGBA")
        self.image_label.config(text=path.name)
        self.refresh_preview()

    def refresh_preview(self) -> None:
        if self.preview_image is None:
            return
        rendered = self.render_to_image(self.preview_image)
        rendered.thumbnail((820, 720), Image.Resampling.LANCZOS)
        self.preview_photo = ImageTk.PhotoImage(rendered)
        self.canvas.delete("all")
        self.canvas.create_image(410, 360, image=self.preview_photo, anchor=tk.CENTER)

    def render_to_image(self, image: Image.Image) -> Image.Image:
        width, height = image.size
        font_size = max(12, int(min(width, height) * self.size_var.get() / 100))
        font = fit_font_to_width(self.text_var.get().strip(), font_size, width, self.font_var.get())
        center = (width * self.x_var.get() / 100, height * self.y_var.get() / 100)
        alpha = int(255 * self.opacity_var.get() / 100)
        fill = hex_to_rgba(self.fill_color, alpha)
        stroke_fill = hex_to_rgba(self.stroke_color, min(220, alpha))
        stroke_width = max(1, font_size // 18)
        text = self.text_var.get().strip()
        output = image
        if self.bubble_var.get():
            output = apply_bubbles_overlay(output, self.bubble_opacity_var.get(), self.bubble_density_var.get())
        if self.overlay_path:
            output = apply_image_overlay(
                output,
                self.overlay_path,
                self.overlay_x_var.get(),
                self.overlay_y_var.get(),
                self.overlay_size_var.get(),
                self.overlay_opacity_var.get(),
            )
        if text:
            layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
            if abs(self.curve_var.get()) < 3:
                draw_straight_text(layer, text, center, font, fill, stroke_fill, stroke_width)
            else:
                draw_curved_text(layer, text, center, font, self.curve_var.get(), fill, stroke_fill, stroke_width)
            output = Image.alpha_composite(output, layer)
        return output

    def save_image(self) -> None:
        if self.image_path is None:
            messagebox.showerror("No image", "Choose an image first.")
            return
        text = self.text_var.get().strip()
        if not text and not self.bubble_var.get() and self.overlay_path is None:
            messagebox.showerror("Nothing to save", "Add lettering, bubbles, or an overlay image first.")
            return
        output_path = build_output_path(self.image_path, text)
        render_lettering(
            self.image_path,
            output_path,
            text,
            self.x_var.get(),
            self.y_var.get(),
            self.size_var.get(),
            self.curve_var.get(),
            self.opacity_var.get(),
            self.font_var.get(),
            self.fill_color,
            self.stroke_color,
            self.bubble_var.get(),
            self.bubble_opacity_var.get(),
            self.bubble_density_var.get(),
            self.overlay_path,
            self.overlay_x_var.get(),
            self.overlay_y_var.get(),
            self.overlay_size_var.get(),
            self.overlay_opacity_var.get(),
        )
        messagebox.showinfo("Saved", f"Saved:\n{output_path}")


def main() -> None:
    root = tk.Tk()
    LetteringApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
