"""Tests for geospatial dataset validation."""

from geospatial_etl.models import DatasetInspection
from geospatial_etl.validation import validate_dataset


def test_validate_dataset_accepts_valid_dataset() -> None:
    inspection = DatasetInspection(
        feature_count=10,
        crs="EPSG:4326",
        geometry_column="geometry",
        geometry_types=("Point",),
        attribute_columns=("name",),
        null_geometry_count=0,
        empty_geometry_count=0,
        invalid_geometry_count=0,
        bounds=(0.0, 0.0, 10.0, 10.0),
    )

    result = validate_dataset(inspection)

    assert result.is_valid is True
    assert result.issues == ()


def test_validate_dataset_rejects_empty_dataset() -> None:
    inspection = DatasetInspection(
        feature_count=0,
        crs="EPSG:4326",
        geometry_column="geometry",
        geometry_types=(),
        attribute_columns=("name",),
        null_geometry_count=0,
        empty_geometry_count=0,
        invalid_geometry_count=0,
        bounds=None,
    )

    result = validate_dataset(inspection)

    assert result.is_valid is False
    assert len(result.issues) == 1
    assert result.issues[0].code == "empty_dataset"


def test_validate_dataset_rejects_missing_crs() -> None:
    inspection = DatasetInspection(
        feature_count=1,
        crs=None,
        geometry_column="geometry",
        geometry_types=("Point",),
        attribute_columns=("name",),
        null_geometry_count=0,
        empty_geometry_count=0,
        invalid_geometry_count=0,
        bounds=(0.0, 0.0, 0.0, 0.0),
    )

    result = validate_dataset(inspection)

    assert result.is_valid is False
    assert result.issues[0].code == "missing_crs"


def test_validate_dataset_reports_geometry_problems() -> None:
    inspection = DatasetInspection(
        feature_count=10,
        crs="EPSG:4326",
        geometry_column="geometry",
        geometry_types=("Polygon",),
        attribute_columns=("name",),
        null_geometry_count=2,
        empty_geometry_count=1,
        invalid_geometry_count=3,
        bounds=(0.0, 0.0, 10.0, 10.0),
    )

    result = validate_dataset(inspection)

    assert result.is_valid is False

    codes = tuple(issue.code for issue in result.issues)

    assert codes == (
        "null_geometries",
        "empty_geometries",
        "invalid_geometries",
    )


def test_validate_dataset_reports_multiple_issues() -> None:
    inspection = DatasetInspection(
        feature_count=0,
        crs=None,
        geometry_column="geometry",
        geometry_types=(),
        attribute_columns=(),
        null_geometry_count=0,
        empty_geometry_count=0,
        invalid_geometry_count=0,
        bounds=None,
    )

    result = validate_dataset(inspection)

    codes = tuple(issue.code for issue in result.issues)

    assert result.is_valid is False
    assert codes == (
        "empty_dataset",
        "missing_crs",
    )