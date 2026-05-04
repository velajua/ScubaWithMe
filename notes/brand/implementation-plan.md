# Brand Assets Implementation Plan

## Goal

Build the first reusable ScubaWithMe Shopify brand asset pack.

## Approach

- Generate a shell-lettered turtle logo for the storefront mark
- Generate a turtle-only icon for favicon/avatar use
- Remove chroma backgrounds locally and save transparent masters
- Export reproducible raster assets through a local Python script
- Document usage in `notes/brand/`

## Outputs created

- `exports/shopify/brand/logo-primary-color.png`
- `exports/shopify/brand/logo-stacked-color.png`
- `exports/shopify/brand/icon-badge-1024.png`
- `exports/shopify/brand/favicon-32.png`
- `exports/shopify/brand/watermark-white.png`
- `exports/shopify/brand/shopify-brand-board.png`
- `exports/shopify/brand/logo-primary-color.svg`
- `exports/shopify/brand/logo-stacked-color.svg`

## Implementation notes

- The final primary mark uses the shell-integrated logo direction.
- The board layout was adjusted so the preview area does not stack turtles on top of each other.
- The generator now resolves paths from the repo location instead of depending on the current working directory.

## Follow-up

If the brand is taken from Shopify-ready to long-term final, the next step is a clean manual vector redraw of the shell-lettered turtle while preserving the current proportions, pose, and lettering style.
