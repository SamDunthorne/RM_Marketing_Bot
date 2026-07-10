"""Add an attention-grabbing headline + CTA text overlay to a photo.

Modern/clean type treatment: a light-weight "kicker" line, a bold headline, and an
optional bold yellow CTA line -- letter-spaced, no heavy black outline (a soft drop
shadow instead), stacked over a soft gradient scrim for contrast.

Meant to run BEFORE apply_logo_overlay.py in the pipeline (text banner sits at the
top, logo band sits at the bottom-right, so they don't collide):

    python add_text_overlay.py --input raw/photo.jpg --output tmp/photo.jpg \
        --kicker "SPRING IS HERE" --headline "IS YOUR ROOF READY?" \
        --subtext "Free Estimates - Call (613) 521-0088"
    python apply_logo_overlay.py --input tmp --output images
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_LIGHT = Path("C:/Windows/Fonts/segoeuil.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/segoeuib.ttf")
BRAND_YELLOW = (255, 242, 0)
POSITION_CHOICES = ["top", "bottom"]


def _vertical_gradient_scrim(width: int, height: int, max_alpha: int, fade_toward_bottom: bool) -> Image.Image:
    col = []
    for y in range(height):
        progress = y / height if fade_toward_bottom else 1 - y / height
        col.append(int(max_alpha * (1 - progress)))
    grad_col = Image.new("L", (1, height))
    grad_col.putdata(col)
    return grad_col.resize((width, height))


def _tracked_width(text: str, font: ImageFont.FreeTypeFont, tracking: int) -> int:
    if not text:
        return 0
    return int(sum(font.getlength(ch) for ch in text) + tracking * (len(text) - 1))


def _wrap_tracked(text: str, font: ImageFont.FreeTypeFont, tracking: int, max_width: int) -> list:
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if _tracked_width(candidate, font, tracking) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_tracked_line(draw, xy, text, font, fill, tracking, shadow_offset, shadow_fill):
    x, y = xy
    for ch in text:
        if shadow_offset:
            draw.text((x + shadow_offset, y + shadow_offset), ch, font=font, fill=shadow_fill)
        draw.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking


def _draw_tracked_block(draw, x, y, lines, font, fill, tracking, line_gap, shadow_offset, shadow_fill):
    for line in lines:
        _draw_tracked_line(draw, (x, y), line, font, fill, tracking, shadow_offset, shadow_fill)
        y += font.size + line_gap
    return y


def add_text_overlay(
    image_path: Path,
    output_path: Path,
    headline: str,
    subtext: str = None,
    kicker: str = None,
    position: str = "top",
    scrim_height_ratio: float = 0.44,
    scrim_opacity: float = 0.45,
):
    image = Image.open(image_path).convert("RGBA")
    w, h = image.size

    scrim_height = int(h * scrim_height_ratio)
    scrim_alpha = _vertical_gradient_scrim(
        w, scrim_height, max_alpha=int(255 * scrim_opacity), fade_toward_bottom=(position == "top")
    )
    scrim = Image.new("RGBA", (w, scrim_height), (0, 0, 0, 255))
    scrim.putalpha(scrim_alpha)

    composited = image.copy()
    scrim_y = 0 if position == "top" else h - scrim_height
    composited.alpha_composite(scrim, dest=(0, scrim_y))

    draw = ImageDraw.Draw(composited)
    padding = int(w * 0.05)
    max_text_width = int(w * 0.85)
    tracking = int(h * 0.004)
    line_gap = int(h * 0.014)
    shadow_offset = max(1, int(h * 0.0025))
    shadow_fill = (0, 0, 0, 130)

    kicker_size = int(h * 0.05)
    headline_size = int(h * 0.075)
    subtext_size = int(h * 0.042)

    kicker_font = ImageFont.truetype(str(FONT_BOLD), kicker_size)
    headline_font = ImageFont.truetype(str(FONT_BOLD), headline_size)
    subtext_font = ImageFont.truetype(str(FONT_BOLD), subtext_size)

    kicker_lines = _wrap_tracked(kicker, kicker_font, tracking, max_text_width) if kicker else []
    headline_lines = _wrap_tracked(headline, headline_font, tracking, max_text_width)
    subtext_lines = _wrap_tracked(subtext, subtext_font, tracking, max_text_width) if subtext else []

    block_height = 0
    if kicker_lines:
        block_height += len(kicker_lines) * (kicker_size + line_gap) + int(h * 0.01)
    block_height += len(headline_lines) * (headline_size + line_gap)
    if subtext_lines:
        block_height += int(h * 0.01) + len(subtext_lines) * (subtext_size + line_gap)

    text_y = padding if position == "top" else h - padding - block_height

    if kicker_lines:
        text_y = _draw_tracked_block(
            draw, padding, text_y, kicker_lines, kicker_font, "white", tracking, line_gap, shadow_offset, shadow_fill
        )
        text_y += int(h * 0.01)
    text_y = _draw_tracked_block(
        draw, padding, text_y, headline_lines, headline_font, "white", tracking, line_gap, shadow_offset, shadow_fill
    )
    if subtext_lines:
        text_y += int(h * 0.01)
        _draw_tracked_block(
            draw, padding, text_y, subtext_lines, subtext_font, BRAND_YELLOW, tracking, line_gap, shadow_offset, shadow_fill
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() in (".jpg", ".jpeg"):
        composited.convert("RGB").save(output_path, quality=90)
    else:
        composited.save(output_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--headline", required=True)
    parser.add_argument("--subtext", default=None)
    parser.add_argument("--kicker", default=None)
    parser.add_argument("--position", choices=POSITION_CHOICES, default="top")
    args = parser.parse_args()
    add_text_overlay(args.input, args.output, args.headline, args.subtext, args.kicker, args.position)
    print(f"{args.input} -> {args.output}")


if __name__ == "__main__":
    main()
