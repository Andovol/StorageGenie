"""Shared image redaction helper (SG-027): EXIF/GPS never leaves the machine.

One function, used by the OpenCode GO adapter now and by the SG-028 pipeline
later. Re-encoding to PNG drops EXIF (including GPS) by construction while the
rendered pixels are preserved; orientation is applied before the strip so the
visible content is unchanged.
"""

from __future__ import annotations

import io

from PIL import Image, ImageOps


def redact_image(raw: bytes) -> bytes:
    """Re-encode any decodable image to PNG carrying zero EXIF/GPS tags."""
    with Image.open(io.BytesIO(raw)) as img:
        upright = ImageOps.exif_transpose(img)
        buffer = io.BytesIO()
        upright.save(buffer, format="PNG")
    return buffer.getvalue()
