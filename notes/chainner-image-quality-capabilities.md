# chaiNNer Image Quality Capabilities

Sources:

- Official site: https://chainner.app/
- CLI docs: https://github.com/chaiNNer-org/chaiNNer/wiki/05--CLI
- Nodes docs: https://github.com/chaiNNer-org/chaiNNer/wiki/03--Nodes
- Local install inspected through `%LOCALAPPDATA%\chaiNNer\`.

## What chaiNNer Is Good For

chaiNNer is a node-based image-processing tool. For ScubaWithMe, it is useful as a repeatable image lab:

- resize and export image batches
- create controlled brand backgrounds and gradients
- correct contrast and color casts
- denoise, sharpen, blur, crop, pad, and composite
- compare outputs with image metrics
- run AI upscaling models once model dependencies are installed

The official site describes chaiNNer as a visual node editor for image workflows with comprehensive processing, AI upscaling, batch processing, and CLI support. The CLI docs confirm that command-line mode runs saved `.chn` chains and can override text, number, file, and directory inputs.

## Already Working

Standard chaiNNer image operations are usable from CLI in this project today:

- deterministic resize/export
- stretch contrast
- hue/saturation and brightness/contrast grading
- gamma adjustment
- non-local-means denoise
- unsharp mask sharpening
- gradient image generation

Current product-test workflows:

```text
workflows/scubawithme-template-01-natural-print-prep.chn
workflows/scubawithme-template-02-clean-product-prep.chn
workflows/scubawithme-template-03-vivid-reef-grade.chn
```

These use deterministic resize, not AI upscaling.

## CLI Notes

Use this pattern:

```cmd
cmd /c ""%CHAINNER_EXE%" run "%CD%\workflows\CHAIN.chn" > "%CD%\notes\CHAIN.log" 2>&1"
```

Keep stdout/stderr redirected to a log file. chaiNNer 0.25.1 can hit an Electron console pipe issue when writing directly to the shell.

For real automation, create/save the workflow in the GUI, then use CLI overrides. The docs say overrides support:

- text inputs
- number inputs
- file inputs
- directory inputs

They do not support dropdowns, checkboxes, or generic inputs, so those should be fixed inside the saved chain.

## Useful Nodes For ScubaWithMe

### Resolution And Export

Installed nodes:

- `chainner:image:resize`
- `chainner:image:resize_to_side`
- `chainner:image:pad`
- `chainner:image:crop`
- `chainner:image:crop_to_content`
- `chainner:image:save`
- `chainner:image:load`
- `chainner:image:load_images`

Use cases:

- 2x or 4x resize tests
- social exports
- print-test exports
- fixed square crops
- padded art-print layouts
- batch processing folders

Important:

- Resize is not the same as AI super-resolution.
- Lanczos/Bicubic-style resizing is useful for proofing and layout tests.
- AI model upscaling is needed for true detail reconstruction, and must be checked for fake texture.

### Gradients And Brand Backgrounds

Installed node:

- `chainner:image:create_gradient`

Supported gradient styles:

- horizontal
- vertical
- diagonal
- radial
- conic

Use cases:

- ocean-blue product mockup backgrounds
- print preview backgrounds
- social story backgrounds
- brand palette experiments
- subtle catalog cards behind transparent cutouts

Rule:

- Gradients should support the photo, not replace it. ScubaWithMe should be photo-led.

### Color And Tone

Installed nodes:

- `chainner:image:brightness_and_contrast`
- `chainner:image:color_levels`
- `chainner:image:hue_and_saturation`
- `chainner:image:stretch_contrast`
- `chainner:image:gamma`
- `chainner:image:color_transfer`
- `chainner:image:average_color_fix`

Best underwater-photo uses:

- correct mild blue/green color cast
- recover contrast lost to water haze
- create consistent collection tone
- gently warm subjects without making them fake
- match an upscaled image back to its original colors

Risk:

- Underwater photos are easy to overcorrect. Avoid neon blues, crushed blacks, and oversaturated fish.

Suggested starting recipe:

1. `Stretch Contrast` with low percentile, keep colors on.
2. `Color Levels` for careful channel correction.
3. `Hue & Saturation` with small saturation changes only.
4. `Brightness & Contrast` for final mild adjustment.
5. Save as PNG or TIFF for review.

### Denoise And Sharpen

Installed nodes:

- `chainner:image:fast_nlmeans` / Denoise
- `chainner:image:sharpen` / Unsharp Mask
- `chainner:image:sharpen_hbf` / High Boost Filter
- blur nodes including box, gaussian, lens, median, and surface blur

Best uses:

- reduce noisy water/background regions
- gently sharpen animal eyes and edges after resize
- prepare cleaner social exports

Risk:

- Denoising can smear scales, skin, coral texture, and tiny detail.
- Sharpening can amplify backscatter and compression artifacts.

Suggested rule:

- Denoise before final sharpening.
- Sharpen after final size decision.
- Never judge sharpening only zoomed out.

### Cleanup And Backscatter

Installed nodes:

- `chainner:image:inpaint`
- `chainner:image:chroma_key`
- `chainner:image:alpha_matting`
- `chainner:image:fill_alpha`

Use cases:

- remove small distracting particles if a mask exists
- create cutouts or isolated subjects for merch/mockups
- test transparent-background artwork

Important:

- chaiNNer inpaint needs a mask. Masks are usually made outside chaiNNer.
- This can help with backscatter, but it is not a one-click underwater cleanup system.

### Composition And Product Prep

Installed nodes:

- stack images
- blend images
- add caption
- rotate
- flip
- shift
- crop/pad
- text as image

Use cases:

- contact sheets
- before/after comparisons
- image audit boards
- simple product/social layouts
- test captions or species labels

Rule:

- For Shopify product art, keep output files clean. Do not bake captions into artwork unless the product is intentionally typographic.

### Image Metrics And Statistics

Installed nodes:

- `chainner:image:image_metrics`
- `chainner:image:image_statistics`
- `chainner:image:generate_hash`

Use cases:

- compare two same-size variants using MSE, PSNR, SSIM
- estimate clipping or tonal range
- keep track of whether a chain changed an image unexpectedly

Limit:

- Metrics are not taste. They help detect drift, but final selection is visual.

## AI Upscaling Options

Installed model-backed paths:

- `chainner:pytorch:upscale_image`
- `chainner:ncnn:upscale_image`
- `chainner:onnx:upscale_image`
- `chainner:pytorch:guided_upscale`
- `chainner:pytorch:wavelet_color_fix`
- `chainner:image:average_color_fix`

Current local status from logs:

- Standard image dependencies installed successfully.
- NCNN, ONNX, PyTorch, Torch, and model packages are not fully installed yet.
- No Nvidia GPU was detected in chaiNNer logs.

Practical implication:

- Standard resize/color/denoise/sharpen workflows can run now.
- AI model upscaling needs additional setup and model selection.
- NCNN may be the best path to test first because chaiNNer describes NCNN as having broad GPU support through Vulkan, but we need to install/enable its dependency stack.

## Recommended ScubaWithMe Workflow

### Workflow 1: Brand Background Generator

Purpose:

- Generate ocean-toned gradients for social/mockup backgrounds.

Chain:

```text
Create Gradient -> Save Image
```

Fixed settings:

- 1600 x 2000 for vertical social
- 2400 x 2400 for square mockups
- radial or vertical gradient

Output:

```text
exports/social/backgrounds/
```

### Workflow 2: Deterministic Print-Test Resize

Purpose:

- Make non-AI 2x and 4x candidates for layout and print-size testing.

Chain:

```text
Load Image -> Resize -> optional Denoise -> optional Unsharp Mask -> Save Image
```

Output:

```text
exports/print-tests/chainner-resize/
```

Use for:

- comparing how far each image can be pushed before AI model setup
- Shopify mockup experiments

### Workflow 3: Underwater Color Correction

Purpose:

- Create tasteful “mint” color variants.

Chain:

```text
Load Image -> Stretch Contrast -> Color Levels -> Hue & Saturation -> Save Image
```

Output:

```text
exports/print-tests/color-corrected/
```

Suggested variants:

- natural
- slightly warmer subject
- stronger reef contrast

Reject:

- fake-looking water
- clipped highlights
- color casts that erase the underwater feeling

### Workflow 4: Before/After Contact Sheet

Purpose:

- Review original vs enhanced vs resized outputs quickly.

Chain:

```text
Load original + load variants -> Stack Images -> Add Caption -> Save Image
```

Output:

```text
exports/print-tests/contact-sheets/
```

### Workflow 5: AI Upscale Lab

Purpose:

- Test Real-ESRGAN/ESRGAN-style models through chaiNNer once dependencies are installed.

Possible chain:

```text
Load Image -> Load Model -> Upscale Image -> Average Color Fix or Wavelet Color Fix -> Save Image
```

Output:

```text
exports/print-tests/ai-upscale/
```

Review criteria:

- animal anatomy unchanged
- scales/eyes are believable
- no fake coral or invented detail
- original mood preserved
- print-size improvement is meaningful

## Next Practical Step

Build two GUI-saved chains:

1. `scubawithme-color-correct.chn`
2. `scubawithme-resize-export.chn`

Then copy override IDs for:

- input image path
- output directory
- output filename
- resize percentage, if exposed as a number input

After those are GUI-saved, CLI automation should be much cleaner and less fragile than hand-authored `.chn` files.
