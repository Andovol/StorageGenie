#!/usr/bin/env python3
"""SG-166 G1 — the ONE direct Image-API POST that SG-159 never sent for Muse.

SG-159 proved the chat server-tool path never delivers an image artifact for
`meta/muse-image` (persisted 200 body: text only) and measured the dedicated
Image API's per-endpoint record empty (`endpoints: []`). It never sent the
direct `POST /api/v1/images` that the owner-supplied docs name as the transport:
`{model, prompt, input_references[]}` → `data[].b64_json` + `usage.cost`
(all-or-nothing billing).

This driver performs exactly that one direct POST for `meta/muse-image`, through
the guarded send path (`app.services.scene.openrouter.render_scene`,
`transport="image_api"`), so the Evidence bytes + ledger row persist the moment
it returns (PG-EV-14). It sends at most once per invocation.

Frozen inputs (quote + reuse SG-158/159; not re-derived):
- photo: SG-159 photo 1 = evidence `01a0c481-08b8-72b2-ab22-8ad28fed8fda`
  (Milbona Parmigiano Reggiano; clear printed label), reused byte-identical.
- brief: FROZEN_BRIEF, identical to SG-158/SG-159.
- image model: `meta/muse-image` (config, never architecture — D7).
- orchestrator: `bytedance-seed/seed-1.6-flash` (Seed permitted; cheapest
  routable vision model). The Image API does not use the orchestrator; it is
  recorded on the ledger row for provenance.

Payload decision (reported): the reference image rides as a base64 data URL
(self-contained; no external hosting needed) — `build_direct_payload` pins the
exact documented shape `{model, prompt, input_references}`.

Consent: the explicit `SceneSpendAuthority` below quotes this packet's spend
authority (D-1009-4 + L3 D-1009-7 + D-1012-3 + m0034), cap $1.00; `sg_consent`
is never consulted, never flipped.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path
from typing import Any

from app.db import SessionLocal
from app.services.scene import openrouter as scene

HOUSEHOLD_ID = "01a0a029-1477-7ca0-b200-bce78a96c679"

# SG-159 photo 1 (Milbona Parmigiano Reggiano) — reused byte-identical.
PHOTO_EVIDENCE_ID = "01a0c481-08b8-72b2-ab22-8ad28fed8fda"
PHOTO_STORAGE_KEY = (
    "01a0a029-1477-7ca0-b200-bce78a96c679/05/"
    "052a5f7b47d0556aace108ea32fbd67f8641c9e940f4a7ef69e1cc92e75a1a45.png"
)

ORCHESTRATOR = "bytedance-seed/seed-1.6-flash"
IMAGE_MODEL = "meta/muse-image"
FROZEN_BRIEF = (
    "Restage this packaged product on a clean kitchen counter in warm natural "
    "daylight; keep the package, its label and its printed text exactly as "
    "photographed."
)
WORST_CASE_USD = 0.05  # Muse: <= ~4175 image tokens x $0.0000023952 ~= $0.01, bound 5x.
AUTHORITY = scene.SceneSpendAuthority(
    grant_id="D-1009-4 + L3 (D-1009-7) + D-1012-3 + m0034", cap_usd=1.0
)
STORAGE_ROOT = Path("/data/storage")


def build_direct_payload(photo_ref: str, prompt: str, image_model: str) -> dict[str, Any]:
    """The documented direct Image-API payload: exactly `{model, prompt, input_references}`.

    Pins the transport the owner-supplied docs name (fetched 2026-10-12):
    `POST /api/v1/images` `{model, prompt, input_references[]}` → `data[].b64_json`
    + `usage.cost`. Reference images may be HTTP(S) URLs or base64 data URLs; the
    caller passes `photo_ref` as a base64 data URL.
    """
    return {
        "model": image_model,
        "prompt": prompt,
        "input_references": [{"type": "image_url", "image_url": {"url": photo_ref}}],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--photo-key", default=PHOTO_STORAGE_KEY, help="storage key of the picked photo"
    )
    args = parser.parse_args()

    photo_bytes = (STORAGE_ROOT / args.photo_key).read_bytes()
    photo_ref = "data:image/png;base64," + base64.b64encode(photo_bytes).decode("ascii")
    payload = build_direct_payload(photo_ref, FROZEN_BRIEF, IMAGE_MODEL)

    # The shipped builder must agree on the documented keys (the live send uses
    # `render_scene`, which builds via `build_image_request`).
    shipped = scene.build_image_request(photo_ref, FROZEN_BRIEF, IMAGE_MODEL)["json"]
    assert isinstance(shipped, dict)
    for key in ("model", "prompt", "input_references"):
        assert shipped.get(key) == payload[key], f"builder drift on {key}"

    print(
        f"render=G1 photo_evidence={PHOTO_EVIDENCE_ID} image_model={IMAGE_MODEL} "
        f"photo_bytes={len(photo_bytes)} orchestrator={ORCHESTRATOR} "
        f"worst_case_usd={WORST_CASE_USD}",
        file=sys.stderr,
    )

    db = SessionLocal()
    try:
        outcome = scene.render_scene(
            db,
            household_id=HOUSEHOLD_ID,
            photo_ref=photo_ref,
            brief=FROZEN_BRIEF,
            image_model=IMAGE_MODEL,
            orchestrator=ORCHESTRATOR,
            worst_case_usd=WORST_CASE_USD,
            authority=AUTHORITY,
            transport="image_api",
        )
    finally:
        db.close()

    result = {
        "render": "G1",
        "status": outcome.status,
        "refusal": (
            {"code": outcome.refusal.code, "reason": outcome.refusal.reason}
            if outcome.refusal is not None
            else None
        ),
        "status_code": outcome.status_code,
        "response_id": outcome.response_id,
        "image_model": IMAGE_MODEL,
        "orchestrator": ORCHESTRATOR,
        "evidence_id": outcome.evidence_id,
        "ledger_id": outcome.ledger_id,
        "image_sha256": outcome.image_sha256,
        "image_media_type": outcome.image_media_type,
        "storage_key": outcome.storage_key,
        "cost_usd": outcome.cost_usd,
        "usage": outcome.usage,
        "latency_ms": outcome.latency_ms,
        "error_state": outcome.error_state,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if outcome.status == "rendered" else 1


if __name__ == "__main__":
    raise SystemExit(main())
