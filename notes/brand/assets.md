# Shopify Brand Assets

## Asset usage

- `logo-primary-color.png`: default Shopify header logo; shell-integrated turtle mark
- `logo-primary-whitewordmark.png`: alternate header logo for dark headers
- `logo-stacked-color.png`: centered square version of the shell-integrated logo
- `logo-wordmark-color.png`: text-only version for narrow header placements
- `logo-wordmark-white.png`: text-only version for dark overlays
- `icon-badge-1024.png`: profile icon / social avatar / square brand mark using the turtle-only icon
- `favicon-32.png`: Shopify favicon upload
- `favicon-512.png`: larger favicon/app-icon export
- `apple-touch-icon-180.png`: optional mobile bookmark/home-screen icon
- `watermark-white.png`: subtle watermark for previews and mockups
- `shopify-brand-board.png`: quick reference board for visual setup

## Palette

- `Ocean Dark`: `#072C3B`
- `Ocean`: `#0C4454`
- `Ocean Mid`: `#146779`
- `Seafoam`: `#8FD6D0`
- `Seafoam Light`: `#DDF4F2`
- `Sand`: `#D7BE8F`

## Shopify setup notes

- Use a clean light header background first. The shell logo works best there.
- If the theme header is dark or photographic, switch to `logo-primary-whitewordmark.png`.
- Use the badge icon as the profile image for social channels so the turtle stays readable at small size.
- Keep the photography doing most of the storytelling. The logo should identify the brand, not compete with the images.

## Regeneration

If the turtle master or layout treatment changes, rerun:

```powershell
python C:\Users\juanv\Downloads\ScubaWithMe\workflows\generate_shopify_brand_assets.py
```

## Source assets

The generator currently depends on:

- `exports/shopify/brand/logo-shell-transparent.png`
- `exports/shopify/brand/turtle-icon-transparent.png`
- `workflows/generate_shopify_brand_assets.py`
