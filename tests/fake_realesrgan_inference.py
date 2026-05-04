from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-n")
    parser.add_argument("-i", dest="input_path", required=True)
    parser.add_argument("-o", dest="output_dir", required=True)
    parser.add_argument("--model_path")
    parser.add_argument("--outscale")
    parser.add_argument("--suffix", default="out")
    parser.add_argument("--tile")
    parser.add_argument("--fp32", action="store_true")
    args = parser.parse_args()

    sleep_seconds = float(os.environ.get("FAKE_ESRGAN_SLEEP", "0"))
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    input_stem = Path(args.input_path).stem
    output_path = output_dir / f"{input_stem}_{args.suffix}.png"
    output_path.write_text("fake output", encoding="utf-8")

    print(f"fake inference wrote {output_path}")

    if os.environ.get("FAKE_ESRGAN_FAIL") == "1":
        print("fake inference failing on request", file=sys.stderr)
        return 7

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
