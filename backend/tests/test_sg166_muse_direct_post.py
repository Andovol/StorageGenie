"""SG-166 — offline direct-POST payload-shape pin (offline, $0; `PG-EV-04`).

SG-159 measured `meta/muse-image` with an empty Image-API per-endpoint record and
only ever sent the chat server-tool path for Muse; it never sent the direct
`POST /api/v1/images` the owner-supplied docs name. SG-166's G1 sends exactly
that one direct POST. This test pins, offline and with no network, key or money,
the exact documented payload shape `{model, prompt, input_references}` that the
direct POST carries (`backend/scripts/sg166_render.py::build_direct_payload`),
and asserts the shipped builder (`scene.build_image_request`) agrees on those
documented keys — so the pinned shape is the one the live send actually uses.

Fail-pre (isolated base worktree, candidate test copied in): the SG-166 driver
does not exist on base, so loading it fails (`FileNotFoundError`). Pass-post
(candidate): the payload builder returns exactly the three documented keys.
No HTTP client is constructed; no key is read; nothing is billed.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from app.services.scene import openrouter as scene

BRIEF = (
    "Restage this packaged product on a clean kitchen counter in warm natural "
    "daylight; keep the package, its label and its printed text exactly as "
    "photographed."
)
IMAGE_MODEL = "meta/muse-image"
PHOTO = "data:image/png;base64,QUJD"


def _load_direct_post_driver() -> ModuleType:
    """Load the SG-166 driver from its source file (CO-27: source, never a copy)."""
    path = Path(__file__).resolve().parents[1] / "scripts" / "sg166_render.py"
    spec = importlib.util.spec_from_file_location("sg166_render", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_direct_post_payload_shape_is_exact() -> None:
    driver = _load_direct_post_driver()
    payload = driver.build_direct_payload(PHOTO, BRIEF, IMAGE_MODEL)

    # Exactly the documented keys, no more (the packet names model/prompt/input_references).
    assert set(payload.keys()) == {"model", "prompt", "input_references"}
    assert payload["model"] == IMAGE_MODEL
    assert payload["prompt"] == BRIEF
    assert payload["input_references"] == [
        {"type": "image_url", "image_url": {"url": PHOTO}}
    ]

    # The shipped builder (used by the live send) agrees on the documented keys.
    shipped = scene.build_image_request(PHOTO, BRIEF, IMAGE_MODEL)["json"]
    assert isinstance(shipped, dict)
    assert shipped["model"] == payload["model"]
    assert shipped["prompt"] == payload["prompt"]
    assert shipped["input_references"] == payload["input_references"]
