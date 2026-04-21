# chaiNNer Final Product Templates

These are comparison templates for turning one working underwater PNG into stronger product-test exports.

They are not final proof of print readiness. They are repeatable starting points for judging color grade, denoise strength, resize amount, and sharpening before we commit to a real ScubaWithMe product style.

## Input And Output

Default input folder:

```text
working/current-png/
```

Comparison output folder:

```text
exports/print-tests/final-template-comparison/
```

The chains save 16-bit PNG files so we keep more tonal room during review.

Use the helper script to change the input image and derived output names:

```cmd
cmd /c python chainner-template-helper.py update working\current-png\moray1.png
```

That updates all three `.chn` files so the load node points at `moray1.png` and the save nodes write under:

```text
exports/print-tests/final-template-comparison/moray1/
```

## Template 01: Natural Print Prep

Workflow:

```text
Load Image
-> Stretch Contrast, percentile 0.75, keep colors
-> Hue & Saturation, saturation +4, lightness +1
-> Brightness & Contrast, brightness +2, contrast +8
-> Denoise, low strength
-> Resize 300 percent, Lanczos
-> Unsharp Mask, radius 1.2, amount 0.45, threshold 2
-> Save 16-bit PNG
```

Use this as the baseline. It should feel underwater-real, with modest contrast and controlled sharpening.

Run:

```cmd
cmd /c ""%CHAINNER_EXE%" run "%CD%\workflows\scubawithme-template-01-natural-print-prep.chn" > "%CD%\notes\scubawithme-template-01-natural-print-prep.log" 2>&1"
```

Example output for `fish1.png`:

```text
exports/print-tests/final-template-comparison/fish1/template-01-natural-print/fish1-t01-natural-print-prep-3x.png
```

## Template 02: Clean Product Prep

Workflow:

```text
Load Image
-> Denoise, medium strength
-> Stretch Contrast, percentile 0.5, keep colors
-> Gamma 0.96
-> Hue & Saturation, saturation +6, lightness +2
-> Resize 400 percent, Lanczos
-> Unsharp Mask, radius 0.9, amount 0.35, threshold 3
-> Save 16-bit PNG
```

Use this when water noise, grain, or compression artifacts are the main risk. The tradeoff is possible texture smoothing, so inspect eyes, fish patterns, and coral detail at 100 percent.

Run:

```cmd
cmd /c ""%CHAINNER_EXE%" run "%CD%\workflows\scubawithme-template-02-clean-product-prep.chn" > "%CD%\notes\scubawithme-template-02-clean-product-prep.log" 2>&1"
```

Example output for `fish1.png`:

```text
exports/print-tests/final-template-comparison/fish1/template-02-clean-product/fish1-t02-clean-product-prep-4x.png
```

## Template 03: Vivid Reef Grade

Workflow:

```text
Load Image
-> Stretch Contrast, percentile 1.25, per-channel
-> Hue & Saturation, saturation +10, lightness +3
-> Brightness & Contrast, brightness +3, contrast +14
-> Gamma 0.92
-> Denoise, light strength
-> Resize 300 percent, Lanczos
-> Unsharp Mask, radius 1.5, amount 0.65, threshold 1
-> Save 16-bit PNG
```

Use this as the upper boundary for a punchier ScubaWithMe look. It may be useful for social or small products, but reject it if blues look neon, blacks crush, or fish/coral colors stop feeling real.

Run:

```cmd
cmd /c ""%CHAINNER_EXE%" run "%CD%\workflows\scubawithme-template-03-vivid-reef-grade.chn" > "%CD%\notes\scubawithme-template-03-vivid-reef-grade.log" 2>&1"
```

Example output for `fish1.png`:

```text
exports/print-tests/final-template-comparison/fish1/template-03-vivid-reef/fish1-t03-vivid-reef-grade-3x.png
```

## Run One Image

From the project root:

```cmd
cmd /c python chainner-template-helper.py run-one working\current-png\fish1.png
```

## Run A Folder

Run every supported image in `working/current-png/`:

```cmd
cmd /c python chainner-template-helper.py run-folder
```

Run a specific folder:

```cmd
cmd /c python chainner-template-helper.py run-folder working\current-png
```

## How To Compare

Check each output at fit-to-screen, 100 percent, and 200 percent.

Look for:

- believable animal detail
- eyes and patterns that still look photographic
- reduced water haze without fake contrast
- no obvious halos around fins, coral, or high-contrast edges
- no smeared scales or painted-looking texture
- no neon cyan/blue clipping
- enough final pixel size for the intended product

At the current source size, the templates create roughly:

```text
3x export: about 2541 x 2478 px
4x export: about 3388 x 3304 px
```

At 300 DPI, the 4x export is still only around 11.3 x 11.0 inches before cropping. That is a product-test candidate, not a promise of large-print readiness.
