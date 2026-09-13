"""Tests for the geospatial ETL command-line interface."""

from pathlib import Path
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from geospatial_etl.cli import app
from geospatial_etl.models import (
    DatasetInspection,
    DatasetValidation,
)
from geospatial_etl.pipeline import ETLPipelineResult
from geospatial_etl.report import ETLReport


runner = CliRunner()


def _build_pipeline_result() -> ETLPipelineResult:
    inspection = DatasetInspection(
        feature_count=2,
        crs="EPSG:31983",
        geometry_column="geometry",
        geometry_types=("Point",),
        attribute_columns=("name",),
        null_geometry_count=0,
        empty_geometry_count=0,
        invalid_geometry_count=0,
        bounds=(0.0, 0.0, 10.0, 10.0),
    )

    validation = DatasetValidation(
        is_valid=True,
        issues=(),
    )

    report = ETLReport(
        source_path="sample.gpkg",
        destination_table="features",
        destination_schema="public",
        target_crs="EPSG:31983",
        started_at="2026-09-12T20:00:00+00:00",
        finished_at="2026-09-12T20:01:00+00:00",
        source_inspection=inspection,
        validation=validation,
        normalized_inspection=inspection,
    )

    return ETLPipelineResult(
        source_inspection=inspection,
        validation=validation,
        normalized_inspection=inspection,
        report=report,
    )


def test_cli_run_executes_pipeline(tmp_path: Path) -> None:
    source = tmp_path / "sample.gpkg"
    source.touch()

    engine = Mock()
    pipeline_result = _build_pipeline_result()

    with (
        patch(
            "geospatial_etl.cli.create_postgis_engine",
            return_value=engine,
        ),
        patch(
            "geospatial_etl.cli.run_etl_pipeline",
            return_value=pipeline_result,
        ) as pipeline_mock,
    ):
        result = runner.invoke(
            app,
            [
                "run",
                str(source),
                "--database-url",
                "postgresql+psycopg://user:password@localhost/db",
                "--table",
                "features",
                "--target-crs",
                "EPSG:31983",
            ],
        )

    assert result.exit_code == 0

    assert "ETL completed successfully" in result.stdout
    assert "2 features" in result.stdout
    assert "public.features" in result.stdout

    pipeline_mock.assert_called_once()

    engine.dispose.assert_called_once()


def test_cli_run_writes_report_when_requested(
    tmp_path: Path,
) -> None:
    source = tmp_path / "sample.gpkg"
    source.touch()

    report_path = tmp_path / "report.json"

    engine = Mock()
    pipeline_result = _build_pipeline_result()

    with (
        patch(
            "geospatial_etl.cli.create_postgis_engine",
            return_value=engine,
        ),
        patch(
            "geospatial_etl.cli.run_etl_pipeline",
            return_value=pipeline_result,
        ),
        patch(
            "geospatial_etl.cli.write_etl_report",
        ) as report_mock,
    ):
        result = runner.invoke(
            app,
            [
                "run",
                str(source),
                "--database-url",
                "postgresql+psycopg://user:password@localhost/db",
                "--table",
                "features",
                "--report",
                str(report_path),
            ],
        )

    assert result.exit_code == 0

    report_mock.assert_called_once_with(
        pipeline_result.report,
        report_path,
    )

    assert "Report written to" in result.stdout
    engine.dispose.assert_called_once()


def test_cli_run_returns_error_when_pipeline_fails(
    tmp_path: Path,
) -> None:
    source = tmp_path / "sample.gpkg"
    source.touch()

    engine = Mock()

    with (
        patch(
            "geospatial_etl.cli.create_postgis_engine",
            return_value=engine,
        ),
        patch(
            "geospatial_etl.cli.run_etl_pipeline",
            side_effect=ValueError(
                "Dataset validation failed: missing_crs"
            ),
        ),
    ):
        result = runner.invoke(
            app,
            [
                "run",
                str(source),
                "--database-url",
                "postgresql+psycopg://user:password@localhost/db",
                "--table",
                "features",
            ],
        )

    assert result.exit_code == 1
    assert "ETL failed" in result.stderr
    assert "missing_crs" in result.stderr

    engine.dispose.assert_called_once()