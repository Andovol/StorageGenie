import datetime

from app.schemas.common import (
    ProblemDetail,
    decode_cursor,
    dumps_json,
    encode_cursor,
    loads_json,
)


def test_loads_json() -> None:
    # 1. None returns None
    assert loads_json(None) is None

    # 2. Valid JSON strings
    assert loads_json('{"key": "value"}') == {"key": "value"}
    assert loads_json("[1, 2, 3]") == [1, 2, 3]
    assert loads_json('"string"') == "string"
    assert loads_json("123") == 123
    assert loads_json("true") is True

    # 3. Invalid JSON strings (error handling fallback)
    assert loads_json("invalid json") == "invalid json"
    assert loads_json("{bad_json:}") == "{bad_json:}"
    assert loads_json("not a json string") == "not a json string"


def test_dumps_json() -> None:
    data = {"name": "Test", "unicode": "こんにちは"}
    dumped = dumps_json(data)
    assert 'こんにちは' in dumped
    assert loads_json(dumped) == data


def test_encode_and_decode_cursor() -> None:
    ts = datetime.datetime(2026, 1, 15, 12, 30, 0)
    item_id = "item-123"

    # Encode cursor
    cursor = encode_cursor(ts, item_id)
    assert isinstance(cursor, str)

    # Decode spec cursor (id:ts)
    decoded = decode_cursor(cursor)
    assert decoded == (ts, item_id)


def test_decode_cursor_legacy_format() -> None:
    # Legacy format uses '|' and ts|id order
    import base64

    raw_legacy = "2026-01-15|legacy-item-456"
    cursor = base64.urlsafe_b64encode(raw_legacy.encode()).decode()

    decoded = decode_cursor(cursor)
    assert decoded == (datetime.datetime(2026, 1, 15, 0, 0, 0), "legacy-item-456")


def test_decode_cursor_invalid() -> None:
    assert decode_cursor("invalid_base64_!@#$") is None
    # Valid base64 but neither ':' nor '|'
    import base64

    cursor_no_sep = base64.urlsafe_b64encode(b"no_separator").decode()
    assert decode_cursor(cursor_no_sep) is None

    # Invalid timestamp format
    cursor_bad_ts = base64.urlsafe_b64encode(b"item:bad-timestamp").decode()
    assert decode_cursor(cursor_bad_ts) is None


def test_problem_detail() -> None:
    pd = ProblemDetail(title="Not Found", status=404, detail="Item not found")
    assert pd.type == "about:blank"
    assert pd.title == "Not Found"
    assert pd.status == 404
    assert pd.detail == "Item not found"
