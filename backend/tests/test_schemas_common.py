import base64
from datetime import datetime, timezone

from app.schemas.common import (
    ProblemDetail,
    decode_cursor,
    dumps_json,
    encode_cursor,
    loads_json,
)


def test_encode_and_decode_cursor_valid() -> None:
    now = datetime(2026, 3, 30, 12, 0, 0, tzinfo=timezone.utc)
    asset_id = "asset-123"

    # Encode cursor using spec format
    encoded = encode_cursor(now, asset_id)
    assert isinstance(encoded, str)

    # Decode cursor
    decoded = decode_cursor(encoded)
    assert decoded is not None
    decoded_ts, decoded_id = decoded
    assert decoded_ts == now
    assert decoded_id == asset_id


def test_decode_cursor_legacy_format() -> None:
    # Legacy format: ts|id (where ts is date without colons e.g. YYYY-MM-DD or custom format without colons)
    ts_str = "2026-03-30"
    asset_id = "asset-456"
    raw = f"{ts_str}|{asset_id}"
    encoded = base64.urlsafe_b64encode(raw.encode()).decode()

    decoded = decode_cursor(encoded)
    assert decoded is not None
    decoded_ts, decoded_id = decoded
    assert decoded_ts == datetime.fromisoformat(ts_str)
    assert decoded_id == asset_id


def test_decode_cursor_invalid_base64() -> None:
    # Not valid base64 string
    assert decode_cursor("!!!invalid_base64!!!") is None


def test_decode_cursor_missing_separator() -> None:
    # Valid base64 encoding of a string without ':' or '|'
    raw = "just_some_random_string_without_separators"
    encoded = base64.urlsafe_b64encode(raw.encode()).decode()
    assert decode_cursor(encoded) is None


def test_decode_cursor_invalid_timestamp_format() -> None:
    # Valid base64 encoding with ':' separator but invalid ISO timestamp
    raw = "asset-123:not-a-timestamp"
    encoded = base64.urlsafe_b64encode(raw.encode()).decode()
    assert decode_cursor(encoded) is None

    # Valid base64 encoding with '|' legacy separator but invalid ISO timestamp
    raw_legacy = "not-a-timestamp|asset-123"
    encoded_legacy = base64.urlsafe_b64encode(raw_legacy.encode()).decode()
    assert decode_cursor(encoded_legacy) is None


def test_decode_cursor_empty_string() -> None:
    assert decode_cursor("") is None


def test_json_dumps_and_loads() -> None:
    data = {"key": "value", "count": 42}
    dumped = dumps_json(data)
    assert isinstance(dumped, str)
    assert loads_json(dumped) == data

    assert loads_json(None) is None
    # Invalid JSON string should return the original string
    assert loads_json("invalid json {") == "invalid json {"


def test_problem_detail_model() -> None:
    detail = ProblemDetail(title="Not Found", status=404, detail="Resource not found")
    assert detail.type == "about:blank"
    assert detail.title == "Not Found"
    assert detail.status == 404
    assert detail.detail == "Resource not found"


def test_loads_json_non_dict_types() -> None:
    # Folded from PR #37 (unique cases: list/int/bool + string scalar).
    # Pins the loads_json `return json.loads(value)` success branch for
    # non-mapping JSON payloads (PR #33 covered only a dict payload).
    assert loads_json("[1, 2, 3]") == [1, 2, 3]
    assert loads_json("123") == 123
    assert loads_json("true") is True
    assert loads_json('"string"') == "string"


def test_dumps_json_unicode_not_escaped() -> None:
    # Folded from PR #37 (unique case). Pins dumps_json's ensure_ascii=False
    # branch: a unicode payload must round-trip through loads_json.
    data = {"name": "Test", "unicode": "こんにちは"}
    dumped = dumps_json(data)
    assert "こんにちは" in dumped
    assert loads_json(dumped) == data
