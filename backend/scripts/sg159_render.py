#!/usr/bin/env python3
"""SG-159 G1 — one controlled scene render per invocation (Google vs Muse).

Runs INSIDE the production image with the live volume mounted (`/data/storage`)
and the live DB bind (`/data/db`); it calls the committed send path
(`app.services.scene.openrouter.render_scene`) exactly once per invocation, so
each render's Evidence + ledger rows are persisted the moment it returns.

Frozen plan (same brief for every render; R2a/R2b share photo 1; R3 re-confirms
the winner on photo 2):
- brief: FROZEN_BRIEF (below), identical for R2a, R2b, R3.
- photo P1: SG-158 R2's photo — evidence 01a0c481 (Milbona Parmigiano);
- photo P2: SG-158 P2 — evidence 01a0c47f (UHT Lapte 3,5%).
- R2a: P1 x google/gemini-3.1-flash-image (Google AI Studio — permitted)
- R2b: P1 x meta/muse-image (Meta — permitted; Image-API endpoints empty, so
  the chat server-tool path is the only routable one for this model)
- R3: P2 x the winner slug passed on `--model` (run only after the pick)

Transport decision (G0-fix, reported): the chat-completions server tool
(frozen envelope) is kept for both legs — the dedicated Image API cannot route
`meta/muse-image` (zero endpoints, measured 2026-10-12) and a cross-transport
contest would confound the pick; the 2xx-body persistence + extractor
hardening now record exactly what the tool returns.

The live DB already holds 3 `provider_call` rows from SG-158 (spent
$0.000758925); this slice's guard accounts them and refuses `over_cap` before
any send. Worst case per render here: 0.30 (Google image budget 4096 image
tokens x T0 image_output 0.00006 + orchestrator budget; Muse's list price is
~0.01/image, far inside). Total spend of the arc stays <= $1.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

from app.db import SessionLocal
from app.services.scene import openrouter as scene

HOUSEHOLD_ID = "01a0a029-1477-7ca0-b200-bce78a96c679"
# Account allowed-providers (live R1 404 body, SG-158): xai, meta, seed, baidu,
# nvidia, xiaomi, minimax, stealth, deepseek, moonshotai, open-inference,
# google-ai-studio. Orchestrator: bytedance-seed/seed-1.6-flash (Seed is
# permitted and cheapest routable vision+tools model).
ORCHESTRATOR = "bytedance-seed/seed-1.6-flash"
FROZEN_BRIEF = (
    "Restage this packaged product on a clean kitchen counter in warm natural "
    "daylight; keep the package, its label and its printed text exactly as "
    "photographed."
)
AUTHORITY = scene.SceneSpendAuthority(
    grant_id="D-1009-4 + L3 (D-1009-7) + D-1009-10", cap_usd=1.0
)
STORAGE_ROOT = Path("/data/storage")

# photo_key -> storage key inside the live volume (photo bytes only)
PHOTOS: dict[str, str] = {
    "P1": "01a0a029-1477-7ca0-b200-bce78a96c679/05/052a5f7b47d0556aace108ea32fbd67f8641c9e940f4a7ef69e1cc92e75a1a45.png",
    "P2": "01a0a029-1477-7ca0-b200-bce78a96c679/b6/b6e11ecce9be93ee2470ad75143e8e1d89489da1e128baecc89688ae9e3a833e.png",
}

# render id -> (photo, image model, worst-case USD)
RENDERS: dict[str, dict[str, object]] = {
    "R2a": {
        "photo": "P1",
        "image_model": "google/gemini-3.1-flash-image",
        "worst_case_usd": 0.15,
        "transport": "image_api",
    },
    "R2b": {
        "photo": "P1",
        "image_model": "meta/muse-image",
        "worst_case_usd": 0.05,
        "transport": "server_tool",
    },
    "R3": {"photo": "P2", "image_model": None, "worst_case_usd": 0.15, "transport": "image_api"},
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("render", choices=sorted(RENDERS))
    parser.add_argument("--model", default=None, help="required for R3: the winner slug")
    args = parser.parse_args()

    plan = RENDERS[args.render]
    image_model = plan["image_model"] if args.model is None else args.model
    if not image_model:
        print("model_required_for_r3", file=sys.stderr)
        return 2
    photo_key = PHOTOS[str(plan["photo"])]
    photo_bytes = (STORAGE_ROOT / photo_key).read_bytes()
    photo_ref = "data:image/png;base64," + base64.b64encode(photo_bytes).decode("ascii")
    print(
        f"render={args.render} photo={plan['photo']} image_model={image_model} "
        f"photo_bytes={len(photo_bytes)} orchestrator={ORCHESTRATOR} "
        f"worst_case_usd={plan['worst_case_usd']}",
        file=sys.stderr,
    )

    db = SessionLocal()
    try:
        outcome = scene.render_scene(
            db,
            household_id=HOUSEHOLD_ID,
            photo_ref=photo_ref,
            brief=FROZEN_BRIEF,
            image_model=str(image_model),
            orchestrator=ORCHESTRATOR,
            worst_case_usd=float(plan["worst_case_usd"]),  # type: ignore[arg-type]
            authority=AUTHORITY,
            transport=str(plan.get("transport", "server_tool")),
        )
    finally:
        db.close()

    result = {
        "render": args.render,
        "status": outcome.status,
        "refusal": (
            {"code": outcome.refusal.code, "reason": outcome.refusal.reason}
            if outcome.refusal is not None
            else None
        ),
        "status_code": outcome.status_code,
        "response_id": outcome.response_id,
        "image_model": image_model,
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
