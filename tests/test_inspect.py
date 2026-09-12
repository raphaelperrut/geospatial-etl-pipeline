"""Tests for geospatial dataset inspection."""

import geopandas as gpd
from shapely.geometry import Point, Polygon

from geospatial_etl.inspect import inspect_dataset


def test_inspect_dataset_returns_expected_summary() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "name": ["alpha", "beta"],
            "value": [10, 20],
        },
        geometry=[
            Point(0, 0),
            Point(10, 5),
        ],
        crs="EPSG:4326",
    )

    result = inspect_dataset(dataset)

    assert result.feature_count == 2
    assert result.crs == "EPSG:4326"
    assert result.geometry_column == "geometry"
    assert result.geometry_types == ("Point",)
    assert result.attribute_columns == ("name", "value")
    assert result.null_geometry_count == 0
    assert result.empty_geometry_count == 0
    assert result.invalid_geometry_count == 0
    assert result.bounds == (0.0, 0.0, 10.0, 5.0)


def test_inspect_dataset_counts_null_and_empty_geometries() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "name": ["valid", "null", "empty"],
        },
        geometry=[
            Point(1, 2),
            None,
            Point(),
        ],
        crs="EPSG:4326",
    )

    result = inspect_dataset(dataset)

    assert result.feature_count == 3
    assert result.null_geometry_count == 1
    assert result.empty_geometry_count == 1
    assert result.invalid_geometry_count == 0
    assert result.geometry_types == ("Point",)


def test_inspect_dataset_counts_invalid_geometries() -> None:
    invalid_polygon = Polygon(
        [
            (0, 0),
            (2, 2),
            (2, 0),
            (0, 2),
            (0, 0),
        ]
    )

    dataset = gpd.GeoDataFrame(
        {
            "name": ["invalid"],
        },
        geometry=[invalid_polygon],
        crs="EPSG:4326",
    )

    result = inspect_dataset(dataset)

    assert result.invalid_geometry_count == 1
    assert result.geometry_types == ("Polygon",)


def test_inspect_dataset_handles_missing_crs() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "name": ["alpha"],
        },
        geometry=[Point(0, 0)],
    )

    result = inspect_dataset(dataset)

    assert result.crs is None


def test_inspect_dataset_returns_none_bounds_for_empty_dataset() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "name": [],
        },
        geometry=[],
        crs="EPSG:4326",
    )

    result = inspect_dataset(dataset)

    assert result.feature_count == 0
    assert result.bounds is None