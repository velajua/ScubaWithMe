import importlib.util
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scuba_lettering_tool.py"


def load_module():
    spec = importlib.util.spec_from_file_location("scuba_lettering_tool", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_render_lettering_preserves_size_and_changes_pixels(tmp_path):
    module = load_module()
    source = tmp_path / "source.png"
    output = tmp_path / "lettered.png"
    Image.new("RGB", (420, 300), (20, 110, 145)).save(source)

    result = module.render_lettering(
        image_path=source,
        output_path=output,
        text="JUST KEEP DRIFTING",
        x_percent=50,
        y_percent=24,
        size_percent=9,
        curve_percent=25,
        font_name="Arial Bold",
        fill_hex="#ffeeaa",
        stroke_hex="#001122",
    )

    assert result == output
    original = Image.open(source).convert("RGB")
    lettered = Image.open(output).convert("RGB")
    assert lettered.size == original.size
    assert ImageChops.difference(original, lettered).getbbox() is not None


def test_build_output_path_adds_lettered_suffix(tmp_path):
    module = load_module()
    source = tmp_path / "turtle1_realesrnet-2x-t07.png"
    source.write_bytes(b"placeholder")

    output = module.build_output_path(source, "The Original Chill Diver", project_root=tmp_path)

    assert output.parent == tmp_path / "exports" / "shopify" / "images" / "turtle1"
    assert output.name == "turtle1_realesrnet-2x-t07-the-original-chill-diver-lettered.png"


def test_build_output_path_uses_first_filename_part_for_collection_folder(tmp_path):
    module = load_module()
    source = tmp_path / "shark1-realesrnet-2x-final.png"
    source.write_bytes(b"placeholder")

    output = module.build_output_path(source, "Just Keep Drifting", project_root=tmp_path)

    assert output.parent == tmp_path / "exports" / "shopify" / "images" / "shark1"


def test_fitted_font_keeps_long_lettering_inside_canvas():
    module = load_module()

    font = module.fit_font_to_width("The Original Chill Diver", requested_size=80, image_width=420)
    width, _height = module.text_size("The Original Chill Diver", font)

    assert width <= 420 * 0.9


def test_render_with_bubbles_overlay_changes_pixels(tmp_path):
    module = load_module()
    source = tmp_path / "source.png"
    output = tmp_path / "bubbles.png"
    Image.new("RGB", (420, 300), (20, 110, 145)).save(source)

    module.render_lettering(
        image_path=source,
        output_path=output,
        text="",
        bubble_overlay=True,
        bubble_opacity_percent=80,
    )

    original = Image.open(source).convert("RGB")
    rendered = Image.open(output).convert("RGB")
    assert ImageChops.difference(original, rendered).getbbox() is not None


def test_render_with_overlay_image_resizes_and_positions(tmp_path):
    module = load_module()
    source = tmp_path / "source.png"
    overlay = tmp_path / "overlay.png"
    output = tmp_path / "overlayed.png"
    Image.new("RGB", (420, 300), (20, 110, 145)).save(source)
    Image.new("RGBA", (20, 20), (255, 255, 255, 180)).save(overlay)

    module.render_lettering(
        image_path=source,
        output_path=output,
        text="",
        overlay_path=overlay,
        overlay_x_percent=50,
        overlay_y_percent=50,
        overlay_size_percent=20,
        overlay_opacity_percent=70,
    )

    original = Image.open(source).convert("RGB")
    rendered = Image.open(output).convert("RGB")
    assert ImageChops.difference(original, rendered).getbbox() is not None


def test_render_accepts_expanded_slider_ranges(tmp_path):
    module = load_module()
    source = tmp_path / "source.png"
    output = tmp_path / "expanded.png"
    overlay = tmp_path / "overlay.png"
    Image.new("RGB", (420, 300), (20, 110, 145)).save(source)
    Image.new("RGBA", (20, 20), (255, 255, 255, 180)).save(overlay)

    module.render_lettering(
        image_path=source,
        output_path=output,
        text="ScubaWithMe",
        x_percent=125,
        y_percent=-10,
        size_percent=40,
        curve_percent=180,
        bubble_overlay=True,
        bubble_density_percent=180,
        overlay_path=overlay,
        overlay_x_percent=-25,
        overlay_y_percent=125,
        overlay_size_percent=175,
    )

    assert Image.open(output).size == (420, 300)


def test_save_and_load_preset_round_trip(tmp_path):
    module = load_module()
    preset = tmp_path / "drifting.json"
    overlay = tmp_path / "exports" / "shopify" / "brand" / "watermark-white.png"
    overlay.parent.mkdir(parents=True)
    overlay.write_bytes(b"placeholder")
    settings = {
        "text": "Just Keep Drifting",
        "font_name": "Segoe Print",
        "fill_hex": "#ffeeaa",
        "stroke_hex": "#001122",
        "x_percent": 45,
        "y_percent": 16,
        "size_percent": 12,
        "curve_percent": 25,
        "opacity_percent": 92,
        "bubble_overlay": True,
        "bubble_opacity_percent": 55,
        "bubble_density_percent": 120,
        "overlay_path": str(overlay),
        "overlay_x_percent": 52,
        "overlay_y_percent": 80,
        "overlay_size_percent": 35,
        "overlay_opacity_percent": 45,
    }

    module.save_preset(preset, settings)

    loaded = module.load_preset(preset, project_root=tmp_path)
    assert loaded == {**settings, "overlay_path": "exports/shopify/brand/watermark-white.png"}


def test_load_preset_applies_defaults_for_missing_fields(tmp_path):
    module = load_module()
    preset = tmp_path / "partial.json"
    preset.write_text('{"text": "Turtle Time", "size_percent": 20}', encoding="utf-8")

    settings = module.load_preset(preset)

    assert settings["text"] == "Turtle Time"
    assert settings["size_percent"] == 20
    assert settings["font_name"] == "ScubaWithMe Logo Script"
    assert settings["bubble_overlay"] is False


def test_load_preset_accepts_old_absolute_overlay_paths(tmp_path):
    module = load_module()
    overlay = tmp_path / "exports" / "shopify" / "brand" / "icon.png"
    overlay.parent.mkdir(parents=True)
    overlay.write_bytes(b"placeholder")
    preset = tmp_path / "absolute.json"
    preset.write_text(
        '{"overlay_path": "' + str(overlay).replace("\\", "\\\\") + '"}',
        encoding="utf-8",
    )

    settings = module.load_preset(preset, project_root=tmp_path)

    assert settings["overlay_path"] == "exports/shopify/brand/icon.png"
