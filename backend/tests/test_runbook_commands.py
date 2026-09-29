"""SG-144 guard: the README runbook commands equal the SG-086 drill form (F-SG126-3).

No test tied the README runbook command strings to the live drill tooling, so the
doubled-``/_data`` drift (F-SG126-1) survived 40+ slices before SG-126 caught it by
hand. This pin reads the REAL ``README.md`` bytes from the tree (never a copied
fixture) and asserts the runbook command strings the operator copies stay
byte-equal to the SG-086 form, deriving the drill's required flag set from the real
``backend/scripts/backup_restore_drill.py``.
"""

from __future__ import annotations

import re
from pathlib import Path

README_PATH = Path(__file__).resolve().parents[2] / "README.md"
DRILL_PATH = Path(__file__).resolve().parents[1] / "scripts" / "backup_restore_drill.py"

COMPOSE_UP = "docker compose up --build -d"
ALEMBIC_UPGRADE = "docker compose exec backend python -m alembic upgrade head"
SEED = "docker compose exec backend python -m app.seed"

STORAGE_EXPR = "$(docker volume inspect storagegenie_storage_data --format '{{.Mountpoint}}')"
DRILL_INVOCATION = "\n".join(
    (
        "backend/venv/bin/python backend/scripts/backup_restore_drill.py \\",
        "  --prod-db data/db/storagegenie.db \\",
        f'  --prod-storage "{STORAGE_EXPR}"',
    )
)

SECRET_PATTERN = re.compile(
    r"\bsk-[A-Za-z0-9]{10,}|\bghp_[A-Za-z0-9]{20,}|-{5}BEGIN\b|api[_-]?key\s*=", re.I
)


def readme_text() -> str:
    return README_PATH.read_text(encoding="utf-8")


def drill_script_text() -> str:
    return DRILL_PATH.read_text(encoding="utf-8")


def required_flag_names() -> set[str]:
    """The drill flags the script declares ``required=True`` (the SG-086 interface)."""
    return set(re.findall(r'add_argument\("(--[a-z-]+)",\s*required=True', drill_script_text()))


def drill_block(text: str) -> str:
    """The fenced sh block that invokes the drill (the SG-086 runbook form)."""
    anchor = text.index("backend/venv/bin/python backend/scripts/backup_restore_drill.py")
    open_fence = text.rfind("```sh", 0, anchor)
    close_fence = text.index("```", anchor)
    return text[open_fence:close_fence]


def drill_flags_used(text: str) -> set[str]:
    return set(re.findall(r"^\s*(--[a-z-]+)", drill_block(text), re.MULTILINE))


def storage_argument(text: str) -> str:
    match = re.search(r"^\s*(--prod-storage .*)$", text, re.MULTILINE)
    return match.group(1) if match else ""


def runbook_violations(text: str, required_flags: set[str]) -> list[str]:
    """Every way the README runbook can drift from the SG-086 form, as messages."""
    violations: list[str] = []
    for label, command in (
        ("compose-up", COMPOSE_UP),
        ("alembic-upgrade", ALEMBIC_UPGRADE),
        ("seed", SEED),
    ):
        if command not in text:
            violations.append(f"{label}: exact command string missing: {command!r}")
    if DRILL_INVOCATION not in text:
        violations.append(f"drill-invocation: exact block missing: {DRILL_INVOCATION!r}")
    expected_storage = f'--prod-storage "{STORAGE_EXPR}"'
    if storage_argument(text) != expected_storage:
        violations.append(
            "drill-invocation: --prod-storage is not the SG-086 form: "
            f"{storage_argument(text)!r} != {expected_storage!r}"
        )
    used = drill_flags_used(text)
    if used != required_flags:
        violations.append(
            f"drill-invocation: flags {sorted(used)} != required flags {sorted(required_flags)}"
        )
    return violations


def test_readme_runbook_commands_match_sg086_form() -> None:
    text = readme_text()
    assert text.strip(), "README.md is empty — a pin on empty bytes proves nothing"
    required_flags = required_flag_names()
    assert required_flags, "no required flags derived from the drill script — vacuous guard"
    violations = runbook_violations(text, required_flags)
    assert violations == [], "\n".join(violations)


def test_guard_flags_the_doubled_data_suffix_drift() -> None:
    """Seen-to-fail property: the historical ``/_data`` doubling must be caught."""
    text = readme_text()
    drifted = text.replace(STORAGE_EXPR, f"{STORAGE_EXPR}/_data")
    assert drifted != text, "drift injection did not change the README — test is inert"
    violations = runbook_violations(drifted, required_flag_names())
    assert any("--prod-storage" in message for message in violations), violations


def test_guard_constants_carry_no_secret() -> None:
    blob = "\n".join((COMPOSE_UP, ALEMBIC_UPGRADE, SEED, DRILL_INVOCATION))
    assert SECRET_PATTERN.search(blob) is None, "a credential-shaped literal leaked into the guard"
