# ScubaWithMe Notes Index

This folder holds working notes for the ScubaWithMe brand, image-quality pipeline, and print-on-demand preparation.

## Current structure

- `brand/`: active brand direction, asset usage, and implementation notes
- `workflows/`: workflow-specific plans and implementation notes
- `esrgan-print-test-workflow.md`: current RealESRNet 2x plus chaiNNer correction workflow
- `chainner-crispness-render-review.md`: visual review notes for chaiNNer crispness variants

## Brand notes

- `brand/design.md`: current logo direction and visual constraints
- `brand/assets.md`: exported brand assets and Shopify usage notes
- `brand/implementation-plan.md`: record of the first brand asset build
- `brand/README.md`: quick overview of the brand notes section

## Workflow helpers

- `run-realesrgan-python.cmd`: runs the local PyTorch Real-ESRGAN implementation
- `chainner-template-helper.py`: runs the saved chaiNNer templates through temporary runtime chains without rewriting tracked workflow files

## Workflow notes

- `workflows/realesrgan-wrapper-plan.md`: plan for making the RealESRGAN wrapper easier to test and trace

## Recommended Note Files To Add Next

- `image-audit.md`: per-image print readiness and visual quality notes.
- `brand-voice.md`: caption tone, naming conventions, and collection language.
- `product-ideas.md`: product candidates, print sizes, and Shopify/POD assumptions.

Keep notes practical. Record what was tested, where outputs went, what settings were used, and what should be visually reviewed next.
