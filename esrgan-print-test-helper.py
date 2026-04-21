#!/usr/bin/env python
"""Run Real-ESRGAN against the working image set.

This helper keeps the Windows .cmd wrapper simple and makes path handling
reliable while preserving the source folder structure in the ESRGAN output.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch Real-ESRGAN print-test exports.")
    parser.add_argument(
        "scale_positional",
        nargs="?",
        choices=["2", "3", "4"],
        help="Optional upscale ratio, kept so run-esrgan-print-tests.cmd 3 still works.",
    )
    parser.add_argument("--scale", default="2", choices=["2", "3", "4"], help="Upscale ratio.")
    parser.add_argument(
        "--input-root",
        default="working/current-png",
        help="Folder of source images to upscale. Defaults to working/current-png.",
    )
    parser.add_argument(
        "--output-root",
        default="exports/print-tests/ESRGAN",
        help="Folder where ESRGAN outputs are written.",
    )
    parser.add_argument(
        "--descriptive-names",
        action="store_true",
        help="Append model and scale to output filenames instead of preserving source filenames.",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        help=(
            "Only process relative paths matching this path segment, path prefix, or glob. "
            "May be repeated, for example --only fish1 --only template-01-natural-print."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional maximum number of new images to create. Useful for smoke tests.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show planned work without running ESRGAN.")
    parser.add_argument(
        "--tile",
        default="128",
        help="Real-ESRGAN tile size. Defaults to 128 to avoid auto-tiling artifacts on this Windows/Vulkan setup.",
    )
    parser.add_argument(
        "--no-rgb-preflight",
        action="store_true",
        help="Skip the RGB input conversion preflight. Not recommended for the current PNG photo set.",
    )
    return parser.parse_args()


def matches_filters(path: Path, filters: list[str]) -> bool:
    if not filters:
        return True

    rel = path.as_posix().lower()
    segments = [part.lower() for part in path.parts]
    for raw_filter in filters:
        value = raw_filter.replace("\\", "/").lower()
        if any(char in value for char in "*?[]"):
            if fnmatch.fnmatch(rel, value):
                return True
        elif "/" in value:
            if rel == value or rel.startswith(f"{value}/"):
                return True
        elif value in segments:
            return True
    return False


def prepare_input(src: Path, input_root: Path, runtime_root: Path, *, rgb_preflight: bool) -> Path:
    """Return a Real-ESRGAN-safe input file.

    The portable Vulkan runner can fragment RGBA PNGs on some GPUs. Converting
    photo inputs to RGB keeps the image geometry stable and is fine for this
    underwater photo workflow, where alpha is not meaningful product data.
    """

    if not rgb_preflight:
        return src

    rel = src.relative_to(input_root)
    prepared = runtime_root / rel.with_suffix(".png")
    prepared.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(src) as image:
        image.convert("RGB").save(prepared)

    return prepared


def main() -> int:
    args = parse_args()
    scale = args.scale_positional or args.scale
    project_root = Path(__file__).resolve().parent
    exe = project_root / "tools" / "realesrgan-ncnn-vulkan.exe"
    model_dir = project_root / "tools" / "models"
    input_root = (project_root / args.input_root).resolve()
    output_root = (project_root / args.output_root).resolve()
    runtime_root = output_root.parent / "ESRGAN-runtime"
    log_dir = project_root / "notes"
    log_file = log_dir / "esrgan-print-test.log"

    model = os.environ.get("ESRGAN_MODEL", "realesrgan-x4plus")
    overwrite = env_flag("ESRGAN_OVERWRITE")

    if not exe.exists():
        print(f"Missing Real-ESRGAN executable: {exe}")
        print("See notes/esrgan-print-test-workflow.md for setup steps.")
        return 1

    if not input_root.exists():
        print(f"Missing input folder: {input_root}")
        return 1

    output_root.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    sources = sorted(
        path
        for path in input_root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
        and matches_filters(path.relative_to(input_root), args.only)
    )

    created = 0
    skipped = 0
    failed = 0

    with log_file.open("w", encoding="utf-8") as log:
        log.write("Real-ESRGAN print-test run\n")
        log.write(f"Input: {input_root}\n")
        log.write(f"Output: {output_root}\n")
        log.write(f"Model: {model}\n")
        log.write(f"Scale: {scale}x\n")
        log.write(f"Tile: {args.tile}\n")
        log.write(f"RGB preflight: {not args.no_rgb_preflight}\n")
        log.write(f"Overwrite: {overwrite}\n\n")

        if args.dry_run:
            print(f"Dry run: {len(sources)} matching source image(s).")
            log.write(f"DRY-RUN matches={len(sources)}\n")
            for src in sources:
                rel = src.relative_to(input_root)
                dest_name = (
                    f"{src.stem}-esrgan-{model}-{scale}x.png" if args.descriptive_names else f"{src.stem}.png"
                )
                dest = output_root / rel.parent / dest_name
                print(f"{rel} -> {dest.relative_to(output_root)}")
                log.write(f"DRY-RUN {src} -> {dest}\n")
            return 0

        for src in sources:
            rel = src.relative_to(input_root)
            dest_name = f"{src.stem}-esrgan-{model}-{scale}x.png" if args.descriptive_names else f"{src.stem}.png"
            dest = output_root / rel.parent / dest_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            temp_dest = runtime_root / "_outputs" / rel.parent / dest_name
            temp_dest.parent.mkdir(parents=True, exist_ok=True)

            if dest.exists() and not overwrite:
                skipped += 1
                print(f"Skipping existing: {rel}")
                log.write(f"SKIP {src}\n")
                continue

            if args.limit and created >= args.limit:
                log.write(f"LIMIT-STOP after {created} created image(s)\n")
                break

            print(f"Upscaling: {rel}")
            log.write(f"RUN {src} -> {dest}\n")
            log.flush()
            prepared_src = prepare_input(
                src,
                input_root,
                runtime_root,
                rgb_preflight=not args.no_rgb_preflight,
            )

            command = [
                str(exe),
                "-i",
                str(prepared_src),
                "-o",
                str(temp_dest),
                "-n",
                model,
                "-s",
                scale,
                "-t",
                args.tile,
                "-f",
                "png",
                "-m",
                str(model_dir),
            ]

            temp_dest.unlink(missing_ok=True)
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)
            if result.returncode:
                failed += 1
                log.write(f"FAIL {src} exit={result.returncode}\n")
                print(f"Failed: {rel}")
            else:
                if not temp_dest.exists() or temp_dest.stat().st_size == 0:
                    failed += 1
                    log.write(f"FAIL {src} missing temporary output {temp_dest}\n")
                    print(f"Failed: {rel}")
                    continue
                dest.unlink(missing_ok=True)
                temp_dest.replace(dest)
                created += 1

    print()
    print("Real-ESRGAN run complete.")
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
    print(f"Log: {log_file}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
