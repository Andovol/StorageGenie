"""Deterministic synthetic label generator for the SG-029 image corpus.

Produces every committed PNG under `images/` from a fixed recipe: fixed canvas
size, fixed dates, fixed text, a seeded pseudo-random clutter field. No clock,
no network, no personal image, no EXIF/GPS (PIL writes bare PNG; the shared
`redact_image` is a second, byte-level guarantee at call time). Re-running this
script reproduces the committed bytes on this host's Pillow/font build.

The date is drawn for the "clean" fixtures and deliberately removed/washed/
occluded for the hard cases whose ground truth expects an unknown.
"""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
IMAGES = HERE / "images"
CANVAS = (700, 500)
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _font(path: str, size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default(size=size)


def _label(img: Image.Image, box: tuple[int, int, int, int], title: str, lines: list[str]) -> None:
    draw = ImageDraw.Draw(img)
    draw.rectangle(box, fill=(250, 250, 245), outline=(60, 60, 60), width=3)
    x0, y0, x1, _ = box
    draw.text((x0 + 24, y0 + 20), title, font=_font(FONT_BOLD, 44), fill=(20, 20, 20))
    y = y0 + 92
    for line in lines:
        draw.text((x0 + 24, y), line, font=_font(FONT_REGULAR, 30), fill=(35, 35, 35))
        y += 46


def _label_box() -> tuple[int, int, int, int]:
    return (120, 110, 580, 400)


def _clutter_field(img: Image.Image, seed: int) -> None:
    draw = ImageDraw.Draw(img)
    rng = random.Random(seed)
    for _ in range(90):
        x = rng.randint(0, CANVAS[0] - 60)
        y = rng.randint(0, CANVAS[1] - 40)
        w = rng.randint(30, 120)
        h = rng.randint(20, 90)
        shade = rng.randint(150, 220)
        draw.ellipse((x, y, x + w, y + h), fill=(shade, shade - 10, shade - 20), outline=(90, 90, 90))


def _glare(img: Image.Image) -> None:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.polygon([(260, 0), (520, 0), (330, 500), (120, 500)], fill=(255, 255, 255, 235))
    img.paste(overlay, (0, 0), overlay)


def _tear(img: Image.Image) -> None:
    draw = ImageDraw.Draw(img)
    draw.polygon([(320, 175), (580, 155), (580, 400), (290, 400)], fill=(235, 235, 230))


def clean_food() -> Image.Image:
    img = Image.new("RGB", CANVAS, (225, 235, 230))
    _label(img, _label_box(), "MILK", ["BEST BEFORE 2031-03-15", "LOT L4471", "1 L"])
    return img


def clean_medicine() -> Image.Image:
    img = Image.new("RGB", CANVAS, (232, 230, 240))
    _label(img, _label_box(), "PARACETAMOL", ["EXP 2030-06-30", "BATCH B778", "20 TABLETS"])
    return img


def glare_food() -> Image.Image:
    img = Image.new("RGB", CANVAS, (235, 232, 220))
    _label(img, _label_box(), "ORANGE JUICE", ["BEST BEFORE 2031-08-12", "LOT J2210", "1 L"])
    _glare(img)
    return img


def clutter_food() -> Image.Image:
    img = Image.new("RGB", CANVAS, (240, 238, 232))
    _clutter_field(img, seed=29)
    _label(img, (150, 140, 610, 430), "TOMATO SOUP", ["BEST BEFORE 2030-11-05", "LOT T9081"])
    draw = ImageDraw.Draw(img)
    draw.rectangle((300, 200, 700, 460), fill=(205, 175, 140), outline=(80, 60, 40), width=3)
    return img


def partial_label_food() -> Image.Image:
    img = Image.new("RGB", CANVAS, (228, 233, 226))
    _label(img, _label_box(), "BAKED BEANS", ["BEST BEFORE 2030-09-19", "LOT K3320", "400 g"])
    _tear(img)
    return img


def partial_label_medicine() -> Image.Image:
    img = Image.new("RGB", CANVAS, (232, 228, 236))
    _label(img, _label_box(), "AMOXICILLIN", ["EXP 2030-04-30", "BATCH A119", "14 CAPSULES"])
    _tear(img)
    return img


def no_date_medicine() -> Image.Image:
    img = Image.new("RGB", CANVAS, (235, 231, 227))
    _label(img, _label_box(), "VITAMIN D3", ["1000 IU", "30 SOFTGELS"])
    return img


def clean_cosmetics() -> Image.Image:
    img = Image.new("RGB", CANVAS, (238, 225, 232))
    _label(img, _label_box(), "MOISTURISER", ["OPENED 2031-04-10", "50 ML", "PAO 12M"])
    return img


def no_date_cosmetics() -> Image.Image:
    img = Image.new("RGB", CANVAS, (236, 228, 224))
    _label(img, _label_box(), "SHAMPOO", ["400 ML", "SULFATE FREE"])
    return img


def partial_label_cosmetics() -> Image.Image:
    img = Image.new("RGB", CANVAS, (230, 232, 236))
    _label(img, _label_box(), "FACE CREAM", ["OPENED 2030-12-01", "30 ML"])
    _tear(img)
    return img


RECIPES = {
    "sg029_01_clean_food": clean_food,
    "sg029_02_clean_medicine": clean_medicine,
    "sg029_03_glare_food": glare_food,
    "sg029_04_clutter_food": clutter_food,
    "sg029_05_partial_label_food": partial_label_food,
    "sg029_06_partial_label_medicine": partial_label_medicine,
    "sg029_07_no_date_visible_medicine": no_date_medicine,
    "sg029_08_clean_cosmetics": clean_cosmetics,
    "sg029_09_no_date_visible_cosmetics": no_date_cosmetics,
    "sg029_10_partial_label_cosmetics": partial_label_cosmetics,
}


def main() -> int:
    IMAGES.mkdir(parents=True, exist_ok=True)
    for name, recipe in RECIPES.items():
        path = IMAGES / f"{name}.png"
        recipe().save(path, format="PNG", optimize=True)
        print(f"wrote {path.relative_to(HERE)} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
