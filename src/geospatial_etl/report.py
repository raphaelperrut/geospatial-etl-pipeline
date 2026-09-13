"""Structured reporting for ETL pipeline executions."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import json
from geospatial_etl.models import DatasetInspection, DatasetValidation


@dataclass(frozen=True)
class ETLReport:
    """Structured report for a completed ETL execution."""

    source_path: str
    destination_table: str
    destination_schema: str
    target_crs: str | None
    started_at: str
    finished_at: str
    source_inspection: DatasetInspection
    validation: DatasetValidation
    normalized_inspection: DatasetInspection

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the report."""

        return asdict(self)


def build_etl_report(
    *,
    source_path: str | Path,
    destination_table: str,
    destination_schema: str,
    target_crs: str | None,
    started_at: datetime,
    finished_at: datetime,
    source_inspection: DatasetInspection,
    validation: DatasetValidation,
    normalized_inspection: DatasetInspection,
) -> ETLReport:
    """Build a structured ETL execution report."""

    return ETLReport(
        source_path=str(source_path),
        destination_table=destination_table,
        destination_schema=destination_schema,
        target_crs=target_crs,
        started_at=_format_datetime(started_at),
        finished_at=_format_datetime(finished_at),
        source_inspection=source_inspection,
        validation=validation,
        normalized_inspection=normalized_inspection,
    )


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""

    return datetime.now(timezone.utc)


def _format_datetime(value: datetime) -> str:
    """Return a timezone-aware datetime as an ISO 8601 string."""

    if value.tzinfo is None:
        raise ValueError("Report timestamps must be timezone-aware.")

    return value.isoformat()

def write_etl_report(
    report: ETLReport,
    output_path: str | Path,
) -> Path:
    """Write an ETL report to a JSON file.

    Parameters
    ----------
    report
        ETL execution report to serialize.
    output_path
        Destination JSON file path.

    Returns
    -------
    pathlib.Path
        Path to the written report file.
    """

    path = Path(output_path)

    if path.suffix.lower() != ".json":
        raise ValueError("ETL report output must use the .json extension.")

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report.to_dict(),
            file,
            indent=2,
            ensure_ascii=False,
        )

    return path