# RealESRGAN Wrapper Plan

## Goal

Make the RealESRGAN batch wrapper reliable for long-running single-image jobs and easier to trace with per-input logs.

## Approach

- Add a lightweight regression harness around `run-realesrgan-python.cmd`
- Support runtime overrides for testing and controlled local runs
- Write deterministic per-input log files
- Keep the documented CLI entrypoint unchanged

## Planned work

### Task 1: Add a regression harness for wrapper behavior

Files:

- `tests/test_realesrgan_wrapper.py`
- `tests/fake_realesrgan_inference.py`

Expected checks:

- wrapper waits for a deliberate sleep instead of returning early
- wrapper writes an output file
- wrapper creates an image-specific log
- wrapper returns nonzero when the fake inference fails

### Task 2: Patch the wrapper

Target file:

- `run-realesrgan-python.cmd`

Changes needed:

- accept runtime overrides
- derive a safe image stem from the input path
- write a per-input log file
- force the launched process to stay attached until completion

### Task 3: Verify on current images

Run the wrapper on:

- `working/fish13.png`
- `working/fish14.png`
- `working/shark3.png`
- `working/shark4.png`

Confirm:

- matching `*_realesrnet-2x.png` outputs appear under `exports/print-tests/ESRGAN-pytorch-RealESRNet/`
- each image has its own log file under `.realesrgan-runtime/logs/`
