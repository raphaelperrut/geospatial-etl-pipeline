"""Integration tests for the geospatial ETL pipeline."""

from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

from geospatial_etl.ingest import read_vector_dataset
from geospatial_etl.inspect import inspect_dataset
from geospatial_etl.normalization import normalize_dataset
from geospatial_etl.validation import validate_dataset


def test_geopackage_ingestion_inspection_and_validation(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "sample.gpkg"

    source = gpd.GeoDataFrame(
        {
            "name": ["alpha", "beta", "gamma"],
            "value": [10, 20, 30],
        },
        geometry=[
            Point(0, 0),
            Point(5, 10),
            Point(10, 20),
        ],
        crs="EPSG:4326",
    )

    source.to_file(
        input_path,
        layer="features",
        driver="GPKG",
    )

    dataset = read_vector_dataset(input_path)
    inspection = inspect_dataset(dataset)
    validation = validate_dataset(inspection)

    assert inspection.feature_count == 3
    assert inspection.crs == "EPSG:4326"
    assert inspection.geometry_types == ("Point",)
    assert inspection.attribute_columns == ("name", "value")
    assert inspection.bounds == (0.0, 0.0, 10.0, 20.0)

    assert validation.is_valid is True
    assert validation.issues == ()


def test_pipeline_detects_missing_crs(tmp_path: Path) -> None:
    input_path = tmp_path / "missing_crs.gpkg"

    source = gpd.GeoDataFrame(
        {
            "name": ["alpha", "beta"],
        },
        geometry=[
            Point(0, 0),
            Point(1, 1),
        ],
    )

    source.to_file(
        input_path,
        layer="features",
        driver="GPKG",
    )

    dataset = read_vector_dataset(input_path)
    inspection = inspect_dataset(dataset)
    validation = validate_dataset(inspection)

    assert inspection.crs is None
    assert validation.is_valid is False

    codes = tuple(issue.code for issue in validation.issues)

    assert codes == ("missing_crs",)


def test_geopackage_pipeline_normalizes_dataset(
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "normalization.gpkg"

    source = gpd.GeoDataFrame(
        {
            "Feature Name": ["alpha", "beta"],
            "Source-ID": [100, 200],
        },
        geometry=[
            Point(-47.88, -15.79),
            Point(-47.87, -15.78),
        ],
        crs="EPSG:4326",
    )

    source.to_file(
        input_path,
        layer="features",
        driver="GPKG",
    )

    dataset = read_vector_dataset(input_path)

    inspection = inspect_dataset(dataset)
    validation = validate_dataset(inspection)

    assert validation.is_valid is True

    normalized = normalize_dataset(
        dataset,
        target_crs="EPSG:31983",
    )

    normalized_inspection = inspect_dataset(normalized)

    assert tuple(normalized.columns) == (
        "feature_name",
        "source_id",
        "geometry",
    )
    assert normalized.crs is not None
    assert normalized.crs.to_epsg() == 31983

    assert normalized_inspection.feature_count == 2
    assert normalized_inspection.crs == "EPSG:31983"
    assert normalized_inspection.attribute_columns == (
        "feature_name",
        "source_id",
    )
    assert normalized_inspection.geometry_types == ("Point",)