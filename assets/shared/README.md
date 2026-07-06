# Shared Assets

Put anything here that should be reusable across multiple posts: logo files, brand-color
graphics, watermark/frame overlays, standard headshots, truck/crew photos, before-after
templates, etc.

## Layout

- `logos/` - Roofmaster Ottawa logo files (PNG with transparent background preferred, plus a
  square version for profile-picture-style crops).
- `branding/` - color swatches, fonts, banner/frame overlays you want stamped on photos.
- `boilerplate/` - reusable text snippets, e.g. `company_bio.txt`, `standard_cta.txt`,
  `hashtags.txt`. Posting scripts can read these to keep messaging consistent.

## How posts reference shared assets

Individual posts under `posts/post-XX/` should keep their own job-specific photos in their own
`images/` folder. If a post also wants a shared asset (e.g. the logo watermark or a "Call Now"
graphic), reference it with a relative path back into this folder, e.g.:

```json
"images": [
  "images/job-photo-1.jpg",
  "images/job-photo-2.jpg",
  "../../assets/shared/branding/call-now-banner.png"
]
```

Keep file names lowercase-with-hyphens and under a few MB each -- large images slow down the
Graph API fetch and Instagram/Facebook both re-compress anyway.
