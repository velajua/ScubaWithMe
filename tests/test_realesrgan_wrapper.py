from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WRAPPER = ROOT / "run-realesrgan-python.cmd"
FAKE_INFERENCE = ROOT / "tests" / "fake_realesrgan_inference.py"


class RealEsrganWrapperTests(unittest.TestCase):
    def run_wrapper(self, *, fail: bool = False) -> tuple[subprocess.CompletedProcess[str], float, Path, Path]:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)

        temp_root = Path(tempdir.name)
        input_path = temp_root / "shark3.png"
        model_path = temp_root / "fake-model.pth"
        output_dir = temp_root / "output"
        log_dir = temp_root / "logs"

        input_path.write_text("fake image", encoding="utf-8")
        model_path.write_text("fake model", encoding="utf-8")

        env = os.environ.copy()
        env["PY_ESRGAN_PYTHON_EXE"] = sys.executable
        env["PY_ESRGAN_INFERENCE"] = str(FAKE_INFERENCE)
        env["PY_ESRGAN_MODEL_PATH"] = str(model_path)
        env["PY_ESRGAN_OUTPUT"] = str(output_dir)
        env["PY_ESRGAN_SUFFIX"] = "test-suffix"
        env["PY_ESRGAN_LOG_DIR"] = str(log_dir)
        env["FAKE_ESRGAN_SLEEP"] = "2"
        if fail:
            env["FAKE_ESRGAN_FAIL"] = "1"

        start = time.monotonic()
        result = subprocess.run(
            ["cmd", "/c", str(WRAPPER), str(input_path)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
        elapsed = time.monotonic() - start
        output_path = output_dir / "shark3_test-suffix.png"
        log_path = log_dir / "shark3.log"
        return result, elapsed, output_path, log_path

    def test_wrapper_waits_and_writes_per_image_log(self) -> None:
        result, elapsed, output_path, log_path = self.run_wrapper()

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertGreaterEqual(elapsed, 1.8, msg=f"Wrapper returned too early: {elapsed}")
        self.assertTrue(output_path.exists(), msg="Expected output file was not created")
        self.assertTrue(log_path.exists(), msg="Expected per-image log file was not created")
        self.assertIn("fake inference wrote", log_path.read_text(encoding="utf-8"))

    def test_wrapper_propagates_inference_failure(self) -> None:
        result, _, output_path, log_path = self.run_wrapper(fail=True)

        self.assertNotEqual(result.returncode, 0, msg="Wrapper should return a failure code")
        self.assertTrue(output_path.exists(), msg="Fake inference should still write its output before failing")
        self.assertTrue(log_path.exists(), msg="Expected failure log file was not created")


if __name__ == "__main__":
    unittest.main()
