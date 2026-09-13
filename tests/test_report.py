"""Tests for ETL execution reports."""

from datetime import datetime, timezone

import pytest

import json
from pathlib import Path

from geospatial_etl.models import (
    DatasetInspection,
    DatasetValidation,
)
from geospatial_etl.report import (
    build_etl_report,
    write_etl_report,
)


def test_build_etl_report_returns_serializable_structure() -> None:
    inspection = DatasetInspection(
        feature_count=2,
        crs="EPSG:4326",
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

    started_at = datetime(
        2026,
        9,
        12,
        20,
        0,
        tzinfo=timezone.utc,
    )

    finished_at = datetime(
        2026,
        9,
        12,
        20,
        1,
        tzinfo=timezone.utc,
    )

    report = build_etl_report(
        source_path="sample.gpkg",
        destination_table="features",
        destination_schema="public",
        target_crs="EPSG:31983",
        started_at=started_at,
        finished_at=finished_at,
        source_inspection=inspection,
        validation=validation,
        normalized_inspection=inspection,
    )

    result = report.to_dict()

    assert result["source_path"] == "sample.gpkg"
    assert result["destination_table"] == "features"
    assert result["destination_schema"] == "public"
    assert result["target_crs"] == "EPSG:31983"
    assert result["validation"]["is_valid"] is True
    assert result["source_inspection"]["feature_count"] == 2
    assert result["started_at"] == "2026-09-12T20:00:00+00:00"
    assert result["finished_at"] == "2026-09-12T20:01:00+00:00"


def test_build_etl_report_rejects_naive_timestamp() -> None:
    inspection = DatasetInspection(
        feature_count=1,
        crs="EPSG:4326",
        geometry_column="geometry",
        geometry_types=("Point",),
        attribute_columns=(),
        null_geometry_count=0,
        empty_geometry_count=0,
        invalid_geometry_count=0,
        bounds=(0.0, 0.0, 0.0, 0.0),
    )

    validation = DatasetValidation(
        is_valid=True,
        issues=(),
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        build_etl_report(
            source_path="sample.gpkg",
            destination_table="features",
            destination_schema="public",
            target_crs=None,
            started_at=datetime(2026, 9, 12, 20, 0),
            finished_at=datetime(
                2026,
                9,
                12,
                20,
                1,
                tzinfo=timezone.utc,
            ),
            source_inspection=inspection,
            validation=validation,
            normalized_inspection=inspection,
        )

def test_write_etl_report_creates_json_file(
    tmp_path: Path,
) -> None:
    inspection = DatasetInspection(
        feature_count=2,
        crs="EPSG:4326",
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

    report = build_etl_report(
        source_path="sample.gpkg",
        destination_table="features",
        destination_schema="public",
        target_crs="EPSG:31983",
        started_at=datetime(
            2026,
            9,
            12,
            20,
            0,
            tzinfo=timezone.utc,
        ),
        finished_at=datetime(
            2026,
            9,
            12,
            20,
            1,
            tzinfo=timezone.utc,
        ),
        source_inspection=inspection,
        validation=validation,
        normalized_inspection=inspection,
    )

    output_path = tmp_path / "reports" / "etl_report.json"

    written_path = write_etl_report(
        report,
        output_path,
    )

    assert written_path == output_path
    assert output_path.exists()

    data = json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    )

    assert data["destination_table"] == "features"
    assert data["destination_schema"] == "public"
    assert data["validation"]["is_valid"] is True
    assert data["source_inspection"]["feature_count"] == 2


def test_write_etl_report_rejects_non_json_extension(
    tmp_path: Path,
) -> None:
    inspection = DatasetInspection(
        feature_count=1,
        crs="EPSG:4326",
        geometry_column="geometry",
        geometry_types=("Point",),
        attribute_columns=(),
        null_geometry_count=0,
        empty_geometry_count=0,
        invalid_geometry_count=0,
        bounds=(0.0, 0.0, 0.0, 0.0),
    )

    validation = DatasetValidation(
        is_valid=True,
        issues=(),
    )

    report = build_etl_report(
        source_path="sample.gpkg",
        destination_table="features",
        destination_schema="public",
        target_crs=None,
        started_at=datetime(
            2026,
            9,
            12,
            20,
            0,
            tzinfo=timezone.utc,
        ),
        finished_at=datetime(
            2026,
            9,
            12,
            20,
            1,
            tzinfo=timezone.utc,
        ),
        source_inspection=inspection,
        validation=validation,
        normalized_inspection=inspection,
    )

    with pytest.raises(
        ValueError,
        match=r"\.json",
    ):
        write_etl_report(
            report,
            tmp_path / "etl_report.txt",
        )