# RealESRNet + chaiNNer Workflow

This is the current ScubaWithMe print-test workflow.

```text
working/current-png/
-> PyTorch RealESRNet 2x
-> chaiNNer correction templates
-> manual visual review and tier decision
```

RealESRNet does the resolution/restoration step. chaiNNer does color, contrast, denoise, and finishing only. The chaiNNer templates should not enlarge the image again.

## Current Outputs

RealESRNet 2x outputs:

```text
exports/print-tests/ESRGAN-pytorch-RealESRNet/
```

chaiNNer corrected variants:

```text
exports/print-tests/chainner_from_realesrnet/<image-name>/<image-name>-tXX-variant.png
```

## Runtime Setup

The full Python/PyTorch Real-ESRGAN environment lives in ignored runtime state:

```text
.realesrgan-runtime/venv/
```

Model weights live in the ignored Real-ESRGAN clone:

```text
Real-ESRGAN/weights/RealESRNet_x4plus.pth
Real-ESRGAN/weights/RealESRGAN_x4plus.pth
```

Runtime logs are written under:

```text
.realesrgan-runtime/logs/
.chainner-runtime/logs/
```

These paths are ignored by git.

## Run RealESRNet

Run the current conservative restoration/upscale model over the working PNG folder:

```cmd
cmd /c "set PY_ESRGAN_MODEL=RealESRNet_x4plus&& set PY_ESRGAN_OUTPUT=exports\print-tests\ESRGAN-pytorch-RealESRNet&& set PY_ESRGAN_SUFFIX=realesrnet-2x&& run-realesrgan-python.cmd working\current-png"
```

Run one image:

```cmd
cmd /c "set PY_ESRGAN_MODEL=RealESRNet_x4plus&& set PY_ESRGAN_OUTPUT=exports\print-tests\ESRGAN-pytorch-RealESRNet&& set PY_ESRGAN_SUFFIX=realesrnet-2x&& run-realesrgan-python.cmd working\current-png\squid1.png"
```

The default scale is `2x`. Use larger scales only for selected images that survive visual inspection.

## Run chaiNNer Corrections

Run all correction templates over the RealESRNet outputs:

```cmd
cmd /c "python chainner-template-helper.py --output-root exports\print-tests\chainner_from_realesrnet run-folder exports\print-tests\ESRGAN-pytorch-RealESRNet"
```

Regenerate existing corrected outputs:

```cmd
cmd /c "python chainner-template-helper.py --output-root exports\print-tests\chainner_from_realesrnet run-folder exports\print-tests\ESRGAN-pytorch-RealESRNet --regenerate"
```

## Templates

- `template-01-natural-print`: moderate natural correction.
- `template-02-clean-product`: brighter product-style correction.
- `template-03-vivid-reef`: stylized high-impact correction; use cautiously for print.
- `template-04-subtle-esrgan-finish`: restrained post-ESRGAN finish intended to preserve the moody underwater look.
- `template-05-cinematic-deep-blue`: moody deep-blue grade with stronger contrast and sharper drama.
- `template-06-bright-product-pop`: high-key, brighter product-style grade with more saturation.
- `template-07-matte-dream-water`: soft, lower-contrast, denoised matte grade for atmospheric frames.
- `template-08-hard-detail-clarity`: aggressive detail/edge test for subjects that can survive sharpening.
- `template-09-warm-coral-recovery`: warmer, coral-forward grade that tests stronger red/orange recovery.

Normal `run-one` and `run-folder` executions use temporary runtime chains and should not rewrite the saved workflow templates.

Output layout is intentionally flat inside each image folder. Do not create per-template subfolders:

```text
exports/print-tests/chainner_from_realesrnet/
  squid1_realesrnet-2x/
    squid1_realesrnet-2x-t01-natural-print-corrected.png
    squid1_realesrnet-2x-t02-clean-product-corrected.png
    squid1_realesrnet-2x-t03-vivid-reef-corrected.png
    squid1_realesrnet-2x-t04-subtle-esrgan-finish-corrected.png
    squid1_realesrnet-2x-t05-cinematic-deep-blue-corrected.png
    squid1_realesrnet-2x-t06-bright-product-pop-corrected.png
    squid1_realesrnet-2x-t07-matte-dream-water-corrected.png
    squid1_realesrnet-2x-t08-hard-detail-clarity-corrected.png
    squid1_realesrnet-2x-t09-warm-coral-recovery-corrected.png
```

## Review Checklist

- Check eyes, skin/scales, coral, and sand for invented texture.
- Look for halos around fish edges, fins, antennae, and high-contrast reef shapes.
- Compare at crop level, not only full-frame.
- Reject outputs where the image looks more detailed but less believable.
- Prefer smaller print sizes until a real sample confirms the result.
