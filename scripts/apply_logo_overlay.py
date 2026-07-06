"""Stamp the Roofmaster Ottawa logo onto photos before they go into a post.

The logo sits flush in a corner on top of a solid-to-transparent gradient band (anchored to
that corner's edges) so it stays legible over busy photo backgrounds without a hard-edged
"bubble" -- the band fades out toward the middle of the photo.

Convention: originals live in an `images/raw/` folder, and this script writes the
logo-stamped versions into `images/` (the folder post.json actually references and
that the scheduler publishes from). Re-running is safe -- it always re-reads from
raw/ and overwrites the stamped output.

Usage:
    python apply_logo_overlay.py --input posts/post-01/images/raw --output posts/post-01/images
    python apply_logo_overlay.py --input sandbox/test-batch/raw --output sandbox/test-batch/final
"""
import argparse
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOGO = REPO_ROOT / "assets" / "shared" / "logos" / "logo.png"

CORNER_CHOICES = ["bottom-right", "bottom-left", "top-right", "top-left"]


def _horizontal_alpha_gradient(width: int, height: int, solid_width: int, max_alpha: int, solid_on_right: bool) -> Image.Image:
    """'L' image of the given size: `solid_width` px at max_alpha on one side, ramping
    down to 0 across the remaining width on the other side."""
    fade_width = max(width - solid_width, 1)
    row = []
    for x in range(width):
        if solid_on_right:
            dist_from_solid = (width - x) - solid_width  # >0 means still in fade region
        else:
            dist_from_solid = x - solid_width
        if dist_from_solid <= 0:
            row.append(max_alpha)
        else:
            row.append(int(max_alpha * max(0.0, 1 - dist_from_solid / fade_width)))
    grad_row = Image.new("L", (width, 1))
    grad_row.putdata(row)
    return grad_row.resize((width, height))


def _corner_flags(corner: str):
    """Returns (anchor_right, anchor_bottom) -- which edges the band/logo sit flush against."""
    return {
        "bottom-right": (True, True),
        "bottom-left": (False, True),
        "top-right": (True, False),
        "top-left": (False, False),
    }[corner]


def overlay_logo(
    image_path: Path,
    logo_path: Path,
    output_path: Path,
    corner: str = "bottom-right",
    logo_width_ratio: float = 0.26,
    padding_ratio: float = 0.03,
    fade_ratio: float = 1.2,
    band_opacity: float = 0.85,
    band_color=(255, 255, 255),
):
    image = Image.open(image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    logo_width = int(image.width * logo_width_ratio)
    logo_height = int(logo.height * (logo_width / logo.width))
    logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

    anchor_right, anchor_bottom = _corner_flags(corner)
    padding = int(image.width * padding_ratio)

    solid_width = logo_width + 2 * padding
    band_height = logo_height + 2 * padding
    band_width = int(solid_width * (1 + fade_ratio))

    band_alpha = _horizontal_alpha_gradient(
        band_width, band_height, solid_width, max_alpha=int(255 * band_opacity), solid_on_right=anchor_right
    )
    band = Image.new("RGBA", (band_width, band_height), band_color + (255,))
    band.putalpha(band_alpha)

    band_x = image.width - band_width if anchor_right else 0
    band_y = image.height - band_height if anchor_bottom else 0
    logo_x = image.width - padding - logo_width if anchor_right else padding
    logo_y = image.height - padding - logo_height if anchor_bottom else padding

    composited = image.copy()
    composited.alpha_composite(band, dest=(band_x, band_y))
    composited.alpha_composite(logo, dest=(logo_x, logo_y))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() in (".jpg", ".jpeg"):
        composited.convert("RGB").save(output_path, quality=90)
    else:
        composited.save(output_path)


def process_directory(input_dir: Path, output_dir: Path, logo_path: Path, corner: str):
    image_exts = {".jpg", ".jpeg", ".png"}
    images = sorted(p for p in input_dir.iterdir() if p.suffix.lower() in image_exts)
    if not images:
        print(f"No images found in {input_dir}")
        return
    for image_path in images:
        output_path = output_dir / image_path.name
        overlay_logo(image_path, logo_path, output_path, corner=corner)
        print(f"{image_path} -> {output_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Folder of raw/original images")
    parser.add_argument("--output", required=True, type=Path, help="Folder to write logo-stamped images into")
    parser.add_argument("--logo", type=Path, default=DEFAULT_LOGO, help="Path to logo PNG (default: assets/shared/logos/logo.png)")
    parser.add_argument("--corner", choices=CORNER_CHOICES, default="bottom-right")
    args = parser.parse_args()

    if not args.logo.exists():
        raise SystemExit(f"Logo file not found: {args.logo} -- drop a logo PNG there first.")

    process_directory(args.input, args.output, args.logo, args.corner)


if __name__ == "__main__":
    main()
