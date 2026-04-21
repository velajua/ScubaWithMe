from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = ROOT / "working" / "current-png"
DEFAULT_OUTPUT_ROOT = ROOT / "exports" / "print-tests" / "final-template-comparison"
LOG_DIR = ROOT / "notes"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}


@dataclass(frozen=True)
class Template:
    path: Path
    label: str
    output_folder: str
    output_suffix: str


TEMPLATES = [
    Template(
        path=ROOT / "workflows" / "scubawithme-template-01-natural-print-prep.chn",
        label="template-01-natural-print-prep",
        output_folder="template-01-natural-print",
        output_suffix="t01-natural-print-prep-3x",
    ),
    Template(
        path=ROOT / "workflows" / "scubawithme-template-02-clean-product-prep.chn",
        label="template-02-clean-product-prep",
        output_folder="template-02-clean-product",
        output_suffix="t02-clean-product-prep-4x",
    ),
    Template(
        path=ROOT / "workflows" / "scubawithme-template-03-vivid-reef-grade.chn",
        label="template-03-vivid-reef-grade",
        output_folder="template-03-vivid-reef",
        output_suffix="t03-vivid-reef-grade-3x",
    ),
]


def find_chainner() -> Path:
    env_path = os.environ.get("CHAINNER_EXE")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path

    path_from_path = shutil.which("chaiNNer.exe") or shutil.which("chainner")
    if path_from_path:
        return Path(path_from_path)

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        path = Path(local_app_data) / "chaiNNer" / "chaiNNer.exe"
        if path.exists():
            return path

    raise FileNotFoundError(
        "Could not find chaiNNer. Set CHAINNER_EXE to the full chaiNNer executable path."
    )


def chainner_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def image_stem(path: Path) -> str:
    return path.stem.lower().replace(" ", "-")


def find_node(chain: dict, schema_id: str) -> dict:
    matches = [
        node
        for node in chain["content"]["nodes"]
        if node.get("data", {}).get("schemaId") == schema_id
    ]
    if len(matches) != 1:
        raise ValueError(f"Expected one {schema_id} node, found {len(matches)}.")
    return matches[0]


def update_template(template: Template, image: Path, output_root: Path) -> Path:
    image = image.resolve()
    output_root = output_root.resolve()
    stem = image_stem(image)

    chain = json.loads(template.path.read_text(encoding="utf-8"))
    load_node = find_node(chain, "chainner:image:load")
    save_node = find_node(chain, "chainner:image:save")

    load_node["data"]["inputData"]["0"] = chainner_path(image)

    save_input = save_node["data"]["inputData"]
    save_input["1"] = chainner_path(output_root)
    save_input["2"] = f"{stem}/{template.output_folder}"
    save_input["3"] = f"{stem}-{template.output_suffix}"

    template.path.write_text(
        json.dumps(chain, separators=(",", ":")),
        encoding="utf-8",
    )
    return output_root / stem / template.output_folder / f"{stem}-{template.output_suffix}.png"


def update_all_templates(image: Path, output_root: Path) -> list[Path]:
    image = image.resolve()
    if not image.exists():
        raise FileNotFoundError(f"Image not found: {image}")
    if image.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError(f"Unsupported image extension: {image.suffix}")
    try:
        image.relative_to(ROOT)
    except ValueError:
        print(
            "Warning: this input is outside the project, so its absolute path must be written to the chaiNNer file.",
            file=sys.stderr,
        )

    outputs = []
    for template in TEMPLATES:
        outputs.append(update_template(template, image, output_root))
    return outputs


def output_is_stable(path: Path, checks: int = 3, interval: float = 1.0) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False

    size = path.stat().st_size
    for _ in range(checks):
        time.sleep(interval)
        if not path.exists():
            return False
        new_size = path.stat().st_size
        if new_size != size or new_size == 0:
            size = new_size
            continue
    return True


def stop_process_tree(pid: int) -> None:
    subprocess.run(
        ["taskkill", "/pid", str(pid), "/t", "/f"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def cleanup_chainner_backends() -> None:
    # The chaiNNer CLI can leave Electron and integrated Python backend
    # processes running after the chain is done. Clear them between batch items.
    subprocess.run(
        ["taskkill", "/im", "chaiNNer.exe", "/t", "/f"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    subprocess.run(
        [
            "wmic",
            "process",
            "where",
            "commandline like '%chaiNNer%resources%src%'",
            "delete",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def run_template(template: Template, image: Path, expected_output: Path) -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"chainner-{image_stem(image)}-{template.label}.log"

    if expected_output.exists():
        expected_output.unlink()

    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [str(find_chainner()), "run", str(template.path)],
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
        )

        deadline = time.monotonic() + 300
        while time.monotonic() < deadline:
            if output_is_stable(expected_output):
                stop_process_tree(process.pid)
                cleanup_chainner_backends()
                return 0

            time.sleep(1)

        stop_process_tree(process.pid)
        cleanup_chainner_backends()
        return 1


def run_for_image(image: Path, output_root: Path) -> list[Path]:
    outputs = update_all_templates(image, output_root)
    print(f"Updated templates for {image.name}")

    for template, output in zip(TEMPLATES, outputs):
        print(f"Running {template.label}...")
        code = run_template(template, image, output)
        if code != 0:
            raise RuntimeError(f"{template.label} exited with code {code}. Check notes logs.")

    return outputs


def iter_images(folder: Path) -> list[Path]:
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    images = [
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return sorted(images, key=lambda path: path.name.lower())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update and run ScubaWithMe chaiNNer final-product templates."
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Base output folder for generated print-test files.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    update = subparsers.add_parser("update", help="Update templates for one image.")
    update.add_argument("image", help="Image path to use as the chain input.")

    run_one = subparsers.add_parser("run-one", help="Update and run all templates for one image.")
    run_one.add_argument("image", help="Image path to process.")

    run_folder = subparsers.add_parser(
        "run-folder", help="Run all templates for every image in a folder."
    )
    run_folder.add_argument(
        "folder",
        nargs="?",
        default=str(DEFAULT_INPUT_DIR),
        help="Folder of images to process. Defaults to working/current-png.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = Path(args.output_root)

    try:
        if args.command == "update":
            outputs = update_all_templates(Path(args.image), output_root)
            print("Updated templates. Expected outputs:")
            for output in outputs:
                print(display_path(output))
            return 0

        if args.command == "run-one":
            outputs = run_for_image(Path(args.image), output_root)
            print("Finished. Review outputs:")
            for output in outputs:
                print(display_path(output))
            return 0

        if args.command == "run-folder":
            images = iter_images(Path(args.folder))
            if not images:
                print(f"No images found in {args.folder}")
                return 0

            print(f"Found {len(images)} image(s).")
            for image in images:
                outputs = run_for_image(image, output_root)
                for output in outputs:
                    print(display_path(output))
            print("Batch complete.")
            return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
