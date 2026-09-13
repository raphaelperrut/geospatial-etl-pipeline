"""High-level orchestration for the geospatial ETL pipeline."""

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import Engine

from geospatial_etl.ingest import read_vector_dataset
from geospatial_etl.inspect import inspect_dataset
from geospatial_etl.load import load_to_postgis
from geospatial_etl.models import DatasetInspection, DatasetValidation
from geospatial_etl.normalization import normalize_dataset
from geospatial_etl.report import ETLReport, build_etl_report, utc_now
from geospatial_etl.validation import validate_dataset


@dataclass(frozen=True)
class ETLPipelineResult:
    """Structured result of a geospatial ETL execution."""

    source_inspection: DatasetInspection
    validation: DatasetValidation
    normalized_inspection: DatasetInspection
    report: ETLReport


def run_etl_pipeline(
    source_path: str | Path,
    engine: Engine,
    table_name: str,
    *,
    target_crs: str | None = None,
    schema: str = "public",
    if_exists: str = "fail",
) -> ETLPipelineResult:
    """Run the geospatial ETL pipeline from file ingestion to PostGIS load."""

    started_at = utc_now()

    dataset = read_vector_dataset(source_path)

    source_inspection = inspect_dataset(dataset)
    validation = validate_dataset(source_inspection)

    if not validation.is_valid:
        issue_codes = ", ".join(
            issue.code for issue in validation.issues
        )

        raise ValueError(
            f"Dataset validation failed: {issue_codes}"
        )

    normalized = normalize_dataset(
        dataset,
        target_crs=target_crs,
    )

    normalized_inspection = inspect_dataset(normalized)

    load_to_postgis(
        normalized,
        engine,
        table_name,
        schema=schema,
        if_exists=if_exists,
    )

    finished_at = utc_now()

    report = build_etl_report(
        source_path=source_path,
        destination_table=table_name,
        destination_schema=schema,
        target_crs=target_crs,
        started_at=started_at,
        finished_at=finished_at,
        source_inspection=source_inspection,
        validation=validation,
        normalized_inspection=normalized_inspection,
    )

    return ETLPipelineResult(
        source_inspection=source_inspection,
        validation=validation,
        normalized_inspection=normalized_inspection,
        report=report,
    )