# Real-ESRGAN Print-Test Workflow

This workflow runs Real-ESRGAN first on the smaller working PNG images. The ESRGAN outputs can then be used as inputs for the chaiNNer print-prep templates.

Input folder:

```text
working/current-png/
```

Output folder:

```text
exports/print-tests/ESRGAN/
```

By default, output filenames preserve the original image names, for example:

```text
working/current-png/fish1.png
exports/print-tests/ESRGAN/fish1.png
```

The goal is comparison and print testing, not automatic print approval. ESRGAN can improve apparent resolution, but it can also invent animal detail, sharpen backscatter, create halos, or shift fine reef textures. Treat these outputs as candidates that still need visual inspection and sample-print judgment.

## Setup Used

The project root contains:

```text
Real-ESRGAN/
```

That is a clone of:

```text
https://github.com/xinntao/Real-ESRGAN
```

For local Windows runs, this workflow uses the official portable executable from the Real-ESRGAN releases:

```text
tools/realesrgan-ncnn-vulkan.exe
tools/models/
```

This avoids installing the full Python/PyTorch environment while still using Real-ESRGAN's released upscaling models.

## Run The Workflow

Default 2x pass:

```cmd
cmd /c run-esrgan-print-tests.cmd
```

3x pass:

```cmd
cmd /c run-esrgan-print-tests.cmd 3
```

4x pass:

```cmd
cmd /c run-esrgan-print-tests.cmd 4
```

The default is 2x because these source files are still small, but underwater detail can become artificial quickly. Use 3x or 4x only for selected images that survive visual inspection.

Important implementation detail:

- The helper converts inputs to RGB before calling Real-ESRGAN.
- The helper uses `--tile 128` by default instead of Real-ESRGAN's auto tile mode.
- This avoids fragmented/tile-scrambled output seen when the portable Vulkan runner processed the original `RGBA` PNGs on this Windows GPU path.

Prepared RGB inputs are temporary files written under:

```text
exports/print-tests/ESRGAN-runtime/
```

ESRGAN also writes each generated output to a temporary file under that runtime folder first, then replaces the final output only after the command succeeds. This avoids keeping a partial or stale final PNG if an upscale is interrupted.

Smoke test one new output:

```cmd
cmd /c run-esrgan-print-tests.cmd --limit 1
```

The workflow is resumable. Existing ESRGAN outputs are skipped unless overwrite mode is enabled, so it is safe to stop a long run and launch it again later.

Preview what would run without creating files:

```cmd
cmd /c run-esrgan-print-tests.cmd --dry-run
```

Run only one image group:

```cmd
cmd /c run-esrgan-print-tests.cmd --only fish1
```

For fuzzy matches, use a glob:

```cmd
cmd /c run-esrgan-print-tests.cmd --only "*vivid-reef*"
```

Run only the natural-print template across all images:

```cmd
cmd /c run-esrgan-print-tests.cmd --only template-01-natural-print
```

Run one selected image/template combination:

```cmd
cmd /c run-esrgan-print-tests.cmd --only fish1.png
```

If you want filenames that include model and scale instead of preserving the source filename:

```cmd
cmd /c run-esrgan-print-tests.cmd --only fish1.png --descriptive-names
```

To experiment with another tile size:

```cmd
cmd /c run-esrgan-print-tests.cmd --only fish1.png --tile 256
```

Do not use `--no-rgb-preflight` unless you are intentionally testing the Real-ESRGAN runner behavior. The current working PNGs are `RGBA`, and direct RGBA input produced broken image geometry during testing.

## Feeding ESRGAN Into chaiNNer

The chaiNNer helper can still run from the original working PNG images:

```cmd
cmd /c "python chainner-template-helper.py run-folder"
```

To run chaiNNer from the ESRGAN-upscaled images instead, pass the ESRGAN folder:

```cmd
cmd /c "python chainner-template-helper.py --output-root exports\print-tests\chainner_from_esrgan run-folder exports\print-tests\ESRGAN"
```

`run-folder` reads image files directly inside the folder. Nested comparison folders from older experiments are ignored.

## Optional Model Choice

Default model:

```text
realesrgan-x4plus
```

Alternative natural-image baseline:

```cmd
cmd /c "set ESRGAN_MODEL=realesrnet-x4plus&& run-esrgan-print-tests.cmd"
```

Use `realesrgan-x4plus` for sharper detail experiments. Try `realesrnet-x4plus` if the default model looks too crunchy, haloed, or artificial around fish edges and coral textures.

## Re-running

By default, existing ESRGAN outputs are skipped so previous comparisons are preserved.

To overwrite existing ESRGAN outputs:

```cmd
cmd /c "set ESRGAN_OVERWRITE=1&& run-esrgan-print-tests.cmd"
```

Run logs are written to:

```text
notes/esrgan-print-test.log
```

## Review Checklist

- Check eyes, skin/scales, coral, and sand for invented texture.
- Look for halos around fish edges, fins, antennae, and high-contrast reef shapes.
- Compare against the chaiNNer output at the same crop, not only zoomed out.
- Reject outputs where the image looks more detailed but less believable.
- Prefer smaller print sizes until a real sample confirms the result holds up.
