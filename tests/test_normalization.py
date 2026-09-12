"""Tests for geospatial dataset normalization."""

import geopandas as gpd
import pytest
from shapely.geometry import Point

from geospatial_etl.normalization import normalize_dataset


def test_normalize_dataset_normalizes_attribute_columns() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "Feature Name": ["alpha"],
            "Source-ID": [10],
        },
        geometry=[Point(0, 0)],
        crs="EPSG:4326",
    )

    result = normalize_dataset(dataset)

    assert tuple(result.columns) == (
        "feature_name",
        "source_id",
        "geometry",
    )


def test_normalize_dataset_preserves_geometry_column() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "Feature Name": ["alpha"],
        },
        geometry=[Point(1, 2)],
        crs="EPSG:4326",
    )

    result = normalize_dataset(dataset)

    assert result.geometry.name == "geometry"
    assert result.geometry.iloc[0].equals(Point(1, 2))


def test_normalize_dataset_reprojects_to_target_crs() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "name": ["alpha"],
        },
        geometry=[Point(-47.88, -15.79)],
        crs="EPSG:4326",
    )

    result = normalize_dataset(
        dataset,
        target_crs="EPSG:31983",
    )

    assert result.crs is not None
    assert result.crs.to_epsg() == 31983


def test_normalize_dataset_rejects_reprojection_without_source_crs() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "name": ["alpha"],
        },
        geometry=[Point(0, 0)],
    )

    with pytest.raises(
        ValueError,
        match="source CRS is undefined",
    ):
        normalize_dataset(
            dataset,
            target_crs="EPSG:31983",
        )


def test_normalize_dataset_detects_duplicate_normalized_columns() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "Feature Name": ["alpha"],
            "feature-name": ["beta"],
        },
        geometry=[Point(0, 0)],
        crs="EPSG:4326",
    )

    with pytest.raises(
        ValueError,
        match="duplicate column names",
    ):
        normalize_dataset(dataset)


def test_normalize_dataset_does_not_modify_original_dataset() -> None:
    dataset = gpd.GeoDataFrame(
        {
            "Feature Name": ["alpha"],
        },
        geometry=[Point(0, 0)],
        crs="EPSG:4326",
    )

    normalize_dataset(dataset)

    assert "Feature Name" in dataset.columns