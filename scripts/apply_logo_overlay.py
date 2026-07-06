"""Stamp the Roofmaster Ottawa logo onto photos before they go into a post.

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


def _position(corner: str, image_size, logo_size, margin: int):
    img_w, img_h = image_size
    logo_w, logo_h = logo_size
    if corner == "bottom-right":
        return (img_w - logo_w - margin, img_h - logo_h - margin)
    if corner == "bottom-left":
        return (margin, img_h - logo_h - margin)
    if corner == "top-right":
        return (img_w - logo_w - margin, margin)
    return (margin, margin)  # top-left


def overlay_logo(
    image_path: Path,
    logo_path: Path,
    output_path: Path,
    corner: str = "bottom-right",
    logo_width_ratio: float = 0.18,
    margin_ratio: float = 0.03,
):
    image = Image.open(image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    logo_width = int(image.width * logo_width_ratio)
    logo_height = int(logo.height * (logo_width / logo.width))
    logo = logo.resize((logo_width, logo_height), Image.LANCZOS)

    margin = int(image.width * margin_ratio)
    position = _position(corner, image.size, logo.size, margin)

    composited = image.copy()
    composited.alpha_composite(logo, dest=position)

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
